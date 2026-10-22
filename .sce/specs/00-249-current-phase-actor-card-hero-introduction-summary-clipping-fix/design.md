# 演员卡 Hero 个人简介摘要防硬截断 - 技术设计

_Requirements: 3.1-3.3, 4-6_

## 1. 根因

```text
ActorCardRenderer Hero
  -> intro card: fixed 281 x 159rpx, overflow hidden
  -> hero-copy: complete profile.introduction
  -> no line clamp / no ellipsis
  -> long text is clipped by parent at an arbitrary glyph row
```

下方正文使用独立 `.actor-card-renderer__intro`，可以完整展示内容；缺陷只发生在 Hero 固定容量摘要卡。

## 2. 视觉合同

| 区域 | 修改 | 保持 |
|---|---|---|
| Hero 个人简介文本 | 专用三行 clamp，超出显示省略语义 | `top:1077 / left:81 / width:281 / height:159` |
| 长页个人简介正文 | 不修改 | 完整原文、正文顺序 |
| 其他 Hero 卡片 | 不修改 | facts/skills/works/photos/video 坐标和样式 |

## 3. 实现

- 为 Hero 简介文本增加专用 class `actor-card-renderer__hero-copy--intro`。
- 专用 class 使用 `display: -webkit-box`、`-webkit-box-orient: vertical`、`-webkit-line-clamp: 3` 和 `word-break: break-all`。
- 保留共享 `.actor-card-renderer__hero-copy` 的颜色、字号、字重和行高；专用 class 只控制三行容量与省略。
- 下方 `.actor-card-renderer__intro` 不增加 clamp。

## 4. 门禁

- 新增 `verify-00249-actor-card-hero-intro-summary.mjs`。
- 断言 Spec 三件套、源码专用 class、三行 clamp、Hero 坐标不变、正文未 clamp。
- 断言 build/dev WXML 包含专用 class，WXSS 包含三行 clamp，WXML/WXSS/JS scope hash 三件套及双侧一致。
- 继续执行 `verify:actor-card-renderer` 与 `verify:actor-card-share-detail`，防止共享结构回归。

## 5. 运行态验证

- 固定工程：`D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin`。
- MCP 路由：`pkg-actor-card/generate/index?cardId=1`。
- 页面数据必须仍返回完整 introduction；截图中 Hero 显示三行摘要且没有硬切，长页完整简介仍存在。
- 不使用桌面截图、坐标、鼠标或键盘自动化。

## 6. 发版兼容

- 前端包内自洽，无 API/数据库合同变化。
- 候选变更后重新冻结和切换固定 dev；生产继续 `NOT_AUTHORIZED`。

