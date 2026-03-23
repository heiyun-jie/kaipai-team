# 新建角色页

## 1. 概述

"开拍了"(KaiPai)小程序新建角色页面，路由为 `pages/project/role-create`，供剧组用户在指定项目下创建角色招募需求。页面通过 query 参数 `projectId` 接收所属项目 ID。采用 Cinematic Glassmorphism 设计语言：深色头部（标题"发布角色"）+ 白色内容区（表单）+ 固定底部发布按钮。

## 2. 用户故事

- 作为剧组用户，我希望为项目添加角色需求，填写角色名称、性别要求、年龄范围、报酬、角色描述和截止时间，以便演员能看到完整的招募信息。
- 作为剧组用户，我希望通过标签单选快速设置性别要求，以便高效填写表单。
- 作为剧组用户，我希望发布成功后返回上一页并收到提示，以便我知道角色已发布。

## 3. 功能需求

### 3.1 路由配置

**描述**: 页面注册路径为 `pages/project/role-create`，非 Tab 页面，需要登录且角色为剧组（`user.role === 2`）才可访问。通过 query 参数 `projectId` 接收所属项目 ID。导航栏标题"发布角色"，显示返回按钮。

**依赖**:
- `stores/user.ts` → `useUserStore` (00-03-shared-utils-api §3.7)
- `KpPageLayout` 组件 (00-02-shared-components §3.1)
- `KpNavBar` 组件 (00-02-shared-components §3.2)

**验收标准**:
- WHEN 剧组用户携带 `projectId` 进入页面 THEN 显示深色头部 + "发布角色"标题 + 返回按钮
- WHEN 缺少 `projectId` 参数 THEN 提示错误并返回上一页
- WHEN 非剧组用户尝试访问 THEN 重定向到首页
- WHEN 点击返回按钮 THEN 调用 `navigateBack` 返回上一页

### 3.2 角色名称输入

**描述**: 白色内容区第一个表单项，标签"角色名称"，必填，placeholder"请输入角色名称"。

**依赖**:
- `KpFormItem` 组件 (00-02-shared-components §3.8)
- `KpInput` 组件 (00-02-shared-components §3.6)

**验收标准**:
- WHEN 页面渲染 THEN 显示带红色星号的"角色名称"标签和输入框
- WHEN 用户输入文字 THEN 通过 v-model 双向绑定到 `form.roleName`

### 3.3 性别要求选择

**描述**: 第二个表单项，标签"性别要求"，必填，以三个标签按钮形式呈现：[不限] [男] [女]，单选模式，默认选中"不限"。

**依赖**:
- `KpFormItem` 组件 (00-02-shared-components §3.8)
- `KpTag` 组件 (00-02-shared-components §3.5)

**验收标准**:
- WHEN 页面渲染 THEN 显示带红色星号的"性别要求"标签和三个标签按钮，"不限"默认选中
- WHEN 用户点击某个标签 THEN 该标签高亮（selected），其他标签取消选中
- WHEN 选中"不限" THEN `form.gender` 绑定为 `"不限"`
- WHEN 选中"男" THEN `form.gender` 绑定为 `"男"`
- WHEN 选中"女" THEN `form.gender` 绑定为 `"女"`

### 3.4 年龄范围选择

**描述**: 第三个表单项，标签"年龄范围"，可选，由两个 picker 组成（最小年龄 — 最大年龄），范围 1-120。

**依赖**:
- `KpFormItem` 组件 (00-02-shared-components §3.8)

**验收标准**:
- WHEN 页面渲染 THEN 显示"年龄范围"标签和两个 picker（最小年龄、最大年龄）
- WHEN 用户选择最小年龄 THEN 绑定到 `form.minAge`
- WHEN 用户选择最大年龄 THEN 绑定到 `form.maxAge`
- WHEN 最小年龄大于最大年龄 THEN 自动调整最大年龄等于最小年龄
- WHEN 用户不选择 THEN 不影响表单提交，API 传空值

