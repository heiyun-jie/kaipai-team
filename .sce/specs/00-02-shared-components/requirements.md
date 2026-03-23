# 共享组件库

## 1. 概述

"开拍了"（KaiPai）微信小程序的共享 UI 组件库，统一前缀 `Kp`，基于 uni-app 3.0 + Vue 3.4 + TypeScript + uview-plus + SCSS 构建。所有组件遵循 **Cinematic Glassmorphism** 设计语言（深色头部 + 浅色内容区、品牌色 Spotlight Orange `#FF6B35`、毛玻璃效果），为 14 个页面提供一致的视觉体验与交互模式。

## 2. 用户故事

- 作为**前端开发者**，我希望使用统一的 Kp 组件库搭建页面，以保证视觉一致性并减少重复代码。
- 作为**设计师**，我希望组件库严格遵循 Cinematic Glassmorphism 风格，使产品呈现专业的影视行业质感。
- 作为**用户（演员/剧组）**，我希望界面流畅、风格统一、操作直觉化，在不同页面间切换时体验连贯。

## 3. 功能需求

### 3.1 KpPageLayout

**描述**: 全局页面骨架组件，实现深色头部区域 + 浅色内容区域的双层布局结构。自动处理安全区域（状态栏、底部安全区）适配。

**Props**:
```typescript
interface KpPageLayoutProps {
  /** 深色头部区域背景色 */
  headerBg?: string            // default: '#1A1A2E'
  /** 内容区域背景色 */
  contentBg?: string           // default: '#F5F5F7'
  /** 头部区域高度（rpx），不含状态栏 */
  headerHeight?: number        // default: 400
  /** 是否显示头部区域 */
  showHeader?: boolean         // default: true
  /** 是否启用内容区域滚动 */
  scrollable?: boolean         // default: true
  /** 是否适配底部安全区 */
  safeAreaBottom?: boolean     // default: true
}
```

**Events**:
| 事件名 | Payload | 说明 |
|--------|---------|------|
| scroll | `{ scrollTop: number }` | 内容区域滚动时触发 |
| scrolltolower | — | 滚动到底部时触发（用于加载更多） |

**Slots**:
| 插槽名 | 说明 |
|--------|------|
| header | 深色头部区域内容 |
| default | 浅色内容区域 |

**使用页面**: 全部 14 个页面

**验收标准**:
- WHEN 页面使用 KpPageLayout THEN 自动呈现深色头部 + 浅色内容的双层结构
- WHEN 在不同机型上渲染 THEN 状态栏高度自动适配，内容不被遮挡
- WHEN scrollable 为 true 且内容超出 THEN 内容区域可滚动，触发 scroll 事件
- WHEN scrolltolower 触发 THEN 可用于分页加载

### 3.2 KpNavBar

**描述**: 自定义导航栏组件，适配微信小程序胶囊按钮位置，支持返回、标题、右侧操作区。在深色头部区域上以透明/毛玻璃风格呈现。

**Props**:
```typescript
interface KpNavBarProps {
  /** 标题文字 */
  title?: string               // default: ''
  /** 标题颜色 */
  titleColor?: string          // default: '#FFFFFF'
  /** 是否显示返回按钮 */
  showBack?: boolean           // default: true
  /** 背景色 */
  bgColor?: string             // default: 'transparent'
  /** 是否固定在顶部 */
  fixed?: boolean              // default: true
  /** 是否启用毛玻璃背景（滚动后） */
  glassOnScroll?: boolean      // default: false
  /** 返回按钮图标颜色 */
  backIconColor?: string       // default: '#FFFFFF'
}
```

**Events**:
| 事件名 | Payload | 说明 |
|--------|---------|------|
| back | — | 点击返回按钮时触发 |
| clickRight | — | 点击右侧操作区时触发 |

**Slots**:
| 插槽名 | 说明 |
|--------|------|
| left | 自定义左侧区域（覆盖默认返回按钮） |
| center | 自定义标题区域 |
| right | 右侧操作区 |

**使用页面**: 所有非 Tab 页面（12 个页面）

**验收标准**:
- WHEN 组件渲染 THEN 导航栏高度与微信胶囊按钮对齐，不遮挡胶囊
- WHEN showBack 为 true 且用户点击返回 THEN 触发 back 事件
- WHEN glassOnScroll 为 true 且页面滚动 THEN 导航栏背景渐变为毛玻璃效果
- WHEN 在不同机型上渲染 THEN 状态栏高度自动适配

