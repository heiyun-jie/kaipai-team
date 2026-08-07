# v2.0 小程序演员卡创建向导 - 技术设计

_Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9, 3.10, 3.11, 3.12, 3.13_

## 1. 路由配置

### 主包路由（变更）

| 路由                     | 说明           | 变更类型 |
|--------------------------|----------------|----------|
| `pages/home/index`       | 首页改版       | 修改     |
| `pages/mine/index`       | 个人中心改版   | 修改     |
| `pages/card-list/index`  | 名片夹（新 Tab）| 新增     |

### 新分包路由（`pkg-actor-card`）

| 路由                                   | 说明            |
|----------------------------------------|-----------------|
| `pkg-actor-card/create/index`          | 创建向导 Hub    |
| `pkg-actor-card/step-visual/index`     | 步骤 1 主视觉   |
| `pkg-actor-card/step-profile/index`    | 步骤 2 个人资料 |
| `pkg-actor-card/step-works/index`      | 步骤 3 参演作品 |
| `pkg-actor-card/step-photos/index`     | 步骤 4 生活照片 |
| `pkg-actor-card/step-video/index`      | 步骤 5 视频简历 |
| `pkg-actor-card/step-attachment/index` | 步骤 6 附件简历 |
| `pkg-actor-card/step-settings/index`   | 步骤 7 生成设置 |
| `pkg-actor-card/generate/index`        | 生成预览与发布  |

`pages.json` 需同步变更：`tabBar.list` 第二项改为 `card-list`；`subpackages` 新增 `pkg-actor-card` 条目。

---

## 2. 分包目录结构

```
src/pkg-actor-card/
├── create/index.vue          向导 Hub（7步总览）
├── step-visual/index.vue     步骤1 主视觉照片
├── step-profile/index.vue    步骤2 个人资料
├── step-works/
│   ├── index.vue             步骤3 参演作品
│   └── StillsManager.vue     剧照管理子组件（可复用）
├── step-photos/index.vue     步骤4 生活照片
├── step-video/index.vue      步骤5 视频简历
├── step-attachment/index.vue 步骤6 附件简历
├── step-settings/index.vue   步骤7 生成设置
└── generate/index.vue        AI生成 + 预览 + 发布
```

---

## 3. 后端 API 合同（新增）

> AI 相关调用由后端统一封装，前端只调用下列业务接口。

### 3.1 演员卡草稿管理

```
POST   /api/actor-card/draft/create         创建草稿，返回 draftId
PUT    /api/actor-card/draft/:id/step/:step 按步骤自动保存（debounce 2s）
GET    /api/actor-card/draft/:id            读取草稿完整数据
GET    /api/actor-card/drafts               获取当前用户草稿列表
DELETE /api/actor-card/draft/:id            删除草稿
```

### 3.2 背景图库

```
GET /api/actor-card/background-library?style=classic|urban|ancient|fresh
返回：{ style, images: [{ id, url, thumbnailUrl }] }
背景图不进入用户素材库，前端只读展示
```

### 3.3 AI 首图扩图

```
POST /api/actor-card/ai/expand-image
body: { draftId, sourceImageUrl }
返回：{ taskId }（异步）
GET  /api/actor-card/ai/expand-image/:taskId
返回：{ status: pending|done|failed, originalUrl, expandedUrl }
```

### 3.4 演员卡生成

```
POST /api/actor-card/generate
body: { draftId }
返回：{ taskId }（异步）
GET  /api/actor-card/generate/:taskId
返回：{ status: pending|done|failed, previewUrl, cardId }
```

### 3.5 演员卡发布与名片夹

```
POST /api/actor-card/:cardId/publish      发布演员卡
GET  /api/actor-card/list?status=published|draft  名片夹列表
GET  /api/actor-card/:cardId              演员卡详情
DELETE /api/actor-card/:cardId            删除草稿或已发布卡
```

### 3.6 资料完整度（个人中心）

