# 00-33 设计说明

## 1. 设计原则

- 路由分发优先遵循后端事实字段
- 当前只实现已知真实值，不做猜测式扩展
- 对未知值继续保留安全回退

## 2. 设计策略

### 2.1 已知 itemType 映射

- `identity_verification -> /verify/pending`
- `referral_risk -> /referral/risk`
- `refund_order -> /refund/orders`
- `payment_order -> /payment/orders`

### 2.2 回退策略

若 `itemType` 未命中显式映射，则按 `bizLine` 回退：

- `verify -> /verify/pending`
- `referral -> /referral/risk`
- `refund -> /refund/orders`
- `payment -> /payment/orders`

### 2.3 类型声明

`DashboardRecentItem.itemType` 从裸 `string` 收口为已知联合类型加字符串兜底，便于后续继续扩展。

## 3. 影响文件

- `kaipai-admin/src/views/dashboard/OverviewView.vue`
- `kaipai-admin/src/types/dashboard.ts`
- `.sce/specs/README.md`
- `.sce/specs/spec-code-mapping.md`
