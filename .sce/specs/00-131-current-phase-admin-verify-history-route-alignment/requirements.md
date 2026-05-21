# 00-131 当前阶段后台 verify 历史路由对齐（Current Phase Admin Verify History Route Alignment）

> 状态：已完成 | 优先级：中 | 依赖：00-129 current-phase-admin-verify-pending-wrapper-retirement、00-110 current-phase-admin-legacy-route-and-fallback-retirement-audit
> 记录目的：在 `00-129` 已把 `/verify/pending` 直接接到 `VerificationBoard.vue` 后，继续补齐当前已经存在权限合同、后端合同和前端组件能力，但 router 缺失的 `/verify/history` hidden tooling 路由。

## 1. 背景

截至 `2026-04-23`：

- `00-129` 已完成：
  - `/verify/pending` 直接承接 `VerificationBoard.vue + props`
  - `PendingView.vue` 已删除
- 当前前端 `VerificationBoard.vue` 已支持：
  - `mode: 'pending' | 'history'`
- 当前前端 permission registry 已登记：
  - `page.verify.history`
- 当前后端 `AdminVerifyController.java` 的列表接口已允许：
  - `page.verify.pending`
  - `page.verify.history`
- 当前 dev 登录态角色数据也已携带：
  - `page.verify.history`

本轮核实到的问题：

- 当前 router 只有：
  - `/verify/pending`
- 当前 router 缺少：
  - `/verify/history`

当前判断：

- 这不是新增业务能力，而是把已经存在的后端权限合同、前端组件 mode 和角色数据补齐成可访问 hidden tooling 路由
- 当前最小改法是直接新增 `/verify/history` route record，并传入 `mode='history'`

## 2. 范围

### 2.1 本轮必须处理

- 新增独立 `00-131`
- 新增 `/verify/history` 路由
- 路由直接承接：
  - `VerificationBoard.vue`
- 通过 router `props` 传入：
  - `mode = 'history'`
- route meta 使用：
  - `title = '实名认证历史'`
  - `pagePermission = 'page.verify.history'`
  - `architectureLayer = 'tooling'`
  - `architectureArea = 'tooling'`
- 通过前端 `type-check` / `build`
- 真实浏览器复核 `/verify/history`

### 2.2 本轮不处理

- 不修改 `VerificationBoard.vue` 业务逻辑
- 不修改 `/verify/pending`
- 不修改 verify 后端接口
- 不修改角色数据或权限 registry
- 不扩展到其它缺路由的权限项

## 3. 需求

### 3.1 路由合同

- **R1** `/verify/history` 必须使用现有 `VerificationBoard.vue`，不得新增重复页面组件。
- **R2** `/verify/history` 必须通过 `props` 固定传入 `mode='history'`。
- **R3** `/verify/history` 必须继续作为 hidden tooling，不得进入正式 8 页侧栏。

### 3.2 权限合同

- **R4** `/verify/history` 必须使用已有权限 `page.verify.history`。
- **R5** 本轮不得改变 `/verify/pending` 的 `page.verify.pending` 门禁。
- **R6** 本轮不得新增新的权限码。

### 3.3 验证要求

- **R7** 必须通过：
  - `kaipai-admin` 的 `npm run type-check`
  - `kaipai-admin` 的 `npm run build`
- **R8** 必须基于真实浏览器复核：
  - `http://127.0.0.1:5100/verify/history`
- **R9** 截图产物必须落到：
  - `D:\XM\kaipai-team\output\playwright\00-131\`

## 4. 验收标准

- [x] 已新增独立 `00-131`
- [x] `/verify/history` 已接入 router
- [x] `/verify/history` 已使用 `VerificationBoard.vue + mode='history'`
- [x] `/verify/history` 已使用 `page.verify.history` 门禁
- [x] 前端 `type-check` / `build` 已通过
- [x] 真实浏览器已复核 `/verify/history`
- [x] README / mapping / CURRENT_CONTEXT / execution 已回填
