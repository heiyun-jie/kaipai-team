# 00-15 财务后台日期范围筛选（Finance Date Range Filters）

> 状态：进行中 | 优先级：P0 | 依赖：00-11 platform-admin-console
> 记录目的：把支付订单、支付流水、退款单、退款日志四个财务列表页的日期范围筛选回接到后端已开放的 DTO 字段，补齐运营可用性。

## 1. 背景

财务页当前已有列表与详情，但日期范围筛选尚未完全回接到后端 DTO 字段，运营按时间检索支付 / 退款记录的效率仍不足。

## 2. 范围

### 2.1 本轮必须处理

- 支付订单：创建时间、支付时间范围
- 支付流水：回调时间范围
- 退款单：支付单号、创建时间、审核时间范围
- 退款日志：日志时间范围

### 2.2 本轮不处理

- 新增统计报表
- 新增导出能力
- 改造后端查询接口

## 3. 需求

### 3.1 支付订单

- **R1** 支付订单页必须支持 `createdAtFrom/createdAtTo`
- **R2** 支付订单页必须支持 `paidAtFrom/paidAtTo`

### 3.2 支付流水

- **R3** 支付流水页必须支持 `callbackFrom/callbackTo`

### 3.3 退款单

- **R4** 退款单页必须支持 `paymentOrderNo`
- **R5** 退款单页必须支持 `createdAtFrom/createdAtTo`
- **R6** 退款单页必须支持 `auditedAtFrom/auditedAtTo`

### 3.4 退款日志

- **R7** 退款日志页必须支持 `dateFrom/dateTo`

### 3.5 一致性

- **R8** 日期控件输出必须与后端 `LocalDateTime` 查询字段兼容
- **R9** 重置筛选时必须同步清空日期范围

## 4. 验收标准

- [ ] 已新增独立 Spec 并登记增量索引
- [ ] 四个财务页日期范围筛选已回接后端 DTO 字段
- [ ] `npm run type-check` 与 `npm run build` 通过
