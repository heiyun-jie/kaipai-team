# v2.0 演员卡分享与观看者页面

## 1. 概述

本 Spec 补全 v2.0 演员卡创建向导的最后一公里：**分享出口 + 观看者落地页**，使已发布演员卡真正可分享给外部观看者查看。

**上游依赖**：`00-206`（v2.0 创建向导）、`00-208`（参演作品）、`00-214`（附件简历）

**历史背景**：`00-209` 已删除旧版 1.0 演员卡体系（`pkg-card/ai-profile-card-detail` 等 10 个页面），当前运行态不存在任何分享出口与观看者页面。本 Spec 为 v2.0 体系重新实现该能力，数据结构、API 契约、UI 规范均与 v2.0 向导对齐。

**核心路径**：卡主在名片夹点击"分享" → 微信分享卡片 → 观看者点击 → 进入演员卡详情页（展示主视觉、个人资料、参演作品、生活照片、视频、附件）

---

## 2. 用户故事

- 作为演员（卡主），我希望在名片夹 - 已发布 Tab 中分享我的演员卡给导演、剧组或朋友
- 作为观看者，我希望点击微信分享卡片后能看到演员的完整信息（主视觉、作品、照片等）
- 作为演员，我希望步骤 7 设置的"联系方式/视频/附件展示开关"在分享页中生效
- 作为演员，我希望步骤 7 设置的模块展示顺序在分享页中按我的意愿排列
- 作为观看者，我希望只能看到已发布的演员卡，草稿卡无法访问

---

## 3. 功能需求

### 3.1 名片夹分享出口

**描述**：在 `pages/card-list/index.vue` 已发布 Tab 为每张卡片增加分享能力。

**验收标准**：
- WHEN 演员进入名片夹 - 已发布 Tab THEN 每张卡片显示"分享"按钮
- WHEN 点击"分享"按钮 THEN 触发微信分享面板（转发给朋友/分享到朋友圈）
- WHEN 分享成功 THEN 分享卡片标题为演员卡名称，封面图为 `previewImageUrl`
- WHEN 观看者点击分享卡片 THEN 跳转到 `/pkg-actor-card/view/index?cardId=123`
- WHEN 草稿卡 THEN 不显示分享按钮（仅已发布卡可分享）

**实现方式**：
- 实现 `onShareAppMessage` 返回分享配置
- 分享路径：`/pkg-actor-card/view/index?cardId={cardId}`
- 分享标题：演员卡名称（从 `profile.name` 或自定义标题字段读取）
- 分享封面：`previewImageUrl`（主视觉图片）

---

### 3.2 观看者落地页（新建）

**描述**：新建 `src/pkg-actor-card/view/index.vue`，作为分享链接的落地页，展示已发布演员卡的完整信息。

**验收标准**：
- WHEN 观看者通过分享进入页面 THEN 读取 URL 参数 `cardId`，调用 `GET /api/actor-card/public/:cardId`
- WHEN 卡片状态为已发布 THEN 正常展示完整信息
- WHEN 卡片状态为草稿 THEN 显示"该演员卡尚未发布"提示页
- WHEN 卡片不存在 THEN 显示"演员卡不存在或已删除"提示页
- WHEN 网络异常 THEN 显示错误提示，提供重试按钮

**页面结构**（从上到下）：

#### 1. 顶部导航
- 使用 `KpPageNav`
- 标题：演员姓名
- 返回按钮：返回小程序首页（观看者可能没有返回栈）

#### 2. 主视觉区
- 大图展示 `previewImageUrl`
- 全宽，高度自适应（保持宽高比）
- 背景色为卡片风格对应色（`style = classic|urban|ancient|fresh`）

#### 3. 个人资料卡片
- 布局：圆角卡片，白底，12rpx 圆角
- 字段（按顺序）：
  - 姓名（加粗，32rpx）
  - 身高 / 城市（灰色副文本）
  - 联系方式（`settings.showContact = true` 时显示）
  - 自我介绍（多行文本，若有）

#### 4. 参演作品区（`settings.showWorks` 默认 true）
- 标题："参演作品"
- 布局：每部作品一个卡片
- 卡片内容：
  - 作品名称 + 饰演角色（标题行）
  - 剧照网格（1-3 张，首张为封面）
- 剧照点击：调用 `uni.previewImage` 查看大图

