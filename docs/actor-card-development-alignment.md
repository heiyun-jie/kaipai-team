# 演员卡创建流程开发对齐手册

_版本：v1.0_
_更新日期：2026-08-18_
_性质：开发合同，不代表功能已完成_
_适用范围：`kaipai-frontend` 的演员卡创建向导、素材库选择模式及其共享组件_

## 1. 文档目的

这份文档把 3.0 蓝白视觉合同转换成开发时可以直接执行的页面、组件和状态规则，解决以下几类漂移：

- 页面颜色已经相近，但仍各自硬编码，无法统一维护；
- 创建向导的顶部、进度、底部操作栏和安全区在不同步骤中不一致；
- 图片、视频、PDF 的空态、处理中、失败、重试和回读状态表达不一致；
- 素材库选择页与创建向导使用了不同的交互语义；
- 视觉入口存在，但没有真实 handler、保存合同或失败回读。

本手册只规定开发对齐方式，不替代功能 Spec，不代表素材库已经接通，也不包含发布或生产迁移操作。

## 2. 权威关系

发生冲突时按以下顺序判断：

1. 当前功能 Spec 的 `requirements.md`：决定业务行为、数据合同和验收边界。
2. 当前功能 Spec 的 `design.md`：决定页面流程、接口交互和实现方案。
3. `00-221-current-phase-miniapp-v3-ui-style-system`：决定 3.0 UI 视觉合同。
4. `docs/ui-style-guide-v3.md`：设计、开发、验收共用的视觉手册。
5. `kaipai-frontend/src/styles/_tokens.scss` 和共享 `Kp*` 组件：实现侧 Token 与组件入口。
6. 页面局部样式：只表达页面布局和局部差异，不得重新定义全局颜色、字体、状态或导航定位。

业务合同优先于视觉稿。不能用换颜色、隐藏按钮或静态占位把未实现的业务能力伪装成完成。

## 3. 当前页面范围

### 3.1 创建向导页面

创建流程由 7 个步骤组成，页面顺序和 `done` 语义固定：

| 步骤 | 路径 | 视觉职责 | 当前资源合同 |
|---:|---|---|---|
| Hub | `pkg-actor-card/create/index` | 展示 7 步完成度、继续编辑和创建入口 | 只消费草稿状态 |
| 1 | `pkg-actor-card/step-visual/index` | 主视觉、背景和扩图状态 | `source_image` / photo |
| 2 | `pkg-actor-card/step-profile/index` | 个人资料快照与同步状态 | profile 数据，不属于素材库 |
| 3 | `pkg-actor-card/step-works/index` | 参演作品、剧照、封面和排序 | `work_still` / photo / 每部最多 3 张 |
| 4 | `pkg-actor-card/step-photos/index` | 生活照片网格、数量和排序 | `life_photo` / photo / 最多 12 张 |
| 5 | `pkg-actor-card/step-video/index` | 视频预览、替换和失败恢复 | `video_resume` / video / 单个 |
| 6 | `pkg-actor-card/step-attachment/index` | PDF 文件卡、页图预览和处理状态 | `attachment` / pdf / ≤20MB、≤20 页 |
| 7 | `pkg-actor-card/step-settings/index` | 显隐、顺序和生成入口 | settings 数据，不负责真实长图生成 |

终态页面 `generate/index` 和 `view/index` 继续使用同一套蓝白 Token，但不显示创建进度；真实长图生成能力不在本手册内。

### 3.2 素材库页面

| 页面 | 角色 | 规则 |
|---|---|---|
| `pages/assets/index` | 原生 Tab 素材库管理页 | 直接渲染素材管理，不接收创建上下文，不持有卡片绑定状态 |
| `pkg-profile/assets/index` | 素材选择 / 管理分包页 | `mode=card-select&requestId=...` 只用于创建上下文；选择结果只返回 assetId 等结构化数据 |

新增开发不得把 `pages/assets/index` 改成 redirect 壳层，也不得把选择状态放进原生 Tab 根页。

## 4. 页面统一壳层

### 4.1 向导页骨架

每个向导页采用同一层级：

```text
page canvas: $kp-color-surface-muted
  header: KpPageNav + KpCreateProgress
  content: title / description -> state or resource area -> helper text
  fixed footer: save status -> primary CTA (+ optional skip)
```

实现要求：

