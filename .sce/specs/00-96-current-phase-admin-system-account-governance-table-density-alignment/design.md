# 00-96 设计说明

## 1. 设计目标

`00-96` 只解决 `system/admin-users` 的主表密度：

1. **row density**：压低行高与 cell padding
2. **cell hierarchy**：收紧联系方式和角色 cell 的层级
3. **action column**：让操作列更轻，尽量减少它对行高的抬升

## 2. 已核实的事实

### 2.1 当前问题已经从首屏结构转到主表区

真实运行态截图：

- current：`D:\XM\kaipai-team\output\playwright\00-96\admin-users-table-before.png`

当前量化：

- table card：`1134 × 424`
- 首个表格行：约 `95px`
- 首个联系方式 stacked cell：约 `50px`
- 首个角色 tag list：约 `30px`
- `loadingMasks = 0`

这说明当前 residual 不再是首屏 shell 问题，而是表格局部密度问题。

### 2.2 当前厚度主要来自三处

1. 共享表格 padding 对当前页仍偏厚
2. 联系方式 / 角色 cell 继续使用更松的默认层级
3. 操作列保留五个 link action，当前 gap 与字号让它稳定落成两行，从而抬高整行

### 2.3 事实源边界不能被打破

当前真实来源仍包括：

- `/system/admin-users`
- `/system/roles`

因此本轮不能：

- 改账号模型
- 改角色绑定模型
- 改弹窗交互链

## 3. 设计策略

### 3.1 主表卡局部覆盖

继续依赖 `admin-users-table-card`，只在当前页内补局部密度样式：

- `th / td` padding
- `.cell` line-height
- table header 与 pager 间距

### 3.2 stacked cell 与 tag list 收紧

为当前页本地结构补齐局部样式：

- `.stack-cell`
- `.tag-list`
- `.tag-list .el-tag`

目标：

- 联系方式主副文本更紧
- 角色标签更轻，不继续维持共享厚胶囊高度

### 3.3 操作列轻量化

保留现有 link action 与点击能力，但通过以下手段减重：

- 调整操作列宽度
- 收紧 `.table-actions` gap
- 降低 link action 的字号与最小高度
- 让当前 5 个动作在常见桌面宽度下尽量压回单行或更紧的双行

## 4. 风险与边界

### 4.1 已确认

- 这是 `AdminUsersView.vue` 的表格区问题
- 不需要动接口与弹窗
- 风险低、可逆

### 4.2 待验证

- 操作列压缩后是否仍可读、可点
- 列宽收紧后是否会造成额外遮挡
- 行高压缩后是否仍保持角色和联系方式可辨识

因此本轮必须结合：

- 浏览器截图
- 运行态量化
- `type-check / build`

一起验证。
