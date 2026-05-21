# 00-114 当前阶段后台招募 fallback 代码退场第一批（Current Phase Admin Recruit Fallback Code Retirement First Pass）

> 状态：已完成 | 优先级：最高 | 依赖：00-110 current-phase-admin-legacy-route-and-fallback-retirement-audit、00-113 current-phase-admin-recruit-fallback-direct-permission-first-pass
> 记录目的：在 `00-113` 已将当前 dev 运行库中的招募治理 fallback 计数清零后，继续把前后端 runtime recruit fallback 逻辑做第一批退场。

## 1. 背景

截至 `2026-04-23`：

- `00-110` 已明确招募治理 fallback 涉及：
  - 前端自动注入：`kaipai-admin/src/stores/permission.ts`
  - 前端 consumer：`ProjectsView.vue`、`RolesView.vue`、`AppliesView.vue`
  - 后端 gate：`AdminRecruitController.java`、`RecruitGovernanceFallbackGate.java`
  - 会话透传：`AdminAuthServiceImpl.java`、`AdminSessionInfoDTO.java`
- `00-113` 已确认当前 dev 运行库：
  - `pageFallbackRoleCount = 0`
  - `actionFallbackRoleCount = 0`
  - `fallbackRoleCount = 0`
  - `fallbackBoundUserCount = 0`

当前判断：

- 当前 dev 运行库已经满足“先补直授权，再删 runtime fallback”的门禁
- 因此可以进入第一批代码退场

## 2. 范围

### 2.1 本轮必须处理

- 新增独立 `00-114`
- 删除前端自动注入的招募 fallback 权限逻辑
- 删除招募页中的 fallback 提示与 `fallback-permissions` 传参
- 删除后端 `AdminRecruitController` 的 fallback `@PreAuthorize` 条件
- 删除 `RecruitGovernanceFallbackGate.java`
- 删除会话 DTO / session 装配中的 `allowLegacyRecruit*` 字段
- 回填：
  - `.sce/specs/README.md`
  - `.sce/specs/spec-code-mapping.md`
  - `.sce/steering/CURRENT_CONTEXT.md`
  - `execution.md`

### 2.2 本轮不处理

- 不处理 AI 治理的 operation-logs fallback
- 不重命名招募矩阵 DTO / API 字段
- 不改动招募矩阵的后端统计口径
- 不处理其它环境数据库，只以 `00-113` 已完成的 dev 运行库为代码退场前提

## 3. 需求

### 3.1 退场门禁

- **R1** 只有在 `00-113` 已确认当前目标运行库 page/action fallback 计数均为 0 时，才允许进入本轮代码退场。
- **R2** 本轮退场只覆盖 **recruit runtime fallback**，不得顺势扩大到其它 fallback 域。
- **R3** 本轮必须显式保留“目标环境上线前需先执行 `00-113` migration”的发布前提，不能假设所有环境已同步直授权。

### 3.2 实施合同

- **R4** 前端退场后，招募页权限判断必须只认 direct `page.recruit.* / action.recruit.*`。
- **R5** 后端退场后，`AdminRecruitController` 必须只认 direct `page.recruit.* / action.recruit.*`。
- **R6** 本轮允许继续保留招募矩阵中现有 fallback 字段结构，作为历史耦合审计载体，但用户可见文案必须从“当前 runtime fallback”切换为“历史后台账号页耦合 / 直授权缺口”。

### 3.3 验证合同

- **R7** 本轮必须至少通过：
  - `kaipai-admin` 的 `npm run type-check`
  - `kaipai-admin` 的 `npm run build`
  - `kaipaile-server` 的 `mvn -q -DskipTests compile`
- **R8** 若编译失败，不得扩大删除范围，需先回收本轮改动。

## 4. 验收标准

- [x] 已新增独立 `00-114`
- [x] 前后端 recruit runtime fallback 逻辑第一批已退场
- [x] 招募矩阵用户可见文案已从 runtime fallback 切到历史耦合 / 直授权缺口口径
- [x] 前端 type-check / build 与后端 compile 通过
- [x] README / mapping / CURRENT_CONTEXT / execution 已回填
