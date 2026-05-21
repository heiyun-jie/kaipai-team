# 00-73 设计说明

## 1. 设计目标

`00-73` 不是继续给 `00-70` 做零散微调，而是把当前前台小程序从“首轮同风格落地”推进到“按 `D:\XM\kaipai-team\_-_.html` 的 7 屏流和页面职责做二次收口”。

本轮设计目标分成两层：

1. **screen fidelity**：把 7 个 core screens 的 visible contract 收到 reference 同一层级，不再停留在“色系接近”
2. **route ownership**：把 `create / card preview / poster preview` 的真实路由职责重新收口，避免 reference UI 继续挂在旧职责页面上

## 2. 参考事实与证据

### 2.1 已核实的 reference 文件

- `D:\XM\kaipai-team\_-_.html`

### 2.2 已核实的 reference 截图

- `D:\XM\kaipai-team\output\playwright\reference-overview.png`
- `D:\XM\kaipai-team\output\playwright\reference-full.png`

### 2.3 用户补充的逐页 reference 基线

截至 `2026-04-21`，用户在当前线程又补充了一组逐页 reference 截图，已明确覆盖：

- 登录页
- 首页（含下半屏 continuation）
- 创建分享页（含 step 02 / step 03 continuation）
- 卡片预览
- 海报预览
- 我的页

当前设计结论：

- 对上述页面，后续页级 block order、CTA、信息架构验收必须优先以用户补充的逐页截图为准
- `D:\XM\kaipai-team\output\playwright\reference-full.png` 与 `reference-overview.png` 继续作为总览、屏流和 records 页的临时视觉基线
- records 页在拿到单页 reference 前，仍只能按总览图里的 `RecordsScreen` 做页级对照

### 2.4 已核实的 reference 组件合同

通过对 `_-_.html` 内嵌 bundler manifest 的解码，已确认 reference 真实包含以下 screen/component：

- `LoginScreen`
- `HomeScreen`
- `RecordsScreen`
- `MyScreen`
- `CreateScreen`
- `CardPreviewScreen`
- `PosterPreviewScreen`
- `WXPhone`
- `BottomTabs`

这说明：

- reference 不是单纯的静态展示板
- 它自身已经表达了一套 7 屏 flow + device shell + shared component contract
- 后续若单页 reference 与总览裁切推断存在冲突，应以单页 reference 为准

## 3. 当前代码与目标架构

### 3.1 当前 active 路由事实

当前 `D:\XM\kaipai-team\kaipai-frontend\src\pages.json` 的 active 前台路由为：

- `pages/login/index`
- `pages/role-select/index`
- `pages/home/index`
- `pages/actor-profile/edit`
- `pages/history/index`
- `pages/mine/index`
- `pages/actor-profile/detail`
- `pkg-card/actor-card/index`
- `pkg-card/verify/index`
- `pkg-card/card-list/index`
- `pkg-tools/webview/index`
- `pkg-tools/video-player/index`

### 3.2 目标 screen ↔ route mapping

| Reference screen | 真实路由 | 目标职责 | 备注 |
|------|------|------|------|
| 01 登录 / 注册 | `pages/login/index` | 完整承接 `LoginScreen` | 必须去掉 reference 外结构 |
| 02 首页 | `pages/home/index` | 完整承接 `HomeScreen` | 保留 tab 首页角色 |
| 03 记录 | `pages/history/index` | 完整承接 `RecordsScreen` | 语义上按 records，而不是旧 history 混合页 |
| 04 我的 | `pages/mine/index` | 完整承接 `MyScreen` | 保留 tab 我的角色 |
| 05 创建分享页 | `pkg-card/card-list/index` | 承接 `CreateScreen` | 从“列表管理优先”收口为“creator entry 优先” |
| 06 卡片预览 | `pkg-card/actor-card/index` | 承接 `CardPreviewScreen` | 通过 `artifact=card` 或等价状态进入 |
| 07 海报预览 | `pkg-card/actor-card/index` | 承接 `PosterPreviewScreen` | 通过 `artifact=poster` 或等价状态进入 |

