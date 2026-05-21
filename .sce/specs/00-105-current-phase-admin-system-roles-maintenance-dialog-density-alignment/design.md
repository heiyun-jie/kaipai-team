# 00-105 设计说明

## 1. 设计目标

`00-105` 只解决 `system/roles` 的维护弹窗密度：

1. **dialog shell**：收紧 header / body / footer / close button
2. **intro density**：降低 `dialog-intro` 占高
3. **form density**：收紧表单项高度与间距
4. **permission density**：压缩权限包卡片、tag list 和权限树编辑区
5. **scroll strategy**：把创建 / 编辑弹窗改为有限高度 dialog，滚动收进 body，不再让整个弹窗高度超过视口

## 2. 已核实的事实

### 2.1 当前问题已收窄到维护弹窗

真实运行态截图：

- create：`D:\XM\kaipai-team\output\playwright\00-105\roles-create-before.png`
- edit：`D:\XM\kaipai-team\output\playwright\00-105\roles-edit-before.png`
- copy：`D:\XM\kaipai-team\output\playwright\00-105\roles-copy-before.png`

当前量化：

- 新建：`860 × 2008`
- 编辑：`860 × 2236`
- 复制：`560 × 674`

这说明当前 residual 已不在主页面，而在维护弹窗本身。

### 2.2 当前厚度主要来自三处

1. 共享 dialog shell 仍偏厚
2. `dialog-intro` 和通用表单项高度偏大
3. 创建 / 编辑弹窗的权限编排区过长，导致整个 dialog 超过视口高度

### 2.3 维护弹窗和状态确认弹窗应拆开

当前状态确认弹窗同样偏厚，但它走的是 `AuditConfirmDialog` 共享组件链，风险模型与创建 / 编辑 / 复制不同。

因此本轮应：

- 先做 `新建 / 编辑 / 复制`
- 下一轮再独立处理状态确认弹窗

## 3. 设计策略

### 3.1 为维护弹窗增加本地 class

为弹窗增加：

- `roles-action-dialog`
- `roles-action-dialog--form`
- `roles-action-dialog--copy`

所有收口都通过这些本地 class 限定，避免影响其它 dialog。

### 3.2 dialog shell

本轮收紧：

- `el-dialog__header`
- `el-dialog__title`
- `el-dialog__body`
- `el-dialog__footer`
- `el-dialog__headerbtn`

### 3.3 创建 / 编辑弹窗滚动策略

创建 / 编辑弹窗不追求把全部内容压到首屏内，而是：

- 把 dialog 本体限制在视口内
- 把滚动收进 body
- 保持 footer 始终可达

这比单纯减小字体或强行压缩树结构更稳。

### 3.4 权限编排区

本轮收紧：

- `permission-stack`
- `el-alert`
- `ai-governance-bundle-grid`
- `ai-governance-bundle-card`
- `PermissionTreeEditor` 内部：
  - `permission-editor`
  - `toolbar`
  - `toolbar-actions`
  - `unknown-list`
  - `permission-tree`
  - `tree-node`

### 3.5 权限包 tag 文案策略

权限包 tag 改为：

- 可见文本使用 `getPermissionCompactDisplayText`
- 完整文本通过 `title` 保留

这样可以明显降低卡片高度，同时不丢失完整权限信息。

## 4. 风险与边界

### 4.1 已确认

- 当前改动只涉及 `RolesView.vue` 的维护弹窗
- 不影响详情抽屉
- 不影响创建 / 编辑 / 复制接口与字段

### 4.2 待验证

- 创建 / 编辑弹窗在 body 内滚动后，footer 是否仍稳定可见
- 权限树编辑区收紧后是否仍可操作
- 复制角色弹窗是否与新样式保持一致

因此本轮必须结合：

- 运行态量化
- 浏览器截图
- `type-check / build`

一起验证。
