# v2.0 演员卡分享与观看者页面 - 任务清单

_Requirements: ALL_  
_Design: ALL_

## 任务分解

### 阶段 A：后端公开接口实现

#### A1 DTO 与实体类准备
- [ ] 创建 `ActorCardPublicRespDTO` 及其嵌套类（ProfileVO / WorkVO / VideoVO / AttachmentVO / SettingsVO）
- [ ] 创建 `ActorCardSettings` 领域对象（解析 `settings_json`）
- [ ] 验证字段映射与 requirements § 3.3 的 JSON 契约完全一致

**验收**：编译通过，字段名与类型匹配前端 TypeScript 接口。

---

#### A2 Service 层 - 核心查询逻辑
- [ ] `ActorCardPublishService.getPublicView(Long cardId)` 实现
  - [ ] 查询 `actor_card` 表，校验 `status = 'published'`
  - [ ] 草稿返回 `BizException(403, "该演员卡尚未发布")`
  - [ ] 不存在返回 `BizException(404, "演员卡不存在")`
- [ ] 解析 `profile_snapshot_json` → `ProfileVO`
- [ ] 查询 `actor_card_work` 表（按 `card_id` + `sort_order` 排序）
- [ ] 解析 `photos_json` → `List<String>`
- [ ] 解析 `settings_json` → `ActorCardSettings`

**验收**：单测覆盖已发布/草稿/不存在三种情况，状态码正确。

---

#### A3 Service 层 - settings 控制逻辑
- [ ] 若 `settings.showContact = false`，则 `profile.contact = null`
- [ ] 若 `settings.showVideo = false`，则 `video = null`
- [ ] 若 `settings.showAttachment = false`，则 `attachment = null`
- [ ] 若 `video_asset_id` / `attachment_asset_id` 为空，对应字段返回 `null`

**验收**：单测覆盖 settings 各开关组合，字段过滤正确。

---

#### A4 Service 层 - 签名 URL 生成
- [ ] 调用 `ActorMediaAssetService.generatePresignedUrl` 生成主视觉图片 URL
- [ ] 为所有剧照 URL 生成签名 URL
- [ ] 为所有生活照 URL 生成签名 URL
- [ ] 为视频封面 URL 生成签名 URL（若有）
- [ ] 验证签名 URL 有效期 = 10 分钟

**验收**：返回的所有 URL 可正常访问，10 分钟后返回 403。

---

#### A5 Controller 层实现
- [ ] `ActorCardController.getPublicCard(@PathVariable Long cardId)` 实现
- [ ] 返回 `ResponseEntity<ActorCardPublicRespDTO>`
- [ ] 异常统一由 `GlobalExceptionHandler` 处理

**验收**：Postman 调用接口，已发布卡返回 200 + 完整数据，草稿返回 403，不存在返回 404。

---

#### A6 白名单配置
- [ ] `SecurityConfig.WHITE_LIST` 添加 `/api/actor-card/public/**`
- [ ] 验证无需 token 可访问

**验收**：不带 Authorization header 调用接口成功。

---

### 阶段 B：前端 API 层

#### B1 TypeScript 类型定义
- [ ] `src/types/actor-card.ts` 新增 `ActorCardPublicVO` 接口
- [ ] 嵌套接口：`ProfileVO` / `WorkVO` / `VideoVO` / `AttachmentVO` / `SettingsVO`
- [ ] 与后端 DTO 字段完全对齐

**验收**：`vue-tsc --noEmit` 无类型错误。

---

#### B2 API 方法实现
- [ ] `src/api/actor-card.ts` 新增 `getPublicCard(cardId: string | number)`
- [ ] 返回类型为 `Promise<ActorCardPublicVO>`
- [ ] 错误处理：403 / 404 / 500 映射到业务错误码

**验收**：本地调用接口，返回数据类型正确。

---

### 阶段 C：观看者落地页实现

#### C1 页面骨架与路由
- [ ] 创建 `src/pkg-actor-card/view/index.vue`
- [ ] `pages.json` 注册路由：`pkg-actor-card/view/index`
- [ ] 配置 `navigationBarTitleText = "演员卡"`
- [ ] 使用 `KpPageNav` 组件（标题动态绑定为演员姓名）

**验收**：手动访问页面，路由正常，顶部导航显示。

---

#### C2 数据加载与状态管理
- [ ] `onMounted` 读取 `options.cardId`
- [ ] 调用 `getPublicCard(cardId)` 加载数据
- [ ] 三态管理：`loading` / `error` / `loaded`
- [ ] 错误处理：403 显示"尚未发布" / 404 显示"不存在" / 其他显示通用错误 + 重试按钮

**验收**：
- 已发布卡显示内容
- 草稿卡显示"尚未发布"
- 不存在的卡显示"不存在"
- 网络异常显示"加载失败"+ 重试按钮可用

