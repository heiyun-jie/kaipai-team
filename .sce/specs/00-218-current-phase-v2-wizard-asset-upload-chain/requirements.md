# v2 向导资源上传链路（首图/照片/视频/剧照）

## 1. 概述

解决 v2 演员卡向导的**资源上传缺口**：此前首图/生活照片/视频/剧照都存**本地临时路径**（`wxfile://`），导致观看页无法展示、AI 扩图拿不到公网 URL、名片夹封面失效（00-213 已登记）。本 Spec 把 4 处资源改为**上传腾讯云公有桶**，保存持久公网 URL。

**上游依赖**：`00-206`（v2 向导）、`00-215`（观看页依赖可访问 URL）、`00-213`（审计登记的 wxfile 缺陷）

**后端能力**：`POST /api/file/upload/photo|video`（1.0 已有，需登录，公有桶 `kaipai-1412601014`，返回 `https://{bucket}.cos.{region}.myqcloud.com/{key}` 持久 URL）——**后端零改动**。

---

## 2. 用户故事

- 作为演员，我上传首图/照片/视频/剧照后，资源应存到服务器，**分享出去别人能看到**、AI 扩图能成功
- 作为维护者，发版兼容：旧草稿/已发布卡的临时路径数据不迁移（无法访问），前端展示兜底；新数据全为公网 URL

---

## 3. 功能需求

### 3.1 首图上传（step-visual）

**验收标准**：
- WHEN 选首图 THEN 上传 `/api/file/upload/photo`，`sourceImageUrl` 存公网 URL（非临时路径）
- WHEN 发起 AI 扩图 THEN `submitExpandImage` 传公网 URL（后端可访问）
- WHEN 上传失败 THEN toast 提示，不写入本地路径

### 3.2 生活照片上传（step-photos）

**验收标准**：
- WHEN 从手机选择照片 THEN 逐张上传，`photosJson` 存 URL 数组
- WHEN 回填已存草稿 THEN 直接显示 URL

### 3.3 视频上传（step-video）

**验收标准**：
- WHEN 选择视频 THEN 上传 `/api/file/upload/video`，`videoUrl` 存公网 URL

### 3.4 作品剧照上传（step-works）

**验收标准**：
- WHEN 添加剧照 THEN 上传图片，`stills` 存 URL（落 `actor_card_work.stills_json`）

### 3.5 发版兼容

**验收标准**：
- 旧数据（临时路径）不迁移：前端对非公网 URL 显示占位/过滤（00-215 已实现 `isHttpUrl` 过滤）
- 上传接口为既有接口（向后兼容）；新前端调用需登录（本就需要登录）

---

## 4. 非功能需求

- 上传封装 `src/api/file.ts`（uni.uploadFile + Bearer token）
- 上传中 loading 提示；失败明确 toast，不静默写入
- 视频 ≤100MB、图片 ≤10MB（后端 CosUtil 校验）

---

## 5. 约束条件

- 后端零改动（复用 `/api/file/upload/*`）
- 不改 `actor_card` 表结构（URL 存既有字段）
- 构建后核对产物（00-216 流程）

---

## 6. 验收标准总览

- [ ] 4 处接入上传（首图/照片/视频/剧照），保存公网 URL
- [ ] 扩图链路可用公网 URL
- [ ] 上传失败有提示
- [ ] `vue-tsc` 0 / `build:mp-weixin` EXIT=0 / 门禁全绿 / 双侧产物核对
- [ ] 发版兼容登记（旧数据兜底、接口既有）