### 3.3 support routes 边界

| 路由 | 角色 | 设计要求 |
|------|------|------|
| `pages/actor-profile/detail` | 公开 / 外部进入详情页 | 退出 creator preview 主链，只保留公开 / 兼容职责 |
| `pages/actor-profile/edit` | 档案编辑页 | 继承 reference token 与节奏，但不强行塞进 7 屏 |
| `pkg-card/verify/index` | 实名认证支撑页 | 同上 |
| `pages/role-select/index` | 历史兼容身份落位页 | 同上 |
| `pkg-tools/webview/index` | 协议说明工具页 | 同上 |
| `pkg-tools/video-player/index` | 视频预览页 | 同上 |

### 3.4 路由职责修正原则

- creator internal flow 不再通过 `pages/actor-profile/detail` 表达
- `pkg-card/actor-card/index` 继续承接 preview，但必须变成 reference 明确的两种 preview state
- `pkg-card/card-list/index` 优先表达创建流，而不是“旧风格卡片管理桌面”

## 4. Shared visual contract

### 4.1 颜色 token（reference `studio` 默认主题）

| Token | 值 | 用途 |
|------|------|------|
| `bg` | `#F5F3EE` | 页面主背景 |
| `surface` | `#FBFAF6` | 卡片、输入、浅层容器 |
| `surface2` | `#EEEBE3` | 轻层级辅助背景 |
| `ink` | `#1A1816` | 主标题、主按钮、深色内容 |
| `muted` | `rgba(26,24,22,0.52)` | 次文本 |
| `border` | `rgba(26,24,22,0.1)` | 边框 |
| `accent` | `#8C6F4F` | 强调色、统计高亮、次 CTA |

### 4.2 字体策略

reference Web 端默认 `serif-sans` 组合是：

- display: `Noto Serif SC / Playfair Display`
- body: `Noto Sans SC`

当前小程序设计策略：

- display token 使用本地 serif fallback，优先：
  - `"Songti SC", "STSong", "Baskerville", serif`
- body token 继续使用系统 sans：
  - `-apple-system, BlinkMacSystemFont, "PingFang SC", "Helvetica Neue", sans-serif`

原因：

- 当前 reference 使用的是 Web 字体与 Google Fonts
- 小程序不能直接照搬网络字体方案
- 当前阶段优先保住版式与层级，其次再评估是否值得引入本地字体资源

### 4.3 390px → rpx 设计换算

reference 的 device shell 以 `390px x 844px` iPhone 画布为基准。

小程序落地时统一按：

- `390px -> 750rpx`
- 比例系数约 `1px = 1.923rpx`

实现原则：

- 外层间距、按钮尺寸、标题字号、图片区块高度都按同一比例映射
- 不允许不同页面各自凭感觉放大 / 缩小

### 4.4 关键共享尺寸

| Reference metric | px | 落地参考 |
|------|------|------|
| 横向主留白 | 24px | 约 `46rpx` |
| 小圆 back/action chip | 34px | 约 `65rpx` |
| login 输入 padding | 14px × 18px | 约 `27rpx × 35rpx` |
| login brand title | 44px | 约 `85rpx` |
| home 主标题 | 30px | 约 `58rpx` |
| records 标题 | 26px | 约 `50rpx` |
| mine 主统计数字 | 34px | 约 `65rpx` |

### 4.5 shared component contract

本轮必须统一以下共享语法：

- 顶部状态条 / capsule
- frosted tabbar
- pill filter
- 主按钮 `primary / accent / ghost / light`
- 卡片圆角与边框
- section strap / serif title / mono side label

优先复用 / 收口的前台共享文件：

- `D:\XM\kaipai-team\kaipai-frontend\src\styles\_tokens.scss`
- `D:\XM\kaipai-team\kaipai-frontend\src\styles\index.scss`
- `D:\XM\kaipai-team\kaipai-frontend\src\components\KpButton.vue`
- `D:\XM\kaipai-team\kaipai-frontend\src\components\KpPillSelector.vue`
- `D:\XM\kaipai-team\kaipai-frontend\src\components\KpSectionHead.vue`

