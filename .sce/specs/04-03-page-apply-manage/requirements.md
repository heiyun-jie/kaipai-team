# 投递管理页（剧组端）

## 1. 概述

"开拍了"(KaiPai)小程序剧组端的投递管理页面，路径为 `pages/apply-manage/index`。剧组用户通过此页面查看某个角色收到的所有投递申请，并对演员进行审核（通过/拒绝）。页面通过 `roleId` 参数接收目标角色，展示该角色的投递列表，支持按状态筛选，提供快捷审核操作入口。

技术栈：uni-app 3.0 + Vue 3.4 + TypeScript + uview-plus + Pinia。

## 2. 用户故事

- 作为**剧组用户**，我希望查看某个角色收到的所有投递，以便了解报名情况。
- 作为**剧组用户**，我希望按状态（全部/待审核/通过/拒绝）筛选投递，以便快速定位需要处理的申请。
- 作为**剧组用户**，我希望在列表中看到演员的头像、姓名、性别、年龄、身高等摘要信息，以便初步判断是否合适。
- 作为**剧组用户**，我希望直接在列表中通过或拒绝投递，以便高效完成审核工作。
- 作为**剧组用户**，我希望点击"查看档案"跳转到演员详情页，以便查看演员完整资料后再做决定。

## 3. 功能需求

### 3.1 路由配置

**描述**: 在 `pages.json` 中注册页面路由 `pages/apply-manage/index`，页面通过 URL 参数 `roleId` 接收目标角色 ID。

**验收标准**:
- WHEN 从角色管理页跳转并携带 roleId 参数 THEN 页面正确接收并解析 roleId
- WHEN roleId 缺失 THEN 提示错误并返回上一页

### 3.2 投递列表加载

**描述**: 页面加载时根据 roleId 调用 `getAppliesByRole(roleId, params)` 获取投递列表，支持分页加载（下拉触底加载更多）。头部区域展示"投递管理"标题、角色名称、所属项目名称及投递总数。

**验收标准**:
- WHEN 页面 onLoad THEN 调用 API 获取第一页投递数据并渲染列表
- WHEN 头部区域渲染 THEN 显示"投递管理"标题、角色名称、项目名称、投递总数
- WHEN 滚动到底部 THEN 自动加载下一页数据并追加到列表
- WHEN 所有数据加载完毕 THEN 不再触发加载请求
- WHEN 列表为空 THEN 显示 KpEmpty 空状态组件

### 3.3 状态筛选

**描述**: 内容区域顶部提供 Tab 筛选栏，包含四个选项：全部、待审核、通过、拒绝，每个 Tab 显示对应数量。切换 Tab 时重新请求对应状态的数据。

**验收标准**:
- WHEN 页面加载 THEN 默认选中"全部"Tab
- WHEN 点击某个 Tab THEN 切换筛选状态，重新从第一页加载对应数据
- WHEN Tab 切换 THEN 各 Tab 旁显示对应状态的投递数量（如"待审核(5)"）
- WHEN 审核操作完成后 THEN Tab 数量实时更新

### 3.4 演员摘要展示

**描述**: 每张投递卡片展示演员的摘要信息，包括头像、姓名、性别、年龄、身高、自我介绍片段、备注信息。使用 KpActorBrief 组件或自定义卡片布局。

**验收标准**:
- WHEN 渲染投递卡片 THEN 显示演员头像（圆形）、姓名、性别、年龄、身高
- WHEN 演员有自我介绍 THEN 显示介绍文字片段（最多两行，超出省略）
- WHEN 投递有备注 THEN 在卡片中显示备注信息

### 3.5 审核通过操作

**描述**: 待审核状态的投递卡片显示"通过"按钮（primary 样式），点击后弹出 KpConfirmDialog 确认，确认后调用 `approveApply(applyId)` 更新状态，成功后刷新列表。

**验收标准**:
- WHEN 投递状态为待审核 THEN 卡片显示"通过"操作按钮
- WHEN 点击"通过"按钮 THEN 弹出确认对话框，内容为"确定通过该演员的投递吗？"
- WHEN 确认通过 THEN 调用 API 更新状态，成功后 toast 提示"已通过"并刷新列表
- WHEN API 调用失败 THEN 提示错误信息，列表状态不变

### 3.6 审核拒绝操作

**描述**: 待审核状态的投递卡片显示"拒绝"按钮（secondary 样式），点击后弹出 KpConfirmDialog 确认（danger 变体），确认后调用 `rejectApply(applyId)` 更新状态，成功后刷新列表。

**验收标准**:
- WHEN 投递状态为待审核 THEN 卡片显示"拒绝"操作按钮
- WHEN 点击"拒绝"按钮 THEN 弹出确认对话框（danger 样式），内容为"确定拒绝该演员的投递吗？"
- WHEN 确认拒绝 THEN 调用 API 更新状态，成功后 toast 提示"已拒绝"并刷新列表
- WHEN 投递状态为已通过或已拒绝 THEN 仅显示 KpStatusTag 状态标签，不显示操作按钮

### 3.7 查看演员档案

**描述**: 每张待审核投递卡片显示"查看档案"按钮，点击后跳转到演员详情查看页（actor-profile-detail），携带 actorId 参数。

**验收标准**:
- WHEN 投递状态为待审核 THEN 卡片显示"查看档案"按钮
- WHEN 点击"查看档案" THEN 跳转到 `/pages/actor-profile/detail?actorId={actorId}`
- WHEN 跳转成功 THEN 演员详情页正确加载对应演员资料

## 4. 非功能需求

> 通用非功能需求见 [SHARED_CONVENTIONS.md](../SHARED_CONVENTIONS.md)

- 列表分页加载，每页 10 条，滚动到底部自动加载

## 5. 约束条件

> 通用约束见 [SHARED_CONVENTIONS.md](../SHARED_CONVENTIONS.md)

- 依赖 API 层：参考 `00-03-shared-utils-api`（api/apply.ts, api/role.ts）
