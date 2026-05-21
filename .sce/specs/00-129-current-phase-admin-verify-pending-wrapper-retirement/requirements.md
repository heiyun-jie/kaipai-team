# 00-129 当前阶段后台 verify 待审核 wrapper 退场（Current Phase Admin Verify Pending Wrapper Retirement）

> 状态：已完成 | 优先级：中 | 依赖：00-110 current-phase-admin-legacy-route-and-fallback-retirement-audit、00-111 current-phase-admin-legacy-wrapper-retirement-first-pass
> 记录目的：在 `00-110` 旧代码退场审计线下，继续处理当前最小的仍在路由里但只承担薄包装作用的对象 `PendingView.vue`。

## 1. 背景

截至 `2026-04-23`：

- `00-111` 已删除第一批无运行引用的历史 wrapper：
  - `DashboardView.vue`
  - `ReferralRiskView.vue`
- 当前 `D:\XM\kaipai-team\kaipai-admin\src\views\verify\PendingView.vue` 仅有 8 行
- 当前文件只做一件事：
  - `VerificationBoard mode="pending"`
- 当前 `/verify/pending` 路由仍指向：
  - `PendingView.vue`

本轮进一步核实：

- `VerificationBoard.vue` 已通过 `defineProps<{ mode: 'pending' | 'history' }>()` 接收模式
- router 可以直接改为：
  - `VerificationBoard.vue + props { mode: 'pending' }`
- 当前源码内对 `PendingView` 的引用只剩：
  - 文件自身
  - router 动态 import

当前判断：

- `PendingView.vue` 当前属于典型薄包装 wrapper
- 与继续扩大到 verify 其它页面相比，这一刀更小、更低风险、更符合 `00-110` 审计线的最小退场原则

## 2. 范围

### 2.1 本轮必须处理

- 新增独立 `00-129`
- 将 `/verify/pending` 路由改为直接加载 `VerificationBoard.vue`
- 通过 router `props` 传入：
  - `mode = 'pending'`
- 删除：
  - `D:\XM\kaipai-team\kaipai-admin\src\views\verify\PendingView.vue`
- 通过前端 `type-check` / `build`
- 真实浏览器复核 `/verify/pending`

### 2.2 本轮不处理

- 不修改 `VerificationBoard.vue` 的业务逻辑
- 不扩展到 `verify/history` 或其它 verify 页面拆分
- 不修改后端 verify 接口
- 不扩展到其它 hidden tooling 页

## 3. 需求

### 3.1 退场边界

- **R1** 本轮只处理 `PendingView.vue` 这一个薄包装对象，不扩大到 verify 域其它文件。
- **R2** 只有在确认 `PendingView.vue` 仅承担 `VerificationBoard mode='pending'` 包装职责时，才允许删除。
- **R3** 删除后 `/verify/pending` 的访问行为、权限判断和页面呈现必须保持一致。

### 3.2 路由合同

- **R4** `/verify/pending` 必须继续由 router 直接承接，不允许因为删除 wrapper 而丢失 `page.verify.pending` 页面权限门禁。
- **R5** `VerificationBoard.vue` 必须继续以 `mode='pending'` 运行，不允许误切到 `history` 语义。

### 3.3 验证要求

- **R6** 必须通过：
  - `kaipai-admin` 的 `npm run type-check`
  - `kaipai-admin` 的 `npm run build`
- **R7** 必须基于真实浏览器复核：
  - `http://127.0.0.1:5100/verify/pending`
- **R8** 浏览器截图必须落到：
  - `D:\XM\kaipai-team\output\playwright\00-129\`

## 4. 验收标准

- [x] 已新增独立 `00-129`
- [x] `/verify/pending` 已直接路由到 `VerificationBoard.vue + props`
- [x] `PendingView.vue` 已删除
- [x] 前端 `type-check` / `build` 已通过
- [x] 真实浏览器已复核 `/verify/pending`
- [x] README / mapping / CURRENT_CONTEXT / execution 已回填
