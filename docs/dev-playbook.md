# 开发经验手册

> 项目开发中沉淀的高频问题、视觉基线和页面实现经验。
> 技术约定见 `.sce/specs/SHARED_CONVENTIONS.md`，开发原则见 `.sce/steering/CORE_PRINCIPLES.md`。

## 一、高频问题速查

| # | 问题 | 根因 | 修复 |
|---|------|------|------|
| 1 | 页面改了用户看到旧页面 | DevTools 未打开最新 `dist/dev/mp-weixin`，或 `build -> dev` 同步后仍在旧缓存工程 | 重新 build → 固定打开 `dist/dev/mp-weixin` → 必要时清缓存重编译 |
| 2 | 改错 CSS 锚点 | 没先拆三层就凭类名猜 | 先定位导航/Hero/Content哪层，一次只改一层 |
| 3 | 返回按钮与胶囊不一致 | 只复制按钮DOM没复制容器 | 三件套整体复制（参考 `utils/floating-back-nav.ts` + `KpCapsuleSpacer`） |
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
| 视觉基线（已冻结） | `pages/mine/index` |
| 多卡片表单 | `pages/actor-profile/edit` |
| 登录交互与禁用态 | `pages/login/index` |
| 首页 Hero + 模板网格 | `pages/home/index` |
| 分步向导 | `pkg-actor-card/step-visual/index` |
| 列表 + 空态 | `pages/card-list/index` |

> `pages/role-detail/index`、`pages/company-profile/edit`、`pages/role-select/index` 已随剧组域退场删除（`00-209`），
> 不再作为参考基线。悬浮返回三件套现由 `utils/floating-back-nav.ts` + `components/KpCapsuleSpacer.vue` 收口。

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

### 首页 — `pages/home/index`

- **类型**: tab 页，不显示返回；`pages.json` 已开 `enablePullDownRefresh`
- **结构**: 「AI 创建演员卡」Hero 卡 → 「模板创建」风格 tab（经典/都市/古风/清新）→ 模板网格
- **数据**: tab 切换即过滤网格，数据来自 `GET /api/actor-card/background-library?style=`；按风格内存缓存，切回不重复请求
- **坑**:
  - 该接口不在 `SecurityConfig` 白名单，游客态拿不到数据，必须给登录引导空态，不能只转圈
  - 开了 `enablePullDownRefresh` 就必须写 `onPullDownRefresh` 并显式 `uni.stopPullDownRefresh()`，否则下拉圈不收起
  - 风格值属于「向导 style」词表，不可与分享卡场景码混用（见下）

### 两套风格词表不可混用

| | 向导 style | 分享卡 scene |
|---|---|---|
| 取值 | `classic\|urban\|ancient\|fresh` | `classic\|costume\|urban\|commercial\|artistic` |
| 权威来源 | `actor_card.style` / `actor_card_background.style` 的 DDL 注释与 seed 数据 | `TemplateSceneCodeValidator` |
| 使用方 | `step-visual`、`card-list`、首页模板网格 | `/api/card/scene-templates`、`share-card-mvp.ts` |

两套只在 `classic` / `urban` 上重合。首页点击写的是 `actor_card.style`，所以首页只能用向导 style；
误用 scene 码会让 `step-visual` 按 `costume` 查背景库、命中 0 条 seed，表现为图库空且无 tab 高亮。

### 分步向导 — `pkg-actor-card/step-*`

- **类型**: 分包内串行向导，`create → step-visual → step-profile → ... → generate`
- **关键**: 每步 `draftStore.saveStep()` 落草稿后再 `navigateTo` 下一步，靠 `cardId` 串联
- **坑**: `step-visual` 是 `actor_card.style` 的唯一写入方，改风格词表必须同时核这一页

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
- 当前基线（2026-08-09 实测，按 apparent size 统计，不用 `du` 默认块大小）：

  | 包 | 体积 | 说明 |
  |----|------|------|
  | 主包 | `442.5 KB` | 限额 `2048 KB`，余量 `1605.5 KB` |
  | `pkg-actor-card` | `81.3 KB` | 演员卡 9 步向导 |
  | `pkg-profile` | `80.7 KB` | `import-review / assets` |
  | `pkg-tools` | `39.2 KB` | `webview / video-player` |
  | `pkg-card` | `31.6 KB` | 仅剩 `verify` |
  | 合计 | `675.3 KB` | |

- 当前主包页面（6 个，以 `pages.json` 为准）：
  `home / login / actor-profile/edit / mine / card-list / assets`
- 分包实际构成以 `pages.json` 的 `subPackages` 为准；旧文档里的
  `style-detail / membership / invite / role-select / role-detail` 均已不存在，不要再作为分包清单沿用
- 后续新增功能默认先做分包判断：
  若模块具备独立入口、非 tab、预计持续增长，则优先新建独立分包
- 后续新增功能默认先做分包判断：
  若模块具备独立入口、非 tab、预计持续增长，则优先新建独立分包
- 若要做真实分包，必须先盘点所有路由引用点和分享路径，不能直接改 `pages.json` 后再补救
