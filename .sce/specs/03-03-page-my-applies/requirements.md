# 我的投递页（演员端）

## 1. 概述

"开拍了"(KaiPai) 小程序的演员投递记录页面，路由路径 `pages/my-applies/index`。演员用户查看自己所有的投递记录，支持按状态筛选（全部/待审核/已通过/已拒绝），以卡片列表形式展示每条投递的角色名称、项目信息、费用、状态和时间。已通过的投递额外显示剧组联系方式。页面采用 Cinematic Glassmorphism 风格：深色头部展示页面标题"我的投递"，浅色内容区包含 Tab 筛选栏和投递卡片列表。

## 2. 用户故事

- 作为演员用户，我希望查看自己所有的投递记录，以便了解投递进度。
- 作为演员用户，我希望按状态筛选投递记录（待审核/已通过/已拒绝），以便快速定位关注的投递。
- 作为演员用户，我希望在投递通过后看到剧组联系方式，以便主动联系剧组。
- 作为演员用户，我希望点击投递卡片进入角色详情页，以便回顾角色要求。
- 作为演员用户，我希望在没有投递记录时看到引导提示，以便快速前往浏览角色。

## 3. 功能需求

### 3.1 路由配置

**描述**: 在 `pages.json` 中注册我的投递页路由，配置为非 Tab 页面，导航栏样式为自定义（`navigationStyle: custom`），背景色 `#121214`。

**验收标准**:
- WHEN 演员用户从"我的"页面点击"我的投递" THEN 跳转到 `/pages/my-applies/index`
- WHEN 页面加载 THEN 系统导航栏隐藏，使用自定义全屏布局
- WHEN 页面背景 THEN 深色头部为 `$kp-color-dark-primary`，内容区为 `$kp-color-bg`

### 3.2 投递列表加载

**描述**: 页面加载时调用 `getMyApplies` API 获取当前演员的投递记录列表，默认按投递时间倒序，每页 10 条。支持上拉加载更多和下拉刷新。

**依赖**:
- `api/apply.ts` → `getMyApplies(params: ApplySearchParams): Promise<PageResult<Apply>>` (00-03-shared-utils-api §3.13)
- `types/apply.ts` → `Apply`, `ApplySearchParams`, `ApplyStatus` (00-03-shared-utils-api §3.1)
- `types/common.ts` → `PageResult`, `PageParams` (00-03-shared-utils-api §3.1)

**验收标准**:
- WHEN 页面首次加载 THEN 调用 `getMyApplies({ page: 1, size: 10 })` 获取第一页数据
- WHEN 滚动到底部且还有更多数据 THEN 自动加载下一页并追加到列表
- WHEN 滚动到底部且无更多数据 THEN 显示"没有更多了"提示
- WHEN 加载中 THEN 底部显示加载指示器，防止重复请求
- WHEN 下拉刷新 THEN 重置 page 为 1，清空列表，重新请求第一页
- WHEN API 请求失败 THEN 显示错误提示，支持重试

### 3.3 状态筛选

**描述**: 内容区顶部展示 Tab 筛选栏，包含四个选项：[全部] [待审核] [已通过] [已拒绝]。切换 Tab 时按对应状态重新加载列表。

**验收标准**:
- WHEN 页面加载 THEN 默认选中"全部"Tab
- WHEN 点击"待审核"Tab THEN 调用 `getMyApplies({ status: 1, page: 1, size: 10 })` 筛选待审核记录
- WHEN 点击"已通过"Tab THEN 调用 `getMyApplies({ status: 2, page: 1, size: 10 })` 筛选已通过记录
- WHEN 点击"已拒绝"Tab THEN 调用 `getMyApplies({ status: 3, page: 1, size: 10 })` 筛选已拒绝记录
- WHEN 点击"全部"Tab THEN 调用 `getMyApplies({ page: 1, size: 10 })` 不传 status 参数
- WHEN 切换 Tab THEN 重置分页为第 1 页，清空当前列表，重新加载
- WHEN 当前 Tab 已选中再次点击 THEN 不触发重复请求

