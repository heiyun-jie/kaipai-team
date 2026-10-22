# 小程序参考图视觉标注、回归对比与风格模板 - 技术设计

_Requirements: 4.1-4.4, 5, 6_

## 1. 证据模型

本 Spec 区分四层证据，优先级从高到低如下：

1. 同路由、同状态、同宽度的微信运行态截图。
2. `dist/dev/mp-weixin` 与 `dist/build/mp-weixin` 的 WXML/WXSS/JS 三件套和 scoped hash。
3. `src` 页面模板、局部样式和共享组件。
4. 五张本地参考图的归一化布局标注。

参考图定义目标，运行态截图定义是否真实生效。没有第 1 层或三侧一致性时，不得把第 3 层的源码改动称为通过。

## 2. 截图采集与归一化

### 2.1 采集条件

每次提交一页对比证据时，记录：

| 字段 | 说明 |
|---|---|
| route | 当前页面的完整路由和 query |
| viewport | 开发者工具或真机的逻辑宽高、系统字号、平台 |
| session | 游客或登录；使用何种演示数据 |
| artifact | `src` / `dist/build` / `dist/dev` 三侧哈希与 `data-v` 一致性 |
| capture | 截图时间、操作者、参考图 ID |
| masks | 被忽略的头像、真实图片、姓名、统计值等动态区域 |

用户当前要求不影响正常电脑使用，因此本轮只建立参考标注。运行态截图由用户在目标页面自行采集并提供，或在用户明确授权构建同步且确认开发者工具可被影响后采集。

非干扰采集是硬约束：视觉回归流程不得把微信开发者工具置顶、强制前台、抢占焦点，不得控制整屏、桌面坐标、鼠标或键盘。若内部模拟器接口会创建或抬起可见窗口，则该轮只做产物核验和用户截图比对；确需运行态开窗时必须先取得用户明确授权，并在结束后只关闭固定项目窗口。

### 2.2 坐标换算

设参考图宽度为 `W`，某元素边界为 `(x, y, width, height)`：

```text
xRpx     = x / W * 750
widthRpx = width / W * 750
gapRpx   = gap / W * 750
```

纵向不直接把 `y` 转成固定页面样式值。先扣除平台顶部区（状态栏 + 胶囊），再记录与前一个业务锚点的距离；避免将不同设备的系统区域当成页面留白。

### 2.3 允许误差

| 比对项 | 允许偏差 | 不通过条件 |
|---|---:|---|
| 主体横向边距、卡片左右边 | 6rpx | 任一主模块未对齐或左右不对称 |
| 导航/进度/正文锚点 | 8rpx | 标题、进度、首卡之间的层级关系失真 |
| 卡片/按钮高度 | 8rpx | CTA、卡片、媒体格比例明显不同 |
| 字体层级 | 一个等级以内 | 标题、正文、状态文案倒置或截断 |
| 颜色/边框/圆角 | 语义一致 | 旧棕米色、橙色选中态、无边框卡或重阴影回归 |
| 功能状态 | 零容忍 | 假入口、丢失真实 handler、排序/上传/保存合同被破坏 |

## 3. 页面标注与真实容器

详细参数见 `reference-layout.md`。本节定义“视觉锚点 -> 实现容器”的映射，实施时只能修改直接负责该锚点的容器。

| 参考图 | 视觉锚点 | 当前实现容器 | 不可改变的行为 |
|---|---|---|---|
| R01 首页 | 品牌标题、问候、Hero、草稿卡、文字 Tab、模板双列 | `home-v2__header`、`__hero`、`__draft-card`、`__style-tabs`、`__style-grid` | 按风格筛选背景库；模板携带 backgroundId；草稿继续编辑 |
| R02 创建 Hub | 居中导航、创建进度、7 张步骤卡、固定 CTA | `KpPageNav`、`KpCreateProgress`、`create-hub__steps`、`__footer` | 7 步状态、路由、回读、重复点击保护 |
| R03 参演作品 | 居中导航、3/7、标题、分段 Tab、作品卡、剧照带、固定 CTA | `KpPageNav`、`KpCreateProgress`、`step-works__tabs`、`__card`、`__stills-row`、`__footer` | 真实经历/新增、剧照素材库、替换、删除、封面、保存 |
| R04 生活照片 | 居中导航、4/7、提示、双上传入口、计数/排序、三列网格、固定 CTA | `KpPageNav`、`KpCreateProgress`、`step-photos__actions`、`__count-row`、`__grid`、`__footer` | 12 张上限、requestId 会话、上传、删除、显式排序、保存回读 |
| R05 个人中心 | 标题、档案卡、完整度、统计卡、资料/服务列表、原生 TabBar | `mine-v2__body`、`__profile-card`、`__completeness-card`、`__stats-row`、`__group-card` | 真实资料路由、统计跳 Tab、实名认证、退出确认；不新增帮助/设置假入口 |