## 5. 页面级设计策略

### 5.1 login / home / records / mine

这四页属于 reference 最明确的 tab / entrance contract：

- 先按 screen-level 结构做 1:1
- 再把真实数据 / 真实 CTA 填进去
- 不允许因为已有逻辑而反过来改 reference block order

### 5.1.1 基于用户补充逐页 reference 的已知差异

截至 `2026-04-21`，对当前运行态与逐页 reference 的对照结论如下：

| 页面 | 单页 reference 是否已补齐 | 当前已知差异 | 推进结论 |
|------|------|------|------|
| `login` | 是 | 当前仅有结构合同，尚缺运行态截图复核 | 先补运行态截图，再决定是否窄改 |
| `home` | 是 | 当前实现虽已进入同色系与同标题语法，但尚未完整落出 `三列风格卡 + 教程说明 + 三步胶囊 + 底部主 CTA` | 重新打开页面级实现任务 |
| `history` | 否 | 当前仍只能按总览图里的 `RecordsScreen` 做对照，空态与真实列表态的验收边界未完全稳定 | 暂保留现有合同，待补单页 reference 或运行态列表样本 |
| `mine` | 是 | 当前实现仍是“个人档案 / 创建分享 + 认证等级类设置项”，与 reference 的“创建分享 / 我的二维码 + 收藏/消息/偏好设置”信息架构不一致 | 重新打开页面级实现任务 |

### 5.1.2 support routes 不再混入 core reference 验收

用户补充的逐页 reference 组没有覆盖：

- `actor-profile/edit`
- `verify`
- `role-select`
- `webview`
- `video-player`

因此这些页面的推进口径应固定为：

- 继承同一套 token、间距、按钮与卡片语法
- 去掉旧 `SCREEN xx / XXX DESK` 叙事
- 不再拿来冒充 7 个 core screens 的 1:1 验收对象

### 5.1.3 `home / 操作指南` 的 block-level frame contract

当前 `home` 页的 `操作指南` 不能再只按“让 CTA 挤进首屏”推进，而必须按用户补充的红框 reference 做 block-level 收口。

该区块当前固定理解为一个完整 frame block：

1. section head
   - `操作指南`
   - `HOW-TO · 02:34`
2. video stage
3. three pills
4. primary CTA
5. CTA 下方到 tabbar 上方的可见白色留白

后续对该块的执行规范固定为：

- **先看整块 frame，再看单个子元素**
  - 不能把问题直接简化成“继续改 CTA”或“继续改 stage”
- **video stage 必须接近 reference 的 16:9 舞台感**
  - 不得再次压成短横幅式 banner
- **section head / stage / pills / CTA 的垂直节奏必须按 reference 收口**
  - 不得再为了追求“首屏完整露出 CTA”而把各子块间距压到异常低值
- **左右 frame 必须继续跟随首页主留白体系**
  - 默认以页面横向主留白为基线
  - 不单独在 guide block 里再造一套更窄或更宽的左右边距
- **CTA 下方白色留白是独立验收项**
  - 它由页面内容外框与底部安全区共同决定
  - 不能再误判为 `guide-cover` 自身高度问题

因此该块的默认排障顺序固定为：

1. 先确认 reference 红框到底指的是：
   - stage 比例
   - 子块垂直节奏
   - CTA 下方外框留白
   - 左右 frame
2. 再判断真实锚点属于：
   - `home-page__section--guide`
   - `home-page__guide-cover`
   - `home-page__body`
   - DevTools 可见运行态错位
3. 最后才允许进入样式数值修改

### 5.1.4 `home / hero + stats + styles` 首屏 frame contract

在 `操作指南` 下半屏已经接近 reference 之后，`home` 页当前最高优先级的可见差异已切回首屏 frame，而不是继续对 `guide` 内部做第 N 轮微调。

该首屏 block 固定理解为：

