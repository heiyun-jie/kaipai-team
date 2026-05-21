# 00-146 Design

## 策略

### 1. 文件级备份

- 将待删或待重写文件复制到 `.sce/backups/20260425-strict-legacy-retirement-batch1/`。
- 备份范围覆盖：
  - 后端 controller / service / impl / DTO
  - 管理端 API / types / 视图 / 权限登记 / IA 文案

### 2. 首批强删对象

- 后端：
  - `GET /admin/content/share-cards/legacy-summary`
  - `POST /admin/content/share-cards/repair-legacy`
  - `UserShareCardService` 中对应 service 方法
  - `UserShareCardServiceImpl` 中对应实现与私有 helper
  - `AdminShareCardLegacySummaryDTO`
  - `AdminShareCardLegacyRepairRespDTO`
- 管理端：
  - `content.ts` 中对应 API
  - `content.ts` / `types/content.ts` 中对应类型
  - `ShareCardsView.vue` 中 legacy 修复区
  - `ActionsView.vue` 中 legacy 修复推荐卡
  - `permission-registry.ts` 中 repair 权限登记

### 3. 文案去过渡化

- `RolesView.vue` 将“迁移阶段 / 兼容迁移中 / fallback”改为中性治理状态表达。
- `admin-information-architecture.ts` 删除“迁移期 / 兼容治理入口”等表述。

### 4. 数据库策略

- 本批只做严格审查结论回填，不直接 drop 字段。
- 真正 drop 字段前必须先补：
  - 代码读写切换
  - 备份 migration
  - dev 库验证
