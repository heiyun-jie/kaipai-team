# 00-211 设计：发版产物地址收口与审计门禁可达化

## 1. 事实基线（本轮实测，非推断）

每条都由命令确认。凡未实测的机制不在此处当结论使用。

### 1.1 `src` 内无硬编码地址

`src` 全量 grep `http://` 只命中 6 个 `static/mine-icons/*.svg` 的 `xmlns`。三处消费点全部读环境变量：

| 文件 | 行 | 形态 |
|---|---|---|
| `src/utils/request.ts` | 16 | `normalizeApiBaseUrl(import.meta.env.VITE_API_BASE_URL \|\| '')` |
| `src/utils/runtime.ts` | 9 | `normalizeApiBaseUrl(import.meta.env.VITE_API_BASE_URL)` |
| `src/api/actor-asset.ts` | 29 / 45 | 同 `request.ts` |

**推论**：无「把地址收进环境配置」这类改造工作量——它已经在环境配置里。

### 1.2 env 文件现状与优先级（实测）

三个 env 文件均被 `.gitignore` 的 `.env.*` 命中，只存在于本机：

| 文件 | `VITE_API_BASE_URL` |
|---|---|
| `.env` | `https://api.kplyyk.com` |
| `.env.local` | `http://127.0.0.1:8010` |
| `.env.example` | `https://api.kplyyk.com` |

实测确认：`.env.local` 覆盖 `.env`，故构建产物取本机地址。**进程内环境变量优先级高于全部 env 文件**（实测：`set VITE_API_BASE_URL=...` 后产物 4 处全部变为生产地址，`.env.local` 未被读取生效）。

### 1.3 npm post 钩子是完整脚本名精确匹配（实测）

探针实验：定义 `a:b`、`posta`、`posta:b` 三个脚本，`npm run a:b` 触发 `posta:b`、**未触发** `posta`。

**推论**：新增 `build:mp-weixin:release` 不会触发 `postbuild:mp-weixin`；要挂后处理必须显式定义 `postbuild:mp-weixin:release`。

### 1.4 `sync-mp-weixin.ps1` 是发版必需的后处理，不只是 dev 同步

该脚本在 `robocopy` **之前**（第 144-146 行）对 `$source`（即 `dist/build`）原地执行三项：

| 函数 | 作用 | 性质 |
|---|---|---|
| `Remove-RetiredExternalAssets` | 剥离 `cdn1.dcloud` 背景图、改写 `vuejs.org` 错误链 | 发版必需 |
| `Repair-GeneratedNumericTernaryLiterals` | 修 `?.5:` 等非法语法 | `00-207` 白屏合同 |
| `Normalize-GeneratedTextEncoding` | 去 UTF-8 BOM | 发版必需 |

之后才是 dev 专属动作：`robocopy /MIR` 镜像 + `Apply-LocalDevProjectConfig`（`urlCheck=false`）。

**推论**：绕过 postbuild 的发版路径会同时绕过白屏修复。正确设计是复用同一套后处理、只跳过 dev 专属段。

### 1.5 「DEV/PROD 分支」不存在，是后处理造成的假象

本轮前期观察到 `build:mp-weixin` 与同体不同名脚本产出不同的 `vendor.js`（md5 在 `d285cd8` / `ce23755` 间确定性翻转），曾归因为构建模式分支。实测证据链：

- `vite.config.ts` 打点显示三个脚本看到的 `NODE_ENV` / `UNI_NODE_ENV` / `VITE_USER_NODE_ENV` **全部相同**（均 `production`）。
- PowerShell 带正向对照的递归扫描（600 个 `.js`，`UNI_NODE_ENV` 命中 2 文件与直接读取位置一致）确认 `@dcloudio` 内 `npm_lifecycle_event` **0 命中**，框架读不到脚本名。
- 读 `sync-mp-weixin.ps1:144` 定位真因：`Remove-RetiredExternalAssets` 把 `` `https://vuejs.org/error-reference/#runtime-${type}` `` 原地改写为 `"runtime-error-"+type`。

