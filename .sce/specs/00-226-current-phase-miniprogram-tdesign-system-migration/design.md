# 小程序 TDesign 组件体系整体迁移 - 技术设计

_Requirements: 4.1-4.5, 5, 6_

## 1. 权威关系

迁移后的实现优先级：

1. 页面业务 Spec 和 API 合同。
2. 00-221 / `docs/ui-style-guide-v3.md` 的视觉合同。
3. `_tokens.scss` 的 3.0 Token。
4. TDesign 通用基础组件。
5. Kp 业务组合组件。
6. 页面局部布局样式。

TDesign 是实现工具，不是新的视觉权威。组件示例中的默认页面结构、字号和留白不能覆盖 3.0 参考图。

## 2. 依赖与目录策略

固定依赖：

```json
"tdesign-miniprogram": "1.16.0"
```

T0 探针确认当前 Uni CLI 不能稳定直接复制 TDesign npm 原生组件，因此正式采用受控生成路径：

1. `scripts/sync-tdesign-miniprogram.mjs` 从固定版本 npm 包读取 allowlist 入口，递归解析 `usingComponents`、WXML 和 WXSS 依赖。
2. esbuild 将官方 ESM 和 dayjs / tslib 闭包打成微信可执行 IIFE；生成目录固定为 `src/wxcomponents/tdesign-miniprogram`，不得手工修改或提交。
3. 页面 `style.usingComponents` 引用 `/wxcomponents/...`；脚本同时为完整递归闭包生成 Uni 编译器探针，避免 `popup/popup` 等“真实 JSON 存在但探针缺失”的构建告警。
4. 图标只从 `tdesign-icons-svg@0.4.6` 生成本地 SVG allowlist，不复制远程字体和完整图标字体。

不使用 app 级全局 `usingComponents`。每个页面 JSON 只出现实际用到的组件；相同分包可在构建阶段去重，但不得假设分包运行时能读取外部业务模块。

平台边界：系统媒体选择、预览、播放器、WebView、导航和短时 `uni.showToast` 保留为微信 / uni-app 能力。`uni.showModal` 与 `uni.showActionSheet` 已从 24 个登记页面清零，由受控 TDesign Dialog / ActionSheet / Popup 接管。

## 3. 主题适配

新增 `src/styles/_tdesign.scss`，在 `App.vue` 全局样式中加载。该文件只定义 TDesign CSS variables 到 3.0 常量的映射，不包含页面布局。

主题映射至少覆盖：

- brand / brand-active / brand-disabled。
- text-primary / secondary / placeholder / disabled。
- bg-page / bg-container / bg-secondary-container。
- border-level-1 / divider。
- success / warning / error。
- radius-small / default / large。
- font-size、button height 和 control height 在组件局部 class 中按 3.0 合同校正。

由于原生组件可能启用 style isolation，变量必须通过组件支持的 CSS custom properties 或组件暴露的 `custom-style` / class 接口传入；不能依赖跨组件普通选择器穿透。

## 4. 页面接入模式

### 4.1 原生组件事件适配

页面直接使用 TDesign 原生小程序组件时，事件值统一从 `event.detail` 提取。复杂转换集中为页面小函数，不在模板写多层表达式。

```ts
function onTabChange(event: { detail?: { value?: string } }): void {
  const value = event.detail?.value;
  if (value === 'photo' || value === 'video' || value === 'pdf') switchType(value);
}
```

需要 `open-type` 的按钮先以单页探针验证编译产物与事件透传，未验证前保留原生 button，不做表面替换。

### 4.2 Kp 组合组件边界

保留：

- `KpPageNav`、`KpFloatingBackButton`：微信胶囊与分包导航合同。
- `KpCreateProgress`：创建流程语义。
- `KpBottomActionBar`：可逐步改为内部使用 `t-button`，外部业务 API 保持不变。

候选退场：

- `KpButton` -> `t-button` 或只保留兼容薄封装。
- `KpInput` -> `t-input`。
- `KpConfirmDialog` -> `t-dialog`。
- `KpStatusTag` 仅在 TDesign Tag 能完整表达业务状态时迁移。

