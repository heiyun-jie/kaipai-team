# 00-207 任务拆解 - v2 Tab 页壳层胶囊对齐、游客态收口与小程序压缩兼容

> 未经用户授权，本 Spec 不包含 git stage、commit、push 或创建分支步骤。
> 本 Spec 属于「实现先行、事后建档」：T2-T5 的代码改动在建档前已存在于工作树，本轮通过门禁脚本与真实构建对其补齐合同。

---

## T1. 建立 Spec 与门禁脚本

**文件：**
- 新建：`.sce/specs/00-207-current-phase-miniapp-v2-tab-shell-and-mp-minify-compat/requirements.md`
- 新建：`.sce/specs/00-207-current-phase-miniapp-v2-tab-shell-and-mp-minify-compat/design.md`
- 新建：`.sce/specs/00-207-current-phase-miniapp-v2-tab-shell-and-mp-minify-compat/tasks.md`
- 新建：`.sce/specs/00-207-current-phase-miniapp-v2-tab-shell-and-mp-minify-compat/scripts/verify-miniapp-v2-tab-shell-and-mp-minify.mjs`

- [x] 写入 `00-207` 范围：三个 Tab 页标题行胶囊对齐、`mine` 游客态收口、`minify: false` 兼容、启动脚本 dev watch 去重，以及首页风格卡 `3/2` 比例。
- [x] 明确不扩范围：不改后端、不改数据库、不改路由注册、不改 TabBar 结构、不改 `00-206` 向导主链。
- [x] 编写源级 + 产物级门禁：既保护 `00-206` 的 `home-v2 / card-list-page / mine-v2` 既有壳层与动作，又断言本轮新增的对齐、游客门禁、压缩与启动脚本合同。

**Validates: Requirements 3.1-3.5, 4**

## T2. 三个 Tab 页标题行胶囊对齐

**文件：**
- 修改：`kaipai-frontend/src/pages/home/index.vue`
- 修改：`kaipai-frontend/src/pages/card-list/index.vue`
- 修改：`kaipai-frontend/src/pages/mine/index.vue`

- [x] 三页统一从 `@/utils/floating-back-nav` 引入 `getFloatingBackNavStyles()`，取 `backButtonStyle` 的 `top / height`。
- [x] 标题行改为 `position: absolute`，父级 header 补 `position: relative`，右边界统一留 `200rpx` 避让胶囊按钮。
- [x] `home` 的 `greeting` 补 `margin-top: 12rpx`、`card-list` 的 `tabs` 补 `margin-top: 16rpx`、`mine` 的 header 补 `padding-bottom: 20rpx`，补偿标题行脱离文档流后的塌陷。
- [x] 保留三页既有 `KpCapsuleSpacer`，不改状态栏占位组件本身。

**Validates: Requirements 3.1, 3.2**

## T3. mine 页游客态收口

**文件：**
- 修改：`kaipai-frontend/src/pages/mine/index.vue`

- [x] `isVisitor` 改由 `userStore.hasStoredSession` 判定，`isLoggedIn` 收敛为 `!isVisitor`，与 `00-192` 全局会话语义对齐。
- [x] 新增 `requireLoginForMineAction()` 与 `openAccountCapability(url)`，把个人资料、演艺经历、自我介绍、实名认证与 `goEditProfile` 统一收口为「先登录再进入」。
- [x] `displayName` 在已登录无昵称时回退到 `formatPhone(phone)`，再回退到 `演员用户`；游客保持 `未登录用户`。
- [x] `onShow` 在游客态直接返回，不调用 `getProfileCompleteness()`。
- [x] 帮助与关于类入口保持游客可进入，不加登录门禁。

**Validates: Requirements 3.3**

## T4. 小程序压缩兼容与首页风格卡比例

**文件：**
- 修改：`kaipai-frontend/vite.config.ts`
- 修改：`kaipai-frontend/src/pages/home/index.vue`

