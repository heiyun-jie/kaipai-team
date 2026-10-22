# 00-221 3.0 小程序最终 UI 风格系统与交互视觉合同 - 任务清单

## 一、文档与决策门

- [x] 基于 00-220 调查结论建立 3.0 UI 风格系统 Spec。
- [x] 创建独立风格手册 docs/ui-style-guide-v3.md。
- [x] 明确 22 个实际路由、8 个旧棕米色页面、13 个蓝白硬编码页面和 TabBar 资源风险。
- [ ] T0-1：确认 3.0 是否覆盖全部 22 个可达页面。
- [ ] T0-2：裁决历史分享详情页保留、重皮肤或退场。
- [ ] T0-3：裁决帮助与反馈、设置、素材库选择、排序和真实长图生成的交付批次（素材库选择与排序已由 2026-08-18 用户裁决转入 `00-222`；帮助与反馈、设置已由 2026-08-19 个人中心对齐改为 `pkg-tools/webview` 真实承载页；真实长图仍待单独裁决）。

## 二、T1 Token 与共享壳层

- [x] 在 _tokens.scss 增加 3.0 语义颜色、间距、圆角和阴影 Token。
- [x] 为旧变量建立临时兼容别名和可执行 legacy 颜色白名单。
- [ ] 全部页面迁移完成后删除兼容别名和 legacy 白名单。
- [x] 迁移 KpButton、KpInput、KpStatusTag、KpConfirmDialog、KpBottomActionBar、KpPageNav。
- [x] 让素材库成为稳定的 Tab 根页，消除中间 redirectTo 壳层。
- [x] 重新制作四项 TabBar 的蓝白线性 active / inactive 图标，移除橙色和 rank.png 复用。

## 三、T2 五张参考图页面

- [ ] 首页：图稿复核中；Hero、草稿续编、模板 Tab、模板标识传递和空态待五张视觉图运行态验收。
- [ ] 创建流程：图稿复核中；Hub 图标、7 步状态、进度、底部 CTA、错误态和返回路径待运行态验收。
- [ ] 参演作品：图稿复核中；保留剧照管理、封面、替换、删除和保存反馈，按当前顺序展示并待运行态验收。
- [ ] 生活照片：素材库选择、手机上传、数量提示、删除、显式排序模式和回读已接通；待图稿运行态验收。
- [ ] 个人中心：图稿复核中；统计入口、资料分组、真实服务入口和退出流程待最终运行态验收；帮助与反馈、设置已恢复为参考图三行结构，并分别绑定 `pkg-tools/webview` 的 support / preferences 真实页面，退出登录收在设置页。

## 四、T3 其他页面与操作闭环

- [x] 名片夹：增加草稿删除确认、失败重试、列表刷新和空态。
- [ ] 向导剩余步骤：统一视觉状态、上传失败、预览、替换、附件真实 PDF 合同和排序。
- [ ] 生成 / 观看者页：区分占位、生成中、失败和真实结果，补资源异常态。
- [x] 登录、演员档案、实名认证、资料库、导入复核、视频播放器、WebView 迁移到 3.0 皮肤。
- [x] 让演员档案页消费 mine 入口的 tab query，或修改入口为准确落点。

## 五、T4 验证与治理

- [ ] 新增页面清单、主题 Token、旧色、Emoji、Tab 根页和点击 handler 静态门禁。
- [ ] 每批构建前执行开发者工具关闭 / 缓存清理检查，构建后核对 src、dist/build、dist/dev。
- [ ] 运行 vue-tsc、build:mp-weixin、verify:nav-title、verify:actor-card-attachment、audit:mp-package。
- [ ] 采集七个关键页面的微信运行态截图和点击证据，记录视口、登录态、数据条件和产物哈希。
- [ ] 更新 CURRENT_CONTEXT.md、docs/product-design.md、spec-code-mapping.md 的 22 页基线。
- [ ] 完成接口、数据库、前后端同批次发布和旧数据可读性的发版兼容检查。

## 六、完成定义

本 Spec 只有在 T0 决策完成、T1-T3 的实现任务全部关闭、T4 门禁和运行态证据齐全后，才能标记为 3.0 UI 定稿完成。仅完成 Token 替换、截图接近或构建成功，均不等同于完成。

## 七、首轮执行记录（2026-08-15）

- 已完成全局蓝白 Token、共享组件皮肤和 7 个旧主题页面迁移：登录、演员档案、实名认证、资料库、导入复核、视频播放器、WebView。
- 已将 pages.json 中旧页面的背景色切换为 #FFFFFF；历史分享详情页 pkg-card/ai-profile-card-detail 保留到 T0 裁决，不在本轮改动。
- 已完成 vue-tsc、build:mp-weixin、verify:nav-title（97/97）、verify:actor-card-attachment（17/17）。
- build/dev 目标页面的 WXML、WXSS 字节和 scoped hash 已逐页核对一致；包体大小门禁全部通过。
- audit:mp-package 仍因既有开发环境 5 个 http:// API 地址失败，包体大小检查通过；该项需按 release 构建链路另行收口。