### 3.4 投递卡片展示

**描述**: 列表中每条投递记录以 `KpApplyCard` 组件展示（viewMode="actor"），卡片内包含角色名称、状态标签、项目名称、公司名称、费用、投递时间。

**依赖**:
- `KpApplyCard` 组件 (00-02-shared-components §3.13)
- `KpStatusTag` 组件 (00-02-shared-components §3.18)
- `utils/format.ts` → `formatApplyStatus`, `formatFee`, `formatDate` (00-03-shared-utils-api §3.5)

**卡片字段映射**:

| 展示字段 | 数据来源 | 样式说明 |
|---------|---------|---------|
| 角色名称 | `apply.roleName` | 主标题，加粗 |
| 状态标签 | `apply.status` | 待审核=warning(黄), 已通过=success(绿), 已拒绝=danger(红/灰) |
| 项目名称 | `apply.projectName` | 次要文字色 |
| 公司名称 | `apply.companyName` | 次要文字色 |
| 费用 | `apply.fee` | 橙色高亮，使用 formatFee |
| 投递时间 | `apply.applyTime` | 次要文字色，使用 formatDate |

**验收标准**:
- WHEN 渲染投递卡片 THEN 所有字段正确展示，状态标签颜色与状态对应
- WHEN 点击投递卡片 THEN 跳转到角色详情页 `/pages/role-detail/index?id={roleId}`

### 3.5 通过后显示联系方式

**描述**: 当投递状态为"已通过"（status === 2）时，卡片底部额外显示剧组联系人姓名和联系电话（完整显示，不脱敏），方便演员主动联系剧组。

**验收标准**:
- WHEN 投递状态为"已通过" THEN 卡片底部显示联系人姓名（contact_name）和联系电话（contact_phone）
- WHEN 投递状态为"待审核"或"已拒绝" THEN 不显示联系方式区域
- WHEN 点击联系电话 THEN 调用 `uni.makePhoneCall` 拨打电话

### 3.6 空状态

**描述**: 当投递列表为空时，展示空状态占位组件，包含引导按钮跳转到首页浏览角色。

**依赖**:
- `KpEmpty` 组件 (00-02-shared-components §3.15)

**验收标准**:
- WHEN 全部 Tab 下列表为空 THEN 显示空状态（KpEmpty type="apply" text="暂无投递记录"）
- WHEN 空状态 THEN 显示引导按钮"去看看有什么角色 →"
- WHEN 点击引导按钮 THEN 跳转到首页 `/pages/home/index`（使用 `switchTab`）
- WHEN 筛选 Tab 下列表为空 THEN 显示空状态（KpEmpty text="暂无该状态的投递"），不显示引导按钮

## 4. 非功能需求

> 通用非功能需求见 [SHARED_CONVENTIONS.md](../SHARED_CONVENTIONS.md)

- 列表单次渲染不超过 10 个 KpApplyCard；上拉加载有明确视觉反馈
- Tab 筛选栏支持 aria-selected 状态；投递卡片支持 aria-label 描述角色名称和状态
- 列表滚动流畅；Tab 切换保留滚动位置；下拉刷新和上拉加载有明确视觉反馈

## 5. 约束条件

> 通用约束见 [SHARED_CONVENTIONS.md](../SHARED_CONVENTIONS.md)

- API：通过 `api/apply.ts` 的 `getMyApplies` 获取数据（00-03-shared-utils-api §3.13）
- 组件依赖：KpPageLayout, KpNavBar, KpApplyCard, KpStatusTag, KpEmpty（00-02-shared-components）
- 工具依赖：`utils/format.ts` 的 formatApplyStatus, formatFee, formatDate（00-03-shared-utils-api §3.5）
- 页面为非 Tab 页，使用自定义导航栏（`navigationStyle: custom`）
