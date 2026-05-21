# 00-100 设计说明

## 1. 设计目标

`00-100` 只解决 `system/roles` 首屏结构：

1. **overview retire / compress**：退掉顶部厚 overview 3 卡的仪表盘感
2. **filter panel tighten**：收紧筛选壳层
3. **first matrix earlier**：让 `AI 授权收口矩阵` 的表格主体更早进入首屏

## 2. 已核实的事实

### 2.1 当前问题集中在首屏垂直占高

真实运行态截图：

- current：`D:\XM\kaipai-team\output\playwright\00-100\roles-before.png`

当前量化：

- overview：`1134 × 161`
- FilterPanel：`1134 × 176`
- AI matrix card：`1134 × 489`
- AI matrix summary：`1084 × 105`
- AI matrix alert：`1084 × 63`
- 首个矩阵行顶部：约 `y=946`

这不是数据问题，而是 page-level 首屏密度问题。

### 2.2 该页没有 direct reference 子页

reference 的 8 页正式导航里只有 `系统设置` 聚合页，不直接包含 `system/roles` 隐藏工具页。

因此本轮目标是：

- 对齐当前 refined admin shell 的系统域语言
- 避免继续保留“旧治理工具页”的厚 overview 感

### 2.3 事实源边界不能被打破

当前真实来源仍包括：

- `/system/roles`
- AI 授权矩阵接口
- 招募治理授权矩阵接口

因此本轮不能：

- 改角色模型
- 改权限模型
- 改矩阵字段语义

## 3. 设计策略

### 3.1 overview 退场为轻量 shell

把 3 张厚 overview 卡收口为一张轻量 shell card：

- 显示角色总数
- 显示当前筛选焦点
- 显示当前状态范围
- 外加一条轻量边界 note

### 3.2 FilterPanel 收紧

保留当前筛选字段，但局部压缩：

- header
- input 高度
- item gap
- description 文案

### 3.3 首张 AI 矩阵壳层收紧

只对第一张 `AI 授权收口矩阵` 卡做局部收口：

- card header
- matrix summary
- summary block
- alert
- matrix table margin

不改：

- 第二张 `招募治理授权矩阵`
- 角色清单
- 表格字段
- 操作列和弹窗

## 4. 风险与边界

### 4.1 已确认

- 这是 `RolesView.vue` 的首屏结构问题
- 不需要动接口
- 不需要动矩阵表格行密度和弹窗

### 4.2 待验证

- 轻量 shell card 是否比 3 overview 卡更稳定
- FilterPanel 压缩后字段是否仍清晰可用
- 首张 AI 矩阵表格是否能更早进入首屏

因此本轮必须结合：

- 浏览器截图
- 运行态量化
- `type-check / build`

一起验证。