## 八、T1 legacy 门禁执行记录（2026-08-15）

- 新增 `scripts/v3-ui-legacy-color-whitelist.json`，仅允许历史分享详情页及其两个 fallback 工具保留 10 处旧色；白名单按文件、色值和出现次数锁定。
- 新增 `npm run verify:v3-ui-legacy-colors`。任何非白名单旧色、白名单数量增加或迁移后未递减的陈旧基线都会使门禁失败。
- `SHARED_CONVENTIONS.md` 的默认页面结构与间距已切换到 3.0 蓝白规则，并同步当前 `KpCreateProgress` 合同。

## 九、T1 素材库 Tab 根页执行记录（2026-08-15）

- `pages/assets/index` 已删除 `onMounted + redirectTo` 壳层，直接渲染素材库标题、照片/视频/PDF Tab、上传、分页列表、轮询、预览、重命名、分类、PDF 重试、删除、空态和错误重试。
- `pkg-profile/assets/index?mode=avatar-select` 保持不变，继续承担带 query 的头像素材选择和返回回传，避免把选择模式错误塞进不能携带 query 的原生 Tab 路由。
- `verify:nav-title` 已把 assets 纳入四个 Tab 根页并新增“直接渲染且无 redirectTo”断言，当前 101/101 通过。
- 微信构建成功，`dist/build` 与 `dist/dev` 的 assets WXML/WXSS/JS scopeId 均为 `3e1fe052`，四个产物文件逐一 SHA-256 相等；主包 `467.62 KB`，占 2 MB 上限 `22.83%`。
- `audit:mp-package` 包体门禁通过，总体仍仅被既有 5 处开发环境 `http://` 地址拦截；微信运行态截图与 Tab 点击证据留在 T4 统一采集。

## 十、T1 TabBar 图标执行记录（2026-08-15）

- 新增 `scripts/generate-tabbar-icons.ps1`，用同一套 81x81 透明画布、4.5px 圆角线宽和确定性几何路径生成 home / card-list / assets / mine 四组 active / inactive PNG。
- active 资源统一为品牌蓝 `#2F6BFF`，inactive 资源统一为中性灰 `#8E8E93`；`pages.json` 的文字颜色同步为同一组语义色。
- 名片夹使用独立身份卡图标，素材库使用独立叠图图标；旧 `rank.png` / `rank-active.png` 已物理删除，运行时引用和三侧构建产物均为 0。
- 新增 `npm run verify:tabbar-icons`，断言 4 个 Tab、8 条唯一资源路径、8 份不同文件内容、81x81 尺寸、透明画布、active/inactive 色值、无橙色像素且旧 rank 文件不存在。
- 微信构建与 postbuild 同步通过，8 个 PNG 在 `src` / `dist/build` / `dist/dev` 逐文件 SHA-256 一致；主包 `459.45 KB`，占 2 MB 上限 `22.43%`。
- `audit:mp-package` 包体门禁通过，总体仍仅被既有 5 处开发环境 `http://` 地址拦截；运行态四项点击和选中态截图留在 T4 统一采集。

## 十一、T2 首页执行记录（2026-08-15）

- `pages/home/index.vue` 已统一使用 3.0 Token：白色画布、浅灰分组、品牌蓝 CTA / 选中态、16rpx 卡片圆角和固定 24rpx 页面边距；Hero 的符号字符已替换为非功能性 AI 标记，CSS 卡片形状仅作为装饰。
- 草稿区新增读取中、读取失败、重新加载和继续编辑反馈；模板区新增登录引导、加载中、空模板、失败重试和创建中锁定状态，空态均有明确下一步按钮。
- 首页点击的背景库 `images[].id` 现在通过 `create?style=&backgroundId=` 传入 Hub；Hub 回读背景库后立即通过既有 `backgroundImageUrl` 合同写入草稿，同时在打开第 1 步时继续传递 `backgroundId` 作为预选回显兜底。该链路不新增后端字段。
- 新增 `scripts/verify-v3-home.mjs` 与 `npm run verify:v3-home`，当前 17/17 通过（2026-08-16 将背景预选检查改为变量名无关的语义断言，并补正反自检）；该门禁同时锁定演员卡风格词表 A、禁止分享卡 scene 专有值进入首页、下拉刷新闭合和背景标识消费链。
- `vue-tsc --noEmit`、`build:mp-weixin`、`verify:nav-title`（101/101）、`verify:actor-card-attachment`（17/17）、`verify:v3-ui-legacy-colors`、`verify:tabbar-icons` 均通过。首页及创建 Hub / 第一步的 `dist/build` 与 `dist/dev` 产物三件套 SHA-256 一致。
- `audit:mp-package` 的包体大小检查通过（主包 466.24 KB，最大分包 120.33 KB）；外链检查仍被既有 `api/actor-asset.js`、`api/file.js`、`utils/request.js`、`utils/runtime.js` 的 5 处开发环境 `http://` 拦截，本轮未扩大范围处理。
- 微信开发者工具运行态截图与点击证据仍属于 T4，当前未宣称首页运行态验收完成。

