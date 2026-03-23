# 我的页面

## 1. 概述

"开拍了"(KaiPai) 小程序的个人中心页面，路由路径 `pages/mine/index`，作为底部 TabBar 的第二个 Tab。该页面是用户的个人入口枢纽，根据用户角色（演员/剧组）展示不同的功能菜单。页面采用 Cinematic Glassmorphism 风格：深色头部展示用户头像、姓名、角色标签和脱敏手机号，白色内容区展示功能菜单列表，底部为毛玻璃 TabBar。

## 2. 用户故事

- 作为演员用户，我希望快速访问我的投递记录、个人档案等功能。
- 作为剧组用户，我希望快速访问投递管理、剧组资料等功能。
- 作为用户，我希望查看和编辑个人基本信息。
- 作为用户，我希望安全退出登录。

## 3. 功能需求

### 3.1 深色头部用户信息区

**描述**: 页面顶部深色区域展示用户基本信息：头像（圆形 120rpx）、姓名、角色标签（KpTag 显示"演员"或"剧组"）、脱敏手机号（formatPhone），右侧显示"编辑资料 →"入口。

**验收标准**:
- WHEN 页面加载 THEN 从 userStore 读取用户信息并展示头像、姓名、角色标签、脱敏手机号
- WHEN 用户为演员 THEN 角色标签显示"演员"，type 为 primary
- WHEN 用户为剧组 THEN 角色标签显示"剧组"，type 为 default
- WHEN 用户点击头像区域或"编辑资料 →" THEN 根据角色跳转到对应编辑页
- WHEN 用户为演员 THEN 跳转 pages/actor-profile/edit
- WHEN 用户为剧组 THEN 跳转 pages/company-profile/edit

### 3.2 演员功能菜单

**描述**: 当用户角色为演员时，白色内容区展示以下菜单项列表：我的投递、我的档案、关于我们、退出登录。每项包含图标、文字和右箭头。

**验收标准**:
- WHEN 用户为演员 THEN 显示菜单：我的投递、我的档案、关于我们、退出登录
- WHEN 点击"我的投递" THEN 跳转 pages/my-applies/index
- WHEN 点击"我的档案" THEN 跳转 pages/actor-profile/edit
- WHEN 点击"关于我们" THEN 跳转关于页面或显示关于信息

### 3.3 剧组功能菜单

**描述**: 当用户角色为剧组时，白色内容区展示以下菜单项列表：投递管理、剧组资料、关于我们、退出登录。

**验收标准**:
- WHEN 用户为剧组 THEN 显示菜单：投递管理、剧组资料、关于我们、退出登录
- WHEN 点击"投递管理" THEN 跳转 pages/apply-manage/index
- WHEN 点击"剧组资料" THEN 跳转 pages/company-profile/edit
- WHEN 点击"关于我们" THEN 跳转关于页面或显示关于信息

### 3.4 退出登录

**描述**: 点击"退出登录"菜单项，弹出 KpConfirmDialog 二次确认，确认后清除登录态并跳转到登录页。

**验收标准**:
- WHEN 点击"退出登录" THEN 弹出确认对话框，标题"提示"，内容"确定要退出登录吗？"
- WHEN 用户点击确认 THEN 调用 userStore.logout() 清除 token 和用户信息，reLaunch 到登录页
- WHEN 用户点击取消 THEN 关闭对话框，无操作

### 3.5 毛玻璃 TabBar

**描述**: 页面底部使用 KpTabBar 组件，毛玻璃风格，当前页面（我的）为激活态。

**验收标准**:
- WHEN 页面渲染 THEN 底部显示毛玻璃 TabBar，"我的"项为激活态（品牌橙色）
- WHEN 点击其他 Tab 项 THEN 切换到对应页面

## 4. 非功能需求

> 通用非功能需求见 [SHARED_CONVENTIONS.md](../SHARED_CONVENTIONS.md)

- 页面作为 Tab 页，需保持页面实例不销毁（使用 onShow 刷新数据）
- 退出登录操作需清除所有本地缓存（token、用户信息）
- 菜单列表支持后续扩展新菜单项

## 5. 约束条件

> 通用约束见 [SHARED_CONVENTIONS.md](../SHARED_CONVENTIONS.md)

- Store 依赖：`stores/user.ts`（userInfo, isActor, isCrew, logout）
- 组件依赖：KpPageLayout, KpTag, KpConfirmDialog, KpTabBar
- 工具依赖：`utils/format.ts` 的 formatPhone
- TabBar 配置：需在 pages.json 中配置自定义 TabBar