1. capsule / safe-area 保留区
2. `JU MING PIAN · STUDIO`
3. serif 主标题 `为每一次相遇 / 留下光影`
4. 副标题 `选择风格，创建属于你的分享页`
5. 细条 stats strip
6. `风格分馆 / SELECT A STYLE`
7. 三列风格卡第一屏完整露出

基于 `D:\XM\kaipai-team\_-_.html` 的 HomeScreen DOM，当前 reference 首屏关键量化值固定为：

- `micro = { x: 24, y: 51, w: 342, h: 12 }`
- `title = { x: 24, y: 69, w: 342, h: 72 }`
- `subtitle = { x: 24, y: 151, w: 342, h: 19 }`
- `stats = { x: 24, y: 188, w: 342, h: 69 }`
- `styleHead = { x: 0, y: 279, w: 390, h: 38 }`
- `styleGrid = { x: 0, y: 317, w: 390, h: 257 }`
- gaps
  - `micro -> title = 6px`
  - `title -> subtitle = 10px`
  - `subtitle -> stats = 18px`
  - `stats -> styleHead = 22px`
  - `styleHead -> styleGrid = 0px`

当前 `home` 首屏默认排障顺序固定为：

1. **先核 top reserve**
   - 先看 `KpCapsuleSpacer`
   - 再看 `home-page__hero-copy`
   - 不能在未量化的情况下直接把问题笼统归因到整页 padding
2. **再核 stats strip 自身**
   - `margin-top`
   - `padding / height`
   - 文案合同
3. **最后核 styles 区段起点**
   - `home-page__body`
   - `home-page__section--styles`
   - 不能在未验证 top reserve 与 stats 的情况下直接去改 styleGrid 坐标

补充 visible contract：

- 三张风格卡的英文 eyebrow 必须按 reference 收口为：
  - `URBAN`
  - `GUO FENG`
  - `CLASSIC`
- 不再使用 `URBAN STYLE / CLASSIC STYLE` 作为首页与创建流风格卡的第一层可见文案
- 在首屏 frame 未重新量化前，不再继续追加 `guide` 内部 `stage / pill / CTA` 的盲调

补充验证降级规则：

- 若 `miniProgram.screenshot()` 持续阻塞，但 `automator.connect + page metrics` 仍可用，则当前轮次允许先使用：
  - `D:\XM\kaipai-team\tmp\automator-probe\capture-home-top.js --skip-screenshot`
  - OS 级窗口截图作为辅助证据
- 这种情况下：
  - DOM metrics 仍可作为布局判断主依据
  - 但必须在 `execution.md` 里明确标记“截图通道受限”
  - 不得把该轮直接汇报为“完整视觉闭环”

### 5.2 create / card / poster chain

creator chain 按 reference 收口为：

1. `card-list/index`：创建分享页
2. `actor-card/index`：预览页（card / poster 双态）

实现约束：

- 继续复用当前 share card 的真实数据 / query / runtime helpers
- 不新造第二套 draft model
- preview 的 `card / poster` 切换优先继续复用当前 `selectedArtifact` 或等价状态
- route 语义必须清楚表达当前是 creator preview，而不是公开详情页

### 5.2.1 基于用户补充逐页 reference 的 creator chain 差异

#### create

当前 `card-list/index` 的 route ownership 已从“列表管理优先”收口到创建流，但与逐页 reference 相比仍有三处核心差异：

1. `STEP 01` 仍未落成三风格卡并列选择
2. `STEP 02` 仍偏“素材统计 + 去完善档案”，未对齐 reference 的上传网格
3. `STEP 03` 仍偏 `preview artifact pill` 语义，未对齐 reference 的标题输入 + 卡片/海报两张大形式卡

因此：

- 当前 create 页可视为“route ownership 首轮完成”
- 但不能视为“frame-level 已完成”

#### card preview / poster preview

用户已补充单页 reference，当前 `actor-card/index` 的最终页级合同必须对齐为：

- `card`
  - 返回按钮
  - 页标题 `卡片预览`
  - 右上 `切到海报`
  - 灰底聊天预览舞台
  - `QUICK EDIT`
  - 底部 `复制链接 / 发送给好友`
