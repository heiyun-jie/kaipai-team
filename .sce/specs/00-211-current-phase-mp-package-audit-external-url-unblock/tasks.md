# 00-211 任务：发版产物地址收口与审计门禁可达化

## T1 建立事实基线并更正前序错误方向

**Validates: Requirements 3.1**

- [x] grep `kaipai-frontend/src` 全量 `http://`，确认只命中 SVG `xmlns`，无 API 地址。
- [x] 定位三个 `VITE_API_BASE_URL` 消费点（`utils/request.ts:16`、`utils/runtime.ts:9`、`api/actor-asset.ts:29/45`）。
- [x] 用审计同模式穷尽扫 `dist/build/mp-weixin`，得全部命中并分类。
- [x] 读 `.env` / `.env.local` / `.env.example`，确认成因是 env 优先级而非代码缺陷。
- [x] 读 `vendor.js:4544` 上下文并回溯 `node_modules/@dcloudio/uni-mp-vue`，确认是框架注释。
- [x] 读 `audit-mp-package.ps1` 全文，确认扫描穷尽、报告被 `$ErrorActionPreference = "Stop"` 截断，且 URL 检查排在包体统计之前。
- [x] 读 `vite.config.ts` 与 `00-207`，确认 `minify: false` 是刻意决定，不可靠开压缩消除外链。
- [x] 在 `design.md` §5 写入全部 6 条错误方向的更正记录。

## T2 实测发版所需的三个机制

**Validates: Requirements 3.1, 3.2**

- [x] 实测 env 优先级：确认 `.env.local` 覆盖 `.env`，进程内变量优先级高于全部 env 文件。
- [x] 实测 npm post 钩子匹配规则：探针 `a:b` / `posta` / `posta:b`，确认为完整脚本名精确匹配。
- [x] 否决 `--mode release` 方案：实测该参数把构建带离 `production`。
- [x] 否决 `UNI_OUTPUT_DIR` 独立输出目录方案：实测非必需，且会让审计默认 `BuildDir` 与发版产物脱钩。
- [x] 排除构建缓存假设：`node_modules/.vite` mtime 为 `08-07`，本轮未改动且内无相关内容。
- [x] 用 `vite.config.ts` 打点证明三个脚本 `NODE_ENV` 全同，排除「脚本名决定分支」。
- [x] 读 `sync-mp-weixin.ps1` 全文定位真因：`Remove-RetiredExternalAssets` 的原地文本替换，所谓 DEV/PROD 分支不存在。
- [x] 清除全部探针（`vite.config.ts` 打点、`probe:*` 脚本、`dist/probe*`、`dist/release`、`_npmhook_probe`、`.env.release`）。

## T3 发版构建链路落地

**Validates: Requirements 3.1, 3.2**

- [x] `package.json` 新增 `build:mp-weixin:release`，以 `set VITE_API_BASE_URL=https://api.kplyyk.com&&` 内联注入生产地址。
- [x] `sync-mp-weixin.ps1` 新增 `[switch] $SourceOnly`：三项归一化后 `exit 0`，跳过 robocopy 与 `urlCheck` 改写。
- [x] `package.json` 新增 `postbuild:mp-weixin:release` 挂 `-SourceOnly`，确保白屏修复与外链剥离不被绕过。
- [x] 确认 `.env.local` 未被修改。
- [x] 核对发版产物：本机地址 `0`、生产地址 `4`、`?.5:` 非法语法 `0`。
- [x] 核对 `dist/dev` 未被污染：本机 `4` / 生产 `0`。
- [x] 补正向对照，排除「模式写错」冒充「已清零」。

## T4 外链在产物侧归零

**Validates: Requirements 3.2**

- [x] 确认 `vendor.js:4544` 为框架注释行，且仓库已有 `cdn1.dcloud` / `vuejs.org` 同类剥离先例。
- [x] `Remove-RetiredExternalAssets` 补一条 `github.com/dcloudio/uni-app/issues/[0-9]+` 剥离规则。
- [x] 重建发版产物，确认非 kplyyk 外链命中 `0`。
- [x] 不采用审计侧「框架注释分级豁免」，门禁口径未放宽。

## T5 审计门禁可达化

**Validates: Requirements 3.3**

- [x] URL 检查改为收集后全量 `Write-Host`（相对路径 + 行号 + 命中内容），不再首错终止。
- [x] 包体统计不再被 URL 检查阻断，`2 MB` 门禁首次可达。
- [x] 末尾聚合判定：`$externalUrlFailed -or $hasError` 决定退出码。
- [x] 正确测量退出码（避免 `PIPESTATUS` 被中间命令重置），确认 `0`。

## T6 全量门禁与文档回填

**Validates: Requirements 3.1, 3.2, 3.3**

- [x] `npm run type-check` PASS，0 报错。
- [x] `npm run build:mp-weixin:release` EXIT=0，postbuild 正确触发。
- [x] `npm run build:mp-weixin` EXIT=0，dev 链路无回归（`urlCheck=false` 仍生效、外链 `0`、`?.5:` `0`）。
- [x] `npm run audit:mp-package` 退出码 `0`，两项检查均出报告。
- [x] 记录包体实测值：主包 `421.09 KB`（`20.56%`），总计 `653.89 KB`。
- [x] 回填 `.sce/specs/README.md`（增量登记 + `00` 索引表）与 `.sce/specs/spec-code-mapping.md`。
