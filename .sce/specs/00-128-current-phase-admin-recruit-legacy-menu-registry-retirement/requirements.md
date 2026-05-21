# 00-128 当前阶段后台 recruit 历史菜单 registry 退场（Current Phase Admin Recruit Legacy Menu Registry Retirement）

> 状态：已完成 | 优先级：中 | 依赖：00-127 current-phase-admin-recruit-legacy-menu-display-retirement、00-126 current-phase-admin-recruit-legacy-menu-runtime-retirement
> 记录目的：在 `00-127` 已确认招募矩阵 live contract 与本机 dev 运行态都不再暴露 `menu.recruit` 后，继续把前端 permission registry 中最后一条 `menu.recruit` 历史登记做成独立最小退场切片。

## 1. 背景

截至 `2026-04-23`：

- `00-125` 曾把 `menu.recruit` 作为历史菜单登记补入前端 permission registry，用于消除角色编辑弹窗最后 1 条 unknown
- `00-126` 已把本机 dev 运行库中的 `menu.recruit` 从角色数据里清理掉
- `00-127` 已把招募矩阵中的 `hasRecruitMenu` / `历史 menu.recruit` 展示合同退场

本轮重新核实到：

- 当前 live `GET /admin/auth/me` 返回的 `menuPermissions` 不包含 `menu.recruit`
- 当前 live `GET /admin/system/roles/1` 返回的 `menuPermissions` 不包含 `menu.recruit`
- 当前业务代码中 `menu.recruit` 只剩：
  - `kaipai-admin/src/constants/permission-registry.ts`
  - `historicalMenuRegistry`
  - `招募治理菜单（历史登记）`
- 当前前后端运行态代码已无其它消费者

当前判断：

- 在当前本机 dev 运行态口径下，`menu.recruit` 已经不再是 runtime 数据，也不再是展示合同
- 因此前端 permission registry 中的历史登记，已经成为当前主线里最后一条可独立退场的残留

## 2. 范围

### 2.1 本轮必须处理

- 新增独立 `00-128`
- 删除 `permission-registry.ts` 中的 `historicalMenuRegistry`
- 删除 `menu.recruit` 的历史登记项
- 确保当前本机 `/system/roles` 编辑弹窗 unknown list 继续保持 `0`
- 通过前端 `type-check` / `build`
- 真实浏览器复核 `/system/roles` 编辑弹窗

### 2.2 本轮不处理

- 不修改后端 controller / DTO / service
- 不修改数据库
- 不修改其它历史菜单
- 不对其它环境数据库是否仍残留 `menu.recruit` 作扩展处理

## 3. 需求

### 3.1 退场门禁

- **R1** 只有在当前本机 live session 与角色详情都不再返回 `menu.recruit` 时，才允许删除前端 registry 中的历史登记。
- **R2** 若 `historicalMenuRegistry` 在删掉 `menu.recruit` 后为空，应一并删除该中间数组，而不是保留空壳。
- **R3** 本轮只能删除当前已确认无人消费的 `menu.recruit` 历史登记，不得顺手扩大到其它模块。

### 3.2 运行态要求

- **R4** 当前本机 `/system/roles` 编辑弹窗 unknown list 必须继续保持 `0`。
- **R5** 当前 recruit 模块权限树应继续保留页面 / 动作权限节点，不得因为删除历史菜单登记而破坏真实权限编排。

### 3.3 验证要求

- **R6** 必须通过：
  - `kaipai-admin` 的 `npm run type-check`
  - `kaipai-admin` 的 `npm run build`
- **R7** 必须基于真实浏览器复核 `/system/roles` 编辑弹窗，并输出截图到 `D:\XM\kaipai-team\output\playwright\00-128\`

## 4. 验收标准

- [x] 已新增独立 `00-128`
- [x] `historicalMenuRegistry` 已删除
- [x] `menu.recruit` 历史登记项已删除
- [x] 当前本机角色编辑弹窗 unknown list 仍为 `0`
- [x] recruit 模块页面 / 动作权限树仍正常可见
- [x] 前端 `type-check` / `build` 通过
- [x] 真实浏览器复核已完成并留档
- [x] README / mapping / CURRENT_CONTEXT / execution 已回填
