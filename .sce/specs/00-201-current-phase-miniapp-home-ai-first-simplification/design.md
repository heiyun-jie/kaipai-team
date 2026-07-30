# 00-201 设计 — 首页 AI 优先简化与阴阳鱼双入口

> 状态：`480rpx` 实现与后台产物验证完成；微信开发者工具等待手动编译刷新

## 1. 现状元素盘点（home/index.vue）

| 现状块 | 类名 / 处理器 | 去向 | 处置 |
|--------|--------------|------|------|
| Hero 品牌微标 + 标题「为每一次相遇 / 留下光影」+ 副标题 | `home-page__hero` / `home-page__title`(58rpx) | — | **精简保留**：标题降字号、副标题改为呼应 AI 主入口，压缩 hero 纵向高度 |
| 统计条（2 stat + 我的数据› + AI生成分享图› pill） | `home-page__stats-strip` / `goMine` / `goAiProfileCard` | 我的数据→mine；AI pill→ai-profile-card | **移除展示块**：`我的数据›` 与 AI pill 均不再展示；AI 能力并入 3.1 主 CTA；`goMine` 保留给其它身份分支复用 |
| 风格分馆（KpShareSceneCard grid） | `home-page__section--styles` / `handleTemplateClick` | style-detail | **完整移除**；风格选择统一放回创建分享页流程 |
| 操作指南视频封面 | `home-page__guide-stage` / `openGuideVideo` | video-player | **移除** |
| 三步条 01 选风格 / 02 传作品 / 03 成海报 | `home-page__guide-steps` | — | **轻量保留**（纯文字）或并入主入口提示 |
| 原主 CTA「开始创建分享页」 | `home-page__guide-cta` / `goCardList` | card-list | **移除原黑色按钮**；`goCardList` 改由新的次级「手动创建分享」入口复用 |

## 2. 目标信息层级（首屏自上而下）

1. **精简 Hero**：品牌微标 + 一行主标题 + 一句呼应「AI 生成分享图」的副标题。压缩原 `58rpx` 大标题与 `stats-strip` 占高。
2. **阴阳鱼双入口**：以 `home-page__creation-stage` 承载一张完整的项目内 PNG 背景和两个对角透明点击区。
   - 背景图 `/static/home/yin-yang-creation.png` 固化全部阴阳鱼造型：黑鱼位于左上、米白鱼位于右下，S 形曲线和两颗反色鱼眼均属于位图像素；页面不再以元素拼接鱼身。
   - 左上透明区是唯一主动作，内容锚定黑色安全区，标题为「AI 生成分享图」，点击 `goAiProfileCard()`；保留诚实前置提示与 `选风格 · 传照片 · AI 生成`。
   - 右下透明区是手动动作，内容锚定米白安全区，标题为「手动创建分享」、说明为「选择风格与作品，创建你的分享页」、动作提示为「去创建 ›」，点击 `goCardList()`。
   - 两个透明区各占背景舞台一半且不重叠；不渲染独立卡片背景、卡片边框、卡片间距、鱼身节点、分享圆形图标或第三个可见 / 可点击元素。
   - 舞台可见尺寸固定为 `658rpx x 480rpx`；相对最初 `1316x1200` 素材上下各裁去 `120px`，得到同宽高比的 `1316x960` PNG，保留原鱼身比例并继续使用 `background-size: 100% 100%`。
   - 高度收紧后两个透明区各高 `240rpx`，入口内边距收至 `22rpx`，步骤区上下间距由 `20rpx` 收至 `16rpx`；标题、说明、步骤字号及内容宽度保持不变。
3. **结束首页内容区**：不再展示模板列表、模板加载态或“我的数据”轻链接；个人数据统一从底部“我的”Tab 进入。

## 3. 低保真布局

