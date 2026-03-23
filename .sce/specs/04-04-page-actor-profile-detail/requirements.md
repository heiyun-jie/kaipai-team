# 演员详情查看页（剧组端）

## 1. 概述

"开拍了"(KaiPai)小程序剧组端的演员详情查看页面，路径为 `pages/actor-profile/detail`。剧组用户从投递管理页跳转至此页面，查看演员的完整个人资料，包括基本信息、擅长类型、自我介绍、个人照片和视频简历。页面通过 `actorId` 参数接收目标演员 ID。

技术栈：uni-app 3.0 + Vue 3.4 + TypeScript + uview-plus + Pinia。

## 2. 用户故事

- 作为**剧组用户**，我希望查看演员的完整资料（照片、视频、介绍），以便全面评估演员是否适合角色。
- 作为**剧组用户**，我希望点击照片可以全屏预览并左右滑动，以便仔细查看演员形象。
- 作为**剧组用户**，我希望点击视频可以全屏播放，以便评估演员的表演能力。

## 3. 功能需求

### 3.1 路由配置

**描述**: 在 `pages.json` 中注册页面路由 `pages/actor-profile/detail`，页面通过 URL 参数 `actorId` 接收目标演员 ID。

**验收标准**:
- WHEN 从投递管理页跳转并携带 actorId 参数 THEN 页面正确接收并解析 actorId
- WHEN actorId 缺失 THEN 提示错误并返回上一页

### 3.2 基本信息展示

**描述**: 深色头部区域展示演员核心信息：大圆形头像、姓名、性别/年龄/身高组合文字（如"女 · 22岁 · 168cm"）、所在城市。调用 `getActorDetail(actorId)` 获取数据。

**验收标准**:
- WHEN 页面加载 THEN 调用 API 获取演员详情数据
- WHEN 数据返回 THEN 头部显示大圆形头像（居中）、姓名、"性别 · 年龄岁 · 身高cm"、城市
- WHEN 头像加载失败 THEN 显示默认占位头像
- WHEN API 请求失败 THEN 提示错误信息

### 3.3 擅长类型展示

**描述**: 浅色内容区域第一个 Section，标题"擅长类型"，使用 KpTag 组件以标签形式展示演员的技能类型列表。

**验收标准**:
- WHEN 演员有擅长类型数据 THEN 以 KpTag 标签形式横向排列展示
- WHEN 演员无擅长类型数据 THEN 隐藏该 Section 或显示"暂无"

### 3.4 自我介绍展示

**描述**: Section 标题"自我介绍"，展示演员的自我介绍文本，支持多行显示。

**验收标准**:
- WHEN 演员有自我介绍 THEN 完整显示介绍文本
- WHEN 演员无自我介绍 THEN 隐藏该 Section 或显示"暂无"

### 3.5 照片墙展示

**描述**: Section 标题"个人照片"，以九宫格形式展示演员的个人照片列表。点击任意照片调用 `uni.previewImage` 进入全屏预览模式，支持左右滑动切换。

**验收标准**:
- WHEN 演员有照片 THEN 以九宫格布局展示照片缩略图
- WHEN 点击某张照片 THEN 调用 uni.previewImage 全屏预览，当前照片为初始图
- WHEN 全屏预览中 THEN 支持左右滑动切换照片
- WHEN 演员无照片 THEN 隐藏该 Section 或显示"暂无"

### 3.6 视频简历播放

**描述**: Section 标题"视频简历"，以 16:9 比例展示视频播放器。点击播放按钮或视频区域进入全屏播放。

**验收标准**:
- WHEN 演员有视频简历 THEN 显示 16:9 视频播放器，带封面图和播放按钮
- WHEN 点击播放 THEN 视频开始播放，支持全屏切换
- WHEN 演员无视频简历 THEN 隐藏该 Section 或显示"暂无"

## 4. 非功能需求

> 通用非功能需求见 [SHARED_CONVENTIONS.md](../SHARED_CONVENTIONS.md)

- 照片使用缩略图加载，全屏预览时加载原图
- 视频播放器支持暂停、进度拖拽、全屏切换

## 5. 约束条件

> 通用约束见 [SHARED_CONVENTIONS.md](../SHARED_CONVENTIONS.md)

- 依赖 API 层：参考 `00-03-shared-utils-api`（api/actor.ts）
