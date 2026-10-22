# 当前阶段小程序单一测试运行入口

> 状态：已完成（2026-09-02）。
>
> 上游：`00-216`、`00-219`、`00-243`、`00-246`、`00-251`

## 1. 概述

当前人工测试工程固定为 `kaipai-frontend/dist/dev/mp-weixin`，但本地测试命令仍先生成 `dist/build/mp-weixin`，再通过 postbuild 镜像到 `dist/dev/mp-weixin`。微信开发者工具运行期间若同步被保护拦截，就会留下 build 新、dev 旧的分叉，MCP 也可能被误传到错误目录。本 Spec 将测试构建、MCP 运行和本地启动脚本收口到一个物理测试入口：`dist/dev/mp-weixin`。

正式发布和隔离 Candidate 构建继续使用各自的临时输出目录，不得写入测试运行入口；它们不改变人工测试的单入口约束。

## 2. 用户故事

- 作为测试人员，我只需要记住 `dist/dev/mp-weixin`，构建、MCP 和人工验收不会在 `dist/build` 与 `dist/dev` 之间切换。
- 作为维护者，我希望构建开始前就发现微信开发者工具运行状态，不能先生成另一套产物再在 postbuild 阶段失败。
- 作为发布执行人员，我希望正式 Candidate 构建与测试运行入口隔离，测试命令不会改写正式候选或生产环境。

## 3. 功能需求

### 3.1 测试构建唯一输出

- WHEN 执行 `kaipai-frontend` 的 `npm run build:mp-weixin` THEN 构建必须通过 `UNI_OUTPUT_DIR` 直接写入 `dist/dev/mp-weixin`。
- WHEN 测试构建命令完成 THEN 不得依赖 `postbuild:mp-weixin` 或 `dist/build/mp-weixin -> dist/dev/mp-weixin` 镜像。
- WHEN 测试构建命令执行 THEN `dist/build/mp-weixin` 不得作为运行入口、成功判定或 MCP 项目路径。

### 3.2 构建前置保护

- WHEN 微信开发者工具进程存在 THEN 测试构建在清理或写入 `dist/dev/mp-weixin` 前失败，返回明确的进程占用结果。
- WHEN 微信开发者工具未运行 THEN 测试构建才可清理并生成固定运行目录，并在同一目录完成编码、实例 ID、开发编译设置和 scoped hash 校验。
- WHEN 测试构建失败 THEN 不得执行任何针对生产容器、生产数据库、正式 Nginx 或正式小程序的操作。

### 3.3 MCP 单一运行入口

- WHEN 调用 MCP 的构建、开页、刷新、截图、运行时、元素、页面或控制台工具 THEN 只允许固定 `dist/dev/mp-weixin`，schema 不再提供 `build` target。
- WHEN 调用 MCP 状态或产物检查 THEN 输出必须明确 `runtimeProject=dist/dev/mp-weixin`；不得打开或把 `dist/build/mp-weixin` 当作运行工程。

### 3.4 发布构建隔离

- WHEN 隔离 Candidate 构建或正式发布构建 THEN 使用调用方提供的隔离 `UNI_OUTPUT_DIR`，继续生成冻结候选或正式产物，但不触碰固定测试运行目录。
- WHEN 隔离构建完成 THEN 其产物只能通过既有 Candidate/发布流程交付，不改变 MCP 的唯一运行入口。

## 4. 验收标准

- `npm run build:mp-weixin` 的输出目录是 `dist/dev/mp-weixin`，且 package scripts 不再注册 `postbuild:mp-weixin` 镜像钩子。
- 测试构建脚本在 DevTools 运行时于任何输出写入前失败；静态门禁覆盖路径、命令和检查顺序。
- MCP tools/list 中所有运行工具的 target 枚举只有 `dev`，`projectForTarget('build')` 不存在，状态和产物检查不返回 build 运行项目。
- `npm run verify:single-runtime-entry` 通过；`npm run type-check`、`npm run verify:actor-card-skill-semantics` 和既有演员卡门禁通过。
- 正式后端、数据库、Nginx 和正式小程序保持不变，正式发布状态继续 `NOT_AUTHORIZED`。

## 5. 约束

- 不结束、重启、置顶、抢焦点或控制微信开发者工具，不使用桌面截图、坐标、键鼠自动化。
- 不执行 `reset --hard`、`checkout` 或批量清理既有工作区修改。
- 构建输出路径只允许是仓库内固定的 `kaipai-frontend/dist/dev/mp-weixin` 或隔离 Candidate 输出目录；脚本必须拒绝路径逃逸。
- 本 Spec 只治理构建与运行入口，不修改业务 API、数据库合同或演员卡展示语义。