- 顶部导航统一使用 `KpPageNav`，调用方不得重复手写胶囊避让、返回按钮绝对定位或 `right: 200rpx`。
- 进度统一使用 `KpCreateProgress`：Hub 的 `done` 是已完成项数量，步骤页的 `done` 是当前步骤号，终态页不显示进度。
- 固定底部操作栏必须使用 `env(safe-area-inset-bottom)`，内容区的 `padding-bottom` 必须覆盖操作栏高度和安全区。
- 页面主体默认使用 `$kp-spacing-page` 左右边距；连续资源卡用父级 `gap: $kp-spacing-gap`，不要逐张写临时 margin。
- 同一页面只保留一组主 CTA。卡片内部不能再复制底部操作栏的“下一步 / 保存”按钮。

### 4.2 Tab 与普通页骨架

- 四个 Tab 根页直接渲染自己的内容：`home`、`card-list`、`assets`、`mine`。
- 普通内容页使用白色导航层和浅灰内容分组；页面标题由 `KpPageNav` 承载。
- 新页面不得使用深色 Hero + 米色上浮内容、装饰性渐变球或整页玻璃拟态作为默认结构。
- 背景、内容区和操作栏优先使用语义 Token；渐变只允许保留在明确登记的历史页面，不得作为新页面默认视觉。

## 5. 3.0 Token 使用合同

页面样式只能引用 `$kp-*` Token；以下是开发最常用的语义映射：

| 语义 | Token | 目标值 |
|---|---|---|
| 品牌主色 | `$kp-color-brand` | `#2f6bff` |
| 按下 / 强调 | `$kp-color-brand-strong` | `#145dff` |
| 浅蓝状态背景 | `$kp-color-brand-soft` | `#eef2ff` |
| 页面白底 | `$kp-color-canvas` | `#ffffff` |
| 浅灰分组 | `$kp-color-surface-muted` | `#f6f7f9` |
| 主文字 | `$kp-color-text-primary` | `#171a21` |
| 次文字 | `$kp-color-text-secondary` | `#667080` |
| 占位 / 未完成 | `$kp-color-text-tertiary` | `#8e8e93` |
| 边框 / 分割 | `$kp-color-border` / `$kp-color-divider` | `#e8e8e8` / `#f0f0f0` |
| 成功 / 警告 / 危险 | `$kp-color-success` / `$kp-color-warning` / `$kp-color-danger` | 语义状态色 |

布局节奏固定为：

- 页面边距：`$kp-spacing-page`，默认 24rpx；
- 卡片内边距：`$kp-spacing-card`，默认 24rpx；
- 同层卡片间距：`$kp-spacing-gap`，默认 16rpx；
- 区块到主 CTA：`$kp-spacing-lg`，默认 32rpx；
- 普通卡片：`$kp-radius-card`，默认 16rpx；
- 按钮 / 输入框：`$kp-radius-button` / `$kp-radius-input`，默认 12rpx；
- 标签：`$kp-radius-tag`，默认 999rpx。

字体层级使用 `Display 48rpx`、`H1 40rpx`、`H2 32rpx`、`Body 28rpx`、`Caption 24rpx`、`Micro 22rpx`。字距保持 0，不使用负字距，也不使用 viewport 字体缩放。

## 6. 共享组件使用规则

| 组件 | 责任 | 页面调用规则 |
|---|---|---|
| `KpPageNav` | 胶囊避让、返回事件、标题 | 标题型页面唯一导航入口；Tab 根页使用 `showBack=false` |
| `KpCreateProgress` | 创建进度 | Hub / 7 个步骤使用；终态页不使用 |
| `KpStatusTag` | 完成、处理中、失败等状态 | 只表达状态，不承担保存或删除主操作 |
| `KpConfirmDialog` | 删除、替换、退出、清空确认 | 取消必须无副作用；确认后显示 loading |
| `KpBottomActionBar` | 页面主 CTA 和安全区 | 一页只保留一组主行动，失败时保留重试入口 |
| `KpButton` | 可访问的按钮状态 | 必须有 default / pressed / disabled / loading 四态 |

没有对应图标时使用已有线性图标资源或新增静态资源；不得用 Emoji 表达删除、设置、帮助、排序、统计等功能。图标按钮必须提供可读的 `aria-label` 或等效辅助文案。

## 7. 创建流程的资源状态合同

所有资源编辑页面都必须能表达以下状态，状态变化同时更新视觉、文案、可点击性和回读数据：

```text
empty -> selecting -> uploading -> ready
ready -> previewing
ready -> replacing -> uploading -> ready | error
ready -> deleting -> empty | error
uploading / processing -> error -> retry
```

状态规则：

- loading / uploading / processing 时锁定重复点击；取消微信文件选择不显示“上传失败”。
- 失败状态必须提供重新加载或重试；不能用空数据覆盖上一次成功回读。
- 替换必须先上传并校验新资源，成功后再切换绑定；失败时保留旧资源。
- 删除只解除演员卡绑定，不删除素材库原文件；删除素材库资源必须由服务端检查引用。
- 保存成功后统一回读草稿，页面显示以后端返回为准，不以本地临时数组作为最终事实。
- 私有素材只保存 `assetId` 和元数据，不保存签名 URL；访问地址按需要现取。