## 十二、T2 创建 Hub 执行记录（2026-08-15）

- `pkg-actor-card/create/index.vue` 已按 `02-AI创建流程.png` 收口为白色导航 / 进度区、7 张独立步骤卡和固定底部 CTA；数字圆点替换为 7 组 CSS 线稿语义图标，完成状态使用独立圆形勾选节点，未使用 Emoji 或符号字符承担功能图标。
- Hub 新增读取中骨架、草稿加载失败、明确的重新加载按钮和导航失败反馈；步骤点击与底部 CTA 使用 `navigating` 锁定重复点击，底部内容预留 `safe-area-inset-bottom`。
- `KpCreateProgress` 保持 `done/total` 合同，视觉值改为 3.0 Token；Hub 仍使用服务端派生的 7 步状态和已完成步数，不自行推断完成度。
- `actor-card-draft` 在新建 / 切换草稿时清空旧快照，`reload()` 返回成功布尔值；Hub 回前台读取失败时进入可重试错误态，避免旧卡数据残留造成假成功显示。
- 新增 `scripts/verify-v3-create-hub.mjs` 与 `npm run verify:v3-create-hub`，当前 13/13 通过；该门禁覆盖 Token、7 步路由、图标、进度、加载 / 错误 / 重试、CTA 锁定和安全区合同。
- `vue-tsc --noEmit`、`build:mp-weixin`、`verify:v3-create-hub`（13/13）、`verify:v3-home`（15/15）、`verify:v3-ui-legacy-colors`、`verify:nav-title`（101/101）、`verify:actor-card-attachment`（17/17）、`verify:tabbar-icons` 均通过。创建 Hub WXML/WXSS/JS 与 `KpCreateProgress.wxss` 的 `dist/build`、`dist/dev` SHA-256 一致。
- `audit:mp-package` 的包体大小检查继续通过；外链检查仍被既有 5 处开发环境 `http://` 地址拦截，本轮未扩大范围处理。
- 微信开发者工具运行态截图、7 步逐项点击和返回路径证据仍属于 T4，当前未宣称创建流程运行态验收完成。

## 十三、T2 参演作品执行记录（2026-08-15）

- `pkg-actor-card/step-works/index.vue` 已迁移到 3.0 蓝白 Token：白色独立作品卡、浅蓝选中态、封面标记、管理入口和固定底部 CTA；页面保留加载中、空态、失败重试、保存中、保存成功、保存失败和返回失败反馈。
- 剧照管理已支持单张替换、删除确认和最多 3 张限制；删除首张后由下一张按现有顺序成为封面。页面明确提示“剧照按添加顺序展示，首张为封面”，本轮不实现拖拽排序，等待 T0-3 对排序交付批次裁决。
- 作品保存直接调用 `replaceActorCardWorks` 与 `saveActorCardStep`，保存后执行 `draftStore.reload()` 回读，下一步导航锁定重复点击并在失败时恢复可操作状态。草稿页进入时按 `cardId` 清理并重新加载旧快照，避免跨草稿残留。
- `npm run verify:v3-step-works` 通过 `11/11`；同时复跑 `verify:v3-create-hub` `13/13`、`verify:v3-home` `15/15`、`verify:v3-ui-legacy-colors`、`verify:nav-title` `101/101`、`verify:actor-card-attachment` `17/17`、`verify:tabbar-icons` 和 `npm run type-check`，全部通过。
- `npm run build:mp-weixin` 及自动 `postbuild:mp-weixin` 通过；`dist/build/mp-weixin/pkg-actor-card/step-works/index.{wxml,wxss,js}` 与 `dist/dev/mp-weixin/pkg-actor-card/step-works/index.{wxml,wxss,js}` 三件套 SHA-256 逐一一致，生成产物已包含管理、封面、替换/删除、保存反馈和安全区样式。
- 最新包体大小检查通过：主包 `466.33 KB`，`pkg-actor-card` `136.61 KB`，总产物 `842.66 KB`，均未超过 2 MB；`audit:mp-package` 整体仍因既有 5 处开发环境 `http://` 地址失败（`api/actor-asset.js` 2 处、`api/file.js`、`utils/request.js`、`utils/runtime.js`），本轮未修改这些开发环境地址。
- 微信开发者工具运行态截图、真实点击和多设备响应式证据仍属于 T4；本记录不把静态门禁和构建结果宣称为运行态验收。

## 十四、T2 生活照片执行记录（2026-08-15）

