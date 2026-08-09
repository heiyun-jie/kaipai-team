# 00-211 发版产物地址收口与审计门禁可达化

> 状态：已完成
> 定位：**发版硬前置**（不是独立治理轮次）。主线是「V3 UI 接通后端 → 发布上线」，本 Spec 只解决其中「提交审核必挂」的阻塞项。
> 前置：`00-207` 的 `minify: false` 是本轮不可推翻的上游约束

## 1. 背景与真实成因

`npm run audit:mp-package` 长期红灯，且包体统计从未打印过。本轮把两件事查到机制层，其中多条既有描述与我在本轮前期的推断均被实测推翻，更正记录见 `design.md` §5。

### 1.1 发版产物内联本机地址（真实阻塞）

不是代码硬编码。`src` 三处消费点全部读环境变量（`utils/request.ts:16`、`utils/runtime.ts:9`、`api/actor-asset.ts:29/45`），`src` 内无任何硬编码地址。

真实成因是 env 文件优先级：`.env` 为 `https://api.kplyyk.com`（合规），`.env.local` 为 `http://127.0.0.1:8010`，构建时本地值胜出并被内联进 `dist/build` 的 4 个点。即**本机联调配置被带进了发版产物**。

### 1.2 审计门禁不可达（结构缺陷）

`audit-mp-package.ps1` 的扫描是穷尽的（一次 `Select-String -AllMatches`），缺陷有两处：

- `Write-Error` 在 `$ErrorActionPreference = "Stop"` 下使首条命中成为终止错误，循环中断、`exit 1` 都执行不到 → **报告只显示 1 条**。
- URL 检查排在包体统计之前 → 只要有一条外链，`2 MB` 包体门禁**永远不可达**。这解释了「包体统计从未打印」。

### 1.3 外链的真实性质：全部为框架产物注释，且已有既成处理机制

产物中的非业务外链共 3 类，全部来自 `@dcloudio` 框架产物、均为注释或框架 CSS，不是业务网络调用：

| 位置 | 内容 | 既有处理 |
|---|---|---|
| `app.wxss` | `cdn1.dcloud.net.cn/.../shadow-grey.png` | `sync-mp-weixin.ps1` 已剥离 |
| `common/vendor.js` | `` `https://vuejs.org/error-reference/#runtime-${type}` `` | `sync-mp-weixin.ps1` 已改写 |
| `common/vendor.js:4544` | `https://github.com/dcloudio/uni-app/issues/3954` | **规则缺失**，本轮补齐 |

关键事实：仓库**早已建立**「后处理阶段剥离框架外链」的机制（`Remove-RetiredExternalAssets`），第 3 条只是漏了一条规则。因此本轮不需要在审计侧新增「框架注释豁免」分级——按既有先例补剥离规则即可，产物侧直接归零，门禁口径无需放宽。

### 1.4 后处理是发版必需，不只是 dev 便利

`sync-mp-weixin.ps1` 在 robocopy **之前**对 `dist/build` 原地执行三项归一化：外链剥离、`Repair-GeneratedNumericTernaryLiterals`（`00-207` 白屏合同）、编码归一化。它此前只挂在 `postbuild:mp-weixin` 上。

**推论**：任何绕过 postbuild 的发版路径，会同时绕过白屏修复与外链剥离。故发版脚本必须复用同一套后处理，只跳过 dev 镜像。

## 2. 用户故事

作为开发者，我希望有一条命令产出可直接提交审核的产物：不含本机地址、已过全部后处理。

作为开发者，我希望发版构建不打断本机联调——`dist/dev` 与 `.env.local` 都不被动。

作为开发者，我希望审计一次把外链与包体两项都报完，而不是首错即停让包体门禁永远不可达。

## 3. 功能需求

### 3.1 发版产物不得内联非生产 API 地址

**描述**：提供发版构建入口，产出的 `dist/build/mp-weixin` 不得含 `127.0.0.1` / `localhost`，且不得改变本机以 `.env.local` 联调的现有习惯。

**验收标准**：

