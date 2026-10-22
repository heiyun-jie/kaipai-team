# 小程序 TDesign 组件体系整体迁移 - 任务清单

## T0 Spec 与接入探针

- [x] **Validates: Requirements 1-7** 记录用户裁决、依赖版本、整体迁移边界、24 页批次和“整体完成”定义。
- [x] **Validates: Requirements 4.1, 5, 6** 安装 `tdesign-miniprogram@1.16.0`，验证 uni-app CLI 的原生 npm 组件复制路径。
- [x] **Validates: Requirements 4.1** 确立无需 DevTools 手工“构建 npm”的可重复构建方式，并记录生成 `usingComponents`。
- [x] **Validates: Requirements 4.1, 5** 记录引入前后主包、各分包和总产物 apparent bytes。

## T1 素材库试点

- [x] **Validates: Requirements 4.4** 过滤照片、视频、PDF 选择取消；取消不显示失败、不创建无效重试。
- [x] **Validates: Requirements 4.4** 将重试按钮限制为存在 `pendingUpload` 的真实上传失败，切 Tab / 新选择 / 成功后清理旧错误。
- [x] **Validates: Requirements 4.2-4.4** 用 `t-image` 展示 ready 照片签名缩略图，用 `t-icon` 展示视频 / PDF 状态，用 `t-button` 承载命令操作。
- [x] **Validates: Requirements 4.4, 5** 单条缩略图失败隔离，签名 URL 仅页面会话缓存，预览与素材 API 合同保持不变。

## T2 四个 Tab 根页

- [x] **Validates: Requirements 4.2, 4.3, 4.5** 迁移 `home` 通用按钮、图片、标签、加载和空态。
- [x] **Validates: Requirements 4.2, 4.3, 4.5** 迁移 `card-list` 通用按钮、图片、Tab、Dialog 和分享按钮，验证 `open-type=share`。
- [x] **Validates: Requirements 4.2, 4.3, 4.5** 迁移 `mine` 列表、图标、状态与反馈，保留独立资料路由合同。
- [x] **Validates: Requirements 4.3** 素材库继续迁移 `t-tabs`、ActionSheet 与 Dialog；短时 Toast 保留平台能力，持久错误使用页面状态。

## T3 创建向导与公开观看

- [x] **Validates: Requirements 4.3, 4.5** 迁移 `pkg-actor-card` 10 个页面的通用控件，保留 Kp 导航、创建进度和素材绑定业务组合。
- [x] **Validates: Requirements 4.3, 4.5** 验证输入清空、上传、排序、弹窗滚动、固定 CTA、安全区、生成和公开观看状态。

## T4 资料、登录和工具页

- [x] **Validates: Requirements 4.3, 4.5** 迁移 `actor-profile/edit`、`login`、`pkg-profile/*` 和 `pkg-card/verify`。
- [x] **Validates: Requirements 4.3, 4.5** 迁移历史详情与 `pkg-tools/*`，保留播放器和旧卡兼容。

## T5 退场与全量验收

- [x] **Validates: Requirements 4.3-4.5** 删除无消费者的通用 Kp 组件和页面局部重复基础控件样式。
- [x] **Validates: Requirements 4.5, 5** 24 页矩阵无 pending，src/build/dev、usingComponents、scope hash 和包体全部通过。
- [x] **Validates: Requirements 4.2, 4.4** `pages/assets/index` 完成缓存清理后的运行态截图、按钮图标尺寸和 ActionSheet 密度核验。
- [ ] **Validates: Requirements 4.2, 4.5** 按 00-223 采集桌面不干扰的运行态截图与交互证据。
- [x] **Validates: Requirements 6** 同步 `SHARED_CONVENTIONS.md`、`docs/ui-style-guide-v3.md`、Spec 索引和代码映射。

## 验证记录（2026-08-19）