- `pkg-actor-card/step-photos/index.vue` 已按 3.0 蓝白 Token 重做页面主体：统一导航 / 进度、照片数量区、手机上传卡片、3 列照片网格、空态、错误态和固定底部 CTA；Emoji 与页面级硬编码颜色已移除，上传和删除图标改为 CSS 线稿。
- 保留 `00-218` 已落地的手机上传链路：逐张调用 `uploadImageFile`，仅把公网 URL 写入本地照片数组；上传中锁定入口，失败展示错误提示和重新选择操作，已上传成功的前序照片不丢失。
- 删除照片改为确认对话框，删除首张时明确下一张自动成为封面；页面显示最多 12 张建议但不人为截断，照片按添加顺序展示。历史 `wxfile://` 数据回读时过滤，不再写回演员卡。
- 保存改为直接调用 `saveActorCardStep`，保存后执行 `draftStore.reload()` 回读；新增保存中、保存成功、保存失败、下一步导航锁定和返回失败反馈。草稿切换时按 `cardId` 重新读取，避免旧快照残留。
- 新增 `scripts/verify-v3-step-photos.mjs` 与 `npm run verify:v3-step-photos`，当前通过 `11/11`；同批复跑 `type-check`、作品 `11/11`、创建 Hub `13/13`、首页 `15/15`、旧色、导航 `101/101`、附件 `17/17` 和 TabBar 门禁，全部通过。
- `npm run build:mp-weixin` 及自动 `postbuild:mp-weixin` 通过；`dist/build` 与 `dist/dev` 的 `pkg-actor-card/step-photos/index.{wxml,wxss,js}` 三件套 SHA-256 逐一一致，生成产物已包含上传卡、删除按钮、继续添加、保存反馈和安全区样式。
- 最新包体大小检查通过：主包 `466.33 KB`，`pkg-actor-card` `148.03 KB`，总产物 `854.09 KB`，均未超过 2 MB；`audit:mp-package` 整体仍因既有 5 处开发环境 `http://` 地址失败，本轮未修改这些开发环境地址。
- 素材库选择和拖拽排序仍保持未交付：依据 `00-213` 的已知缺口和 `00-221 T0-3` 未裁决状态，本轮没有保留“即将开放”假入口，也没有实现临时排序逻辑。生活照片任务暂不勾选完成，待 T0-3 裁决后再接通真实来源。
- 微信开发者工具运行态截图、真实上传 / 删除 / 返回点击和多设备响应式证据仍属于 T4；本记录不把静态门禁和构建结果宣称为运行态验收。

## 十五、T2 个人中心执行记录（2026-08-15）

- `pages/mine/index.vue` 已按 `05-个人中心.png` 收口为白色卡片、浅灰画布、品牌蓝进度和分组列表：个人资料卡、资料完整度、统计区、演员资料、账户与服务和退出操作均保留清晰层级。
- 个人资料、演艺经历、自我介绍、实名认证、演员卡统计和素材统计均绑定真实路由；统计区的演员卡和素材可分别进入 `card-list` / `assets` Tab，浏览统计保持只读，避免伪造详情页。2026-08-19 用户裁决后，资料分组按 `00-225` 分流：个人资料进入 `pages/actor-profile/edit`，演艺经历进入 `pkg-profile/works/index`，自我介绍进入 `pkg-profile/intro/index`。
- 个人资料 / 演艺经历 / 自我介绍入口使用 CSS 线性图标，移除全部 Emoji；`actor-profile/edit.vue` 不再消费 `tab=experience` / `tab=intro`，旧 query 锚点合同由 `00-225-current-phase-mine-profile-entry-dedicated-pages` 撤销。
- 帮助与反馈、设置当前无真实页面，已从 `serviceItems` 删除，不再保留“即将开放”假操作；实名认证保留为唯一真实账户服务入口。
- 完整度读取失败现在显示错误状态和“重新加载”操作；退出登录继续使用 `KpConfirmDialog` 危险确认，执行期间锁定按钮并反馈，成功后回到首页，重定向失败给出提示。
- 新增 `scripts/verify-v3-mine.mjs` 与 `npm run verify:v3-mine`，当前通过 `10/10`；同批复跑 `type-check`、生活照片 `11/11`、作品 `11/11`、创建 Hub `13/13`、首页 `15/15`、旧色、导航 `101/101`、附件 `17/17` 和 TabBar 门禁，全部通过。
- `npm run build:mp-weixin` 及自动 `postbuild:mp-weixin` 通过；`pages/mine/index.{wxml,wxss,js}` 与 `pages/actor-profile/edit.{wxml,wxss,js}` 在 `dist/build`、`dist/dev` 两侧三件套 SHA-256 逐一一致，生成产物已包含 CSS 图标、真实路由、统计重试、退出确认和安全区样式。
- 最新包体大小检查通过：主包 `472.97 KB`，`pkg-actor-card` `148.03 KB`，总产物 `860.73 KB`，均未超过 2 MB；`audit:mp-package` 整体仍因既有 5 处开发环境 `http://` 地址失败，本轮未修改这些开发环境地址。
- 微信开发者工具运行态截图、统计点击、query 展开、退出确认和多设备响应式证据仍属于 T4；本记录不把静态门禁和构建结果宣称为运行态验收。

