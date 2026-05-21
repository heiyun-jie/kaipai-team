# 00-73 当前阶段前台参考稿 UI 与架构重构（Current Phase Reference UI Architecture Rebuild）

> 状态：进行中 | 优先级：最高 | 依赖：00-27 mini-program-frontend-architecture，00-28 architecture-driven-delivery-governance，00-69 current-phase-share-analytics-architecture-refactor，00-70 current-phase-share-prototype-ui-implementation
> 记录目的：把用户最新明确的“参考 `D:\XM\kaipai-team\_-_.html` 的 UI 和架构重新整体进行重构，且帧级 UI 一比一复刻”提升为独立 Spec，区分于 `00-70` 的首轮同风格落地，明确这一次不再只是改配色 / 改文案，而是要按参考稿的 7 屏流和路由职责重新收口当前前台 active 主链。

## 1. 背景

当前前台已经存在两层既有事实：

1. `00-69` 已定义当前阶段前台 active 架构边界，明确小程序主线应围绕：
   - 登录 / 注册
   - 首页
   - 记录
   - 我的
   - 档案编辑
   - 创建 / 编辑分享
   - 分享详情
2. `00-70` 已把 `D:\XM\kaipai-team\_-_.html` 做过一轮真实页面映射与视觉收口。

但用户随后继续明确了更严格的目标：

- 不是“同风格落地”
- 而是“参考稿 UI 和架构重新整体重构”
- 且要求“帧级 UI 一比一复刻”

截至 `2026-04-21`，用户又在当前线程补充了一组逐页 reference 截图，已明确覆盖：

- 登录页
- 首页
- 创建分享页
- 卡片预览
- 海报预览
- 我的页

这意味着此前仅依赖 `D:\XM\kaipai-team\output\playwright\reference-full.png` 总览裁切图做局部推断已经不够；后续同轮页面验收必须按“逐页 reference 截图 > `_-_.html` 总览裁切推断”的优先级执行。

经核对，当前代码仍存在两类明显漂移：

### 1.1 可见层漂移

当前多页已经进入同一套暖米白 / 深色标题块视觉语言，但仍有大量地方只是“风格接近”，并没有按参考稿的页面结构、区块顺序、按钮关系、标题层级和屏内节奏做到 1:1。

### 1.2 路由职责漂移

参考稿的 7 个核心 screen flow 为：

1. 登录 / 注册
2. 首页
3. 记录
4. 我的
5. 创建分享页
6. 卡片预览
7. 海报预览

而当前前台代码里，`创建 / 卡片预览 / 海报预览` 仍分散在历史职责较重的页面上：

- `pkg-card/card-list/index.vue`
- `pages/actor-profile/detail.vue`
- `pkg-card/actor-card/index.vue`

这使得当前实现更像“把参考稿语言套到旧页面职责上”，而不是“按参考稿 flow 重新收口前台主链”。

因此，本轮不应继续把工作记在 `00-70` 的“首轮原型 UI 落地”里；更合理的做法是新增一个后续 Spec，专门承接：

- 前台 reference UI 的 frame-level 复刻
- 前台 creator chain 的 route ownership 重构
- `00-69 -> 00-70 -> 00-73` 的主线 handoff

## 2. 范围

### 2.1 本轮必须处理

- 固化 `D:\XM\kaipai-team\_-_.html` 为当前前台 active 主链的唯一 UI / screen-flow 参考基线
- 把 reference 的 7 个 screen state 映射回当前真实小程序 active 路由
- 收口 `create / card preview / poster preview` 的页面职责
- 把“帧级一比一复刻”落实为可执行的页面视觉合同，而不是泛化成“同风格”
- 把 supporting routes 的角色明确为：
  - 兼容支撑页
  - reference 外辅助页
  - 公开详情页
- 回填 Spec 索引、Spec↔代码映射和 steering 当前上下文

### 2.2 本轮不处理

- 后台控制台视觉重构；后台继续以 `00-71 / 00-72` 为准
- 后端接口、埋点口径和统计模型新增
- 微信开放能力扩展
- 重新开启 legacy 招募 / 投递 / 剧组主线
- 用静态原型页替换真实前台页面

## 3. 需求

### 3.1 参考基线与适用范围

- **R1** `D:\XM\kaipai-team\_-_.html` 必须被视为当前前台 active 主链的唯一参考基线；后续同轮前台 UI 修改默认先对齐该文件，而不是继续沿用首轮实现里的局部变体。
- **R2** 本 Spec 处理的是 reference 中明确出现的 7 个核心 screen flow，而不是把 `_-_.html` 仅视为一个配色板或单页静态效果图；若当前线程已补充某页的逐页 reference 截图，则该截图对该页的 block order、CTA、内容密度与信息架构拥有高于总览裁切图的优先级。
- **R3** 本 Spec 只适用于 `D:\XM\kaipai-team\kaipai-frontend` 的当前 active 前台主链，不覆盖后台 `_-_1.html` 对应的控制台参考稿。
- **R4** reference 中默认 `studio + serif-sans` 的视觉语法必须成为本轮默认可见层基线，至少包括：
  - 暖米白背景
  - 深墨文字
  - 金棕强调色
  - serif display + sans body 的标题 / 正文分工
  - iPhone 画布式 safe-area / capsule / tabbar 结构
