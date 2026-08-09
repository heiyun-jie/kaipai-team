# 00-207 当前阶段小程序 v2 Tab 壳层胶囊对齐与 mp-weixin 压缩兼容

> 状态：实现先行、Spec 后补。本 Spec 用于把已存在于工作树的 5 个文件改动收口为书面合同，并补齐验证门禁。
> 范围锚点：`00-206` 已交付 v2 首页 / 名片夹 / 个人中心与底部导航；本 Spec 只处理这三页的**壳层顶部对齐**、个人中心**游客态边界**、以及 **mp-weixin 产物可解析性**。

## 1. 概述

`00-206` 交付 v2 三个 Tab 页后，工作树中出现了一批尚未建档的改动。这些改动解决三类互相独立的问题：

1. **壳层顶部对齐**：`pages/home/index`、`pages/card-list/index`、`pages/mine/index` 的标题行原先是普通流式 `padding` 块，位于 `KpCapsuleSpacer` 之后，导致标题基线与微信右上角胶囊按钮不在同一水平带上。
2. **个人中心游客态**：`pages/mine/index` 原先用 `userStore.isLoggedIn` 判定身份，且账号类入口直接 `navigateTo`，未登录用户点击后进入需要登录态的页面。
3. **mp-weixin 产物解析失败**：默认 esbuild 压缩产物在微信小程序运行时出现非法语法（记录为 `?.5:` 形态），导致页面 JS 解析失败，表现为 `navigateTo` timeout / 白屏。

本 Spec 不改变 `00-206` 的向导链路、后端合同、路由注册、底部导航结构或名片夹数据来源。

## 2. 用户故事

作为演员用户，我希望三个 Tab 页的页面标题与右上角胶囊按钮在同一水平带上，页面顶部不出现标题偏上或偏下的错位感。

作为未登录访客，我希望在个人中心能看到完整的功能清单，点击账号相关入口时被引导去登录，而不是直接进入一个读不到数据的页面。

作为开发者，我希望构建产物在微信开发者工具中能正常解析并完成页面跳转，而不是在 `navigateTo` 时超时白屏。

作为开发者，我希望一键启动脚本不会重复拉起同一个 dev watch，并且「等待构建完成」判定的是本次构建真实产出，而不是上一次遗留的文件。

## 3. 功能需求

### 3.1 三个 Tab 页标题行胶囊对齐

**描述**：`pages/home/index`、`pages/card-list/index`、`pages/mine/index` 的标题行统一改为相对页面 header 绝对定位，纵向位置与高度由 `getFloatingBackNavStyles().backButtonStyle` 提供。

**验收标准**：
- WHEN 渲染上述三页 THEN 标题行容器必须绑定 `:style="{ top: backButtonStyle.top, height: backButtonStyle.height }"`，且样式为 `position: absolute` 并设置 `display: flex; align-items: center`。
- WHEN 标题行改为绝对定位 THEN 其父级 header 必须显式声明 `position: relative`，避免定位上下文逃逸到页面根节点。
- WHEN 标题行脱离文档流 THEN 原先由标题行 `padding` 撑开的间距必须由紧随其后的可见元素补回：`home` 由 `__greeting` 的 `margin-top` 承担，`card-list` 由 `__tabs` 的 `margin-top` 承担，`mine` 由 `__header` 的 `padding-bottom` 承担。
- 标题行右边界必须留出胶囊按钮避让宽度（`right: 200rpx`），左边界与页面内容保持 `32rpx` 对齐。
- 三页的标题文案（`开拍了演员卡` / `名片夹` / `个人`）、`KpCapsuleSpacer` 的存在与位置不得改变。

### 3.2 个人中心游客态身份边界

**描述**：`pages/mine/index` 的身份判定改用 `userStore.hasStoredSession`，账号类入口统一经过登录门禁。

**验收标准**：
- WHEN 判定当前是否游客 THEN 必须以 `!userStore.hasStoredSession` 为唯一依据；`isLoggedIn` 只能作为 `!isVisitor` 的派生值，不得再直接消费 `userStore.isLoggedIn`。
- WHEN 游客点击「个人资料」「演艺经历」「自我介绍」「实名认证」或用户卡上的编辑资料 THEN 必须跳转 `/pages/login/index`，不得进入目标页。
- WHEN 已登录用户点击上述入口 THEN 必须进入其原有目标路由，query 参数（`?tab=experience` / `?tab=intro`）保持不变。
- WHEN 计算展示名 THEN 游客固定显示 `未登录用户`；已登录用户按 `nickname` → `formatPhone(phone)` → `演员用户` 顺序回退。
- WHEN `onShow` 触发且当前为游客 THEN 不得调用 `getProfileCompleteness()`。
- 「帮助」等不需要登录态的入口不得被登录门禁拦截。

