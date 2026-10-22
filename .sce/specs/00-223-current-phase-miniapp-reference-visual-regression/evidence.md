# 00-223 运行态截图证据与差异矩阵

> 采集日期：2026-08-18。证据分为 A（用户此前提供的历史窗口截图）和 B（本轮由微信开发者工具内置 `wechatide` skill CLI 的 `simulator_screenshot` 采集）。B 组只包含模拟器画面，不包含 Windows 桌面、其他应用或坐标点击。
>
> 本文件区分“当前运行态证据”“已修改源码”和“构建后可验收结果”。截图中没有 DevTools 元素面板，不能从图像推导某个 `data-v` 值；截图哈希用于锁定图像版本，组件产物哈希只用于当时磁盘产物的一致性核验。

## 1. 证据清单

| ID | 运行态截图 | 尺寸 | SHA-256 | 路由 / 状态 | 对应参考图 | 结论 |
|---|---|---:|---|---|---|---|
| A01 | `C:\Users\33340\AppData\Local\Temp\codex-clipboard-2de4489a-d137-4789-893d-5aae256690f2.png` | 748 x 1598 | `CA8FC2E8C056A774CA33534CB5E434A2BF964810A2CAC102F57DA474C7753413` | `pages/home/index`；登录态；经典 Tab；有 2 张草稿 | R01 | 当前产物截图，待重新构建后复测 |
| A02 | `C:\Users\33340\AppData\Local\Temp\codex-clipboard-8f5b2134-3bb9-4cab-a89d-07f3832e47e7.png` | 741 x 1592 | `AA4F11D7C452059A15DDBC657EAD3254AC266CC7BCED379E1C896F84926688F4` | `pkg-actor-card/create/index`；`0/7` | R02 | 当前产物截图，待重新构建后复测 |
| A03 | 未提供 | - | - | `pkg-actor-card/step-works/index` | R03 | 无运行态截图，不做视觉通过结论 |
| A04 | 未提供 | - | - | `pkg-actor-card/step-photos/index` | R04 | 无运行态截图，不做视觉通过结论 |
| A05 | `C:\Users\33340\AppData\Local\Temp\codex-clipboard-29ebc76e-0b62-4bab-b922-5c2ac04e86db.png` | 711 x 1552 | `27C8EF480876D9E3F5FD5B990448712F9126F63A0D28F4D0C334DC15BE099505` | `pages/mine/index`；登录态；未认证；完整度 90% | R05 | 当前产物截图，待重新构建后复测 |
| C01 | `C:\Users\33340\AppData\Local\Temp\codex-clipboard-13c3f9d3-d635-4885-a3b4-0667a30c953d.png` | 751 x 1586 | `A3A5304C7A822A810AB1625C1D64F1A18141C6B3CA8C5177F6A95AA4EF416C83` | `pages/card-list/index`；已发布 Tab | 无对应图稿 | 记录为 3.0 风格一致性页面，不做像素级比对 |
| C02 | `C:\Users\33340\AppData\Local\Temp\codex-clipboard-3914265d-9936-403e-92ae-49f44c0e0a52.png` | 752 x 1584 | `709550EB218092786B908AF4CC349D95CD3A9FEB96427E6EA99D8B93777BC183` | `pages/assets/index`；照片 Tab 空态 | 无对应图稿 | 记录为 3.0 风格一致性页面，不做像素级比对 |

## 1.2 B 组：内部模拟器逐页截图

