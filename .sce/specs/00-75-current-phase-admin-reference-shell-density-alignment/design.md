# 00-75 设计说明

## 1. 设计目标

`00-75` 不再处理后台正式导航、页面职责或 runtime source，而只解决一个更窄的问题：

1. **desktop topbar nowrap**：主线页桌面顶控回到单行表达
2. **title stability**：主标题在桌面首屏保持单行
3. **density tightening**：首屏标题与控制条的空间分配更接近 reference

## 2. 已核实的运行态事实

### 2.1 当前问题不是新的 IA 偏差

在 `00-74` 完成后，以下事实已经稳定：

- 正式侧栏仍为 `OVERVIEW / GROWTH / OPERATE`
- 8 个正式页面都已进入真实运行态
- `AdminLayout / AdminSidebar` 最近一轮收紧后没有出现破版或文字拥挤

这意味着当前剩余偏差已经从“页面架构”收口成“共享壳层密度”。

### 2.2 当前最新浏览器证据

基于真实浏览器主线页截图，已确认：

- `dashboard-index-shell-verify.png`
  - dashboard 顶控右区发生换行
- `dashboard-analytics-current-shell.png`
  - `数据分析` 标题被压成两行
  - 右侧顶控区仍拆成两行
- `users-index-current-shell.png`
  - `用户管理` 标题被压成两行
  - 搜索与通知/账号入口仍拆行
- `content-templates-current-shell.png`
  - `风格模板` 标题被压成两行
  - 搜索与通知/账号入口仍拆行

因此当前问题是：

- 桌面主线页标题与右侧顶控没有分到足够稳定的横向空间
- `AdminTopbar.vue` 的 shrink-to-fit 与 wrap 策略不适合 reference 当前密度

## 3. 设计策略

### 3.1 不继续动 Sidebar / Layout

当前不再改：

- `D:\XM\kaipai-team\kaipai-admin\src\layouts\AdminLayout.vue`
- `D:\XM\kaipai-team\kaipai-admin\src\components\layout\AdminSidebar.vue`

原因：

- 这两处已经通过最新浏览器复核
- 当前可复现问题集中发生在 `AdminTopbar.vue`
- 继续改 Sidebar / Layout 会扩大写入面，但不能直接解决标题与顶控换行

### 3.2 只改 `AdminTopbar.vue` 的桌面布局策略

核心思路：

1. 让主线页左侧标题区变成真正可伸缩的 `flex` 区
2. 让右侧控制区在桌面下优先保持 `max-content` 单行，而不是被 shrink 成多行
3. 搜索框宽度从“隐式撑开”改成“有上限的稳定宽度”
4. 主标题字号、行高、nowrap 策略收紧，避免 2~4 个汉字仍断行

### 3.3 具体实现策略

#### 左侧标题区

- `admin-topbar__left`
  - 改为 `flex: 1 1 auto`
  - `min-width: 0`
- `admin-topbar__headline strong`
  - 主线页桌面下使用更紧的字号 / 行高
  - 强制 `white-space: nowrap`

#### 右侧控制区

- `admin-topbar__right`
  - 桌面下改成 `flex-wrap: nowrap`
  - 使用 `flex: 0 0 auto` 与 `min-width: max-content`
  - 避免搜索框把容器压成 shrink-to-fit 宽度

#### 搜索与按钮密度

- `admin-topbar__search`
  - 改为稳定桌面宽度，不再只靠 `min-width`
  - 保留输入区可读性
- `admin-topbar__chip--button`
- `admin-topbar__icon-button`
- `admin-topbar__button`
- `admin-topbar__user`
  - 增加 `flex-shrink: 0`
  - 保持桌面单行按钮稳定度

#### 断点策略

- `max-width: 900px` 以下仍保留现有堆叠逻辑
- `00-75` 不改变窄屏降级方式

## 4. 影响文件

- `D:\XM\kaipai-team\kaipai-admin\src\components\layout\AdminTopbar.vue`
- `D:\XM\kaipai-team\.sce\specs\00-75-current-phase-admin-reference-shell-density-alignment\requirements.md`
- `D:\XM\kaipai-team\.sce\specs\00-75-current-phase-admin-reference-shell-density-alignment\design.md`
- `D:\XM\kaipai-team\.sce\specs\00-75-current-phase-admin-reference-shell-density-alignment\tasks.md`
- `D:\XM\kaipai-team\.sce\specs\00-75-current-phase-admin-reference-shell-density-alignment\execution.md`
- `D:\XM\kaipai-team\.sce\specs\README.md`
- `D:\XM\kaipai-team\.sce\specs\spec-code-mapping.md`
- `D:\XM\kaipai-team\.sce\steering\CURRENT_CONTEXT.md`

## 5. 风险与边界

### 5.1 已确认

- 当前问题集中在 `AdminTopbar.vue`
- 当前问题在多张主线页上可重复出现
- 当前问题属于低风险、可逆的桌面壳层密度修复

### 5.2 待验证

- dashboard 在保留搜索 + 窗口 + 通知 + 导出 + 账号入口时，桌面单行是否仍需要进一步压缩搜索宽度
- 主标题字号收紧后，是否仍保持 reference 的首屏气质，而不是变得过小

因此本轮先做：

- 桌面单行对齐
- 浏览器验证

若仍有残余差异，再进入下一轮更细的 page-level 密度微调。
