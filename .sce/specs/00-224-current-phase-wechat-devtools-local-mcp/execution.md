# 00-224 执行记录

## 2026-08-18

- 已确认本机项目级 CLI：`D:\AP\微信web开发者工具\cli.bat`；内部 skill CLI：`D:\AP\微信web开发者工具\wechatide.cmd`（版本 `0.3.5`）。
- `cli.bat --help` 已确认提供 `open`、`quit`、`auto`、`agent` 等命令。
- 仅新增项目级 MCP 配置，不改用户全局 MCP 配置，不安装第三方 npm 包。
- `initialize` / `tools/list` 握手通过；工具清单已扩展为构建/产物核验、内部 liteMode 开窗、页面导航、模拟器截图、运行时、元素/页面自动化和 console。
- `wechat_devtools_status` 通过：CLI、`dist/build/mp-weixin`、`dist/dev/mp-weixin` 均存在。
- `wechat_devtools_artifact_check` 通过：`pages/home/index` build/dev 三件套完整且 `buildDevEquivalent=true`；首页 WXSS SHA-256 为 `7B7107DE87F973EFA302F687E118E47D1B8E7CA8E1BBC5B3339AE76394375880`。
- 通过 MCP 调用 `wechat_devtools_open(target=dev)`，CLI 返回码 `0`；通过 `wechat_devtools_enable_automation(target=dev, trustProject=true)`，CLI 返回码 `0`。
- 越界路由 `../../Windows` 被 MCP 输入校验拒绝；未执行任意命令。
- `codex mcp list` 已识别项目级 `wechat_devtools` 配置。当前 CLI 输出的 `Unsupported` 状态与既有本地 MCP 列表一致，不能作为服务握手失败证据；本地 STDIO 握手已单独通过。
- 状态查询已按微信开发者工具安装目录匹配可执行进程，并仅返回 PID / 进程名 / 可执行路径；普通 `Weixin.exe` 不在匹配范围内，也不读取进程命令行中的敏感参数。
- 旧 `open` / `enable_automation` 入口已改为内部 `open_project_window --window-mode liteMode`；不再调用 `cli.bat auto`，不再使用 Windows 桌面截图或坐标点击。
- 首次 `wechatide.cmd -c Codex check_wechatide_status --skill-version 0.3.5` 返回 `pending + taskId`；随后固定项目的 `open_project_window`、`simulator_open_page` 和 `simulator_screenshot` 均返回成功，五页内部截图证据已写入 `00-223` B01-B05。该状态提示仍作为环境事实保留，不把它误写成页面代码错误。
- `automation_page_action(querySelectorAll)` 成功回读创建 Hub 的 7 个步骤节点；`automation_element_action(style)` 成功回读首页 Hero 标题 `20px / 700`、CTA `101px × 33px` 和文字 `14px`，证明字体/按钮核验可在模拟器内部完成。

## 2026-08-19

