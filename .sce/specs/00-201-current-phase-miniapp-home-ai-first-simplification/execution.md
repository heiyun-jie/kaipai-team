# 00-201 当前阶段小程序首页 AI 优先简化与阴阳鱼双入口 - 执行记录

## 当前状态

- 状态：`in_progress`（`480rpx` 实现与后台产物验证完成；微信开发者工具等待手动编译刷新）
- 日期：`2026-07-28`
- 页面：`pages/home/index`
- 范围：首页信息层级、双入口视觉、路由门禁、构建产物与 SCE 映射；未修改目标分包页面或后端链路。

## 已完成基础事实

- 删除首页原统计条、`我的数据` 轻链接、`操作指南` 视频、独立黑色创建按钮，以及「手动选风格 / SELECT A STYLE」标题、三张 `KpShareSceneCard`、加载态和空态。
- 删除首页对 `getMyShareCards()`、模板 / 卡片状态、风格 caption helper、`KpEmpty` 与 `KpShareSceneCard` 的专用消费；首页不再为不可见模板列表发起数据请求。
- `goAiProfileCard()` 与 `goCardList()` 已保留各自的 visitor / crew / actor 分支；首页继续执行 `bootstrapSession()`，已登录演员继续执行 `syncActorRuntimeState()`。

## 已否决视觉方案

- 上一轮使用上下两块卡片背景、`home-page__ai-fish-lobe` / `home-page__manual-fish-lobe` 和鱼眼节点拼出 S 形边界。
- 用户运行态复核后明确否决“上下两卡 + CSS 元素拼形”。该轮构建、截图与视觉通过结论仅作为历史记录，不核销最新位图背景合同。

## 最新实现合同

- 新目标以一个 `home-page__creation-stage` 承载 `/static/home/yin-yang-creation.png`；黑鱼左上、米白鱼右下，S 曲线、纸张质感和反色鱼眼全部固化在位图像素中。
- 页面不得再渲染鱼身 / 鱼眼拼形节点、独立图片节点、两块卡片背景、卡片边框、卡片间距或手动入口圆形图标。
- AI 文案锚定左上黑色安全区，手动创建文案锚定右下米白安全区；两个区域均不得遮挡位图鱼眼或 S 形主体。
- 舞台上仅保留两个无背景、无边框、无阴影且互不重叠的透明点击区；两区各自保留 `aria-role="button"`、`aria-label`、按压反馈和独立 `bindtap`，舞台自身不绑定第三个动作。

## 路由与身份矩阵

| 身份 | 左上 AI 透明区 | 右下手动透明区 |
|------|----------------|----------------|
| 游客 | `goLogin()` | `goLogin()` |
| 演员 | `/pkg-card/ai-profile-card/index` | `/pkg-card/card-list/index` |
| 剧组 | `goMine()` | `goMine()` |

## 构建与产物证据

- `npm run type-check`：通过。
- `npm run build:mp-weixin`：通过；postbuild 已同步到固定目录 `dist/dev/mp-weixin`。
- 两套 `pages/home/index.wxml` 均只有两个入口 `bindtap`，包含左上 AI / 右下手动文案，不包含 `creation-pair`、`*-fish-lobe`、`*-fish-eye`、`KpMineIcon` 或第三个入口节点。
- 两套 `pages/home/index.wxss` 不含 `data:image`，背景资源以运行时样式引用 `/static/home/yin-yang-creation.png`；生成样式均包含 `height:480rpx`、入口 `padding:22rpx` 及步骤区 `16rpx` 间距，两个入口自身无背景、边框和阴影。
- 两套 `pages/home/index.js` 均包含 `/pkg-card/ai-profile-card/index` 与 `/pkg-card/card-list/index`，并保留 visitor / crew 分支。
- `dist/build/mp-weixin` 与 `dist/dev/mp-weixin` SHA-256 一致：WXML `62B74AF8...3B05A`、WXSS `61ED5CA0...DE4CC`、JS `6919C6BC...EC7B`、PNG `D0C9B18D...03994`。
- source / build / dev 背景 PNG 均为 `1316x960`、`21,890` bytes；黑鱼左上、米白鱼右下，S 曲线与两颗反色鱼眼均固化在图片内。

