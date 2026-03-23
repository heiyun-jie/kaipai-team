# 投递确认页

## 1. 概述

"开拍了"(KaiPai) 小程序的投递确认页面，路由路径 `pages/apply-confirm/index`。演员用户从角色详情页点击"立即投递"后进入，确认投递信息（角色摘要、个人档案预览），可添加备注，提交投递申请。页面采用 Cinematic Glassmorphism 风格：深色头部显示"确认投递"标题，白色内容区展示角色摘要卡片和演员简要信息卡片。

## 2. 用户故事

- 作为演员用户，我希望在投递前确认角色信息和自己的档案信息，避免误投。
- 作为演员用户，我希望添加备注说明自己的优势或特殊情况。
- 作为演员用户，我希望在档案不完整时得到提醒并快速跳转编辑。
- 作为演员用户，我希望投递成功后自动返回角色详情页并看到状态更新。

## 3. 功能需求

### 3.1 深色头部区域

**描述**: 页面顶部深色区域，KpNavBar 显示标题"确认投递"和返回按钮。

**验收标准**:
- WHEN 页面加载 THEN 导航栏显示"确认投递"标题
- WHEN 用户点击返回 THEN 返回角色详情页

### 3.2 角色摘要卡片

**描述**: 白色内容区顶部展示角色摘要信息，包括角色名称、所属项目名称、剧组公司名称。使用 KpCard 容器，只读展示。

**验收标准**:
- WHEN 页面加载完成 THEN 显示角色名称、项目名称、公司名称
- WHEN 数据加载中 THEN 显示骨架屏或 loading 状态

### 3.3 演员档案预览卡片

**描述**: 使用 KpActorBrief 组件展示当前用户的演员档案预览（头像、姓名、性别、年龄、身高、简介片段），右侧或底部显示"查看/编辑档案 →"链接。

**验收标准**:
- WHEN 用户档案完整 THEN 显示头像、姓名、性别、年龄、身高、简介摘要
- WHEN 用户点击"查看/编辑档案 →" THEN 跳转到 pages/actor-profile/edit
- WHEN 用户档案不完整（缺少姓名、性别、年龄等必填项） THEN 显示 toast 警告"请先完善个人档案"，自动跳转到编辑页

### 3.4 备注输入区域

**描述**: 提供 KpTextarea 组件供用户输入可选备注信息，最大 200 字，显示字数统计。

**验收标准**:
- WHEN 用户输入备注 THEN 实时显示字数统计（当前/200）
- WHEN 输入超过 200 字 THEN 阻止继续输入
- WHEN 备注为空 THEN 允许提交（备注为可选项）

### 3.5 确认投递按钮

**描述**: 页面底部固定区域放置"确认投递"按钮，使用 KpButton primary 变体。点击后提交投递申请。

**验收标准**:
- WHEN 用户点击"确认投递" THEN 按钮进入 loading 状态，调用 createApply API
- WHEN 投递成功 THEN 显示成功 toast，navigateBack 返回角色详情页
- WHEN 返回角色详情页后 THEN 底部按钮变为"已投递"禁用态
- WHEN 投递失败 THEN 显示错误提示，按钮恢复可点击状态
- WHEN 按钮 loading 中 THEN 禁止重复点击

## 4. 非功能需求

> 通用非功能需求见 [SHARED_CONVENTIONS.md](../SHARED_CONVENTIONS.md)

- 提交操作需防抖，避免重复投递
- 接口请求期间按钮显示 loading 动画
- 页面加载时并行请求角色信息和用户档案信息

## 5. 约束条件

> 通用约束见 [SHARED_CONVENTIONS.md](../SHARED_CONVENTIONS.md)

- API 依赖：`api/apply.ts` 的 `submitApply(roleId, remark)`、`api/role.ts` 的 `getRole(id)`、`api/actor.ts` 的 `getActorProfile(userId)`
- 组件依赖：KpPageLayout, KpNavBar, KpCard, KpActorBrief, KpTextarea, KpButton
- Store 依赖：`stores/user.ts` 获取当前用户 ID
- 页面参数：通过 URL query 接收 `roleId`
