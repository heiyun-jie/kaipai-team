# v2 向导流程收尾与产物一致性治理 - 任务清单

_Requirements: ALL_
_Design: ALL_

> 2026-08-13 完成并构建核验。门禁：`vue-tsc` 0 报错、`build:mp-weixin` EXIT=0、`verify:nav-title` 97/97、`verify:actor-card-attachment` 17/17，`dist/build` ↔ `dist/dev` 双侧 scoped 哈希一致。

## T1 「完成设置」直接进入生成页（Requirements 3.1）

**改动**：`src/pkg-actor-card/step-settings/index.vue` `handleNext`

- 保存 `{ currentStep: 7, settingsJson }` 后 `uni.navigateTo({ url: '/pkg-actor-card/generate/index?cardId=' + draftStore.cardId, fail: 提示 })`。
- 删除 `uni.navigateBack({ delta: 10 })`（超出栈深 → 退到首页，即用户报「完成设置回首页」根因）。
- `cardId` 为空时提示「草稿未就绪」并阻断。

**Validates: Requirements 3.1**

## T2 生成页返回回到上一页（Requirements 3.2）

**改动**：`src/pkg-actor-card/generate/index.vue` `goBack`

- `uni.navigateBack({ delta: 10 })` → `uni.navigateBack()`（回到上一页：设置页 / create Hub / 名片夹）。

**Validates: Requirements 3.2**

## T3 顶部进度条统一「创建进度 x/7」（Requirements 3.3）

**改动**：

- 新建 `src/pkg-actor-card/components/KpCreateProgress.vue`：纯展示（props `done`/`total`，默认 total=7），`创建进度 {{done}}/{{total}}` + 进度条（`done/total` clamp）。**不依赖 store**。
- 7 个 step 页：`<KpCreateProgress :done="N" />`（N=1..7）。
- create 页：`<KpCreateProgress :done="doneCount" />`，加回 `doneCount` computed（后端派生 `stepStatuses` 的 done 计数）。
- 删除 `KpStepProgress.vue`（「第 N 步 / 共 7 步」文案退场）。
- 同步 `verify-miniapp-nav-title-unification.mjs` 3.3 段断言。

**多轮澄清记录（勿重蹈）**：①组件内联 store 算完成度 → step 页显示固定已完成数（用户否）；②双模式「第 N 步 / 共 7 步」（用户否）；③定稿：统一「创建进度 x/7」，step 页 x=当前步、create 页 x=完成数（用户认可）。

**Validates: Requirements 3.3**

## T4 生成页返回文案删除（Requirements 3.4）

**改动**：`generate/index.vue` 移除 `back-text="修改"`，顶部仅返回箭头 + 标题。

**Validates: Requirements 3.4**

## T5 产物一致性治理与防复发（Requirements 3.5）

**问题登记**：

- **复发**：构建时双侧哈希一致，但微信开发者工具运行态把 `dist/dev` 的 `KpPageNav.wxss/js` 回写成旧哈希 `961980b7`（wxml 保持 `f661c11f`）→ 顶部样式静默失效（「样式被回退」）。`dist/build` 不受影响。
- **处置**：重跑 `sync-mp-weixin.ps1` 强制覆盖（/IS /IT）→ 双侧一致（KpPageNav 三件套 `f661c11f`，全树分叉 0）。
- **防复发**：见 design §4.2 —— 先比对 `data-v` 哈希再动源码；工具内清缓存；关工具后重同步。

**Validates: Requirements 3.5**

## T6 跨包 require 治理（Requirements 4 非功能）

**问题登记**：`KpPageNav`/`KpFloatingBackButton`/`KpCapsuleSpacer`/`login` require `@/utils/floating-back-nav`，微信端报 `module not defined`（分包引用主包组件时不稳定）。

**处置**：`getFloatingBackNavStyles()` 内联进 4 个使用方，删除 `src/utils/floating-back-nav.ts`，全仓零 require；`verify:nav-title` 断言 `KpCreateProgress` 纯展示（不含 store）。

**Validates: Requirements 4, 5**

## T7 文档与知识库回填

- `.sce/specs/README.md` 注册 00-216。
- `CURRENT_CONTEXT.md`：登记 00-216、哈希分叉复发与防复发流程、「先读 Spec/知识库再动手」硬约束。
- `.sce/knowledge/errorbook/project-shared-registry.json` 新增条目：
  - `kppagenav-scoped-hash-fork-devtools-rewrite-20260813`（哈希分叉复发：工具运行态回写）
  - `floating-back-nav-cross-package-require-20260813`（分包组件跨包 require 失败）
- `00-212` tasks.md / CURRENT_CONTEXT 四之三：进度条语义定稿回填（已做）。

**Validates: Requirements 8（文档验收）**