- 用户明确要求：微信开发者工具核验不得置顶、不得影响其电脑正常使用。
- 已将桌面非干扰升级为 MCP 硬边界：不置顶、不强制前台、不抢焦点、不控制整屏、不使用桌面截图 / 坐标 / 键鼠自动化。
- 后续 `open` / `enable_automation` / `open_project_window` 这类可能创建可见窗口的入口，必须带有明确用户授权语义；正常用机期间默认改走产物核验、不会抬起桌面的内部接口或用户提供截图。
- 用户进一步明确“不要让我退出，自己操作 MCP 工具去调用微信小程序”后，本轮复核改为项目级 MCP 闭环：`wechat_devtools_close_project_window(target=dev)` 仅关闭固定项目 `D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin` 的窗口，返回 `success=true`、`winId=s0`。
- `wechat_devtools_build(timeoutMs=300000)` 成功执行 `npm run build:mp-weixin`，清理 DevTools `WeappCache`，完成 `dist/build` → `dist/dev` 同步，并通过双侧 scoped style hash 一致性断言。
- `wechat_devtools_artifact_check(route=pages/home/index)` 与 `wechat_devtools_artifact_check(route=pages/mine/index)` 均返回 `buildDevEquivalent=true`；首页 WXSS SHA-256 为 `42B9A94A15A19C80CA02B06A5868CC6CE4747172CCCC98997939194B20C3C9FB`，个人中心 WXSS SHA-256 为 `8CA2AF6B21B4D9703F5282B66E64D8DBB245F56ED770EABFA525F18B8087AC36`。
- `wechat_devtools_open(target=dev)` 成功打开固定 dev 项目，`wechat_devtools_open_page(route=pages/mine/index)` 成功进入个人中心；`wechat_devtools_screenshot` 采集 `.sce/evidence/wechat-devtools/mine-density-20260819-mcp-rerun.png`（593 x 1280，SHA-256 `C1BC43A1E0DFB65ADC2BBE2FD722A53F7D6C9FCAA3BEAECF353A06EAE63701DA`）。
- `wechat_devtools_console(command=grep -i error)` 返回空；本轮未使用 Windows 桌面截图、坐标点击、键鼠自动化、置顶或整屏控制。
- 同日继续对齐 R05 个人中心后，重复 MCP 闭环：`wechat_devtools_close_project_window(target=dev)` 成功，`wechat_devtools_build(timeoutMs=300000)` 成功，`wechat_devtools_artifact_check(route=pages/mine/index)` 与 `wechat_devtools_artifact_check(route=pkg-tools/webview/index)` 均返回 `buildDevEquivalent=true`。个人中心最新 WXSS SHA-256 为 `EB65BD76160371A3E93E3072E3D166CDC36EF833E7FE25EDDFE614C8CAED25BF`；`pkg-tools/webview/index` scoped hash 为 `data-v-5376f887` 且三件套一致。
- 本轮最新内部模拟器截图为 `.sce/evidence/wechat-devtools/mine-reference-align-20260819-v2.png`（593 x 1280，SHA-256 `1FA877486FD3D108C877EDDB24EC25D17E566B6A4191AD2E53C10737F8213205`）。`pkg-tools/webview/index?type=support&title=帮助与反馈` 与 `pkg-tools/webview/index?type=preferences&title=设置` 均通过 `simulator_open_page` 和 `automation_runtime_info` 确认可达；`get_simulator_console(grep -i error)` 返回空。
- 交接后追加非干扰复核：`wechat_devtools_open_page(route=pages/mine/index,target=dev)` 成功，`wechat_devtools_screenshot(wait=1)` 采集 `.sce/evidence/wechat-devtools/mine-reference-align-20260819-final.png`（593 x 1280，SHA-256 `1FA877486FD3D108C877EDDB24EC25D17E566B6A4191AD2E53C10737F8213205`），与 B07 哈希一致；本次只使用固定项目 MCP 内部模拟器接口，未使用 Windows 桌面截图、坐标点击、键鼠自动化、置顶或整屏控制。
- 用户继续指出 R05 的「演员资料 / 账户与服务」字体与间距偏离后，追加第三轮 MCP 闭环：第一次构建因固定 dev 项目窗口仍开着被 `sync-mp-weixin.ps1` 保护拦截；随后 `wechat_devtools_close_project_window(target=dev)` 仅关闭固定项目窗口，重跑 `wechat_devtools_build(timeoutMs=300000)` 成功清理 WeappCache、构建并同步 `dist/build` 到 `dist/dev`。`wechat_devtools_artifact_check(route=pages/mine/index)` 返回 `buildDevEquivalent=true`，个人中心最新 WXSS SHA-256 为 `49BE387284437019C389E436039072E0FDAE5D8A1DDAF1C6F2A19BD01B08A4CC`；`pkg-tools/webview/index` 同步复核 `buildDevEquivalent=true`、scoped hash `data-v-5376f887`。内部模拟器截图 `.sce/evidence/wechat-devtools/mine-list-density-20260819-v4-retry.png`（593 x 1280，SHA-256 `80B40E80589DC31DFF89EAA8E693A020C4A95C1B6166159FA61694B46FFBACFD`）和同宽并排图 `.sce/evidence/wechat-devtools/mine-groups-v4-compare-20260819.png`（1730 x 939，SHA-256 `8B39D3A00804807C509CA97CB359EE1C4A0C237C6DC2E7822ED68F4364980460`）已归档；本轮仍未使用 Windows 桌面截图、坐标点击、键鼠自动化、置顶或整屏控制。