| ID | 内部截图 | 尺寸 | SHA-256 | 路由 / 运行态 | 参考图 | 证据边界 |
|---|---|---:|---|---|---|---|
| B01 | `.sce/evidence/wechat-devtools/home.png` | 702 x 1520 | `C46647B194D08B3D07F0CE875FDD5AF11040C948ACCAB13C8AF9B32AFA394580` | `pages/home/index`；用户 6737；2 张草稿；经典 Tab | R01 | 仅模拟器画面 |
| B02 | `.sce/evidence/wechat-devtools/create.png` | 702 x 1520 | `6327137C4188973435A1C008B02AE48D9CBAE917C70CD599CBAE62B92D1079E2` | `pkg-actor-card/create/index`；0/7；空草稿 | R02 | 仅模拟器画面 |
| B03 | `.sce/evidence/wechat-devtools/works.png` | 702 x 1520 | `6BD326B6276DB91337C3DBD3CA7030B50F8BB10E60AD6DB00373FF4A80E618D3` | `pkg-actor-card/step-works/index`；3/7；无已选作品 | R03 | 仅模拟器画面 |
| B04 | `.sce/evidence/wechat-devtools/photos.png` | 702 x 1520 | `1D9ABD7DAA6B1FCA58CF1D8915644DDA299C3C3C7EECD463306F9317FB793A3D` | `pkg-actor-card/step-photos/index`；4/7；草稿未就绪错误态 | R04 | 仅模拟器画面 |
| B05 | `.sce/evidence/wechat-devtools/mine.png` | 702 x 1520 | `DB19CB28E163BDE5FE2EBB7D24ABADF551937F0B6CA5D45DE44066EC10DF2699` | `pages/mine/index`；用户 6737；完整度 90% | R05 | 仅模拟器画面 |
| B06 | `.sce/evidence/wechat-devtools/mine-density-20260819-mcp-rerun.png` | 593 x 1280 | `C1BC43A1E0DFB65ADC2BBE2FD722A53F7D6C9FCAA3BEAECF353A06EAE63701DA` | `pages/mine/index`；用户 6737；完整度 90%；MCP 构建同步后复测 | R05 | 仅模拟器画面 |
| B07 | `.sce/evidence/wechat-devtools/mine-reference-align-20260819-v2.png` | 593 x 1280 | `1FA877486FD3D108C877EDDB24EC25D17E566B6A4191AD2E53C10737F8213205` | `pages/mine/index`；用户 6737；完整度 90%；三行服务区复测 | R05 | 仅模拟器画面 |

B 组采集链路：`open_project_window(windowMode=liteMode)` → `simulator_open_page` → `simulator_screenshot(optimize=false)`。运行时页栈由 `automation_runtime_info` 回读；内部 console 使用 `get_simulator_console(grep -i error)`，本轮无命中。首次创建页编译出现一次工具侧 `APPID_ERROR`，重试后成功，不把该次工具错误归因于页面样式。

B06 补充链路：用户明确要求改用 MCP 后，先执行 `wechat_devtools_close_project_window(target=dev)`，仅关闭固定项目 `kaipai-frontend/dist/dev/mp-weixin` 的窗口；随后 `wechat_devtools_build(timeoutMs=300000)` 清理 WeappCache、构建并同步 `dist/build` 到 `dist/dev`；再执行 `wechat_devtools_open(target=dev)`、`wechat_devtools_open_page(route=pages/mine/index)` 和 `wechat_devtools_screenshot`。全程不使用 Windows 桌面截图、坐标点击、置顶或键鼠自动化。

B07 补充链路：在 B06 基础上按用户再次提供的 R05 参考图复核，恢复三行服务区并将帮助与反馈、设置绑定到真实 `pkg-tools/webview/index` 内容页；再按 MCP 项目级流程关闭固定 dev 项目、构建同步、产物等价检查、内部模拟器打开 `pages/mine/index` 并截图。随后直接打开 `pkg-tools/webview/index?type=support&title=帮助与反馈` 与 `pkg-tools/webview/index?type=preferences&title=设置`，均返回当前页可达；内部 console `grep -i error` 无命中。

## 1.3 R01 字体与按钮定位

用户在 2026-08-18 的对比图中标出了首页 Hero 标题和“开始创建”按钮。本轮先锁定这两个直接样式锚点：

| 锚点 | 同步前实际值 | 参考图归一目标 | 处理 |
|---|---|---|---|
| `home-v2__hero-title` | `48rpx / 700 / 1.2` | 约 `40rpx / 700 / 1.2` | 改为 `40rpx`，不改文案和字重 |
| `home-v2__hero-btn` | `width:auto`、`min-width:216rpx`、`height:88rpx`、`padding:0 32rpx`、文字 `28rpx` | 约 `196rpx × 64rpx`，文字 `28rpx` | 固定 `width/height`，清除水平内边距，保留真实 `goCreate` handler；避开组件专用 `200rpx` 胶囊魔数 |

当前截图中的按钮被撑满 Hero 左栏，根因是 `width:auto` 与原生 button 默认块级布局叠加，不是点击区域失效。修改后按钮的视觉尺寸变小，但仍保留完整 196rpx × 64rpx 点击区。

