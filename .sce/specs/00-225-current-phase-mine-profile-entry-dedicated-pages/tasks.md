# 00-225 当前阶段个人中心资料入口独立承载 - 任务记录

## T1 Spec 与入口裁决

- [x] 记录用户裁决：演艺经历与自我介绍不是个人资料页锚点，必须是独立设置承载。
- [x] 更新 `pages/mine/index` 三个资料入口目标。
- [x] 移除 `pages/actor-profile/edit` 中为旧同页锚点新增的 `tab` 滚动逻辑，并把自我介绍编辑从个人资料页移出。

## T2 独立页面与接口

- [x] 新增 `pkg-profile/works/index`，接真实 `/api/actor/works` 列表、新增、编辑、删除。
- [x] 新增 `pkg-profile/intro/index`，接独立 intro 保存接口。
- [x] 前端 API 补齐 `actor-work` CRUD 与 `updateMyProfileIntro`。
- [x] 后端新增 `PUT /api/actor/profile/mine/intro`，只更新 `intro`。

## T3 验证与文档

- [x] 更新 `pages.json`、`verify:v3-mine` 和 `docs/ui-style-guide-v3.md`。
- [x] 执行 type-check、个人中心门禁、导航门禁、legacy 颜色门禁；后端执行 `mvn -q -DskipTests compile`。
- [x] 在不关闭/不杀微信开发者工具的前提下说明是否完成 build/dev 产物同步：当前 DevTools 正在运行，本轮不强制关闭、不执行会失败且可能造成 build/dev 漂移的 `npm run build:mp-weixin`。
- [x] 2026-08-19 运行态补充：用户反馈“页面跳转还是错误”后，核实 `src/pages/mine/index.vue` 已是新路由，但 `dist/dev` / `dist/build` 仍是旧 JS 且新页面产物不存在。为遵守桌面非干扰规则，未退出或强杀微信开发者工具，改用 `npm run dev:mp-weixin` 首轮编译刷新 `dist/dev/mp-weixin`，并通过 MCP 只读产物核验确认 `dist/dev` 已包含 `/pkg-profile/works/index`、`/pkg-profile/intro/index` 与两个新增页；随后刷新并打开固定 dev 项目的 `pages/mine/index`。正式 `dist/build` 仍待工具完全退出后执行 `npm run build:mp-weixin`。

## T4 演艺经历新增 / 编辑弹窗化

- [x] 用户指出 `pkg-profile/works/index` 的新增 / 编辑不应在列表页内联展开。已修正 Spec：新增 / 编辑表单必须使用页面内弹窗 / 底部抽屉，列表保持列表语义。
- [x] 将 `src/pkg-profile/works/index.vue` 的内联 `.works-page__form-card` 改为 `.works-page__modal` + `.works-page__modal-panel` + `.works-page__form-scroll`，保存按钮固定在弹窗底部，遮罩 / 取消 / 系统返回在有未保存变更时先确认。
- [x] `verify:v3-mine` 增加门禁：禁止 `v-if="formVisible" class="works-page__form-card"` 这种内联表单回退，要求新增 / 编辑使用弹窗结构。已执行 `type-check`、`verify:v3-mine`、`verify:nav-title`、`verify:v3-ui-legacy-colors`，并用 `npm run dev:mp-weixin` 首轮编译刷新 `dist/dev`；产物核验证实 `dist/dev/pkg-profile/works/index.{wxml,wxss,js}` 已包含弹窗结构。因微信开发者工具仍在运行，未执行会被同步脚本拦截的正式 `build:mp-weixin`；MCP 对新路由的 `open_page` 路由表仍有缓存，但 `dist/dev/app.json` 与页面产物均已更新。

## T5 演艺经历弹窗滚动与完整展示

- [x] 修正弹窗根节点拦截 `touchmove` 导致子级 `scroll-view` 无法滚动的问题：仅遮罩层阻止背景滚动，表单滚动区保留纵向手势。
- [x] 为底部抽屉设置稳定的 `86vh` 高度，并以 `flex: 1 1 auto` + `height: 0` 限定中部滚动区；表单末尾增加底部间距，使「经历描述」可完整滚动到固定保存栏上方。
- [x] `verify:v3-mine` 增加滚动层级、稳定高度和底部留白门禁，防止弹窗再次出现无法滚动或末项被遮挡。
- [x] 已执行 `type-check`、`verify:v3-mine`、`verify:nav-title`、`verify:v3-ui-legacy-colors`；通过一次 `dev:mp-weixin` 首轮编译刷新固定运行目录，并在不触碰 DevTools 进程的前提下直接执行 Uni 正式编译补齐 `dist/build`。MCP 产物核验确认 build/dev 的 WXML、WXSS、JS 三件套各自 scope 哈希一致，且两侧均为弹窗根节点无 `catchtouchmove`、遮罩层拦截背景触摸。MCP 的 `open_page` 仍受旧路由注册缓存影响，返回目标路由未注册，因此未启用会显示窗口的 automation 初始化，运行态手势留待固定 dev 项目内人工确认。
