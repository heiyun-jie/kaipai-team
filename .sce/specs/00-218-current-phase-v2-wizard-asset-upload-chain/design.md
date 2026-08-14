# v2 向导资源上传链路 - 技术设计

_Requirements: ALL_

## 1. 上传封装（`src/api/file.ts`）

```ts
export function uploadImageFile(filePath: string): Promise<string>  // POST /api/file/upload/photo
export function uploadVideoFile(filePath: string): Promise<string>  // POST /api/file/upload/video
```

- `uni.uploadFile` + `Authorization: Bearer {token}`（复用 `uploadActorAsset` 模式）
- 响应 `{ code, data: url }` → 返回公网 URL；失败 reject(message)

## 2. 接入点（4 处）

| 页面 | 原行为 | 新行为 |
|------|--------|--------|
| `step-visual.pickHeroImage` | `sourceImageUrl = tempFilePath` | `sourceImageUrl = await uploadImageFile(path)`（loading + 失败 toast） |
| `step-photos.fromPhone` | `photos.push(tempFilePath)` | 逐张 `uploadImageFile` 后 push URL（`photosJson` 落 URL 数组） |
| `step-video.pickVideo` | `videoUrl = tempFilePath` | `uploadVideoFile` 后设 URL |
| `step-works.addStill` | `work.stills.push(tempFilePath)` | 逐张 `uploadImageFile` 后 push URL（`stills` 落 URL） |

## 3. 数据流（上传后）

- `actor_card.sourceImageUrl / expandedImageUrl / photosJson / videoUrl` ← 公网 URL
- `actor_card_work.stills_json` ← URL 数组
- 观看页（00-215 `isHttpUrl` 过滤）→ 可展示；扩图（AI provider 需公网）→ 可用

## 4. 发版兼容

- **旧数据不迁移**：存量草稿/已发布卡的临时路径无法访问，前端已兜底（空态/占位/过滤）；用户重新上传即得 URL
- **接口既有**：`/api/file/upload/photo|video` 1.0 已有（需登录），新前端调用向后兼容
- **发布**：前后端无新接口依赖（上传接口已存在）→ 前端单方发版即可
- **防御**：上传失败不写入本地路径（拒绝把 wxfile 当 URL 落库的旧缺陷复发）

## 5. 风险

- 视频大文件上传耗时 → loading 提示；失败可重选
- 图片数量多（照片 9 张/剧照 3 张）逐张上传 → 顺序执行，失败中断并提示