**结论**：所谓「PROD 分支」是 postbuild 文本替换后的产物，「DEV 分支」才是构建原样。构建本身不存在分支差异。

### 1.6 审计脚本的两个结构缺陷

```powershell
$ErrorActionPreference = "Stop"          # 第 6 行
...
$externalUrlMatches | ForEach-Object {
  Write-Error "发现非 kplyyk.com ... 外链：..."   # 首条即终止
}
exit 1                                    # 执行不到
```

- 扫描穷尽（`Select-String -AllMatches`），被截断的是**报告**。
- URL 检查位于包体统计之前 → 包体门禁不可达。实测：退出码 `1`，输出中无任何包体统计行。

## 2. 设计决策

### D1：发版地址用 npm script 内联注入进程内变量

不新建 `.env.production` / `.env.release`，不动 `.env.local`。

```json
"build:mp-weixin:release": "set VITE_API_BASE_URL=https://api.kplyyk.com&&uni build -p mp-weixin"
```

理由：

- 进程内变量优先级最高（§1.2 实测），一处注入即覆盖全部 4 个内联点。
- 发版地址随 `package.json` 入库，可见可审；不依赖被 gitignore 的本机文件（后者在他人机器或 CI 上等于不存在）。
- `set X=y&&cmd` 的 `&&` 前不留空格，避免值尾带空格。

**被否决的方案及原因（均经实测）**：

| 方案 | 否决原因 |
|---|---|
| `.env.release` + `--mode release` | `--mode` 会把 mode 带离 `production`，且方案依赖被 gitignore 的本机文件 |
| `UNI_OUTPUT_DIR` 输出到独立目录 | 实测非必需；且审计脚本默认 `BuildDir` 指向 `dist/build`，另开目录会让门禁与发版产物脱钩 |
| 新建 `.env.production` | 会被日常 `build:mp-weixin` 一并加载，反而破坏本机联调 |

### D2：发版复用后处理，`-SourceOnly` 跳过 dev 专属段

`sync-mp-weixin.ps1` 增加 `[switch] $SourceOnly`：三项归一化后 `exit 0`，不执行 robocopy 与 `urlCheck` 改写。

```json
"postbuild:mp-weixin:release": "powershell -ExecutionPolicy Bypass -File scripts/sync-mp-weixin.ps1 -SourceOnly"
```

理由：单一后处理实现，发版与 dev 共用，不会出现「dev 修了、发版没修」的漂移。依赖 §1.3 的钩子精确匹配规则。

### D3：外链在产物侧归零，不在门禁侧豁免

`vendor.js:4544` 的 `github.com/dcloudio/uni-app/issues/3954` 是框架注释行（源出 `uni-mp-vue/dist/vue.runtime.esm.js:7140`）。仓库已有同类先例（`cdn1.dcloud` 与 `vuejs.org` 均由 `Remove-RetiredExternalAssets` 处理），故按既有机制补一条剥离规则：

```powershell
-replace 'https://github\.com/dcloudio/uni-app/issues/[0-9]+', ''
```

**不采用**审计侧「框架注释分级豁免」。原因：产物侧归零后门禁口径无需放宽，也不引入「注释行判定」这类可被绕过的豁免逻辑。

### D4：审计两项检查独立判定、统一退出

URL 检查改为收集后全量 `Write-Host`（含相对路径、行号、命中内容），置 `$externalUrlFailed` 标志但不终止；包体统计照常执行；末尾 `if ($externalUrlFailed -or $hasError) { exit 1 }`。

这是**加强**而非放宽：使用者从只见 1 条变为可见全部，且包体门禁首次可达。

## 3. 影响面

| 对象 | 改动 | 可逆性 |
|---|---|---|
| `kaipai-frontend/package.json` | +2 个脚本 | 删除即回退 |
| `kaipai-frontend/scripts/sync-mp-weixin.ps1` | +`-SourceOnly` 开关、+1 条剥离规则 | 单文件回退 |
| `kaipai-frontend/scripts/audit-mp-package.ps1` | URL 检查不再终止、末尾聚合判定 | 单文件回退 |
| `kaipai-frontend/.env.local` | **不动** | — |
| `kaipai-frontend/src/**` | **不动** | — |
| `vite.config.ts` | **不动**（`00-207` 合同） | — |
| 数据库 / 后端 | **不动** | — |

