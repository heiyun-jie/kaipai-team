# 执行记录

## 2026-09-01 基线调查

- 页面：`pkg-actor-card/generate/index?cardId=1`
- 页面状态：`生成失败 / 数据约束校验失败`
- 前端请求：`POST /api/actor-card/draft/1/generate`
- 测试后端日志：
  - `2026-09-01T05:52:27.333Z`：`Field 'source_image_url' doesn't have a default value`
  - `2026-09-01T08:00:41.062Z`：`Field 'source_image_url' doesn't have a default value`
- Candidate：`20260901-150906-v3-draft`
- Candidate backend JAR SHA256：`6e24be2b2b63afa8612c801a985ed7444552dd9252ff69c6febcb53abd001e3d`
- Candidate JAR 内含：`BOOT-INF/classes/db/migration/V20260901_001__actor_card_internal_auto_expand.sql`
- 当前裁决：小程序目录准入曾返回 ready，但全栈测试运行态未证明一致；当前人工验收失效，状态为 `TEST_STACK_NOT_READY`。
- 生产状态：`NOT_AUTHORIZED`，调查阶段未修改测试或生产运行环境。

## 准入门禁修复

- `verify-test-miniapp-acceptance.py` 新增 `TEST_STACK_NOT_READY / exit 5`。
- 全栈证明绑定 Candidate manifest、artifact evidence、候选/运行 JAR SHA256、测试库备份、目标数据库、迁移、DDL、API 和生产未变状态。
- 单测从 `7/7` 扩展为 `10/10`；新增 TAT 测试发布执行器边界测试 `3/3`。
- 修复前真实门禁：小程序三侧一致，但缺全栈证明，返回 `TEST_STACK_NOT_READY / exit 5`。

## 测试环境修复

- TAT invocation：`inv-h84h8sgdkw`，exit `0`。
- 测试库备份 SHA256：`b438ca8fce9a572a7c42847bc2ff5ab4760f7ce27c6a2dc4cfeb5f965d729146`。
- 迁移 SHA256：`22613b27e4a4a8d1484637701a06466a6003ac7001a48326d45106ffd1bb9bec`。
- 运行 JAR 从旧 `448fd95cdb4f0ce261d8633c5e22c4b561ca56e3f3567de11343e1e5fd587829` 切换为 Candidate `6e24be2b2b63afa8612c801a985ed7444552dd9252ff69c6febcb53abd001e3d`。
- 只重建 `kaipai-backend-test`；`kaipai_test` 的 `source_image_url` 已为 nullable，三个稳定来源列、四列唯一索引和演员卡来源指纹均存在。
- 测试 API HTTP `200`；生产容器 `ID / startedAt / restartCount / status` 前后完全一致。

## MCP 回归

- 固定工程：`D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin`。
- 原页面：`pkg-actor-card/generate/index?cardId=1`，直接点击既有“重新生成”，没有打开、重启或控制可见窗口。
- 结果：结构化长页存在，失败区不存在，“发布演员卡”按钮存在，控制台错误为空。
- 最新任务：`actor_card_generate / success / source_image_url_is_null=1 / failure_reason_is_null=1`。
- 新运行日志没有 `source_image_url` 数据约束异常。
- 最终全栈准入：`READY_FOR_MANUAL_ACCEPTANCE / exit 0`。
- 正式发布仍为 `NOT_AUTHORIZED`，未执行 `00-237`。