### 3.3 KpCard

**描述**: 通用卡片容器，支持白色模式（浅色内容区）和深色模式（深色头部区），可选毛玻璃效果和阴影。

**Props**:
```typescript
interface KpCardProps {
  /** 卡片模式 */
  mode?: 'light' | 'dark'      // default: 'light'
  /** 是否启用毛玻璃效果 */
  glass?: boolean              // default: false
  /** 圆角大小（rpx） */
  radius?: number              // default: 24
  /** 内边距（rpx） */
  padding?: string             // default: '24rpx'
  /** 是否显示阴影 */
  shadow?: boolean             // default: true
  /** 自定义背景色 */
  bgColor?: string             // default: 根据 mode 自动
}
```

**Events**:
| 事件名 | Payload | 说明 |
|--------|---------|------|
| click | — | 点击卡片时触发 |

**Slots**:
| 插槽名 | 说明 |
|--------|------|
| default | 卡片内容 |
| header | 卡片头部（可选） |
| footer | 卡片底部（可选） |

**使用页面**: 多个页面（首页、详情页、编辑页、申请页等）

**验收标准**:
- WHEN mode 为 'light' THEN 卡片呈白色背景 + 浅阴影
- WHEN mode 为 'dark' THEN 卡片呈深色背景 + 浅色文字
- WHEN glass 为 true THEN 卡片呈现毛玻璃半透明效果（backdrop-filter: blur）
- WHEN 用户点击卡片 THEN 触发 click 事件

### 3.4 KpButton

**描述**: 全局按钮组件，支持 primary / secondary / danger / disabled / glass 五种变体，primary 使用品牌色 `#FF6B35`。

**Props**:
```typescript
interface KpButtonProps {
  /** 按钮变体 */
  variant?: 'primary' | 'secondary' | 'danger' | 'glass'  // default: 'primary'
  /** 按钮尺寸 */
  size?: 'small' | 'medium' | 'large'                     // default: 'medium'
  /** 是否禁用 */
  disabled?: boolean           // default: false
  /** 是否加载中 */
  loading?: boolean            // default: false
  /** 是否为块级按钮（宽度 100%） */
  block?: boolean              // default: false
  /** 圆角大小（rpx） */
  radius?: number              // default: 16
  /** 自定义图标（左侧） */
  icon?: string                // default: ''
  /** 微信开放能力 */
  openType?: string            // default: ''
}
```

**Events**:
| 事件名 | Payload | 说明 |
|--------|---------|------|
| click | `event: Event` | 点击按钮时触发（disabled/loading 时不触发） |
| getphonenumber | `event` | openType="getPhoneNumber" 回调 |
| getuserinfo | `event` | openType="getUserInfo" 回调 |

**Slots**:
| 插槽名 | 说明 |
|--------|------|
| default | 按钮文字内容 |
| icon | 自定义图标区域 |

**使用页面**: 全部 14 个页面

**验收标准**:
- WHEN variant 为 'primary' THEN 按钮背景为 #FF6B35，文字白色
- WHEN variant 为 'glass' THEN 按钮呈毛玻璃半透明效果
- WHEN disabled 为 true THEN 按钮置灰且不可点击
- WHEN loading 为 true THEN 显示加载动画且不可重复点击
- WHEN 设置 openType THEN 正确触发微信开放能力回调

### 3.5 KpTag

**描述**: 标签组件，用于筛选标签、技能标签、状态标签等场景，支持多种尺寸和颜色方案。

**Props**:
```typescript
interface KpTagProps {
  /** 标签文字 */
  text: string
  /** 标签类型 */
  type?: 'default' | 'primary' | 'success' | 'warning' | 'danger'  // default: 'default'
  /** 尺寸 */
  size?: 'small' | 'medium'   // default: 'small'
  /** 是否可关闭 */
  closable?: boolean           // default: false
  /** 是否选中态（用于筛选） */
  selected?: boolean           // default: false
  /** 是否为圆角胶囊样式 */
  round?: boolean              // default: true
  /** 自定义背景色 */
  bgColor?: string             // default: 根据 type 自动
  /** 自定义文字颜色 */
  textColor?: string           // default: 根据 type 自动
}
```