- `poster`
  - 深色外背景
  - 返回按钮
  - 页标题 `海报预览`
  - 右上 `切到卡片`
  - 大图 + 双小图 + 二维码 footer
  - 底部 `保存相册 / 分享到朋友圈`

当前仍缺：

- 这两个 screen state 的最新运行态截图
- 基于单页 reference 的最终可见层核验结论

### 5.3 `actor-profile/detail` 的角色回收

`pages/actor-profile/detail` 在 `00-70` 首轮里被借作“卡片预览”承载页，但 `00-73` 要把它收回到更正确的角色：

- 公开分享详情
- 外部打开兼容页
- internal creator chain 外的 support route

这样可以避免：

- creator preview 与 public detail 长期共用一页
- 后续继续在 detail 里叠加 reference 外编辑语义

## 6. 分阶段实施顺序

### 6.1 阶段 1：visual baseline

- 收口 token / serif headline / button / pill / safe-area
- 修正 CURRENT_CONTEXT 与索引映射

### 6.2 阶段 2：四个 core tab / entrance 页

- `login`
- `home`
- `history`
- `mine`

### 6.3 阶段 3：creator chain

- `card-list`
- `actor-card(card)`
- `actor-card(poster)`
- `actor-profile/detail` 职责回收

### 6.4 阶段 4：support routes 与运行态截图

- `actor-profile/edit`
- `verify`
- `role-select`
- `webview`
- `video-player`
- 微信开发者工具 / 真机截图

### 6.5 截图对照推进与三次失败换向规则

当前 `00-73` 不是“一次实现后统一验收”，而是需要边实现边用截图收口的 UI 主线。

因此本轮默认推进循环固定为：

1. 先看 reference 截图
2. 再看当前运行态截图
3. 判断差异属于：
   - 结构差异
   - 信息架构差异
   - 样式差异
   - 运行态未生效 / 工程漂移
4. 做一轮窄改
5. build
6. 核 `src / dist/build / dist/dev`
7. 再拿运行态截图复核

#### 三次失败换向定义

当以下条件同时满足时，视为“同方向已失败 3 次”：

- 同一页面
- 同一可见块
- 同一类问题
- 连续 3 次改动后，运行态截图仍没有得到用户所需的正确变化

达到该条件后，必须自动换方向，不能继续第 4 次做同类调试。

#### 当前主线允许的换向方式

| 原方向 | 触发换向后优先动作 |
|------|------|
| 连续改 margin / padding / top / bottom 等数值 | 改为重新拆 block order 或改直接视觉容器 |
| 连续盯 `src` | 改为核 `dist/build / dist/dev / DevTools` |
| 连续在单页写私有样式 | 改为收 shared token / shared component |
| 连续按“这页本身有问题”猜 | 改为先确认 reference 是否其实要求的是 route ownership 重分配 |
| 连续在 DevTools 里看旧图 | 改为先确认当前工程是不是 `dist/dev/mp-weixin` |

#### 当前工作流的自动推进要求

- 每轮 UI 推进都要明确当前可见块和截图差异
- 第 3 次失败后，不等待用户再次提醒，直接切到新方向继续推进
- 新方向也必须继续基于截图，不允许从“原来猜错了”滑回“继续猜”

### 6.6 Spec-first 的 UI 执行门禁

本轮用户已经明确指出一个流程问题：

- 不是没有 `00-73`
- 而是后续具体 UI 修改时，没有把 `00-73` 当成每轮修改前的强制输入

因此从现在开始，`00-73` 的 UI 推进必须采用下面的固定门禁顺序：

1. **先读 Spec，再改代码**
   - 每轮 UI 修改开始前，必须先读：
     - `requirements.md`
     - `design.md`
     - `tasks.md`
     - `execution.md` 中当前页面 / 当前可见块的最近推进链
2. **先写本轮视觉合同**
   - 至少明确：
     - 页面 route
     - reference 图路径
     - 当前运行态图路径
     - 当前可见块
     - 预期变化
     - 保持不动项
