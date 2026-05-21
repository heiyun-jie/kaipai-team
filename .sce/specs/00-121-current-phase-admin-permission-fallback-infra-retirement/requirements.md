# 00-121 当前阶段后台权限 fallback 基础设施退场（Current Phase Admin Permission Fallback Infrastructure Retirement）

> 状态：已完成 | 优先级：中 | 依赖：00-110 current-phase-admin-legacy-route-and-fallback-retirement-audit、00-114 current-phase-admin-recruit-fallback-code-retirement-first-pass、00-115 current-phase-admin-recruit-matrix-schema-cleanup、00-116 current-phase-admin-ai-matrix-schema-cleanup、00-120 current-phase-admin-operation-logs-runtime-refresh-and-browser-revalidation
> 记录目的：在招募 runtime fallback 已退场、AI / 招募矩阵 schema 已清理、`8010` 运行态已验证吃到最新代码后，继续把前端权限内核中无人消费的 fallback 基础设施做成最小退场切片，并同步清理仍误报“仍保留 fallback 兼容链路”的架构文案。

## 1. 背景

截至 `2026-04-23`：

- `00-114` 已完成招募 runtime fallback 代码退场
- `00-115 / 00-116` 已完成招募 / AI 矩阵 schema 清理
- `00-120` 已确认本机 `8010 / 5100` 运行态已经吃到最新代码

但当前前端代码仍保留一层旧的 fallback 权限基础设施：

- `src/utils/permission.ts` 仍定义 `PermissionAccessMode = 'open' | 'direct' | 'fallback' | 'denied'`
- `src/stores/permission.ts` 仍保留 `resolveFallbackPermissions(...)` 与 `getAccessMode(...)`
- `router/index.ts`、`types/admin.ts`、`types/router.d.ts` 仍承接 `pagePermissionFallbacks`
- `PermissionButton.vue` 仍保留 `fallbackPermissions` 透传口
- `admin-information-architecture.ts` 对 `/recruit/*` 的说明仍写着“仍保留 admin-users fallback 兼容链路”

当前初步核查结果：

- 现有前端运行时代码内，已找不到实际 `pagePermissionFallbacks` 配置
- 现有组件调用中，已找不到实际传入 `fallbackPermissions` 的按钮使用点

当前判断：

- 当前这层 fallback 基础设施更像是历史残留，而不是运行时必需链路
- 可以将其提升为独立最小实现型切片处理

## 2. 范围

### 2.1 本轮必须处理

- 新增独立 `00-121`
- 核销前端权限系统中仍保留的 fallback 基础设施是否已无人消费
- 在证据成立前提下，删除无人消费的：
  - `pagePermissionFallbacks`
  - `fallbackPermissions`
  - `PermissionAccessMode` 中的 `fallback`
  - `resolveFallbackPermissions(...)`
  - 无引用的 `getAccessMode(...)`
- 同步清理 IA 文案中仍宣称“招募治理仍保留 admin-users fallback 兼容链路”的过期说法
- 做前端构建验证
- 做最小浏览器 smoke，确认主导航页与 hidden tooling 页权限放通未被破坏

### 2.2 本轮不处理

- 不删除 hidden tooling 路由
- 不删除招募 / AI / operation-logs 页面
- 不修改后端权限模型
- 不继续扩大到菜单结构重构或新的信息架构调整

## 3. 需求

### 3.1 退场合同

- **R1** 必须先证明当前前端运行时代码已不存在实际 fallback 调用点，才能删除权限 fallback 基础设施。
- **R2** 删除范围必须限定在“无人消费的前端权限基础设施”，不得顺手删除 hidden tooling 页面或历史耦合审计矩阵。
- **R3** 权限判断语义必须保持为：
  - 无页面权限要求：允许
  - 有页面 / 动作权限要求：仅按 direct permission 判断

### 3.2 文案合同

- **R4** 任何仍宣称“仍保留 admin-users fallback 兼容链路”的用户可见文案，都必须改成与当前 direct-authority 事实一致的口径。

### 3.3 验证合同

- **R5** 必须通过 `npm run type-check` 与 `npm run build` 验证前端未被破坏。
- **R6** 必须做真实浏览器 smoke，至少覆盖：
  - 一个正式主线页
  - 一个 hidden tooling 页
- **R7** 浏览器截图产物必须落到 `D:\XM\kaipai-team\output\playwright\00-121\`

## 4. 验收标准

- [x] 已新增独立 `00-121`
- [x] 已核实当前前端权限 fallback 基础设施无运行时消费者
- [x] 已删除前端权限 fallback 基础设施残留
- [x] 过期 fallback 文案已同步清理
- [x] `type-check` 与 `build` 通过
- [x] 真实浏览器 smoke 已完成并留档
- [x] README / mapping / CURRENT_CONTEXT / execution 已回填
