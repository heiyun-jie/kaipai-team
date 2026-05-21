# 00-122 当前阶段后台 membership 历史菜单退场（Current Phase Admin Membership Legacy Menu Retirement）

> 状态：已完成 | 优先级：中 | 依赖：00-110 current-phase-admin-legacy-route-and-fallback-retirement-audit、00-121 current-phase-admin-permission-fallback-infra-retirement
> 记录目的：在前端权限 fallback 基础设施已退场后，继续核销 `menu.membership` 是否仍是运行时必需项；若已不是，则把前端权限 registry 中残留的 membership 历史菜单登记做最小退场。

## 1. 背景

截至 `2026-04-23`：

- `00-121` 已完成前端权限 fallback 基础设施退场
- 当前继续沿 `00-110` 的“旧路由 / 旧代码 / fallback 退场审计”主线推进

当前已补充核实到：

- 前端 `D:\XM\kaipai-team\kaipai-admin\src\constants\permission-registry.ts` 仍保留：
  - `legacyMenuRegistry`
  - `menu.membership`
- 但当前后端源码只命中：
  - `page.membership.*`
  - `action.membership.*`
  - 未命中 `menu.membership`
- 当前本机运行库角色复核结果：
  - 现有角色未携带 `menu.membership`
- 当前角色矩阵和登录态运行态也未显示 `menu.membership` 作为有效菜单权限

当前判断：

- `menu.membership` 更像历史菜单残留，而不是现行运行时权限项

## 2. 范围

### 2.1 本轮必须处理

- 新增独立 `00-122`
- 核销 `menu.membership` 是否仍被：
  - 前端权限 registry
  - 后端鉴权
  - 当前运行库角色
  实际依赖
- 在证据成立前提下，删除前端 `permission-registry.ts` 中的 `legacyMenuRegistry` / `menu.membership` 残留
- 做前端构建验证
- 做最小浏览器 smoke，确认角色治理页与权限编排区未被破坏

### 2.2 本轮不处理

- 不处理 membership 页面 / 动作权限本身
- 不处理角色矩阵阶段枚举 `compat_transition / fallback_only`
- 不新增 membership 正式导航
- 不改后端 membership controller

## 3. 需求

### 3.1 退场合同

- **R1** 必须先证明 `menu.membership` 当前不被后端鉴权和运行库角色消费，才能执行退场。
- **R2** 删除范围必须限定在前端权限 registry 中的历史菜单残留，不得顺手改动 membership 页面 / 动作权限。
- **R3** 删除后角色治理页的权限编排区不能出现类型错误或未知权限异常。

### 3.2 验证合同

- **R4** 必须通过 `npm run type-check` 与 `npm run build`。
- **R5** 必须做真实浏览器 smoke，至少覆盖 `/system/roles`。
- **R6** 浏览器截图产物必须落到 `D:\XM\kaipai-team\output\playwright\00-122\`

## 4. 验收标准

- [x] 已新增独立 `00-122`
- [x] 已核实 `menu.membership` 当前不被后端与运行库消费
- [x] 已删除 `permission-registry.ts` 中的 membership 历史菜单残留
- [x] `type-check` 与 `build` 通过
- [x] 真实浏览器 smoke 已完成并留档
- [x] README / mapping / CURRENT_CONTEXT / execution 已回填
