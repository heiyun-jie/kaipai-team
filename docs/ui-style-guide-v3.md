# 开拍了小程序 3.0 UI 风格手册

版本：3.0（最终 UI 定稿基线）
状态：设计合同；五张参考页的逐页标注、运行态证据与回归结论由 `00-223` 管理
适用范围：kaipai-frontend 小程序全部 24 个实际注册路由
视觉参考：C:\Users\33340\Desktop\开拍了\小程序UI图

## 1. 风格定位

3.0 的产品气质是“蓝白、专业、清晰的演员作品集工具”。界面优先服务于资料整理、作品展示和演员卡创建，不使用旧版深色 Hero、棕米色内容区、重度玻璃拟态或装饰性渐变球作为默认视觉。

核心感受：

- 专业：标题、作品、资料和状态有明确层级。
- 可靠：每个操作都有状态、反馈和可回读结果。
- 轻量：白色画布和浅灰分组降低视觉噪声。
- 聚焦：品牌蓝只用于关键行动和选中状态，不让整页变成单一蓝色。

## 2. 颜色系统

| 名称 | 色值 | 使用规则 |
|---|---|---|
| Brand | #2F6BFF | 主按钮、进度、选中态、链接 |
| Brand Strong | #145DFF | 按下态、关键强调 |
| Brand Soft | #EEF2FF | 选中背景、提示区 |
| Canvas | #FFFFFF | 页面主背景 |
| Surface Muted | #F6F7F9 | 列表和分组背景 |
| Text Primary | #171A21 | 标题、正文 |
| Text Secondary | #667080 | 描述、辅助信息 |
| Text Tertiary | #8E8E93 | 占位、未完成、禁用辅助文案 |
| Border | #E8E8E8 | 卡片和输入框边框 |
| Divider | #F0F0F0 | 轻分割线 |
| Success | #2E8A57 | 完成、成功 |
| Warning | #E67E22 | 待处理、提醒 |
| Danger | #FF3B30 | 删除、失败、退出 |

禁止把 #1D1814、#8C6F4F、#F5F3EE、橙色 TabBar active 位图带入新的 3.0 页面。颜色必须通过语义 Token 使用，不能在页面样式中直接复制色值。

## 3. 字体与排版

字体栈：-apple-system、BlinkMacSystemFont、Helvetica Neue、PingFang SC、Microsoft YaHei、sans-serif。

| 层级 | 规格 | 使用场景 |
|---|---|---|
| Display | 48rpx / 700 | 首屏核心数字或主标题 |
| Page title | 36rpx / 700 | 页面标题 |
| H1 | 40rpx / 700 | 页面主区块标题 |
| H2 | 32rpx / 700 | 卡片、分组标题 |
| Body | 28rpx / 400 | 正文和主操作文案 |
| Caption | 24rpx / 400 | 描述、辅助说明 |
| Micro | 22rpx / 400 | 标签、时间、弱提示 |

行高使用 1.2、1.5、1.8 三档。字距保持 0，不用负字距挤压标题；长文案在窄屏下换行，不允许覆盖按钮或相邻内容。

R01 首页的「继续编辑」草稿卡标题也按 Body 层级收口，不再单独抬高到 H2；在当前参考稿里它保留 28rpx / 700 / 1.2 的视觉层级，和 Hero 主标题形成一档之差。草稿卡右侧「继续」是轻量链接，不作为主 CTA 处理，使用 28rpx / 500；首页模板 Tab 选中态下划线固定为短线，避免铺满四分之一 Tab 宽度。

R01 首页 Hero 的主标题保持 H1 层级 `40rpx / 700 / 1.2`；Hero 卡片以略高于参考图初始标注的一档外高承载内容，当前目标为 `416rpx` 外高、左侧文案有完整上下呼吸、右侧三层演员卡插画占 Hero 高度的大半。插画只作为装饰，不替代真实模板图、草稿封面或演员卡媒体。

