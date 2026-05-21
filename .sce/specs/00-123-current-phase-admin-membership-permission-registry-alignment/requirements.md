# 00-123 当前阶段后台 membership 权限 registry 对齐（Current Phase Admin Membership Permission Registry Alignment）

> 状态：已完成 | 优先级：中 | 依赖：00-122 current-phase-admin-membership-legacy-menu-retirement、00-110 current-phase-admin-legacy-route-and-fallback-retirement-audit
> 记录目的：在 `00-122` 已退掉 `menu.membership` 历史菜单后，继续把后端仍真实消费的 membership 页面 / 动作权限补入前端 permission registry 与 permission tree，消除角色编辑弹窗中的“未登记权限”误报。

## 1. 背景

截至 `2026-04-23`：

- `00-122` 已完成 `menu.membership` 历史菜单退场
- 但在真实浏览器打开 `/system/roles` -> `编辑角色` 弹窗时，当前仍能看到以下权限出现在“未登记权限”区域：
  - `page.membership.benefits`
  - `page.membership.logs`
  - `action.membership.benefit.create`
  - `action.membership.benefit.edit`
  - `action.membership.benefit.enable`
  - `action.membership.benefit.disable`
  - `action.membership.product.edit`
  - `action.membership.product.enable`
  - `action.membership.product.disable`
  - `action.membership.product.sort`

同时已核实：

- 后端 `AdminMembershipController.java` 当前真实使用上述 `page.membership.* / action.membership.*`
- 前端 `permission-registry.ts` 当前只登记了：
  - `page.membership.products`
  - `page.membership.accounts`
  - `action.membership.product.create`
  - `action.membership.account.open / extend / close`
- `permissionTreeData` 的模块顺序当前仍来自 `adminMenus.map(...)`
- 当前 `adminMenus` 不含 membership 模块，因此即使部分 membership 权限已进入 registry，也不会进入权限树显示

当前判断：

- 这不是“删除权限”问题
- 是“前端 registry / permission tree 落后于后端真实权限合同”的对齐问题

## 2. 范围

### 2.1 本轮必须处理

- 新增独立 `00-123`
- 以 `AdminMembershipController.java` 为准，补齐前端 membership 页面 / 动作权限 registry
- 让 membership 模块进入 permission tree，可在角色编辑弹窗中被标准展示
- 确保 membership 权限不再落入“未登记权限”区域
- 做前端构建验证
- 做真实浏览器复核 `/system/roles` 编辑弹窗

### 2.2 本轮不处理

- 不恢复 `menu.membership`
- 不新增 membership 正式导航
- 不创建新的 membership 页面容器
- 不调整后端 membership controller 或数据库角色授权

## 3. 需求

### 3.1 registry 合同

- **R1** 必须以 `AdminMembershipController.java` 中真实出现的 `page.membership.* / action.membership.*` 为唯一权限来源，不得凭猜测扩写。
- **R2** 必须补齐前端 registry 中缺失的 membership 页面 / 动作权限文案。
- **R3** membership 模块必须进入 permission tree，但不能因此恢复 `menu.membership`。

### 3.2 体验合同

- **R4** `/system/roles` 编辑弹窗中的 membership 权限不应继续显示为“未登记权限”。

### 3.3 验证合同

- **R5** 必须通过 `npm run type-check` 与 `npm run build`。
- **R6** 必须基于真实浏览器复核角色编辑弹窗。
- **R7** 浏览器截图产物必须落到 `D:\XM\kaipai-team\output\playwright\00-123\`

## 4. 验收标准

- [x] 已新增独立 `00-123`
- [x] membership 页面 / 动作权限已按后端真实合同补齐到前端 registry
- [x] membership 模块已进入 permission tree
- [x] 角色编辑弹窗中 membership 权限不再显示为“未登记权限”
- [x] `type-check` 与 `build` 通过
- [x] 真实浏览器复核已完成并留档
- [x] README / mapping / CURRENT_CONTEXT / execution 已回填
