# 00-114 设计说明

## 1. 设计目标

`00-114` 只处理一条主线：

1. 删除 recruit runtime fallback
2. 保持招募矩阵继续承担“历史后台账号页耦合”审计
3. 不在本轮改 DTO / API schema

## 2. 已核实事实

### 2.1 当前 dev 运行库已具备直授权前提

`00-113` 已确认：

- `ADMIN` 已补齐：
  - `page.recruit.projects`
  - `page.recruit.roles`
  - `page.recruit.applies`
  - `action.recruit.project.status`
  - `action.recruit.role.status`
- 当前 dev 运行库 page/action fallback 均为 0

因此：

- 删除 runtime fallback 不会改变当前 dev 运行态的访问结果

### 2.2 当前 runtime fallback 分布清晰

前端：

- `kaipai-admin/src/stores/permission.ts`
- `kaipai-admin/src/views/recruit/ProjectsView.vue`
- `kaipai-admin/src/views/recruit/RolesView.vue`
- `kaipai-admin/src/views/recruit/AppliesView.vue`

后端：

- `kaipaile-server/.../AdminRecruitController.java`
- `kaipaile-server/.../RecruitGovernanceFallbackGate.java`
- `kaipaile-server/.../AdminAuthServiceImpl.java`
- `kaipaile-server/.../AdminSessionInfoDTO.java`

### 2.3 为什么本轮不改矩阵 DTO

当前 `AdminRoleRecruitGovernanceMatrix*` 仍带有：

- `fallbackRoleCount`
- `pageReliesOnFallback`
- `actionReliesOnFallback`
- `canRetirePageFallback`
- `canRetireActionFallback`

这些字段名在语义上已偏向历史阶段，但当前仍被：

- 后端矩阵装配
- 前端 `RolesView.vue`

共同消费。

如果本轮同步重命名：

- 需要改后端 DTO
- 改前端类型
- 改 API 消费
- 改矩阵逻辑

这会把一次“runtime fallback 退场”扩成“矩阵 schema 重构”。

因此本轮策略是：

- **先删 runtime fallback**
- **保留矩阵字段结构**
- **只改用户可见文案**

## 3. 设计策略

### 3.1 前端策略

- `permission.ts` 不再自动把 `page.recruit.* / action.recruit.*` 回退到 `page.system.admin-users`
- 招募三个 hidden tooling 页不再展示 fallback 提示
- 招募动作按钮不再透传 `fallback-permissions`

### 3.2 后端策略

- `AdminRecruitController` 改为 direct authority only
- 删除 `RecruitGovernanceFallbackGate.java`
- `AdminAuthServiceImpl` 不再把 `allowLegacyRecruit*` 注入 session
- `AdminSessionInfoDTO` 去掉对应字段

### 3.3 矩阵与文案策略

招募矩阵保留现有字段，但 UI 文案改成：

- “历史后台账号页耦合”
- “页面直授权待补 / 动作直授权待补”
- “历史耦合已清零 / 仍有历史耦合”

这样可以在不改 API schema 的前提下，让用户看到的运行时口径正确。

## 4. 风险与边界

### 4.1 已确认

- 对当前 dev 运行库，这次退场不应改变权限结果
- 本轮不触碰 AI fallback
- 本轮不触碰 hidden tooling routes 的保留事实

### 4.2 仍存在的边界

- 其它环境若未先执行 `00-113` migration，部署本轮代码会失去招募 fallback

因此本轮结论附带明确前提：

- **目标环境上线前必须先完成 `00-113` migration**
