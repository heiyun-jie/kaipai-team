# 00-113 当前阶段后台招募 fallback 直授权首轮对齐（Current Phase Admin Recruit Fallback Direct Permission First Pass）

> 状态：已完成 | 优先级：最高 | 依赖：00-110 current-phase-admin-legacy-route-and-fallback-retirement-audit、00-112 current-phase-admin-placeholder-view-retirement-verification
> 记录目的：在 `00-110` 已确认招募治理仍依赖 `page.system.admin-users` fallback、且 `00-112` 已完成低风险旧文件退场后，先把当前 dev 运行库中唯一启用的 fallback 角色补齐直授权，为后续真实删除 fallback 代码建立前提。

## 1. 背景

截至 `2026-04-22`：

- `00-110` 已确认招募治理 fallback 仍由以下链路承接：
  - 前端：`kaipai-admin/src/stores/permission.ts`
  - 前端 consumer：`ProjectsView.vue` / `RolesView.vue` / `AppliesView.vue`
  - 后端 gate：`AdminRecruitController.java` + `RecruitGovernanceFallbackGate.java`
  - 审计矩阵：`AdminRoleServiceImpl.java`
- 当前继续推进旧代码退场时，真正的主阻塞已不再是历史 wrapper，而是**运行库中是否还有启用角色依赖 fallback**

本轮新增运行时核查已确认：

1. 当前 dev 运行库启用角色数为 `1`
2. 当前启用角色中：
   - `pageFallbackRoleCount = 1`
   - `actionFallbackRoleCount = 1`
   - `fallbackRoleCount = 1`
   - `fallbackBoundUserCount = 2`
3. 当前唯一启用且依赖 fallback 的角色是：
   - `role_code = ADMIN`
   - `role_name = 管理`
4. `ADMIN` 当前已经具备：
   - `page.system.admin-users`
5. 但仍缺少全部招募治理直授权：
   - `page.recruit.projects`
   - `page.recruit.roles`
   - `page.recruit.applies`
   - `action.recruit.project.status`
   - `action.recruit.role.status`

当前判断：

- 当前 fallback 仍未清零，不应直接删除前后端 fallback 代码
- 但阻塞面已经足够明确：**先补当前启用 `ADMIN` 角色的 5 个直授权**

## 2. 范围

### 2.1 本轮必须处理

- 新增独立 `00-113`
- 新增一份增量 SQL migration，为当前 `ADMIN` 角色补齐 3 个招募页面权限 + 2 个招募动作权限
- 将该 migration 手动执行到当前 dev 运行库
- 执行后重新核查 fallback 计数，确认 page/action fallback 已清零
- 回填：
  - `.sce/specs/README.md`
  - `.sce/specs/spec-code-mapping.md`
  - `.sce/steering/CURRENT_CONTEXT.md`
  - `execution.md`

### 2.2 本轮不处理

- 不删除前端 `resolveFallbackPermissions`
- 不删除后端 `RecruitGovernanceFallbackGate`
- 不改动 `ProjectsView.vue` / `RolesView.vue` / `AppliesView.vue` 的 fallback 提示逻辑
- 不处理其它环境，仅验证当前 dev 运行库

## 3. 需求

### 3.1 运行时门禁

- **R1** 本轮必须先证明当前 fallback 仍有启用角色在用，不能凭猜测直接删兼容代码。
- **R2** 若当前阻塞只集中在 `ADMIN` 角色，则本轮只补 `ADMIN` 角色，不批量给所有角色扩权。
- **R3** 本轮必须明确 `menu.recruit` 不是运行时必需权限，因此直授权补齐只处理 `page.recruit.*` 与 `action.recruit.*`。

### 3.2 实施合同

- **R4** 必须把权限补齐动作固化为增量 SQL 文件，而不是只做一次临时手工 DB 改写。
- **R5** SQL 必须是幂等的；重复执行不能产生重复权限项。
- **R6** SQL 执行后必须重新核查：
  - `pageFallbackRoleCount`
  - `actionFallbackRoleCount`
  - `fallbackRoleCount`
  - `fallbackBoundUserCount`

### 3.3 边界与回填

- **R7** 本轮即使 fallback 计数归零，也不等于可立即删除兼容代码；真实删代码必须另起切片。
- **R8** `execution.md` 必须记录：
  - 执行前矩阵事实
  - `ADMIN` 角色缺失权限
  - SQL 文件路径
  - 执行后矩阵结果

## 4. 验收标准

- [x] 已新增独立 `00-113`
- [x] 已新增幂等 SQL migration，补齐 `ADMIN` 角色的招募治理直授权
- [x] 当前 dev 运行库已执行该 migration
- [x] 执行后 `pageFallbackRoleCount / actionFallbackRoleCount / fallbackRoleCount / fallbackBoundUserCount` 已归零
- [x] README / mapping / CURRENT_CONTEXT / execution 已回填
