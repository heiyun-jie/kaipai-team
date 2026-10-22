# 00-224 任务清单

## T0 Spec 与边界

- [x] 建立 MCP 接入需求、命令边界和验收标准。
- [x] 确认微信 CLI 已提供 `open`、`quit`、`auto` 和 `agent` 命令。
- [x] 确认微信工具内置 `wechatide.cmd` skill CLI 与 `liteMode` 模拟器自动化工具注册表。
- [x] 将用户桌面非干扰纳入硬边界：不置顶、不强制前台、不抢焦点、不控制整屏、不使用桌面坐标或键鼠自动化。

## T1 实现

- [x] 创建无第三方依赖的 STDIO MCP 服务。
- [x] 添加固定项目路径、路由校验、超时和输出截断。
- [x] 添加项目级 `.codex/config.toml` 注册。
- [x] 添加本地 README 与调用示例。
- [x] 接入内部项目开窗、页面导航、模拟器截图、运行时、元素/页面自动化和 console 受限封装。
- [x] 将兼容入口 `open` / `enable_automation` 收口到内部 `liteMode`，不再调用桌面级 `auto`。
- [x] 对所有可能打开可见 DevTools 窗口的入口加入显式 `allowVisibleWindow` 护栏，未确认用户允许时默认拒绝开窗。

## T2 验证

- [x] 通过 JSON-RPC `initialize` 和 `tools/list` 握手测试。
- [x] 通过状态检查与 artifact check 只读测试。
- [x] 通过 CLI `--help` 验证命令入口可用。
- [x] 不结束普通微信或其他桌面进程；状态查询仅匹配微信开发者工具安装目录。
- [x] 通过内部 skill CLI 获取五个目标路由的模拟器截图并逐页对比参考图；证据见 `00-223/evidence.md` B01-B05。
- [x] 通过静态核验确认 MCP README、Spec 和工具描述均声明非干扰边界；后续正常用机期间不再调用未确认的可见开窗工具。
