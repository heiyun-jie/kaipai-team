# 05-12 分享链路邀请码收口（Share Invite Code Consolidation）

> 状态：历史收口 | 优先级：P0 | 依赖：05-05、05-10、05-11、00-11
> 目标：收口前台分享链路中的邀请码展示口径，明确“前台分享闭环”和“后台治理闭环”的职责边界。

> 2026-04-04 说明：本 Spec 记录的是旧版“invite 页承担邀请码/链接/海报/分享操作”的收口思路；当前阶段 invite 页面边界已改为“记录页 + 登录承接邀请码 + 分享入口留在 actor-card/membership”，若与本文冲突，以 `00-52 current-phase-invite-record-page-boundary-alignment` 为准。

## 1. 概述

当前邀请码能力已经同时存在于：

- 小程序分享页：`pkg-card/actor-card/index`
- 小程序等级中心：`pkg-card/membership/index`
- 小程序邀请页：`pkg-card/invite/index`
- 后台治理页：`kaipai-admin/src/views/referral/*`

其中 `pkg-card/invite/index` 已经具备邀请码、邀请链接、邀请海报、邀请记录的完整前台闭环；后台 `referral` 页面承担的是查询、审核、资格处理等治理职责。  
但 `actor-card/index` 仍保留 raw invite code 与“复制邀请码”动作，导致分享主线与邀请主线混用，页面边界持续发散。

本 Spec 要求把 raw invite code 的前台展示权收口到邀请页，把后台的邀请码保留在治理域，不再倒逼前台分享页继续暴露邀请码。

## 2. 用户故事

### 2.1 演员端

作为演员，我希望在名片分享页只看到“分享名片”“邀请好友”“海报分享”等明确动作，而不是在分享页重复看到 raw invite code 和复制入口。

### 2.2 邀请链路运营

作为已认证演员，我仍然需要一个独立邀请页来查看邀请码、复制邀请链接、保存海报和查看邀请记录。

### 2.3 后台运营

作为后台运营，我需要继续在 referral 治理页中按邀请码查询、定位风险记录和核对资格，不受前台收口影响。

## 3. 功能需求

### 3.1 前台分享页不得重复暴露邀请码

**描述**：

- `pkg-card/actor-card/index` 不再展示 raw invite code，不再提供“复制邀请码”动作。
- `pkg-card/membership/index` 不再展示 raw invite code 作为主视觉信息，不再提供邀请码复制捷径。
- `pages/actor-profile/detail`、`pkg-card/fortune/index` 等非邀请专页不得新增邀请码展示和复制逻辑。

**验收标准**：

- WHEN 用户打开 `pkg-card/actor-card/index` THEN 页面内不出现邀请码文本和“复制邀请码”按钮。
- WHEN 用户打开 `pkg-card/membership/index` THEN 页面内不出现邀请码文本和“复制邀请码”按钮。
- WHEN 后续新增分享页入口 THEN 不得再次在非邀请专页暴露 raw invite code。

### 3.2 `pkg-card/invite/index` 是前台邀请码唯一操作页

**描述**：

- `pkg-card/invite/index` 是前台唯一允许展示 raw invite code、复制邀请码、复制邀请链接、保存邀请海报、查看邀请记录的页面。
- 其他页面如需触发邀请动作，只能跳转到 `pkg-card/invite/index`，并通过 `artifact` / `scene` / `actorId` 等参数恢复目标态。

**验收标准**：

- WHEN 用户在 `actor-card` 或 `membership` 点击邀请相关动作 THEN 页面跳转到 `pkg-card/invite/index`，而不是在当前页完成邀请码复制。
- WHEN 用户需要 raw invite code 或邀请链接 THEN 只能在 `pkg-card/invite/index` 中获得。

### 3.3 邀请概览组件必须支持“治理态”和“分享态”分离

**描述**：

- `KpInviteSummaryCard` 不能继续把“邀请码展示”当作所有场景的默认能力。
- 组件需要支持至少两种口径：
  - 前台分享态：只展示邀请统计 / 状态 / 入口，不展示 raw invite code。
  - 邀请治理态：展示邀请码与邀请相关操作，仅供 `pkg-card/invite/index` 使用。
- 若现有组件无法自然表达两种口径，则应拆分为更清晰的组件或 props 约束。

**验收标准**：

- WHEN `actor-card` / `membership` 复用邀请概览组件 THEN 组件以“无邀请码展示”的分享态渲染。
- WHEN `invite/index` 复用邀请概览组件 THEN 组件可以保留邀请码展示与邀请动作。

### 3.4 邀请分享路径与邀请码恢复必须由共享工具单一收口

**描述**：

- 邀请落点、邀请码恢复、分享产物到邀请页的路径拼装，必须继续统一复用 `utils/invite.ts` 与 `utils/share-artifact.ts`。
- 页面不得自行散落拼接邀请路径、复制邀请码或推断 invite base path。

**验收标准**：

- WHEN 页面需要构造邀请路径 THEN 使用共享工具而不是页面内联新规则。
- WHEN 分享产物切到 `inviteCard` THEN 仍能通过共享路径逻辑恢复到 `pkg-card/invite/index`。

### 3.5 后台邀请码能力保留在治理域

**描述**：

- 后台 `referral` 模块中的邀请码筛选、展示、详情、资格核对字段保留，不属于本轮前台清理对象。
- 后台的邀请码能力是治理和审计能力，不应被解释为“前台必须继续展示邀请码”。

**验收标准**：

- WHEN 运营在后台 `referral` 页面检索记录 THEN 仍可按邀请码查询和查看详情。
- WHEN 前台完成邀请码收口 THEN 后台治理页字段和类型定义不受破坏。

### 3.6 重构需要同步回写 Spec 与映射

**描述**：

- 本轮清理必须回写到独立 Spec、Spec 索引和 Spec ↔ 代码映射。
- 后续实现、验证、页面证据和回归记录都应归入本 Spec，而不是继续散落到 actor-card / invite / membership 多个页面 Spec 中。

**验收标准**：

- WHEN 新建本 Spec THEN `requirements.md`、`design.md`、`tasks.md` 三件套完整存在。
- WHEN Spec 创建完成 THEN `.sce/specs/README.md` 与 `spec-code-mapping.md` 已可定位到本 Spec。

## 4. 非功能需求

- 前台邀请码口径必须保持单一来源，避免“名片页有邀请码、邀请页也有邀请码、等级页也有邀请码”的多口径并存。
- 前台重构不得影响后台邀请码审计效率，不得把后台治理字段误删为“前台已不展示”。
- 前台入口迁移后，分享闭环仍需保持可发现性，不得把邀请动作做成隐藏能力。

## 5. 约束条件

- 遵循“展示状态与资格判断必须单一来源”的长期规则，邀请显示与邀请资格口径不能再次散落到页面层。
- 遵循“优惠券/资格判断以后端为权威源”的同类治理原则，邀请码、邀请资格、邀请记录以后端和后台治理口径为准。
- 如果页面首屏依赖登录态获取邀请信息，必须先建立会话，再请求受保护数据，不能用匿名兜底掩盖时序错误。
