# 名片夹草稿发布准备度与操作入口收口 - 执行记录

## 2026-09-02

- 已完成调查：草稿列表当前只有“继续编辑 / 删除草稿”，列表 DTO 不包含生成或发布准备度；生成页和服务端发布接口均要求先存在生成预览。
- 已确定不使用总完成度推断资格：可选步骤会影响百分比，但不阻断生成；准备度必须由后端读取必填字段、真实作品行数和生成预览字段后明确返回。
- 后端 `ActorCardListItemDTO` 已增量增加 `generateReady / publishReady`；`ActorCardPublishService` 使用有效主视觉、资料快照、真实 `actor_card_work` 行数、生成设置和 `generatedPreviewUrl` 派生状态。列表完成度不再默认把作品计为完成。
- 前端字段保持可选并严格比较 `=== true`。普通草稿显示两列“继续编辑 / 删除草稿”；可生成草稿增加“生成预览”；已生成草稿增加“预览并发布”。列表未导入或调用发布接口，发布确认继续由生成页承载。
- 后端 `ActorCardPublishServiceTest` 共 13 项通过，覆盖可生成、可发布、已发布卡不暴露草稿动作、缺作品、以及未生成草稿仍被发布接口拒绝。
- 前端 `verify:card-list-draft-actions` 25 项、`verify:card-list-layout` 15 项、`verify:v3-card-list` 13 项、`verify:single-runtime-entry` 和 `type-check` 均通过。
- 项目级 MCP 先关闭并退出固定工程，`npm run build:mp-weixin` 成功直接写入唯一 `dist/dev/mp-weixin`，构建基址 `https://test-api.kplyyk.com`。运行产物本地 API 0 个文件、测试 API 3 个文件、正式 API 0 个文件。
- MCP 产物检查确认 `pages/card-list/index` JS/WXML/WXSS 完整且 scoped hash 状态一致；SHA-256 分别为 `A494ABCC7265476CCC96A81B4DD3422E648A2B17160CBE60CCDB1216C6E39B14`、`40D1EEDC9226D22977F7C00D94EF4B3F7E261F2219A450FDF87CCA433E6FE6FE`、`2D573E64E4A7A9C688A8173F253E55BADFF7840C252724324FF23ED9D54A78AA`。
- 当前测试 API 尚未部署新 DTO，MCP 真实运行数据确认两个新增字段缺失时，两张草稿均安全回退两列操作，控制台错误为空；证据为 `.sce/evidence/wechat-devtools/00-254-card-list-draft-old-backend-fallback-20260902.png`。
- MCP 内部视觉 fixture 临时给两张草稿注入 `publishReady / generateReady` 渲染态，仅验证布局，未调用接口或写数据库；“预览并发布 / 生成预览”均在 `344 x 33px` 三列操作栏内完整显示。截图为 `.sce/evidence/wechat-devtools/00-254-card-list-draft-actions-visual-fixture-20260902.png`。截图后已刷新并重新打开草稿 Tab，fixture 已清除。
- `audit:mp-package` 所有包均低于 2 MB；全局外链门禁仍因既有白名单不识别 `test-api.kplyyk.com` 报 4 处失败，本次未扩大范围修改该门禁。
- 事务证据见 `evidence/VERIFICATION.txt`。回滚只在 `ROLLBACK_TEST_COPY` 执行，7 个基线文件 mismatch=`0`，新增脚本已删除；业务实现 8 个文件与 `MODIFIED_FILES` mismatch=`0`。
- 代码与固定小程序运行产物已完成；测试环境完整新行为仍需将新后端与小程序重新冻结为同一 Candidate 后验证。未部署测试后端，未执行生产数据库迁移、生产容器重建、Nginx 切流或正式小程序上传；正式发布状态保持 `NOT_AUTHORIZED`。

## 2026-09-02 全栈 Candidate 恢复

- 已重新冻结 Candidate `20260902-145540-v3-draft`；manifest SHA256 为 `8a1d6807ff985d33a140a887c5239c3829ab4b9527359e22a6a0c91c3f6ff8a1`，backend JAR SHA256 为 `5dd678378ae02c48677f1dc4a73707b03c73b534db749986a63e4b69ce129a98`。
- `mini-program-test` 为 `329 / 2,041,422 / d1528b66647a79dacf19eb1ed0d3f6d165249b51a19e978e0a3c1fbdf6316f1e`，已完整同步到唯一 `dist/dev/mp-weixin`，目录等价为 `true`。
- 测试后端已运行同一 JAR；测试库备份、Schema 合同、API 健康和生产容器不变证明全部通过。
- 内部 MCP 使用真实测试数据验证：第一张草稿显示“继续编辑 / 预览并发布 / 删除草稿”，第二张显示“继续编辑 / 生成预览 / 删除草稿”；控制台 `error/fail` 均为 `0`。
- 截图证据：`.sce/evidence/wechat-devtools/00-254-card-list-live-readiness-20260902.png`，SHA256 `1f5bc39049729879caed78d087a58c008e3da628c8832939f8fe1beec2c7d0cd`。
- 最终准入为 `READY_FOR_MANUAL_ACCEPTANCE / exit 0`。未置顶或抢占微信开发者工具焦点，未使用桌面截图、坐标或键鼠自动化。
