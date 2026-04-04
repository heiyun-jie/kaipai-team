# 05-12 分享链路邀请码收口 - 执行记录

> 执行日期：2026-04-03
> 范围：前台分享链路邀请码收口、共享路径复核、后台 referral 治理边界确认

> 2026-04-04 说明：本文结论对应旧版 invite 分享页口径；当前阶段 invite 页面边界已改为“记录页 + 登录承接邀请码 + 分享入口留在 actor-card/membership”，若与本文冲突，以 `00-52 current-phase-invite-record-page-boundary-alignment` 为准。

## 1. 结论

- `pkg-card/invite/index` 仍是前台唯一允许展示 raw invite code、复制邀请码、复制邀请链接、保存邀请海报、查看邀请记录的页面。
- `pkg-card/actor-card/index` 与 `pkg-card/membership/index` 已移除 raw invite code 展示和“复制邀请码”捷径，只保留跳转邀请页的统一入口。
- `KpInviteSummaryCard` 已支持显式 `showInviteCode` 开关，默认值为 `false`，前台分享态默认不展示邀请码。
- 邀请路径与 `inviteCard` 产物路径仍由 `src/utils/invite.ts` 与 `src/utils/share-artifact.ts` 收口。
- 后台 `referral` 页面与类型定义仍保留邀请码、资格码、治理详情字段，未被前台清理误伤。

## 2. 源码验证

### 2.1 前台清理域

- `kaipai-frontend/src/pkg-card/actor-card/index.vue`
  - 已移除 `copyInviteCode()`。
  - `KpInviteSummaryCard` 仅保留统计与跳转动作，不再传入 `inviteCode`、`secondaryText`、`@secondary`。
  - `handleInviteAction()` 统一跳转 `/pkg-card/invite/index`，附带 `artifact`、`actorId`、`scene`、`tone`。
- `kaipai-frontend/src/pkg-card/membership/index.vue`
  - 不再向 `KpInviteSummaryCard` 传入 `inviteCode`。
  - 底部动作统一跳转 `/pkg-card/invite/index?artifact=inviteCard|poster`。

### 2.2 前台保留域

- `kaipai-frontend/src/pkg-card/invite/index.vue`
  - 显式传入 `show-invite-code`。
  - 保留 `copyInviteCode()`、`copyInviteLink()`、`savePoster()`、`open-type="share"`、邀请记录列表。
  - 分享路径通过 `patchPathQuery()` 基于邀请落点补齐 `artifact`、`scene`、`themeId`、`tone`、`shared`。

### 2.3 共享组件与工具

- `kaipai-frontend/src/components/KpInviteSummaryCard.vue`
  - 新增 `showInviteCode?: boolean`。
  - 默认 `showInviteCode: false`，安全默认值改为分享态。
- `kaipai-frontend/src/utils/invite.ts`
  - 继续负责 `normalizeInviteCode()`、`buildInvitePath()`、`setInviteShareState()`、邀请码恢复逻辑。
- `kaipai-frontend/src/utils/share-artifact.ts`
  - `resolveShareArtifactPath()` 继续统一处理 `inviteCard` 路径恢复。
  - `patchPathQuery()` 继续作为 query patch 单一入口。

## 3. 后台治理边界验证

- `kaipai-admin/src/views/referral/RiskView.vue`
  - 仍保留邀请码筛选、表格列、详情块、同小时命中摘要中的邀请码字段。
- `kaipai-admin/src/views/referral/RecordsView.vue`
  - 仍保留邀请码筛选、列表列、详情抽屉中的邀请码 / 邀请码 ID 字段。
- `kaipai-admin/src/views/referral/EligibilityView.vue`
  - 仍保留资格码筛选、详情和手工发放治理动作。
- `kaipai-admin/src/views/referral/PoliciesView.vue`
  - 仍保留邀请资格规则配置与自动发放策略治理语义。
- `kaipai-admin/src/types/referral.ts`
  - `inviteCode`、`inviteCodeId`、`grantCode` 等字段仍完整存在。

## 4. 后台口径治理落地

- 已按 `admin-referral-retain-refactor-retire-matrix.md` 完成后台 referral 第一阶段口径收口。
- 本轮只调整模块命名和页头说明，不改 referral 数据模型、权限码、接口路径、审核动作和字段事实链。

### 4.1 模块入口与权限口径

- `kaipai-admin/src/constants/menus.ts`
  - 顶级菜单 `referral.label` 已从 `邀请裂变` 改为 `邀请治理`。
- `kaipai-admin/src/constants/permission-registry.ts`
  - `MODULE_LABELS.referral` 已从 `邀请裂变` 改为 `邀请治理`，权限树模块口径与菜单保持一致。
- `kaipai-admin/src/constants/status.ts`
  - `dashboardBizLineMap.referral` 已从 `邀请裂变` 改为 `邀请治理`，工作台业务线展示同步收口。

### 4.2 referral 页面页头口径

- `kaipai-admin/src/views/referral/RecordsView.vue`
  - 页头说明从“前台展示口径”改为“后台治理事实链”。
- `kaipai-admin/src/views/referral/RiskView.vue`
  - 页头说明改为突出“复核、作废、风险处置闭环”。
- `kaipai-admin/src/views/referral/EligibilityView.vue`
  - 页头说明改为突出“资格来源、发放动作与治理事实链”。
- `kaipai-admin/src/views/referral/PoliciesView.vue`
  - 页头说明改为突出“后台治理规则口径收口”。

### 4.3 本轮未改项

- `邀请记录 / 异常邀请 / 邀请资格 / 邀请规则` 子页名称保持不变。
- `page.referral.*`、`action.referral.*` 权限码保持不变。
- `AdminReferralController` 与后台 referral API 保持不变。
- 后台仍保留 `inviteCode`、`inviteCodeId`、`grantCode`、`riskReason` 等治理字段。

## 5. 编译与产物证据

- 已复核生成产物：
  - `kaipai-frontend/dist/build/mp-weixin/components/KpInviteSummaryCard.js`
  - `kaipai-frontend/dist/build/mp-weixin/components/KpInviteSummaryCard.wxml`
  - `kaipai-frontend/dist/build/mp-weixin/pkg-card/actor-card/index.js`
  - `kaipai-frontend/dist/build/mp-weixin/pkg-card/membership/index.wxml`
  - `kaipai-frontend/dist/build/mp-weixin/pkg-card/invite/index.wxml`
  - `kaipai-frontend/dist/dev/mp-weixin/components/KpInviteSummaryCard.js`
  - `kaipai-frontend/dist/dev/mp-weixin/components/KpInviteSummaryCard.wxml`
- 复核结论：
  - 编译后组件存在 `showInviteCode`，默认值为 `false`。
  - 编译后 `membership` 页面不再直接包含 raw invite code 相关文案和复制动作。
  - 编译后 `actor-card` 页面跳转邀请页时保留 `artifact`、`actorId`、`scene`、`tone`。

## 6. 校验命令

- 已执行：`npm run type-check`
- 已执行：`npm run build:mp-weixin`
- 已执行：`cd kaipai-admin && npm run build`