---

#### C3 主视觉区实现
- [ ] `<image :src="cardData.previewImageUrl" mode="widthFix" />`
- [ ] 全宽显示，高度自适应
- [ ] 加载失败显示占位图

**验收**：主视觉图片正常显示，宽度填满屏幕。

---

#### C4 个人资料卡片组件
- [ ] 创建 `src/pkg-actor-card/view/components/ProfileCard.vue`
- [ ] 展示字段：姓名 / 身高 / 城市 / 学校 / 联系方式 / 自我介绍
- [ ] 联系方式按 `profile.contact` 是否为空决定显隐
- [ ] 样式：圆角卡片，白底，12rpx 圆角，32rpx 内边距

**验收**：个人资料完整显示，联系方式关闭时不显示该字段。

---

#### C5 参演作品区组件
- [ ] 创建 `src/pkg-actor-card/view/components/WorksSection.vue`
- [ ] 接收 `works: WorkVO[]` prop
- [ ] 每部作品一个卡片：作品名 + 角色名 + 剧照网格（1-3 张）
- [ ] 剧照点击调用 `uni.previewImage` 查看大图

**验收**：
- 作品列表正常显示
- 剧照网格布局正确（3 列）
- 点击剧照可预览大图

---

#### C6 生活照片区组件
- [ ] 创建 `src/pkg-actor-card/view/components/PhotosSection.vue`
- [ ] 接收 `photos: string[]` prop
- [ ] 3 列网格布局，间距 16rpx
- [ ] 点击调用 `uni.previewImage` 查看大图

**验收**：
- 照片网格显示正常
- 点击可预览大图
- 多张照片可左右滑动

---

#### C7 视频简历区组件
- [ ] 创建 `src/pkg-actor-card/view/components/VideoSection.vue`
- [ ] 接收 `video: VideoVO` prop
- [ ] 显示视频封面 + 播放按钮图标
- [ ] 点击跳转 `/pkg-tools/video-player?assetId={assetId}`

**验收**：
- 封面显示正常
- 点击跳转视频播放器
- 播放器正常播放

---

#### C8 附件简历区组件
- [ ] 创建 `src/pkg-actor-card/view/components/AttachmentSection.vue`
- [ ] 接收 `attachment: AttachmentVO` prop
- [ ] 显示 PDF 图标 + 文件名 + "查看"按钮
- [ ] 点击调用 `listActorAssetPages(assetId)`，提取 `accessUrl` 数组
- [ ] 调用 `uni.previewImage({urls})` 分页预览（复用 00-214 逻辑）

**验收**：
- 附件入口显示正常
- 点击可分页预览 PDF
- 可左右滑动查看各页

---

#### C9 动态模块排序
- [ ] 根据 `settings.moduleOrder` 数组渲染模块
- [ ] 默认顺序：`["works", "photos", "video", "attachment"]`
- [ ] 使用 `v-for="module in orderedModules"` + `v-if` 条件渲染

**验收**：
- 后端修改 `settings.moduleOrder` 为 `["photos", "works", "video", "attachment"]`
- 前端页面模块顺序对应改变

---

#### C10 样式与布局
- [ ] 页面背景色 `#f5f5f5`
- [ ] 各区块间距 `32rpx`
- [ ] 卡片内边距 `32rpx`
- [ ] 标题字号 `32rpx`，加粗
- [ ] 正文字号 `28rpx`，行高 `1.6`

**验收**：视觉与设计稿一致（参考旧版 `ai-profile-card-detail` 布局）。

---

### 阶段 D：名片夹分享功能

#### D1 分享按钮 UI
- [ ] `pages/card-list/index.vue` - 已发布 Tab
- [ ] 每张卡片增加"分享"按钮
- [ ] 草稿 Tab 不显示分享按钮
- [ ] 按钮样式：主色调，圆角 8rpx

**验收**：已发布卡显示分享按钮，草稿卡不显示。

---

#### D2 分享逻辑实现
- [ ] 实现 `onShareAppMessage` 钩子
- [ ] 点击分享按钮时记录当前卡片到 `currentShareCard`
- [ ] 返回分享配置：
  - `title`: `"${ownerName} 的演员卡"`
  - `path`: `/pkg-actor-card/view/index?cardId=${cardId}`
  - `imageUrl`: `card.coverUrl`（预览图）

**验收**：
- 点击分享触发微信分享面板
- 分享卡片标题、封面、路径正确
- 观看者点击进入观看者页面

---

#### D3 封面预加载
- [ ] 分享前调用 `uni.getImageInfo(card.coverUrl)` 预加载封面
- [ ] 避免微信分享面板显示空白

**验收**：分享面板立即显示封面图，无空白闪烁。

---

### 阶段 E：门禁与回归验证

