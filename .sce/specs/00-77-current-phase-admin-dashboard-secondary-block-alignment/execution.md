# 00-77 执行记录

## 1. 当前状态

- 已重新读取 `User Global Memory`
- 已核对 `00-76` 当前收口结果
- 已把当前主线继续收窄到 dashboard 次级三块

## 2. 已核实的修复前证据

### 2.1 reference 对比基线

- `D:\XM\kaipai-team\output\playwright\00-74-reference\reference-dashboard.png`

### 2.2 当前运行态基线

- `D:\XM\kaipai-team\output\playwright\00-76\dashboard-index-full.png`

当前确认的剩余差异：

- `留存承接`
  - 当前标题被压成多行
  - 当前 stacked 代理卡过重
- `风格偏好`
  - 当前 donut 与 legend 仍偏下堆叠
- `渠道分布`
  - 当前仍是 bar board，与 reference 差距较大

## 3. 设计判断

当前最合理的下一手不是去碰其他页面，也不是回到共享样式，而是继续沿 dashboard 同一证据链推进。

原因：

- 当前问题仍然只落在 `OverviewView.vue`
- reference 与当前 full-page 对比已足够明确
- 修复范围小、风险低、可逆

## 4. 本轮实施

### 4.1 已改文件

- `D:\XM\kaipai-team\kaipai-admin\src\views\dashboard\OverviewView.vue`

### 4.2 已实施内容

#### 留存承接

- 移除原先过重的纵向 stacked retention cards
- 改成：
  - retention canvas / placeholder 区
  - 右上代理徽记
  - 底部 4 个代理指标横向排列
  - 轻量说明区

当前继续只使用：

- `activeShareCardCount`
- `activeShareOwnerCount`
- `uniqueViewerCount`
- `approvedContactRequestCount`

没有伪造次日、7日或 cohort 曲线。

#### 风格偏好

- 保留现有 scene donut
- 从“下堆叠 legend”改成更接近 reference 的横向：
  - 左侧 donut
  - 右侧纵向 legend

#### 渠道分布

- 不再继续使用 bar board
- 改成：
  - donut
  - 右侧 legend
  - 底部边界说明

当前 donut 继续只认 scene 近似承接，不引入真实渠道归因事实源。

#### 次级区块共享局部收口

- `dashboard-grid--secondary .table-header`
  - 改为更轻的 stacked header
  - 避免 `留存承接` 标题继续被压成多行
- `table-header__hint`
  - 改成左对齐、全宽轻量说明

### 4.3 代码层验证

已执行：

- `cd D:\XM\kaipai-team\kaipai-admin && npm run type-check`
- `cd D:\XM\kaipai-team\kaipai-admin && npm run build`

结果：

- `type-check`：通过
- `build`：通过
- 已知 warning：
  - Sass legacy JS API deprecation
  - Vite chunk size warning
- 当前均不是本轮新增问题

### 4.4 浏览器运行态复核

已通过真实 Playwright 会话 `layout-shell` 重新采集：

- 修复前：
  - `D:\XM\kaipai-team\output\playwright\00-76\dashboard-index-full.png`
- 修复后：
  - `D:\XM\kaipai-team\output\playwright\00-77\dashboard-index-secondary-full.png`

已确认：

- `留存承接`
  - 标题已恢复单行
  - 结构已从重堆叠卡改成更轻的代理承接板
- `风格偏好`
  - donut 与 legend 已更接近 reference 的横向关系
- `渠道分布`
  - 已从 bar board 收口为 donut + legend
  - 边界说明仍保留，未伪装成真实渠道归因系统
- 浏览器 console：0 errors / 0 warnings

## 5. 本轮结论

`00-77` 首轮目标已完成：

- dashboard 次级三块的剩余差异已被继续收口
- 当前修改仍然只留在 `OverviewView.vue` 本地
- 没有无证据外溢到共享样式、共享顶控或其他页面

因此，后台当前主线已经从：

- `00-76` 的 dashboard 首屏首轮收口

进一步推进到：

- `00-77` 的 dashboard 次级三块首轮收口完成

若后续还要继续精修，下一轮更合理的方向是：

- dashboard 底部 `正式页面矩阵 / 治理动态` 的 page-level 密度
- 或转入下一张正式页的 page-level 精修

而不是回到共享顶控或 IA。