本轮通过内部 `automation_element_action(action=style)` 回读 B01 实际计算值：`.home-v2__hero-title` 为 `20px / 700`，`.home-v2__hero-btn` 为 `101px × 33px`、文字 `14px`；按模拟器 2x 逻辑像素折算，分别对应约 `40rpx / 700`、`196rpx × 64rpx` 和 `28rpx`，与源码目标一致。

## 1.5 R01 继续编辑草稿标题收口

用户在本轮进一步指出首页「继续编辑」草稿标题字号偏大。已将该锚点收口到正文档层级并完成运行态复核：

| 锚点 | 当前值 | 说明 |
|---|---|---|
| `home-v2__draft-title` | `14px / 700 / 16.8px` | 内部模拟器读取结果，对应约 `28rpx / 700 / 1.2` |
| 证据截图 | `.sce/evidence/wechat-devtools/home-draft-title-font-20260819.png` | 内部模拟器截图，当前运行态可见 |

这次收口的目标不是把草稿标题做成 H2，而是让它回到参考图中更克制的正文档层级，避免和 Hero 主标题争抢视觉权重。

## 1.6 R01 草稿操作与模板 Tab 细节收口

继续优化 R01 首页时，只调整两个直接视觉锚点：

| 锚点 | 修改前 | 修改后 / 运行态 | 说明 |
|---|---|---|---|
| `home-v2__draft-resume` | `28rpx / 700` | 内部模拟器读数 `14px / 500` | 仍是 28rpx 链接，但从主按钮权重降为中等权重 |
| `home-v2__style-tab--active::after` | 左右各留 `20rpx`，下划线按 Tab 宽度拉长 | `width: 56rpx` 且居中 | 更接近参考图的文字短下划线 |
| 证据截图 | - | `.sce/evidence/wechat-devtools/home-tab-draft-refine-20260819.png` | 只含内部模拟器画面 |

本轮不改变 Tab 的真实风格过滤、不改背景图数据和模板创建行为。

## 1.7 R01 Hero 纵向密度与插画比例收口

用户要求继续优化首页 Hero 的纵向密度和插画比例。本轮只调整 `home-v2__hero` 这一组直接视觉锚点，不改首页模板过滤、草稿继续编辑、`goCreate` 或背景库 API。

| 锚点 | 修改前 | 修改后 / 目标 | 说明 |
|---|---|---|---|
| `home-v2__hero` | `min-height: 392rpx; padding: 40rpx 36rpx` | `min-height: 416rpx; padding: 46rpx 28rpx 42rpx 48rpx` | Hero 外高略增，左侧起点更贴近参考图；右侧留出插画放大空间 |
| `home-v2__hero-mark` | `68rpx × 60rpx; margin-bottom: 12rpx` | `72rpx × 64rpx; margin-bottom: 16rpx` | 星芒与标题间距更接近参考图的纵向呼吸 |
| `home-v2__hero-title` | `margin-bottom: 12rpx` | `margin-bottom: 14rpx` | 字号继续保持 `40rpx / 700 / 1.2`，只微调标题到说明的距离 |
| `home-v2__hero-btn` | `margin-top: 28rpx` | `margin-top: 34rpx` | 按钮尺寸仍是 `196rpx × 64rpx`，仅拉开与说明文案的距离 |
| `home-v2__card-illus` | `210rpx × 250rpx` | `246rpx × 292rpx` | 插画占 Hero 右侧高度比例上调，避免右半边显空 |
| `home-v2__card-illus-front` | `154rpx × 210rpx` | `174rpx × 240rpx` | 前景演员卡更接近参考图主卡体量 |
| `home-v2__card-illus-orbit` | `252rpx × 86rpx` | `300rpx × 100rpx` | 环线随插画同步放大，仍作为纯装饰层 |

静态核验：`npm run verify:v3-home` 通过 `17/17`，`npm run type-check` 通过。`npm run build:mp-weixin` 的 uni build 阶段已完成，`dist/build/mp-weixin/pages/home/index.wxss` 已生成本轮新值，SHA-256 为 `42B9A94A15A19C80CA02B06A5868CC6CE4747172CCCC98997939194B20C3C9FB`。