**Events**:
| 事件名 | Payload | 说明 |
|--------|---------|------|
| click | — | 点击标签时触发 |
| close | — | 点击关闭按钮时触发 |

**Slots**: 无

**使用页面**: 首页、详情页、申请页

**验收标准**:
- WHEN selected 为 true THEN 标签呈品牌色高亮状态
- WHEN closable 为 true THEN 显示关闭图标，点击触发 close 事件
- WHEN type 为 'primary' THEN 使用品牌色 #FF6B35 色系

### 3.6 KpInput

**描述**: 表单输入框组件，统一输入样式，支持标签、占位符、校验状态、清除按钮，适配深色/浅色背景。

**Props**:
```typescript
interface KpInputProps {
  /** 绑定值 */
  modelValue: string
  /** 输入类型 */
  type?: 'text' | 'number' | 'idcard' | 'digit' | 'password'  // default: 'text'
  /** 占位文字 */
  placeholder?: string         // default: '请输入'
  /** 是否禁用 */
  disabled?: boolean           // default: false
  /** 最大长度 */
  maxlength?: number           // default: 140
  /** 是否显示清除按钮 */
  clearable?: boolean          // default: true
  /** 校验状态 */
  status?: '' | 'error'        // default: ''
  /** 前缀图标 */
  prefixIcon?: string          // default: ''
  /** 后缀图标 */
  suffixIcon?: string          // default: ''
}
```

**Events**:
| 事件名 | Payload | 说明 |
|--------|---------|------|
| update:modelValue | `string` | 输入值变化（v-model） |
| focus | `event` | 获取焦点 |
| blur | `event` | 失去焦点 |
| clear | — | 点击清除按钮 |
| clickSuffix | — | 点击后缀图标 |

**Slots**:
| 插槽名 | 说明 |
|--------|------|
| prefix | 自定义前缀区域 |
| suffix | 自定义后缀区域 |

**使用页面**: 登录页、演员编辑页、公司编辑页、项目创建页、角色创建页

**验收标准**:
- WHEN 用户输入文字 THEN 通过 v-model 双向绑定更新值
- WHEN status 为 'error' THEN 输入框边框变为红色
- WHEN clearable 为 true 且有输入内容 THEN 显示清除按钮，点击清空内容
- WHEN disabled 为 true THEN 输入框置灰不可编辑

### 3.7 KpTextarea

**描述**: 多行文本输入组件，支持字数统计、自动增高、校验状态。

**Props**:
```typescript
interface KpTextareaProps {
  /** 绑定值 */
  modelValue: string
  /** 占位文字 */
  placeholder?: string         // default: '请输入'
  /** 最大长度 */
  maxlength?: number           // default: 500
  /** 是否显示字数统计 */
  showCount?: boolean          // default: true
  /** 是否自动增高 */
  autoHeight?: boolean         // default: false
  /** 最小高度（rpx） */
  minHeight?: number           // default: 200
  /** 是否禁用 */
  disabled?: boolean           // default: false
  /** 校验状态 */
  status?: '' | 'error'        // default: ''
}
```

**Events**:
| 事件名 | Payload | 说明 |
|--------|---------|------|
| update:modelValue | `string` | 输入值变化（v-model） |
| focus | `event` | 获取焦点 |
| blur | `event` | 失去焦点 |

**Slots**: 无

**使用页面**: 演员编辑页、公司编辑页、项目创建页、角色创建页

**验收标准**:
- WHEN showCount 为 true THEN 右下角显示"当前字数/最大字数"
- WHEN 输入超过 maxlength THEN 阻止继续输入
- WHEN autoHeight 为 true THEN 文本框高度随内容自动增长
- WHEN status 为 'error' THEN 边框变为红色

### 3.8 KpFormItem

**描述**: 表单项容器，包裹 KpInput / KpTextarea 等表单控件，提供标签、必填标记、校验错误提示。

**Props**:
```typescript
interface KpFormItemProps {
  /** 标签文字 */
  label: string
  /** 是否必填（显示红色星号） */
  required?: boolean           // default: false
  /** 错误提示文字 */
  error?: string               // default: ''
  /** 标签宽度（rpx） */
  labelWidth?: number          // default: 180
  /** 布局方向 */
  direction?: 'horizontal' | 'vertical'  // default: 'vertical'
}
```

**Events**: 无

