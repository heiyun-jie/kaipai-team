# 演员卡步骤页内部 AI 自动扩图边界收口 - 技术设计

_Requirements: 3.1-3.4, 4, 5_

## 1. 页面边界

`pkg-actor-card/step-visual/index` 保留一个“首图”区段及三个来源：模板图库、素材库、手机上传。移除步骤页中的扩图区段和所有扩图可见状态；创建中心步骤提示和首页创建横幅也不再提及扩图。选择入口、上传、绑定、下一步导航和原有底部避让不改变。

## 2. 状态与保存合同

- 删除 `expandStatus`、`expandFailureReason`、任务 id、轮询定时器和 `startExpand/pollExpand`，并移除步骤页对 `submitExpandImage/getExpandImageStatus` 的 import。
- `expandedImageUrl` 作为隐藏的历史兼容值保留在步骤保存请求中：页面初次读取时承接草稿值，但不渲染；模板或素材来源变化时置为空字符串，避免旧扩图结果覆盖新首图。
- 步骤页不再持有 `sourceAssetId` 扩图状态，也不直接调用 `submitExpandImage/getExpandImageStatus`。
- `actor-card.ts` 中的扩图 API 与 DTO 保留兼容；自动触发由后端在步骤 1 保存或 `source_image` 绑定事务完成后执行。

## 3. 源码实现点

1. 删除 template 中 `step-visual__expand-section` 整个区段及相关结果/错误文案。
2. 删除脚本 setup 中扩图 import、轮询资源和方法；保留来源变化时清理 `expandedImageUrl` 的两处逻辑，以及 mounted 时对历史字段的读取。
3. 将素材绑定来源分支改为显式 `asset` / `legacy` 赋值，保持行为不变并满足 00-242 的来源互斥门禁。
4. 删除只服务扩图区段的 SCSS 选择器，避免产物继续包含可见扩图样式。

## 4. 后端自动编排

1. `ActorCardController` 在步骤 1 保存成功及 `source_image` 绑定替换成功后调用内部自动编排入口。该入口捕获提交阶段异常并写日志，不能改变原保存接口的成功响应。
2. `ActorCardMainVisualResolver` 把当前首图解析为稳定来源：私有素材使用 `assetId`，模板/历史来源使用规范化 URL，并统一生成 SHA-256 来源指纹。
3. `ActorCardExpandImageService` 以 `actorCardId + generationMode + sourceFingerprint` 幂等复用任务；私有素材只写 `source_asset_id`，异步执行时即时签发 URL。
4. Provider 结果先写入受管存储，再由事务服务锁定演员卡、重新解析当前首图并比对指纹；只有仍匹配时才回写 `expanded_image_url` 和 `expanded_source_fingerprint`。
5. 步骤保存和素材绑定检测到来源变化时同时清空扩图 URL 与指纹。生成、预览和公开读取通过同一解析器拒绝不匹配的新扩图结果；无指纹历史数据继续兼容。
6. Provider 失败写入任务 `failed/failure_reason` 并记录日志，不回传到演员的步骤保存/绑定响应。

## 5. 数据库合同

新增幂等迁移 `V20260901_001__actor_card_internal_auto_expand.sql`：

- `actor_ai_profile_card_task.actor_card_id BIGINT NULL`；
- `actor_ai_profile_card_task.source_asset_id BIGINT NULL`；
- `actor_ai_profile_card_task.source_fingerprint VARCHAR(64) NULL`；
- `actor_ai_profile_card_task.source_image_url` 改为可空；
- 唯一索引覆盖 `actor_card_id / generation_mode / source_fingerprint / deleted`；
- `actor_card.expanded_source_fingerprint VARCHAR(64) NULL`。

迁移不回填或改写历史业务数据；历史任务的新字段保持 `NULL`，历史演员卡扩图结果按无指纹兼容语义读取。

## 6. 验证与产物

新增 `scripts/verify-00245-actor-card-internal-expand-visibility.mjs`，检查：

- 源码没有扩图可见文案和直接提交/轮询调用；首图来源入口仍存在；历史 `expandedImageUrl` 只保留保存/清理语义。
- build/dev 步骤页 WXML/JS/WXSS 与源码边界一致，三件套字节和 scoped `data-v` 一致。
- 后端 controller/service 和 API 类型仍保留扩图合同。

后端测试覆盖私有素材稳定身份、相同来源任务复用、失败单次重试、结果受管存储、来源变化拒绝回写、步骤/绑定变更清理，以及 MySQL 8 幂等迁移合同。

构建后生成全新 Candidate，不覆盖旧候选。冻结 `mini-program-test` 完整物化到 `dist/build/mp-weixin` 和固定 `dist/dev/mp-weixin`；项目级 compile cache 清理和内部刷新不结束、不置顶、不抢焦点微信开发者工具。最终以 `verify-test-miniapp-acceptance.py` 返回 `READY_FOR_MANUAL_ACCEPTANCE / exit 0` 为准。

## 7. 发布兼容与回滚

旧前端仍可使用原步骤保存、素材绑定和手动扩图接口；新增字段全部可空。部署顺序为候选迁移先于新后端，新小程序不依赖新增响应字段。`.sce/evidence/20260901-actor-card-internal-auto-expand/ROLLBACK.sh` 只对另一个本地服务文件副本验证恢复；实际代码保持修改态，不执行测试或生产回滚。
