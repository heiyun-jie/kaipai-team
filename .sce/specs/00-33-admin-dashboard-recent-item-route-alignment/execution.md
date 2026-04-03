# 00-33 后台工作台最近事项路由对齐 - 执行记录

> 执行日期：2026-04-03
> 范围：`kaipai-admin` dashboard 最近事项路由分发

## 1. 后端事实核对

已核对后端 `AdminDashboardServiceImpl` 当前真实产出的 `itemType`：

- `identity_verification`
- `referral_risk`
- `refund_order`
- `payment_order`

其中 referral 当前仅产出：

- `referral_risk`

对应代码位置：

- `kaipaile-server/src/main/java/com/kaipai/module/server/system/service/impl/AdminDashboardServiceImpl.java`

## 2. 本轮结论

- 最近事项跳转已从“按 bizLine 粗分发”改为“按 itemType 精分发，未知值回退”。
- referral 当前只识别并映射 `referral_risk -> /referral/risk`。
- 没有臆造新的 referral itemType。

## 3. 落地文件

- `kaipai-admin/src/types/dashboard.ts`
- `kaipai-admin/src/views/dashboard/OverviewView.vue`

## 4. 分发规则

### 4.1 itemType 显式映射

- `identity_verification -> /verify/pending`
- `referral_risk -> /referral/risk`
- `refund_order -> /refund/orders`
- `payment_order -> /payment/orders`

### 4.2 bizLine 回退

若未来后端新增 `itemType` 且前端尚未接入，则继续按 `bizLine` 回退：

- `verify -> /verify/pending`
- `referral -> /referral/risk`
- `refund -> /refund/orders`
- `payment -> /payment/orders`

## 5. 验证结果

- 已执行：`cd kaipai-admin && npm run build`
- 结果：通过
- 保留告警：
  - Vite chunk size warning
  - Sass legacy JS API deprecation warning

本轮未新增阻塞错误。