**Slots**:
| 插槽名 | 说明 |
|--------|------|
| default | 表单控件（KpInput / KpTextarea 等） |
| label | 自定义标签区域 |
| extra | 标签右侧额外信息 |

**使用页面**: 登录页、演员编辑页、公司编辑页、项目创建页、角色创建页

**验收标准**:
- WHEN required 为 true THEN 标签前显示红色星号
- WHEN error 不为空 THEN 表单项下方显示红色错误提示文字
- WHEN direction 为 'horizontal' THEN 标签与控件水平排列
- WHEN direction 为 'vertical' THEN 标签在上、控件在下

### 3.9 KpImageUploader

**描述**: 图片上传组件，支持单图（头像）和多图（九宫格照片墙）模式，集成图片预览、裁剪提示、上传进度。

**Props**:
```typescript
interface KpImageUploaderProps {
  /** 已上传图片列表 */
  modelValue: string[]
  /** 最大上传数量 */
  maxCount?: number            // default: 9
  /** 是否为单图模式（头像） */
  single?: boolean             // default: false
  /** 单张图片最大体积（MB） */
  maxSize?: number             // default: 5
  /** 图片尺寸模式 */
  sizeType?: ('original' | 'compressed')[]  // default: ['compressed']
  /** 图片来源 */
  sourceType?: ('album' | 'camera')[]       // default: ['album', 'camera']
  /** 是否可删除 */
  deletable?: boolean          // default: true
  /** 是否禁用 */
  disabled?: boolean           // default: false
  /** 上传提示文字 */
  uploadText?: string          // default: '上传图片'
}
```

**Events**:
| 事件名 | Payload | 说明 |
|--------|---------|------|
| update:modelValue | `string[]` | 图片列表变化（v-model） |
| afterRead | `{ file: File, index: number }` | 图片读取完成，用于触发上传 |
| delete | `{ index: number, url: string }` | 删除图片 |
| oversize | `{ file: File }` | 图片超出大小限制 |
| preview | `{ index: number, urls: string[] }` | 预览图片 |

**Slots**:
| 插槽名 | 说明 |
|--------|------|
| trigger | 自定义上传触发区域 |

**使用页面**: 演员资料编辑页（头像单图 + 照片墙九宫格）

**验收标准**:
- WHEN single 为 true THEN 只显示一个圆形上传区域（头像模式）
- WHEN 图片数量达到 maxCount THEN 隐藏上传按钮
- WHEN 图片超过 maxSize THEN 触发 oversize 事件并提示用户
- WHEN 点击已上传图片 THEN 全屏预览
- WHEN 点击删除按钮 THEN 触发 delete 事件并从列表移除

### 3.10 KpVideoUploader

**描述**: 视频上传组件，支持视频选择、上传进度显示、视频预览播放，限制视频时长和大小。

**Props**:
```typescript
interface KpVideoUploaderProps {
  /** 已上传视频 URL */
  modelValue: string
  /** 最大视频时长（秒） */
  maxDuration?: number         // default: 60
  /** 最大视频大小（MB） */
  maxSize?: number             // default: 50
  /** 是否禁用 */
  disabled?: boolean           // default: false
  /** 是否显示上传进度 */
  showProgress?: boolean       // default: true
  /** 上传提示文字 */
  uploadText?: string          // default: '上传视频'
  /** 视频来源 */
  sourceType?: ('album' | 'camera')[]  // default: ['album', 'camera']
}
```

**Events**:
| 事件名 | Payload | 说明 |
|--------|---------|------|
| update:modelValue | `string` | 视频 URL 变化（v-model） |
| progress | `{ percent: number }` | 上传进度变化 |
| success | `{ url: string }` | 上传成功 |
| fail | `{ error: string }` | 上传失败 |
| delete | — | 删除视频 |

**Slots**: 无

**使用页面**: 演员资料编辑页

**验收标准**:
- WHEN 用户选择视频 THEN 显示上传进度条
- WHEN 视频超过 maxDuration 或 maxSize THEN 提示用户并阻止上传
- WHEN 上传成功 THEN 显示视频缩略图和播放按钮
- WHEN 点击播放按钮 THEN 全屏播放视频
- WHEN 点击删除 THEN 清空视频并触发 delete 事件

### 3.11 KpRoleCard