2026-08-19 用户明确要求改用 MCP 后，已通过 `wechat_devtools_close_project_window(target=dev)` 仅关闭固定 dev 项目窗口，再执行 `wechat_devtools_build(timeoutMs=300000)` 完成构建同步。`wechat_devtools_artifact_check(route=pages/home/index)` 返回 `buildDevEquivalent=true`，首页 WXSS 在 `dist/build` 与 `dist/dev` 的 SHA-256 均为 `42B9A94A15A19C80CA02B06A5868CC6CE4747172CCCC98997939194B20C3C9FB`。本轮未再要求用户退出，也未使用桌面级自动化；首页如需新的运行态视觉结论，继续通过内部 `simulator_screenshot` 补图。

## 1.8 R05 个人中心顶部卡片与列表密度收口

用户要求开始对齐个人中心。本轮只调整 `pages/mine/index` 的可见视觉容器，不改个人资料、演艺经历、自我介绍、实名认证、统计跳转和退出确认等真实交互。

| 锚点 | 修改前 | 修改后 / 目标 | 说明 |
|---|---|---|---|
| `mine-v2__profile-card` | 仅 `padding: 32rpx`，无显式外高合同 | `box-sizing: border-box; min-height: 192rpx` | 头像继续保持 `128rpx`，只锁定参考图档案卡外高 |
| `mine-v2__completeness-card` | `padding: 32rpx; margin-bottom: 24rpx` | `min-height: 168rpx; padding: 28rpx 32rpx 26rpx; margin-bottom: 20rpx` | 完整度卡向参考图收紧，仍保留错误重试扩展态 |
| `mine-v2__completeness-pct` | `32rpx` | `40rpx / 700 / 1.2` | 让百分比恢复参考图里的主强调层级 |
| `mine-v2__stats-row` | `min-height: 144rpx; padding: 28rpx 0; margin-bottom: 40rpx` | `min-height: 136rpx; padding: 20rpx 0; margin-bottom: 36rpx` | 统计卡整体降低一档，靠近参考图紧凑比例 |
| `mine-v2__stat-value` | `48rpx / 700 / 1` | `40rpx / 700 / 1.2` | 统计数字从 Display 降为 H1，避免抢过页面标题 |
| `mine-v2__row` | `min-height: 124rpx; padding: 26rpx 28rpx` | `min-height: 116rpx; padding: 20rpx 28rpx` | 双行资料列表收紧为参考图的轻量分组行 |
| `mine-v2__row-icon` | `56rpx × 56rpx` | `52rpx × 52rpx` | 图标随行高轻微收敛，仍是 CSS 线性图标 |

静态核验：`npm run verify:v3-mine` 通过 `16/16`，`npm run type-check` 通过。`npm run build:mp-weixin` 的 uni build 阶段已完成，`dist/build/mp-weixin/pages/mine/index.wxss` 已生成本轮新值，SHA-256 为 `8CA2AF6B21B4D9703F5282B66E64D8DBB245F56ED770EABFA525F18B8087AC36`。

2026-08-19 用户明确要求改用 MCP 后，已通过 `wechat_devtools_close_project_window(target=dev)` 仅关闭固定 dev 项目窗口，再执行 `wechat_devtools_build(timeoutMs=300000)` 完成构建同步。第一次 R05 复测产物中个人中心 WXSS 在 `dist/build` 与 `dist/dev` 的 SHA-256 均为 `8CA2AF6B21B4D9703F5282B66E64D8DBB245F56ED770EABFA525F18B8087AC36`。随后内部模拟器打开 `pages/mine/index` 并采集 B06，`get_simulator_console(grep -i error)` 无命中。

用户再次提供 R05 参考图后，本轮进一步对齐真实锚点：档案头像放大到 `148rpx`，档案卡保留 `192rpx` 外高并将内边距收为 `22rpx 28rpx 22rpx 22rpx`；完整度卡收为 `160rpx`，统计卡收为 `128rpx`，资料双行列表收为 `112rpx`，服务单行收为 `72rpx`；服务区恢复「实名认证 / 帮助与反馈 / 设置」三行，帮助和设置分别指向 `pkg-tools/webview` 的 `support` 与 `preferences` 真实页面；主页面红色退出按钮移除，退出保留在设置页。第二次 MCP 复测中 `pages/mine/index` `buildDevEquivalent=true`，个人中心 WXSS build/dev SHA-256 均为 `EB65BD76160371A3E93E3072E3D166CDC36EF833E7FE25EDDFE614C8CAED25BF`，B07 可见三行服务区完整露出且箭头在最右侧。

