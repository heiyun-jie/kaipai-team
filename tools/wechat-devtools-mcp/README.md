# `kaipai-wechat-devtools` 本地 MCP

这是一个项目内 STDIO MCP，用来把当前仓库的小程序构建、固定 `dist/dev/mp-weixin` 运行产物核验和微信开发者工具运行态核验接入 Codex。它只使用 Node 内置模块，不安装 npm 包，不接入远程 MCP。运行态操作调用微信开发者工具自带的 `wechatide` skill CLI，并固定使用 `liteMode` 模拟器，不激活或截图 Windows 桌面。

## 桌面非干扰规则

本 MCP 的默认边界是“不影响用户正常使用电脑”：不得置顶、强制前台、抢占焦点、控制整屏，也不得使用 Windows 桌面截图、坐标点击、鼠标或键盘自动化。

`wechat_devtools_open`、`wechat_devtools_enable_automation` 和 `wechat_devtools_open_project_window` 可能创建或抬起可见微信开发者工具窗口，因此必须在用户明确允许可见窗口核验后传入 `allowVisibleWindow: true`。未传该参数时工具会拒绝开窗；正常用机期间应改用 `wechat_devtools_artifact_check`、不抬起窗口的内部读取能力或用户提供截图。

## 接入方式

项目根目录的 `.codex/config.toml` 已登记：

```toml
[mcp_servers.wechat_devtools]
type = "stdio"
command = "node"
args = ["tools/wechat-devtools-mcp/server.mjs"]
cwd = "D:\\XM\\kaipai-team"
default_tools_approval_mode = "writes"
```

如微信开发者工具安装位置不同，可在 MCP 配置的 `env` 中设置 `WECHAT_DEVTOOLS_CLI`（显式项目退出命令）和 `WECHATIDE_CLI`（内部 skill CLI）；两个值都必须是已存在的 `.bat` 或 `.cmd` 文件。当前本机路径分别是 `D:\AP\微信web开发者工具\cli.bat` 和 `D:\AP\微信web开发者工具\wechatide.cmd`。`WECHATIDE_CLIENT_NAME` 可覆盖 skill CLI 客户端名，默认 `Codex`。

## 工具

- `wechat_devtools_status`：只读检查 CLI、固定项目目录和可识别的 DevTools 进程。
- `wechat_devtools_build`：在 `kaipai-frontend` 执行 `npm run build:mp-weixin`，输出截断并带超时。
- `wechat_devtools_artifact_check`：核对固定 `dist/dev/mp-weixin` 指定路由的三件套、SHA-256 和 `data-v-*`。
- `wechat_devtools_open`：只打开固定的 `dist/dev/mp-weixin`；必须先确认用户允许可见窗口核验并传 `allowVisibleWindow: true`。
- `wechat_devtools_quit`：只调用微信 CLI 的项目级 `quit`。
- `wechat_devtools_enable_automation`：兼容旧入口，改为内部 `liteMode` 开窗，不调用桌面级 `auto`；必须先确认用户允许可见窗口核验并传 `allowVisibleWindow: true`。
- `wechat_devtools_open_project_window` / `wechat_devtools_close_project_window`：只操作内部模拟器项目窗口；打开窗口必须先确认用户允许可见窗口核验并传 `allowVisibleWindow: true`，关闭窗口只关闭固定项目。
- `wechat_devtools_open_page` / `wechat_devtools_refresh`：在模拟器内部导航或刷新登记路由。
- `wechat_devtools_screenshot`：只截取模拟器画面；指定输出路径时必须位于 `.sce/evidence/wechat-devtools`。
- `wechat_devtools_runtime_info` / `wechat_devtools_console`：读取运行时页栈、当前页、系统信息和受限 grep console。
- `wechat_devtools_element_action` / `wechat_devtools_page_action`：调用微信工具注册的页面元素/页面自动化接口。

服务没有通用 shell 工具，也不接收任意命令、任意 cwd 或任意项目路径。`quit` 不使用 `Stop-Process`，因此不会按宽泛进程名结束普通微信或其他应用。

## 手工握手测试

```powershell
node tools/wechat-devtools-mcp/server.mjs
```

随后逐行发送 JSON-RPC `initialize` 和 `tools/list` 请求即可。服务的 stdout 只用于 MCP 协议，诊断信息写入 stderr。

页面级截图、模拟器 DOM 和控制台日志是否可用，仍取决于当前微信开发者工具版本暴露的自动化接口；本 MCP 不把未验证的 Agent 卡片 DOM 当成小程序页面 DOM。