**描述**: 角色卡片组件，展示角色名称、所属项目、薪酬、标签（性别/年龄/类型）、状态，用于首页演员端列表和角色详情页。

**Props**:
```typescript
interface KpRoleCardProps {
  /** 角色数据 */
  role: {
    id: string
    name: string
    projectName: string
    salary: string
    gender: string
    ageRange: string
    tags: string[]
    status: 'recruiting' | 'paused' | 'closed'
    coverImage?: string
    publishTime: string
  }
  /** 是否显示项目名称 */
  showProject?: boolean        // default: true
  /** 是否显示状态标签 */
  showStatus?: boolean         // default: true
}
```

**Events**:
| 事件名 | Payload | 说明 |
|--------|---------|------|
| click | `{ roleId: string }` | 点击卡片跳转详情 |

**Slots**:
| 插槽名 | 说明 |
|--------|------|
| footer | 卡片底部自定义区域 |

**使用页面**: 首页演员端、角色详情页

**验收标准**:
- WHEN 渲染角色卡片 THEN 显示角色名、项目名、薪酬、标签信息
- WHEN status 为 'recruiting' THEN 显示绿色"招募中"状态标签
- WHEN 用户点击卡片 THEN 触发 click 事件并传递 roleId

### 3.12 KpProjectCard

**描述**: 项目卡片组件，展示项目名称、类型、拍摄地点、时间、招募角色数量，用于首页剧组端列表。

**Props**:
```typescript
interface KpProjectCardProps {
  /** 项目数据 */
  project: {
    id: string
    name: string
    type: string
    location: string
    shootingDate: string
    roleCount: number
    coverImage?: string
    status: 'draft' | 'active' | 'completed'
  }
  /** 是否显示角色数量 */
  showRoleCount?: boolean      // default: true
}
```

**Events**:
| 事件名 | Payload | 说明 |
|--------|---------|------|
| click | `{ projectId: string }` | 点击卡片跳转详情 |

**Slots**:
| 插槽名 | 说明 |
|--------|------|
| footer | 卡片底部自定义区域 |

**使用页面**: 首页剧组端

**验收标准**:
- WHEN 渲染项目卡片 THEN 显示项目名、类型、地点、时间等信息
- WHEN showRoleCount 为 true THEN 显示"招募 X 个角色"
- WHEN 用户点击卡片 THEN 触发 click 事件并传递 projectId

### 3.13 KpApplyCard

**描述**: 申请卡片组件，展示申请记录信息（角色名、项目名、申请状态、申请时间），演员端和剧组端共用但展示侧重不同。

**Props**:
```typescript
interface KpApplyCardProps {
  /** 申请数据 */
  apply: {
    id: string
    roleName: string
    projectName: string
    status: 'pending' | 'accepted' | 'rejected' | 'cancelled'
    applyTime: string
    actorName?: string
    actorAvatar?: string
  }
  /** 视角模式 */
  viewMode?: 'actor' | 'crew'  // default: 'actor'
}
```

**Events**:
| 事件名 | Payload | 说明 |
|--------|---------|------|
| click | `{ applyId: string }` | 点击卡片查看详情 |
| action | `{ applyId: string, action: 'accept' | 'reject' }` | 剧组端操作按钮 |

**Slots**:
| 插槽名 | 说明 |
|--------|------|
| action | 自定义操作区域 |

**使用页面**: 我的申请页（演员端）、申请管理页（剧组端）

**验收标准**:
- WHEN viewMode 为 'actor' THEN 显示角色名、项目名、申请状态
- WHEN viewMode 为 'crew' THEN 额外显示演员头像和姓名
- WHEN 剧组端点击"通过/拒绝" THEN 触发 action 事件
- WHEN status 变化 THEN 状态标签颜色相应更新

### 3.14 KpActorBrief

**描述**: 演员简要信息卡片，展示演员头像、姓名、基本信息（性别/年龄/身高/体重），用于申请确认和申请管理场景。

**Props**:
```typescript
interface KpActorBriefProps {
  /** 演员数据 */
  actor: {
    id: string
    name: string
    avatar: string
    gender: string
    age: number
    height: number
    weight: number
    tags?: string[]
  }
  /** 是否可点击查看详情 */
  clickable?: boolean          // default: true
  /** 是否显示标签 */
  showTags?: boolean           // default: false
  /** 尺寸 */
  size?: 'small' | 'medium'   // default: 'medium'
}
```

