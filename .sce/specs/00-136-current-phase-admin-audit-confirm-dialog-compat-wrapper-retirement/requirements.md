# 00-136 当前阶段后台 AuditConfirmDialog 兼容 wrapper 退场（Current Phase Admin Audit Confirm Dialog Compat Wrapper Retirement）

> 状态：已完成 | 优先级：中 | 依赖：00-110 current-phase-admin-legacy-route-and-fallback-retirement-audit、00-135 current-phase-admin-router-static-routes-retirement
> 记录目的：在 `00-135` 已完成 `static-routes.ts` 单文件退场后，继续核销 `kaipai-admin/src/components/AuditConfirmDialog.vue` 是否仍承担运行态职责，并在证据充分时执行退场。

## 1. 背景

截至 `2026-04-23`：

- 当前后台各业务页已经统一从：
  - `D:\XM\kaipai-team\kaipai-admin\src\components\dialogs\AuditConfirmDialog.vue`
  消费确认弹窗
- 当前仓内仍保留：
  - `D:\XM\kaipai-team\kaipai-admin\src\components\AuditConfirmDialog.vue`

本轮实现前核查已确认：

1. `src/components/AuditConfirmDialog.vue` 当前只做一层兼容转发：
   - import canonical dialog
   - 透传 props / emits
2. 当前 `kaipai-admin/src` 内所有运行时 consumer 都直连：
   - `@/components/dialogs/AuditConfirmDialog.vue`
3. 当前未发现任何源码 consumer 继续引用：
   - `@/components/AuditConfirmDialog.vue`
   - `components/AuditConfirmDialog.vue`
4. `.sce` 中对 `AuditConfirmDialog.vue` 的提及主要是历史追溯：
   - 旧兼容层改造历史
   - 弹窗样式对齐历史
   - 本轮候删说明

当前判断：

- 顶层 `src/components/AuditConfirmDialog.vue` 更像历史兼容 wrapper
- 在无源码 consumer 的前提下，适合作为本轮最小单文件退场对象

## 2. 范围

### 2.1 本轮必须处理

- 新增独立 `00-136`
- 核销 `D:\XM\kaipai-team\kaipai-admin\src\components\AuditConfirmDialog.vue` 的运行时依赖
- 若确认无依赖，则删除该文件
- 删除后通过：
  - `npm run type-check`
  - `npm run build`
- 回填：
  - `.sce/specs/README.md`
  - `.sce/specs/spec-code-mapping.md`
  - `.sce/steering/CURRENT_CONTEXT.md`
  - `execution.md`

### 2.2 本轮不处理

- 不修改 `D:\XM\kaipai-team\kaipai-admin\src\components\dialogs\AuditConfirmDialog.vue`
- 不调整任何业务页对 canonical dialog 的引用
- 不扩到其它 component wrapper
- 不处理 hidden tooling 路由
- 不处理 fallback 权限兼容链

## 3. 需求

### 3.1 删除门禁

- **R1** 本轮只核销并处理 `src/components/AuditConfirmDialog.vue`，不扩展到 `dialogs/AuditConfirmDialog.vue` 或其它组件。
- **R2** 删除前必须同时满足：
  - 无源码 import / 动态 import consumer
  - 当前文件本身只承担兼容转发职责
  - 文档引用仅属于历史追溯，不构成运行时保留理由
- **R3** 若仍存在任一运行时 consumer 指向顶层 wrapper，则本轮不得删除。

### 3.2 验证合同

- **R4** 删除前必须记录：
  - wrapper 文件职责
  - 源码搜索证据
  - 文档追溯与运行时依赖的区分
- **R5** 删除后必须通过：
  - `npm run type-check`
  - `npm run build`
- **R6** 若删除后出现类型或构建失败，本轮必须回退删除结论，不得扩大清理范围。

### 3.3 回填要求

- **R7** 本轮必须回填 `README.md`、`spec-code-mapping.md`、`CURRENT_CONTEXT.md`。
- **R8** `execution.md` 必须记录：
  - 删除前核查范围
  - 删除前关键证据
  - 删除动作
  - 删除后验证结果

## 4. 验收标准

- [x] 已新增独立 `00-136`，并把问题收口为 `AuditConfirmDialog.vue` 的单文件核销
- [x] 已记录 `src / .sce` 双侧证据，并明确区分运行时依赖与历史追溯引用
- [x] `src/components/AuditConfirmDialog.vue` 已删除
- [x] `type-check` 与 `build` 通过
- [x] README / mapping / CURRENT_CONTEXT / execution 已回填
