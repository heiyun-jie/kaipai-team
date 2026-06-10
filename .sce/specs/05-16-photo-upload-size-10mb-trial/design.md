# Photo 上传 10MB 试用 - 技术设计

## 1. 变更范围

_Requirements: 3.1, 3.2, 3.3_

本次只调整 `photo` 上传类型：

- 前端：`kaipai-frontend/src/utils/upload.ts`
- 后端：`kaipaile-server/src/main/java/com/kaipai/integration/storage/CosUtil.java`
- 后端接口说明：`kaipaile-server/src/main/java/com/kaipai/controller/api/file/FileController.java`
- 验收脚本：`.sce/specs/05-16-photo-upload-size-10mb-trial/verify-photo-upload-size.mjs`

## 2. 前端设计

_Requirements: 3.1, 3.2, 3.3_

`UPLOAD_SIZE_LIMITS.photo` 从 `5 * 1024 * 1024` 改为 `10 * 1024 * 1024`。

`UPLOAD_SIZE_MESSAGES.photo` 从 `作品图片不能超过5MB` 改为 `作品图片不能超过10MB`。

其他字段保持不变：

- `avatar: 2 * 1024 * 1024`
- `license: 5 * 1024 * 1024`
- `pdf: 20 * 1024 * 1024`
- `video: 100 * 1024 * 1024`

## 3. 后端设计

_Requirements: 3.1, 3.2, 3.3_

`CosUtil.PHOTO_MAX_SIZE` 从 `5 * MB` 改为 `10 * MB`。

`imageMaxSizeMessage("photo")` 从 `作品图片不能超过5MB` 改为 `作品图片不能超过10MB`。

`imageMaxSizeMessage(default)` 从 `图片大小不能超过5MB` 改为 `图片大小不能超过10MB`，因为默认分支实际使用 `PHOTO_MAX_SIZE`。

`FileController.uploadPhoto` 的 OpenAPI 描述从 `每张建议不超过 5MB` 改为 `每张建议不超过 10MB`。

头像、营业执照、PDF、视频的上限和文案保持不变。

## 4. 验证设计

_Requirements: 3.1, 3.2, 3.3_

新增静态验收脚本 `verify-photo-upload-size.mjs`，检查：

1. 前端 `photo` 限制为 `10 * 1024 * 1024`。
2. 前端 `photo` 文案为 `作品图片不能超过10MB`。
3. 前端非 `photo` 限制保持既有值。
4. 后端 `PHOTO_MAX_SIZE` 为 `10 * MB`。
5. 后端 `photo` 文案为 `作品图片不能超过10MB`。
6. 后端 `license` 文案仍为 `营业执照图片不能超过5MB`。
7. 后端 `/upload/photo` 接口说明为 `每张建议不超过 10MB`。

构建验证：

- `cd kaipai-frontend && npm run build:mp-weixin`

可选后端编译验证：

- `cd kaipaile-server && mvn -DskipTests compile`