**Events**:
| 事件名 | Payload | 说明 |
|--------|---------|------|
| click | `{ actorId: string }` | 点击查看演员详情 |

**Slots**:
| 插槽名 | 说明 |
|--------|------|
| extra | 右侧额外信息区域 |

**使用页面**: 申请确认页、申请管理页

**验收标准**:
- WHEN 渲染组件 THEN 显示圆形头像 + 姓名 + 基本信息
- WHEN clickable 为 true 且用户点击 THEN 触发 click 事件
- WHEN showTags 为 true THEN 在基本信息下方显示技能标签

### 3.15 KpEmpty

**描述**: 空状态占位组件，在列表无数据时展示插画、提示文字和可选操作按钮。

**Props**:
```typescript
interface KpEmptyProps {
  /** 空状态类型（决定默认插画） */
  type?: 'default' | 'search' | 'network' | 'apply'  // default: 'default'
  /** 提示文字 */
  text?: string                // default: '暂无数据'
  /** 是否显示操作按钮 */
  showAction?: boolean         // default: false
  /** 操作按钮文字 */
  actionText?: string          // default: ''
  /** 自定义图片 URL */
  image?: string               // default: 根据 type 自动
}
```

**Events**:
| 事件名 | Payload | 说明 |
|--------|---------|------|
| action | — | 点击操作按钮时触发 |

**Slots**:
| 插槽名 | 说明 |
|--------|------|
| image | 自定义插画区域 |
| default | 自定义提示内容 |
| action | 自定义操作区域 |

**使用页面**: 首页、我的申请页、申请管理页

**验收标准**:
- WHEN 列表为空 THEN 显示对应类型的空状态插画和提示文字
- WHEN showAction 为 true THEN 显示操作按钮
- WHEN 用户点击操作按钮 THEN 触发 action 事件

### 3.16 KpFilterBar

**描述**: 筛选栏组件，支持多维度筛选（性别/年龄/地区/片酬），以横向滚动标签 + 下拉面板形式呈现。

**Props**:
```typescript
interface KpFilterBarProps {
  /** 筛选项配置 */
  filters: Array<{
    key: string
    label: string
    type: 'single' | 'multiple' | 'range'
    options: Array<{ label: string; value: string | number }>
  }>
  /** 当前筛选值 */
  modelValue: Record<string, any>
  /** 是否固定在顶部 */
  sticky?: boolean             // default: true
  /** 固定时距顶部距离（rpx） */
  stickyTop?: number           // default: 0
}
```

**Events**:
| 事件名 | Payload | 说明 |
|--------|---------|------|
| update:modelValue | `Record<string, any>` | 筛选值变化（v-model） |
| change | `{ key: string, value: any }` | 单个筛选项变化 |
| reset | — | 重置所有筛选 |

**Slots**:
| 插槽名 | 说明 |
|--------|------|
| extra | 筛选栏右侧额外区域 |

**使用页面**: 首页演员端

**验收标准**:
- WHEN 点击筛选项 THEN 展开对应下拉面板
- WHEN 选择筛选值 THEN 通过 v-model 更新并触发 change 事件
- WHEN 有激活的筛选 THEN 对应标签高亮显示品牌色
- WHEN 点击重置 THEN 清空所有筛选条件

### 3.17 KpTabBar

**描述**: 底部导航栏组件，毛玻璃风格，适配微信小程序自定义 TabBar 规范，支持图标 + 文字 + 角标。

**Props**:
```typescript
interface KpTabBarProps {
  /** 当前选中项索引 */
  current: number
  /** 导航项列表 */
  items: Array<{
    icon: string
    activeIcon: string
    text: string
    pagePath: string
    badge?: number
  }>
  /** 是否启用毛玻璃效果 */
  glass?: boolean              // default: true
  /** 激活项颜色 */
  activeColor?: string         // default: '#FF6B35'
  /** 未激活项颜色 */
  inactiveColor?: string       // default: '#999999'
}
```

**Events**:
| 事件名 | Payload | 说明 |
|--------|---------|------|
| change | `{ index: number, pagePath: string }` | 切换导航项 |

**Slots**: 无

**使用页面**: Tab 页面（首页、我的）

