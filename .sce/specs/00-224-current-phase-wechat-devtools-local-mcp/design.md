# 微信开发者工具本地 MCP 接入 - 技术设计

_Requirements: 3.1-3.4, 4_

## 1. 目录与配置

```text
tools/wechat-devtools-mcp/server.mjs     # 无第三方依赖的 STDIO MCP
tools/wechat-devtools-mcp/README.md      # 本地接入与边界说明
.codex/config.toml                       # 项目级 MCP 注册
```

服务通过 `node tools/wechat-devtools-mcp/server.mjs` 启动，工作目录固定为仓库根目录。项目级旧 CLI 默认路径为 `D:\AP\微信web开发者工具\cli.bat`；内部 skill CLI 默认路径为同目录的 `wechatide.cmd`，可分别通过 `WECHAT_DEVTOOLS_CLI` / `WECHATIDE_CLI` 覆盖。客户端名通过 `WECHATIDE_CLIENT_NAME` 配置，默认 `Codex`。

## 2. 工具契约

| 工具 | 读写 | 作用 |
|---|---|---|
| `wechat_devtools_status` | 只读 | 返回 CLI、前端目录、build/dev 目录和可识别进程信息 |
| `wechat_devtools_build` | 写 | 在 `kaipai-frontend` 执行 `npm run build:mp-weixin` |
| `wechat_devtools_artifact_check` | 只读 | 检查指定路由的 build/dev 三件套、SHA-256 和 scoped hash |
| `wechat_devtools_open` | 写 | 用内部 `open_project_window(liteMode)` 打开固定项目 |
| `wechat_devtools_quit` | 写 | 用 CLI 退出固定项目，不执行通用杀进程 |
| `wechat_devtools_enable_automation` | 写 | 兼容入口，改用内部 `liteMode` 开窗 |
| `wechat_devtools_open_project_window` / `close_project_window` | 写 | 只开/关内部模拟器项目窗口 |
| `wechat_devtools_open_page` / `refresh` | 写 | 内部编译、导航和刷新登记路由 |
| `wechat_devtools_screenshot` | 读 | 截取内部模拟器画面，证据输出路径受限 |
| `wechat_devtools_runtime_info` / `console` | 读 | 读取页栈、当前页、系统信息和受限 console |
| `wechat_devtools_element_action` / `page_action` | 写/读 | 通过微信注册的自动化接口操作页面元素或查询页面 |

输入参数只接受枚举、固定路由格式和有限整数。工具实现不得提供 `exec`、`powershell`、`shell` 或任意命令字符串参数。

## 3. MCP 协议

服务实现 JSON-RPC `initialize`、`notifications/initialized`、`ping`、`tools/list` 和 `tools/call`。STDIO 每行一个 JSON 消息，工具结果使用 MCP `content[type=text]` 返回；失败使用 `isError: true`，同时保留退出码、超时和 stderr 摘要。

## 4. 命令执行边界

- Windows `.bat` 命令只通过 Node 子进程调用，参数由服务内部生成。
- CLI 项目参数只能是 `dist/dev/mp-weixin` 或 `dist/build/mp-weixin`。
- 构建命令固定为 `npm run build:mp-weixin`，cwd 固定为 `kaipai-frontend`。
- 所有子进程有超时和输出上限；超时只终止当前子进程。
- 不实现按路径强杀进程；`close_project_window` 关闭项目窗口，`quit` 只调用微信 CLI 的项目级命令。

## 5. 产物核验

`wechat_devtools_artifact_check` 将 route 约束为 `pages/.../index` 或 `pkg-.../.../index` 形式，分别读取 `js`、`wxml`、`wxss`。它返回每侧文件是否存在、各文件 SHA-256、三件套 scoped hash 集合和 build/dev 是否完全一致。它不修改产物、不清理缓存。

## 6. 内部自动化边界

`wechatide.cmd` 的调用参数由 MCP 内部生成，项目只允许两个固定产物目录，页面只允许当前项目登记路由。`simulator_screenshot` 不传路径时使用微信工具临时文件；传路径时只允许 `.sce/evidence/wechat-devtools`。MCP 不提供 `exec`、PowerShell、桌面坐标或任意选择器以外的系统控制。

桌面非干扰是本 MCP 的硬边界：服务和调用方不得请求或模拟置顶、前台激活、焦点抢占、桌面截图、鼠标坐标或键盘输入。`open_project_window(liteMode)` 只作为用户明确允许的运行态核验证据入口；若当前微信开发者工具实现会创建可见置顶/抢焦点窗口，则该工具在用户正常使用电脑期间禁用，改走产物核验或用户提供截图。运行态核验结束后只允许调用 `close_project_window` 关闭固定项目窗口。