## 1.4 同步后运行态观察

> 本节只记录 A 组历史窗口观察，保留作修改前上下文；本轮 B 组复测已改用微信工具内部模拟器接口，不再激活窗口、点击坐标或截取桌面。

| 字段 | 结果 |
|---|---|
| 观察方式 | 历史窗口观察方式（已废弃，不再采用）：曾在用户授权后关闭微信开发者工具进程并通过可见窗口观察；2026-08-19 起改用 00-224 MCP 项目级闭环 |
| 工程窗口 | `开拍了演员卡`；页面路径显示为 `pages/home/index` |
| 运行态结果 | Hero 标题已不再使用旧的过大字号；“开始创建”已不再撑满左栏，呈现紧凑固定宽度，和 R01 参考图的层级关系一致 |
| 交互范围 | 本轮只做视觉观察，没有点击按钮、跳转页面或修改业务数据 |
| 独立告警 | 控制台出现 `simulator launch failed` 红色日志，但模拟器页面仍正常渲染；该告警不归因于本轮字体 / CTA CSS，需另行处理 |

> 由于窗口截图由运行态观察工具即时生成而未写入用户临时目录，本条作为窗口观察记录，不替代用户提供的持久化逐页截图哈希。像素级最终验收仍以相同设备宽度截图为准。

## 1.9 2026-08-19 MCP 非干扰复核

用户明确指出“不应再要求手动退出，应由 MCP 调用微信小程序”。本轮复核采用 `00-224` 的项目级 MCP 工具：

| 项目 | 结果 |
|---|---|
| 固定项目 | `D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin` |
| 项目级关闭 | `wechat_devtools_close_project_window(target=dev)` 成功，返回 `winId=s0` |
| 构建同步 | `wechat_devtools_build(timeoutMs=300000)` 成功，已清理 WeappCache，并同步 `dist/build` 到 `dist/dev` |
| 首页产物 | `pages/home/index` 的 build/dev 三件套完整且 `buildDevEquivalent=true`；WXSS SHA-256：`42B9A94A15A19C80CA02B06A5868CC6CE4747172CCCC98997939194B20C3C9FB` |
| 个人中心产物 | `pages/mine/index` 的 build/dev 三件套完整且 `buildDevEquivalent=true`；最新 WXSS SHA-256：`EB65BD76160371A3E93E3072E3D166CDC36EF833E7FE25EDDFE614C8CAED25BF` |
| 运行态 | `wechat_devtools_open(target=dev)` 后 `wechat_devtools_open_page(route=pages/mine/index)` 成功 |
| 截图 | B06：`.sce/evidence/wechat-devtools/mine-density-20260819-mcp-rerun.png`，593 x 1280，SHA-256 `C1BC43A1E0DFB65ADC2BBE2FD722A53F7D6C9FCAA3BEAECF353A06EAE63701DA`；B07：`.sce/evidence/wechat-devtools/mine-reference-align-20260819-v2.png`，593 x 1280，SHA-256 `1FA877486FD3D108C877EDDB24EC25D17E566B6A4191AD2E53C10737F8213205`；final：`.sce/evidence/wechat-devtools/mine-reference-align-20260819-final.png`，593 x 1280，SHA-256 同 B07，确认复核无视觉漂移 |
| 控制台 | `get_simulator_console(grep -i error)` 返回空 |
| 桌面边界 | 不置顶、不抢焦点、不控制整屏、不用桌面截图 / 坐标 / 键鼠自动化 |

## 1.10 2026-08-19 R05 列表字体与间距追加复核

用户指出“演员资料”和“账户与服务”分组内字体与间距仍明显偏离参考图。本轮只调整 `pages/mine/index` 的列表内部直接锚点，不改顶部档案卡、完整度、统计卡、TabBar 或真实路由：

