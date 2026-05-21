# 00-146 Execution

## 1. 启动记录

- 触发原因：
  - 用户否定此前“兼容保留也算完成”的评分口径。
  - 用户明确要求“备份之后，强行物理删除”。
- 本轮执行标准：
  - 不再把 legacy summary / repair / fallback 文案视为可接受完成态。

## 2. 已做备份

- 备份目录：
  - `D:\XM\kaipai-team\.sce\backups\20260425-strict-legacy-retirement-batch1`
- 已备份对象：
  - 后端 `AdminContentController / UserShareCardService / UserShareCardServiceImpl / legacy DTO`
  - 管理端 `content.ts / types/content.ts / ShareCardsView.vue / ActionsView.vue / permission-registry.ts / RolesView.vue / admin-information-architecture.ts`

## 3. 首批删除范围

- 删除后端分享卡 legacy summary / repair 正式接口。
- 删除管理端对应类型、API、按钮、辅助治理区与权限登记。
- 删除两份 legacy DTO 源文件。

## 4. 当前边界

- 默认普通卡补偿链仍在主链运行时被调用，当前不能暴力删除。
- `scene_key / actor_card_config_id` 等数据库字段仍有真实代码读写，当前不能直接 drop。
- 因此本 spec 先完成“已确认安全对象”的强制退休，再继续推进数据库严格化。

## 5. 本轮验证

- 后端：
  - `D:\XM\kaipai-team\kaipaile-server`
  - `mvn -q -DskipTests compile`：通过
- 管理端：
  - `D:\XM\kaipai-team\kaipai-admin`
  - `npm run type-check`：通过
  - `npm run build`：通过
- 删除核验：
  - `legacy-summary / repair-legacy` 已不再出现在本轮后端与管理端主代码引用中
  - `AdminShareCardLegacySummaryDTO / AdminShareCardLegacyRepairRespDTO` 已物理删除

## 6. 严格复评分

### 6.1 后端 API / 后台管理首批强删完成度

- 复评分：`95 / 100`
- 加分依据：
  - 已完成文件备份后物理删除 `share-cards/legacy-summary` 与 `repair-legacy`
  - 后端 DTO / service / controller 与管理端 API / 类型 / 权限 / 页面入口已同步收口
  - 管理端明显 `兼容 / fallback / 迁移阶段` 外露文案已做首批去过渡化
- 剩余扣分：
  - 默认普通卡补偿链仍在主链运行时对外可见
  - 角色治理矩阵底层仍然以旧 rolloutStage 值承载部分历史授权识别

### 6.2 数据库严格重构完成度

- 当前评分：`72 / 100`
- 结论：
  - 不能宣称达到 `95`
  - 原因不是数据未回填，而是旧字段与旧定位键仍在真实运行时代码中被读写
- 当前阻塞：
  - `share_card_contact_request.actor_card_config_id`
  - `share_card_contact_request.scene_key`
  - `share_card_view_history.scene_key`
  - `actor_share_preference.scene_key`
  - 默认普通卡与分享卡实例绑定链仍受 `scene_key / latest_config` 主导

## 7. 当前结论

- 本轮已经按用户要求完成：
  - 先备份
  - 再物理删除首批确认安全的 legacy 正式暴露面
  - 再重新编译 / 构建 / 复审
- 但数据库严格重构这一条线还没有到 `95`，不能虚报通过。
- 下一批若继续推进，必须进入：
  - 代码读写切换
  - 备份 migration
  - 字段 drop
  - dev 库复核
