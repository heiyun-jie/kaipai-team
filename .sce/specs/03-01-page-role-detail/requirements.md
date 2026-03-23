# 角色详情页

## 1. 概述

"开拍了"(KaiPai) 小程序的角色详情页面，路由路径 `pages/role-detail/index`。演员用户从首页角色列表点击进入，查看角色完整信息（角色要求、项目信息、剧组信息、截止日期），并决定是否投递申请。页面采用 Cinematic Glassmorphism 风格：深色头部展示角色名称与片酬，浅色内容区分段展示详细信息，底部固定投递操作按钮。

## 2. 用户故事

- 作为演员用户，我希望查看角色的完整要求（性别、年龄、身高、描述），以判断自己是否符合条件。
- 作为演员用户，我希望了解项目和剧组的基本信息，以评估项目可靠性。
- 作为演员用户，我希望一键投递申请，流程简洁高效。
- 作为演员用户，我希望看到投递状态和截止时间，避免重复投递或错过截止日期。

## 3. 功能需求

### 3.1 深色头部区域

**描述**: 页面顶部深色区域展示角色核心信息——角色名称（H1 白色）和片酬（Display 48rpx 品牌橙色 #FF6B35）。包含 KpNavBar 导航栏（返回按钮 + 标题"角色详情"）。

**验收标准**:
- WHEN 页面加载完成 THEN 深色头部显示角色名称（白色 H1）和片酬（48rpx 橙色）
- WHEN 片酬数据存在 THEN 以 `¥{fee}` 格式展示，使用 formatFee 格式化
- WHEN 用户点击导航栏返回按钮 THEN 返回上一页

### 3.2 角色要求区块

**描述**: 白色内容区第一个区块，标题"角色要求"，展示性别、年龄范围、身高范围、角色要求描述文本。使用 KpCard 容器。

**验收标准**:
- WHEN 数据加载完成 THEN 显示性别（formatGender）、年龄范围（formatAge）、身高范围、要求描述
- WHEN 某字段为空 THEN 显示"不限"或隐藏该行
- WHEN 要求描述文本过长 THEN 完整展示，不截断

### 3.3 项目信息区块

**描述**: 展示角色所属项目的基本信息，包括项目名称、拍摄地点、项目描述。使用 KpCard 容器。

**验收标准**:
- WHEN 数据加载完成 THEN 显示项目名称、拍摄地点、项目描述
- WHEN 项目描述过长 THEN 完整展示

### 3.4 剧组信息区块

**描述**: 展示发布该角色的剧组/公司信息，包括公司名称、联系人姓名、联系电话（脱敏显示 138****1234）。

**验收标准**:
- WHEN 数据加载完成 THEN 显示公司名称、联系人姓名
- WHEN 用户未投递或投递未通过 THEN 联系电话脱敏显示（formatPhone）
- WHEN 用户投递已通过 THEN 显示完整联系电话

### 3.5 截止日期展示

**描述**: 在内容区底部展示角色投递截止日期，使用 formatDate 格式化。

**验收标准**:
- WHEN 截止日期存在 THEN 以"截止日期：YYYY-MM-DD"格式展示
- WHEN 已过截止日期 THEN 文字标红提示"已截止"

### 3.6 底部投递操作按钮

**描述**: 页面底部固定区域放置投递操作按钮，根据投递状态和截止日期显示不同状态。使用 KpButton 组件。

**验收标准**:
- WHEN 用户未投递且未截止 THEN 显示橙色"立即投递"按钮，点击跳转至投递确认页
- WHEN 用户已投递 THEN 按钮变为灰色禁用态，文字为"已投递"
- WHEN 已过截止日期 THEN 按钮变为灰色禁用态，文字为"已截止"
- WHEN 点击"立即投递" THEN 携带 roleId 跳转到 pages/apply-confirm/index

## 4. 非功能需求

> 通用非功能需求见 [SHARED_CONVENTIONS.md](../SHARED_CONVENTIONS.md)

- 接口请求期间显示 loading 状态
- 接口请求失败时显示错误提示并支持重试
- 页面支持下拉刷新

## 5. 约束条件

> 通用约束见 [SHARED_CONVENTIONS.md](../SHARED_CONVENTIONS.md)

- API 依赖：`api/role.ts` 的 `getRole(id)`、`api/apply.ts` 的 `getMyApplies()`
- 组件依赖：KpPageLayout, KpNavBar, KpCard, KpButton, KpTag
- 工具依赖：`utils/format.ts` 的 formatFee, formatGender, formatAge, formatPhone, formatDate