- **R5** 若小程序运行时受字体能力限制，允许使用本地可用 serif fallback 替代 reference Web 字体，但这种差异必须被显式记录，不能直接当成“已 1:1”。

### 3.2 当前前台主架构

- **R6** 当前前台 visible 主链必须继续围绕 reference 的 7 个 screen state 组织：
  - 登录 / 注册
  - 首页
  - 记录
  - 我的
  - 创建分享页
  - 卡片预览
  - 海报预览
- **R7** 底部 tabbar 当前阶段只允许保留：
  - 首页
  - 记录
  - 我的
- **R8** `创建分享页` 当前必须由 `pkg-card/card-list/index` 承接，页面语义以 reference 的 `CreateScreen` 为准，不再继续保留“列表管理页优先、创建流只是附属入口”的旧心智。
- **R9** `卡片预览 / 海报预览` 当前必须由 `pkg-card/actor-card/index` 统一承接，可通过内部 mode / artifact state 实现两个 screen state，但 visible contract 必须分别对齐 reference 的 `CardPreviewScreen / PosterPreviewScreen`。
- **R10** `pages/actor-profile/detail` 不得继续被当成内部 creator preview 的默认承担页；它只能被定义为：
  - 公开分享详情页
  - 外部进入兼容页
  - reference 外支撑页
- **R11** `pages/actor-profile/edit`、`pkg-card/verify`、`pages/role-select`、`pkg-tools/webview`、`pkg-tools/video-player` 可以继续保留，但只能被定义为 support routes，不计入 reference 的 7 个核心 screen。

### 3.3 帧级页面合同

- **R12** 登录页必须对齐 reference `LoginScreen` 的结构合同：
  - 上半屏完整封面图 + 底部渐隐
  - 居中品牌识别 `brandLatin / brandName / 机构版 · 分享平台`
  - 底部单栏表单
  - 手机号输入 + 验证码输入
  - 单一主 CTA `登录 / 注册`
  - 微信一键登录
  - 协议区
  - 不允许继续混入 editorial 版辅助栏、mode tabs、flow note 等 reference 外结构
- **R13** 首页必须对齐 reference `HomeScreen` 的结构合同：
  - 顶部品牌 strap
  - serif 主标题
  - 细条数据摘要
  - `风格分馆 / SELECT A STYLE`
  - 三列风格卡
  - 视频教程区
  - `三步创建你的分享页`
  - `01 选风格 / 02 传作品 / 03 成海报`
  - 底部主 CTA `开始创建分享页`
- **R14** 记录页必须对齐 reference `RecordsScreen` 的结构合同：
  - `MY · RECORDS` strap
  - serif 主标题 `曾打开的分享`
  - 分馆筛选胶囊
  - 封面 + 标题 + studio + tag + 打开次数 + 时间的列表卡
  - 若当前尚无单页 reference，则继续以 `_-_.html` 总览截图与 `reference-full / reference-overview` 里的 records 画面为临时页级基线，直到用户补充单页图
- **R15** 我的页必须对齐 reference `MyScreen` 的结构合同：
  - 头像 + 姓名 + 机构 / 用户信息
  - 编辑按钮
  - `我的数据` 卡
  - 趋势线与 `卡片 / 海报 / 再进入` 子统计
  - 双主动作卡
  - `创建分享 + 我的二维码`
  - 设置列表
  - `我的作品集 / 收藏的分享 / 消息通知 / 偏好设置`
  - 退出登录
- **R16** 创建分享页必须对齐 reference `CreateScreen` 的结构合同：
  - 返回头
  - `01 / 02 / 03` 步骤条
  - `STEP 01` 三风格卡选择块
  - `STEP 02` 上传作品网格
  - 固定底部 CTA `生成分享卡片`
  - `STEP 03` 标题输入 + `卡片 / 海报` 分享形式卡
- **R17** 卡片预览必须对齐 reference `CardPreviewScreen` 的结构合同：
  - 返回按钮 + 页标题 + `切到海报`
  - 类微信聊天背景预览区
  - 聊天气泡 + 分享卡片组合
  - `QUICK EDIT`
  - 底部 `复制链接 / 发送给好友`
- **R18** 海报预览必须对齐 reference `PosterPreviewScreen` 的结构合同：
  - 深色外部背景
  - 返回按钮 + 页标题 + `切到卡片`
  - 浅色竖版海报舞台
  - 大图 + 双小图
  - 二维码 footer
  - 底部 `保存相册 / 分享到朋友圈`

### 3.4 Shared visual contract

- **R19** 本轮不得再以“同色系即可”替代 frame-level 复刻；至少需要统一以下可见层 contract：
  - 顶部状态条 / capsule 位置关系
  - 24px 级横向留白节奏
  - 34px back chip / action chip
  - frosted tabbar 结构
  - pill / button / card radius
  - serif headline + sans body 的层级分工