`dist/build` 的地址形态随最后一次执行的脚本变化（`build:mp-weixin` → 本机，`build:mp-weixin:release` → 生产）。`dist/dev` 只由前者更新，DevTools 联调始终不受发版构建影响。

## 4. 验证结果（实测值）

| 项 | 结果 |
|---|---|
| `vue-tsc --noEmit` | PASS，0 报错 |
| 发版产物 `127.0.0.1` / `localhost` | `0` |
| 发版产物 `api.kplyyk.com` | `4`（正向对照有效） |
| 发版产物非 kplyyk 外链 | `0` |
| 发版产物 `?.5:` 非法语法 | `0` |
| `dist/dev` 本机地址 / 生产地址 | `4` / `0`（未被污染） |
| `dist/dev` `urlCheck` | `false`（dev 链路无回归） |
| `audit:mp-package` 退出码 | `0` |
| 主包 | `421.09 KB` / `2.00 MB`（`20.56%`） |
| `pkg-actor-card` | `81.28 KB`（`3.97%`） |
| `pkg-card` | `31.64 KB`（`1.54%`） |
| `pkg-profile` | `80.67 KB`（`3.94%`） |
| `pkg-tools` | `39.21 KB`（`1.91%`） |
| 产物总计 | `653.89 KB` |

包体统计为**本仓库首次成功打印**——此前被 URL 检查首错终止，从未可达。

## 5. 对错误方向的更正记录

本 Spec 显式记录 6 条已输出但不成立的判断，避免后续轮次沿用。前 2 条来自前序轮次，后 4 条来自本轮我自己的中途归因。

| 表述 | 实测结论 |
|---|---|
| 「要把 baseURL 收到环境配置里再全量扫」 | 不成立。`src` 三处消费点早已读 `import.meta.env.VITE_API_BASE_URL`（§1.1） |
| 「脚本首错即停，不代表已穷尽其他外链」 | 部分不成立。扫描穷尽，被截断的是报告（§1.6） |
| 「`--mode release` + `.env.release` 是发版方案」 | 不成立。`--mode` 把构建带离 `production`；且该文件被 gitignore，他机不可复现（§2 D1） |
| 「`UNI_OUTPUT_DIR` 是 DEV/PROD 差异的元凶」 | 不成立。不设它、仅注入地址变量时仍产出同样形态（§1.5） |
| 「构建缓存被 `--mode release` 污染」 | 不成立。`node_modules/.vite` mtime 为 `08-07`，本轮从未改动，且内无相关内容（§1.5） |
| 「脚本名决定 DEV/PROD 分支」 | 不成立。三脚本 `NODE_ENV` 全同；`npm_lifecycle_event` 在框架内 0 命中；真因是 postbuild 文本替换（§1.5） |

**共同根因**：在读定义机制的文件之前，就把观察到的相关性推成了因果。§1.5 的四次连续误判尤其典型——真因（`sync-mp-weixin.ps1:144`）在第一次读该文件时就该发现，但当时只读了第 39 行附近的 `Read-LocalApiBaseUrl`，没读完全文。

**对治规则**（本轮新增，供后续沿用）：

1. 机制类判断必须落成可执行验证步骤，不写成既定事实。
2. 涉及某脚本行为时，读**全文**再下结论，不只读命中行附近。
3. 空 grep 输出必须配正向对照。本轮又踩一次：Git Bash 在 `node_modules` 下递归 grep 失效（`UNI_NODE_ENV` 明明存在却 0 命中），正向对照当场识破，改用 PowerShell 重做。
4. 退出码要单独测量。`PIPESTATUS` 会被中间命令重置——本轮一度误读 `audit exit: 0`，实际是 `1`。
