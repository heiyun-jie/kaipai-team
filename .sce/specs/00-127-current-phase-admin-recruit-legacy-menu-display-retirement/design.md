# 00-127 设计说明

## 1. 设计目标

`00-127` 只处理一个问题：

1. 把招募治理矩阵中已失效的 `menu.recruit` 历史展示合同退场。

本轮不重新解释招募权限模型，也不扩展到其它历史菜单。

## 2. 已核实事实

### 2.1 当前运行态已经不需要 `menu.recruit`

已确认：

- 招募路由与 `AdminRecruitController.java` 只认 `page.recruit.* / action.recruit.*`
- 当前 dev 运行库 `ADMIN` 角色详情 `menuPermissions` 已不再包含 `menu.recruit`
- 当前登录态 session 也不再包含 `menu.recruit`
- 当前招募矩阵中 `hasRecruitMenu = false`

因此：

- `hasRecruitMenu` 继续保留在矩阵响应中，已经不是运行态需要，而是过期展示合同。

### 2.2 当前仍要保留 registry 兼容

`permission-registry.ts` 中的 `menu.recruit` 历史登记本轮保留。

原因：

- 它只服务角色详情 / 编辑弹窗的历史权限可读展示
- 它不会重新参与路由或后端 controller 放通
- 若其它环境仍残留 `menu.recruit`，保留 registry 可避免编辑弹窗重新出现 unknown 噪音

## 3. 设计策略

### 3.1 后端矩阵合同收口

从以下位置移除 `hasRecruitMenu`：

- `AdminRoleRecruitGovernanceMatrixItemDTO`
- `AdminRoleServiceImpl#toRecruitGovernanceMatrixItem`

同时删除只为该字段存在的：

- `RECRUIT_MENU_PERMISSION`
- `menuPermissions` 读取逻辑

### 3.2 前端矩阵展示收口

从以下位置移除 `hasRecruitMenu`：

- `AdminRoleRecruitGovernanceMatrixItem`
- 招募矩阵“权限覆盖”列中的 `历史 menu.recruit` 标签
- 招募治理权限提示中针对“当前只配置了历史 menu.recruit”的特殊分支
- `PERMISSIONS.menu.recruit` 死常量

招募矩阵继续展示：

- 项目页
- 角色页
- 投递页
- 项目处置
- 角色处置
- 后台账号页历史耦合
- 页面 / 动作直授权缺口

### 3.3 不改权限树 registry

`permission-registry.ts` 继续保留：

- `menu.recruit`
- `招募治理菜单（历史登记）`

这不是运行时入口，而是历史数据的可读兼容层。

## 4. 验证策略

本轮验证分三层：

1. 静态构建：
   - `npm run type-check`
   - `npm run build`
   - `mvn -q -DskipTests compile`
2. 登录态 API：
   - `GET /admin/system/roles/recruit-governance-matrix`
   - 响应首项字段不再包含 `hasRecruitMenu`
3. 真实浏览器：
   - `/system/roles`
   - 招募矩阵不再出现 `历史 menu.recruit`
   - 页面无 console error

## 5. 风险与边界

### 5.1 已确认

- 当前 `hasRecruitMenu` 消费集中在招募矩阵 DTO / service / 前端类型 / `RolesView.vue`
- `menu.recruit` 不参与 runtime 放通

### 5.2 当前边界

- 本轮不删除 registry 历史登记
- 本轮不修改数据库
- 本轮不删除 `/recruit/*` hidden tooling
- 若后续确认所有目标环境都不再保存 `menu.recruit`，再另起 registry 历史登记退场切片
