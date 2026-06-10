# Photo 上传 10MB 试用 - 执行记录

## 2026-06-10

### 背景

用户确认采用方案 A：将当前 `photo` 图片上传从 5MB 放开到 10MB。由于 `05-15` 的 AI 分析图上传复用 `photo` 类型，且上传后同步进入演员档案照片池，本次试用按 `photo` 统一调整，而不是新增独立 `analysis` 上传类型。

### 范围

- 前端 `photo` 上传本地大小校验改为 10MB。
- 后端 `photo` 上传强校验改为 10MB。
- 前后端 `photo` 文案与后端接口说明同步为 10MB。
- 头像、营业执照、PDF、视频限制不变。

### 验证记录

- 已执行红灯验证：`node .sce/specs/05-16-photo-upload-size-10mb-trial/verify-photo-upload-size.mjs .`
  - 结果：失败于 `frontend photo size limit missing: photo: 10 * 1024 * 1024`，确认脚本能识别当前 5MB 状态。
- 已执行绿灯验证：`node .sce/specs/05-16-photo-upload-size-10mb-trial/verify-photo-upload-size.mjs .`
  - 结果：通过，输出 `Photo upload size verification passed.`
- 已执行小程序构建：`cd kaipai-frontend && npm run build:mp-weixin`
  - 结果：通过，输出 `DONE Build complete.` 与 `synced mp-weixin build to dev`。
  - 备注：构建过程仍有既有 `Dart Sass legacy JS API` deprecation warning 与 uni-app 更新提示，不影响本次构建结果。
- 已执行后端编译：`cd kaipaile-server && mvn -DskipTests compile`
  - 结果：通过，输出 `BUILD SUCCESS`。
  - 备注：编译过程提示部分 AI 相关源码使用或覆盖了已过时 API，为既有编译 warning；本次未触碰相关文件。