- **R20** reference 的 `studio` 主题色值必须成为默认 token 基线，至少包括：
  - bg: `#F5F3EE`
  - surface: `#FBFAF6`
  - surface2: `#EEEBE3`
  - ink: `#1A1816`
  - accent: `#8C6F4F`
- **R21** 旧 editorial 登录页残留、旧后台式 summary 结构、旧分享管理桌面语言和 reference 外实验性区块，不得继续混入 7 个 core screens。

### 3.5 治理与验证

- **R22** 本轮必须通过独立 `00-73` Spec 固化 reference-driven 的前台 UI / 架构二次收口边界，不能继续只在 `00-70` 内口头追加说明。
- **R23** 本轮必须把 `00-73` 回填到 `.sce/specs/README.md`、`.sce/specs/spec-code-mapping.md` 和 `.sce/steering/CURRENT_CONTEXT.md`。
- **R24** 小程序运行态验证与结果汇报必须继续以 `D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin` 为主口径；`dist\build\mp-weixin` 仅作为构建产物核对，不再作为主要验收口径。
- **R25** 每个 core screen 的最终验收必须至少同时覆盖：
  - `src`
  - `dist\build`
  - `dist\dev`
  - 微信开发者工具 / 真机运行态截图
- **R26** 若因为运行时字体、组件限制、数据事实源或微信能力约束导致无法完全与 reference 等价，必须在 `execution.md` 里逐条记录边界，不能笼统宣称“已 1:1”。
- **R27** 当前前台 UI 整理必须持续采用“reference 截图 ↔ 当前运行态截图”对照推进；没有截图证据时，只能视为实现中，不能直接判定为视觉完成。
- **R28** 对同一页面、同一可见块、同一类问题，若连续 3 次调试仍未让运行态截图产生用户可感知的正确变化，必须自动更换方向，不能继续在原方向上做第 4 次同类试错。
- **R29** `更换方向` 至少包括以下动作之一：
  - 从样式数值微调切换为结构重排
  - 从源码猜测切换为 `src / dist/build / dist/dev / DevTools` 四层核对
  - 从单页局部修改切换为 shared component / token / route ownership 收口
  - 从继续改样式切换为先补截图、先核 reference、先确认运行态工程路径
- **R30** 每次触发第 3 次失败后的自动换向，都必须在 `execution.md` 里显式记录：
  - 当前页面
  - 当前可见块
  - 已失败的 3 次尝试口径
  - 新的推进方向
  - 为什么原方向不再继续
- **R31** 后续每一轮属于 `00-73` 范围内的 UI 修改，在改代码前必须先重新读取当前 Spec 的：
  - `requirements.md`
  - `design.md`
  - `tasks.md`
  - `execution.md` 中与当前页面 / 当前可见块相关的最近执行链
  若未完成上述读取，不得直接进入样式修改。
- **R32** 若某次 UI 修改仍属于 `00-73` 已覆盖的页面与链路范围，不得再跳过当前 Spec 另起口头流程；应优先把需求、差异、锚点和结论回填到现有 `00-73`，而不是脱离 Spec 单独推进。
- **R33** `00-73` 必须显式记录当前前台 UI 的执行规范，至少包括：
  - 页面 route
  - reference 基线路径
  - 当前运行态截图路径
  - 当前可见块
  - 预期变化
  - 保持不动项
  - 直接视觉锚点 class / wrapper
  - 四层核验要求（`src / dist\build / dist\dev / DevTools`）
- **R34** 每次用户补充新的页级截图、红框、局部 continuation 或明确指出新的 frame-level 差异时，必须先把该截图对应的页面合同与锚点结论回填到现有 Spec，再继续后续 UI 修改；不能只在对话里临时记忆。
- **R35** 任何一轮 UI 修改若没有同时说明：
  - 本轮使用了哪些 Spec 依据
  - 为什么选择当前锚点
  - 当前不改哪些块
  则不得汇报为“已修”或“已对齐 reference”。

## 4. 验收标准

- [ ] 已新增独立 `00-73` Spec，并明确其与 `00-70` 的边界不同
- [ ] 已明确 reference 的 7 个 screen state 与真实 active 路由的映射关系
- [ ] 已明确 `card-list / actor-card / actor-profile/detail` 的目标职责分层
- [ ] 已把 login / home / records / mine / create / card preview / poster preview 的 frame-level 合同写成可执行需求
- [ ] 已把用户补充的逐页 reference 截图组并入 `00-73`，并明确页级基线优先级
- [ ] 已把 reference 视觉 token、safe-area、tabbar 和 button/pill/card contract 固化到设计层
- [ ] 已回填 Spec 索引、Spec↔代码映射与 CURRENT_CONTEXT
- [ ] 已把“每轮 UI 修改必须先读 Spec、先记页面合同、再改代码”的执行门禁写入 `00-73`