- [x] `build.minify` 置为 `false`，并写入原因注释：esbuild 压缩产物在微信小程序环境出现 `?.5:` 形态非法语法，导致页面 JS 解析失败与 `navigateTo` timeout / 白屏。
- [x] 首页 `&__style-img-wrap` 的 `aspect-ratio` 从 `3/4` 改为 `3/2`。
- [x] 保留 `postbuild:mp-weixin` 既有同步与 `urlCheck` 行为，不在本轮改动发布脚本语义。

**Validates: Requirements 3.4, 3.5**

## T5. 本地启动脚本 dev watch 去重

**文件：**
- 修改：`kaipai-frontend/scripts/start-miniapp.py`

- [x] 新增 `has_existing_dev_watch()`，通过只读 `Win32_Process` 查询识别本项目已存在的 `mp-weixin` uni watch，避免重复启动。
- [x] 新增 `file_signature()`，`wait_for_dev_build()` 改为接收 `proc` 与 `previous_signature`，等待本次构建真实产出或更新 `app.json`，而不是只判断文件存在。
- [x] dev watch 在首次构建完成前退出时，脚本以其退出码失败退出，不再假成功。
- [x] `open_devtools()` 形参类型修正为 `Path`。

**Validates: Requirements 3.6**

## T6. 执行验证与三层核对

- [x] `cd kaipai-frontend && npm run type-check`
- [x] `cd kaipai-frontend && npm run build:mp-weixin`（postbuild 自动同步 `dist/build` → `dist/dev`）
- [x] 三层核对 `src / dist/build / dist/dev` 的胶囊对齐与 `3/2` 比例一致
- [x] `cd kaipai-frontend && npm run audit:mp-package`
- [x] `cd kaipai-frontend && npm run audit:steering`
- [x] 运行 `00-207` 专项门禁脚本

### 验证记录

- `npm run type-check`：通过。
- `npm run build:mp-weixin`：`DONE Build complete.`，postbuild 已同步到 `dist/dev/mp-weixin`。
- 三层核对：
  - `aspect-ratio: 3/2` 在 `dist/build/mp-weixin/pages/home/index.wxss` 与 `dist/dev/mp-weixin/pages/home/index.wxss` 均命中。
  - `backButtonStyle` 在 `dist/build/mp-weixin/pages/home/index.js` 与 `dist/dev/mp-weixin/pages/home/index.js` 均命中。
- `audit:mp-package`：**FAIL**，首错即停于 `dist/build/mp-weixin/api/actor-asset.js:1` 的本地 API base `http://127.0.0.1:8010`。该阻塞与 `00-204 / 00-205` 记录的既有阻塞同源，不由本轮 `minify: false` 引入；本轮遵循范围约束未改无关 API 配置。
- 包体实测（`minify: false` 生效后）：
  - 主包（排除分包）：`588K`
  - `pkg-card`：`1.2M`
  - `pkg-profile`：`248K`
  - `pkg-tools`：`120K`
  - 产物总计：`2.1M`
  - 结论：单包均显著低于微信 `2MB` 单包上限，关闭压缩当前未触发包体门禁。主包最大单文件为 `common/vendor.js` `120K`。

**Validates: Requirements 4**

## T7. 取代关系落账（方案 A 最小范围）

**文件：**
- 修改：`.sce/specs/README.md`
- 修改：`.sce/specs/spec-code-mapping.md`
- 修改：`.sce/steering/CURRENT_CONTEXT.md`

- [ ] 记录 `00-201` / `00-205` 的首页合同已由 `00-206` T7 首页改版物理取代：当前 `pages/home/index.vue` 为 `home-v2`，`480rpx` 阴阳鱼舞台、Hero 文案「为每一次相遇 / 留下光影」与 `/static/home/yin-yang-creation.png` 双透明入口在源码中均为 `0` 命中。
- [ ] 将 `verify-miniapp-home-portfolio-waterfall.mjs` 标注为历史脚本，不再作为当前门禁执行；其当前结果为 `13 PASS / 6 FAIL`，6 个 FAIL 全部属于已被取代的 `00-201` 保护合同，不是回归缺陷。
- [ ] 把 `CURRENT_CONTEXT.md` 从 V7.7（停在 `00-199 / 00-200`）刷新到 `00-206 / 00-207` 基线，并记录当前分支为 `V3.0`。

**Validates: Requirements 5**