## 十六、T4 首页背景预选门禁语义修正（2026-08-16）

- 复核 `verify:v3-home` 时发现唯一红项不是实现缺失：`step-visual` 已通过 `Number(props.backgroundId)` 读取背景标识，并用背景项 `id` 匹配后回显；旧断言却硬编码寻找不存在的局部变量名 `b` / `requestedBackgroundId`，形成 `14/15` 误报。
- `verify-v3-home.mjs` 已改为捕获实际局部标识符并校验同一标识符参与 `find(...item.id === requestedId)`，不再把变量命名当作业务合同。
- 门禁增加两项自检：变量重命名后的等价实现必须通过，使用无关 id 变量的实现必须失败，防止修正后空转。
- 本任务不修改页面源码、样式、接口或构建产物；T4 的微信运行态截图、三侧产物复核和发布门禁仍保持未完成。

## 十七、T3 名片夹执行记录（2026-08-16）

- `pages/card-list/index.vue` 已完成加载中、网络错误重试、已发布 / 草稿双空态、下拉刷新和创建入口；草稿删除使用 `KpConfirmDialog` 危险确认，调用既有 `deleteActorCardDraft`，删除中锁定重复点击，失败后在原卡片保留可重试错误，成功后立即从本地列表移除。
- 已发布卡继续保留预览、微信分享和复制创建三项既有能力；草稿卡保留继续编辑与删除。页面仍是直接渲染的原生 Tab 根页，未引入重定向壳层。
- 补齐游客态闭环：未登录时显示「登录后管理名片 / 去登录」，状态按钮与悬浮新建入口共用 `requireLogin`，跳既有 `/pages/login/index`；网络错误仍显示「名片夹加载失败 / 重新加载」，不再把未登录当成点击无效的重试状态。
- `verify:v3-card-list` 增加游客真实登录动作与新建入口登录门禁两项断言，当前 `13/13` 通过；`type-check`、`verify:nav-title`（`101/101`）、`verify:v3-ui-legacy-colors`、`verify:tabbar-icons`、`verify:v3-home`（`17/17`）均通过。
- `npm run build:mp-weixin` 与 postbuild 同步成功，build/dev scoped hash 全树断言通过。名片夹三件套两侧 SHA-256 分别一致：WXML `A1356D2F...4006`、WXSS `BDE89BE9...9806`、JS `2C55D4E9...9DB3`；`dist/dev` 已包含游客状态绑定、登录失败反馈、删除 API 调用、状态按钮 `padding: 18rpx 32rpx` 和底部安全区。
- 包体审计的大小门禁通过：主包 `480.83 KB`、`pkg-actor-card` `204.20 KB`、总产物 `924.76 KB`，均低于 `2 MB`。整体审计仍仅被既有 5 处开发环境 `http://` 地址拦截，本任务未改环境地址。
- 发版兼容：本任务仅复用既有登录路由与删除接口，不改后端、数据库、路由登记或演员卡数据合同。微信开发者工具中的真实登录、删除成功 / 失败和四项 Tab 点击截图仍归 T4，本记录不宣称运行态验收完成。

## 十八、T3 演员档案 query 落点执行记录（2026-08-16；2026-08-19 已撤销）

- 本节原合同要求个人中心的「演艺经历」与「自我介绍」通过 `/pages/actor-profile/edit?tab=experience`、`/pages/actor-profile/edit?tab=intro` 落到个人资料页内展开区块。2026-08-19 用户明确裁决后，该方案撤销，当前以 `00-225-current-phase-mine-profile-entry-dedicated-pages` 为准。
- 当前合同：个人资料进入 `pages/actor-profile/edit`；演艺经历进入 `pkg-profile/works/index` 管理真实 `/api/actor/works` 经历；自我介绍进入 `pkg-profile/intro/index` 单独保存 `actor_profile.intro`。
- `verify:v3-mine` 已改为禁止旧 query 锚点和 `actor-profile/edit.vue` 的 `requestedTab` / `scrollIntoView` / `introExpanded` / `introSummary` 等同页伪装实现。本记录不再作为当前验收依据，仅保留为历史回溯。

## 十九、T0-3 素材库与排序转立项（2026-08-18）

- 用户已明确要求建立独立 Spec，将素材库接入创建流程并打通选择与排序；该决策由 `00-222-current-phase-actor-card-asset-library-and-wizard-integration` 承接。
- 本记录只关闭 T0-3 中“素材库选择与排序”的决策缺口，不关闭整个 T0-3；帮助与反馈、设置和真实长图生成仍待单独产品决策。
- `00-222` 明确不把素材库私有桶的短时签名 URL 写入演员卡 URL 字段，采用 assetId 绑定、服务端验权、现签读取和旧 URL 回退，避免把选择功能做成过期死链。

## 二十、五张视觉图复核（2026-08-18）

