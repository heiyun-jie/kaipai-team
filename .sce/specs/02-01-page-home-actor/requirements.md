# 首页 - 演员视角

## 1. 概述

"开拍了"(KaiPai)小程序首页演员视角页面，路由为 `pages/home/index`（Tab 1），当 `user.role === 1`（演员）时展示。页面以"通告流"形式呈现所有正在招募的角色列表，演员可通过搜索和多维筛选快速定位目标角色，点击卡片进入角色详情页。

页面采用 Cinematic Glassmorphism 设计语言：深色沉浸式头部（搜索栏 + 筛选标签）+ 白色内容区（圆角上移重叠 -40rpx）+ 毛玻璃底部 TabBar。

## 2. 用户故事

- 作为演员，我希望打开首页就能看到最新的招募角色列表，以便快速浏览通告信息。
- 作为演员，我希望通过性别、年龄、地区、报酬等条件筛选角色，以便找到适合自己的通告。
- 作为演员，我希望通过关键词搜索角色，以便精准定位目标角色。
- 作为演员，我希望下拉刷新获取最新通告，上拉加载更多历史通告，以便持续浏览。
- 作为演员，我希望点击角色卡片进入详情页，以便查看完整的角色要求和项目信息。

## 3. 功能需求

### 3.1 页面路由与 TabBar 配置

**描述**: 页面注册为 Tab 页面，路径 `pages/home/index`，在 `pages.json` 中配置为 TabBar 第一项（"首页"）。页面 `onShow` 时根据 `useUserStore().isActor` 判断是否展示演员视角，若为剧组角色则展示剧组视角（见 02-02-page-home-crew）。

**依赖**:
- `stores/user.ts` → `useUserStore` (00-03-shared-utils-api)
- `KpTabBar` 组件 (00-02-shared-components §3.17)

**验收标准**:
- WHEN 演员用户进入首页 THEN 展示演员视角（角色列表 + 搜索 + 筛选）
- WHEN 剧组用户进入首页 THEN 展示剧组视角（项目列表）
- WHEN 底部 TabBar 渲染 THEN 显示"首页"和"我的"两个导航项，"首页"高亮
- WHEN 点击 TabBar "我的" THEN 跳转到我的页面

### 3.2 角色列表加载（分页）

**描述**: 页面加载时调用 `searchRoles` API 获取角色列表，默认按发布时间倒序，每页 10 条。滚动到底部时自动加载下一页，直到无更多数据。

**依赖**:
- `api/role.ts` → `searchRoles(params: RoleSearchParams): Promise<PageResult<Role>>` (00-03-shared-utils-api §3.12)
- `types/role.ts` → `Role`, `RoleSearchParams` (00-03-shared-utils-api §3.1)
- `types/common.ts` → `PageResult`, `PageParams` (00-03-shared-utils-api §3.1)

**验收标准**:
- WHEN 页面首次加载 THEN 调用 `searchRoles({ page: 1, size: 10 })` 获取第一页数据
- WHEN 滚动到底部且还有更多数据 THEN 自动加载下一页并追加到列表
- WHEN 滚动到底部且无更多数据 THEN 显示"没有更多了"提示
- WHEN 加载中 THEN 底部显示加载指示器，防止重复请求
- WHEN API 请求失败 THEN 显示错误提示，支持重试

### 3.3 下拉刷新

**描述**: 支持 uni-app `onPullDownRefresh` 下拉刷新，重置分页参数并重新加载第一页数据。

**验收标准**:
- WHEN 用户下拉刷新 THEN 重置 page 为 1，清空现有列表，重新请求第一页
- WHEN 刷新完成 THEN 调用 `uni.stopPullDownRefresh()` 停止刷新动画
- WHEN 刷新期间有筛选条件 THEN 保留当前筛选条件刷新

### 3.4 搜索功能

**描述**: 深色头部区域包含半透明搜索输入框，用户输入关键词后 300ms 防抖触发搜索，将 `keyword` 参数传入 `searchRoles` API。

