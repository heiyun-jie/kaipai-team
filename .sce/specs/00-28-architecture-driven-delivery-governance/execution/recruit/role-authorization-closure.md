# 招募治理角色授权收口说明

## 1. 文档目的

- 把招募治理从“页面已上线但仍靠 `page.system.admin-users` fallback 可见”推进到“可在真实角色分配流程中显式授权”
- 明确当前角色权限树、角色保存、后台登录回包与招募治理矩阵的真实数据流
- 给出建议角色包、环境收口步骤与 `admin-users` fallback 下线条件

## 2. 当前代码事实

### 2.1 角色管理页权限树数据源

- `kaipai-admin/src/views/system/RolesView.vue`
  - 角色新建 / 编辑使用 `PermissionTreeEditor`
  - 角色列表页已新增招募治理授权矩阵，直接盘点 fallback 依赖角色
- `kaipai-admin/src/components/forms/PermissionTreeEditor.vue`
  - 权限树展示、勾选、分类拆分都在前端完成
- `kaipai-admin/src/constants/permission-registry.ts`
  - 权限树数据来自本地 registry
  - `menu.recruit`
  - `page.recruit.projects`
  - `page.recruit.roles`
  - `page.recruit.applies`
  - `action.recruit.project.status`
  - `action.recruit.role.status`
  - 均已登记到 `recruit` 模块

### 2.2 角色保存与回显数据源

- `kaipai-admin/src/api/system.ts`
  - 角色管理页通过 `/admin/system/roles` 读写角色
  - 角色管理页通过 `/admin/system/roles/recruit-governance-matrix` 拉取招募授权矩阵
- `kaipaile-server/src/main/java/com/kaipai/module/controller/admin/system/AdminSystemController.java`
  - 角色列表、详情、创建、编辑、复制、启停用，以及招募授权矩阵均走真实后端接口
- `kaipaile-server/src/main/java/com/kaipai/module/server/system/service/impl/AdminRoleServiceImpl.java`
  - 角色的 `menuPermissionsJson`、`pagePermissionsJson`、`actionPermissionsJson` 会按原样落库并回显
  - 会额外汇总角色是否补齐招募菜单 / 页面 / 动作权限、是否仍依赖 fallback、绑定账号数与 fallback 下线判断

### 2.3 会话权限聚合

- `kaipaile-server/src/main/java/com/kaipai/module/server/adminauth/service/impl/AdminAuthServiceImpl.java`
  - 登录态会把角色的菜单 / 页面 / 动作权限聚合到当前后台会话
  - 因此只要角色里配置了 recruit 新权限码，登录后的真实后台账号就能拿到对应 authority

## 3. 当前结论

- recruit 新页面 / 动作权限已经能在真实角色分配流程中出现
- 当前缺的不是“代码是否可分配”，而是“目标环境是否已按统一角色矩阵完成一次真实绑定和验证”
- `page.system.admin-users` 仍是兼容兜底，不应再作为招募治理新授权的首选入口

## 4. 建议角色包

| 角色包 | 适用对象 | 菜单权限 | 页面权限 | 动作权限 |
|--------|----------|----------|----------|----------|
| 招募治理只读 | 运营查看、排查问题 | `menu.recruit` | `page.recruit.projects`、`page.recruit.roles`、`page.recruit.applies` | 无 |
| 招募治理处置 | 运营处置、状态校准 | `menu.recruit` | `page.recruit.projects`、`page.recruit.roles`、`page.recruit.applies` | `action.recruit.project.status`、`action.recruit.role.status` |

补充说明：

- 若账号还需要继续维护后台账号管理，可额外保留 `page.system.admin-users`
- 但这项权限不应再被当作招募治理入口的替代品

## 5. 环境收口步骤

1. 先在角色管理页招募授权矩阵中确认哪些角色处于 `fallback_only / compat_transition / partial_recruit`
2. 为目标角色套用“招募治理只读”或“招募治理处置”权限包
3. 在后台账号管理页把目标角色绑定到真实后台账号
4. 使用该账号重新登录后台，确认当前会话返回了独立 recruit 菜单 / 页面 / 动作权限
5. 验证招募治理菜单、项目 / 角色 / 投递三张页和状态处置按钮是否与角色范围一致
6. 把验证结果回填到 `status/crew-company-project-status.md` 与 `status/recruit-role-apply-status.md`

## 6. Fallback 下线条件

只有同时满足以下条件，才建议删除 `page.system.admin-users` 对招募治理的兼容兜底：

1. 目标环境里至少一组启用中的角色已显式配置 `menu.recruit`
2. 需要查看招募治理页的角色已显式配置三张 `page.recruit.*`
3. 需要处置项目 / 角色状态的角色已显式配置 `action.recruit.project.status` 与 `action.recruit.role.status`
4. 已确认不再存在“仅靠 `page.system.admin-users` 才能进入招募治理页”的后台账号
5. 已完成一次真实账号登录验证，并确认当前会话权限中出现独立 recruit 权限码

## 7. 下线时需要一起改动的文件

- `kaipai-admin/src/constants/menus.ts`
- `kaipai-admin/src/router/index.ts`
- `kaipai-admin/src/views/recruit/ProjectsView.vue`
- `kaipai-admin/src/views/recruit/RolesView.vue`
- `kaipai-admin/src/views/recruit/AppliesView.vue`
- `kaipaile-server/src/main/java/com/kaipai/module/controller/admin/recruit/AdminRecruitController.java`
- `status/crew-company-project-status.md`
- `status/recruit-role-apply-status.md`

## 8. 本轮新增支撑物

- `kaipai-admin/src/views/system/RolesView.vue`
  - 已补招募治理授权矩阵与建议授权包，减少手工检索权限码的操作成本
- `kaipaile-server/src/main/java/com/kaipai/module/server/system/service/impl/AdminRoleServiceImpl.java`
  - 已补 `/admin/system/roles/recruit-governance-matrix` 汇总，直接产出角色迁移阶段、绑定账号数与 fallback 下线判断
- 本文档
  - 作为招募角色矩阵收口与 fallback 下线的统一说明
