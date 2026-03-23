# 新建项目页

## 1. 概述

"开拍了"(KaiPai)小程序新建项目页面，路由为 `pages/project/create`，供剧组用户创建新的拍摄项目。页面采用 Cinematic Glassmorphism 设计语言：深色头部（标题"发布项目"）+ 白色内容区（表单）+ 固定底部发布按钮。

## 2. 用户故事

- 作为剧组用户，我希望填写项目名称、拍摄地点和项目简介来创建一个新项目，以便后续为项目添加角色需求。
- 作为剧组用户，我希望表单有清晰的必填提示和校验反馈，以便我不会遗漏关键信息。
- 作为剧组用户，我希望发布成功后自动跳转到剧组首页并收到提示，以便我知道下一步该添加角色。

## 3. 功能需求

### 3.1 路由配置

**描述**: 页面注册路径为 `pages/project/create`，非 Tab 页面，需要登录且角色为剧组（`user.role === 2`）才可访问。导航栏标题"发布项目"，显示返回按钮。

**依赖**:
- `stores/user.ts` → `useUserStore` (00-03-shared-utils-api §3.7)
- `KpPageLayout` 组件 (00-02-shared-components §3.1)
- `KpNavBar` 组件 (00-02-shared-components §3.2)

**验收标准**:
- WHEN 剧组用户进入页面 THEN 显示深色头部 + "发布项目"标题 + 返回按钮
- WHEN 非剧组用户尝试访问 THEN 重定向到首页
- WHEN 点击返回按钮 THEN 调用 `navigateBack` 返回上一页

### 3.2 项目名称输入

**描述**: 白色内容区第一个表单项，标签"项目名称"，必填，最大长度 50 字符，placeholder"请输入项目名称"。

**依赖**:
- `KpFormItem` 组件 (00-02-shared-components §3.8)
- `KpInput` 组件 (00-02-shared-components §3.6)

**验收标准**:
- WHEN 页面渲染 THEN 显示带红色星号的"项目名称"标签和输入框
- WHEN 用户输入文字 THEN 通过 v-model 双向绑定到 `form.title`
- WHEN 输入超过 50 字符 THEN 阻止继续输入

### 3.3 拍摄地点选择

**描述**: 第二个表单项，标签"拍摄地点"，必填，使用城市选择器（uni.chooseLocation 或自定义 picker），placeholder"请选择拍摄城市"。

**依赖**:
- `KpFormItem` 组件 (00-02-shared-components §3.8)
- `KpInput` 组件 (00-02-shared-components §3.6)

**验收标准**:
- WHEN 页面渲染 THEN 显示带红色星号的"拍摄地点"标签和选择器
- WHEN 用户点击输入框 THEN 弹出城市选择器
- WHEN 选择城市后 THEN 输入框显示所选城市名称，绑定到 `form.location`

### 3.4 项目简介输入

**描述**: 第三个表单项，标签"项目简介"，可选，多行文本输入，最大长度 500 字符，显示字数统计，placeholder"请输入项目简介（选填）"。

**依赖**:
- `KpFormItem` 组件 (00-02-shared-components §3.8)
- `KpTextarea` 组件 (00-02-shared-components §3.7)

**验收标准**:
- WHEN 页面渲染 THEN 显示"项目简介"标签和多行输入框
- WHEN 用户输入文字 THEN 右下角显示字数统计（当前/500）
- WHEN 输入超过 500 字符 THEN 阻止继续输入
- WHEN 用户不填写 THEN 不影响表单提交

### 3.5 表单校验与发布

**描述**: 页面底部固定"发布项目"按钮（KpButton primary block），点击时校验必填字段，校验通过后调用 `createProject` API 提交数据。提交成功后跳转到剧组首页并显示 toast 提示。

**依赖**:
- `KpButton` 组件 (00-02-shared-components §3.4)
- `api/project.ts` → `createProject` (00-03-shared-utils-api §3.11)
- `utils/validate.ts` → `requiredRule` (00-03-shared-utils-api §3.6)

**验收标准**:
- WHEN 必填字段未填写且点击发布 THEN 对应表单项显示红色错误提示
- WHEN 项目名称为空 THEN 提示"请输入项目名称"
- WHEN 拍摄地点为空 THEN 提示"请选择拍摄地点"
- WHEN 校验通过且点击发布 THEN 按钮显示 loading 状态，调用 `createProject({ title, location, description })`
- WHEN 发布成功 THEN 跳转到剧组首页（`switchTab` 到 `pages/home/index`），toast 提示"发布成功，去添加角色吧"
- WHEN 发布失败 THEN 显示错误提示，按钮恢复可点击状态
- WHEN 正在提交中 THEN 按钮禁用，防止重复提交

## 4. 非功能需求

> 通用非功能需求见 [SHARED_CONVENTIONS.md](../SHARED_CONVENTIONS.md)

- **体验**: 表单校验即时反馈；提交成功有明确的 toast 提示和页面跳转。

## 5. 约束条件

> 通用约束见 [SHARED_CONVENTIONS.md](../SHARED_CONVENTIONS.md)

- 状态管理：Pinia `useUserStore` 判断用户角色
- API：通过 `api/project.ts` 的 `createProject` 提交数据
- 页面路由：`pages/project/create`，非 Tab 页面，支持 `navigateBack`
