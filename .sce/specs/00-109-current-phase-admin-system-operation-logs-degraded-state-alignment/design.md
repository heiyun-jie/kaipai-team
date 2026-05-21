# 00-109 设计说明

## 1. 设计目标

`00-109` 只解决 `system/operation-logs` 的首屏降级问题：

1. **runtime degradation**：`loadLogs` 失败时不再抛未处理异常
2. **source boundary visibility**：显式区分“事实源异常”和“当前筛选条件下为空”
3. **empty-state alignment**：让表格区空态与当前 refined admin shell 一致，不再使用默认 `No Data`

## 2. 已核实的事实

### 2.1 当前页主要问题是运行态语义错误

真实运行态截图：

- current：`D:\XM\kaipai-team\output\playwright\00-109\operation-logs-before.png`

真实浏览器 console：

- `Unhandled error during execution of mounted hook`
- `Error: 操作失败`

当前这张页表面上像“无数据”，但实际是接口异常；因此继续只做视觉密度收紧收益很低。

### 2.2 现有仓内已有同源降级口径

`SettingsView.vue` 已用 `Promise.allSettled` 把该事实源标记为：

- `事实源异常`

这说明当前产品语义已经接受 operation logs 事实源可能异常；`OperationLogsView.vue` 本身需要跟上这一边界，而不是继续伪装成正常空页。

## 3. 设计策略

### 3.1 列表加载

本轮将：

- 在 `loadLogs` 中补 `catch`
- 失败时把 `rows / total` 清空，但显式记录 `sourceError`
- 不再把错误向 mounted hook 外抛

### 3.2 首屏事实源状态

本轮将：

- 概览主卡从固定 `0 条操作记录` 改为按 `sourceError / sourceLoaded / total` 动态表达
- 表格 header hint 与 empty state 同步承接当前事实源状态

### 3.3 空态表达

本轮将：

- 在表格 `#empty` 中补自定义 `table-empty`
- 正常空态：提示当前条件下没有操作记录
- 降级态：提示当前 `operation-logs` 接口不可用，页面只保留筛选条件与审计入口说明

## 4. 风险与边界

### 4.1 已确认

- 当前改动可以局限在 `OperationLogsView.vue`
- 不需要改 API 层签名
- 不需要动后端接口或权限模型

### 4.2 待验证

- 前端 catch 后 console 是否不再出现 mounted hook 未处理异常
- 降级态截图是否比当前默认 `No Data` 更清晰
- 当前页在事实源恢复后是否仍能正常显示真实空态

因此本轮必须结合：

- 浏览器截图
- console 对比
- DOM 量化
- `type-check / build`

一起验证。