## 8. 五类资源页面对齐

### 8.1 主视觉 `step-visual`

- 首图区域保持稳定比例，空态、上传中、上传失败和已就绪不能改变页面结构高度。
- “选择素材库”与“手机上传”是同一层级的入口；成功后进入 `source_image` 绑定。
- 扩图状态至少区分未开始、处理中、成功和失败；服务端使用 `sourceAssetId` 现签，旧 URL 只作为历史回退。
- 背景图库仍是系统资源，不混入用户素材库选择结果。

### 8.2 参演作品 `step-works`

- 作品信息和剧照管理分成清晰的内容组；作品卡显示封面、剧照数量和管理入口。
- 每部作品最多 3 张剧照，第一张是封面；替换、删除和排序都必须保持顺序回读。
- 空作品、读取失败、保存失败和剧照上传失败不能显示成空白卡。
- 作品剧照选择使用 `work_still`，关联 `workId`，不能把不同作品的选择会话混用。

### 8.3 生活照片 `step-photos`

- 网格项尺寸稳定，删除按钮不推动其他项重排；序号和封面规则可见。
- 素材库多选与手机上传进入同一个有序列表，最多 12 张；翻页或返回素材库不能丢失已选项。
- 空态给出明确上传 / 选择动作；处理中和失败项必须有可恢复状态。
- 排序使用统一的明确操作，不把“可排序”写成没有 handler 的静态文案。

### 8.4 视频简历 `step-video`

- 预览区域保持稳定视频比例；加载、预览失败和无资源状态不改变 CTA 位置。
- 允许选择、上传、预览、替换、删除和跳过；替换前保留旧视频直到新视频 ready。
- 选择和上传统一使用 `video_resume`，默认分类 `self_intro`。

### 8.5 附件简历 `step-attachment`

- 文件卡必须区分未绑定、processing、ready、failed 和历史 URL 五种可读状态。
- ready 状态显示预览入口；预览按 assetId 现取页图，不缓存签名 URL。
- 附件沿用 00-214 的三态：不传 `attachment` 表示不变，绑定 assetId，`assetId: null` 才表示显式清空。
- 只显示真实 PDF 合同：单份、≤20MB、≤20 页；不得恢复 PPT / PPTX 文案。

## 9. 素材选择模式对齐

`pkg-profile/assets/index` 在 `mode=card-select` 下仍是素材选择页，不是另一个素材管理 Tab：

- 页面标题、媒体类型、默认分类、单选 / 多选上限和已选数量来自 `requestId` 会话。
- 选择结果只返回 `assetId`、媒体类型、分类、状态、文件名和顺序；不返回或持久化签名 URL。
- 确认、取消、系统返回、页面卸载和失败重试都必须清理当前 `requestId`，不能污染头像或作品的旧单例状态。
- 选择页新增上传必须先进入 `actor_media_asset`，再把 assetId 返回向导；不能直接写演员卡 URL。
- 选择页的空态、处理中、失败、预览和安全区规则与向导资源卡一致。

## 10. 开发验收清单

每个页面或共享组件完成前，逐项确认：

- [ ] 页面壳层、导航、进度和底部 CTA 使用规定组件。
- [ ] 新增颜色、字号、间距、圆角和阴影均来自 `$kp-*` Token。
- [ ] 页面在 iPhone SE 宽度下文本、按钮、资源卡和底部安全区不重叠。
- [ ] 所有异步操作有 loading、成功、失败和重试状态；重复点击已锁定。
- [ ] 资源状态与后端回读一致，未把 `wxfile://` 或签名 URL 作为持久化数据。
- [ ] 删除、替换、退出和清空具备确认与失败恢复。
- [ ] 素材选择使用 requestId 会话，确认 / 取消 / 返回 / unload 都能清理。
- [ ] 视觉入口对应真实 handler；没有“即将开放”或无消费方的假入口。
- [ ] 修改完成后再按对应 Spec 执行类型检查、构建、运行态截图和专项门禁。

## 11. 关联文档

- `docs/ui-style-guide-v3.md`
- `.sce/specs/SHARED_CONVENTIONS.md`
- `.sce/specs/00-221-current-phase-miniapp-v3-ui-style-system/`
- `.sce/specs/00-222-current-phase-actor-card-asset-library-and-wizard-integration/`
- `kaipai-frontend/src/styles/_tokens.scss`
- `kaipai-frontend/src/components/KpPageNav.vue`
- `kaipai-frontend/src/pkg-actor-card/components/KpCreateProgress.vue`
