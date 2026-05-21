# AI 分享图固定三页资料册 - 技术设计

> 状态：已被 `00-171-current-phase-ai-profile-card-single-cover-theme-flow` 取代。本文仅保留历史记录，不再指导当前实现。

## 1. 设计结论

本需求采用固定三页结构，不做任意页数：

```text
AI profile card album
  1. cover   - 封面摘要页
  2. resume  - 履历信息页
  3. gallery - 影像作品页
```

继续沿用现有稳定原则：

```text
AI provider -> 只生成背景图
前端/合成器 -> 渲染真实文字、照片、视频、卡片和交互
```

`cover` 继续承担分享封面和第一屏视觉，`resume` / `gallery` 承担资料扩展。三页不是三张“AI 画好的完整海报”，而是三张风格统一的背景页加确定性前景。

## 2. 与现有能力的关系

### 2.1 复用

1. 复用 `00-160` 的 AI 任务入口和 provider registry。
2. 复用 `00-164` 的 deterministic overlay 思路。
3. 复用 `00-166` 的 `750 x 1334` authoritative design canvas。
4. 复用 `00-167` 的首屏 derivative 与非关键请求后置策略。

### 2.2 扩展

1. 从“一个任务一张图”扩展为“一个主任务三个页面资产”。
2. 从“单页 preset”扩展为“按 pageType 拆分的 preset 集合”。
3. 从“详情页单张 poster”扩展为“详情页三页连续浏览”。

### 2.3 明确不做

1. 不把三页拼成一张超长图。
2. 不把 AI 背景图升级为事实源。
3. 不在后台暴露“页数”配置项。

## 3. 后端数据设计

### 3.1 现有主表保留

现有 `actor_ai_profile_card_task` 继续作为主任务表，保留兼容字段：

```text
task_id
share_card_id
template_scene_code
style_code
source_image_url
provider_code
model_code
prompt_json
prompt_text
negative_prompt
status
generated_image_url   // 兼容旧单页，未来映射 cover 背景
```

### 3.2 新增页面资产表

新增：

```sql
CREATE TABLE actor_ai_profile_card_page (
  page_id BIGINT PRIMARY KEY AUTO_INCREMENT,
  task_id VARCHAR(64) NOT NULL,
  share_card_id BIGINT NULL,
  page_no INT NOT NULL,
  page_type VARCHAR(32) NOT NULL,
  prompt_json LONGTEXT NULL,
  prompt_text LONGTEXT NULL,
  negative_prompt LONGTEXT NULL,
  provider_code VARCHAR(64) NULL,
  model_code VARCHAR(128) NULL,
  status VARCHAR(32) NOT NULL,
  generated_image_url VARCHAR(1024) NULL,
  failure_reason VARCHAR(1000) NULL,
  started_at DATETIME NULL,
  completed_at DATETIME NULL,
  create_time DATETIME NULL,
  last_update DATETIME NULL,
  UNIQUE KEY uk_task_page_no (task_id, page_no),
  UNIQUE KEY uk_task_page_type (task_id, page_type)
);
```

### 3.3 页面 DTO

新增页面 DTO：

```json
{
  "pageNo": 1,
  "pageType": "cover",
  "status": "success",
  "generatedImageUrl": "https://...",
  "providerCode": "tencent-hunyuan",
  "modelCode": "hunyuan-image-3.0",
  "failureReason": ""
}
```

扩展现有 task / artifact DTO：

```json
{
  "taskId": "aipf_xxx",
  "status": "success",
  "generatedImageUrl": "https://cover-background-url",
  "pages": [
    { "pageNo": 1, "pageType": "cover", "status": "success" },
    { "pageNo": 2, "pageType": "resume", "status": "success" },
    { "pageNo": 3, "pageType": "gallery", "status": "success" }
  ]
}
```

兼容策略：

1. 旧 artifact 没有 `pages` 时，前端按 v1 单页渲染。
2. 新 artifact 继续填充主表 `generated_image_url = cover.generated_image_url`，避免旧入口立即断裂。

## 4. 生成编排

### 4.1 主流程

```text
POST /api/ai/profile-card/generate
  -> 创建主任务
  -> 创建固定 3 个 page 记录
  -> 后台异步生成 cover / resume / gallery
  -> 全部成功后创建/更新 share card
  -> 主任务 success
```

第一版建议页面生成策略：

1. 可并行生成 3 页，以缩短总耗时。
2. `cover`、`resume`、`gallery` 各自保留独立 prompt。
3. 只要任一页失败，主任务即失败。
4. 后续如做重试，只重试失败页，不重跑成功页。

### 4.2 页面角色

#### cover

目标：

- 右侧人物主视觉；
- 左侧身份摘要；
- 少量事实、少量技能、一个作品摘要；
- 维持当前分享封面价值。

AI 背景：

- 可以含主肖像；
- 必须保留现有 subjectBox / identitySafeArea 思路；
- 继续沿用当前 hero-right 构图。

#### resume

目标：

- 完整基础资料；
- 形象 / 发型 / 语言；
- 技能组；
- 长简介；
- 多条作品履历。

AI 背景：

- 优先纯背景或弱人物环境图；
- 大面积低细节区域；
- 不再重复强人物主视觉，避免挤压内容和多页脸部不一致。

#### gallery

目标：

- portrait / lifestyle / production 分类照片；
- 作品剧照；
- 视频简历入口；
- 可补充联系前的视觉印象。

AI 背景：

- 优先轻背景；
- 可带摄影棚、胶片、布光、场记板气氛，但不能生成真实界面或文字；
- 大面积留给图片网格。

## 5. Prompt Agent 设计

### 5.1 输出结构

从单页：

```json
{
  "fixedLayout": {}
}
```

扩展为：