| 项目 | 结果 |
|---|---|
| 视觉锚点 | `mine-v2__section-group`、`mine-v2__row`、`mine-v2__row--service`、`mine-v2__row-title`、`mine-v2__row-sub`、`mine-v2__row-icon`、`mine-v2__row-arrow` |
| 源码修正 | 资料行主文案 `26rpx`、副文案 `22rpx`、副文案上间距 `6rpx`；服务行 `76rpx`、主文案 `24rpx`、服务行 `gap: 12rpx`、`padding: 12rpx 28rpx 12rpx 24rpx`；图标描边 `2rpx`；实名认证恢复盾牌图标；右箭头取消缩放 |
| 构建同步 | `wechat_devtools_build(timeoutMs=300000)` 成功，已清理 WeappCache，并同步 `dist/build` 到 `dist/dev` |
| 个人中心产物 | `pages/mine/index` 的 build/dev 三件套完整且 `buildDevEquivalent=true`；最新 WXSS SHA-256：`49BE387284437019C389E436039072E0FDAE5D8A1DDAF1C6F2A19BD01B08A4CC` |
| 承载页产物 | `pkg-tools/webview/index` 的 build/dev 三件套完整且 `buildDevEquivalent=true`；scoped hash `data-v-5376f887` |
| 截图 | v4：`.sce/evidence/wechat-devtools/mine-list-density-20260819-v4-retry.png`，593 x 1280，SHA-256 `80B40E80589DC31DFF89EAA8E693A020C4A95C1B6166159FA61694B46FFBACFD`；同宽并排图：`.sce/evidence/wechat-devtools/mine-groups-v4-compare-20260819.png`，1730 x 939，SHA-256 `8B39D3A00804807C509CA97CB359EE1C4A0C237C6DC2E7822ED68F4364980460` |
| 桌面边界 | 只使用固定项目 MCP 内部模拟器接口；未使用 Windows 桌面截图、坐标点击、键鼠自动化、置顶或整屏控制 |

## 2. 当前三层产物结论

核验时间：2026-08-18。该节记录早期可见窗口观察结论；2026-08-19 起已被 00-224 MCP 项目级闭环替代，后续不得再依赖用户手动退出、置顶、桌面截图或整屏控制。

| 层级 | 观察到的事实 | 结论 |
|---|---|---|
| `src` | `KpPageNav.centerTitle`、`KpCreateProgress.showLabel`、首页白色画布 / 40rpx 留白；本轮 R01 Hero 标题为 `40rpx`，CTA 为 `196rpx × 64rpx` | 源码已完成本轮字体与按钮锚点收口 |
| `dist/build/mp-weixin` | 20:30 最新编译成功；已生成 `40rpx` 标题、`196rpx × 64rpx` CTA。首页 WXSS SHA-256：`7B7107DE87F973EFA302F687E118E47D1B8E7CA8E1BBC5B3339AE76394375880` | build 已含本轮改动 |
| `dist/dev/mp-weixin` | 20:30 同步成功；首页 WXSS SHA-256 与 build 完全一致：`7B7107DE87F973EFA302F687E118E47D1B8E7CA8E1BBC5B3339AE76394375880` | 可作为当前运行态基线 |
| 微信运行态 | A01 / A02 / A05 是同步前的旧窗口截图；B01-B05 是本轮从固定 `dist/dev/mp-weixin` 内部模拟器采集的当前证据 | A 组仅作为修改前证据；B 组用于当前结构/状态判断，动态数据和 fixture 缺口单独标记 |

> 2026-08-18 后续又对 `create` / `step-works` / `step-photos` 做了一轮源码收口：创建页主标题收回 `40rpx`、三页底部留白统一收紧到 `196rpx`；`step-works` 右侧状态改成参考图同款的上下结构，`step-photos` 底部提示恢复首张封面合同并保留“长按可调整顺序”文案。`dist/build` 已重新生成并通过静态门禁；`dist/dev` 因微信开发者工具仍在运行，当前尚未完成同步，待工具退出后补做运行态复测。

## 3. 参考图与当前截图的差异矩阵

