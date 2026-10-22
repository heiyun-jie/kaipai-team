# 3.0 小程序最终 UI 风格系统与交互视觉合同 - 技术设计

_Requirements: 4.1-4.7, 5, 6_

## 1. 设计原则与权威关系

3.0 的权威顺序如下：

1. 本 Spec 的 requirements.md：必须满足的行为和验收合同。
2. docs/ui-style-guide-v3.md：设计师、开发者和验收人员共用的视觉手册。
3. kaipai-frontend/src/styles/_tokens.scss：实现侧 Token 名称和值。
4. 共享 Kp 组件：跨页面行为和状态的唯一实现入口。
5. 页面局部样式：只能表达页面布局，不得重新定义品牌颜色和全局状态。

00-220 是路由和问题证据基线；00-221 不是对 00-206 等业务合同的替代。若视觉稿与真实业务合同冲突，先在 T0 裁决，再修改视觉或需求，不能通过样式掩盖能力缺口。

## 2. Token 设计

### 2.1 颜色 Token

建议在 _tokens.scss 中增加语义命名，并在迁移完成后删除旧默认值：

| SCSS Token | 值 | 语义 |
|---|---|---|
| $kp-color-brand | #2F6BFF | 品牌蓝 |
| $kp-color-brand-strong | #145DFF | pressed / 强调 |
| $kp-color-brand-soft | #EEF2FF | 浅蓝容器 |
| $kp-color-canvas | #FFFFFF | 页面背景 |
| $kp-color-surface-muted | #F6F7F9 | 列表 / 分组背景 |
| $kp-color-text-primary | #171A21 | 主文字 |
| $kp-color-text-secondary | #667080 | 次文字 |
| $kp-color-text-tertiary | #8E8E93 | 占位文字 |
| $kp-color-border | #E8E8E8 | 边框 |
| $kp-color-divider | #F0F0F0 | 分割线 |
| $kp-color-success | #2E8A57 | 成功 |
| $kp-color-warning | #E67E22 | 警告 |
| $kp-color-danger | #FF3B30 | 危险 |

迁移期间可以建立旧变量到新变量的兼容别名，但旧变量不得继续被新页面直接引用。legacy 颜色只允许在遗留页面白名单中存在，并在每轮迁移后递减。

### 2.2 字体、间距和圆角

| 类别 | 规格 |
|---|---|
| Display / Page title | 48rpx/700、36rpx/700 |
| H1 / H2 | 40rpx/700、32rpx/700 |
| Body / Caption / Micro | 28rpx/400、24rpx/400、22rpx/400 |
| 页面边距 | 默认 24rpx；五张参考图页面主体 40rpx |
| 卡片内边距 | 24rpx |
| 连续卡片间距 | 16rpx |
| 区块间距 | 32rpx |
| 普通卡片圆角 | 16rpx |
| 控件圆角 | 12rpx |
| 胶囊圆角 | 999rpx |

字体使用系统无衬线栈：-apple-system、BlinkMacSystemFont、Helvetica Neue、PingFang SC、Microsoft YaHei、sans-serif。3.0 不再使用宋体展示标题，也不使用负字距。

## 3. 页面壳层

### 3.1 Tab 根页

适用：home、card-list、assets、mine。

- 白色页面背景，必要时使用 surface-muted 作为列表区域底色。
- 顶部标题由 KpPageNav 或 Tab 专用标题槽承载，遵守胶囊避让。
- 底部使用原生 TabBar；选中态仅由独立蓝色图标和文字表达。
- 每个 Tab 根页直接渲染内容，禁止通过重定向页代替根页。

### 3.2 普通内容页

适用：login、actor-profile/edit、pkg-card/verify、pkg-profile/import-review、pkg-profile/assets、pkg-tools/webview、pkg-tools/video-player 等。

- 顶部使用白色导航层、返回按钮和页面标题。
- 内容用区块和卡片分层，不使用旧深色 Hero + 米色上浮内容。
- 表单页将概览、基础字段、补充字段和展示字段拆为独立区块。
- 页面底部固定 CTA 时，内容 padding-bottom 必须覆盖 CTA 高度和安全区。

### 3.3 向导页

适用：pkg-actor-card/create 和 7 个 step 页面。

