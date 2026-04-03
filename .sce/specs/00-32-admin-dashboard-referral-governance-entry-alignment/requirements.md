# 00-32 后台工作台邀请治理入口对齐（Admin Dashboard Referral Governance Entry Alignment）

> 状态：进行中 | 优先级：P1 | 依赖：00-31 admin-referral-policies-governance-refinement，05-12 share-invite-code-consolidation
> 记录目的：把工作台中的 referral 模块从单点“异常邀请”入口提升为完整的“邀请治理”入口链。

## 1. 背景

当前工作台 `OverviewView.vue` 中，referral 域只以“异常邀请审核”模块出现。

这会导致两个问题：

- 运营容易把 referral 理解成单一风控页，而不是完整治理域。
- `邀请记录 / 邀请资格 / 邀请规则` 三个已存在页面在工作台缺少可见入口链。

## 2. 范围

### 2.1 本轮必须处理

- `kaipai-admin/src/views/dashboard/OverviewView.vue`

### 2.2 本轮不处理

- dashboard overview 后端接口
- recent items 路由分发逻辑
- referral 四个子页面本身

## 3. 需求

### 3.1 模块语义

- **R1** 工作台中的 referral 模块标题必须从“异常邀请审核”升级为“邀请治理”。
- **R2** 模块说明必须明确 referral 是治理域，而不是单页动作入口。
- **R3** 模块状态仍以 `referralRiskPendingCount` 作为当前待处理压力信号。

### 3.2 入口链

- **R4** 模块内必须提供四个清晰入口：
  - 异常邀请
  - 邀请记录
  - 邀请资格
  - 邀请规则
- **R5** 保留一个主 CTA，优先进入异常邀请。
- **R6** 四个入口应在同一模块卡中展示，而不是散落成独立模块。

### 3.3 交互边界

- **R7** 不新增 dashboard 接口字段。
- **R8** 不修改 recent items 的既有行为。
- **R9** 页面整体文案应继续维持“邀请治理”口径。

## 4. 验收标准

- [ ] 已新增独立 Spec 并登记索引与代码映射
- [ ] 工作台 referral 模块已改为“邀请治理”
- [ ] 模块内已展示四个 referral 子入口
- [ ] `npm run build` 在 `kaipai-admin` 通过