R05 个人中心采用轻量白卡密度：档案卡保持约 `192rpx` 外高，头像按参考图比例使用 `148rpx`，卡内左上留白薄于普通内容卡；完整度卡约 `160rpx`，百分比为 H1 `40rpx / 700 / 1.2`；统计卡约 `128rpx`，统计数字使用 H1 而不是 Display，避免抢过页面标题；资料分组双行列表行约 `112rpx`，主文案使用 `26rpx / 1.2`、副文案使用 `22rpx / 1.2` 且间距 `6rpx`；服务分组单行列表行约 `76rpx`，主文案使用 `24rpx / 1.2`，左侧轴线比资料双行更紧。列表图标保持 `2rpx` 轻线性 CSS 形态，右箭头不得缩成小点。个人中心「个人资料 / 演艺经历 / 自我介绍」必须是三个独立业务入口：个人资料进入 `pages/actor-profile/edit`，演艺经历进入 `pkg-profile/works/index` 设置本人作品经历，自我介绍进入 `pkg-profile/intro/index` 单独编辑 intro；不得再用 `?tab=experience` / `?tab=intro` 伪装成同一个个人资料页。个人中心主页面不放红色退出按钮，退出登录收在「设置」页；「帮助与反馈」和「设置」必须指向真实承载页，不得使用“即将开放”占位 toast。

## 4. 间距、圆角与层级

- 页面左右边距：默认 24rpx；首页、创建 Hub、参演作品、生活照片、个人中心按五张参考图使用 40rpx 主体留白。
- 卡片内边距：24rpx。
- 同层连续卡片间距：16rpx。
- 文字区块到主 CTA：32rpx。
- 大区块之间：32rpx。
- 普通卡片圆角：16rpx。
- 输入框、按钮等控件圆角：12rpx。
- 标签和筛选胶囊：999rpx。
- 阴影只用于浮层、弹窗和必要的操作栏；普通内容优先使用边框和留白表达层级。

不要把页面区块全部做成浮动卡片，也不要在卡片里再套一层相同语义的卡片。

## 5. 页面结构

### 5.0 参考图回归模板

五张视觉参考图不是泛化的“蓝白”示意，而是首页、创建 Hub、参演作品、生活照片和个人中心的可验收版式合同。实现这五页时必须同时遵守下表和 `00-223` 的逐页标注：

| 模板 | 固定视觉职责 | 适用规则 |
|---|---|---|
| `ReferencePageShell` | 白色画布、主体 40rpx 留白、16rpx 白卡圆角、细边框 | 参考页正文不可回退为深色 Hero 或大面积灰底 |
| `ReferenceNav` | Tab 页左对齐标题；向导页标题整屏居中；胶囊由 `KpPageNav` 对齐 | 调用页不手写胶囊坐标 |
| `ReferenceProgress` | 蓝色 10rpx 进度条，与正文 40rpx 同轴 | Hub 显示“创建进度 x/7”，步骤页只显示 `x/7` |
| `ReferenceCard` | 内容优先用留白和细边框分层，避免重阴影 | `min-height` 与 `padding` 并存时必须 `box-sizing: border-box`，防止外高叠加 |
| `ReferenceSegmentedTabs` | 首页用文字 + 下划线；表单页才用分段轨道 | 首页不得回退为大胶囊 Tab |
| `ReferenceMediaGrid` | 首页两列、生活照片三列；媒体比例稳定 | 动态图片仅作为内容掩膜，不改变网格尺度 |
| `ReferenceBottomCta` | 40rpx 横向内缩、96rpx 品牌按钮、安全区预留 | 只绑定现有真实 handler，禁止伪造入口 |

运行态截图的文件哈希、页面状态、产物层级和差异结论记录在 `.sce/specs/00-223-current-phase-miniapp-reference-visual-regression/evidence.md`。未经过 `src` / `dist/build` / `dist/dev` 三侧核验的源码改动，不能标记为视觉通过。

### 5.1 四个 Tab 根页

首页、名片夹、素材库、个人必须直接渲染自己的内容，并保持原生 TabBar 的选中状态。素材库不能依赖一个只做 redirectTo 的中间页。

Tab 根页的首屏顺序：

