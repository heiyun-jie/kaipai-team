# 00-98 设计说明

## 1. 设计目标

`00-98` 只解决 `system/admin-users` 的三个维护弹窗密度：

1. **dialog shell**：收紧 header、body、footer 与关闭按钮
2. **dialog intro**：降低引导说明块占高
3. **form density**：收紧输入框、textarea、角色选择区和表单项间距

## 2. 已核实的事实

### 2.1 当前剩余问题已收窄到三个维护弹窗

真实运行态截图：

- 新建账号：`D:\XM\kaipai-team\output\playwright\00-98\admin-users-create-before.png`
- 绑定角色：`D:\XM\kaipai-team\output\playwright\00-98\admin-users-bind-before.png`
- 重置密码：`D:\XM\kaipai-team\output\playwright\00-98\admin-users-reset-before.png`

当前量化：

- 新建账号弹窗：`720 × 743`，intro `117px`
- 绑定角色弹窗：`560 × 599`，intro `117px`
- 重置密码弹窗：`560 × 674`，intro `117px`
- 多数表单项仍约 `78px`

这说明当前 residual 已不在首屏、主表和详情抽屉，而在维护弹窗壳层与表单密度。

### 2.2 当前厚度主要来自三处

1. 共享 `el-dialog__header / body / footer` 对当前页仍偏厚
2. 共享 `dialog-intro` 节奏偏大
3. 当前表单项和输入控件最小高度偏高，导致新建、绑定、重置三类弹窗都偏厚

### 2.3 事实源边界不能被打破

当前真实来源仍包括：

- `/system/admin-users`
- `/system/roles`

因此本轮不能：

- 改字段语义
- 改表单校验
- 改接口提交链

## 3. 设计策略

### 3.1 增加弹窗本地 class

为三个弹窗增加本地 class：

- `admin-users-action-dialog`
- `admin-users-action-dialog--form`
- `admin-users-action-dialog--bind`
- `admin-users-action-dialog--reset`

所有壳层收口都通过这些 class 限定，避免影响其它 Element Plus dialog。

### 3.2 弹窗壳层

本轮收紧：

- `el-dialog__header`
- `el-dialog__title`
- `el-dialog__body`
- `el-dialog__footer`
- `el-dialog__headerbtn`

### 3.3 表单内容

本轮只做视觉密度：

- `dialog-intro`
- `el-form-item`
- `el-input__wrapper / el-select__wrapper / el-textarea__inner`
- `role-field`
- textarea 高度与间距

## 4. 风险与边界

### 4.1 已确认

- 当前改动只涉及 `AdminUsersView.vue` 本地弹窗视觉密度
- 不影响表单逻辑与接口链
- 风险低、可逆

### 4.2 待验证

- 收紧后是否仍保持表单可读、可填
- 角色选择区和 textarea 是否仍有足够操作空间
- 三个弹窗是否能在同一套局部规则下稳定收口

因此本轮必须结合：

- 运行态量化
- 浏览器截图
- `type-check / build`

一起验证。
