# 开发经验手册

> 项目开发中沉淀的高频问题、视觉基线和页面实现经验。
> 技术约定见 `.sce/specs/SHARED_CONVENTIONS.md`，开发原则见 `.sce/steering/CORE_PRINCIPLES.md`。

## 一、高频问题速查

| # | 问题 | 根因 | 修复 |
|---|------|------|------|
| 1 | 页面改了用户看到旧页面 | DevTools 未打开最新 `dist/build/mp-weixin` | 重新 build → 打开 `dist/build/mp-weixin` |
| 2 | 改错 CSS 锚点 | 没先拆三层就凭类名猜 | 先定位导航/Hero/Content哪层，一次只改一层 |
| 3 | 返回按钮与胶囊不一致 | 只复制按钮DOM没复制容器 | 三件套整体复制（参考 role-detail） |
| 4 | WXSS/WXML 编译报错 | 不兼容小程序的选择器 | 以小程序兼容为先，看生成 `.wxml`/`.wxss` |
| 5 | `common/assets.js is not defined` | 产物不完整 | 删 dist → 重新 build → 重新打开 |
| 6 | 按钮点不到/文案不居中 | 原生 `disabled` 被微信接管 | 保留点击，条件不满足时事件内提示 |
| 7 | 自定义组件小程序运行不稳定 | 组件抽象过深 | 复杂表单回到原生 input/textarea/picker |
| 8 | 登录后全局状态不更新 | 没同步写 token + userInfo | 登录后同写；保存后调 `updateProfile()` |
| 9 | 上传体验版失败 | 账号无开发者权限 | 用有权限账号登录 DevTools |

## 二、视觉语言基线

以 `pages/mine/index`（已冻结）为参考：

- 深色头部 `#121214`，可叠低透明度橙色/白色光斑
- 强调色橙色渐变，用于主按钮/标签/进度条
- 白卡大圆角、轻阴影，深色头部+白卡叠层
- 主操作按钮固定底部，高度偏大
- 导航栏极简白字；图标用简化图形；标签用低饱和半透明底；模块间用留白+细分隔线
- TabBar 使用微信小程序原生配置，图标为正式资源

## 三、参考基线页面

| 场景 | 页面 |
|------|------|
| 深色 Hero + 悬浮返回 | `pages/role-detail/index` |
| 多卡片表单 | `pages/actor-profile/edit` |
| 剧组编辑 | `pages/company-profile/edit` |
| 视觉基线（已冻结） | `pages/mine/index` |
| 登录交互与禁用态 | `pages/login/index` |

## 四、页面实现经验

### 登录页 — `pages/login/index`

- **类型**: 入口页，不显示返回
- **交互**: 手机号+验证码 / 微信一键登录；未勾协议不可提交（弹提示+抖动）
- **UI**: 深色沉浸 `#121214`；橙色光晕+Logo；深色半透明输入框；橙色主按钮+玻璃态微信按钮
- **坑**: 不用原生 `button disabled`；排查时先确认 `dist/dev` vs `dist/build`

### 角色选择页 — `pages/role-select/index`

- **类型**: 入口页，不显示返回
- **交互**: 点击身份卡片直接写入角色，无二次确认
- **UI**: 浅暖底 `#F6F3EE`；演员橙色暖调 / 剧组深色电影感卡片

### 角色详情页 — `pages/role-detail/index`

- **类型**: 深色 Hero 页，悬浮返回
- **关键**: 返回按钮页面本地实现 `getMenuButtonBoundingClientRect()`；外层 header padding 必须清零
- **三层类名**: `__header` / `__hero` / `__content`
- **坑**: "内容区域往上"指白色主卡片，不是 hero 区

### 演员编辑页 — `pages/actor-profile/edit`

- **类型**: 普通顶部页
- **策略**: 保留深色头部风格 + 表单控件用原生（自定义组件在小程序运行不稳定）
- **结构**: 档案概览卡 → 头像上传卡 → 基本信息卡 → 擅长介绍卡 → 照片墙卡 → 视频简历卡
