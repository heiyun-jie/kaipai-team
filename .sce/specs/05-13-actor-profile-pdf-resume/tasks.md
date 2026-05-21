# 演员档案 PDF 简历上传与图片页渲染 Tasks

## Phase 1: Spec

- [x] 新增 `05-13`，锁定 PDF 转图片页方案。
- [x] 明确第一版不做 OCR、结构化解析或自动回填。
- [x] 明确 PDF 作为公开详情页原稿附件展示。

## Phase 2: Backend

- [x] 新增 PDF 上传 DTO。
- [x] 扩展 COS 上传工具，支持 PDF 和服务端生成图片上传。
- [x] 引入 PDFBox 并实现 PDF 转图片页服务。
- [x] 新增 `/api/file/upload/pdf`。
- [x] 扩展 `ActorProfileDTO / ActorProfileSaveDTO`。
- [x] 将 PDF 元数据保存到 `actor_profile.extended_field`。

## Phase 3: Frontend

- [x] 扩展 `ActorProfile` 类型和表单模型。
- [x] 新增 PDF 文件选择与上传工具。
- [x] 新增 `PdfResumeSection` 并接入资料编辑页。
- [x] 公开详情页新增 PDF 图片页渲染区块。

## Phase 4: Verification

- [x] 后端编译通过。
- [x] 前端类型检查通过。
- [x] 微信小程序构建通过。
- [x] 小程序包体审计通过。
- [ ] 使用样例 PDF 完成真实上传与详情页展示检查。
