# 00-70 当前阶段分享原型 UI 落地（Current Phase Share Prototype UI Implementation）

> 状态：进行中 | 优先级：高 | 依赖：00-28 architecture-driven-delivery-governance，00-62 current-phase-minimal-share-card-mvp-alignment，00-68 current-phase-share-runtime-and-poster-capability-alignment，00-69 current-phase-share-analytics-architecture-refactor
> 记录目的：把用户指定的参考原型 `D:\XM\kaipai-team\_-_.html` 提升为当前前端可见层独立 Spec，明确 7 个原型页与真实路由的映射、视觉边界和分阶段落地顺序，避免继续只改局部页面或让旧页面规范覆盖当前原型方向。

## 1. 背景

当前 `00-69` 已把前端 active 架构收口为：

1. 登录 / 注册
2. 首页
3. 记录
4. 我的
5. 创建分享页
6. 卡片预览
7. 海报预览

与此同时，当前真实可达页面里还保留了三类需要继续统一视觉语言的页面：

- `pages/actor-profile/edit`：档案编辑页
- `pkg-card/verify/index`：实名认证兼容页
- `pages/role-select/index`：历史兼容身份落位页
- `pkg-tools/webview/index`、`pkg-tools/video-player/index`：工具页，虽不在 7 页原型里，但仍是当前 active 路由

但 `00-69` 主要解决的是“当前架构和旧代码删除边界”，并未把用户提供的原型稿提升为独立实现边界。用户随后明确要求：

- 参考 `D:\XM\kaipai-team\_-_.html`
- 重新开发当前页面
- 并要求“创建 specs，然后持续推进”

当前如果不单独建 Spec，会继续出现三类问题：

- 已定义了新架构，但可见层仍混用旧深色玻璃拟态和新的机构版原型语言
- 页面改动只停留在单文件，没有统一定义“参考稿 -> 真实页面”的 7 页映射
- 继续推进时无法区分“架构收口”与“原型 UI 落地”的边界

## 2. 范围

### 2.1 本轮必须处理

- 固化 `_-_.html` 为当前可见层唯一原型参考源
- 明确 7 个原型页与真实小程序页面 / 分包页面的映射
- 将当前前端 active 页面统一到机构版分享平台原型语言
- 将当前仍可达的兼容页一并统一到同一视觉系统，避免主链与兼容页风格断裂
- 将当前仍可达的工具页一并统一到同一视觉系统，避免 active 路由中出现明显异质页面
- 保留现有真实接口、状态、分享与路由逻辑，不允许把页面做成静态壳
- 为后续剩余 2 个预览页继续落地提供明确任务顺序

### 2.2 本轮不处理

- 后台控制台视觉重做
- 后端接口重构
- DevTools 授权问题本身
- 大规模新增交互动画系统
- 用全新静态页替换真实小程序页面

## 3. 需求

### 3.1 原型基线与映射

- **R1** `D:\XM\kaipai-team\_-_.html` 必须被视为当前前端可见层的单一原型基线，后续同轮页面视觉重做默认先对齐该文件，而不是继续沿用旧 page Spec 的历史视觉描述。
- **R2** 本轮必须明确以下 7 个原型页与真实页面的映射：
  - 登录 / 注册 -> `kaipai-frontend/src/pages/login/index.vue`
  - 首页 -> `kaipai-frontend/src/pages/home/index.vue`
  - 记录 -> `kaipai-frontend/src/pages/history/index.vue`
  - 我的 -> `kaipai-frontend/src/pages/mine/index.vue`
  - 创建分享页 -> `kaipai-frontend/src/pkg-card/card-list/index.vue`
  - 卡片预览 -> `kaipai-frontend/src/pages/actor-profile/detail.vue`
  - 海报预览 -> `kaipai-frontend/src/pkg-card/actor-card/index.vue`
- **R2.1** 除 7 个原型页外，当前仍可达的三类兼容 / 支撑页也必须纳入同轮视觉系统收口：
  - 工具页 -> `kaipai-frontend/src/pkg-tools/webview/index.vue`、`kaipai-frontend/src/pkg-tools/video-player/index.vue`
  - 档案编辑 -> `kaipai-frontend/src/pages/actor-profile/edit.vue`
  - 实名认证 -> `kaipai-frontend/src/pkg-card/verify/index.vue`
  - 身份补全兼容页 -> `kaipai-frontend/src/pages/role-select/index.vue`
