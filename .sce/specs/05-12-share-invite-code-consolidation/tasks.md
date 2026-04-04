> 2026-04-04 说明：以下任务完成情况对应的是旧版 invite 分享页口径；当前阶段 invite 页面边界以 `00-52 current-phase-invite-record-page-boundary-alignment` 为准。

- [x] T1 盘点前台与后台所有邀请码展示面，确认保留域（`invite/index`、后台 referral）与清理域（`actor-card`、`membership`）
  - **Validates: Requirements 3.1, 3.2, 3.5**
- [x] T2 重构 `src/components/KpInviteSummaryCard.vue` 或拆分组件，支持“分享态无邀请码展示”与“邀请治理态展示邀请码”两种口径
  - **Validates: Requirements 3.3**
- [x] T3 改造 `src/pkg-card/actor-card/index.vue`，移除 `copyInviteCode()` 与 raw invite code 展示，仅保留去邀请页 / 统一分享入口
  - **Validates: Requirements 3.1, 3.2, 3.4**
- [x] T4 改造 `src/pkg-card/membership/index.vue`，移除 raw invite code 展示，保留邀请统计与两类分享入口
  - **Validates: Requirements 3.1, 3.2, 3.3**
- [x] T5 复核 `src/pkg-card/invite/index.vue`，确保它仍是前台唯一的邀请码 / 链接 / 海报 / 记录操作页
  - **Validates: Requirements 3.2, 3.4**
- [x] T6 复核 `src/utils/invite.ts`、`src/utils/share-artifact.ts`，继续收口邀请路径与 `inviteCard` 产物路径生成，不允许页面重新散落拼接
  - **Validates: Requirements 3.4**
- [x] T7 复核 `kaipai-admin/src/views/referral/*.vue` 与 `src/types/referral.ts`，确保后台邀请码治理字段保留且未被前台清理误伤
  - **Validates: Requirements 3.5**
- [x] T8 回填 `.sce/specs/README.md`、`.sce/specs/spec-code-mapping.md` 与本 Spec 的执行记录，完成类型检查和页面证据留存
  - **Validates: Requirements 3.6**
- [x] T9 按后台治理边界矩阵完成 `kaipai-admin` referral 域第一阶段口径收口，把模块入口与页头说明从“邀请裂变”统一为“邀请治理”，且不改数据模型与治理流程
  - **Validates: Requirements 3.5, 3.6**

## 执行说明

- 2026-04-03 已完成源码复核：
  - 前台清理域：`kaipai-frontend/src/pkg-card/actor-card/index.vue`、`kaipai-frontend/src/pkg-card/membership/index.vue`
  - 前台保留域：`kaipai-frontend/src/pkg-card/invite/index.vue`
  - 共享收口：`kaipai-frontend/src/components/KpInviteSummaryCard.vue`、`kaipai-frontend/src/utils/invite.ts`、`kaipai-frontend/src/utils/share-artifact.ts`
  - 后台治理域：`kaipai-admin/src/views/referral/RiskView.vue`、`kaipai-admin/src/views/referral/RecordsView.vue`、`kaipai-admin/src/views/referral/EligibilityView.vue`、`kaipai-admin/src/views/referral/PoliciesView.vue`、`kaipai-admin/src/types/referral.ts`
- 2026-04-03 已补执行记录：`execution.md`
- 2026-04-03 已完成后台 referral 域第一阶段口径收口：
  - `kaipai-admin/src/constants/menus.ts`
  - `kaipai-admin/src/constants/permission-registry.ts`
  - `kaipai-admin/src/constants/status.ts`
  - `kaipai-admin/src/views/referral/RecordsView.vue`
  - `kaipai-admin/src/views/referral/RiskView.vue`
  - `kaipai-admin/src/views/referral/EligibilityView.vue`
  - `kaipai-admin/src/views/referral/PoliciesView.vue`
- 2026-04-03 已复核编译产物：
  - `kaipai-frontend/dist/build/mp-weixin/components/KpInviteSummaryCard.*`
  - `kaipai-frontend/dist/build/mp-weixin/pkg-card/actor-card/index.*`
  - `kaipai-frontend/dist/build/mp-weixin/pkg-card/membership/index.*`