- 用户反馈当前运行态没有按五张本地视觉图完成对齐，因此首页、创建流程、参演作品、生活照片、个人中心的 T2 状态重新打开，不能以此前静态门禁或历史构建记录宣称验收完成。
- 本轮视觉合同：白色画布、约 `40rpx` 页面边距、细边框白卡、品牌蓝仅用于 CTA/进度/选中态；首页保留真实的风格 Tab 过滤，不能将静态稿中的四张示例错误改为同屏混合模板。
- 生活照片默认仅呈现「调整顺序」入口；用户明确进入排序模式后才显示上移/下移操作，以保留真实排序能力并避免网格被工具按钮长期遮挡。
- 本轮只允许源码层改动和静态检查。用户正在使用微信开发者工具，构建同步、缓存清理、开发者工具控制和运行态截图均暂停，待用户明确允许后再执行三侧产物与人工核验。

## 二十一、R01 首页 Hero 密度与插画比例（2026-08-19）

- 按用户继续反馈，首页 Hero 只调整直接视觉锚点：`home-v2__hero` 外高从 `392rpx` 提到 `416rpx`，内边距改为 `46rpx 28rpx 42rpx 48rpx`；`home-v2__hero-btn` 保持 `196rpx × 64rpx`，上间距从 `28rpx` 提到 `34rpx`。
- 右侧 CSS 插画同步放大：`home-v2__card-illus` 从 `210rpx × 250rpx` 调整为 `246rpx × 292rpx`，前景卡从 `154rpx × 210rpx` 调整为 `174rpx × 240rpx`；该插画仍是装饰层，不替代真实模板、草稿或演员卡内容。
- `verify:v3-home` 通过 `17/17`，`type-check` 通过；2026-08-19 已按用户要求改走 MCP 项目级流程，`wechat_devtools_build(timeoutMs=300000)` 成功清理 WeappCache、构建并同步 `dist/build` 到 `dist/dev`。`wechat_devtools_artifact_check(route=pages/home/index)` 返回 `buildDevEquivalent=true`，首页 WXSS 在 build/dev 两侧 SHA-256 均为 `42B9A94A15A19C80CA02B06A5868CC6CE4747172CCCC98997939194B20C3C9FB`；未置顶、未控制整屏。

## 二十二、R05 个人中心密度对齐（2026-08-19）

- 按用户要求开始对齐个人中心，本轮只收 `pages/mine/index.vue` 的直接视觉锚点：档案卡、头像比例、完整度卡、统计卡、资料分组、服务分组和主页面退出按钮位置；不改个人资料、演艺经历、自我介绍、实名认证、统计跳转等真实交互。
- 第一轮密度目标：`mine-v2__profile-card` 锁定 `192rpx` 外高合同，`mine-v2__completeness-card` 调整为 `168rpx`、`mine-v2__stats-row` 调整为 `136rpx`、`mine-v2__row` 调整为 `116rpx`；统计数字从 Display `48rpx` 降到 H1 `40rpx`，完整度百分比升到 H1 `40rpx`。
- 第二轮按用户再次提供的 R05 图修正：头像从 `128rpx` 放大到 `148rpx`，档案卡内边距收为 `22rpx 28rpx 22rpx 22rpx`；完整度卡收为 `160rpx`，统计卡收为 `128rpx`，资料双行 row 收为 `112rpx`，服务单行 row 收为 `72rpx`；服务区恢复「实名认证 / 帮助与反馈 / 设置」三行，其中帮助与反馈指向 `pkg-tools/webview/index?type=support`，设置指向 `type=preferences`，退出登录从个人中心主页面移入设置页。
- `verify:v3-mine` 增加 R05 密度、服务三行和真实承载页断言，当前 `18/18` 通过；`type-check` 通过；2026-08-19 已按用户要求改走 MCP 项目级流程，`wechat_devtools_build(timeoutMs=300000)` 成功清理 WeappCache、构建并同步 `dist/build` 到 `dist/dev`。`wechat_devtools_artifact_check(route=pages/mine/index)` 返回 `buildDevEquivalent=true`，个人中心 WXSS 在 build/dev 两侧最新 SHA-256 均为 `EB65BD76160371A3E93E3072E3D166CDC36EF833E7FE25EDDFE614C8CAED25BF`；`pkg-tools/webview/index` 也返回 `buildDevEquivalent=true`。内部模拟器已打开 `pages/mine/index` 并采集 `.sce/evidence/wechat-devtools/mine-reference-align-20260819-v2.png`，console `grep -i error` 无命中，未置顶、未控制整屏。
- 用户继续指出“演员资料 / 账户与服务字体和间距严重不一致”后，追加第三轮只改列表内部锚点：新增 `kp-font-size-list-title: 26rpx`，资料行主文案 `26rpx`、副文案 `22rpx`、副文案上间距 `6rpx`；服务行 `76rpx`、主文案 `24rpx`、左内边距/图标文字 gap 收为 `24rpx + 12rpx`；图标描边 `3rpx → 2rpx`，实名认证图标从旋转形态恢复为盾牌，右箭头取消缩放。`verify:v3-mine`、`type-check`、`wechat_devtools_build` 均通过；`pages/mine/index` 最新 WXSS SHA-256 为 `49BE387284437019C389E436039072E0FDAE5D8A1DDAF1C6F2A19BD01B08A4CC`，v4 截图 `.sce/evidence/wechat-devtools/mine-list-density-20260819-v4-retry.png` 已归档。

