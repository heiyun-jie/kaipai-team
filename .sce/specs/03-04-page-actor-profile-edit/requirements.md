# 编辑演员资料页

## 1. 概述

"开拍了"(KaiPai)小程序演员端的个人资料编辑页面，路径为 `pages/actor-profile/edit`。演员用户通过此页面编辑和完善个人档案——即展示给剧组的"演员简历"，包括头像、基本信息、擅长类型、自我介绍、照片墙和视频简历。页面加载时自动填充已有资料，编辑完成后保存并返回。

技术栈：uni-app 3.0 + Vue 3.4 + TypeScript + uview-plus + Pinia。

## 2. 用户故事

- 作为演员用户，我希望上传个人头像，以便剧组快速识别我。
- 作为演员用户，我希望填写基本信息（姓名、性别、年龄、身高），以便剧组了解我的基本条件。
- 作为演员用户，我希望选择所在城市，以便剧组按地域筛选。
- 作为演员用户，我希望选择擅长的表演类型，以便剧组按类型匹配角色。
- 作为演员用户，我希望撰写自我介绍，以便展示个人特色和经历。
- 作为演员用户，我希望上传照片墙（最多9张），以便剧组查看我的形象照。
- 作为演员用户，我希望上传视频简历，以便剧组查看我的表演片段。
- 作为演员用户，我希望保存时对必填字段进行校验，以避免提交不完整的档案。

## 3. 功能需求

### 3.1 页面路由配置

**描述**: 在 `pages.json` 中注册页面路由 `pages/actor-profile/edit`，配置为非 Tab 页面，导航栏样式为自定义（`navigationStyle: custom`），背景色 `#121214`。页面加载时调用 `getActorProfile()` 获取当前演员资料并填充表单。

**验收标准**:
- WHEN 页面 onLoad THEN 调用 API 获取演员资料并填充到表单
- WHEN API 返回数据 THEN 各表单字段正确回显已有值（头像、基本信息、照片墙等）
- WHEN API 请求失败 THEN 提示错误信息，表单保持空白可编辑状态
- WHEN 页面背景 THEN 深色头部为 `$kp-color-dark-primary`，内容区为 `$kp-color-bg`

### 3.2 头像上传

**描述**: 页面顶部居中展示圆形头像区域，点击后弹出 ActionSheet 选择拍照或从相册选取。选取后调用 `uploadImage()` 上传并更新头像预览。头像为必填项。

**依赖**:
- `KpImageUploader` 组件 avatar 模式 (00-02-shared-components)
- `utils/upload.ts` → `uploadImage()` (00-03-shared-utils-api)

**验收标准**:
- WHEN 渲染页面 THEN 显示圆形头像占位区域，已有头像则回显
- WHEN 点击头像区域 THEN 弹出 ActionSheet（拍照 / 从相册选择）
- WHEN 选择图片后 THEN 调用 uploadImage 上传，成功后更新头像预览
- WHEN 上传失败 THEN toast 提示"头像上传失败"
- WHEN 保存时头像为空 THEN 校验不通过，提示"请上传头像"

### 3.3 基本信息表单

**描述**: 使用 KpFormItem + KpInput 组件展示基本信息表单，包含姓名、性别、年龄、身高四个字段，均为必填。性别使用 picker（男/女），年龄和身高使用数字输入。

**验收标准**:
- WHEN 渲染表单 THEN 显示姓名、性别、年龄、身高四个表单项，均带红色必填星号
- WHEN 用户输入姓名 THEN v-model 双向绑定，maxlength 20
- WHEN 点击性别字段 THEN 弹出 picker 选择（男/女）
- WHEN 用户输入年龄 THEN 仅允许数字，范围 1-99
- WHEN 用户输入身高 THEN 仅允许数字，单位 cm，范围 50-250
- WHEN 任一必填字段为空且提交 THEN 显示对应错误提示

### 3.4 城市选择

**描述**: 使用 KpFormItem + KpInput（只读模式）展示城市选择，点击后弹出城市选择器。城市为必填项。

**验收标准**:
- WHEN 渲染表单 THEN 显示"所在城市"标签，带红色必填星号
- WHEN 点击城市字段 THEN 弹出城市选择器（省市区三级联动或城市列表）
- WHEN 选择城市后 THEN 更新显示值
- WHEN 城市为空且提交 THEN 显示"请选择所在城市"错误提示

### 3.5 擅长类型多选

**描述**: 展示预定义的表演类型标签列表：古装、现代、反派、喜剧、文艺、动作、恐怖、其他。用户可多选，选中的标签高亮显示。使用 KpTag 组件实现 toggle 效果。

**验收标准**:
- WHEN 渲染表单 THEN 显示"擅长类型"标签和所有类型标签
- WHEN 点击未选中的标签 THEN 标签变为选中状态（高亮）
- WHEN 点击已选中的标签 THEN 标签变为未选中状态
- WHEN 已有资料包含擅长类型 THEN 对应标签默认选中
- WHEN 未选择任何类型 THEN 允许保存（非必填）

