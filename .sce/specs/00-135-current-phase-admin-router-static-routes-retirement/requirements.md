# 00-135 当前阶段后台 router static-routes 退场（Current Phase Admin Router Static Routes Retirement）

> 状态：已完成 | 优先级：中 | 依赖：00-110 current-phase-admin-legacy-route-and-fallback-retirement-audit、00-111 current-phase-admin-legacy-wrapper-retirement-first-pass、00-112 current-phase-admin-placeholder-view-retirement-verification
> 记录目的：在 `00-110` 审计矩阵与 `00-111 / 00-112` 已完成第一批候删对象退场后，继续核销 `kaipai-admin/src/router/static-routes.ts` 是否仍承担运行态职责，并在证据充分时执行退场。

## 1. 背景

截至 `2026-04-23`：

- `00-110` 已明确：下一步应进入**实现型删除前验证切片**，只处理经过核销后的真正候删对象
- 当前 `kaipai-admin/src/router/index.ts` 已完整内联：
  - `/login`
  - `/403`
  - `/:pathMatch(.*)*`
- 当前仓内仍保留：
  - `D:\XM\kaipai-team\kaipai-admin\src\router\static-routes.ts`

本轮实现前核查已确认：

1. `static-routes.ts` 只导出一组静态路由：
   - `/login`
   - `/403`
   - `/:pathMatch(.*)*`
2. `index.ts` 已重复承接同一组静态路由
3. 当前全仓搜索：
   - `staticRoutes`
   - `router/static-routes`
   - `static-routes.ts`
   未命中任何源码或文档 consumer
4. `tsconfig.json` 与 `vite.config.ts` 未发现约定式路由自动注册或按目录扫描 router 文件的机制

当前判断：

- `static-routes.ts` 是历史静态路由表残留
- 它比 `components/AuditConfirmDialog.vue` 更独立，适合作为本轮最小退场切片

## 2. 范围

### 2.1 本轮必须处理

- 新增独立 `00-135`
- 核销 `D:\XM\kaipai-team\kaipai-admin\src\router\static-routes.ts` 的运行时依赖
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

- 不删除 `D:\XM\kaipai-team\kaipai-admin\src\components\AuditConfirmDialog.vue`
- 不调整 `router/index.ts` 现有静态路由定义
- 不删除任何 hidden tooling route
- 不处理 fallback 权限兼容链
- 不扩大到其它未引用文件

## 3. 需求

### 3.1 删除门禁

- **R1** 本轮只核销并处理 `static-routes.ts`，不扩展到其它 router / component / view 文件。
- **R2** 删除前必须同时满足：
  - 无源码 import / 动态 import 引用
  - 无文档路径引用
  - 无约定式自动注册依赖
  - `router/index.ts` 已独立承接同等静态路由职责
- **R3** 若证据只能说明“当前没看到引用”而无法排除自动注册机制，则不得删除。

### 3.2 验证合同

- **R4** 删除前必须记录：
  - 文件职责
  - 搜索证据
  - 无自动注册机制的证据
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

- [x] 已新增独立 `00-135`，并把问题收口为 `static-routes.ts` 的单文件核销
- [x] 已记录 `src / router / tsconfig / vite / docs` 多维核查证据
- [x] `static-routes.ts` 已删除
- [x] `type-check` 与 `build` 通过
- [x] README / mapping / CURRENT_CONTEXT / execution 已回填