## 二十三、演员档案顶部分割线下移（2026-08-19）

- 按用户截图反馈，`pages/actor-profile/edit` 顶部红框所指为普通返回模式 B 的本地导航分割线，不是正文卡片分割线；本轮只调整 `.profile-edit__nav` 的直接视觉锚点，不改 `KpPageNav`、不改 `KpFloatingBackButton` 本体，也不重排正文表单。
- `.profile-edit__nav` 从直接 `border-bottom` 改为本地 `::after` 伪元素承载分割线，并增加 `padding-bottom: $kp-spacing-lg`；`.profile-edit__nav-title` 同步设置 `bottom: $kp-spacing-lg` 抵消底部预留，视觉结果为分割线下移 `32rpx`，标题 / 返回按钮位置保持稳定。
- `docs/ui-style-guide-v3.md` 已补充模式 B 的导航分割线合同：此类页保留 `KpFloatingBackButton + 本地居中标题 + sticky 导航容器`，顶部分割线不得贴住标题 / 胶囊行，应由本地导航容器底部伪元素承载并至少预留 `$kp-spacing-lg` 呼吸位。
- `type-check` 通过，`verify:nav-title` 通过 `101/101`；`wechat_devtools_build(timeoutMs=300000)` 成功执行 `build:mp-weixin` 与 `postbuild:mp-weixin`，同步日志显示 `dist/build scoped style hash consistent` 与 `dist/dev scoped style hash consistent`。
- 由于 MCP `open_page` / `artifact_check` 当前只接受 `/index` 结尾路由，无法直接对 `pages/actor-profile/edit` 调用内置路由核验；已改用手动三侧产物核验。生成 WXSS 在 `dist/build` 与 `dist/dev` 两侧均包含 `.profile-edit__nav.data-v-e8248cf1 { padding-bottom: 32rpx; }`、`.profile-edit__nav.data-v-e8248cf1::after { height: 1rpx; }`、`.profile-edit__nav-title.data-v-e8248cf1 { bottom: 32rpx; }`。六个产物文件 build/dev SHA-256 逐一一致：WXML `b6ca136444ad31f02eb9f2e7b00ce1540a34c42f7ea94170871287d72758007f`，WXSS `22cde617110c806dc7a6b79f553be1caec44244729ef2ff37b99ba1a8ae54a02`，JS `01066d3b36a2dd0980bed553861b0f4cfa9699d6658c58fc792d323b2e9f7285`；scopeId 均为 `data-v-e8248cf1`。
- 本轮遵守桌面非干扰规则：未使用桌面级截图、坐标、鼠标或键盘控制；MCP 自动化结束后已关闭固定 `dist/dev/mp-weixin` 项目窗口，`wechat_devtools_status` 显示 DevTools 进程为空。

## 二十四、演员档案粘贴导入入口卡片化（2026-08-19）

- 按用户截图反馈，`pages/actor-profile/edit` 中「从复制内容智能填写」入口缺少卡片元素，视觉上贴在白底上成为普通文字行；本轮将该入口定位为导入 / 粘贴入口卡片，只调整其直接 wrapper，不改 `openImportReview`、导入复核流程、核心资料表单、保存逻辑、后端接口或数据库。
- 源码新增 `.profile-edit__import-card` 到首个 `.profile-edit__cell-group`，使用 `$kp-color-border`、`$kp-radius-card`、`$kp-shadow-card` 建立白卡边界；卡内 `.profile-edit__cell` 调整为 `min-height: 112rpx`、`padding: 24rpx 28rpx`，并隐藏单行卡片内部末尾分割线，避免白卡底部出现多余细线。
- `docs/ui-style-guide-v3.md` 已补充演员档案导入 / 粘贴入口卡片合同：顶部「从复制内容智能填写」必须以独立白卡呈现，点击仍进入导入复核流程。
- `type-check` 通过，`verify:nav-title` 通过 `101/101`；首次 `wechat_devtools_build` 因 DevTools 正在运行被 `sync-mp-weixin.ps1` 安全门禁拒绝，已按桌面非干扰规则使用 MCP 关闭 / quit 固定 `dist/dev/mp-weixin` 项目窗口后重跑成功，构建日志显示已清理 WeappCache、`dist/build scoped style hash consistent` 与 `dist/dev scoped style hash consistent`。
- 手动三侧产物核验通过：生成 WXML 在 `dist/build` 与 `dist/dev` 两侧均包含 `profile-edit__cell-group profile-edit__import-card`；生成 WXSS 两侧均包含 `.profile-edit__import-card.data-v-d6bed0db { border: 1rpx solid #e8e8e8; border-radius: 16rpx; box-shadow: 0 8rpx 24rpx rgba(23, 26, 33, 0.06); }`、`.profile-edit__import-card .profile-edit__cell.data-v-d6bed0db { min-height: 112rpx; padding: 24rpx 28rpx; }`。六个产物文件 build/dev SHA-256 逐一一致：WXML `70987bd89711502c2dfb14a19b6adc938d1e2f1c5266ecbaea03f513dc5ed7be`，WXSS `17c3c96dd753429d56b17d60066d0a55e865c3d079f9fa7aea29869447a2e849`，JS `c8103a9b77c49edde99db61a58e6ef495a2957a0e9930a3fa00dbfb1fb6236be`；scopeId 均为 `data-v-d6bed0db`。
- 本轮未使用桌面级截图、坐标、鼠标或键盘控制；收口时 `wechat_devtools_status` 显示 DevTools 进程为空。