删除任何 Kp 组件前，以 src import 和 dist `usingComponents` 双侧确认零消费者。

## 5. 素材库试点设计

### 5.1 视觉合同

- 路由：`pages/assets/index`。
- 用户指出的可见块：素材列表行左侧媒体标记，以及列表下方常驻“选择素材失败 / 重试上传”。
- 目标：ready 照片左侧显示稳定的 88rpx 正方形真实缩略图；视频 / PDF 使用 TDesign 语义图标；取消系统选择不产生任何错误块。
- 保持不变：顶部导航、照片/视频/PDF业务筛选、分页、轮询、预览、重命名、分类、删除和素材 API。

### 5.2 状态模型

```ts
type PreviewState =
  | { status: 'idle' }
  | { status: 'loading' }
  | { status: 'ready'; url: string }
  | { status: 'error' };

const previewByAssetId = reactive<Record<number, PreviewState>>({});
```

- `load(true)` 返回照片列表后，为 ready 且未请求的最多 10 条并发调用 `requestAssetAccessUrl`。
- `load(false)` 只请求新追加照片。
- 单条签发失败写 `error`，不设置 `loadError`。
- 页面隐藏 / 卸载不持久化 URL；重新进入列表可重新签发。
- 点击图片时优先使用仍在页面缓存中的 URL，否则重新签发后预览。

### 5.3 取消识别

统一使用：

```ts
function isPickerCancel(error: unknown): boolean {
  const message = String((error as { errMsg?: string; message?: string })?.errMsg
    || (error as Error)?.message || '').toLowerCase();
  return message.includes('cancel');
}
```

`chooseImage`、`chooseVideo`、`chooseMessageFile` 的取消全部静默返回。开始新选择、切换类型和成功上传时清空旧 `uploadError`。`retryUpload` 只在 `pendingUpload` 非空时渲染。

### 5.4 首批 TDesign 组件

素材库首批只使用低耦合组件：

- `t-image`：照片缩略图的 lazy / loading / error。
- `t-icon`：视频、文件、添加和更多操作图标。
- `t-button`：上传、重试和空态命令按钮。

`t-tabs`、`t-action-sheet`、`t-dialog` 留到 T1：先验证三个低耦合组件的 uni-app 编译、样式变量和包体闭包，再扩大接入面。

本项目移除了 TDesign 远程图标字体，只保留本地 SVG allowlist。`t-button` 的 `icon` 属性在未显式传入尺寸时会让内部 `t-icon` 依赖节点实测高度，图标字体退场后可能得到零尺寸。因此按钮内的本地 SVG 必须通过默认插槽显式渲染 `t-icon` 并固定 `size`，禁止把 `/wxcomponents/tdesign-miniprogram/icon/assets/*.svg` 直接传给 `t-button icon`。素材库上传/更多按钮使用 `64rpx` 稳定点击区和 `32rpx` 图标；上传按钮与页面右侧保持 `24rpx` 留白，列表行最低 `120rpx`。

素材操作 ActionSheet 不直接沿用 TDesign 默认 `32rpx` 大字号和 `112rpx` 级行高。两个素材库页面通过组件 `custom-style` 局部设置 `--td-font-body-large: 400 28rpx/40rpx`、`--td-spacer-2: 24rpx` 和 `16rpx` 顶部圆角，使普通操作行与取消项收口到约 `88rpx`；该变量只作用于当前 ActionSheet，不污染其他 TDesign 组件。

素材列表标题继续以 `originalName` 为业务事实，但展示层识别长度不少于 32 位、只由字母/数字/下划线/连字符组成且同时含字母数字的存储键式名称，并降级显示为“未命名照片 / 未命名视频 / 未命名 PDF”。正常文件名只去除路径前缀后原样展示；重命名、更新接口和持久值不变。

## 6. 迁移矩阵