#### E1 编译门禁
- [ ] `vue-tsc --noEmit` 0 错误
- [ ] `npm run build:mp-weixin` 成功
- [ ] 产物 grep 核对：`dist/build` 与 `dist/dev` 双层均包含 `view/index` 相关文件

**验收**：编译成功，产物正确。

---

#### E2 包体门禁
- [ ] 主包 < 2MB
- [ ] `pkg-actor-card` 分包大小未超限
- [ ] 验证 `view/index` 落在分包内（不计入主包）

**验收**：包体审计通过，主包未增长。

---

#### E3 既有门禁回归
- [ ] `npm run verify:nav-title` 全绿
- [ ] `npm run verify:actor-card-attachment` 全绿
- [ ] 所有既有断言通过

**验收**：回归门禁无新增失败。

---

#### E4 功能回归测试
- [ ] 既有创建向导 7 步流程正常
- [ ] 生成演员卡功能正常
- [ ] 名片夹列表正常
- [ ] 附件简历（00-214）功能正常

**验收**：既有功能无退化。

---

### 阶段 F：新增门禁脚本（可选，建议）

#### F1 分享功能门禁
- [ ] `scripts/verify-actor-card-share.mjs`
- [ ] 断言：
  - [ ] `pages/card-list/index.vue` 包含 `onShareAppMessage`
  - [ ] 分享路径指向 `/pkg-actor-card/view/index`
  - [ ] `view/index.vue` 存在
  - [ ] `view/index.vue` 调用 `getPublicCard`
- [ ] `package.json` 新增 `"verify:actor-card-share": "node scripts/verify-actor-card-share.mjs"`

**验收**：脚本执行，全部断言通过。

---

### 阶段 G：文档同步

#### G1 更新 spec-code-mapping.md
- [ ] 新增 00-215 增量登记块
- [ ] 映射：
  - 后端：`ActorCardController` / `ActorCardPublishService` / `ActorCardPublicRespDTO`
  - 前端：`pages/card-list/index.vue` / `pkg-actor-card/view/index.vue` / `view/components/*` / `api/actor-card.ts`
  - 门禁：`scripts/verify-actor-card-share.mjs`（若有）

**验收**：映射完整，格式与既有块一致。

---

#### G2 更新 README.md
- [ ] Spec 目录 00-2xx 表新增 00-215 行
- [ ] 标注"已完成"状态
- [ ] 增量登记 bullet 更新：记录 00-215 已交付

**验收**：README 更新完整。

---

#### G3 更新 CURRENT_CONTEXT.md
- [ ] 小程序主线补充 00-215
- [ ] 更新"分享面"章节：当前存在分享出口
- [ ] 更新门禁章节：新增分享门禁（若有）

**验收**：当前上下文准确反映运行态。

---

#### G4 回填 00-206 / 00-214
- [ ] `00-206/requirements.md` - 更新 § 3.10（生成、预览与发布）
  - 补充"发布后可通过名片夹分享"
- [ ] `00-214/requirements.md` - G4 缺口状态更新
  - `showAttachment` 缺口闭合（00-215 已消费）
  - 附件渲染缺口闭合（00-215 已渲染）

**验收**：上游 Spec 状态准确。

---

#### G5 提交 Git
- [ ] 提交信息：`feat(sce): 00-215 v2.0 演员卡分享与观看者页面`
- [ ] 提交体：
  ```
  - 后端公开接口 GET /api/actor-card/public/:cardId（按 settings 控制字段返回）
  - 观看者落地页 pkg-actor-card/view/index（动态模块排序、三态处理）
  - 名片夹分享出口（onShareAppMessage + 封面预加载）
  - 闭合 00-214 两条缺口：showAttachment 有消费方、附件进渲染
  - 子组件：ProfileCard / WorksSection / PhotosSection / VideoSection / AttachmentSection
  - 门禁：verify:actor-card-share（若有）
  - 回填 00-206 / 00-214 文档
  ```

**验收**：提交成功，Git 历史清晰。

---

## 验收标准总览

### 功能验收
- [ ] 已发布卡可分享，草稿卡无分享按钮
- [ ] 观看者点击分享进入观看者页面
- [ ] 观看者页面展示主视觉、个人资料、参演作品、生活照片、视频、附件
- [ ] `settings` 开关生效（联系方式、视频、附件按设置显隐）
- [ ] `moduleOrder` 控制模块排列顺序
- [ ] 草稿卡访问返回"尚未发布"提示
- [ ] 不存在的卡访问返回"不存在"提示
- [ ] 剧照、生活照点击可预览大图
- [ ] 视频点击可播放
- [ ] 附件点击可分页预览（复用 00-214）

