# 00-89 执行记录

## 1. 当前状态

- 已重新读取 `C:\Users\33340\.codex\memories\user-global-memory.md`
- 已核对 `CURRENT_CONTEXT.md`、`README.md` 与 `00-88`
- 已把当前主线继续收窄到 `users/orgs` 首屏与目录区

## 2. 修复前证据

### 2.1 修复前截图

- reference：`D:\XM\kaipai-team\output\playwright\00-89\orgs-reference.png`
- 当前运行态：`D:\XM\kaipai-team\output\playwright\00-89\orgs-before.png`

### 2.2 修复前量化

`2026-04-22` 当前轮次真实浏览器量化结果：

- KPI 卡：`367 × 161`，当前呈现为 `3 + 1`
- segment / 快筛壳层高度：`128px`
- FilterPanel 高度：`244px`
- 首个机构卡尺寸：`349 × 342`
- 首个机构卡顶部：`y ≈ 1092`

## 3. 设计判断

当前最合理的下一手是：

- 不离开 `机构管理` 页面
- 只处理首屏结构与目录区表达
- 不动详情抽屉和招募链路事实源

原因：

- reference 差异已明确集中在首屏和目录区
- 当前目录区被前置壳层挤出首屏
- 这是典型的 page-level 视觉密度问题

## 4. 本轮实施

### 4.1 代码改动

文件：

- `D:\XM\kaipai-team\kaipai-admin\src\views\user\OrganizationsView.vue`

已实施内容：

1. 局部恢复 `organization-overview` 的桌面单行 4 卡布局，避免继续被共享样式压成 `3 + 1`
2. 移除顶部独立 `el-alert`，把边界说明收口为首屏轻量 `organization-boundary-note`
3. 将目录区从原来的卡片墙：
   - `.organization-grid`
   - `.organization-card`
   收口为更接近 reference 的：
   - `.organization-ledger`
   - `.organization-ledger__row`
4. 将 `FilterPanel` 下沉到目录区之后，让机构目录重新进入首屏
5. 第二手继续压缩首屏说明区：
   - 缩短 `boundaryAlertTitle / boundaryAlertDescription`
   - 缩短目录 header hint
   - 收紧 segment、搜索区、boundary note 与 ledger header / row 的局部尺寸
6. 整个过程只改模板顺序、局部 copy 和局部样式；未改聚合逻辑与详情抽屉

### 4.2 边界确认

本轮未改动：

- 详情抽屉结构
- `/admin/recruit/projects`
- `/admin/recruit/roles`
- `/admin/recruit/applies`
- `/company/{userId}`
- reference 中没有真实事实源支撑的等级、到期日、用户数等字段

## 5. 验证结果

### 5.1 真实浏览器复核

会话：

- 当前运行态：Playwright `layout-shell`

运行态路径：

- 当前页：`http://127.0.0.1:5100/users/orgs`
- reference：`http://127.0.0.1:8765/_-_1.html`

修复前后截图：

- reference：`D:\XM\kaipai-team\output\playwright\00-89\orgs-reference.png`
- 修复前：`D:\XM\kaipai-team\output\playwright\00-89\orgs-before.png`
- 第一手收口后：`D:\XM\kaipai-team\output\playwright\00-89\orgs-after.png`
- 第二手收口后：`D:\XM\kaipai-team\output\playwright\00-89\orgs-after-v2.png`

### 5.2 最新量化

`2026-04-22` 当前轮次真实浏览器最新量化结果：

- KPI 卡：`272 × 132`，已恢复桌面单行 4 卡
- `organization-shell-card`：`1134 × 139`
- `organization-boundary-note`：`1084 × 26`
- 目录 header：`1084 × 53`
- 首个 ledger 行：`1082 × 72`
- 首个目录行顶部：`y ≈ 558`
- `FilterPanel` 顶部：`y ≈ 741`
- `loadingMasks = 0`
- `segments = ["全部机构1","进行中1","有投递1","待补档案0"]`

### 5.3 修复前后对比

| 项目 | 修复前 | 当前最新 | 结论 |
|------|--------|----------|------|
| KPI 卡 | `367 × 161`，`3 + 1` | `272 × 132`，单行 4 卡 | 已恢复首屏概览关系 |
| 首个目录项表达 | `349 × 342` 厚卡片 | `1082 × 72` ledger 行 | 已从卡片墙切回目录表达 |
| 首个目录项顶部 | `y ≈ 1092` | `y ≈ 558` | 已重新进入首屏 |
| 前置说明区 | segment 壳层 `128px` + FilterPanel `244px` | shell card `139px` + boundary note `26px` + header `53px` | 首屏前置壳层已明显收紧 |
| 高级筛选位置 | 目录区之前 | 目录区之后，顶部 `y ≈ 741` | 已不再压住目录首屏 |

### 5.4 运行态判断

当前修复后运行态已更接近 reference：

- 首屏先看到 4 个 KPI
- KPI 下方已快速进入机构目录
- 目录区已从厚卡片墙改为轻量 ledger
- 机构页边界仍然保持真实事实源承接，没有伪装成完整组织主数据中心

当前仍保留的 reference 差异：

- reference 的 `VIP / 到期日 / 用户数` 属于原型字段，当前运行态没有真实事实源支撑，因此继续不伪造
- 当前页仍保留真实招募链路说明和筛选面板，这是运行态边界所必需的治理信息

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

`00-89` 已完成本轮目标：

- `OrganizationsView.vue` 已完成机构页首屏和目录区独立收口
- 运行态已通过真实浏览器复核
- 修复前后截图、量化结果与构建验证已回填

如果继续后台 reference UI 主线，下一手最自然的候选是继续看 `system/settings` 的滚动后半段 / 子入口细节，或切到下一个尚未独立精修的正式页。