### 3.3 首页风格卡比例

**描述**：首页模板创建区风格卡封面比例由 `3/4` 改为 `3/2`。

**验收标准**：
- WHEN 渲染首页风格网格 THEN `__style-img-wrap` 的 `aspect-ratio` 必须为 `3/2`。
- 2×2 网格结构、4 个风格 Tab、风格标签文案与点击行为不得改变。

### 3.4 mp-weixin 构建产物压缩兼容

**描述**：`vite.config.ts` 显式关闭构建压缩，保证产物为标准 JS。

**验收标准**：
- WHEN 执行任意 `build:mp-weixin` THEN `vite.config.ts` 必须显式设置 `build.minify: false`，并在同处保留说明该配置存在原因的注释。
- WHEN 该配置生效 THEN 构建产物不得再出现导致微信小程序解析失败的压缩语法，页面 `navigateTo` 不得因 JS 解析失败而 timeout。
- WHEN 关闭压缩 THEN 必须实测主包体积并记录，确认仍在微信单包 `2 MB` 约束内；若超限，本配置不得直接进入发布链路。

### 3.5 一键启动脚本可重入性

**描述**：`scripts/start-miniapp.py` 增加 dev watch 去重与真实构建完成判定。

**验收标准**：
- WHEN 本项目已存在 `mp-weixin` dev watch 进程 THEN 脚本不得重复拉起第二个 watch。
- WHEN 检测已有进程 THEN 只能使用只读进程查询（Win32_Process），不得终止、修改或注入任何既有进程。
- WHEN 等待首次构建 THEN 必须以 `dist/dev/mp-weixin/app.json` 的「修改时间 + 大小」签名相对本次启动前发生变化为准，不得仅判断文件是否存在。
- WHEN dev watch 在首次构建完成前退出 THEN 脚本必须以该进程退出码失败退出，不得继续调用开发者工具 CLI。

## 4. 非功能需求

- 本轮不新增业务能力、页面、路由、API 或数据库改动。
- 不得引入 mock 数据、假占位内容或与当前账号无关的数据。
- 三页壳层改动必须是局部密度 / 定位调整，不得外溢为全局样式重构。
- 继续遵循 `SHARED_CONVENTIONS.md`，以及 `00-187` / `00-192` / `00-205` 已建立的会话与访客边界。
- 静态门禁不得采用整文件快照，必须检查可理解的模板、样式、身份与配置合同。

## 5. 约束条件

- `minify: false` 的代价是产物体积上升。它必须与 `audit:mp-package` 的实测结果一起被记录；只要主包逼近 `2 MB`，就要转为「分包 / 按平台条件关闭压缩」的后续独立 Spec，而不是在本 Spec 内扩大改动。
- 微信官方拒审相关合同（`00-187` 登录门禁、`00-188` 复审合规）不得因本轮壳层改动回退。
- 改动 `src` 后必须重新执行 `npm run build:mp-weixin`，并核对 `src / dist/build / dist/dev` 三层一致。

## 6. 验收清单

- [ ] 三个 Tab 页标题行均为绝对定位 + `backButtonStyle` 绑定，父级 header 为 `position: relative`。
- [ ] 三页均补回了标题行脱流后的间距，视觉上标题与胶囊同水平带。
- [ ] `mine` 游客态以 `hasStoredSession` 判定，5 个账号类入口全部经过登录门禁。
- [ ] `mine` 游客态不调用 `getProfileCompleteness()`。
- [ ] 首页风格卡 `aspect-ratio` 为 `3/2`，网格与入口行为未变。
- [ ] `vite.config.ts` 显式 `build.minify: false` 且带原因注释。
- [ ] `start-miniapp.py` 具备 dev watch 去重、签名比对与 watch 早退失败传播。
- [ ] `npm run type-check` 与 `npm run build:mp-weixin` 通过。
- [ ] `src / dist/build / dist/dev` 三层已核对一致。
- [ ] 主包体积已实测并记录，明确是否仍在 `2 MB` 内。
- [ ] `verify-miniapp-v2-tab-shell-and-minify.mjs` 全项通过。
