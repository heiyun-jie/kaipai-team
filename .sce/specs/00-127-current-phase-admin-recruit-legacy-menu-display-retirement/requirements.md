# 00-127 当前阶段后台 recruit 历史菜单展示合同退场（Current Phase Admin Recruit Legacy Menu Display Retirement）

> 状态：已完成 | 优先级：中 | 依赖：00-126 current-phase-admin-recruit-legacy-menu-runtime-retirement、00-115 current-phase-admin-recruit-matrix-schema-cleanup
> 记录目的：在 `00-126` 已确认 dev 运行库与登录态都不再携带 `menu.recruit` 后，继续把招募治理矩阵里剩余的 `hasRecruitMenu` 历史展示合同退场，避免前后端继续把已失效菜单作为矩阵字段和用户可见标签。

## 1. 背景

截至 `2026-04-23`：

- `00-113` 已补齐当前 dev 运行库中的招募页面 / 动作直授权
- `00-114` 已完成招募 runtime fallback 代码退场
- `00-115` 已把招募矩阵从 `fallback*` schema 切到后台账号页历史耦合口径
- `00-125` 曾把 `menu.recruit` 作为历史菜单登记补入前端 registry，消除角色编辑弹窗 unknown
- `00-126` 已把当前 dev 运行库中的 `menu.recruit` 从角色数据中清理掉

本轮重新核实到：

- 当前 live `GET /admin/system/roles/recruit-governance-matrix` 仍返回：
  - `hasRecruitMenu`
- 当前 `hasRecruitMenu = false`
- 当前角色详情 `menuPermissions` 已不再包含：
  - `menu.recruit`
- 代码中仍残留：
  - `AdminRoleRecruitGovernanceMatrixItemDTO.hasRecruitMenu`
  - `AdminRoleServiceImpl.RECRUIT_MENU_PERMISSION`
  - `RolesView.vue` 中“历史 menu.recruit”矩阵标签与表单提示分支
  - `AdminRoleRecruitGovernanceMatrixItem.hasRecruitMenu`
  - `PERMISSIONS.menu.recruit` 常量

当前判断：

- `menu.recruit` 已不再参与招募 runtime 放通
- 当前 dev 运行库已不再返回该菜单
- 招募矩阵继续暴露 `hasRecruitMenu` 只会保留过期展示合同
- 但前端 permission registry 中的历史登记仍可作为编辑 / 详情兼容兜底，不应在本轮删除

## 2. 范围

### 2.1 本轮必须处理

- 新增独立 `00-127`
- 从招募矩阵后端 DTO / service 装配中移除 `hasRecruitMenu`
- 从前端 `types/system.ts` 中移除招募矩阵 `hasRecruitMenu`
- 从 `RolesView.vue` 中移除招募矩阵的“历史 menu.recruit”标签与对应历史提示分支
- 删除前端已无消费者的 `PERMISSIONS.menu.recruit` 常量
- 通过前端 type-check / build 与后端 compile
- 刷新后端运行态后复核招募矩阵响应不再包含 `hasRecruitMenu`
- 真实浏览器复核 `/system/roles`

### 2.2 本轮不处理

- 不删除 `permission-registry.ts` 中的 `menu.recruit` 历史登记
- 不删除 `V20260423_009__admin_recruit_legacy_menu_runtime_retirement.sql`
- 不修改招募 controller 鉴权
- 不修改数据库数据
- 不删除 hidden tooling 的 `/recruit/*` 页面

## 3. 需求

### 3.1 合同退场要求

- **R1** 招募矩阵响应体不应继续暴露 `hasRecruitMenu`。
- **R2** 招募矩阵前端类型和页面消费必须与后端响应体同步，不允许出现前端仍消费已删除字段的半完成状态。
- **R3** `RolesView.vue` 用户可见文案应继续围绕 `page.recruit.* / action.recruit.*` 直授权与 `page.system.admin-users` 历史耦合，不再把 `menu.recruit` 当成矩阵判断项。

### 3.2 兼容边界要求

- **R4** 前端 permission registry 中的 `menu.recruit` 历史登记本轮保留，避免其它环境残留角色数据在编辑弹窗中重新变成 unknown。
- **R5** 本轮不得重新引入 `menu.recruit` 运行时放通语义。
- **R6** 本轮不得扩大到其它历史菜单或其它 hidden tooling 删除。

### 3.3 验证要求

- **R7** 必须通过：
  - `kaipai-admin` 的 `npm run type-check`
  - `kaipai-admin` 的 `npm run build`
  - `kaipaile-server` 的 `mvn -q -DskipTests compile`
- **R8** 刷新后端运行态后，登录态招募矩阵响应字段不应包含 `hasRecruitMenu`。
- **R9** 必须基于真实浏览器复核 `/system/roles`，截图落到 `D:\XM\kaipai-team\output\playwright\00-127\`。

## 4. 验收标准

- [x] 已新增独立 `00-127`
- [x] 招募矩阵后端 DTO / service 已移除 `hasRecruitMenu`
- [x] 前端 `types/system.ts` / `RolesView.vue` 已同步移除 `hasRecruitMenu` 消费
- [x] `PERMISSIONS.menu.recruit` 死常量已退场
- [x] `permission-registry.ts` 中的历史登记仍保留
- [x] 前端 type-check / build 与后端 compile 通过
- [x] 登录态 API 已确认招募矩阵响应不再包含 `hasRecruitMenu`
- [x] 真实浏览器复核已完成并留档
- [x] README / mapping / CURRENT_CONTEXT / execution 已回填
