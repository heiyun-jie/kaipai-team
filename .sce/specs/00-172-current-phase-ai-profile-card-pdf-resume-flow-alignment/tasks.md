# 00-172 任务

## Phase 1: Spec

- [x] 新增 `00-172`，承接 AI 分享图详情页与 `05-13` PDF 简历展示范围同步问题。
- [x] 明确本轮只补 AI 分享图详情页前端展示，不改 PDF 上传/转换和 AI 生成合同。
- [x] 明确 PDF 展示资格单一来源为 `ActorProfile.resumePdfPageImageUrls`。

## Phase 2: Frontend

- [x] 在 `pkg-card/ai-profile-card-detail/index.vue` 新增 PDF 图片页计算属性。
- [x] 在 AI 分享图详情页内容流新增 PDF 简历 section。
- [x] 将 PDF 简历 section 放在内容流最底部。
- [x] 新增 PDF 页预览函数。
- [x] 新增 PDF section 样式。

## Phase 3: Verification

- [x] 前端类型检查通过。
- [x] 微信小程序构建通过。
- [x] 小程序包体审计通过。
- [x] 构建产物确认包含 AI 分享图详情页 PDF 简历区块。
- [x] 自动化 H5 E2E 覆盖 mock actor snapshot 到 AI 分享图详情页 PDF 简历渲染链路。

## Acceptance

- [x] AI 分享图详情页能展示演员档案 PDF 简历图片页。
- [x] PDF 展示判断不新增第二事实源。
- [x] 不改变 `00-171` 单封面合同。
- [x] 自动化断言覆盖 PDF section 标题、文件名、页数、页容器与两张 PDF 图片页 URL。
- [x] 自动化断言覆盖 PDF section 位于内容流视频简历之后。
