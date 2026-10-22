# 演员卡 Hero 与正文中性交接收口

> 状态：已完成（2026-09-01）。

## 1. 概述

`pkg-actor-card/generate/index?cardId=1` 的运行截图显示，Hero 最后两张卡片在 `1236rpx` 结束，而固定 Hero 到 `1334rpx` 才结束；正文流又增加 `16rpx` 顶部 padding。背景图在交接区露出约 `114rpx` 的大面积黄色，统计摘要与 Hero 呈现为两个断裂色块。

本 Spec 只重做 Hero 尾部与统计摘要的交接：固定画布、背景裁切、七区坐标、统计数据和长页顺序全部保持不变。

## 2. 用户故事

- 作为卡主，我希望 Hero 与正文过渡紧凑、稳定，不因背景图片底色产生大面积黄色空带。
- 作为观看者，我希望统计摘要成为主视觉与详细资料之间的连续视觉锚点。

## 3. 功能需求

### 3.1 中性 Hero 尾部

**验收标准**：

- WHEN 最后两张 Hero 卡片结束 THEN 从 `1236rpx` 到 `1334rpx` 的 `98rpx` 尾部使用 `$kp-color-surface-muted`，不得继续暴露背景图底色。
- 中性尾部必须位于 Hero 图片/色调层之上、全部 Hero 内容卡片之下，不得遮挡简介或视频内容。
- 不使用渐变，不依赖具体背景图片颜色。

### 3.2 统计卡叠接

**验收标准**：

- 统计摘要向上叠入 Hero `74rpx`，正文流顶部 padding 从 `16rpx` 收口为 `0`。
- 最后两张卡片底部 `1236rpx` 与统计卡顶部 `1260rpx` 之间保留 `24rpx` 间距。
- 统计卡必须位于 Hero 中性尾部上方，左右露出的背景为 `$kp-color-surface-muted`，不得出现黄色侧边。
- 统计数据、四列结构、`132rpx` 最小高度和底部固定操作栏保持不变。

### 3.3 共享页面一致

**验收标准**：

- `generate/index` 与 `view/index` 继续只引用同一个 `ActorCardRenderer`。
- `src`、`dist/build/mp-weixin`、`dist/dev/mp-weixin` 三侧必须包含相同交接规则和 scoped hash。
- 内部 MCP 在 `pkg-actor-card/generate/index?cardId=1` 截图确认黄色空带消失、末卡到统计卡间距稳定、底栏没有遮挡交接信息。

## 4. 必须保持

- Hero 继续为 `750 x 1334rpx`，图片继续 `aspectFill`。
- identity/facts/skills/works/photos/intro/video 七区坐标与尺寸不变。
- `00-249` 的 Hero 简介三行省略摘要和下方完整简介不变。
- 长页模块顺序、媒体展示、固定底栏与 safe-area 避让不变。

## 5. 非目标

- 不缩短 Hero，不移动或放大最后两张 Hero 卡片。
- 不裁剪、重绘、调色或重新生成用户背景图片。
- 不改变统计卡内容、正文模块或后端数据合同。
- 不修改数据库、后端、测试数据或生产环境。

## 6. 发布兼容

- 纯前端共享组件样式修复；旧后端继续兼容。
- 当前 Candidate 在源码变化后失效，必须冻结新测试 Candidate 并重新通过 build/dev/缓存/实时请求准入。
- 正式发布继续 `NOT_AUTHORIZED`。
