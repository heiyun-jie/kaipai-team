# 00-94 设计说明

## 1. 设计目标

`00-94` 只解决 `system/settings` 的 grouped-row 细节：

1. **grouped cards**：收紧每组卡的 header 和 hint
2. **row density**：让 grouped rows 更接近 reference 的紧凑行表达
3. **sub-entry affordance**：补齐更明确的右侧进入感

## 2. 已核实的事实

### 2.1 当前问题集中在行级表达，不再是首屏结构问题

真实运行态截图：

- current：`D:\XM\kaipai-team\output\playwright\00-94\settings-current.png`
- reference：`D:\XM\kaipai-team\output\playwright\00-94\settings-reference.png`

当前量化：

- 第一张卡：`680 × 314`
- 第二张卡：`680 × 378`
- 第三张卡：`680 × 378`
- 现有子入口行高：约 `62-63px`

当前问题是：

- grouped card header 偏厚
- grouped row 的副文案仍占高
- value 文案过长

### 2.2 reference 的核心语义

reference 已确认：

- 三组 grouped cards 宽度较窄
- 每组是更干净的 rows
- 右侧 value 后跟轻量进入 affordance
- 没有大段解释文案压住行表达

### 2.3 事实源边界不能被打破

当前系统设置页真实来源包括：

- `/admin/dashboard/overview`
- `/content/templates`
- `/content/share-cards`
- `/system/admin-users`
- `/system/roles`
- `/system/operation-logs`
- `/system/ai-resume-governance`

因此本轮不能伪造：

- `juming.app`
- `help@juming.app`
- 超级管理员 / 运营岗 / 审核岗的人数

## 3. 设计策略

### 3.1 压缩 grouped card header

保留：

- eyebrow
- group title
- 事实边界 hint

但会：

- 缩短 hint copy
- 收紧字体和行距
- 减少 header 与 rows 之间空白

### 3.2 收口 row 细节

保留当前三段式信息：

- title
- subtitle
- value

但会：

- 缩短 subtitle
- 进一步降低 row 高度
- 让右侧 value 更紧凑

### 3.3 增加右侧 affordance

通过轻量箭头样式，给每个 row 更接近 reference 的进入感。

### 3.4 风险控制

- 不改入口路由
- 不删行
- 不改 facts
- 只改 copy 和样式密度

## 4. 风险与边界

### 4.1 已确认

- 这是 `SettingsView.vue` 的行级表达问题
- 不需要改数据接口
- 不应伪造 reference 的配置值

### 4.2 待验证

- 更短文案是否仍足够表达事实边界
- 行级进入感增强后是否不影响可读性
- 行高继续压缩后是否不影响点击区域

因此本轮必须结合：

- 浏览器截图
- 运行态量化
- `type-check / build`

一起验证。