```
GET /api/actor/profile/completeness
返回：{ percentage, stats: { cardCount, materialCount, viewCount } }
```

---

## 4. 状态管理

新建 `src/stores/actor-card-draft.ts`：

```ts
interface ActorCardDraftStore {
  draftId: string | null
  currentStep: number        // 1-7
  stepStatus: StepStatus[]   // 每步完成状态
  visualData: VisualStepData
  profileData: ProfileStepData
  worksData: WorksStepData
  photosData: PhotosStepData
  videoData: VideoStepData
  attachmentData: AttachmentStepData
  settingsData: SettingsStepData
  // actions
  initDraft(): Promise<void>
  saveStep(step: number, data: any): Promise<void>
  loadDraft(draftId: string): Promise<void>
}
```

---

## 5. 关键页面模板结构

### 5.1 向导 Hub 页（`create/index.vue`）

```
<顶部进度条 "创建进度 X/7">
<标题区 "准备演员资料" + 副标题>
<步骤列表>
  <StepRow v-for="step in steps" :status="step.status" @click="navigate(step)"/>
</步骤列表>
<底部按钮 "继续下一项" | "生成演员卡">
```

### 5.2 参演作品页（`step-works/index.vue`）

```
<进度条 "3/7">
<Tab 从演艺经历选择 | 新增作品>
<作品列表>
  <WorkCard v-for="work" :selected="work.selected">
    <checkbox + 类型Badge + 作品名 + 饰演角色 + 已选X/3>
    <StillsManager :workId="work.id" :stills="work.stills"/>  ← 仅已选作品展开
  </WorkCard>
</作品列表>
<添加其他作品按钮>
<底部状态行 "已选择N部作品">
<下一步按钮>
```

### 5.3 生活照片页（`step-photos/index.vue`）

```
<进度条 "4/7">
<超12张软提示 Banner（v-if）>
<双按钮 从素材库选择 | 从手机上传>
<"已选择N张" + "调整顺序"链接>
<SortablePhotoGrid :photos="photos" @reorder="onReorder"/>
<底部提示 "长按照片可调整展示顺序">
<下一步按钮>
```

---

## 6. 交互逻辑

### 6.1 自动保存

每个步骤页离开前或数据变化时触发 `saveStep(step, data)（debounce 2s）`，保存失败时仅打印 console 警告，不中断用户操作。

### 6.2 步骤跳转

所有步骤页使用 `uni.navigateTo` 跳转，Hub 页始终保留在页面栈底。步骤内的「下一步」按钮先校验本步骤再跳 Hub 或下一步。

### 6.3 AI 扩图轮询

提交扩图后，每 2s 轮询一次 `GET /api/actor-card/ai/expand-image/:taskId`，超过 60s 判定超时显示失败态，允许用户重新生成。

### 6.4 步骤 3 校验门禁

「下一步」点击时遍历已勾选作品，若任意作品 stills.length === 0 则滚动到该作品并展示错误提示，不允许跳转。

---

## 7. 页面跳转关系

```
首页 → pkg-actor-card/create（新建或恢复草稿）
首页（点击风格图）→ pkg-actor-card/step-visual（带 style 参数）
pkg-actor-card/create → 任意步骤页（双向）
步骤页 → pkg-actor-card/generate（完成所有必填步骤后）
pkg-actor-card/generate（发布）→ pages/card-list（名片夹）
pkg-actor-card/generate（退出）→ pages/card-list（草稿 Tab）
```

---

## 8. 数据库变更（后端）

```sql
-- 演员卡主表（草稿 + 已发布）
actor_card (id, user_id, status, style, draft_data_json,
            published_version, created_at, updated_at)

-- 演员卡参演作品快照
actor_card_work (id, card_id, work_title, role_name, work_type,
                 stills_json, sort_order)

-- 背景图库（可配置）
actor_card_background (id, style, image_url, thumbnail_url, sort_order, enabled)
```
