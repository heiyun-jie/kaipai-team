# 演员卡 Hero 与正文中性交接收口 - 技术设计

_Requirements: 3.1-3.3, 4-6_

## 1. 根因与几何合同

```text
intro/video bottom = 1077 + 159 = 1236rpx
Hero bottom = 1334rpx
image tail = 98rpx
flow top padding = 16rpx
visible handoff = 114rpx
```

目标几何：

```text
neutral tail begins = 1236rpx
flow margin-top = -74rpx
flow top padding = 0
stats top = 1334 - 74 = 1260rpx
last-card-to-stats gap = 1260 - 1236 = 24rpx
```

## 2. 图层

```text
z0  Hero image
z1  existing Hero tone + new 98rpx neutral tail
z2  Hero content and seven fixed slots
z3  flow/stats bridge
```

- 在 `.actor-card-renderer__hero::after` 创建固定 `98rpx` 中性尾部。
- 尾部使用 `$kp-color-surface-muted`，不使用渐变或图片取色。
- `.actor-card-renderer__flow` 增加 `position: relative`、`z-index: 3`、`margin-top: -74rpx`，顶部 padding 改为 `0`。
- Hero 自身高度、图片、tone、content 和七区绝对坐标不改。

## 3. 门禁

- 新增 `verify-00250-actor-card-hero-flow-handoff.mjs`。
- 断言 Spec、Hero `1334rpx`、尾部 `98rpx`、flow `-74rpx`/top padding `0` 和 `24rpx` 几何推导。
- 断言七区坐标、`aspectFill`、`00-249` 三行摘要、正文完整简介继续存在。
- 断言 build/dev Renderer WXML/WXSS/JS 三侧 scope hash 一致。
- 继续执行 `verify:actor-card-renderer`、`verify:actor-card-share-detail`、`verify:actor-card-hero-intro-summary`。

## 4. 运行态验证

- 固定工程：`D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin`。
- 页面：`pkg-actor-card/generate/index?cardId=1`。
- MCP 截图需覆盖最后两张 Hero 卡、24rpx 交接、统计摘要和固定底栏。
- MCP 同时验证长页仍可滚动，控制台 `error/fail` 为空。
- 不使用桌面截图、坐标、鼠标、键盘或窗口置顶。

## 5. 发版兼容

- 只改变共享 Renderer 样式，generate/view 同包自洽。
- 后端 JAR 与数据库无变化；若新 Candidate JAR SHA256 与当前测试运行 JAR相同，使用只读证明复用测试栈。
- 生产环境保持不变。
