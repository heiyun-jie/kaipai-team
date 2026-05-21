# AI 分享图单封面主题内容流 Tasks

## Phase 1: Spec

- [x] 新增 `00-171`，定义单封面 + 主题内容流。
- [x] 标记 `00-168 / 00-169 / 00-170` 被本 spec 取代。
- [x] 补充角色矩阵，明确演员本人、外部访客、未登录访客、剧组端和研发运营边界。
- [x] 明确产品口径为“AI 分享详情页：单 AI 封面 + 主题内容流”，不是纯单图页。
- [x] 明确 provider 调用口径：新任务只有单个 cover 生成目标，质检重试也只能重试 cover。
- [x] 明确 `pages`、page entity 和 continuity 字段只作为历史兼容残留。

## Phase 2: Backend

- [x] 后端新任务不再创建 `cover / resume / gallery` 页面记录。
- [x] 后端生成流程只围绕单个 cover 目标生成，成功图写入 `generatedImageUrl`。
- [x] 移除新主路径中的 continuity reference / tail crop 逻辑。
- [x] DTO 返回任务级 `theme` payload。
- [x] Prompt Agent 收敛为单封面背景 prompt。
- [x] 更新后端单测。

## Phase 3: Frontend

- [x] AI 详情页改为单封面 poster。
- [x] 封面以下改为统一底色内容流。
- [x] 不再渲染 `resume / gallery` AI 背景页。
- [x] 前端类型接入 `theme` payload。
- [x] 分享图仍使用单张 `generatedImageUrl`。

## Phase 4: Verification

- [x] 后端定向单测通过。
- [x] 前端类型检查通过。
- [x] 构建或可用等价检查通过。

## Phase 5: Deferred Hardening

- [x] 将 API 文档、OpenAPI 或前端详情页注释中的 `pages` 标记为 legacy compat。
- [x] 评估是否在兼容窗口结束后删除未进入新主路径的 page background renderer 和 continuity 相关模型。
- [x] 明确历史 page-only 数据策略：优先由后端/数据迁移补齐 task-level `generatedImageUrl`，前端详情页只保留临时 cover fallback。
- [x] 删除无生产调用的 page background renderer、continuity bottom band crop helper 和相关测试；验证命令：`mvn -q "-DskipTests" compile`、`mvn -q "-Dtest=AiProfileCardServiceImplTest,AiProfileCardPromptAgentTest,AdminAiImageProviderControllerTest" test`。
- [x] 补充历史 page-only 数据 backfill 审查说明，明确探测 SQL、执行门槛和完成判据。
- [x] 新增只读盘点脚本 `read-ai-profile-card-page-only-inventory.py`、证据目录模板和执行 runbook；该入口只输出候选 count 与抽样，不执行 backfill，且本项不是线上/准线上盘点完成证据。
- [x] 完成目标环境 page-only 数据盘点，证据目录：`.sce/runbooks/backend-admin-release/records/diagnostics/20260520-230700-ai-profile-card-page-only-inventory/`；`pageOnlyCoverCount=0`、`sampleRows=0`，无需 forward migration 或 re-host，前端 legacy `pages` cover fallback 已删除并验证。

## Phase 6: Production Hardening

- [x] 生产环境 `TencentOcrAiProfileCardImageQualityInspector` 在腾讯 OCR 未开通或服务不可用时改为 non-retryable unavailable，不再把“质检服务不可用”放行成成功结果；本轮已收紧 Tencent 混元 prompt，避免把档案字段和可读布局信号继续喂给生成模型，并通过后端单测与 `mvn -q -DskipTests compile` 验证。
- [x] `pkg-card/ai-profile-card-detail/index` 增加封面下半屏主题底色遮罩，避免 provider 在底部写入可读文字、水印或 `AI` 声明时继续暴露在详情页可见区域；已通过 H5 与 `build:mp-weixin` 复核。
- [x] 重新跑通生产生成流程，最新任务 `aipf_d2ced0aa1ca44b0ba0bcb418432f4cf1` 成功，`generatedImageUrl` 正常落地，详情页 DOM 未包含 `AI GENERATED SHARE`、`图示使用Ai生成` 或旧三页标记。

## Acceptance

- [x] 新任务只生成一张封面图。
- [x] 页面只展示一张 AI 背景图。
- [x] 后续内容使用同一主题底色延展。
- [x] 旧三页生成逻辑不再作为新主路径保留。
