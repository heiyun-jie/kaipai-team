# 00-39 设计说明

## 1. 设计原则

- 在已有时间窗口透传之上追加“当前事项标识”透传
- 不改后端接口，只复用目标页已有筛查字段
- 区分“模块跳转”和“最近事项跳转”，避免把列表入口误收窄

## 2. 设计策略

### 2.1 dashboard 最近事项 query 映射

- `identity_verification`
  - `/verify/pending`
  - 透传 `userId`
  - 继续透传 `submitTimeFrom/submitTimeTo`

- `referral_risk`
  - `/referral/risk`
  - 优先透传 `inviteCode=referenceNo`
  - 辅助透传 `inviteeUserId=userId`
  - 继续透传 `registeredAtFrom/registeredAtTo`

- `refund_order`
  - `/refund/orders`
  - 透传 `refundNo=referenceNo`
  - 辅助透传 `userId`
  - 继续透传 `createdAtFrom/createdAtTo`

- `payment_order`
  - `/payment/orders`
  - 透传 `orderNo=referenceNo`
  - 辅助透传 `userId`
  - 继续透传 `createdAtFrom/createdAtTo`

### 2.2 目标页回填

目标页在现有路由 query 回填逻辑上增加精确字段读取：

- `VerificationBoard`：`userId`
- `RiskView`：`inviteCode`、`inviteeUserId`
- `Refund OrdersView`：`refundNo`、`userId`
- `Payment OrdersView`：`orderNo`、`userId`

## 3. 影响文件

- `kaipai-admin/src/views/dashboard/OverviewView.vue`
- `kaipai-admin/src/views/referral/RiskView.vue`
- `kaipai-admin/src/views/refund/OrdersView.vue`
- `kaipai-admin/src/views/payment/OrdersView.vue`
- `kaipai-admin/src/views/verify/VerificationBoard.vue`
- `.sce/specs/README.md`
- `.sce/specs/spec-code-mapping.md`
