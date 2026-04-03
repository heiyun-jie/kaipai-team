# 后台邀请模块保留 / 改造 / 下线矩阵

> 归属 Spec：`05-12 share-invite-code-consolidation`
> 更新时间：2026-04-03
> 适用范围：`kaipai-admin/src/views/referral/*`、`kaipaile-server/src/main/java/com/kaipai/module/controller/admin/referral/*`

## 1. 目的

把后台邀请模块从“前台分享链路的一部分”重新校准为“后台治理域”。

本矩阵用于回答两个问题：

- 哪些模块必须保留，不能因为前台去掉邀请码展示就误删。
- 哪些模块只需要调口径，不需要整体推倒重做。

## 2. 总结结论

### 2.1 必须保留

- `邀请记录`
- `异常邀请`
- `邀请资格`
- `邀请规则`
- 后端 `admin/referral/*` 全套治理接口

### 2.2 当前不建议整体重做

- `RecordsView.vue`
- `RiskView.vue`

原因：

- 这两页直接承接后台审核、追踪、定位和审计职责。
- 前台分享链路是否展示邀请码，不改变后台按邀请码定位记录的治理需求。

### 2.3 需要按业务决策决定是否收缩

- `EligibilityView.vue`
- `PoliciesView.vue`

原因：

- 这两页承接的是“邀请资格发放”和“邀请规则配置”。
- 如果产品继续保留邀请驱动成长、资格发放、风险频控，这两页应保留并只调文案。
- 如果后续决定废弃邀请资格与自动发放机制，才应单独立新 spec 做下线或并表重构。

## 3. 模块矩阵

| 模块 | 页面 / 接口 | 当前职责 | 处理结论 | 原因 |
|------|-------------|----------|----------|------|
| 邀请记录 | `kaipai-admin/src/views/referral/RecordsView.vue` | 查询邀请记录、邀请码、邀请人 / 被邀请人、状态与详情 | 保留 | 这是后台事实链总表，前台收口邀请码不影响后台核查 |
| 异常邀请 | `kaipai-admin/src/views/referral/RiskView.vue` | 风险邀请筛选、详情、通过 / 作废 / 复核完成 | 保留 | 这是后台审核闭环，不属于前台分享重构范围 |
| 邀请资格 | `kaipai-admin/src/views/referral/EligibilityView.vue` | 手工发放、延长、撤销邀请资格 | 条件保留，优先调口径 | 是否存在取决于产品是否继续保留资格机制 |
| 邀请规则 | `kaipai-admin/src/views/referral/PoliciesView.vue` | 邀请门槛、频控、自动发放规则治理 | 条件保留，优先调口径 | 是否存在取决于产品是否继续保留规则驱动 |
| 后端治理接口 | `com.kaipai.module.controller.admin.referral.AdminReferralController` | 后台 referral 全套治理 API | 保留 | 管理端页面依赖这些接口，不应因前台收口被误删 |
| 前台邀请码展示 | `kaipai-frontend/src/pkg-card/actor-card/index.vue`、`kaipai-frontend/src/pkg-card/membership/index.vue` | 历史上重复暴露 raw invite code | 已收口 | 已按 05-12 收口到前台 `invite/index` |
| 前台邀请码操作页 | `kaipai-frontend/src/pkg-card/invite/index.vue` | 邀请码 / 邀请链接 / 海报 / 记录操作 | 保留 | 前台唯一邀请码操作页 |

## 4. 具体边界

### 4.1 后台必须继续保留的邀请码字段

以下字段属于治理字段，不应因前台清理而删除：

- `inviteCode`
- `inviteCodeId`
- `grantCode`
- `inviterUserId`
- `inviteeUserId`
- `riskReason`
- `riskFlag`
- `status`

对应文件：

- `kaipai-admin/src/types/referral.ts`
- `kaipaile-server/src/main/java/com/kaipai/module/model/referral/dto/*`

### 4.2 后台不应该再承担的职责

后台不应该再反向要求前台分享页承担以下职责：

- 在 `actor-card` 或 `membership` 内展示 raw invite code
- 在非邀请专页复制邀请码
- 把后台治理字段解释成“前台必须可见”

### 4.3 后台页面建议调整的口径

建议把“邀请裂变”统一弱化为“邀请治理”或“邀请管理”，避免继续误导为前台分享入口。

建议优先调整位置：

- `kaipai-admin/src/constants/menus.ts`
- `kaipai-admin/src/constants/permission-registry.ts`
- `kaipai-admin/src/constants/status.ts`
- `kaipai-admin/src/views/referral/*.vue` 页头描述文案

## 5. 推荐推进顺序

### 5.1 第一阶段：只调口径，不改事实模型

- 保留 `Records / Risk / Eligibility / Policies`
- 菜单与页头从“邀请裂变”改为“邀请治理”
- 保留所有治理字段和接口

### 5.2 第二阶段：评估资格机制是否继续存在

若产品仍保留：

- 邀请升级
- 邀请资格发放
- 自动资格规则
- 风险频控

则：

- `Eligibility / Policies` 继续保留，只做体验优化

若产品不再保留：

- 另开新 spec，单独推进 `Eligibility / Policies` 下线或并入其他治理页
- 不允许直接在当前分支无 spec 删除

## 6. 本轮执行结论

本轮评估后，后台邀请模块不需要“整体重改”。

明确结论如下：

- `邀请记录`：保留
- `异常邀请`：保留
- `邀请资格`：条件保留，先不删
- `邀请规则`：条件保留，先不删
- 前台邀请码重复展示：已收口，不再作为后台重构理由

后续若要继续推进，应基于这份矩阵单独开“后台邀请治理口径优化”或“资格机制下线” spec，而不是直接对 `referral` 域做无边界改造。