### 技术验收
- [ ] 后端接口返回数据结构与契约一致
- [ ] 签名 URL 10 分钟有效
- [ ] 接口在白名单内，无需鉴权
- [ ] `vue-tsc --noEmit` 0 错误
- [ ] `npm run build:mp-weixin` 成功
- [ ] 主包 < 2MB
- [ ] 产物 grep 核对通过
- [ ] 既有门禁全绿
- [ ] 新增门禁全绿（若有）

### 文档验收
- [ ] spec-code-mapping.md 新增 00-215 块
- [ ] README.md Spec 目录新增 00-215 行
- [ ] CURRENT_CONTEXT.md 更新分享面状态
- [ ] 00-206 / 00-214 文档回填
- [ ] tasks.md 执行记录完整

---

## 风险与依赖

### 依赖项
- `ActorMediaAssetService.generatePresignedUrl` 方法已实现
- `actor_card` 表字段完整（`status` / `profile_snapshot_json` / `photos_json` / `video_asset_id` / `attachment_asset_id` / `settings_json`）
- `actor_card_work` 表已建立
- `listActorAssetPages` API 已实现（00-214）
- `KpPageNav` 组件可用
- `pkg-tools/video-player` 页面可用

### 风险项
- 签名 URL 过期 → 缓解：前端检测 403 自动重新请求
- 大图加载慢 → 缓解：骨架屏 + CDN 加速
- 旧版页面参考代码可能过时 → 缓解：只参考布局思路，不直接复制

---

## 执行顺序建议

1. **阶段 A**（后端）→ Postman 验证接口可用
2. **阶段 B**（前端 API）→ 本地调用接口测试
3. **阶段 C**（观看者页面）→ 手动访问测试
4. **阶段 D**（分享功能）→ 微信开发者工具测试分享
5. **阶段 E**（门禁回归）→ 确保无退化
6. **阶段 F**（新增门禁，可选）
7. **阶段 G**（文档同步）→ 提交 Git

---

## 预估工作量

| 阶段 | 任务数 | 预估时间 |
|------|--------|----------|
| A（后端接口） | 6 | 4-6 小时 |
| B（前端 API） | 2 | 1 小时 |
| C（观看者页面） | 10 | 6-8 小时 |
| D（分享功能） | 3 | 2 小时 |
| E（门禁回归） | 4 | 1 小时 |
| F（新增门禁） | 1 | 1 小时（可选） |
| G（文档同步） | 5 | 1 小时 |
| **总计** | **31** | **16-20 小时** |

按"一次只做一个任务"原则，建议分 6-8 个会话完成。

---

## 实现记录（2026-08-14，核心交付）

按用户裁决实现 v2 分享闭环（此前 tasks 全部未勾选）。**完成范围**：

- **后端**（新 jar 已打包重启，本地验证）：
  - `GET /api/actor-card/public/{cardId}`：无需鉴权（`SecurityConfig` 白名单 `/actor-card/public/*`）；不存在 404「演员卡不存在」、草稿 403「该演员卡尚未发布」；解析 profile（`profileSnapshotJson`）/ works（`actor_card_work` 子表）/ photos / video / attachment（`attachmentAssetId`→文件名）；settings 控制 contact/video/attachment 显隐、`order`（前端实际字段名，非草案的 moduleOrder）；非公网 URL 资源（本地 wxfile:// 临时路径）过滤
  - `POST /api/actor-card/{cardId}/copy`：复制已发布卡为新草稿（含作品子表），返回新草稿 id
  - smoke 验证：404 / 已发布 200（完整数据）/ copy 生成新草稿
- **前端**：
  - `src/pkg-actor-card/view/index.vue` 观看者页（loading/error/loaded 三态；403/404 提示页；主视觉/资料卡/按 order 渲染模块；照片/剧照 previewImage；视频 `<video>`；附件 listActorAssetPages 预览——未登录 401 提示）
  - `pages.json` 注册 `pkg-actor-card/view/index`
  - 名片夹已发布卡三操作：预览（generate?preview=1）/ 分享（`open-type="share"` + `onShareAppMessage` → `/pkg-actor-card/view/index?cardId={id}`）/ 复制创建（copyActorCard → 跳新草稿）
  - api：`getPublicCard` / `copyActorCard` + `ActorCardPublicVO` 类型
- **门禁**：`vue-tsc` 0、`build:mp-weixin` EXIT=0（postbuild 曾因微信开发者工具锁定 app.js 失败，CLI 关项目后重同步成功）、`verify:nav-title` 97/97、`verify:actor-card-attachment` 17/17、双层产物核对通过

**数据缺口（如实登记，独立立项）**：v2 向导照片/视频/剧照存本地临时路径，公开接口过滤后观看页显示占位；资源上传链路（00-206 遗留）接通后自然填充。

**未实现（00-215 §7 待定项）**：分享统计、海报生成、观看者互动（点赞/评论/收藏）、卡主编辑入口。