- `npm run type-check`：通过。
- 原始 Uni build 与 dev 首轮编译：通过，无 `popup/popup` 缺 JSON 告警；dev watch 在 `ready` 后由本任务主动停止，未操作 DevTools。
- `npm run verify:tdesign-migration`：1292 / 1292。
- `npm run verify:v3-ui-legacy-colors`：通过（10 处均在既有 3 文件白名单）。
- `npm run verify:nav-title`：101 / 101。
- `npm run audit:mp-package`：全部包 < 2 MB；脚本仅因 7 处既有 Uni/Vue 文档链接和本地 API URL 最终退出 1。
- apparent bytes：引入前主包 `495,101`；最终主包 `1,389,926`（增量 `894,825`）；总产物 `2,001,571`；`pkg-actor-card 275,388`；`pkg-card 130,624`；`pkg-profile 162,773`；`pkg-tools 42,860`。
- 发布兼容：后端接口、请求字段、数据库、迁移 SQL 和发布顺序均无变化；旧前端契约不受影响。

## 素材库运行态回归修正（2026-08-19）

- 用户提供的 `pages/assets/index` 截图确认 TDesign Tabs / Button / Image 已加载，但上传与更多按钮的本地 SVG 未显示；此前结构门禁不足以证明视觉正确，运行态验收继续保持未完成。
- 根因：本地 SVG 直接传入 `t-button icon`，其内部 `t-icon` 未获得稳定尺寸；已改为按钮默认插槽内显式 `t-icon size="32rpx"`，并同步修正 `pkg-profile/assets/index`。
- 上传/更多按钮点击区统一为 `64rpx`，上传按钮右侧留白 `24rpx`，素材行最低高度 `120rpx`；上传、选择、预览、分类、重命名和删除业务逻辑未变。
- `verify:tdesign-migration` 新增禁止本地 SVG Button icon 属性、要求源码及 build/dev WXML 都存在按钮内嵌图标、保留稳定点击区、紧凑 ActionSheet 密度和存储键展示降级的断言；结果 `1327 / 1327`。
- `type-check`、`verify:nav-title`、`verify:v3-asset-wizard`、`verify:v3-ui-legacy-colors` 均通过；build/dev WXML 均存在按钮内嵌 `t-icon`，对应 WXML/WXSS/JS scoped hash 各自一致。
- `audit:mp-package` 各包均小于 `2 MB`；总脚本仍只因 7 处既有 Uni/Vue 文档链接及本地 API URL 退出 1，与本次 UI 修正无关。
- 微信 MCP 内部 refresh / openPage 后采集的运行态仍是旧编译包：元素 WXML 继续带旧 `icon=...`、`88x82rpx`，内部图标实测 `0x0px`；同一时刻磁盘 `dist/dev` 已是按钮内嵌 `t-icon`、`64x64rpx`。该证据确认旧运行态缓存尚未换包，不再继续猜改源码。
- 经用户明确授权后，只退出固定项目窗口并由 `sync-mp-weixin.ps1` 清理 `WeappCache`、重新镜像 build→dev；重新打开的运行态元素已变为内嵌 `t-icon size="32rpx"`，按钮实际约 `64rpx`，图标可见。
- 素材操作 ActionSheet 已从 TDesign 默认大字号/大行高收口为 `28rpx/40rpx`、约 `88rpx` 操作行、`16rpx` 顶部圆角；预览、重命名、修改分类、删除和取消项均正常展示，遮罩正常拦截背景。
- 旧数据中的长对象式名称已在展示层降级为“未命名照片 / 未命名视频 / 未命名 PDF”；MCP 实测当前行标题为“未命名照片”，重命名和后端 `originalName` 原值未改变。
- 证据：旧缓存截图 `.sce/evidence/wechat-devtools/00-226-assets-icon-fix-20260819.png`；图标修正截图 `00-226-assets-icon-fix-loaded-20260819.png`；ActionSheet 密度截图 `00-226-assets-action-sheet-compact-20260819.png`；最终对齐截图 `00-226-assets-final-aligned-20260820.png`。
- 最终 MCP 产物检查：`pages/assets/index` build/dev 的 JS、WXML、WXSS SHA-256 分别完全一致，三件套 scoped hash 均为 `data-v-44acd705`。素材库单页运行态通过；24 页全量截图任务仍未完成。

## 完成门

只有 T0-T5 全部关闭，且不存在“页面仍使用重复原生通用控件但任务标完成”、TDesign 整库全局注册、单包超 2 MB、分包模块缺失、取消误报或图片无缩略图，才能将本 Spec 状态改为完成。
