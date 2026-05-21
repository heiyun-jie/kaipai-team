# 00-97 设计说明

## 1. 设计目标

`00-97` 只解决 `system/admin-users` 的详情抽屉密度：

1. **drawer shell**：收紧抽屉宽度、header 与 body padding
2. **detail hero**：降低 hero 占高，但保持账号与状态可读
3. **detail density**：把字段块由厚卡节奏收口成更轻的治理详情网格

## 2. 已核实的事实

### 2.1 当前问题已收窄到详情抽屉

真实运行态截图：

- current：`D:\XM\kaipai-team\output\playwright\00-97\admin-users-drawer-before-open.png`

当前量化：

- 抽屉宽度：`620px`
- header：`618 × 77`
- body：`618 × 1021`
- hero：`566 × 85`
- detail grid：`566 × 827`
- `detail-block`：`92px`
- 角色 `tag-list`：`532 × 34`

这说明当前 residual 已不在表格区，而在详情抽屉壳层与字段块密度。

### 2.2 当前厚度主要来自三处

1. 共享 `el-drawer__header / body` 对当前页仍偏厚
2. 共享 `drawer-hero` 与 `detail-block` 节奏偏大
3. 当前页没有详情卡分组，所有字段直接平铺，块高一旦偏厚就会把整屏拉长

### 2.3 事实源边界不能被打破

当前真实来源仍包括：

- `/system/admin-users`
- `/system/roles`

因此本轮不能：

- 改字段语义
- 改详情接口
- 改角色绑定模型

## 3. 设计策略

### 3.1 增加抽屉本地 class

为 `el-drawer` 增加本地 class：

- `admin-users-detail-drawer`

所有壳层收口都通过该 class 限定，避免影响其它 Element Plus drawer。

### 3.2 抽屉壳层

本轮收紧：

- `size`
- `el-drawer__header`
- `el-drawer__title`
- `el-drawer__body`
- close button 尺寸

### 3.3 详情内容

本轮只做视觉密度：

- `.detail-grid` gap
- `.drawer-hero` padding / radius / 标题层级
- `.detail-block` min-height / padding / 字号 / 行高
- 角色绑定区 `tag-list / el-tag`

## 4. 风险与边界

### 4.1 已确认

- 当前改动只涉及详情抽屉视觉密度
- 不影响详情数据读取
- 不影响 `查看详情` 点击链路
- 风险低、可逆

### 4.2 待验证

- 抽屉宽度收窄后双列字段是否仍不拥挤
- 字段块收紧后是否仍可读
- 角色绑定区 tag 是否仍保持可辨识

因此本轮必须结合：

- 运行态量化
- 浏览器截图
- `type-check / build`

一起验证。
