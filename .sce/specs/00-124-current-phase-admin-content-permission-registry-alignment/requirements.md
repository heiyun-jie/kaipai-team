# 00-124 当前阶段后台 content 权限 registry 对齐（Current Phase Admin Content Permission Registry Alignment）

> 状态：已完成 | 优先级：中 | 依赖：00-123 current-phase-admin-membership-permission-registry-alignment、00-110 current-phase-admin-legacy-route-and-fallback-retirement-audit
> 记录目的：在 `00-123` 已完成 membership 权限 registry 对齐后，继续把角色编辑弹窗中剩余的 content 真实权限补齐到前端 permission registry，消除这批 unknown 权限误报。

## 1. 背景

截至 `2026-04-23`：

- `00-123` 已完成 membership 页面 / 动作权限 registry 对齐
- 当前 `/system/roles` 编辑弹窗的 unknown list 已从 `19` 降到 `9`

剩余 unknown 权限中，当前已核实有 **8 个** 属于 content 真实权限：

- `page.content.publish-logs`
- `page.content.share-artifacts`
- `page.content.theme-tokens`
- `action.content.artifact.edit`
- `action.content.template.disable`
- `action.content.template.enable`
- `action.content.template.sort`
- `action.content.theme.edit`

同时已核实：

- 上述 8 个权限均被后端 `AdminContentController.java` 真实消费
- 前端 `permission-registry.ts` 当前仍未完整登记这批权限
- `TemplatesView.vue` 已直接使用：
  - `action.content.template.enable`
  - `action.content.template.disable`

当前判断：

- 这批 content 权限不是 dead code
- 是前端权限 registry 落后于后端真实合同

## 2. 范围

### 2.1 本轮必须处理

- 新增独立 `00-124`
- 以 `AdminContentController.java` 为准，补齐 content 页面 / 动作权限 registry
- 必要时同步补齐 `PERMISSIONS` 常量中已经被页面直接使用或应由权限合同承接的 content 权限
- 做前端构建验证
- 做真实浏览器复核 `/system/roles` 编辑弹窗，确认 content 权限不再显示为 unknown

### 2.2 本轮不处理

- 不处理 `menu.recruit`
- 不新增 content 隐藏页容器
- 不恢复 content 正式导航
- 不修改后端 content controller

## 3. 需求

### 3.1 权限合同

- **R1** 必须以 `AdminContentController.java` 中真实出现的 content 权限为唯一事实源，不得凭猜测扩写。
- **R2** 前端 registry 必须补齐这批 content 页面 / 动作权限文案。
- **R3** 已被页面直接使用的 content 权限字符串，若当前仍以裸字符串存在，应优先收口到 `PERMISSIONS` 常量。

### 3.2 验证合同

- **R4** `/system/roles` 编辑弹窗中的 content 权限不应继续显示为 unknown。
- **R5** 必须通过 `npm run type-check` 与 `npm run build`。
- **R6** 必须基于真实浏览器复核角色编辑弹窗。
- **R7** 浏览器截图产物必须落到 `D:\XM\kaipai-team\output\playwright\00-124\`

## 4. 验收标准

- [x] 已新增独立 `00-124`
- [x] content 页面 / 动作权限已按后端真实合同补齐到前端 registry
- [x] 相关 content 权限常量已按最小范围收口
- [x] 角色编辑弹窗中 content 权限不再显示为 unknown
- [x] `type-check` 与 `build` 通过
- [x] 真实浏览器复核已完成并留档
- [x] README / mapping / CURRENT_CONTEXT / execution 已回填
