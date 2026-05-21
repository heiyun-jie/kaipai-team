# 00-90 执行记录

## 1. 当前状态

- 已重新读取 `C:\Users\33340\.codex\memories\user-global-memory.md`
- 已核对 `CURRENT_CONTEXT.md`、`README.md` 与 `00-89`
- 已把当前主线继续收窄到 `dashboard/analytics` 默认 `channel` 首屏

## 2. 修复前证据

### 2.1 修复前截图

- reference：`D:\XM\kaipai-team\output\playwright\00-90\analytics-reference.png`
- 当前运行态：`D:\XM\kaipai-team\output\playwright\00-90\analytics-current-authenticated.png`

### 2.2 修复前量化

`2026-04-22` 当前轮次真实浏览器量化结果：

- tabs shell：`488 × 94`
- 左表：`621 × 283`
- 右卡：`447 × 571`

## 3. 设计判断

当前最合理的下一手是：

- 不离开 `数据分析` 页面
- 只处理默认 `channel` tab 首屏
- 不动真实接口和其他三个 tab

原因：

- reference 差异已明确集中在首屏 tabs、渠道区和 donut 区
- 当前左卡的主要问题是被右卡拉伸后的大块空白
- 这是典型的 page-level 视觉密度问题

## 4. 本轮实施

### 4.1 代码改动

文件：

- `D:\XM\kaipai-team\kaipai-admin\src\views\dashboard\DashboardAnalyticsView.vue`

已实施内容：

1. 收紧默认 tabs strip：
   - `analytics-toolbar-card .el-card__body`
   - `analytics-tabs`
   - `analytics-tab`
2. 默认 `channel` tab 左侧从 `el-table` 改为轻量 ledger / progress board：
   - `.analytics-ledger`
   - `.analytics-ledger__head`
   - `.analytics-ledger__row`
   - `.analytics-progress`
3. 右侧 `CHANNEL MIX` 卡改为更紧凑的横向 donut + legend：
   - `.analytics-donut--compact`
   - `.analytics-donut__legend--compact`
   - `.analytics-insight--compact`
4. 修复双栏高度关系：
   - `analytics-grid` 增加 `align-items: start`
   - 避免左侧渠道卡被右侧 donut 卡高度拉伸后出现大块空白
5. 缩短 fact-boundary copy：
   - 保留 `sceneKey` 近似承接说明
   - 不伪造微信好友 / 朋友圈 / 企业微信真实渠道字段

### 4.2 边界确认

本轮未改动：

- `/admin/dashboard/overview`
- route query 时间窗口
- `retention / funnel / segment` 三个 tab 的业务结构
- `AdminTopbar.vue`
- reference 中无真实来源的微信好友 / 朋友圈 / 企业微信渠道数值

## 5. 验证结果

### 5.1 真实浏览器复核

会话：

- 当前运行态：Playwright `layout-shell`
- reference：Playwright `analytics-reference`

运行态路径：

- 当前页：`http://127.0.0.1:5100/dashboard/analytics`
- reference：`http://127.0.0.1:8765/_-_1.html`

修复前后截图：

- reference：`D:\XM\kaipai-team\output\playwright\00-90\analytics-reference.png`
- 修复前：`D:\XM\kaipai-team\output\playwright\00-90\analytics-current-authenticated.png`
- 第一手收口后：`D:\XM\kaipai-team\output\playwright\00-90\analytics-after.png`
- 第二手收口后：`D:\XM\kaipai-team\output\playwright\00-90\analytics-after-v2.png`

### 5.2 最新量化

`2026-04-22` 当前轮次真实浏览器最新量化结果：

- tabs shell：`446 × 66`
- `analytics-ledger`：`629 × 280`
- 首个 ledger 行：`627 × 78`
- 右侧 donut mix 卡：`447 × 446`
- insight：`405 × 133`
- `loadingMasks = 0`

### 5.3 修复前后对比

| 项目 | 修复前 | 当前最新 | 结论 |
|------|--------|----------|------|
| tabs shell | `488 × 94` | `446 × 66` | 已明显收紧 |
| 左侧渠道表达 | `el-table`，表格区约 `621 × 283`，卡片被右侧拉伸后底部空白明显 | `analytics-ledger`，`629 × 280` | 已从通用表格改成轻量 board |
| 右侧 mix 卡 | `447 × 571` | `447 × 446` | 已明显压缩 |
| 双栏高度关系 | 左卡被右卡拉伸 | `align-items: start` 后左右卡按内容高度渲染 | 已修复首屏空白问题 |
| 渠道口径 | scene 分布近似承接 | scene 分布近似承接 | 事实源边界保持不变 |

### 5.4 运行态判断

当前修复后运行态已更接近 reference：

- 默认首屏保持 tabs + 左渠道 board + 右 donut mix 的双栏结构
- 左侧不再是厚重 `el-table`
- 右侧 donut / legend / insight 已收紧
- 不再伪造 reference 原型里的真实微信渠道数据

仍保留的 reference 差异：

- 顶部 `导出分析` 是当前共享顶控里的显式降级入口，本轮按 scope 未修改
- reference 原型的微信好友 / 朋友圈 / 企业微信字段没有真实接口支撑，当前继续用 scene 近似承接并明确说明

### 5.5 静态构建验证

命令：

- `cd D:\XM\kaipai-team\kaipai-admin && npm run type-check`
- `cd D:\XM\kaipai-team\kaipai-admin && npm run build`

结果：

- `type-check`：通过
- `build`：通过

保留告警：

- Sass legacy JS API deprecation
- Vite chunk size warning

## 6. 结论

`00-90` 已完成本轮目标：

- `DashboardAnalyticsView.vue` 默认 `channel` 首屏已完成独立局部收口
- 运行态已通过真实浏览器复核
- 修复前后截图、量化结果与构建验证已回填

如果继续后台 reference UI 主线，下一手最自然的候选是继续在 `dashboard/analytics` 做 `retention / funnel / segment` 三个 tab 的局部精修，或转回 `system/settings` 的滚动后半段 / 子入口细节。
