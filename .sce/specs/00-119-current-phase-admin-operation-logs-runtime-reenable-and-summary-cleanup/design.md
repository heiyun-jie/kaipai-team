# 00-119 设计说明

## 1. 设计目标

`00-119` 只处理系统设置页的 operation-logs 摘要口径：

1. 后端已恢复时，不再默认显示异常
2. 真实异常时，继续保留异常提示
3. 不改变 operation-logs 页面自身的降级兜底

## 2. 已核实事实

### 2.1 operation-logs 列表事实源已恢复

`00-118` 已验证：

- `GET /admin/system/operation-logs?pageNo=1&pageSize=1` -> `code=200`

### 2.2 系统设置页仍有旧降级摘要口径

当前 `SettingsView.vue` 中：

- `operationLogLoaded` 初始为 `false`
- `operationLogLabel` 使用：
  - `operationLogLoaded ? "${total} 条记录" : "事实源异常"`

这导致：

- 加载尚未完成时也会被显示成事实源异常

## 3. 设计策略

新增：

- `operationLogError`

状态规则：

| 状态 | 条件 | 展示 |
|------|------|------|
| 初始 / 加载中 | `!operationLogLoaded && !operationLogError` | `正在核对` |
| 成功 | `operationLogLoaded` | `${operationLogTotal} 条记录` |
| 异常 | `operationLogError` | `事实源异常` |

## 4. 风险与边界

### 4.1 已确认

- 本轮只改系统设置页摘要，不影响 operation-logs 列表页
- 保留失败分支，不会隐藏真实异常

### 4.2 边界

- 本轮不做浏览器截图复核
- 本轮以 type-check / build 和 `00-118` 运行态事实作为验证依据
