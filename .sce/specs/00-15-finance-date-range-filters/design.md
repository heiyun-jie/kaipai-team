# 财务后台日期范围筛选 - 技术设计

_Requirements: 00-15 全部_

## 1. 设计目标

在不修改后端接口的前提下，为支付 / 退款列表页补齐日期范围筛选，使前端查询字段和后端 DTO 一一对应。

## 2. 字段映射

- 支付订单：
  - `createdAtFrom` / `createdAtTo`
  - `paidAtFrom` / `paidAtTo`
- 支付流水：
  - `callbackFrom` / `callbackTo`
- 退款单：
  - `paymentOrderNo`
  - `createdAtFrom` / `createdAtTo`
  - `auditedAtFrom` / `auditedAtTo`
- 退款日志：
  - `dateFrom` / `dateTo`

## 3. 交互策略

- 使用 `el-date-picker` 的 `datetimerange`
- `value-format` 统一使用 `YYYY-MM-DDTHH:mm:ss`
- 页面内用临时 range 值驱动两个独立查询字段
- 点击“重置”时同时清空 range UI 和底层 query 字段

## 4. 验证方式

1. 四个页面都能设置时间范围并发起查询
2. 重置后时间范围 UI 与 query 字段都清空
3. 运行 `npm run type-check`
4. 运行 `npm run build`