#### 5. 生活照片区（`settings.showPhotos` 默认 true）
- 标题："生活照片"
- 布局：3 列网格，每张正方形，间距 16rpx
- 点击：调用 `uni.previewImage` 查看大图

#### 6. 视频简历区（`settings.showVideo = true` 时显示）
- 标题："视频简历"
- 布局：视频封面 + 播放按钮
- 点击：跳转 `pkg-tools/video-player`，传递 `assetId`

#### 7. 附件简历区（`settings.showAttachment = true` 时显示）
- 标题："附件简历"
- 布局：PDF 图标 + 文件名 + "查看"按钮
- 点击：调用 `listActorAssetPages` 获取页图，`uni.previewImage` 原生浏览（复用 00-214 逻辑）

**模块顺序**：
- 按 `settings.moduleOrder` 数组排列 4-7 区块
- 默认顺序：`["works", "photos", "video", "attachment"]`
- 未在数组中的模块不展示

---

### 3.3 后端公开接口（新建）

**端点**：`GET /api/actor-card/public/:cardId`

**权限**：无需鉴权，加入 `SecurityConfig.WHITE_LIST`

**响应结构**：

```json
{
  "id": 123,
  "style": "classic",
  "previewImageUrl": "https://...",
  "profile": {
    "name": "张三",
    "height": "175cm",
    "city": "北京",
    "school": "中央戏剧学院",
    "contact": "138****1234",
    "introduction": "10年表演经验..."
  },
  "works": [
    {
      "id": 1,
      "title": "XX电影",
      "role": "主角李明",
      "workType": "电影",
      "stills": [
        "https://...",
        "https://...",
        "https://..."
      ]
    }
  ],
  "photos": [
    "https://...",
    "https://..."
  ],
  "video": {
    "assetId": 456,
    "coverUrl": "https://...",
    "duration": 60
  },
  "attachment": {
    "assetId": 789,
    "filename": "张三_简历.pdf"
  },
  "settings": {
    "showContact": true,
    "showVideo": true,
    "showAttachment": false,
    "moduleOrder": ["works", "photos", "video", "attachment"]
  }
}
```

**业务逻辑**：

1. **权限校验**：
   - 查询 `actor_card` 表，`id = :cardId`
   - 若 `status != 'published'` → 返回 `403 Forbidden`（"该演员卡尚未发布"）
   - 若不存在 → 返回 `404 Not Found`（"演员卡不存在"）

2. **字段映射**：
   - `profile` ← `profile_snapshot_json`
   - `works` ← `actor_card_work` 表（`card_id = :cardId`），包含 `stills_json` 解析
   - `photos` ← `photos_json`
   - `video` ← 关联 `actor_media_asset` 表（若 `video_asset_id` 非空）
   - `attachment` ← 关联 `actor_media_asset` 表（若 `attachment_asset_id` 非空）

3. **`settings` 解析**：
   - 读取 `settings_json` 字段
   - 若 `showContact = false`，则 `profile.contact` 返回 `null`
   - 若 `showVideo = false`，则 `video` 整个字段返回 `null`
   - 若 `showAttachment = false`，则 `attachment` 整个字段返回 `null`
   - `moduleOrder` 原样返回，前端按此顺序渲染

4. **资源 URL 处理**：
   - 所有图片/视频 URL 需要是**签名 URL**（10 分钟有效期）
   - 调用 `ActorMediaAssetService` 的 `generatePresignedUrl` 方法

---

### 3.4 解决 00-214 的两条已知缺口

本 Spec 实施后，以下缺口自动闭合：

| 缺口 | 原登记 | 本 Spec 解决方式 |
|------|--------|------------------|
| `settingsJson.showAttachment` 无消费方 | 服务端从不解析 | `GET /api/actor-card/public/:cardId` 按此开关控制 `attachment` 字段返回 |
| 附件未进已发布卡渲染 | `toListItem` 无附件字段 | 观看者页面直接读取并渲染附件模块 |

---

## 4. 非功能需求

- 观看者页面 `view/index.vue` 必须落在 `pkg-actor-card` 分包，不增加主包体积
- 分享卡片封面图需提前预加载，避免微信分享面板显示空白
- 大图资源使用 CDN 加速，签名 URL 有效期 10 分钟
- 页面加载态显示骨架屏，避免白屏
- 接口失败时提供重试按钮，不强制用户返回

---