```
┌────────────────────────────────────┐
│ KAIPAILE · SHARE                    │  ← 精简 hero（标题字号下调）
│ 为每一次相遇，留下光影                │
│ 用 AI 快速生成你的分享图              │  ← 副标题呼应主入口
│                                     │
│ ┌────────────────────────────────┐ │
│ │ AI 生成分享图        立即开始 › │ │  ← 左上透明区 goAiProfileCard()
│ │ 实名后上传照片  ╲      ○        │ │
│ │ 选风格 · 传照片   ╲             │ │  ← 单张阴阳鱼 PNG 背景
│ │                    ╲            │ │
│ │       ●              ╲          │ │
│ │                        手动创建分享│ │  ← 右下透明区 goCardList()
│ │             选风格 · 传作品 · 保存│ │
│ └────────────────────────────────┘ │
└────────────────────────────────────┘
   [首页]   [记录]   [我的]
```

## 4. 分支与跳转（复用既有处理器）

| 身份 | AI 主 CTA | 手动创建分享 |
|------|-----------|----------|
| 访客（未登录） | `goLogin()` | `goLogin()` |
| 演员 | `/pkg-card/ai-profile-card/index` | `/pkg-card/card-list/index` |
| 剧组 | `goMine()` | `goMine()` |

- `goAiProfileCard()` / `goCardList()` / `goMine()` 复用既有 visitor / crew 分支；删除可见轻链接后仍保留 `goMine()`，供两个透明入口的 crew 分支复用。
- 阴阳鱼视觉只由 `/static/home/yin-yang-creation.png` 提供；该资源使用确定尺寸和压缩后的 PNG，纳入主包体审计，不依赖网络地址。
- 删除 `KpMineIcon name="share"`、鱼身 / 鱼眼装饰节点及对应 CSS。两个透明点击区仅承载文字与交互语义，按压态只调整内容透明度，不绘制新的矩形卡面。
- 背景图预留左上浅色字和右下深色字的净空，避免文案遮挡鱼眼和 S 曲线；舞台使用稳定 `aspect-ratio` / 固定 rpx 高度保证各设备构图不漂移。
- 删除 `KpEmpty`、`KpShareSceneCard`、`getMyShareCards`、模板 / 卡片状态、`handleTemplateClick()`、风格 caption helper 与对应样式，避免不可见数据请求和死代码。
- 移除 `openGuideVideo()` 及 `guideTitle` / `guideCopy` / `guideActionText` 中仅服务视频区的分支文案；保留仍被复用的 computed（如仍用于三步提示则改写，否则删除）。

## 5. 访客 / 新用户降噪

- `stats` 中 `我的卡片 = 0`、访客 `可浏览 = 3` 这类对新用户无意义的数字从首屏主区移除；`我的数据 ›` 轻链接同步删除，避免和底部“我的”Tab 重复。
- 未登录仅执行全局 `bootstrapSession()` 恢复，不请求个人分享数据；已登录演员保留 `syncActorRuntimeState()`，维持全局会话与账号边界。

## 6. 不改动边界

- `pkg-card/ai-profile-card/index` 页内三步（风格 / 分析图 / 生成）与实名门禁、异步回执，均不在本 Spec 改动范围（`00-168` / `00-182` 治理）。
- 后端 AI 链路与 `getMyShareCards` 数据契约不变；仅删除首页对后者的无效消费。
- `00-187` 登录门禁验收脚本保持通过。

## 7. 验证方式

1. `cd kaipai-frontend && npm run build:mp-weixin`。
2. `rg` 核对首页产物：`/static/home/yin-yang-creation.png`、`手动创建分享`、`card-list/index` 与两个透明入口各自的按压态、独立 `bindtap` 进入产物；`home-page__creation-seal`、`*-fish-lobe`、`*-fish-eye`、`KpMineIcon`、手动选风格与历史入口类名已消失。
3. 核对首页源码与 WXSS：舞台仅使用一张背景图，两个子入口无背景 / 边框 / 阴影且不重叠；不存在 CSS 拼形节点或第三个点击处理器。
4. 复跑 `00-187` 既有验收脚本，确认未回归。
5. 使用无头浏览器按 `375x812` 视口、`329x240` 舞台预览真实背景与文字叠层，确认裁切后鱼眼、S 曲线和文字不重叠，并验证相对最初 `329x300` 高度减少 `60px`。
6. 微信开发者工具加载 `dist/dev/mp-weixin`，人工核对单一图片画面、左上 / 右下内容锚点、两个透明点击区域与演员态跳转；用户要求仅后台操作时保持未执行并如实记录。
