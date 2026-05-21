# 00-106 设计说明

## 1. 设计目标

`00-106` 只解决 `system/roles` 的启用 / 禁用确认弹窗密度：

1. **dialog shell**：收紧 dialog width、header、body、footer 与 close button
2. **intro density**：降低 `dialog-intro` 占高
3. **meta density**：压缩 `dialog-meta` 和 meta item
4. **reason area**：收紧 textarea 和 tip，但保留原因填写可用性

## 2. 已核实的事实

### 2.1 当前问题已收窄到状态确认弹窗

真实运行态截图：

- current：`D:\XM\kaipai-team\output\playwright\00-106\roles-status-before.png`

当前量化：

- 弹窗：`520 × 687`
- header：`67px`
- body：`511px`
- footer：`75px`
- intro：`117px`
- meta：`434 × 204`
- textarea：`434 × 96`

这说明当前 residual 已不在维护弹窗，而在状态确认弹窗的 dialog shell、intro、meta 和输入区。

### 2.2 当前最稳的方案是 page-local 收口

`AuditConfirmDialog` 已经支持：

- `dialogClass`
- `width`

因此本轮最稳的路径是：

- 不修改组件默认行为
- 在 `RolesView.vue` 调用点启用 page-local class 和 width
- 用 `:deep(.roles-status-dialog ...)` 做局部覆写

### 2.3 可直接复用 `00-99` 的收口模式

`00-99` 已在 `system/admin-users` 验证过：

- 可选 `dialogClass / width` 扩展入口可行
- page-local dialog-density 风险低
- 不会误伤其它页面

所以 `00-106` 可直接复用同类策略，但仅应用到 `RolesView.vue`。

## 3. 设计策略

### 3.1 调用点接入局部入口

在 `RolesView.vue` 的 `AuditConfirmDialog` 调用点增加：

- `dialog-class="roles-status-dialog"`
- `width="500px"`

### 3.2 本轮收紧内容

通过 `:deep(.roles-status-dialog ...)` 覆盖：

- `el-dialog__header`
- `el-dialog__title`
- `el-dialog__body`
- `el-dialog__footer`
- `el-dialog__headerbtn`
- `dialog-content`
- `dialog-intro`
- `dialog-meta`
- `el-textarea__inner`
- `dialog-tip`

### 3.3 不动默认组件样式

不修改 `AuditConfirmDialog.vue` 的默认 CSS，避免影响其它业务页。

## 4. 风险与边界

### 4.1 已确认

- 当前改动只影响 `RolesView.vue` 的状态确认弹窗
- 不影响维护弹窗
- 不影响其它页面对 `AuditConfirmDialog` 的默认表现

### 4.2 待验证

- textarea 收紧后是否仍可填写较长原因
- meta 区收紧后是否仍可读
- page-local class 是否真正命中 teleport 后的 dialog

因此本轮必须结合：

- 运行态量化
- 浏览器截图
- `type-check / build`

一起验证。