**验收标准**:
- WHEN 组件渲染 THEN 底部显示毛玻璃效果导航栏
- WHEN 点击导航项 THEN 触发 change 事件并切换页面
- WHEN 某项有 badge THEN 在图标右上角显示红色角标数字
- WHEN glass 为 true THEN 导航栏背景呈半透明毛玻璃效果
- WHEN 适配底部安全区 THEN 自动增加底部 padding

### 3.18 KpStatusTag

**描述**: 状态标签组件，专用于展示业务状态（招募中/已暂停/已关闭/待审核/已通过/已拒绝），颜色与状态语义绑定。

**Props**:
```typescript
interface KpStatusTagProps {
  /** 状态值 */
  status: 'recruiting' | 'paused' | 'closed' | 'pending' | 'accepted' | 'rejected' | 'cancelled'
  /** 尺寸 */
  size?: 'small' | 'medium'   // default: 'small'
  /** 是否显示圆点指示器 */
  dot?: boolean                // default: false
}
```

**Events**: 无

**Slots**: 无

**使用页面**: 首页、详情页、申请管理页、我的申请页

**验收标准**:
- WHEN status 为 'recruiting' THEN 显示绿色"招募中"
- WHEN status 为 'paused' THEN 显示黄色"已暂停"
- WHEN status 为 'closed' THEN 显示灰色"已关闭"
- WHEN status 为 'pending' THEN 显示橙色"待审核"
- WHEN status 为 'accepted' THEN 显示绿色"已通过"
- WHEN status 为 'rejected' THEN 显示红色"已拒绝"
- WHEN status 为 'cancelled' THEN 显示灰色"已取消"
- WHEN dot 为 true THEN 文字前显示对应颜色的圆点

### 3.19 KpConfirmDialog

**描述**: 确认对话框组件，用于二次确认操作（角色选择、申请确认、退出登录等），支持标题、内容、双按钮。

**Props**:
```typescript
interface KpConfirmDialogProps {
  /** 是否显示 */
  modelValue: boolean
  /** 标题 */
  title?: string               // default: '提示'
  /** 内容文字 */
  content?: string             // default: ''
  /** 确认按钮文字 */
  confirmText?: string         // default: '确认'
  /** 取消按钮文字 */
  cancelText?: string          // default: '取消'
  /** 确认按钮变体 */
  confirmVariant?: 'primary' | 'danger'  // default: 'primary'
  /** 是否显示取消按钮 */
  showCancel?: boolean         // default: true
  /** 点击遮罩是否关闭 */
  closeOnClickOverlay?: boolean  // default: false
}
```

**Events**:
| 事件名 | Payload | 说明 |
|--------|---------|------|
| update:modelValue | `boolean` | 显示状态变化（v-model） |
| confirm | — | 点击确认按钮 |
| cancel | — | 点击取消按钮 |

**Slots**:
| 插槽名 | 说明 |
|--------|------|
| default | 自定义对话框内容（覆盖 content） |
| footer | 自定义底部按钮区域 |

**使用页面**: 角色选择页、申请确认页、申请管理页、我的页面（退出登录）

**验收标准**:
- WHEN modelValue 为 true THEN 显示遮罩 + 居中对话框
- WHEN 点击确认按钮 THEN 触发 confirm 事件并关闭对话框
- WHEN 点击取消按钮 THEN 触发 cancel 事件并关闭对话框
- WHEN confirmVariant 为 'danger' THEN 确认按钮为红色（用于危险操作）
- WHEN closeOnClickOverlay 为 false THEN 点击遮罩不关闭对话框

## 4. 非功能需求

> 通用非功能需求见 [SHARED_CONVENTIONS.md](../SHARED_CONVENTIONS.md)

- **性能**: 组件首次渲染 < 100ms；单次渲染不超过 20 个卡片；图片/视频上传使用压缩；毛玻璃效果低端机型自动降级
- **可维护性**: 每个组件独立目录（.vue + types.ts + index.ts）；Props 用 TypeScript interface 定义并导出

## 5. 约束条件

> 通用约束见 [SHARED_CONVENTIONS.md](../SHARED_CONVENTIONS.md)

- 命名规范：组件统一 `Kp` 前缀，文件名 PascalCase（如 `KpButton.vue`）
- 组件通信：Props 向下传递，Events 向上冒泡，禁止组件间直接引用
- 状态管理：组件内部状态自管理，全局状态通过 Pinia Store 注入
