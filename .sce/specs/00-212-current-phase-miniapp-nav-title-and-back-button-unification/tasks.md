# 00-212 当前阶段小程序导航标题与返回按钮统一收口 - 执行步骤

> 执行原则：一次只做一个任务，做完停下等用户审核。
> 每个任务开工前读 `requirements.md` + `design.md` + `SHARED_CONVENTIONS.md`。

**状态：T1 ~ T8 全部完成（2026-08-10）**。`vue-tsc` `0` 报错、`build:mp-weixin` `EXIT=0`、`verify:nav-title` `69/69`（经反向注入验证非空转）、`dist/build` 与 `dist/dev` 双层产物已核对、主包 `423.0 KB / 2048 KB`。**未提交**，等用户审核。

## T1 新增 `KpPageNav` 组件

新建 `src/components/KpPageNav.vue`，按 `design.md §4.1` 模板结构与 `§8` 样式实现。内部调用 `getFloatingBackNavStyles()`（setup 期同步取值，不得提到模块顶层），自持占位块与胶囊带定位，`position: relative` 收在组件外层。接口为 `title` / `showBack` / `back` 事件 / 默认插槽，只 `emit('back')`，不自行 `navigateBack`。

**Validates: Requirements 3.4**

## T2 `pkg-actor-card` 8 页导航行改造

`create` / `step-profile` / `step-works` / `step-photos` / `step-video` / `step-attachment` / `step-settings` / `generate` 换用 `KpPageNav`，删除各页 `__nav` / `__back` / `__title` 手写结构与样式，按 `design.md §5.3` 补回下内边距。`generate` 为特例（返回文案 `‹ 修改` + 标题原居中），单独确认视觉未回归。

**Validates: Requirements 3.1, 3.4**

## T3 `step-visual` 导航改造 + 进度条移出

换用 `KpPageNav`，`__prog-bar` 移出导航行、独立为 `__prog-row`（胶囊带下方、正文之上，左右与内容对齐），删除 `__title { flex: 1 }`。进度值 `14.3%` 与进度条视觉不得变。

**Validates: Requirements 3.1, 3.3, 3.4**

## T4 消除 5 页标题重复

删除 `step-visual` / `step-profile` / `step-video` / `step-settings` / `step-attachment` 的正文 `__h1` 节点及 `&__h1` 样式，补回其原承担的顶部间距，`__sub` 不得贴顶。**`step-works` / `step-photos` 的 `__h1` 保留**（措辞不同）。

**Validates: Requirements 3.2**

## T5 模式 A 三页归一

`home` / `card-list` / `mine` 从 `00-207` 的手写绝对定位标题行换用 `KpPageNav`，标题文案与 `KpCapsuleSpacer` 语义不变。完成后全仓页面层不应再出现「`KpCapsuleSpacer` + 手写绝对定位标题行」组合。

**Validates: Requirements 3.4**

## T6 回归门禁脚本

新建 `scripts/verify-miniapp-nav-title-unification.mjs`，断言：12 页均用 `KpPageNav`、9 页无流式 `__nav`、5 页重复 `__h1` 已消除且 2 页保留、`step-visual` 进度条已移出导航、页面层无残留 `right: 200rpx` 魔数。**必须收集全部失败项后再非零退出**（不得首错即停，见 `00-211`），并接入 `package.json`（未接入不计门禁，见 `00-205`）。

**Validates: Requirements 3.5**

## T7 构建与产物核验

`vue-tsc --noEmit` 须 `0` 报错；`npm run build:mp-weixin` 须 `EXIT=0`；grep 核对 `KpPageNav` 已进入 `dist/build` 与 `dist/dev` 双层产物，且被删标题文案在产物中的出现次数符合预期；实测主包体积并记录（限 `2 MB`）。

**Validates: Requirements 4, 5**

## T8 文档同步

按 `design.md §10` 同步 `SHARED_CONVENTIONS.md`（第 22 行失效 `KpNavBar` 引用、第 85-93 行「不依赖共享导航组件」需限定为仅深色 Hero 页）、`.sce/specs/README.md`、`spec-code-mapping.md`、`CURRENT_CONTEXT.md`。

**Validates: Requirements 5**