1. 页面标题或主视觉。
2. 当前任务 / 草稿 / 统计摘要。
3. 主要内容列表或模板网格。
4. 空态或下一步行动。
5. 原生 TabBar。

### 5.2 普通内容页

普通内容页使用白色导航层、清晰标题和浅灰分组。标题型页面的返回按钮、标题和微信胶囊对齐默认由 KpPageNav 负责。表单拆成多个信息区块，底部固定操作必须留出安全区。

`actor-profile/edit`、`pkg-profile/import-review`、`pkg-profile/assets`、`pkg-profile/works`、`pkg-profile/intro` 属于 00-212 保留的普通返回模式 B：使用 KpFloatingBackButton + 页面本地居中标题 + sticky / relative 导航容器，不强行并入 KpPageNav。此类页面的顶部分割线不得贴住标题 / 胶囊行，应由本地导航容器底部的伪元素承载，并至少预留一个 `$kp-spacing-lg` 的底部呼吸位；标题本身用同等 bottom offset 抵消，保证“只移动分割线，不下压标题”。

演员档案编辑页顶部的「从复制内容智能填写」属于导入 / 粘贴入口，不应贴在白色画布上成为普通文字行；必须以独立白卡呈现，使用 `$kp-radius-card`、`$kp-color-border` 和 `$kp-shadow-card` 建立卡片边界，卡内行高不低于 `112rpx`，点击逻辑仍指向导入复核流程。

`pkg-profile/works` 是经历列表管理页，不是长表单页；新增 / 编辑经历必须使用页面内弹窗 / 底部抽屉承载。弹窗顶部保留标题与取消按钮，中部表单独立滚动，底部保存按钮固定并显式锁定高度、字号和 disabled 态；主列表不得被表单插入挤压。遮罩层负责拦截背景触摸，弹窗根节点不得吞掉中部 `scroll-view` 的纵向手势；抽屉和滚动区必须有稳定可计算高度，表单末尾预留底部间距，保证最后一个字段能完整滚动到固定保存栏上方。

资料导入复核页 `pkg-profile/import-review/index` 的「原始内容」区域属于表单卡片，应使用同一套白卡、细边框、16rpx 圆角和轻阴影承载。剪贴板读取、开始识别、冲突确认和底部应用按钮必须显式锁定高度、字号、字重、居中和 disabled 颜色，避免被小程序原生 button 默认样式挤压文字排版。

### 5.3 创建向导

创建 Hub 和 7 个步骤保持同一套顶部进度、状态卡和底部主 CTA。进度文案使用“创建进度 x/7”：Hub 的 x 表示已完成项，步骤页的 x 表示当前步骤。资源卡必须能够表达空、上传中、完成、失败、重试、预览、替换和删除。

### 5.4 公开观看页

公开观看页以作品阅读为主，采用白色画布、媒体比例稳定的内容区和明确的资源异常态。草稿、无权限、资源失效和网络失败不可显示成空白。

## 6. 组件和操作状态

### 6.0 TDesign 基础组件合同

- 通用基础组件固定使用 `tdesign-miniprogram@1.16.0`，由 `00-226` 的 allowlist 生成脚本按递归依赖闭包进入小程序产物，不要求微信开发者工具手工“构建 npm”。
- 页面在 `pages.json` 中按需声明实际渲染的组件，禁止在 `globalStyle` 注册整套 TDesign；组件默认外观必须由 3.0 Token、页面字号和稳定高度覆盖，不能直接套示例页样式。
- `t-button / t-input / t-textarea / t-image / t-tabs / t-picker / t-switch / t-dialog / t-popup / t-action-sheet / t-tag / t-checkbox` 承担通用控件；导航、创建进度、固定操作栏等业务组合仍使用职责明确的 `Kp*` 组件。
- 小尺寸协议勾选框由 `t-checkbox` 单独拥有视觉盒子，页面宿主不得再绘制圆框；当 TDesign 图标字体因包体治理被移除时，必须使用随包生成的官方 checked/unchecked SVG 数组，禁止保留不可见的默认字体图标。
- TDesign 选择控件的外观由组件 `custom-style` CSS 变量控制；页面宿主不得再绘制同形状的边框、背景或伪图标，否则会与组件内部图标叠成双控件。图标和文案间距只能保留一个事实源。
- 系统文件和媒体选择、预览、播放器、WebView、导航及短时平台 Toast 继续使用微信 / uni-app 平台能力；受控弹窗和操作菜单不得回退到 `uni.showModal` / `uni.showActionSheet`。
- TDesign SVG 图标必须由本地 `tdesign-icons-svg` allowlist 生成，禁止加载远程字体、整套图标字体或 Emoji 功能图标。

