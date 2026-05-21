# 00-125 当前阶段后台 recruit 历史菜单 registry 对齐（Current Phase Admin Recruit Legacy Menu Registry Alignment）

> 状态：已完成 | 优先级：中 | 依赖：00-124 current-phase-admin-content-permission-registry-alignment、00-110 current-phase-admin-legacy-route-and-fallback-retirement-audit
> 记录目的：在 `00-124` 已把角色编辑弹窗中的 unknown 收到只剩 `menu.recruit` 后，继续明确它的真实边界，并把它作为“历史菜单登记”纳入前端 permission registry，消除最后 1 条 unknown，而不误改当前运行时放通边界。

## 1. 背景

截至 `2026-04-23`：

- `00-124` 已完成 content 权限 registry 对齐
- 当前 `/system/roles` 编辑弹窗中的 unknown 总量已从 `9` 降到 `1`
- 当前唯一剩余 unknown：
  - `menu.recruit`

本轮已进一步核实：

- `adminMenus` 中 `recruit` 组没有 `menuPermission`
- `router/index.ts` 中招募页只认：
  - `page.recruit.projects`
  - `page.recruit.roles`
  - `page.recruit.applies`
- `AdminRecruitController.java` 只认：
  - `page.recruit.*`
  - `action.recruit.*`
- 当前运行库 `ADMIN` 角色仍携带 `menu.recruit`
- `AdminRoleServiceImpl.java` / `RolesView.vue` 当前仍把它作为：
  - `hasRecruitMenu`
  - “历史 menu.recruit”
  的历史登记展示项

当前判断：

- `menu.recruit` 当前不参与 runtime 放通
- 但当前仍是角色数据中的历史登记项
- 因此当前更适合做 **registry 对齐**，而不是直接删角色数据

## 2. 范围

### 2.1 本轮必须处理

- 新增独立 `00-125`
- 把 `menu.recruit` 作为“历史菜单登记”补入前端 permission registry
- 确保 `/system/roles` 编辑弹窗中不再把 `menu.recruit` 误判为 unknown
- 做前端构建验证
- 做真实浏览器复核角色编辑弹窗

### 2.2 本轮不处理

- 不从运行库角色中删除 `menu.recruit`
- 不修改后端招募 controller 鉴权
- 不恢复 `menu.recruit` 为 runtime 放通条件
- 不修改招募矩阵 `hasRecruitMenu` 的历史展示逻辑

## 3. 需求

### 3.1 边界合同

- **R1** 必须明确 `menu.recruit` 当前只作为历史登记展示项，不得把它重新引回 runtime 放通。
- **R2** `menu.recruit` 在前端 registry 中的文案必须明确体现“历史”口径，避免用户误以为它仍控制访问。
- **R3** 本轮改动必须限定在前端 registry / tree 展示层，不改变后端鉴权合同。

### 3.2 验证合同

- **R4** `/system/roles` 编辑弹窗中的 unknown list 应降到 `0`。
- **R5** 必须通过 `npm run type-check` 与 `npm run build`。
- **R6** 必须基于真实浏览器复核角色编辑弹窗。
- **R7** 浏览器截图产物必须落到 `D:\XM\kaipai-team\output\playwright\00-125\`

## 4. 验收标准

- [x] 已新增独立 `00-125`
- [x] `menu.recruit` 已按历史菜单登记补入前端 registry
- [x] 角色编辑弹窗中的 unknown list 已清零
- [x] `type-check` 与 `build` 通过
- [x] 真实浏览器复核已完成并留档
- [x] README / mapping / CURRENT_CONTEXT / execution 已回填
