# 剧组资料编辑页

## 1. 概述

"开拍了"(KaiPai)小程序剧组端的公司/团队资料编辑页面，路径为 `pages/company-profile/edit`。剧组用户通过此页面编辑和保存公司名称、联系人、联系电话、简介等信息。页面加载时自动填充已有资料，编辑完成后保存并返回。

技术栈：uni-app 3.0 + Vue 3.4 + TypeScript + uview-plus + Pinia。

## 2. 用户故事

- 作为**剧组用户**，我希望编辑公司/团队的基本资料，以便演员了解我的剧组信息。
- 作为**剧组用户**，我希望页面加载时自动填充已有资料，以便在现有基础上修改。
- 作为**剧组用户**，我希望保存时对必填字段进行校验，以避免提交不完整的信息。

## 3. 功能需求

### 3.1 路由配置

**描述**: 在 `pages.json` 中注册页面路由 `pages/company-profile/edit`。页面加载时调用 `getMyCompany()` 获取当前剧组的公司资料并填充表单。

**验收标准**:
- WHEN 页面 onLoad THEN 调用 API 获取公司资料并填充到表单
- WHEN API 返回数据 THEN 各表单字段正确回显已有值
- WHEN API 请求失败 THEN 提示错误信息，表单保持空白可编辑状态

### 3.2 公司名称输入

**描述**: 使用 KpFormItem + KpInput 组件，标签"公司名称"，必填字段，placeholder"请输入公司/团队名称"。

**验收标准**:
- WHEN 渲染表单 THEN 显示"公司名称"标签，带红色必填星号
- WHEN 用户输入公司名称 THEN 通过 v-model 双向绑定更新值
- WHEN 公司名称为空且提交 THEN 显示"请输入公司名称"错误提示

### 3.3 联系人输入

**描述**: 使用 KpFormItem + KpInput 组件，标签"联系人"，必填字段，placeholder"请输入联系人姓名"。

**验收标准**:
- WHEN 渲染表单 THEN 显示"联系人"标签，带红色必填星号
- WHEN 用户输入联系人 THEN 通过 v-model 双向绑定更新值
- WHEN 联系人为空且提交 THEN 显示"请输入联系人"错误提示

### 3.4 联系电话输入

**描述**: 使用 KpFormItem + KpInput 组件，标签"联系电话"，必填字段，type="number"，placeholder"请输入联系电话"，maxlength 11。

**验收标准**:
- WHEN 渲染表单 THEN 显示"联系电话"标签，带红色必填星号
- WHEN 用户输入电话 THEN 仅允许数字输入，最多 11 位
- WHEN 联系电话为空且提交 THEN 显示"请输入联系电话"错误提示
- WHEN 联系电话格式不正确 THEN 显示"请输入正确的手机号"错误提示

### 3.5 简介输入

**描述**: 使用 KpFormItem + KpTextarea 组件，标签"简介"，可选字段，placeholder"请输入公司/团队简介"，maxlength 500，显示字数统计。

**验收标准**:
- WHEN 渲染表单 THEN 显示"简介"标签，无必填星号
- WHEN 用户输入简介 THEN 通过 v-model 双向绑定更新值
- WHEN 输入内容 THEN 右下角显示"当前字数/500"
- WHEN 输入达到 500 字 THEN 阻止继续输入

### 3.6 表单校验与保存

**描述**: 页面底部固定"保存资料"按钮（KpButton primary block），点击时先校验必填字段和手机号格式，校验通过后调用 `updateCompanyInfo(data)` 保存，成功后 toast 提示并 navigateBack。

**验收标准**:
- WHEN 点击"保存资料" THEN 触发表单校验
- WHEN 校验不通过 THEN 显示对应字段的错误提示，不发起请求
- WHEN 校验通过 THEN 调用 API 保存公司资料
- WHEN 保存成功 THEN toast 提示"保存成功"并 navigateBack 返回上一页
- WHEN 保存失败 THEN 提示错误信息，保持当前页面
- WHEN 保存请求进行中 THEN 按钮显示 loading 状态，防止重复提交

## 4. 非功能需求

> 通用非功能需求见 [SHARED_CONVENTIONS.md](../SHARED_CONVENTIONS.md)

- 表单校验实时反馈（blur 触发）

## 5. 约束条件

> 通用约束见 [SHARED_CONVENTIONS.md](../SHARED_CONVENTIONS.md)

- 依赖 API 层：参考 `00-03-shared-utils-api`（api/company.ts, utils/validate.ts）