## 二十五、导入复核页卡片与按钮排版对齐（2026-08-19）

- 按用户截图反馈，`pkg-profile/import-review/index` 存在顶部分割线贴近标题行、原始内容区缺少 3.0 白卡层级、两个操作按钮文字排版受原生 button 默认样式影响的问题。本轮只调整页面局部样式，不改粘贴读取、识别提交、复核应用、返回、接口或数据库。
- 导航继续遵守 00-212 模式 B：`.import-review__nav` 从直接 `border-bottom` 改为底部 `::after` 伪元素承载分割线，并增加 `padding-bottom: $kp-spacing-lg`；`.import-review__nav-title` 同步设置 `bottom: $kp-spacing-lg`，实现分割线下移 `32rpx` 且标题 / 返回按钮位置稳定。
- `.import-review__source` 与 `.import-review__group` 按 3.0 风格补齐白卡边界：`border: 1rpx solid $kp-color-border`、`border-radius: $kp-radius-card`、`box-shadow: $kp-shadow-card`、`box-sizing: border-box`；页面内容左右边距改为 `32rpx`，连续卡片 gap 使用 `$kp-spacing-gap`。
- `.import-review__primary`、`.import-review__secondary`、`.import-review__confirm`、`.import-review__apply` 统一显式设置 `display: flex`、居中、清零原生 margin/padding、`$kp-radius-button`、`$kp-font-size-list-title` / `$kp-font-weight-medium` 与 `line-height: 1.2`；识别 / 读取按钮锁定 `height: 64rpx`，底部应用按钮锁定 `height: 88rpx`、正文字号和粗体。disabled 态改为 `$kp-color-surface-muted + $kp-color-text-tertiary + opacity: 1`，不再交给原生 button 默认灰态挤压文字。
- `docs/ui-style-guide-v3.md` 已补充 `pkg-profile/import-review/index` 合同：原始内容区必须是白卡，剪贴板读取、开始识别、冲突确认和底部应用按钮必须显式锁定高度、字号、字重、居中和 disabled 颜色。
- `type-check`、`verify:nav-title`（`101/101`）和 `verify:v3-ui-legacy-colors` 均通过；构建前检测到 DevTools 正在运行，已按桌面非干扰规则仅使用 MCP 关闭 / quit 固定 `dist/dev/mp-weixin` 项目，随后 `wechat_devtools_build(timeoutMs=300000)` 成功，日志显示已清理 WeappCache、`dist/build scoped style hash consistent` 与 `dist/dev scoped style hash consistent`。
- `wechat_devtools_artifact_check(route=pkg-profile/import-review/index)` 返回 `buildDevEquivalent=true`。生成 WXSS 在 `dist/build` 与 `dist/dev` 两侧均包含 `.import-review__nav.data-v-0079fad9 { padding-bottom: 32rpx; }`、`.import-review__nav.data-v-0079fad9::after`、`.import-review__nav-title.data-v-0079fad9 { bottom: 32rpx; }`、`.import-review__source.data-v-0079fad9, .import-review__group.data-v-0079fad9` 的 `border-radius: 16rpx` / 轻阴影，以及按钮 `height: 64rpx`、`font-size: 26rpx`、`line-height: 1.2` 和 disabled `#f6f7f9 / #8e8e93 / opacity: 1`。六个产物文件 build/dev SHA-256 逐一一致：WXML `d54080f8dae61c23c8f4797eeeb176475ee83734ef874f6e115778cfd67416e2`，WXSS `da20b7648fe6d573b9fc69bbacfb8213fc3746175c7e8cb7cc801bbc9bdd0ecf`，JS `e852308b86dbd1714179fe9dc822370006a4217747277845863a961abf921116`；scopeId 均为 `data-v-0079fad9`。
- 本轮未使用桌面级截图、坐标、鼠标或键盘控制；收口时仅保留产物与 MCP artifact 证据。
