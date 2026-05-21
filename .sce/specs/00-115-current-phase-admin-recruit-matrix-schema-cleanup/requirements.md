# 00-115 当前阶段后台招募矩阵 schema 清理（Current Phase Admin Recruit Matrix Schema Cleanup）

> 状态：已完成 | 优先级：高 | 依赖：00-114 current-phase-admin-recruit-fallback-code-retirement-first-pass
> 记录目的：在 `00-114` 已完成 recruit runtime fallback 退场后，继续清理招募治理授权矩阵中仍残留的 fallback 字段命名，把 schema 口径统一切到“后台账号页历史耦合 / 直授权缺口”。

## 1. 背景

截至 `2026-04-23`：

- `00-114` 已完成：
  - 前端不再给 `page.recruit.* / action.recruit.*` 自动注入 fallback
  - 后端 `AdminRecruitController` 已只认 direct authority
  - `RecruitGovernanceFallbackGate.java` 已删除
- 当前 runtime recruit fallback 已退场，但招募矩阵 DTO / 前端类型仍残留以下旧字段命名：
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

当前判断：

- 这些字段名已经不再准确描述当前运行态
- 若继续保留，会让“历史后台账号页耦合审计”与“runtime fallback”混淆

## 2. 范围

### 2.1 本轮必须处理

- 新增独立 `00-115`
- 清理招募矩阵后端 DTO 字段命名
- 清理 `AdminRoleServiceImpl` 中招募矩阵装配命名
- 清理前端 `types/system.ts` 与 `RolesView.vue` 对招募矩阵字段的消费命名
- 回填：
  - `.sce/specs/README.md`
  - `.sce/specs/spec-code-mapping.md`
  - `.sce/steering/CURRENT_CONTEXT.md`
  - `execution.md`

### 2.2 本轮不处理

- 不改 AI 治理矩阵 schema
- 不改 `/admin/system/roles/recruit-governance-matrix` 的接口路径
- 不改 `rolloutStage` 的枚举值，只允许调整其用户可见标签
- 不改数据库

## 3. 需求

### 3.1 命名合同

- **R1** 招募矩阵字段命名必须从 `fallback` 语义切换到“后台账号页历史耦合 / 直授权缺口”语义。
- **R2** 字段重命名必须前后端一致，不允许出现后端已改、前端仍消费旧字段的半完成状态。
- **R3** 本轮只清理招募矩阵相关 schema，不得顺势扩大到 AI 矩阵。

### 3.2 口径合同

- **R4** “页面侧缺口”字段必须表达：当前角色仍保留后台账号页耦合，且缺少招募页面直授权。
- **R5** “动作侧缺口”字段必须表达：当前角色仍保留后台账号页耦合，且缺少招募动作直授权。
- **R6** “总耦合”字段必须表达：当前角色是否仍保留后台账号页历史耦合，而不是 runtime fallback 是否仍可用。

### 3.3 验证合同

- **R7** 本轮必须至少通过：
  - `kaipai-admin` 的 `npm run type-check`
  - `kaipai-admin` 的 `npm run build`
  - `kaipaile-server` 的 `mvn -q -DskipTests compile`

## 4. 验收标准

- [x] 已新增独立 `00-115`
- [x] 招募矩阵 schema 命名已从 `fallback` 切换到“后台账号页耦合 / 直授权缺口”
- [x] 前端 `RolesView.vue` 与 `types/system.ts` 已同步消费新字段
- [x] 前端 type-check / build 与后端 compile 通过
- [x] README / mapping / CURRENT_CONTEXT / execution 已回填