| 页面 | 参考目标 | 当前截图观察 | 负责容器 | 本轮处理 | 复测前状态 |
|---|---|---|---|---|---|
| R01 首页 | 白画布；40rpx 主体边距；浅蓝 Hero；约 184rpx 草稿媒体卡；文字下划线 Tab | 内容区仍偏灰；Hero 插画和留白较参考图紧；草稿卡、Tab 为旧比例 | `home-v2__hero`、`__draft-card`、`__style-tabs` | Hero 已进一步收口到 `416rpx` 外高和放大插画；保留真实风格过滤和 `backgroundId` | 2026-08-19 MCP 构建同步后 build/dev 等价；运行态截图如需继续通过内部模拟器补采 |
| R02 创建 Hub | 整屏居中标题；进度与正文同轴；7 张约 144rpx 外高步骤卡；底部 40rpx CTA | 标题呈左对齐；步骤卡外高与正文密度偏离；内容底色偏灰 | `KpPageNav`、`KpCreateProgress`、`create-hub__step` | 使用既有 `center-title` 与 `show-label`；步骤卡改为 `border-box` | 待构建 / 截图 |
| R03 参演作品 | 居中导航、3/7、表单 Tab、作品卡和剧照带 | B03 已有空数据态截图；剧照带因无选中作品不出现 | `step-works__tabs`、`__card`、`__stills-row` | 保留空态，不凭空数据补图片；另需 fixture 复测已选态 | 已采集，正常已选态待 fixture |
| R04 生活照片 | 居中导航、4/7、提示、上传卡、三列网格、排序入口 | B04 已有草稿未就绪错误态截图；正常网格因数据未就绪不出现 | `step-photos__actions`、`__count-row`、`__grid` | 保留错误原因与重试；另需 fixture 复测正常态 | 已采集，正常网格态待 fixture |
| R05 个人中心 | 白画布；40rpx 边距；148rpx 头像；紧凑统计卡；服务区三行；细边框列表 | v4 可见头像比例、顶部卡片、完整度、统计、资料列表和三行服务区已收紧；列表字体与图标线宽比 B07 更贴近参考图；动态头像/姓名/统计值不同 | `mine-v2__profile-card`、`__avatar`、`__completeness-card`、`__stats-row`、`__row`、`__row--service`、`__row-title`、`__row-sub`、`__row-icon` | profile `192rpx` + avatar `148rpx`、completeness `160rpx`、stats `128rpx`、资料行 `112rpx`；资料主文案 `26rpx`、副文案 `22rpx`；服务行 `76rpx`、服务主文案 `24rpx`、图标 `2rpx` 轻线稿；服务区三行真实可达 | 2026-08-19 MCP 构建同步 + 内部模拟器截图已完成；help/settings 通过 `pkg-tools/webview` 承载 |
| C01 名片夹 | 无像素参考，只遵守白卡、40rpx、线性图标、蓝色主操作 | 三个卡片操作按钮纵向堆叠，内容密度较高 | `card-list-page__ops` | 已登记为后续独立视觉收口，避免虚构参考图 | 未验收 |
| C02 素材库 | 无像素参考，只遵守白色工具区、线性图标、可用空态 | 右侧新增按钮贴边，空态区域偏空 | `assets-page__toolbar`、`__empty` | 已登记为后续独立视觉收口，避免虚构参考图 | 未验收 |

### 3.1 B 组逐页对比结论

| 页面 | B 组对比事实 | 结论 |
|---|---|---|
| R01 首页 | 白画布、40rpx 主体留白、浅蓝 Hero、紧凑 CTA、文字 Tab 和两列模板网格已呈现；草稿图片/数量与参考图不同 | 布局风格基本一致；动态数据差异不作为样式缺陷 |
| R02 创建 Hub | 居中标题、`创建进度 0/7`、蓝色进度条、7 步卡片和底部主 CTA 使用同一套蓝白壳层；702x1520 视口下第 7 卡被固定 CTA 部分遮住 | 顶部/卡片节奏一致；需在目标设备高度确认底部安全区，不凭单一视口追加高度猜测 |
| R03 参演作品 | 3/7、居中标题、分段 Tab、单选作品卡、添加作品 CTA、底部下一步均存在；参考图的已选剧照带在当前空数据态不出现 | 结构与风格可比；需用有作品/剧照数据的固定 fixture 做第二次视觉回归 |
| R04 生活照片 | 4/7、标题/说明、白色资源容器、错误态重试、禁用下一步均可回读；参考图的上传入口和三列照片网格因草稿未就绪未出现 | 错误态有明确原因和恢复按钮；正常态网格仍需可用草稿 fixture 验证 |
| R05 个人中心 | 白画布、40rpx 留白、头像/资料卡、完整度、统计卡、三行服务区和原生四项 TabBar 层级一致；v4 已把资料/服务分组的文字层级、服务行轴线、图标线宽和箭头尺寸重新收口；头像、用户名和统计值是动态数据 | v4 对参考图的列表结构与字体/间距锚点已收口；动态用户资料差异不作为样式缺陷 |

## 4. 本轮修改值