- WHEN 执行发版构建 THEN 产物内 `127.0.0.1` 与 `localhost` 命中数为 `0`。
- WHEN 执行发版构建 THEN 4 个内联点均为 `https://api.kplyyk.com`。
- WHEN 执行发版构建 THEN `.env.local` 未被修改，`dist/dev` 仍为本机地址（DevTools 联调不中断）。
- WHEN 判定 env 优先级 THEN 结论必须来自实测，不得依据记忆或文档断言。

### 3.2 发版产物必须经过与 dev 相同的后处理

**描述**：发版路径复用 `sync-mp-weixin.ps1` 的三项归一化，只跳过 dev 镜像与 `urlCheck` 改写。

**验收标准**：

- WHEN 执行发版构建 THEN 产物内 `?.5:` 形态非法语法命中为 `0`（`00-207` 白屏合同不被绕过）。
- WHEN 执行发版构建 THEN 框架外链（`cdn1.dcloud` / `vuejs.org` / `github.com/dcloudio`）命中为 `0`。
- WHEN 执行发版构建 THEN `dist/dev` 内容与 `project.config.json` 均不被改写。
- WHEN 执行日常 `build:mp-weixin` THEN dev 链路行为与本轮之前完全一致（无回归）。

### 3.3 审计的外链检查与包体检查各自独立判定

**描述**：修正首错即停，使两项检查都跑完并各自出报告，退出码为二者聚合。

**验收标准**：

- WHEN 产物存在 N 处不合规外链 THEN 审计输出全部 N 条（相对路径 + 行号 + 命中内容）而非仅 1 条。
- WHEN 存在外链命中 THEN 包体统计仍然执行并打印，`2 MB` 门禁可达。
- WHEN 两项检查均通过 THEN 退出码 `0`；任一项失败 THEN 退出码 `1`。
- WHEN 无命中 THEN 分包统计逻辑与 `2 MB` 阈值行为保持不变。

## 4. 非功能需求

- 不得开启 `build.minify`：`00-207` 的 `minify: false` 为修白屏而设，属上游约束。
- 不得为消除告警而放宽门禁口径（跳过 `vendor.js` 全文件 / 加 URL 白名单 / 删除 URL 检查）。外链在**产物侧**归零，不在**门禁侧**豁免。
- 不得修改 `.env.local`，不得让发版构建污染 `dist/dev`。
- 审计脚本改动不得影响 `2 MB` 阈值与分包统计逻辑。
- 分支固定 `V3.0`，不新建不切换。

## 5. 约束条件

- 环境文件（`.env` / `.env.local` / `.env.example`）被 `.gitignore` 命中，只存在于本机；本轮不将地址写入任何入库文件之外的新配置文件（发版地址以 npm script 内联注入，随仓库入库、可见可审）。
- 仅改动：`kaipai-frontend/package.json`、`kaipai-frontend/scripts/sync-mp-weixin.ps1`、`kaipai-frontend/scripts/audit-mp-package.ps1`、本 Spec 与治理文档。
- `src/**`、`vite.config.ts`、数据库、后端均不动。

## 6. 完成清单

- [x] 实测确认 env 优先级与 npm 钩子匹配规则，结论写入 `design.md`。
- [x] 发版产物 `127.0.0.1` / `localhost` 命中 `0`，生产地址 `4` 处。
- [x] 发版产物框架外链命中 `0`、`?.5:` 命中 `0`。
- [x] `dist/dev` 未被污染（本机 `4` / 生产 `0`），`.env.local` 未改。
- [x] 日常 `build:mp-weixin` 无回归，`urlCheck=false` 仍生效。
- [x] 审计两项检查各自出报告，包体统计首次可见。
- [x] `audit:mp-package` 退出码 `0`。
- [x] `vue-tsc --noEmit` 0 报错。
- [x] 回填 `.sce/specs/README.md` 与 `spec-code-mapping.md`。

## 7. 本轮移出范围

- `.env.example` 入库（`.gitignore:15` 的 `.env.*` 连带忽略）：独立缺陷，与发版阻塞无因果关系，按主线收窄移出本轮。
- `login/index.vue:16` 的 `剧组版 · 分享平台` 旧版文案：需用户给新文案，与本 Spec 无关。