3. **先找真实视觉锚点**
   - 不能把用户指的 frame-level 差异，直接翻译成“继续试 padding / margin”
   - 必须明确：
     - 当前块由哪个 wrapper / class 控制
     - 是否属于页级容器、局部 wrapper、shared component 还是运行态错位
4. **再做单锚点窄改**
   - 一轮只改一个主锚点
   - 不在没有新证据时并改多个宿主
5. **四层核验**
   - `src`
   - `dist\build`
   - `dist\dev`
   - DevTools / fresh runtime 截图
6. **把结论写回 Spec**
   - 不是只在对话里说明“我改了什么”
   - 必须回填 `execution.md`
   - 若用户新增 reference 截图、红框、局部 continuation，也要先补进 `00-73`

#### 为什么不再为每个微调单独新建 Spec

当前 `home / login / history / mine / create / actor-card` 都已经在 `00-73` 的处理范围内。

因此：

- 对这类页面，不应再为一次局部 margin/padding 调整新建重复 Spec
- 正确做法是：
  - 继续使用已有 `00-73`
  - 把新的页级合同、局部红框差异和执行门禁补进现有 Spec

只有当用户提出了**超出 `00-73` 当前范围**的新链路、新页面族或新的职责重构主题时，才需要新增后续 Spec。

## 7. 当前影响文件

### 7.1 核心前台页面

- `D:\XM\kaipai-team\kaipai-frontend\src\pages\login\index.vue`
- `D:\XM\kaipai-team\kaipai-frontend\src\pages\home\index.vue`
- `D:\XM\kaipai-team\kaipai-frontend\src\pages\history\index.vue`
- `D:\XM\kaipai-team\kaipai-frontend\src\pages\mine\index.vue`
- `D:\XM\kaipai-team\kaipai-frontend\src\pkg-card\card-list\index.vue`
- `D:\XM\kaipai-team\kaipai-frontend\src\pkg-card\actor-card\index.vue`
- `D:\XM\kaipai-team\kaipai-frontend\src\pages\actor-profile\detail.vue`
- `D:\XM\kaipai-team\kaipai-frontend\src\pages.json`

### 7.2 shared visual files

- `D:\XM\kaipai-team\kaipai-frontend\src\styles\_tokens.scss`
- `D:\XM\kaipai-team\kaipai-frontend\src\styles\index.scss`
- `D:\XM\kaipai-team\kaipai-frontend\src\components\KpButton.vue`
- `D:\XM\kaipai-team\kaipai-frontend\src\components\KpPillSelector.vue`
- `D:\XM\kaipai-team\kaipai-frontend\src\components\KpSectionHead.vue`

### 7.3 support routes

- `D:\XM\kaipai-team\kaipai-frontend\src\pages\actor-profile\edit.vue`
- `D:\XM\kaipai-team\kaipai-frontend\src\pkg-card\verify\index.vue`
- `D:\XM\kaipai-team\kaipai-frontend\src\pages\role-select\index.vue`
- `D:\XM\kaipai-team\kaipai-frontend\src\pkg-tools\webview\index.vue`
- `D:\XM\kaipai-team\kaipai-frontend\src\pkg-tools\video-player\index.vue`

## 8. 风险与不确定边界

### 8.1 已确认

- reference 的 screen flow 与组件合同是可提取的，不是纯视觉猜测
- 当前 active routes 与 creator chain 漂移已经存在，不能再忽略
- 当前验证主口径继续是 `dist/dev/mp-weixin`

### 8.2 尚待实施期核实

- `card-list -> actor-card` 的具体 draft handoff 是否完全复用现有 query / store，即可做到无新增 runtime model
- 小程序运行时是否需要为 serif headline 再加一层更精细的 fallback
- `actor-profile/detail` 从 creator preview 退出后，是否还存在少量旧入口需要兼容跳转
- records 页何时能拿到单页 reference，还是继续以总览图 + 真实运行态列表页作为最终合同

因此：

- 当前设计已经能确定 visible contract 与 route ownership
- 但具体数据 handoff 仍需在实现阶段基于现有 runtime helper 继续核实，不允许凭空新造第二套草稿链路
