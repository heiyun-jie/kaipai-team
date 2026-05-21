# 00-113 设计说明

## 1. 设计目标

`00-113` 只解决一个运行时前提问题：

1. 让当前 dev 运行库中仍依赖 `page.system.admin-users` fallback 的启用角色改为**显式直授权**
2. 先清零 page/action fallback 计数
3. 不在本轮直接删除 fallback 代码

## 2. 已核实事实

### 2.1 当前 fallback 仍真实存在

运行库核查结果表明：

- 启用角色数：`1`
- page fallback：`1`
- action fallback：`1`
- 总 fallback：`1`
- fallback 绑定账号：`2`

说明：

- fallback 不是历史代码残留
- 而是当前 dev 运行库仍在真实使用的兼容通道

### 2.2 当前阻塞只集中在 `ADMIN`

当前唯一启用且依赖 fallback 的角色为：

- `ADMIN / 管理`

它当前已经拥有：

- `page.system.admin-users`

但缺少：

- `page.recruit.projects`
- `page.recruit.roles`
- `page.recruit.applies`
- `action.recruit.project.status`
- `action.recruit.role.status`

因此：

- 当前 fallback 的阻塞面是单点、明确、低扩散

### 2.3 为什么本轮只补 `ADMIN`

依据：

1. 当前只有 `ADMIN` 是启用角色并触发 fallback
2. `ADMIN` 通过后台账号页 fallback 已经拥有等价招募治理能力
3. 给 `ADMIN` 补直授权属于**能力显式化**，不是新增业务权限

因此：

- 本轮只补 `ADMIN`，能最小代价清零当前 dev 运行库的 fallback 计数

### 2.4 为什么不补 `menu.recruit`

已核实：

- `adminMenus` 中招募治理组顶层没有依赖 `menu.recruit` 放通
- `RolesView.vue` 已明确把 `menu.recruit` 标为“历史 menu.recruit，不作为运行时必需项”

因此：

- 本轮 migration 不补 `menu.recruit`
- 只补真正参与运行时 gating 的 `page.recruit.*` 与 `action.recruit.*`

## 3. 设计策略

### 3.1 代码侧策略

新增增量 migration：

- `D:\XM\kaipai-team\kaipaile-server\src\main\resources\db\migration\V20260422_008__admin_recruit_direct_permission_alignment.sql`

该文件只做 5 次幂等追加：

- 3 个页面权限
- 2 个动作权限

目标角色：

- `role_code = 'ADMIN'`

### 3.2 运行时策略

在当前 dev 库手动执行该 migration 一次，随后重新查询矩阵。

预期：

- `ADMIN` 从 fallback-only / compat-transition 转为 direct-ready
- `canRetirePageFallback = true`
- `canRetireActionFallback = true`

### 3.3 为什么本轮不删 fallback 代码

即使当前 dev 库计数清零，也仍有两个边界：

1. 其它环境尚未验证
2. 前后端 fallback 代码删除属于更高风险变更，应另起切片完成

因此本轮到此为止：

- 先把运行库前提补齐
- 再为下一轮代码退场创造条件

## 4. 风险与边界

### 4.1 已确认

- 给 `ADMIN` 补招募直授权不会扩大正式 8 页导航
- recruit 页仍是 hidden tooling
- 当前能力不会新增，只是从 fallback 改为 direct

### 4.2 当前不确定边界

- 其它环境是否已有不同角色组合
- 其它环境是否也只有 `ADMIN` 依赖 fallback

因此当前结论仅覆盖：

- **当前 dev 运行库**