- 顶部统一 KpPageNav。
- 进度语义统一为创建进度 x/7：Hub 显示已完成步数，step 页显示当前步骤。
- 主体顺序固定为标题 / 描述、状态卡或资源区、辅助说明、底部 CTA。
- 资源区必须可表达空、加载、成功、失败、替换和删除。
- 返回、跳步和完成设置必须保留已有 00-216 导航合同。

### 3.4 公开观看和历史页面

适用：pkg-actor-card/view、pkg-card/ai-profile-card-detail。

- 公开观看页以内容阅读为主，保持白色画布、内容分组和资源异常态。
- 历史分享页在 T0 裁决前不能直接标为最终 3.0；若保留，先套用 Token，再评估信息架构。
- 旧页面可以保留业务兼容，但不得继续作为新页面风格来源。

## 4. 组件契约

### 4.1 KpButton

主按钮使用 brand，按下使用 brand-strong，禁用降低对比度并保留文本可读性。按钮必须支持 loading 并锁定点击；危险操作使用 danger，不用橙色表达删除。

### 4.2 KpPageNav

继续作为标题型页面唯一导航组件。它负责胶囊占位、标题定位、返回事件和安全区；调用方不再手写 top、height、right: 200rpx 等定位数值。

### 4.3 KpStatusTag

状态映射固定为：完成 / 成功 -> success，待处理 / 待确认 -> warning，失败 / 删除 -> danger，未添加 / 未完成 -> text-tertiary + surface-muted。标签只表达状态，不承担主操作。

### 4.4 KpBottomActionBar

只承载当前页面的主 CTA。若页面已有固定操作栏，卡片内部不得再重复同一主操作。操作栏必须处理安全区、loading、disabled 和错误重试。

### 4.5 KpConfirmDialog

用于删除、退出、替换、清空等不可逆操作。确认按钮使用 danger 或 brand，取消必须无副作用；网络失败时保留对话框或提供重试，不静默关闭。

## 5. 图标、插画和媒体

- TabBar 使用四组独立的线性图标资源，命名应能区分 home、card-list、assets、mine 的 active / inactive。
- 功能图标优先使用现有图标库；没有对应图标时新增静态资源，不用 Emoji 或临时字符。
- 首页 Hero 插画若保留 CSS 形状，只能作为装饰层，不能替代模板、演员卡或真实作品信息。
- 图片、视频、PDF 等资源必须显示加载、失败和重试状态；禁止把 wxfile:// 临时路径作为持久展示地址。

## 6. 交互状态模型

所有异步操作按以下状态建模：

idle -> loading -> success
idle -> loading -> error -> retry

资源编辑额外支持：

empty -> selecting -> uploading -> ready
ready -> previewing
ready -> replacing -> uploading
ready -> deleting -> empty

状态变更必须同时更新视觉状态、可点击性、提示文案和回读数据。列表操作完成后刷新当前列表或本地快照，避免按钮成功但页面仍显示旧数据。

## 7. 迁移策略

1. 先改 Token 和共享组件，建立 legacy 颜色扫描白名单。
2. 再修复四项 Tab 壳层和 TabBar 资源，确保导航稳定。
3. 按五张参考图迁移首页、创建 Hub、作品、生活照片、个人中心。
4. 再迁移名片夹、向导剩余步骤、生成、观看者页和其他 8 个旧棕米色页面。
5. 每个批次同步检查操作闭环，不接受只换颜色的“视觉完成”。
6. 最后一轮删除 legacy 白名单，更新 SHARED_CONVENTIONS.md、CURRENT_CONTEXT.md、docs/product-design.md 和 spec-code-mapping.md 的 22 页基线。

## 8. 验证方案

- 静态：扫描旧颜色、硬编码颜色、Emoji 图标、redirectTo Tab 根页和无 handler 的点击入口。
- 类型与构建：vue-tsc、build:mp-weixin。
- 门禁：verify:nav-title、verify:actor-card-attachment、verify:v3-ui-legacy-colors、verify:tabbar-icons、audit:mp-package。
- 产物：比较 src、dist/build、dist/dev 的 data-v / scoped hash，确保三件套一致。
- 运行态：在微信开发者工具逐页采集首页、Hub、作品、生活照片、个人中心、名片夹、素材库截图和关键点击证据。
- 响应式：至少验证 iPhone SE、iPhone 15 Pro Max 和 Android 常见宽度，检查文本、CTA 和安全区不重叠。