## 验证结果与剩余边界

- `00-187`：`15/15 PASS`；`00-192`：`10/10 PASS`；`npm run audit:steering`：通过。
- `npm run audit:mp-package` 已重新执行，但仍被 `dist/build/mp-weixin/api/actor-asset.js:1` 中既有本地开发地址 `http://127.0.0.1:8010` 阻断；本轮未修改 API / 环境配置。
- 在不绕过 URL 门禁、不修改审计脚本的前提下，按其同一分包规则单独核算：主包 `475.37 KB`，`pkg-card` `212.54 KB`，`pkg-profile` `79.48 KB`，`pkg-tools` `32.34 KB`，均低于 2 MB；裁切后背景 PNG 占 `21.38 KB`。
- 使用无头 Chrome 按 `375x812` 视口、`329x240` 舞台渲染真实 PNG 与当前文字叠层；确认画面为单一背景，AI 位于左上黑色安全区、手动内容位于右下米白安全区，文字未遮挡鱼眼或 S 曲线。
- 用户要求后续只进行后台操作，不再置顶或切换微信开发者工具窗口；因此本轮未执行开发者工具前台截图、点击或演员态双路由实点，也不将其记为已验证。静态源码与构建产物已确认两个透明区分别绑定正确处理器和目标路由。

## `540rpx` 高度调整结果

- 用户于 `2026-07-28` 确认采用推荐的 `540rpx` 紧凑高度。
- 舞台已由 `658rpx x 600rpx` 调整为 `658rpx x 540rpx`；背景图已从 `1316x1200` 上下各裁去 `60px`，生成同比例 `1316x1080` PNG，没有拉伸或重画阴阳鱼。
- 两个透明入口继续各占舞台一半，即各高 `270rpx`；内容内边距已由 `30rpx` 收至 `26rpx`，内容宽度、字号、路由和 visitor / crew / actor 分支保持不变。
- source / build / dev 位图尺寸与哈希、生成 WXSS 的 `540rpx` / `26rpx`、两个 `bindtap` 及 `329x270` 无头预览均已核对；全过程未使用前台窗口自动化。

## `540rpx` 未形成明显视觉差异的诊断

- 用户运行态观察反馈“大小没有改动”。后台排查确认微信开发者工具主进程以 `--project D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin` 启动，工作区路径正确。
- source、`dist/build`、`dist/dev` 三层均为 `540rpx`；开发者工具模拟器缓存 `f_000013` 于 `15:55:30` 写入 `540rpx`，Code Cache `819b295b60204705_0` 于 `16:06:38` 同样只包含 `540rpx`，排除未编译或仍加载 `600rpx` 的假设。
- 根因是幅度不足：在 `375px` 视口中，舞台只从 `329x300px` 变为 `329x270px`，高度仅减少 `30px`（10%），宽度保持不变，因此缺少明确的大小变化感知。

## `480rpx` 显著高度结果

- 舞台已调整为 `658rpx x 480rpx`，相对最初 `600rpx` 高度缩短 20%；在 `375px` 视口中对应 `329x240px`，比最初减少 `60px`。
- 背景已从 `1316x1080` 上下各再裁去 `60px`，得到 `1316x960` PNG；没有拉伸、重新生成或重画鱼身。
- 两个透明入口各高 `240rpx`；内容内边距已改为 `22rpx`，步骤区 `margin-top` / `padding-top` 已改为 `16rpx`，文字字号、内容宽度和路由分支保持不变。
- `npm run type-check`、`npm run build:mp-weixin`、`00-187` `15/15`、`00-192` `10/10` 与 steering audit 均通过；`329x240` 无头预览及 `600rpx / 480rpx` 同视口并排对比确认高度差明确且内容无重叠。
- `dist/dev` 已于 `16:15:30` 写入 `480rpx`，但开发者工具在后台没有自动生成包含 `480rpx` 的模拟器缓存；重复同步同哈希 WXSS 并轮询 30 秒后仍无更新。按用户“不置顶窗口”要求，本轮不执行前台“编译”点击，也不声称模拟器已刷新。
