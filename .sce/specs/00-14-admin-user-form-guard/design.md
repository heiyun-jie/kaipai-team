# 后台账号表单校验与高风险原因约束 - 技术设计

_Requirements: 00-14 全部_

## 1. 设计目标

在不修改后端接口契约的前提下，为后台账号页补齐最小但有效的前端校验，统一高风险操作原因约束。

## 2. 校验策略

优先复用 Element Plus `el-form` 规则与现有 `AuditConfirmDialog`：

1. 创建 / 编辑账号：使用 `el-form` + `rules`
2. 绑定角色：在现有弹窗表单中要求 `reason`
3. 重置密码：要求 `newPassword`、`credentialDeliveryMode`、`reason`
4. 启用 / 禁用：把 `AuditConfirmDialog` 的 `reasonRequired` 显式打开

## 3. 输入规范

- 字符串提交前统一 `trim`
- 手机与邮箱仅做基础格式拦截，不引入更激进的业务规则
- 不新增前端自定义密码复杂度策略，避免与后端契约脱节

## 4. 验证方式

1. 空账号 / 空姓名 / 空密码时前端直接阻断
2. 手机或邮箱格式非法时前端直接阻断
3. 绑定角色、重置密码、启停用空原因时前端直接阻断
4. 运行 `npm run type-check`
5. 运行 `npm run build`
