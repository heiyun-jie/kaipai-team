# v2 向导流程收尾与产物一致性治理 - 技术设计

_Requirements: ALL_

## 1. 页面跳转关系

```text
create(Hub) ──goStep──▶ step-1..step-7（线性，navigateTo）
step-settings ──handleNext──▶ generate（navigateTo，00-216 3.1）
create(Hub) ──handleNext(requiredAllDone)──▶ generate（既有）
card-list ──preview=1──▶ generate（既有）
generate ──goBack──▶ navigateBack()（回到上一页，00-216 3.2）
```

**关键修正**：
- `step-settings.handleNext`：保存 `{ currentStep: 7, settingsJson }` 后 `uni.navigateTo('/pkg-actor-card/generate/index?cardId=' + draftStore.cardId)`，`fail` 回调提示「页面打开失败」。**禁止 `navigateBack({ delta: 10 })`**——导航栈深（首页+create+7step≈9 层）不足 10，微信端会一路退到栈底首页。
- `generate.goBack`：`uni.navigateBack()`（默认回上一页）。原 `delta: 10` 同因失效。

## 2. `KpCreateProgress` 组件设计（00-216 3.3）

**位置**：`src/pkg-actor-card/components/KpCreateProgress.vue`（分包目录硬约束，00-212 同款：放 `src/components/` 白占主包预算）。

**契约**（纯展示，props 驱动，不依赖 store）：

```ts
interface Props {
  /** 进度数字：7 个 step 页传当前步号；create 中心页传已完成步数（doneCount） */
  done: number;
  /** 向导总步数，默认 7 */
  total?: number;
}
```

**模板**：`创建进度 {{done}}/{{total}}` + 进度条，宽度 = `done/total`（clamp 到 [0,1]）。

**数字来源**：
- step 页：`<KpCreateProgress :done="N" />`（N=1..7，编译期常量，随页面固定）
- create 页：`<KpCreateProgress :done="doneCount" />`，`doneCount = draftStore.stepStatuses.filter(s => s.statusCode === 'done').length`（后端派生，与生成门禁同源）

**历史（勿重蹈）**：
- 第一版组件内联 `useActorCardDraftStore()` 算完成度 → step 页显示固定已完成数（用户反馈「固定 6/7」）
- 第二版双模式（mode=step/progress）→ 文案变成「第 N 步 / 共 7 步」，仍不符用户期望
- **定稿**：统一「创建进度 x/7」形态，x 由父页面传（step=当前步、create=完成数）。语义与形态的最终裁决见 requirements §3.3。

## 3. 跨包 require 教训（`floating-back-nav` 事件，00-216 3.5 关联）

**现象**：`KpPageNav` / `KpFloatingBackButton` / `KpCapsuleSpacer` 编译后 `require("../utils/floating-back-nav.js")`，微信端报 `module 'utils/floating-back-nav.js' is not defined`（尤其分包页面 usingComponents 主包组件时）。

**根因**：磁盘上模块文件存在、主包 require 正常，但微信运行时对「被分包引用的主包组件 → require 外部业务模块」的模块注册不稳定。

**处置**：`getFloatingBackNavStyles()` 内联进全部 4 个使用方（`KpPageNav` / `KpFloatingBackButton` / `KpCapsuleSpacer` / `pages/login`），删除 `src/utils/floating-back-nav.ts`，**全仓零 require**。

**防复发规则**：被分包页面引用的组件保持**自包含**（不 require 任何业务模块）；`verify:nav-title` 断言 `KpCreateProgress` 不含 `useActorCardDraftStore`（纯展示）。

## 4. scoped 样式哈希分叉：完整根因与防复发（00-216 3.5）

### 4.1 机制（含复发）

`dist/build` 与 `dist/dev` 各文件携带 scoped `data-v-{hash}`；wxml 节点类名与 wxss 选择器、js `__scopeId` 三者必须同哈希，任一错配则**组件整套样式静默失效**（`__row` 丢绝对定位、返回箭头/标题错位 → 用户看到「顶部样式回退」）。

**第一次（00-212 四之四）**：sync 脚本后处理把目标端修改时间推晚 → robocopy `/MIR` 按「大小+时间戳」跳过 → wxml 新哈希、wxss 旧哈希。已修：robocopy 加 `/IS /IT` + `Assert-ScopedStyleHashConsistency` 双侧断言。

**复发（2026-08-13，本 Spec）**：构建时双侧哈希断言通过（日志 consistent），但**微信开发者工具运行中把 `dist/dev` 的 `KpPageNav.wxss`/`js` 回写成旧构建哈希 `961980b7`**（工具缓存回写，`961980b7` 为历史旧构建哈希），wxml 保持新哈希 `f661c11f` → 分叉 → 顶部样式失效。`dist/build` 不受影响。

**教训**：哈希断言只能防「构建链路内的分叉」，防不了「工具运行态的外部改写」。

### 4.2 防复发操作流程（用户反馈「样式回退/没变化」时强制执行）

1. **先比对哈希，禁止直接改源码**：取截图/元素面板的 `data-v-{hash}`，与 `dist/build`、`dist/dev` 对应文件的 wxml/wxss 比对（`Assert-ScopedStyleHashConsistency` 可全树扫描）。哈希不一致 → 产物问题，不是源码问题。
2. **工具内清缓存**：微信开发者工具「工具 → 清缓存 → 清除全部缓存」（清 `compile`/`fileutils`/`session` 类缓存），再重新编译。
3. **关工具重同步**：若工具运行中锁文件导致 sync 失败或再次回写，先关闭工具（或「关闭项目」）→ 重跑 `powershell -File scripts/sync-mp-weixin.ps1`（或完整 `npm run build:mp-weixin`）→ 确认双侧哈希一致 → 再打开工具。
4. 只有确认产物一致后仍异常，才回到源码排查。

## 5. 生成页顶部（00-216 3.4）

`generate/index.vue`：`<KpPageNav title="生成演员卡" @back="goBack" />`（移除 `back-text="修改"`）。`KpPageNav` 的 `back-text` prop 保留（通用能力），但**全仓使用归零**。

## 6. 门禁与核对

- `scripts/verify-miniapp-nav-title-unification.mjs` 3.3 段：断言 `KpCreateProgress`（分包目录 / `done`/`total` 契约 / 纯展示不含 store / computed 百分比 / clamp / 「创建进度」文案）、7 个 step 页 `:done="N"`（N=1..7）、create `:done="doneCount"` + `doneCount` computed、`KpStepProgress` 已退场（97 项）。
- 构建后核对：`KpCreateProgress.js` 进 `dist/build` 与 `dist/dev`；`KpStepProgress` 全量消失；wxml 挂载 `<kp-create-progress>`；双侧 scoped 哈希一致。
