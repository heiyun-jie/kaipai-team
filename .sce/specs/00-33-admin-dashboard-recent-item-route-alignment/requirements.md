# 00-33 后台工作台最近事项路由对齐（Admin Dashboard Recent Item Route Alignment）

> 状态：进行中 | 优先级：P1 | 依赖：00-32 admin-dashboard-referral-governance-entry-alignment
> 记录目的：把工作台最近事项从“按 bizLine 粗分发”收口为“按 itemType 精分发，未知值回退”。

## 1. 背景

当前 `OverviewView.vue` 的最近事项跳转规则按 `bizLine` 粗分发：

- `verify -> /verify/pending`
- `referral -> /referral/risk`

但后端 `recentItems` 已提供 `itemType`，说明路由分发的真实锚点应是事项类型，而不是业务线。

经本轮核对，当前 dashboard 后端真实产出的 `itemType` 为：

- `identity_verification`
- `referral_risk`
- `refund_order`
- `payment_order`

其中 referral 当前只有 `referral_risk`，前端不应臆测更多值，但应先把分发层改成按 `itemType`。

## 2. 范围

### 2.1 本轮必须处理

- `kaipai-admin/src/views/dashboard/OverviewView.vue`
- `kaipai-admin/src/types/dashboard.ts`

### 2.2 本轮不处理

- dashboard 后端接口
- recentItems 后端 itemType 产出逻辑
- referral 子页面本身

## 3. 需求

### 3.1 路由分发

- **R1** 最近事项跳转必须优先按 `itemType` 分发。
- **R2** 已知类型应显式映射：
  - `identity_verification`
  - `referral_risk`
  - `refund_order`
  - `payment_order`
- **R3** 对未知 `itemType` 必须回退到既有 `bizLine` 默认路由。

### 3.2 referral 边界

- **R4** 当前 referral 最近事项只允许把 `referral_risk` 映射到 `/referral/risk`。
- **R5** 不允许在当前分支臆造 `referral_record`、`referral_policy` 等未被后端产出的事项类型。

## 4. 验收标准

- [ ] 已新增独立 Spec 并登记索引与代码映射
- [ ] `OverviewView` 最近事项已按 `itemType` 分发
- [ ] referral 当前只识别 `referral_risk`
- [ ] `npm run build` 在 `kaipai-admin` 通过
