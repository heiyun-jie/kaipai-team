# 开发经验手册

> 项目开发中沉淀的高频问题、视觉基线和页面实现经验。
> 技术约定见 `.sce/specs/SHARED_CONVENTIONS.md`，开发原则见 `.sce/steering/CORE_PRINCIPLES.md`。

## 一、高频问题速查

| # | 问题 | 根因 | 修复 |
|---|------|------|------|
| 1 | 页面改了用户看到旧页面 | DevTools 未打开最新 `dist/dev/mp-weixin`，或 `build -> dev` 同步后仍在旧缓存工程 | 重新 build → 固定打开 `dist/dev/mp-weixin` → 必要时清缓存重编译 |
| 2 | 改错 CSS 锚点 | 没先拆三层就凭类名猜 | 先定位导航/Hero/Content哪层，一次只改一层 |
| 3 | 返回按钮与胶囊不一致 | 只复制按钮DOM没复制容器 | 三件套整体复制（参考 role-detail） |
| 4 | WXSS/WXML 编译报错 | 不兼容小程序的选择器 | 以小程序兼容为先，看生成 `.wxml`/`.wxss` |
| 5 | `common/assets.js is not defined` | 产物不完整 | 删 dist → 重新 build → 重新打开 |
| 6 | 按钮点不到/文案不居中 | 原生 `disabled` 被微信接管 | 保留点击，条件不满足时事件内提示 |
| 7 | 自定义组件小程序运行不稳定 | 组件抽象过深 | 复杂表单回到原生 input/textarea/picker |
| 8 | 登录后全局状态不更新 | 没同步写 token + userInfo | 登录后同写；保存后调 `updateProfile()` |
| 9 | 上传体验版失败 | 账号无开发者权限 | 用有权限账号登录 DevTools |
| 10 | 同一个 UI 问题改了 3 次还没变化 | 方向错了，不是值不够大 | 第 3 次失败后自动换方向：先停同类试错，改做截图复核 / 结构重排 / 运行态工程核对 |

## 二、文档治理基线

- `docs/product-design.md` 只保留当前主线，不混写历史方案
- 历史产品文档统一归档到 `docs/archive/`
- 当前项目主线以后台 `00-140 / 00-141 / 00-142` 为准；继续做后台架构、模板配置、旧能力退场时，先读 `CURRENT_CONTEXT.md`
- 小程序前端整体架构总纲以 `00-27 mini-program-frontend-architecture` 为准
- 项目推进治理以 `00-28 architecture-driven-delivery-governance` 为准，按能力切片而不是单页面任务排开发
- 小程序前台历史业务主线不得直接沿用；已退场的外部个性化输入域由 `00-149` 物理退场
- `05-03 credit-score` 仅作历史保留，不再作为当前功能范围
- 小程序包体治理以 `00-05 mini-program-package-governance` 为准
- 页面、组件、API、types、utils 的事实数量以仓库当前文件数为准，不凭旧文档沿用
- 文档治理与代码治理同轮闭环，主线切换时同步更新主文档、Spec 索引和映射

## 三、视觉语言基线

以 `pages/mine/index`（已冻结）为参考：

- 深色头部 `#121214`，可叠低透明度橙色/白色光斑
- 强调色橙色渐变，用于主按钮/标签/进度条
- 白卡大圆角、轻阴影，深色头部+白卡叠层
- 主操作按钮固定底部，高度偏大
- 导航栏极简白字；图标用简化图形；标签用低饱和半透明底；模块间用留白+细分隔线
- TabBar 使用微信小程序原生配置，图标为正式资源

## 四、参考基线页面

| 场景 | 页面 |
|------|------|
| 深色 Hero + 悬浮返回 | `pages/role-detail/index` |
| 多卡片表单 | `pages/actor-profile/edit` |
| 剧组编辑 | `pages/company-profile/edit` |
| 视觉基线（已冻结） | `pages/mine/index` |
| 登录交互与禁用态 | `pages/login/index` |

## 五、页面实现经验

### UI 页面持续整理默认循环

当前小程序 UI 页面整理默认按以下顺序推进：

1. 看 reference 截图
2. 看当前运行态截图
3. 拆当前可见块与真实视觉锚点
4. 只做一轮窄改
5. `npm run build:mp-weixin`
6. 核对：
   - `src`
   - `dist/build/mp-weixin`
   - `dist/dev/mp-weixin`
7. 再看运行态截图

没有截图对比证据时，只能说“已改代码”，不能说“页面已完成”。

### UI 调试三次失败自动换向

对同一页面、同一可见块、同一类问题：

- 如果连续 3 次调试后，运行态截图仍没出现用户要的正确变化
- 则不再做第 4 次同类试错
- 必须自动换方向继续推进

优先换向方式：

1. 从继续调数值，改为重拆 block order / 结构容器
2. 从只看 `src`，改为核 `dist/build / dist/dev / DevTools`
3. 从单页私有样式，改为 shared component / token 收口
4. 从继续猜样式，改为先确认 reference 与当前 route ownership 是否不一致

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

## 六、小程序包体治理

- 微信小程序默认约束：单包不超过 `2 MB`
- 包体检查不能只看源码目录，必须看 `kaipai-frontend/dist/build/mp-weixin`
- 推荐验证顺序：
  `npm run build:mp-weixin` → `npm run audit:mp-package` → 微信开发者工具固定打开 `kaipai-frontend/dist/dev/mp-weixin`
- 路径统一规则：
  - `dist/build/mp-weixin`：内部构建源目录，只用于核对“最新编译产物是否正确生成”
  - `dist/dev/mp-weixin`：微信开发者工具固定工程目录，只用于实际运行和人工验收
- 当前基线：
  2026-03-31 审计结果为主包 `517.65 KB`，`pkg-card 86.81 KB`，`pkg-tools 18.80 KB`
- 当前建议保留主包的页面：
  `login / role-select / home / mine / role-detail / actor-profile/edit` 等启动即达或基础链路页
- 当前演员增强主线分包：
  `actor-card / card-list / style-detail / membership / verify / invite`
- 当前工具分包：
  `webview / video-player`
- 后续新增功能默认先做分包判断：
  若模块具备独立入口、非 tab、预计持续增长，则优先新建独立分包
- 若要做真实分包，必须先盘点所有路由引用点和分享路径，不能直接改 `pages.json` 后再补救