```json
{
  "album": {
    "pageCount": 3,
    "pages": [
      {
        "pageNo": 1,
        "pageType": "cover",
        "fixedLayout": {}
      },
      {
        "pageNo": 2,
        "pageType": "resume",
        "fixedLayout": {}
      },
      {
        "pageNo": 3,
        "pageType": "gallery",
        "fixedLayout": {}
      }
    ]
  }
}
```

每页必须包含：

```text
pageType
designCanvas
providerCanvas
layoutPreset
backgroundPolicy
subjectPolicy
safeAreas
slots
```

### 5.2 页面级 prompt 原则

所有 provider 都必须收到：

1. `background only`
2. `no readable text`
3. `no cards / no boxes / no fake UI`
4. 页面的留白目标和风格目标

Tencent 这类易改写 provider 必须继续默认关闭 prompt rewrite，并避免把 slot 名称、坐标标签、`profile-card`、`UI zone` 等容易被画出来的词直接投喂给模型。

## 6. 前端设计

### 6.1 页面结构

当前：

```text
ai-profile-card-detail
  poster
```

升级后：

```text
ai-profile-card-detail
  album
    cover-page
    resume-page
    gallery-page
```

### 6.2 前端数据类型

扩展 `AiProfileCardTask` / `AiProfileCardArtifact`：

```ts
export type AiProfileCardPageType = 'cover' | 'resume' | 'gallery';

export interface AiProfileCardPage {
  pageNo: 1 | 2 | 3;
  pageType: AiProfileCardPageType;
  status: 'pending' | 'running' | 'success' | 'failed';
  generatedImageUrl?: string;
  providerCode?: string;
  modelCode?: string;
  failureReason?: string;
}
```

### 6.3 Preset registry

当前 `layout-presets.ts` 是单页 slot registry。升级后建议结构：

```ts
export type AiProfileAlbumPageType = 'cover' | 'resume' | 'gallery';

export interface AiProfileAlbumPagePreset {
  pageType: AiProfileAlbumPageType;
  slots: Record<string, AiProfilePosterSlot>;
}

export interface AiProfileAlbumPreset {
  scene: CardScene;
  code: string;
  pages: Record<AiProfileAlbumPageType, AiProfileAlbumPagePreset>;
}
```

各页 slot 分工：

```text
cover:
  identity, facts, skills, works, photos, intro, video

resume:
  title, basics, appearance, languages, skills, intro, workTimeline

gallery:
  title, portraitPhotos, lifestylePhotos, productionPhotos, workPhotos, video
```

### 6.4 渲染与加载

1. `cover` 首屏优先加载。
2. `resume` / `gallery` 使用 lazy image 或进入视口前再加载。
3. 三页都使用固定 9:16 容器。
4. 底部操作栏只属于页面级，不得侵入每张 poster 的坐标映射。
5. 三页内容仍全部来自实时 profile snapshot / 当前分享卡事实源，不从 AI bitmap 读取业务数据。

## 7. 分享与作品集

### 7.1 分享

1. 默认分享图继续使用 `cover`。
2. 分享路径继续进入 AI 详情页。
3. 当前阶段不实现三页拼接导出。

### 7.2 作品集

1. 作品集卡片继续展示封面页。
2. 进入详情后展示完整三页。
3. 若任务旧制无 `pages`，作品集仍按旧单页打开。

## 8. 管理后台与配置

### 8.1 固定边界

后台不新增“页数”输入框。当前业务能力固定为 3 页。

### 8.2 需要可见的运营信息

如果后续后台要观察 AI 任务，建议新增：

```text
pageCount = 3
completedPageCount
failedPageType
```

但这属于任务可观测性，不是页数配置能力。

## 9. 测试设计

### 9.1 后端

1. 主任务创建时固定创建 3 页。
2. 页序固定。
3. 每页 prompt 都带 pageType 和独立 layout。
4. 任一页失败时主任务失败。
5. 旧单页任务 DTO 兼容。
6. provider 默认仍关闭 prompt rewrite。

### 9.2 前端

1. `pages` 存在时渲染三页。
2. `pages` 缺失时回退单页。
3. 每页使用自己的 preset slot。
4. `cover` 外的页面不影响首屏性能。
5. 三页内容无溢出、无重叠、无被底栏遮挡。

### 9.3 真人 E2E

必须截图覆盖：

1. 登录
2. 发起生成
3. 作品集任务
4. `cover`
5. `resume`
6. `gallery`

必须人工检查：

1. 三页顺序正确；
2. 三页背景风格一致；
3. `cover` 人物位置遵守 agent 输入；
4. `resume` / `gallery` 没有 AI 假文字、假模块；
5. 三页真实资料没有截断、错位或前后不一致；
6. 分享入口仍指向三页详情页。

## 10. 分阶段实施建议

### Phase 1: 合同先行

1. 新增数据库页面资产模型。
2. 扩展 DTO。
3. 扩展 agent 输出三页 contract。
4. 保持现有 UI 先兼容旧单页。

### Phase 2: 三页生成

1. 后端固定创建三页。
2. provider 逐页生成。
3. 主任务汇总状态。

### Phase 3: 三页详情页

1. 前端 album preset。
2. 三页连续渲染。
3. 非首屏懒加载。

### Phase 4: 验证与收口

1. 自动化测试。
2. 真人 E2E。
3. 后台任务可观测性按需要补充。

## 11. 关键取舍

1. **固定 3 页，不做任意页数**：降低成本波动和布局复杂度。
2. **只让 `cover` 画清晰主肖像**：降低多页脸部不一致风险。
3. **不做三页拼接导出**：先保详情页体验，避免把问题重新变成长图合成。
4. **保留旧单页兼容**：避免历史 artifact 失效。
