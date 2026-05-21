# AI 分享图单封面主题内容流 - 技术设计

## 1. 设计结论

本轮直接废弃旧三页生成主线，目标态为：

```text
AI provider -> 生成 1 张 cover background
后端 -> 持久化 generatedImageUrl + 返回任务级 theme
前端 -> cover poster + deterministic content flow
```

`resume / gallery` 不再是生成页面，也不再需要连续性参考带。封面以下的资料由前端普通内容流承载，背景使用同一套主题底色。

设计前提补充：

1. 当前功能的主用户是演员本人，外部访客只消费公开详情页，不新增剧组端工作台。
2. 新主路径的 canonical asset 是 `generatedImageUrl`，不是 `pages` 列表。
3. `pages`、continuity 字段和 page entity 只作为历史兼容残留，不作为新任务成功条件。

## 2. 后端设计

### 2.1 任务模型

继续使用 `actor_ai_profile_card_task` 主表：

```text
task_id
user_id
actor_profile_id
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
generated_image_url
```

不再为新任务创建 `actor_ai_profile_card_page` 记录。页面表只保留为历史数据兼容和删除清理用途。

### 2.2 生成流程

新流程：

```text
POST /api/ai/profile-card/generate
  -> 创建主任务 pending
  -> 异步 runGeneration
  -> promptAgent.generate(...) 只生成 cover
  -> 质检封面（如配置启用）
  -> 上传生成图
  -> 创建/更新普通 share card config
  -> generated_image_url = cover background
  -> status = success
```

删除旧流程中的：

1. 固定 `cover / resume / gallery` page defs。
2. 非封面页生成。
3. 底部裁切 continuity reference。
4. 页面级成功/失败汇总作为任务成功标准。

### 2.3 Theme Payload

任务和作品 DTO 增加：

```json
{
  "theme": {
    "backgroundColor": "#f5f3ee",
    "surfaceColor": "#fbfaf6",
    "surfaceStrongColor": "#eadfce",
    "accentColor": "#8c6f4f",
    "textColor": "#231b15",
    "mutedTextColor": "#6c7483",
    "borderColor": "rgba(35, 27, 21, 0.12)"
  }
}
```

第一版 theme 由 `templateSceneCode/styleCode` 固定映射，且同一映射要被 prompt 色彩方向使用。后续如需要取图像主色，可在该 DTO 上扩展来源字段。

### 2.4 Prompt Agent

`AiProfileCardPromptAgent` 收敛为单封面背景合同：

1. `generate(...)` 是主入口。
2. `generatePage(...)` 不再作为新业务主路径。
3. prompt 文案只描述单张封面，不再出现 `第 1/3 页`、`资料册三页`、`上一页底部`、`resume/gallery` 连续性。
4. prompt 必须说明封面底部和边缘应自然过渡到固定主题底色，便于前端下方内容延展。
5. negative prompt 继续禁止文字、二维码、Logo、水印、假 UI、卡片边框和最终资料内容。

### 2.5 任务状态与兼容边界

1. `pending` 和 `running` 只表示任务仍在生成中，不能让前端误判为成功作品。
2. `failed` 只表示封面生成链路最终失败，前端可以展示失败态和重试入口，但不能继续把该任务当作可分享成功资产。
3. 允许质检重试时，重试对象仍然只能是单个 cover 目标，不得扩展出页级生成。
4. 任务/作品 DTO 里的 `pages` 只能作为 legacy compat 字段存在，主路径不得用 `pages.length` 作为成功判断。
5. `actor_ai_profile_card_page` 只服务历史清理和兼容兜底，不再参与新任务主路径。

## 3. 前端设计

### 3.1 类型

`AiProfileCardTask` / `AiProfileCardArtifact` 增加：

```ts
interface AiProfileCardTheme {
  backgroundColor: string
  surfaceColor: string
  surfaceStrongColor: string
  accentColor: string
  textColor: string
  mutedTextColor: string
  borderColor: string
}
```

`pages` 在新主路径中不再使用。历史字段不作为渲染条件。

### 3.2 详情页结构

新的 `pkg-card/ai-profile-card-detail/index`：

```text
ai-share-detail-page
  cover-poster
    generated background image
    deterministic cover overlay
  content-flow
    stats
    basic facts
    appearance/languages
    skills
    intro
    work timeline
    photo gallery
    video resume
```

`content-flow` 使用 `--ai-flow-bg` 作为整页底色。每个 section 可以使用轻量 surface，但页面底色必须保持一致。
封面和内容流之间应通过同一组 theme token 形成视觉过渡，避免被理解为两套独立页面。

### 3.3 封面

封面继续复用现有 cover slot preset：

```text
identity
facts
skills
works
photos
intro
video
```

封面只是第一屏 9:16 poster，不再是 album 的第 1 页。

### 3.4 内容流

内容流承接原 `resume / gallery` 的信息密度，但不再绝对定位到 9:16 画布：

1. 基础资料和形象条件使用普通 grid。
2. 技能和语言使用可换行 chip。
3. 拍摄经历使用纵向列表。
4. 照片使用可扩展横向/网格布局。
5. 视频简历使用普通可点击 media block。

### 3.5 分享与状态展示

1. 详情页分享入口和联系入口都应基于同一个 `generatedImageUrl + theme` 组合，不再从 `pages` 回推封面。
2. 失败态、加载态和成功态应在 UI 层显式区分，不应把历史数据兼容当作成功。
3. 底部操作栏需要预留内容滚动的安全距离，避免遮挡最后一个内容区块。

## 4. 兼容边界

1. 新任务不创建三页。
2. 新前端不按 `pages` 渲染三张 AI 背景图。
3. 删除作品时可以继续清理历史 page 记录，避免遗留脏数据。
4. 如果历史 artifact 带有 `pages`，新详情页只取 `generatedImageUrl` 或 cover page 作为单封面兜底。
5. 历史数据兜底不应反向影响新任务合同，不得把旧三页 schema 当成新业务 schema。

## 5. 测试设计

### 后端

1. prompt agent 单封面合同测试：
   - prompt 不包含三页/上一页/continuity 语义。
   - prompt 包含固定主题底色延展说明。
2. service 生成流程测试：
   - 只调用一次 `promptAgent.generate(...)`。
   - 不调用 `generatePage(...)`。
   - 不调用 continuity crop。
   - response theme 存在。

### 前端

1. 类型检查通过。
2. 详情页不再引用 `albumSlotToPercentStyle`、`resume/gallery` 渲染分支和 continuity band。
3. 分享图仍使用单张 `generatedImageUrl`。
4. 页面底色来自 API theme 或本地 scene fallback。
5. 失败态、加载态和历史兜底态都能正确区分，不会把旧数据误标成新成功作品。

## 6. Rollout

本轮直接切换新任务主路径。旧三页 Spec 和 runtime 逻辑不再维护。若线上已经存在历史三页数据，按单封面兜底展示，不继续修三页接缝。