### 3.6 自我介绍

**描述**: 使用 KpFormItem + KpTextarea 组件，标签"自我介绍"，可选字段，placeholder"介绍一下自己的表演经历和特长"，maxlength 500，显示字数统计。

**验收标准**:
- WHEN 渲染表单 THEN 显示"自我介绍"标签，无必填星号
- WHEN 用户输入内容 THEN v-model 双向绑定，右下角显示字数统计
- WHEN 输入达到 500 字 THEN 阻止继续输入
- WHEN 已有自我介绍 THEN 回显已有内容

### 3.7 照片墙上传

**描述**: 使用 KpImageUploader 组件（grid 模式），以九宫格形式展示已上传照片，最多 9 张。末尾显示"+"按钮添加新照片，长按已有照片可删除。

**依赖**:
- `KpImageUploader` 组件 grid 模式 (00-02-shared-components)
- `utils/upload.ts` → `uploadImage()` (00-03-shared-utils-api)

**验收标准**:
- WHEN 渲染照片墙 THEN 以九宫格布局展示已上传照片
- WHEN 照片数量 < 9 THEN 末尾显示"+"添加按钮
- WHEN 照片数量 = 9 THEN 隐藏"+"按钮
- WHEN 点击"+"按钮 THEN 弹出 ActionSheet（拍照 / 从相册选择），支持多选
- WHEN 选择图片后 THEN 逐张调用 uploadImage 上传，成功后追加到照片列表
- WHEN 长按已有照片 THEN 弹出确认弹窗"确定删除该照片？"，确认后移除
- WHEN 点击已有照片 THEN 全屏预览（uni.previewImage）

### 3.8 视频简历上传

**描述**: 使用 KpVideoUploader 组件上传视频简历，仅支持 mp4 格式，最大 100MB。上传过程中显示进度条，上传完成后显示视频缩略图，点击可播放预览，支持删除后重新上传。

**依赖**:
- `KpVideoUploader` 组件 (00-02-shared-components)
- `utils/upload.ts` → `uploadVideo()` (00-03-shared-utils-api)

**验收标准**:
- WHEN 未上传视频 THEN 显示上传占位区域（带视频图标和"上传视频简历"文字）
- WHEN 点击上传区域 THEN 调用 uni.chooseVideo 选择视频（mp4，maxDuration 60s）
- WHEN 选择的视频 > 100MB THEN toast 提示"视频大小不能超过100MB"，不上传
- WHEN 上传进行中 THEN 显示进度条和百分比
- WHEN 上传成功 THEN 显示视频缩略图
- WHEN 点击缩略图 THEN 全屏播放视频预览
- WHEN 点击删除按钮 THEN 弹出确认弹窗，确认后清除视频，恢复上传占位
- WHEN 上传失败 THEN toast 提示"视频上传失败"，恢复上传占位

### 3.9 表单校验与保存

**描述**: 页面底部固定"保存资料"按钮（KpButton primary block），点击时校验必填字段（头像、姓名、性别、年龄、身高、城市），校验通过后调用 `updateActorProfile(data)` 保存，成功后 toast 提示并 navigateBack。

**验收标准**:
- WHEN 点击"保存资料" THEN 触发全量表单校验
- WHEN 校验不通过 THEN 显示对应字段的错误提示，滚动到第一个错误字段
- WHEN 校验通过 THEN 调用 API 保存演员资料
- WHEN 保存成功 THEN toast 提示"保存成功"并 navigateBack 返回上一页
- WHEN 保存失败 THEN 提示错误信息，保持当前页面
- WHEN 保存请求进行中 THEN 按钮显示 loading 状态，防止重复提交

## 4. 非功能需求

> 通用非功能需求见 [SHARED_CONVENTIONS.md](../SHARED_CONVENTIONS.md)

- 图片上传前自动压缩（宽度不超过 1080px）；视频上传支持断点续传或分片上传
- 表单项支持 aria-label；必填字段有视觉和语义标识；上传区域有明确的操作提示
- 表单校验实时反馈（blur 触发）；上传过程有明确进度反馈

## 5. 约束条件

> 通用约束见 [SHARED_CONVENTIONS.md](../SHARED_CONVENTIONS.md)

- API：通过 `api/actor.ts` 的 `getActorProfile()` 和 `updateActorProfile(data)` 操作数据（00-03-shared-utils-api）
- 上传：通过 `utils/upload.ts` 的 `uploadImage()` 和 `uploadVideo()` 处理文件上传（00-03-shared-utils-api）
- 组件依赖：KpPageLayout, KpNavBar, KpImageUploader, KpVideoUploader, KpFormItem, KpInput, KpTextarea, KpButton, KpTag（00-02-shared-components）
- 页面为非 Tab 页，使用自定义导航栏（`navigationStyle: custom`）
