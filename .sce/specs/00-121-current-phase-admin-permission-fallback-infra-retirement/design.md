# 00-121 设计说明

## 1. 设计目标

`00-121` 只处理一个问题：

1. 当前前端权限系统里仍残留的一层 fallback 基础设施，是否已经没有运行时消费者；若已无消费者，则在最小范围内退场

## 2. 已核实事实

### 2.1 招募 / AI runtime fallback 已经退场

已有前置事实：

- `00-114` 已删除招募 runtime fallback 代码
- `00-115 / 00-116` 已把矩阵字段改为历史耦合口径
- `00-120` 已确认本机 `8010` 运行态吃到最新代码

因此：

- 当前需要区分“历史耦合展示”与“前端权限 runtime fallback 基础设施”

### 2.2 前端权限 fallback 入口当前只剩基础设施残留

当前前端代码里仍能看到：

- `PermissionAccessMode` 中的 `fallback`
- `resolveFallbackPermissions(...)`
- `pagePermissionFallbacks`
- `fallbackPermissions`

但当前尚未发现：

- 实际 route meta 配置 `pagePermissionFallbacks`
- 实际按钮调用传入 `fallbackPermissions`

因此：

- 当前更像是基础设施残留，而不是活跃运行时依赖

### 2.3 当前运行态已验证 direct-authority 未被破坏

本轮已再次核实：

- `type-check` 与 `build` 已通过
- 真实浏览器可继续访问：
  - `/system/settings`
  - `/recruit/projects`
- `/recruit/projects` 顶部 tooling 说明已更新为“当前已按独立页面 / 动作权限直连放通”

## 3. 设计策略

### 3.1 先删除无人消费的权限 fallback 管线

本轮只做最小收口：

1. `utils/permission.ts`
   - 删掉 `fallback` 模式
   - `hasPermission(...)` 改为只按 direct permission 判断
2. `stores/permission.ts`
   - 删掉 `resolveFallbackPermissions(...)`
   - 删掉无调用价值的 `getAccessMode(...)`
3. `router/index.ts`
   - 删掉 `pagePermissionFallbacks` 读取
4. `types/admin.ts`、`types/router.d.ts`
   - 删掉 `pagePermissionFallbacks`
5. `PermissionButton.vue`
   - 删掉 `fallbackPermissions` prop

### 3.2 再清理过期文案

与权限 fallback 退场直接相关的文案同步更新：

- `admin-information-architecture.ts` 中 `/recruit/*` 描述

必要时同步收口仍把“fallback 清理”当未来事项的用户可见提示，但不扩到无关页面。

### 3.3 最后做最小运行态验证

由于本轮改的是权限内核，需做最小浏览器 smoke：

- 正式页：确认主导航仍可访问
- hidden tooling 页：确认 direct page permission 仍可正常放通

## 4. 风险与边界

### 4.1 已确认

- 当前不应删除 hidden tooling 页
- 当前不应删除矩阵中的历史耦合展示能力
- 当前只退场“无人消费的权限 fallback 基础设施”

### 4.2 当前边界

- 本轮只改前端
- 不修改后端鉴权
- 不修改角色权限数据库
