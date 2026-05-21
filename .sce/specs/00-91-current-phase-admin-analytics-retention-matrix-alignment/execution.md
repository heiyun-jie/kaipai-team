# 00-91 执行记录

## 1. 当前状态

- 已重新读取 `C:\Users\33340\.codex\memories\user-global-memory.md`
- 已核对 `CURRENT_CONTEXT.md`、`README.md` 与 `00-90`
- 已把当前主线继续收窄到 `dashboard/analytics` 的 `retention` tab

## 2. 修复前证据

### 2.1 修复前截图

- reference：`D:\XM\kaipai-team\output\playwright\00-91\analytics-retention-reference-clicked.png`
- 当前运行态：`D:\XM\kaipai-team\output\playwright\00-91\analytics-retention-current.png`

### 2.2 修复前量化

`2026-04-22` 当前轮次真实浏览器量化结果：

- 第一张 retention 卡：`559 × 456`
- 第二张说明卡：`559 × 344`
- `retention-grid`：`509 × 336`
- 首张 `retention-card`：`160 × 161`
- `analytics-insight--spacious`：`509 × 220`

## 3. 设计判断

当前最合理的下一手是：

- 不离开 `数据分析` 页面
- 只处理 `retention` tab
- 不动真实接口和其他三个 tab

原因：

- reference 差异已明确集中在 `单板矩阵` vs `多卡 + 说明盒`
- 当前 retention tab 仍是典型的 page-level 结构问题
- 风险低、可逆

## 4. 本轮实施

### 4.1 代码改动

文件：

- `D:\XM\kaipai-team\kaipai-admin\src\views\dashboard\DashboardAnalyticsView.vue`

已实施内容：

1. 将 `retention` tab 从双卡结构改为单张矩阵板：
   - 原结构：左侧 `retention-grid` + 右侧 `analytics-insight--spacious`
   - 新结构：单张 `analytics-card--retention`
2. 新增代理矩阵结构：
   - `.retention-matrix`
   - `.retention-matrix__head`
   - `.retention-matrix__row`
   - `.retention-matrix__heat`
3. 新增 `retentionMatrixRows`：
   - 活跃分享卡
   - 持卡用户
   - 分享访问
   - 唯一访客
   - 查看后成卡
   - 已同意联系
4. 矩阵列只使用真实 overview 字段推导：
   - 当前值
   - 对持卡用户占比
   - 对分享访问占比
5. 将治理信号收口为矩阵底部内联 note：
   - 退款待处理
   - 联系方式待处理
   - 实名认证待审
6. 删除不再使用的 `retentionRows` 多卡数据结构

### 4.2 边界确认

本轮未改动：

- `/admin/dashboard/overview`
- route query 时间窗口
- `channel / funnel / segment` 三个 tab
- `AdminTopbar.vue`
- reference 中无真实来源的 `W-7 ~ W-1` 周 cohort 与 `D1 / D7 / D14 / D30` 留存率

## 5. 验证结果

### 5.1 真实浏览器复核

会话：

- 当前运行态：Playwright `layout-shell`
- reference：Playwright `analytics-reference`

运行态路径：

- 当前页：`http://127.0.0.1:5100/dashboard/analytics`
- reference：`http://127.0.0.1:8765/_-_1.html`

修复前后截图：

- reference：`D:\XM\kaipai-team\output\playwright\00-91\analytics-retention-reference-clicked.png`
- 修复前：`D:\XM\kaipai-team\output\playwright\00-91\analytics-retention-current.png`
- 修复后：`D:\XM\kaipai-team\output\playwright\00-91\analytics-retention-after.png`

### 5.2 最新量化

`2026-04-22` 当前轮次真实浏览器最新量化结果：

- active tab：`留存分析`
- retention 单板：`1134 × 707`
- `retention-matrix`：`1092 × 490`
- 首个 matrix 行：`1090 × 74`
- `retention-governance`：`1092 × 92`
- `loadingMasks = 0`

### 5.3 修复前后对比

| 项目 | 修复前 | 当前最新 | 结论 |
|------|--------|----------|------|
| 页面结构 | 左 6 卡 + 右说明盒 | 单张 retention matrix 板 | 已接近 reference 单板矩阵结构 |
| 第一张卡 | `559 × 456` | 合并为 `1134 × 707` 单板 | 已消除左右拆分 |
| 第二张说明卡 | `559 × 344` | 合并为底部 `1092 × 92` 内联 note | 说明区已明显收紧 |
| 指标卡 | 单张 `160 × 161`，共 6 张 | matrix 行 `1090 × 74` | 已从厚卡片改为矩阵行 |
| 事实口径 | 活动代理 + 大段说明 | 当前窗口代理矩阵 + 内联边界 | 事实源边界保持不变 |

### 5.4 运行态判断

当前修复后运行态已更接近 reference：

- `retention` tab 首屏从多卡说明态转为单张矩阵板
- 代理指标以 heatmap / matrix 方式表达
- 边界说明从右侧大卡收进矩阵底部
- 没有伪造 reference 原型里的真实 cohort 留存序列

当前仍保留的 reference 差异：

- reference 的 `W-7 ~ W-1` 与 `D1 / D7 / D14 / D30` 是原型值，当前运行态没有真实事实源支撑
- 当前页继续明确写成“当前窗口留存代理矩阵”，不伪装成熟 cohort 系统

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

`00-91` 已完成本轮目标：

- `DashboardAnalyticsView.vue` 的 `retention` tab 已完成独立局部收口
- 运行态已通过真实浏览器复核
- 修复前后截图、量化结果与构建验证已回填

如果继续后台 reference UI 主线，下一手最自然的候选是继续在 `dashboard/analytics` 做 `funnel` tab 或 `segment` tab 的局部精修。
