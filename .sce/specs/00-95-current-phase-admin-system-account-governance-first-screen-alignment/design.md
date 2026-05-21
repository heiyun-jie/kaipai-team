# 00-95 设计说明

## 1. 设计目标

`00-95` 只解决 `system/admin-users` 的首屏结构：

1. **overview retire / compress**：退掉厚 overview 3 卡的仪表盘感
2. **filter panel tighten**：收紧筛选壳层
3. **table earlier**：让账号清单更早进入首屏

## 2. 已核实的事实

### 2.1 当前问题集中在首屏垂直占高

真实运行态截图：

- current：`D:\XM\kaipai-team\output\playwright\00-95\admin-users-current.png`

当前量化：

- overview：`1134 × 161`
- FilterPanel：`1134 × 244`
- table card：`1134 × 432`
- 首个表格行：约 `95px`

这不是数据问题，而是 page-level 首屏密度问题。

### 2.2 该页没有 direct reference 子页

reference 的 8 页正式导航不包含 `system/admin-users` 隐藏工具页。

因此本轮目标是：

- 对齐当前 refined admin shell 的系统域语言
- 避免继续保留“旧治理工具页”的厚 overview 感

### 2.3 事实源边界不能被打破

当前真实来源仍包括：

- `/system/admin-users`
- `/system/roles`

因此本轮不能：

- 改账号模型
- 改角色绑定模型
- 伪造新的组织域

## 3. 设计策略

### 3.1 overview 退场为轻量 shell

把 3 张厚 overview 卡收口为一张轻量 shell card：

- 显示账号总数
- 显示当前筛选焦点
- 显示当前状态范围
- 外加一条轻量边界 note

### 3.2 FilterPanel 收紧

保留当前筛选字段，但局部压缩：

- header
- input 高度
- item gap
- description 文案

### 3.3 table header 继续前移

通过：

- overview 退场
- filter 收紧
- table header hint 收短

让表格区尽快进入首屏。

## 4. 风险与边界

### 4.1 已确认

- 这是 `AdminUsersView.vue` 的首屏结构问题
- 不需要动接口
- 不需要动表格行高和弹窗

### 4.2 待验证

- shell card 是否比 3 overview 卡更稳定
- FilterPanel 压缩后字段是否仍清晰可用
- 首屏是否能更早看到表格

因此本轮必须结合：

- 浏览器截图
- 运行态量化
- `type-check / build`

一起验证。
