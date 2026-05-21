# 00-115 执行记录

## 1. 当前状态

- 已重新读取 `C:\Users\33340\.codex\memories\user-global-memory.md`
- 已核对 `CURRENT_CONTEXT.md`、`README.md`、`spec-code-mapping.md`、`00-114`
- 已确认当前主线从“runtime fallback 退场”转入“招募矩阵 schema 命名清理”

## 2. 清理前证据

### 2.1 当前残留字段

后端 DTO / 前端类型 / 前端消费仍残留：

- `fallbackRoleCount`
- `pageFallbackRoleCount`
- `actionFallbackRoleCount`
- `fallbackBoundUserCount`
- `canRetirePageFallback`
- `canRetireActionFallback`
- `canRetireFallback`
- `pageReliesOnFallback`
- `actionReliesOnFallback`
- `reliesOnFallback`

### 2.2 当前真实语义

结合 `00-114` 已知事实，当前这些字段真实表达的是：

- 后台账号页历史耦合是否仍保留
- 页面直授权是否仍待补
- 动作直授权是否仍待补

而不是 runtime fallback 是否仍可用。

## 3. 本轮实施

### 3.1 后端

已完成：

- `AdminRoleRecruitGovernanceMatrixRespDTO.java`
- `AdminRoleRecruitGovernanceMatrixItemDTO.java`
- `AdminRoleServiceImpl.java`

把招募矩阵字段统一改成：

- `adminUsersCouplingRoleCount`
- `pageAdminUsersCouplingRoleCount`
- `actionAdminUsersCouplingRoleCount`
- `adminUsersCouplingBoundUserCount`
- `pageAdminUsersCouplingCleared`
- `actionAdminUsersCouplingCleared`
- `adminUsersCouplingCleared`
- `pageRetainsAdminUsersCoupling`
- `actionRetainsAdminUsersCoupling`
- `retainsAdminUsersCoupling`

### 3.2 前端

已完成：

- `types/system.ts`
- `RolesView.vue`

同步改为消费新字段，并把相关 helper / 统计变量命名同步切换到后台账号页耦合口径。

### 3.3 用户可见标签

已补一处阶段标签收口：

- `fallback_only` 在招募矩阵中的用户可见标签改为 `仅后台账号页耦合`

## 4. 验证结果

### 4.1 前端

命令：

- `cd D:\XM\kaipai-team\kaipai-admin && npm run type-check`
- `cd D:\XM\kaipai-team\kaipai-admin && npm run build`

结果：

- `type-check`：通过
- `build`：通过

保留告警：

- Sass legacy JS API deprecation
- Vite chunk size warning

### 4.2 后端

命令：

- `cd D:\XM\kaipai-team\kaipaile-server && mvn -q -DskipTests compile`

结果：

- `compile`：通过

## 5. 结论

`00-115` 已完成本轮目标：

- 招募矩阵 schema 命名已与当前运行态一致
- 当前“后台账号页历史耦合 / 直授权缺口”的语义已在前后端统一
- 本轮未触碰 AI 矩阵与数据库