## 5. 约束条件

- 草稿卡（`status = 'draft'`）禁止通过公开接口访问
- 已删除或下架的演员卡返回 404
- 观看者无需登录即可查看已发布演员卡
- 卡主自己查看自己的演员卡时，使用相同的观看者页面（统一体验）
- 分享路径必须是小程序页面路径，不能是 H5 链接（微信限制）

---

## 6. 全局规则

① 分享仅对已发布卡开放，草稿卡无分享入口  
② 观看者页面按 `settings` 开关与顺序渲染模块  
③ 所有资源 URL 使用签名 URL，10 分钟有效期  
④ 页面加载失败提供重试，不强制返回  
⑤ 复用 v2.0 现有组件（`KpPageNav` / 参演作品卡片 / 照片网格）  
⑥ 附件预览复用 00-214 的 `listActorAssetPages` + `uni.previewImage` 方案

---

## 7. 边界与待定项

### 7.1 分享统计

- 本轮**不实现**分享次数、浏览次数统计
- 后续若需要，需在后端增加埋点表 `actor_card_view_log`

### 7.2 分享海报生成

- 本轮**不实现**生成海报图片功能
- 当前分享方式：微信原生分享卡片（标题 + 封面 + 路径）

### 7.3 观看者互动

- 本轮**不实现**点赞、收藏、评论功能
- 观看者页面为**只读展示**

### 7.4 卡主编辑入口

- 观看者页面**不提供**"编辑演员卡"入口
- 卡主若要编辑，需返回名片夹 - 已发布 Tab，点击卡片进入编辑

---

## 8. 验收标准总览

### 前端

- [ ] 名片夹 - 已发布 Tab 每张卡片有"分享"按钮
- [ ] 点击分享按钮触发微信分享面板
- [ ] 分享卡片标题、封面、路径正确
- [ ] 观看者点击分享卡片进入 `view/index`
- [ ] 观看者页面按 `settings` 渲染模块与顺序
- [ ] 草稿卡访问返回"尚未发布"提示
- [ ] 不存在的卡访问返回"不存在"提示
- [ ] 剧照、生活照点击可预览大图
- [ ] 视频简历点击可播放
- [ ] 附件简历点击可分页预览（复用 00-214）
- [ ] `vue-tsc --noEmit` 0 错误
- [ ] `npm run build:mp-weixin` 成功
- [ ] 主包 < 2MB（新页面在分包内）
- [ ] 产物 grep 核对关键字已进入 `dist/build` 与 `dist/dev`

### 后端

- [ ] `GET /api/actor-card/public/:cardId` 返回正确数据
- [ ] 草稿卡返回 403
- [ ] 不存在的卡返回 404
- [ ] `settings.showContact/showVideo/showAttachment` 正确控制字段返回
- [ ] 所有图片 URL 为签名 URL，10 分钟有效
- [ ] 接口加入 `SecurityConfig.WHITE_LIST`（无需鉴权）
- [ ] 接口响应时间 < 500ms（P95）

### 回归

- [ ] 既有门禁全绿（`verify:nav-title` / `verify:actor-card-attachment`）
- [ ] `00-214` 的 17 项断言仍通过
- [ ] 已发布演员卡数据完整性校验（参演作品、照片、视频、附件字段完整）

---

## 9. 依赖与前置

- `00-206` 已完成（v2.0 创建向导）
- `00-208` 已完成（参演作品）
- `00-214` 已完成（附件简历）
- `actor_card` 表结构包含 `status` / `profile_snapshot_json` / `photos_json` / `video_asset_id` / `attachment_asset_id` / `settings_json`
- `actor_card_work` 表已建立（参演作品快照）
- `ActorMediaAssetService` 提供 `generatePresignedUrl` 方法

---

## 10. 风险与缓解

| 风险 | 缓解措施 |
|------|----------|
| 签名 URL 过期导致图片加载失败 | 前端检测 403，自动重新请求接口刷新 URL |
| 大图加载慢，用户体验差 | 使用 CDN 加速 + 骨架屏占位 |
| 分享卡片封面空白 | 提前调用 `uni.getImageInfo` 预加载封面 |
| 观看者页面内容过长，滑动卡顿 | 照片网格使用虚拟滚动（若超过 50 张） |
| 草稿卡被恶意访问 | 后端严格校验 `status = 'published'`，403 阻断 |