| 批次 | 页面 | 重点组件 | 业务回归重点 |
|---|---|---|---|
| T0 | `pages/assets/index` | image/icon/button | 取消、签名缩略图、上传、预览、分页 |
| T1 | `pages/home`、`card-list`、`mine` | image/button/tabs/tag/result | Tab 根页、分享 open-type、删除、入口路由 |
| T2 | `pkg-actor-card/*` 10 页 | button/input/textarea/switch/upload/popup/dialog | 7 步保存、素材绑定、排序、生成和公开观看 |
| T3 | `actor-profile/edit`、`login`、`pkg-profile/*`、`pkg-card/verify` | form/cell/input/picker/dialog/popup | 表单值、导入、作品弹窗滚动、登录授权 |
| T4 | `pkg-card/ai-profile-card-detail`、`pkg-tools/*` | image/button/loading/result | 历史兼容、视频播放、帮助与设置 |
| T5 | 全 24 页 | 清理与统一 | 零悬空组件、全截图、包体、无 legacy 回退 |

## 7. 验证与门禁

新增 `scripts/verify-00226-tdesign-migration.mjs`，至少检查：

1. 依赖精确版本。
2. 禁止 app 全局注册 TDesign。
3. 素材库存在 TDesign image/icon/button 声明和组件节点。
4. 素材库取消过滤、错误清理、`pendingUpload` 重试门禁。
5. 照片签名 URL 只在页面会话预览映射，不进入 Pinia 或持久请求体。
6. 生成 page JSON 的 `usingComponents` 指向存在的组件文件。
7. build/dev 页面 WXML/WXSS/JS 与 TDesign 组件目录均存在。
8. 迁移矩阵 pending 数量随批次单调递减。
9. 禁止 `t-button` 通过 `icon` 属性直接引用本地 SVG；素材库上传/更多按钮必须编译为按钮内嵌 `t-icon`，并保留固定点击区和显式图标尺寸。

每批运行：

```text
npm run type-check
npm run verify:tdesign-migration
npm run verify:v3-ui-legacy-colors
npm run verify:nav-title
npm run build:mp-weixin
npm run audit:mp-package
```

DevTools 运行时若正式同步脚本拒绝构建，允许使用项目内 Uni CLI 生成 build、`dev:mp-weixin` 首轮生成 dev，并分别核对；不得杀掉或控制用户桌面。

## 8. 发布兼容

- 前端依赖和模板替换可独立发布，后端和数据库不变。
- 旧前端继续消费原接口；新前端不提交新字段。
- TDesign 依赖必须进入 lockfile，构建环境执行正常 npm install 即可复现。
- 若按需同步脚本发生错误，发布门禁应失败，不能回退到 DevTools 手工构建 npm 的隐式步骤。
- 每批可通过回退页面模板、page usingComponents 和依赖变更独立撤销，不需要数据回滚。

## 9. 实施结果（2026-08-19）

- 24 / 24 登记页面均有精确 TDesign 组件矩阵；源码与 build/dev WXML 中原生 `button / input / textarea / image / switch / picker / checkbox` 和 `uni.showModal / uni.showActionSheet` 均为 0。
- 递归运行闭包：`action-sheet / badge / button / checkbox / dialog / grid / grid-item / icon / image / input / loading / overlay / picker / picker-item / popup / sticky / switch / tab-panel / tabs / tag / textarea`。
- `KpButton / KpInput / KpConfirmDialog / KpIdentityStatusCard / KpStatusTag` 已确认源码与产物零消费者后删除；业务组合组件保留。
- `verify:tdesign-migration` 共 1292 项通过，覆盖依赖、24 页源码、build/dev JSON/WXML/JS、open-type、组件闭包、本地图标、无远程字体和 scoped hash。
- apparent bytes：总产物 `2,001,571`；主包 `1,389,926`；`pkg-actor-card 275,388`；`pkg-card 130,624`；`pkg-profile 162,773`；`pkg-tools 42,860`；全部低于 2 MB。TDesign 生成闭包约 `893,326` B。
- `audit:mp-package` 包大小门禁通过，但总脚本仍被 7 处既有 Uni/Vue 文档链接及本地后端 URL 阻断；TDesign 目录无远程 URL。
- 接口、请求字段、数据库和发布顺序均未改变；旧版本前端兼容结论不变。
