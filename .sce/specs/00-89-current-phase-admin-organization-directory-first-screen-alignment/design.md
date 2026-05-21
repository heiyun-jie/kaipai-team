# 00-89 设计说明

## 1. 设计目标

`00-89` 只解决 `机构管理` 页的首屏和目录区：

1. **kpi row**：恢复单行 4 卡
2. **screen density**：收紧边界提示、segment 和筛选区
3. **directory ledger**：把机构卡片墙收口为更轻的目录表 / ledger

## 2. 已核实的事实

### 2.1 当前问题集中在首屏被前置壳层挤压

真实运行态量化：

- KPI 区：`367 × 161`，当前呈现为 `3 + 1`
- segment / 快筛壳层高度：`128px`
- FilterPanel 高度：`244px`
- 首个机构卡顶部：`y ≈ 1092`

对应截图：

- current：`D:\XM\kaipai-team\output\playwright\00-89\orgs-before.png`
- reference：`D:\XM\kaipai-team\output\playwright\00-89\orgs-reference.png`

### 2.2 reference 的核心语义

reference 已确认：

- 首屏先看到 4 个 KPI
- 紧接着进入机构列表 / 目录
- 目录表达更接近 ledger / table，而不是多块大卡

### 2.3 事实源边界不能被打破

当前机构目录真实来源为：

- `/admin/recruit/projects`
- `/admin/recruit/roles`
- `/admin/recruit/applies`
- `/company/{userId}`

因此本轮不能伪造：

- reference 里的等级体系
- 会员到期日
- 机构总用户数等当前无事实源字段

## 3. 设计策略

### 3.1 KPI 单行化

只在 `OrganizationsView.vue` 局部恢复：

- `organization-overview` -> `repeat(4, minmax(0, 1fr))`

并收紧每张 overview card 的高度与字号。

### 3.2 前置壳层压缩

本轮继续保留：

- 边界提示
- segment / 快筛
- FilterPanel

但会：

- 把边界提示收成更轻的 inline note
- 收紧 segment 高度和搜索宽度
- 把高级筛选下沉到目录区之后，使目录提前进入首屏

### 3.3 目录区改为 ledger

保留当前 `pagedOrganizations` 数据，但把展示从 `.organization-grid / .organization-card` 改为：

- 轻量目录列头
- 机构行
- 真实统计列
- 状态列
- 入口动作列

### 3.4 风险控制

- 不改详情抽屉结构
- 不改聚合逻辑
- 仅调整模板顺序和局部样式

## 4. 风险与边界

### 4.1 已确认

- 当前是 `OrganizationsView.vue` 的首屏结构问题
- 不需要改共享壳层或全局 `page-overview`
- 不应触碰详情抽屉与接口

### 4.2 待验证

- FilterPanel 下沉后首屏是否明显更接近 reference
- ledger 化后条目是否仍可读、可点击
- KPI 单行后是否不出现拥挤

因此本轮必须结合：

- 浏览器截图
- 运行态量化
- `type-check / build`

一起验证。