**验收标准**:
- WHEN 用户在搜索框输入文字 THEN 300ms 防抖后触发搜索请求
- WHEN 搜索关键词变化 THEN 重置分页为第 1 页，重新加载列表
- WHEN 清空搜索框 THEN 恢复无关键词的默认列表
- WHEN 搜索无结果 THEN 显示搜索类型空状态（KpEmpty type="search"）

### 3.5 筛选功能

**描述**: 搜索栏下方展示轻量筛选标签行：[性别▼] [年龄▼] [地区▼] [报酬▼]。点击标签弹出下拉选择器，支持组合筛选。

**依赖**:
- `KpFilterBar` 组件 (00-02-shared-components §3.16)

**筛选项配置**:

| 筛选维度 | key | type | 选项 |
|---------|-----|------|------|
| 性别 | gender | single | 不限 / 男 / 女 |
| 年龄 | age | single | 不限 / 18-25 / 25-35 / 35+ |
| 地区 | city | single | 城市选择器 |
| 报酬 | fee | single | 不限 / 面议 / 300以下 / 300-800 / 800+ |

**验收标准**:
- WHEN 点击筛选标签 THEN 展开对应下拉选择面板
- WHEN 选择筛选值 THEN 标签高亮为品牌色，重置分页并重新加载列表
- WHEN 多个筛选条件同时激活 THEN 组合传参给 `searchRoles` API
- WHEN 再次点击已选中的筛选值 THEN 取消该筛选条件
- WHEN 筛选结果为空 THEN 显示空状态

### 3.6 角色卡片展示

**描述**: 列表中每个角色以 `KpRoleCard` 组件展示，卡片内包含角色核心信息。

**依赖**:
- `KpRoleCard` 组件 (00-02-shared-components §3.11)
- `utils/format.ts` → `formatFee`, `formatAge` (00-03-shared-utils-api §3.5)

**卡片字段映射**:

| 展示字段 | 数据来源 | 样式说明 |
|---------|---------|---------|
| 角色名称 | `role.roleName` | 主标题，加粗 |
| 报酬 | `role.fee` | 橙色高亮，Display 字重 |
| 所属项目 | `role.projectName` | 次要文字色 |
| 拍摄地点 | `role.location` | 次要文字色 + 定位图标 |
| 性别+年龄 | `role.gender` + `role.minAge`-`role.maxAge` | 标签形式 |
| 公司名称 | `role.companyName` | 次要文字色 |
| 发布时间 | `role.publishTime` | 相对时间（如"2小时前"） |

**验收标准**:
- WHEN 渲染角色卡片 THEN 所有字段正确展示，报酬为橙色高亮
- WHEN 点击角色卡片 THEN 跳转到角色详情页 `/pages/role-detail/index?id={roleId}`

### 3.7 空状态

**描述**: 当角色列表为空时，展示空状态占位组件。

**依赖**:
- `KpEmpty` 组件 (00-02-shared-components §3.15)

**验收标准**:
- WHEN 首次加载列表为空（无筛选） THEN 显示默认空状态（KpEmpty type="default" text="暂无通告"）
- WHEN 搜索结果为空 THEN 显示搜索空状态（KpEmpty type="search" text="未找到相关角色"）
- WHEN 筛选结果为空 THEN 显示默认空状态（KpEmpty text="暂无符合条件的角色"）

## 4. 非功能需求

> 通用非功能需求见 [SHARED_CONVENTIONS.md](../SHARED_CONVENTIONS.md)

- **性能**: 列表单次渲染不超过 10 个 KpRoleCard；搜索防抖 300ms 避免频繁请求。
- **兼容性**: 深色头部区域需适配状态栏高度。
- **体验**: 页面切换保留滚动位置和筛选状态。

## 5. 约束条件

> 通用约束见 [SHARED_CONVENTIONS.md](../SHARED_CONVENTIONS.md)

- 状态管理：Pinia `useUserStore` 判断用户角色
- API：通过 `api/role.ts` 的 `searchRoles` 获取数据
- 页面路由：`pages/home/index`，Tab 页面，不可使用 `navigateBack`