## 4. 可复用风格模板

模板是页面与共享组件的共同视觉语言，不等同于一次性创建的 Vue 组件。确认至少三个页面复用且不突破分包边界后，才抽到 `Kp*` 组件。

### 4.1 ReferencePageShell

```text
canvas      = white
page gutter = 40rpx for R01-R05 body content
content gap = 16rpx for adjacent cards; 32rpx for sections
card        = white / 1rpx border / 16rpx radius / no elevated shadow by default
text        = primary #171A21, secondary #667080, tertiary #8E8E93
accent      = #2F6BFF only for CTA, progress, link, selected state
```

### 4.2 ReferenceNav and ReferenceProgress

```text
nav          = KpPageNav owns capsule alignment; Tab roots use left title; wizard titles are screen-centered
progress     = 10rpx neutral track, blue fill, 40rpx horizontal alignment
hub copy     = "创建进度 x/7"
step copy    = "x/7" only; no duplicate "创建进度" label
```

### 4.3 ReferenceCard and ReferenceSection

```text
section title  = H2 32rpx/700
page H1        = 40rpx/700
card padding   = 24rpx to 32rpx depending on media density
card stroke    = 1rpx #E8E8E8
status text    = color-only or compact outlined tag; it cannot replace the primary action
```

### 4.4 ReferenceSegmentedTabs and ReferenceMediaGrid

```text
home tabs       = flat text tabs + 5rpx blue underline; no pill background
form tabs       = muted outer track + white active segment + subtle border/shadow
media grid      = three equal columns, 16rpx gap, square media, order number top-left, remove top-right
sorting tools   = hidden until user explicitly enters sorting mode
```

### 4.5 ReferenceBottomCta and ReferenceTabBar

```text
bottom CTA      = fixed white support surface, 40rpx horizontal inset, 96rpx blue button, safe-area reserve
TabBar          = native four-tab bar, individual line icons; only active icon/text are blue
```

## 5. 对比流程

1. 在 `tasks.md` 为目标路由登记截图状态与数据条件。
2. 核查 `src`、`dist/build`、`dist/dev` 的目标 WXML/WXSS/JS scoped hash；三侧不一致时停止视觉修改。
3. 将实际截图按 `750rpx` 归一，与同一路由参考图进行叠加对照；屏蔽动态媒体与数据文案。
4. 先检查壳层，再检查模块边界、文本层级、卡片尺寸、网格/CTA，最后验证交互状态。
5. 一轮只修改同一页面的一组直接锚点，重新构建、哈希核验、再次截图。
6. 将差异、修改容器、生成值和截图证据回写 `tasks.md`；所有锚点通过才关闭页面任务。

## 6. 风险控制

- 微信开发者工具可将旧缓存写回 `dist/dev`，造成 WXML 与 WXSS/JS scopeId 分叉。任何“样式没生效”先按 00-219 比对哈希，禁止再猜样式。
- 图稿中的人像和统计数值均为示例，不得将图片、数量、文案当作真实接口/限制的要求。
- 基线图只覆盖五页；其余路由仍遵守 00-221，不能从这五页复制不适用的导航或媒体布局。
- 本轮不打开或操控用户的开发者工具。截图证据不能以非干扰方式自动取得时，任务保持待验收状态，不得为了补证据置顶、抢焦点或控制用户桌面。
