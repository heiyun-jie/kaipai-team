# 00-76 设计说明

## 1. 设计目标

`00-76` 的目标不是再次动后台 IA 或共享顶控，而是把 dashboard 首屏继续往 reference 靠：

1. **KPI row**：恢复单行 4 卡
2. **primary grid**：漏斗 / 趋势双卡首屏横向更稳定
3. **first-screen density**：首屏纵向密度收紧

## 2. 已核实的事实

### 2.1 当前问题不是共享顶控

`00-75` 后已确认：

- 顶控已在 `dashboard/index` 单行恢复
- 标题已恢复单行

因此当前差异不再是 `AdminTopbar.vue`。

### 2.2 当前问题也不是直接等于全局 `page-overview` 缺陷

已核查：

- `page-overview` 与 `page-overview-card` 的 3 列布局来自共享样式：
  - `D:\XM\kaipai-team\kaipai-admin\src\styles\index.scss`
- 该共享样式同时被：
  - `UserCenterView.vue`
  - `OrganizationsView.vue`
  - `ActionsView.vue`
  - `SettingsView.vue`
  - `OverviewView.vue`
  复用

这意味着：

- 如果直接把共享 `page-overview` 改成 4 列，会外溢影响多页
- 当前只有 dashboard 有 reference 的首屏硬证据
- 所以这轮必须做成 `OverviewView.vue` 本地覆盖，而不是共享重构

## 3. 设计策略

### 3.1 只改 `OverviewView.vue`

当前只允许修改：

- `D:\XM\kaipai-team\kaipai-admin\src\views\dashboard\OverviewView.vue`

不改：

- `src/styles/index.scss`
- `AdminTopbar.vue`
- `AdminLayout.vue`
- `AdminSidebar.vue`

### 3.2 KPI 区

对 `.dashboard-overview` 增加 dashboard 局部覆盖：

- 桌面下改成 4 列
- gap 略收紧
- 卡片高度与内边距单独压缩

这样可以：

- 恢复 reference 的单行 4 卡
- 不影响用户管理 / 机构管理 / 运营动作 / 系统设置等其他页

### 3.3 首屏主双卡

对 `.dashboard-grid--primary` 做 dashboard 局部覆盖：

- 调整两列比例，给趋势卡更稳定的横向空间
- 收紧双卡 body padding、chart/board 的纵向占用
- 控制 header hint 的宽度与字号，让标题优先稳定显示

### 3.4 首屏密度

目标不是把 dashboard 做得更花，而是：

- 保留真实事实边界说明
- 通过局部 padding、gap、min-height、header spacing 收紧首屏
- 让 reference 的“同屏更高信息密度”被更好承接

## 4. 风险与边界

### 4.1 已确认

- 当前问题集中在 dashboard
- 当前问题可以通过本地样式覆盖低风险收口
- 该路径可逆，不影响后端与数据边界

### 4.2 待验证

- 4 卡单行后，说明文案是否会把卡片高度再次拉高
- 趋势卡加宽后，漏斗卡是否仍保持可读

因此本轮先做：

- dashboard 首屏局部密度收紧
- 浏览器复核

若验证通过，再决定是否要继续进入下一条单页精修线。
