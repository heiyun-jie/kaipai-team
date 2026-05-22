# AI 分享图详情页 PDF 简历展示范围同步 Requirements

> 状态：当前执行中 | 优先级：高 | 依赖：00-171、05-13

## 1. 概述

`05-13` 已把 PDF 简历定义为公开分享详情页的原稿附件，并要求前端按 `resumePdfPageImageUrls` 顺序渲染 PDF 图片页。`00-171` 已把 AI 分享图详情页收敛为“单 AI 封面 + 主题内容流”，但当前内容流只覆盖基础资料、形象语言、技能、简介、拍摄经历、照片和视频，没有同步承接 PDF 简历展示范围。

本轮只补齐 AI 分享图详情页的前端展示范围，让 `pkg-card/ai-profile-card-detail/index` 与普通公开详情页一样，使用演员档案中的 PDF 图片页事实源展示“PDF 简历”区块。

## 2. 用户故事

- 作为演员，我希望上传 PDF 简历后，普通公开详情页和 AI 分享图详情页都能展示同一份原稿附件。
- 作为项目方或访客，我希望打开 AI 分享图详情页时，能在封面和资料内容流之后继续浏览演员 PDF 简历原稿。
- 作为研发，我希望 AI 分享图详情页复用 `ActorProfile.resumePdfPageImageUrls`，不新增另一套 PDF 展示状态或判断口径。

## 3. 功能需求

### 3.1 AI 详情页展示 PDF 简历区块

**描述**：AI 分享图详情页在主题内容流中展示 PDF 简历图片页。

**验收标准**：

1. WHEN `actor.resumePdfPageImageUrls` 存在且包含有效 URL THEN `pkg-card/ai-profile-card-detail/index` 展示“PDF 简历”区块。
2. WHEN `actor.resumePdfPageImageUrls` 为空 THEN AI 分享图详情页不展示 PDF 简历区块。
3. WHEN PDF 图片页有多页 THEN 前端按数组顺序纵向渲染，保持图片原始比例。
4. WHEN 用户点击某一 PDF 图片页 THEN 使用当前 PDF 图片页列表进行预览。

### 3.2 展示判断单一来源

**描述**：PDF 简历展示资格只来自演员档案事实源。

**验收标准**：

1. WHEN AI 分享图详情页判断是否展示 PDF 区块 THEN 只读取 `ActorProfile.resumePdfPageImageUrls.length > 0`。
2. WHEN 普通公开详情页和 AI 分享图详情页展示 PDF THEN 二者使用同一字段语义，不新增 AI 专属 PDF 字段。
3. WHEN AI 生成任务状态变化 THEN 不影响 PDF 区块是否展示；AI 任务只决定封面是否可见。

### 3.3 内容流与底部操作栏兼容

**描述**：PDF 区块必须融入 `00-171` 的主题内容流，不破坏底部联系/分享操作栏。

**验收标准**：

1. WHEN PDF 页较长 THEN 内容流继续使用 `theme` 底色延展，不依赖额外 AI 背景图。
2. WHEN 底部操作栏固定显示 THEN 页面底部安全距离不遮挡 PDF 最后一页。
3. WHEN PDF 单页图片加载失败 THEN 不阻断其他内容和联系方式操作。

## 4. 非功能需求

1. 不引入 PDF.js 或 web-view。
2. 不新增后端接口、PDF 转换能力或 AI 生成能力。
3. 不改变 `00-171` 的单封面生成合同。
4. 不改变 `05-13` 的 PDF 上传、保存和图片页转换合同。

## 5. 约束条件

1. 遵守“展示状态与资格判断必须单一来源”：PDF 展示资格只来自 `resumePdfPageImageUrls`。
2. 继续由后端提供 PDF 图片页 URL，前端只展示图片页。
3. AI 分享图详情页不得把 PDF 图片页纳入 AI 生成图或 prompt。

## 6. 验收总则

1. 新增 SCE Spec 并追溯到 `00-171 / 05-13`。
2. `pkg-card/ai-profile-card-detail/index` 展示 PDF 简历内容流区块。
3. 前端类型检查通过。
4. 微信小程序构建通过。
