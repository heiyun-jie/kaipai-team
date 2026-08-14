# v2 向导资源上传链路 - 任务清单

_Requirements: ALL_
_Design: ALL_

## T1 上传封装

新建 `src/api/file.ts`（`uploadImageFile` / `uploadVideoFile`，uni.uploadFile + Bearer）。

**Validates: Requirements 4**

## T2 首图上传（step-visual）

`pickHeroImage`：选图 → 上传 → `sourceImageUrl` 存 URL；失败 toast；扩图传 URL。

**Validates: Requirements 3.1**

## T3 生活照片上传（step-photos）

`fromPhone`：逐张上传 → `photos` 存 URL（`photosJson` 落 URL 数组）。

**Validates: Requirements 3.2**

## T4 视频上传（step-video）

`pickVideo`：上传 → `videoUrl` 存 URL。

**Validates: Requirements 3.3**

## T5 作品剧照上传（step-works）

`addStill`：逐张上传 → `work.stills` 存 URL（落 `stills_json`）。

**Validates: Requirements 3.4**

## T6 构建与验证

`vue-tsc` 0；`build:mp-weixin` EXIT=0；产物核对（4 处页面含 `uploadImageFile/uploadVideoFile`、无 wxfile 落库）；`verify:nav-title` / `verify:actor-card-attachment` 全绿；`verify:actor-card-wizard`（若有）检查 saveStep 不含本地路径断言。

**Validates: Requirements 6**
