# 00-113 执行记录

## 1. 当前状态

- 已重新读取 `C:\Users\33340\.codex\memories\user-global-memory.md`
- 已核对 `CURRENT_CONTEXT.md`、`README.md`、`spec-code-mapping.md`、`00-110`、`00-112`
- 已确认当前旧代码 / fallback 主线的真正阻塞已转为：**运行库里是否仍有启用角色依赖招募 fallback**

## 2. 执行前证据

### 2.1 当前 fallback 计数

通过当前 dev 运行库直接查询 `admin_role` 与 `admin_user_role`，按 `AdminRoleServiceImpl#recruitGovernanceMatrix()` 的同口径计算，得到：

- `enabled_role_count = 1`
- `page_fallback_role_count = 1`
- `action_fallback_role_count = 1`
- `fallback_role_count = 1`
- `fallback_bound_user_count = 2`
- `can_retire_page_fallback = false`
- `can_retire_action_fallback = false`

### 2.2 当前阻塞角色

当前唯一启用且依赖 fallback 的角色为：

- `role_code = ADMIN`
- `role_name = 管理`
- `bound = 2`

### 2.3 当前缺失权限

执行前 `ADMIN` 缺少：

- `page.recruit.projects`
- `page.recruit.roles`
- `page.recruit.applies`
- `action.recruit.project.status`
- `action.recruit.role.status`

当前判断：

- fallback 阻塞面已收敛到单一 `ADMIN` 角色

## 3. 本轮实施

### 3.1 新增 migration 文件

已新增：

- `D:\XM\kaipai-team\kaipaile-server\src\main\resources\db\migration\V20260422_008__admin_recruit_direct_permission_alignment.sql`

### 3.2 执行方式

本轮已将上述 migration 同步手动执行到当前 dev 运行库一次。

首次执行结果：

- `rows_changed = 5`

本轮只补：

- `page.recruit.projects`
- `page.recruit.roles`
- `page.recruit.applies`
- `action.recruit.project.status`
- `action.recruit.role.status`

本轮未补：

- `menu.recruit`

原因：

- 当前运行时 gating 不依赖 `menu.recruit`

### 3.3 幂等复核

同一组 SQL 在当前 dev 运行库再次执行后返回：

- `rows_changed = 0`

当前判断：

- migration 已满足幂等要求

## 4. 执行后验证

### 4.1 执行后 fallback 计数

重新按同口径查询后得到：

- `enabled_role_count = 1`
- `page_fallback_role_count = 0`
- `action_fallback_role_count = 0`
- `fallback_role_count = 0`
- `fallback_bound_user_count = 0`
- `can_retire_page_fallback = true`
- `can_retire_action_fallback = true`

### 4.2 执行后角色状态

当前 `ADMIN` 已具备：

- `page.recruit.projects`
- `page.recruit.roles`
- `page.recruit.applies`
- `action.recruit.project.status`
- `action.recruit.role.status`

当前判断：

- 当前 dev 运行库中的招募 fallback 已完成**运行时前提清零**

## 5. 结论

`00-113` 已完成本轮目标：

- 已把当前 dev 运行库中唯一启用 fallback 角色补齐直授权
- 当前 page/action fallback 计数均已清零
- 下一步若继续推进，应另起切片删除前后端 fallback 代码，而不是继续停留在运行库迁移阶段

当前边界：

- 本轮只验证了当前 dev 运行库
- 其它环境是否也能直接退 fallback，尚未核实