### 6.1 按钮

主行动使用 Brand；危险操作使用 Danger；次要行动使用边框或浅灰底。按钮需要 default、pressed、disabled、loading 四态。loading 时锁定点击并保留原文案或明确的进行中状态。

### 6.2 卡片和列表

可点击卡片必须有按下态和明确的右侧 affordance。列表删除、复制、发布、分享等动作应保持同一行的操作优先级，危险操作不能与主操作使用相同颜色。

### 6.3 上传与媒体

上传流程至少显示选择、上传中、成功和失败重试。视频和剧照提供预览；替换不会先丢失旧资源，只有新资源上传成功后才切换。持久展示地址必须是服务端 URL，不能保存 wxfile:// 临时路径。

### 6.4 删除、退出和清空

不可逆操作使用受控 `t-dialog`。取消无副作用；确认后显示 loading；失败时保留可重试入口；成功后刷新列表或回读状态。

### 6.5 空态

空态包含原因、当前状态和下一步行动。没有下一步行动的只读空态必须明确说明原因，不使用“即将开放”作为长期替代。

## 7. 图标和媒体资产

- TabBar 提供 home、card-list、assets、mine 四组 active / inactive 独立图标。
- 功能图标优先使用现有线性图标库；没有对应图标时新增静态资源。
- 不使用 Emoji 表达设置、帮助、统计、删除等功能。
- 图标按钮需要无障碍标签；陌生图标悬停或长按时提供名称。
- 首页装饰插画不能替代真实模板或演员作品内容；真实媒体需要保持可检查的比例和清晰度。

## 8. 3.0 页面迁移优先级

### P0：参考图和主导航

首页、创建 Hub、step-works、step-photos、个人中心、名片夹、素材库 Tab 壳层、TabBar 图标、共享 Token 和共享组件。

### P1：主链剩余页面

step-visual、step-profile、step-video、step-attachment、step-settings、generate、pkg-actor-card/view。

### P2：旧主题和兼容页面

登录、演员档案编辑、实名认证、资料库、资料导入复核、视频播放器、WebView、历史分享详情页。

P2 页面仍可保持业务兼容，但必须最终使用 3.0 Token；历史页面是否退场以 00-221 T0 裁决为准。

## 9. 交付验收清单

- [x] 24 个路由均已登记 TDesign 组件矩阵，通用原生控件已从源码、build 和 dev 产物退场。
- [ ] 旧棕米色默认值和橙色 TabBar active 已从 release 页面移除。
- [ ] 颜色、字号、间距、圆角和阴影均由 Token 提供。
- [ ] 四个 Tab 根页可直接渲染，素材库不依赖中间重定向。
- [ ] 首页、Hub、作品、生活照片、个人中心与五张参考图的结构和关键操作均有运行态证据。
- [ ] 删除、上传、预览、替换、排序、发布、分享、复制创建和返回路径均可验证。
- [x] src、dist/build/mp-weixin、dist/dev/mp-weixin 三侧产物一致，scoped hash 无分叉。
- [x] vue-tsc、构建、导航、附件和包体大小门禁通过；全量外链审计仍记录 7 处既有 Uni/Vue 文档链接与本地联调 URL。

## 10. 关联文档

- .sce/specs/00-220-current-phase-miniapp-v3-final-ui-deep-investigation/
- .sce/specs/00-221-current-phase-miniapp-v3-ui-style-system/
- .sce/specs/00-226-current-phase-miniprogram-tdesign-system-migration/
- .sce/specs/SHARED_CONVENTIONS.md
- docs/product-design.md
- docs/dev-playbook.md
