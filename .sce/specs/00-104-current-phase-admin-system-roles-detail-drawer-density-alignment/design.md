# 00-104 设计说明

## 1. 设计目标

`00-104` 只解决 `system/roles` 的 `角色详情` 抽屉密度：

1. **drawer shell**：收紧抽屉 header、body padding 和 close button
2. **detail hero**：降低 hero 占高，但保持角色与状态可读
3. **detail density**：把字段块从厚卡节奏收口为轻量治理详情网格
4. **permission tag density**：把权限 tag 从“中文 + 权限码”长标签收口为抽屉内中文标签展示，同时保留完整权限语义可追溯

## 2. 已核实的事实

### 2.1 当前问题已收窄到详情抽屉

真实运行态截图：

- current：`D:\XM\kaipai-team\output\playwright\00-104\roles-detail-drawer-before.png`

当前量化：

- drawer：`760 × 1100`
- header：`758 × 77`
- hero：`706 × 85`
- detail grid：`706 × 516`
- `detail-block`：`346 × 92`
- permission grid：`706 × 2166`
- detail cards：`255 / 597 / 1281`
- tag lists：`106 / 448 / 1132`

这说明当前 residual 不再是表格区，而在详情抽屉壳层、字段块和权限 tag。

### 2.2 临时试验结论

本轮做过两类运行态试验：

1. 单纯加宽抽屉：
   - 没有产生有效量化收益
2. 收紧 tag / card / body：
   - permission grid 从约 `2166px` 降到约 `1584px`
3. 收紧壳层并把权限 tag 改为中文标签：
   - header 从约 `77px` 降到约 `61px`
   - hero 从约 `85px` 降到约 `71px`
   - detail grid 从约 `516px` 降到约 `398px`
   - `detail-block` 从约 `92px` 降到约 `70px`
   - permission grid 从约 `2166px` 降到约 `894px`
   - 三组 tag list 从约 `106 / 448 / 1132px` 降到约 `54 / 114 / 324px`

结论：

- 当前主要问题不是 drawer width
- 当前主要问题是权限 tag 的“中文 + 权限码”导致换行过多
- 本轮应做抽屉内中文标签紧凑展示，并用 `title` 保留完整权限文本

## 3. 设计策略

### 3.1 增加抽屉本地 class

为 `el-drawer` 增加：

- `roles-detail-drawer`

所有壳层收口都通过该 class 限定，避免影响其它 Element Plus drawer。

### 3.2 抽屉壳层

本轮收紧：

- `el-drawer__header`
- `el-drawer__title`
- `el-drawer__body`
- `el-drawer__close-btn`

抽屉宽度保持 `760px`，不把宽度调整作为主方案。

### 3.3 详情内容

本轮收紧：

- `.drawer-hero`
- `.detail-grid`
- `.detail-block`
- `.permission-grid`
- `.detail-card`
- `.tag-list`
- `.el-tag`

### 3.4 权限 tag 文案策略

详情抽屉内：

- 可见文本使用 `getPermissionCompactDisplayText(item)`
- 完整文本通过 `title` 保留

示例：

- 可见：`系统管理菜单`
- title：`系统管理菜单 · menu.system`

这样既减少视觉高度，又不丢失完整权限语义。

## 4. 风险与边界

### 4.1 已确认

- 当前改动只涉及详情抽屉视觉密度
- 不影响详情数据读取
- 不影响 `查看详情` 点击链路
- 不影响权限数组与权限树

### 4.2 待验证

- 中文标签收紧后是否仍可读
- 完整权限文本是否仍可通过 title 追溯
- 权限卡高度是否实际下降
- drawer body 是否保持滚动正常

因此本轮必须结合：

- 运行态量化
- 浏览器截图
- `type-check / build`

一起验证。