| 源码容器 | 修改前 | 修改后 | 对应模板 |
|---|---|---|---|
| `home-v2__hero` | `min-height: 360rpx` 与 `padding: 40rpx 36rpx` 叠加为 content-box 外高 | `box-sizing: border-box; min-height: 392rpx` | `ReferenceCard` / R01 Hero |
| `home-v2__hero-title` | `48rpx` | `40rpx` | `ReferenceCard` / R01 Hero typography |
| `home-v2__hero-btn` | 自动撑满左栏，最小 216rpx × 88rpx | `196rpx × 64rpx`，文字保持 28rpx | `ReferenceBottomCta` / R01 Hero CTA |
| `home-v2__hero` / `home-v2__card-illus` | R01 Hero 插画偏小、左侧纵向节奏偏紧 | Hero `416rpx` 外高，插画容器 `246rpx × 292rpx`，前景卡 `174rpx × 240rpx`，按钮上间距 `34rpx` | `ReferenceCard` / R01 Hero density |
| `home-v2__draft-card` | `min-height: 184rpx` 与 `padding: 20rpx` 叠加为 content-box 外高 | `box-sizing: border-box`，保持 184rpx 外高基线 | `ReferenceCard` / R01 草稿卡 |
| `create-hub__step` | `min-height: 144rpx` 与 `padding: 24rpx` 叠加为 content-box 外高 | `box-sizing: border-box`，保持 144rpx 外高基线 | `ReferenceCard.step` / R02 |
| `mine-v2__stats-row` | `min-height: 160rpx` 与垂直 56rpx 内边距叠加 | `box-sizing: border-box; min-height: 144rpx` | `ReferenceCard.stats` / R05 |
| `mine-v2__row` | `min-height: 124rpx` 与垂直 52rpx 内边距叠加 | `box-sizing: border-box`，保持 124rpx 外高基线 | `ReferenceCard.listGroup` / R05 |
| `mine-v2__profile-card` / `__avatar` / `__completeness-card` / `__stats-row` / `__row` / `__row--service` | R05 顶部卡片和分组行整体偏厚，服务区缺帮助/设置，红色退出按钮破坏参考结构；B07 后列表文字仍偏大、图标线条偏重、服务行轴线偏松 | profile `192rpx`、avatar `148rpx`、completeness `160rpx`、stats `128rpx`、资料行 `112rpx`；资料主文案 `26rpx`、副文案 `22rpx` + `6rpx`；服务行 `76rpx`、服务主文案 `24rpx`、服务行 `gap: 12rpx`、图标 `2rpx`、实名认证盾牌、右箭头完整尺寸；服务三行恢复为真实路由，退出移入设置页 | `ReferenceCard.profile/completeness/stats/listGroup` |
| `create-hub__intro-title` | `48rpx` | `40rpx` | `ReferenceSection` / R02 首屏标题 |
| `create-hub__body` / `step-works__body` / `step-photos__body` | `calc(212rpx + safe-area)` | `calc(196rpx + safe-area)` | `ReferencePageShell` / 三页底部留白 |
| `step-works__card-actions` / `step-works__card-status` | 右侧横排计数 + 管理按钮 / 无未选状态 | 右侧上下堆叠计数与管理按钮，未选卡显示 `未选择剧照` | `ReferenceCard.work` / R03 |
| `step-photos__hint` / `step-photos__action-btn` | 单句封面提示 / 带阴影的上传卡 | 封面合同 + 长按排序提示并列，上传卡改为无阴影白卡 | `ReferenceMediaGrid` / R04 |

## 5. 后续验收条件

本轮构建同步、三侧 scoped hash 核验和首页窗口观察均已完成。后续如继续调整其他页面，仍需沿用以下固定顺序复测：

1. 重新执行构建同步并确认 postbuild 完成。
2. 对 R01、R02、R03、R04、R05 进入对应路由；优先使用内部 `simulator_screenshot`，不使用桌面截图。
3. 对 R03 已选剧照、R04 正常照片网格补充可重复的 fixture 数据后复测。
4. 以 750rpx 归一比对主体留白、导航/进度/首卡、卡片外高、CTA 与媒体网格；动态头像、媒体、人名和统计数值只作遮罩。
5. 只有全部主锚点在 `reference-layout.md` 规定的允许误差内，才将页面标记为“运行态通过”。
