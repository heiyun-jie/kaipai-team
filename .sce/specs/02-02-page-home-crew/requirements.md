# 首页 - 剧组视角

## 1. 概述

"开拍了"(KaiPai)小程序首页剧组视角页面，路由为 `pages/home/index`（Tab 1），当 `user.role === 2`（剧组）时展示。页面展示当前剧组用户已发布的项目列表，支持查看项目下的角色和申请情况，并提供快捷入口发布新项目。

页面采用 Cinematic Glassmorphism 设计语言：深色头部（标题"我的发布"）+ 白色内容区（项目卡片列表）+ 固定底部发布按钮（Spotlight Orange）+ 毛玻璃 TabBar。

## 2. 用户故事

- 作为剧组用户，我希望打开首页就能看到我发布的所有项目，以便管理招募进度。
- 作为剧组用户，我希望通过项目卡片快速了解每个项目的状态、角色数和申请数。
- 作为剧组用户，我希望点击项目卡片查看该项目下的角色列表，以便管理各角色的申请。
- 作为剧组用户，我希望通过底部按钮快速发布新项目，以便开始新的招募。
- 作为剧组用户，我希望在没有项目时看到引导提示，以便了解如何开始使用。

## 3. 功能需求

### 3.1 页面路由与 TabBar 配置

**描述**: 与演员视角共享同一页面路由 `pages/home/index`（Tab 1）。页面 `onShow` 时根据 `useUserStore().isCrew` 判断是否展示剧组视角。

**依赖**:
- `stores/user.ts` → `useUserStore` (00-03-shared-utils-api §3.7)
- `KpTabBar` 组件 (00-02-shared-components §3.17)

**验收标准**:
- WHEN 剧组用户进入首页 THEN 展示剧组视角（项目列表 + 发布按钮）
- WHEN 演员用户进入首页 THEN 展示演员视角（见 02-01-page-home-actor）
- WHEN 底部 TabBar 渲染 THEN 显示"首页"和"我的"两个导航项，"首页"高亮
- WHEN 点击 TabBar "我的" THEN 跳转到我的页面

### 3.2 项目列表加载

**描述**: 页面加载时调用 `getMyProjects` API 获取当前剧组用户的项目列表，按创建时间倒序，支持分页。

**依赖**:
- `api/project.ts` → `getMyProjects(params: PageParams): Promise<PageResult<Project>>` (00-03-shared-utils-api §3.11)
- `types/project.ts` → `Project`, `ProjectStatus` (00-03-shared-utils-api §3.1)
- `types/common.ts` → `PageResult`, `PageParams` (00-03-shared-utils-api §3.1)

**验收标准**:
- WHEN 页面首次加载 THEN 调用 `getMyProjects({ page: 1, size: 10 })` 获取第一页数据
- WHEN 滚动到底部且还有更多数据 THEN 自动加载下一页并追加到列表
- WHEN 滚动到底部且无更多数据 THEN 显示"没有更多了"提示
- WHEN 加载中 THEN 底部显示加载指示器，防止重复请求
- WHEN API 请求失败 THEN 显示错误提示，支持重试

### 3.3 下拉刷新

**描述**: 支持 uni-app `onPullDownRefresh` 下拉刷新，重置分页参数并重新加载第一页数据。

**验收标准**:
- WHEN 用户下拉刷新 THEN 重置 page 为 1，清空现有列表，重新请求第一页
- WHEN 刷新完成 THEN 调用 `uni.stopPullDownRefresh()` 停止刷新动画

### 3.4 项目卡片展示

**描述**: 列表中每个项目以 `KpProjectCard` 组件展示，卡片内包含项目核心信息和状态标签。

**依赖**:
- `KpProjectCard` 组件 (00-02-shared-components §3.12)
- `KpStatusTag` 组件 (00-02-shared-components §3.18)
- `utils/format.ts` → `formatDate`, `formatProjectStatus` (00-03-shared-utils-api §3.5)

**卡片字段映射**:

| 展示字段 | 数据来源 | 样式说明 |
|---------|---------|---------|
| 项目名称 | `project.title` | 主标题，加粗 |
| 状态标签 | `project.status` | 进行中=绿色 / 已结束=灰色（KpStatusTag） |
| 拍摄地点 | `project.location` | 次要文字色 + 定位图标 |
| 角色数量 | `project.roleCount` | 次要文字色，如"3个角色" |
| 申请数量 | `project.applyCount` | 次要文字色，如"12份申请" |
| 创建时间 | `project.createTime` | 次要文字色，格式化日期 |

**验收标准**:
- WHEN 渲染项目卡片 THEN 所有字段正确展示
- WHEN 项目状态为进行中（status=1） THEN 状态标签显示绿色"进行中"
- WHEN 项目状态为已结束（status=2） THEN 状态标签显示灰色"已结束"
- WHEN 点击项目卡片 THEN 展开内联角色列表或跳转到项目详情页

### 3.5 项目卡片交互

**描述**: 点击项目卡片后展开该项目下的角色列表（内联展开），点击角色项跳转到申请管理页。

**依赖**:
- `api/role.ts` → `getRolesByProject(projectId: number): Promise<PageResult<Role>>` (00-03-shared-utils-api §3.12)

**验收标准**:
- WHEN 点击项目卡片 THEN 展开显示该项目下的角色列表（调用 `getRolesByProject`）
- WHEN 再次点击已展开的项目卡片 THEN 收起角色列表
- WHEN 点击角色项 THEN 跳转到申请管理页 `/pages/apply-manage/index?roleId={roleId}`
- WHEN 项目下无角色 THEN 显示"暂无角色，去添加"提示

### 3.6 发布新项目

**描述**: 页面底部固定一个 Spotlight Orange 色的"＋ 发布新项目"按钮，点击跳转到项目创建页。

**依赖**:
- `KpButton` 组件 (00-02-shared-components §3.4)

**验收标准**:
- WHEN 页面渲染 THEN 底部固定显示橙色"＋ 发布新项目"按钮
- WHEN 点击发布按钮 THEN 跳转到 `/pages/project/create`
- WHEN 按钮位置 THEN 在 TabBar 上方，不被 TabBar 遮挡

### 3.7 空状态

**描述**: 当项目列表为空时，展示引导性空状态。

**依赖**:
- `KpEmpty` 组件 (00-02-shared-components §3.15)

**验收标准**:
- WHEN 项目列表为空 THEN 显示空状态插画 + "发布你的第一个项目"文字
- WHEN 空状态下 THEN 显示操作按钮"立即发布"，点击跳转到项目创建页

## 4. 非功能需求

> 通用非功能需求见 [SHARED_CONVENTIONS.md](../SHARED_CONVENTIONS.md)

- **性能**: 项目卡片展开角色列表时使用动画过渡（300ms）；列表单次渲染不超过 10 个 KpProjectCard。
- **体验**: 项目卡片展开/收起有平滑动画；发布按钮始终可见不被内容遮挡；从项目创建页返回后自动刷新列表。

## 5. 约束条件

> 通用约束见 [SHARED_CONVENTIONS.md](../SHARED_CONVENTIONS.md)

- 状态管理：Pinia `useUserStore` 判断用户角色
- API：通过 `api/project.ts` 的 `getMyProjects` 获取项目列表，`api/role.ts` 的 `getRolesByProject` 获取角色列表
- 页面路由：`pages/home/index`，Tab 页面，与演员视角共享路由
- 发布按钮颜色：Spotlight Orange `#FF6B35`