- **R3** 不允许把 `_-_.html` 直接当作独立营销概览页接入当前小程序；它只作为设计参考和页面实现边界，不作为产品路由新增页面。

### 3.2 视觉语言统一

- **R4** 当前 active 页面必须统一到“机构版分享平台”视觉语言：米白背景、深色封面卡、编辑感排版、浅色 tabbar、轻量信息卡，不再继续沿用旧版全深色玻璃拟态作为当前主风格。
- **R5** 底部 tabBar 当前文案必须收口为：
  - `首页`
  - `记录`
  - `我的`
  不再继续沿用旧 `可分享 / 历史 / 个人中心` 作为当前主文案。
- **R6** 首页必须围绕原型里的“三栏风格分馆 + 快速开始 + 当前默认卡”组织，不再回退到旧广场式列表或旧深色卡片矩阵表达。
- **R7** 记录页必须具备原型里的“筛选胶囊 + 封面卡 + 再次进入”语义结构，而不是只保留简单历史列表。
- **R8** 我的页必须具备原型里的“个人信息 + 我的工作台 + 账号状态 + 退出登录”结构，不再继续沿用旧多业务入口拼盘。
- **R9** 创建分享页必须明确表达“风格卡片管理 + 预览/分享/移除 + 新增卡片”主流程，不得继续停留在旧后台化列表观感。

### 3.3 逻辑与真实链路保护

- **R10** 登录页视觉重做时，必须继续保留真实手机号验证码登录 / 注册、微信登录、邀请绑定、协议勾选与登录后路由分发逻辑，不得因改 UI 而删除真实能力。
- **R11** 首页、记录、我的、创建分享页重做时，必须继续复用当前真实 API / store / helper：
  - `getMyActorProfile`
  - `getMyShareCards`
  - `getShareCardHistory`
  - `createMyShareCard`
  - `shareActorPoster`
  - `loadShareCardLatestSnapshot`
  - `useUserStore`
- **R12** 不允许为了对齐原型而引入伪数据、硬编码假记录或仅存在于本地页面内存的替代状态。

### 3.4 预览页剩余边界

- **R13** 卡片预览页必须由 `pages/actor-profile/detail.vue` 承接，并逐步向原型中的“卡片预览”语义对齐，而不是继续停留在旧演员详情页叙事。
- **R14** 海报预览页必须由 `pkg-card/actor-card/index.vue` 承接，并逐步向原型中的“分享卡片 / 海报切换 + 快速编辑 + 发送”语义对齐，而不是继续停留在旧编辑器导向叙事。
- **R15** 在未完成 `R13-R14` 前，可以先完成 5 个核心入口页，但必须显式记录剩余 2 页仍待继续推进，不能把当前状态误报为“原型已全量落地”。

### 3.5 治理要求

- **R16** 本轮必须通过独立 `00-70` Spec 固化“原型 UI 落地”边界，不能只在聊天里说明“参考某个 html 改页面”。
- **R17** 本轮必须把已完成页面、待继续页面和验证结果回填到 execution 文档，而不是只保留代码改动。
- **R18** 本轮必须把 `00-70` 挂回 Spec 索引、映射表和 `00-28` 治理入口，避免再次出现“旧文档还停留在旧框架”的问题。

## 4. 验收标准

- [x] 已新增独立 `00-70` Spec，并明确依赖 `00-69`
- [x] 已明确 `_-_.html` 与 7 个真实页面的映射关系
- [x] 已完成 5 个核心入口页首轮落地：`login / home / history / mine / card-list`
- [x] 已完成 `actor-profile/detail` 的卡片预览语义对齐
- [x] 已完成 `pkg-card/actor-card` 的海报预览语义对齐
- [x] 已完成 `actor-profile/edit / verify / role-select` 的同风格视觉系统收口
- [x] 已完成 `pkg-tools/webview / pkg-tools/video-player` 的同风格视觉系统收口
- [x] 已记录首轮类型检查与小程序构建验证结果
- [x] 已回填索引、映射与 `00-28` 治理入口
