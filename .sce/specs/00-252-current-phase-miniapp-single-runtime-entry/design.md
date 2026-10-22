# 当前阶段小程序单一测试运行入口 - 技术设计

_Requirements: 3.1-3.4, 4, 5_

## 1. 入口模型

```text
src + .env / explicit VITE_API_BASE_URL
                |
                v
npm run build:mp-weixin
                |
                +-- UNI_OUTPUT_DIR=kaipai-frontend/dist/dev/mp-weixin
                |
                v
fixed runtime project: dist/dev/mp-weixin
                |
                +-- MCP build/open/page/screenshot/runtime actions
```

`dist/dev/mp-weixin` 是唯一测试运行入口。测试命令不再产生工作区 `dist/build/mp-weixin`，也不执行 build 到 dev 的镜像。`dist/build` 仅可由隔离 Candidate/正式发布脚本使用，不能出现在 MCP 运行项目选择中。

## 2. 测试构建脚本

新增 `kaipai-frontend/scripts/build-mp-weixin-runtime.ps1`：

1. 解析并校验固定 `dist/dev/mp-weixin` 路径，拒绝路径逃逸。
2. 通过只读进程查询检查微信开发者工具；发现进程时在输出目录清理前失败。
3. 设置绝对 `UNI_OUTPUT_DIR` 到固定运行目录和默认测试 API `https://test-api.kplyyk.com`，显式环境变量可覆盖 API。
4. 执行 `npm run prepare:tdesign`，再调用本地 `node_modules/.bin/uni.cmd build -p mp-weixin`。
5. 调用 `sync-mp-weixin.ps1 -RuntimeOnly`，只对 `dist/dev` 做无 BOM、外链、实例 ID、开发编译设置和 scoped hash 校验；RuntimeOnly 同样在工具进程存在时失败，并在安全时清理 WeappCache。
6. 输出 `RUNTIME_PROJECT=...`、`RUNTIME_BUILD=PASS`，失败使用非零退出码。

`package.json` 将 `build:mp-weixin` 指向该脚本并移除 `postbuild:mp-weixin`。`build:mp-weixin:release` 不变，隔离 Candidate 构建器继续自行设置其 snapshot 的 `dist/build` 输出。

## 3. 同步脚本 RuntimeOnly 分支

`sync-mp-weixin.ps1` 增加 `-RuntimeOnly`：

- 目标固定为 `dist/dev/mp-weixin`，不读取或写入 `dist/build`。
- 复用现有归一化、`Remove-WeappCache`、`Set-DevCompileSettings` 与三件套 scoped hash 断言。
- 跳过 source 镜像和 robocopy，避免产生第二个运行源。
- 无参数模式默认等价于 `-RuntimeOnly`，因此任何普通手工调用也只处理 `dist/dev`；隔离发布/候选物化必须显式传入 `-SourceOnly` 或 `-ArtifactOnly`。

## 4. MCP 入口收口

`tools/wechat-devtools-mcp/server.mjs`：

- 删除 `buildProject` 和 `projectForTarget` 的 build 分支。
- 所有运行工具的 schema 只保留 `target: dev`，内部忽略或拒绝其他 target。
- `status` 返回 `runtimeProject`，`artifact_check` 仅检查固定运行目录的 js/wxml/wxss 完整性、SHA-256 和 scoped hash。
- `wechat_devtools_build` 仍调用 `npm run build:mp-weixin`，因此构建结果天然进入唯一运行入口。

## 5. 门禁与兼容

新增 `scripts/verify-single-runtime-entry.mjs`，静态检查 package scripts、RuntimeOnly 脚本、MCP target schema、固定路径和前置进程检查顺序。既有业务门禁保留；它们对 Candidate 的 build/dev 检查属于发布证据，不改变 MCP 的运行入口。

隔离 Candidate 构建器不复用工作区测试脚本，继续在临时 snapshot 中直接设置 `UNI_OUTPUT_DIR=dist/build/mp-weixin`，随后复制到冻结 `mini-program-test`。这样既保持正式发布兼容，也不会让工作区测试入口出现第二套运行目录。

## 6. 回滚

回滚只恢复 `package.json`、RuntimeOnly/构建脚本和 MCP 入口文件的原始内容；不删除用户已有的 `dist/build` 或 `dist/dev`，不操作微信工具和生产环境。回滚验证在独立副本运行，实际工作区保持修改态。
