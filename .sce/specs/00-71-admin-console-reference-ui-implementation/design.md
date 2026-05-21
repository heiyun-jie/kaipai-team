# 00-71 设计说明

## 1. 设计目标

把 `kaipai-admin` 从“旧后台共享壳层继续微调”，提升为“基于 `D:\XM\kaipai-team\_-_1.html` 的控制台式后台”：

1. 先统一壳层与工作台
2. 再以这套壳层作为后续其他业务页的视觉基线
3. 整个过程不新增后台功能，只重组已有功能入口和已有数据表达

## 2. 设计原则

- 先保留真实路由 / 权限 / 接口，再调整视觉结构
- 先收口控制台壳层，再收口工作台
- 参考稿只指导视觉与布局，不直接等价为产品功能清单
- 只承接当前已存在的后台能力，不做“原型里看起来应该有”的新增模块
- 空态、缺数据和未联调状态必须显式保真，不允许伪装成真实已完成

## 3. 参考稿解读

经渲染核对，`D:\XM\kaipai-team\_-_1.html` 重点表达的是：

- 左侧为窄导航，顶部有品牌区、分组标题、底部账号区
- 主区顶部是轻量信息条而不是厚重 hero
- 工作台主体是 4 张关键指标卡 + 2 行看板区块
- 页面整体偏“编辑感 / 控制台感”，而不是旧后台那种层层运营说明卡片

因此本轮不把参考稿理解为“再做一个静态 dashboard”，而是理解为：

- 一套新的后台控制台壳层语言
- 一套新的工作台排版方式
- 一种“已有功能如何被重新组织”的信息架构

## 4. 真实代码映射

### 4.1 本轮核心落点

| 目标 | 真实文件 | 说明 |
|------|----------|------|
| 公共壳层 | `kaipai-admin/src/layouts/AdminLayout.vue` | 控制内容画布、留白和容器 |
| 左侧导航 | `kaipai-admin/src/components/layout/AdminSidebar.vue` | 重新组织已存在菜单 |
| 顶部栏 | `kaipai-admin/src/components/layout/AdminTopbar.vue` | 轻量状态条 + 账号区 |
| 菜单来源 | `kaipai-admin/src/stores/permission.ts` | 仍基于权限过滤后的真实菜单 |
| 全局视觉 | `kaipai-admin/src/styles/index.scss` | 背景、表单、卡片、全局节奏 |
| 工作台 | `kaipai-admin/src/views/dashboard/OverviewView.vue` | 用已有字段重组看板布局 |

### 4.2 非本轮核心落点

以下页面继续保留原有业务结构，只通过公共壳层继承新控制台语言：

- `verify/*`
- `referral/*`
- `recruit/*`
- `membership/*`
- `payment/*`
- `refund/*`
- `content/*`
- `system/*`

## 5. 壳层设计

### 5.1 左侧导航

导航仍由真实权限过滤后的 `adminMenus` 驱动，但在展示层重组为三段：

- `OVERVIEW`
- `CORE`
- `OPERATION`

设计意图：

- 保持参考稿的控制台分组感
- 不改变真实路由、菜单权限和页面权限
- 允许在不新增模块的前提下提升导航可读性

### 5.2 顶部栏

顶部栏不再承担大段说明，而是承担：

- 当前页面路径语义
- 当前页面标题
- 当前日期 / 状态 / 角色
- 当前账号

这样可以更贴近参考稿的轻量控制台气质，同时不丢失后台账号和状态信息。

### 5.3 主内容壳

主内容区使用统一浅色面板承托页面内容：

- 让左导航、topbar、正文三层关系更清晰
- 使后续其他业务页无需全部重写，也能整体进入同一控制台语境

## 6. 工作台设计

### 6.1 数据来源边界

工作台只允许使用当前 `DashboardOverview` 已有字段：

- `verifyPendingCount`
- `referralRiskPendingCount`
- `refundPendingCount`
- `todayPaymentOrderCount`
- `activeShareCardCount`
- `activeShareOwnerCount`
- `shareViewCount`
- `uniqueViewerCount`
- `approvedContactRequestCount`
- `pendingContactRequestCount`
- `convertedViewerCount`
- `classicSceneViewCount`
- `urbanSceneViewCount`
- `costumeSceneViewCount`
- `recentItems`

### 6.2 版块设计

工作台按参考稿重组为：

1. 页面标题区
2. 筛选区
3. 顶部关键指标卡
4. 核心指标结构区
5. 业务热度区
6. 阶段分布 / 风格偏好 / 业务来源占比
7. 已有功能入口列表
8. 实时动态

### 6.3 允许的推导

允许基于现有字段进行轻量派生：

- 转化率
- 通过率
- 占比
- 环形分布
- 入口统计摘要

但这些派生必须：

- 来源于现有真实字段
- 不要求后端新增字段
- 不能伪装成新的平台分析能力

## 7. 实现策略

### 7.1 首轮实现

首轮只处理：

- `AdminLayout`
- `AdminSidebar`
- `AdminTopbar`
- `permission store` 的侧栏数据来源
- `OverviewView`
- 必要的全局样式

### 7.2 不动的运行时层

本轮不改：

- router 路由边界
- 接口路径
- 权限码
- 页面真实交互链路
- 业务字段与表格操作逻辑

### 7.3 验收方式

优先做：

- `npm run type-check`
- `npm run build`
- 预览构建产物做视觉核对

如果本地后端未启动，则：

- 只验证前端壳层与路由可见性
- 不把未联调状态误报为真实接口已完成

## 8. 与 00-18 的边界

### 8.1 00-18 负责什么

- 后台页头 / 筛选区 / 卡片壳层统一
- 让其他页面能自动继承工作台时代的视觉语言

### 8.2 00-71 负责什么

- 把 `_-_1.html` 确立为新的后台控制台参考基线
- 重做后台公共壳层与工作台的信息架构
- 明确“已有功能进入新控制台”的组织方式

因此：

- `00-18` 是“旧后台体系内的共享壳层统一”
- `00-71` 是“参考稿驱动的后台控制台重构”

## 9. 当前影响文件

### 已落地

- `D:\XM\kaipai-team\kaipai-admin\src\stores\permission.ts`
- `D:\XM\kaipai-team\kaipai-admin\src\layouts\AdminLayout.vue`
- `D:\XM\kaipai-team\kaipai-admin\src\components\layout\AdminSidebar.vue`
- `D:\XM\kaipai-team\kaipai-admin\src\components\layout\AdminTopbar.vue`
- `D:\XM\kaipai-team\kaipai-admin\src\styles\index.scss`
- `D:\XM\kaipai-team\kaipai-admin\src\views\dashboard\OverviewView.vue`

### 后续可继续推进

- `D:\XM\kaipai-team\kaipai-admin\src\views\verify\*`
- `D:\XM\kaipai-team\kaipai-admin\src\views\referral\*`
- `D:\XM\kaipai-team\kaipai-admin\src\views\membership\*`
- `D:\XM\kaipai-team\kaipai-admin\src\views\payment\*`
- `D:\XM\kaipai-team\kaipai-admin\src\views\refund\*`
- `D:\XM\kaipai-team\kaipai-admin\src\views\content\*`
- `D:\XM\kaipai-team\kaipai-admin\src\views\system\*`

## 10. 风险控制

- 不允许新增“分析模块”“运营模块”“内容模块”等伪入口
- 不允许因为参考稿好看而引入假数据
- 不允许破坏既有权限过滤结果
- 不允许在后端未启动时把视觉预览结果误报为真实联调完成
