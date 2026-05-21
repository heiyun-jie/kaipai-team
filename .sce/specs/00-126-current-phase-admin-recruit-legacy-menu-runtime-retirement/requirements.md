# 00-126 当前阶段后台 recruit 历史菜单运行库退场（Current Phase Admin Recruit Legacy Menu Runtime Retirement）

> 状态：已完成 | 优先级：中 | 依赖：00-113 current-phase-admin-recruit-fallback-direct-permission-first-pass、00-114 current-phase-admin-recruit-fallback-code-retirement-first-pass、00-125 current-phase-admin-recruit-legacy-menu-registry-alignment
> 记录目的：在 `menu.recruit` 已完成前端 registry 对齐且当前运行时已明确不依赖它放通招募治理后，继续把 dev 运行库中仍残留的 `menu.recruit` 做成独立退场切片，并验证招募矩阵与登录态是否已切到“无历史 menu.recruit”状态。

## 1. 背景

截至 `2026-04-23`：

- `00-113` 已为当前 dev 运行库补齐 `page.recruit.* / action.recruit.*` 直授权
- `00-114` 已完成招募 runtime fallback 代码退场
- `00-125` 已把 `menu.recruit` 收口为前端 registry 中的“历史菜单登记”，角色编辑弹窗 unknown 已清零

当前进一步核实到：

- `AdminRecruitController.java` 当前只认：
  - `page.recruit.projects`
  - `page.recruit.roles`
  - `page.recruit.applies`
  - `action.recruit.project.status`
  - `action.recruit.role.status`
- `adminMenus.recruit` 当前没有 `menuPermission`
- 当前本机 dev 运行库唯一角色 `ADMIN` 仍保留：
  - `menu.recruit`
- 当前 `V20260422_008__admin_recruit_direct_permission_alignment.sql` 明确保留了 `menu.recruit`

当前判断：

- `menu.recruit` 当前不再承担运行时放通作用
- 当前更合理的下一手，不是继续只做前端展示，而是把 dev 运行库中的这条历史菜单权限真正清掉

## 2. 范围

### 2.1 本轮必须处理

- 新增独立 `00-126`
- 新增幂等 migration，把当前已补齐招募页面 / 动作直授权的角色从 `menu_permissions_json` 中移除 `menu.recruit`
- 刷新本机 `8010` 后端运行态
- 用登录态 API 复核：
  - 角色详情中的 `menuPermissions`
  - 招募矩阵中的 `hasRecruitMenu`
- 用真实浏览器复核 `/system/roles`

### 2.2 本轮不处理

- 不删除前端 `PERMISSIONS.menu.recruit` 常量
- 不删除招募矩阵中的 `hasRecruitMenu` 历史展示字段
- 不扩展到其它环境数据库

## 3. 需求

### 3.1 数据退场合同

- **R1** 只有在角色已具备完整 `page.recruit.* / action.recruit.*` 直授权的前提下，才允许从运行库移除 `menu.recruit`。
- **R2** migration 必须幂等，重复执行不能产生副作用。
- **R3** 本轮只能处理 dev 运行库中当前满足门禁的角色，不得盲删所有角色的 `menu.recruit`。

### 3.2 验证合同

- **R4** 刷新后必须重新验证 `8010` 已吃到新 migration 结果。
- **R5** 登录态角色详情中不应再返回 `menu.recruit`。
- **R6** 招募矩阵当前运行态中 `hasRecruitMenu` 应转为 `false`。
- **R7** 必须基于真实浏览器复核 `/system/roles`，并输出截图到 `D:\XM\kaipai-team\output\playwright\00-126\`

## 4. 验收标准

- [x] 已新增独立 `00-126`
- [x] 已新增并应用 `menu.recruit` 运行库清理 migration
- [x] 本机 `8010` 已刷新到新运行态
- [x] 角色详情不再返回 `menu.recruit`
- [x] 招募矩阵中 `hasRecruitMenu` 已变为 `false`
- [x] 真实浏览器截图已复核 `/system/roles`
- [x] README / mapping / CURRENT_CONTEXT / execution 已回填