### 3.5 报酬输入

**描述**: 第四个表单项，标签"报酬"，必填，文本输入，支持自由输入如"500元/天"或"面议"，placeholder"如：500元/天 或 面议"。

**依赖**:
- `KpFormItem` 组件 (00-02-shared-components §3.8)
- `KpInput` 组件 (00-02-shared-components §3.6)

**验收标准**:
- WHEN 页面渲染 THEN 显示带红色星号的"报酬"标签和输入框
- WHEN 用户输入文字 THEN 通过 v-model 双向绑定到 `form.fee`

### 3.6 角色描述输入

**描述**: 第五个表单项，标签"角色描述"，可选，多行文本输入，最大长度 500 字符，显示字数统计，placeholder"请输入角色要求描述（选填）"。

**依赖**:
- `KpFormItem` 组件 (00-02-shared-components §3.8)
- `KpTextarea` 组件 (00-02-shared-components §3.7)

**验收标准**:
- WHEN 页面渲染 THEN 显示"角色描述"标签和多行输入框
- WHEN 用户输入文字 THEN 右下角显示字数统计（当前/500）
- WHEN 输入超过 500 字符 THEN 阻止继续输入
- WHEN 用户不填写 THEN 不影响表单提交

### 3.7 截止时间选择

**描述**: 第六个表单项，标签"截止时间"，可选，使用日期选择器（uni.showDatePicker 或 picker mode="date"），只能选择今天及之后的日期。

**依赖**:
- `KpFormItem` 组件 (00-02-shared-components §3.8)

**验收标准**:
- WHEN 页面渲染 THEN 显示"截止时间"标签和日期选择器入口，placeholder"请选择截止日期（选填）"
- WHEN 用户点击 THEN 弹出日期选择器，最小日期为今天
- WHEN 选择日期后 THEN 显示所选日期（YYYY-MM-DD 格式），绑定到 `form.deadline`
- WHEN 用户不选择 THEN 不影响表单提交

### 3.8 表单校验与发布

**描述**: 页面底部固定"发布角色"按钮（KpButton primary block），点击时校验必填字段，校验通过后调用 `createRole` API 提交数据。提交成功后返回上一页并显示 toast 提示。

**依赖**:
- `KpButton` 组件 (00-02-shared-components §3.4)
- `api/role.ts` → `createRole` (00-03-shared-utils-api §3.12)
- `utils/validate.ts` → `requiredRule` (00-03-shared-utils-api §3.6)

**验收标准**:
- WHEN 必填字段未填写且点击发布 THEN 对应表单项显示红色错误提示
- WHEN 角色名称为空 THEN 提示"请输入角色名称"
- WHEN 报酬为空 THEN 提示"请输入报酬"
- WHEN 校验通过且点击发布 THEN 按钮显示 loading 状态，调用 `createRole({ projectId, roleName, gender, minAge, maxAge, fee, requirement, deadline })`
- WHEN 发布成功 THEN `navigateBack` 返回上一页，toast 提示"角色发布成功"
- WHEN 发布失败 THEN 显示错误提示，按钮恢复可点击状态
- WHEN 正在提交中 THEN 按钮禁用，防止重复提交

## 4. 非功能需求

> 通用非功能需求见 [SHARED_CONVENTIONS.md](../SHARED_CONVENTIONS.md)

- **体验**: 性别标签单选交互流畅；年龄 picker 联动校验；表单校验即时反馈。

## 5. 约束条件

> 通用约束见 [SHARED_CONVENTIONS.md](../SHARED_CONVENTIONS.md)

- 状态管理：Pinia `useUserStore` 判断用户角色
- API：通过 `api/role.ts` 的 `createRole` 提交数据
- 页面路由：`pages/project/role-create?projectId={id}`，非 Tab 页面，支持 `navigateBack`
- 页面参数：`projectId` 通过 query string 传入，必须存在
