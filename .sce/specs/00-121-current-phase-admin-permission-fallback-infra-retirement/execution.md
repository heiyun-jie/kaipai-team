# 00-121 执行记录

## 1. 当前状态

- 已重新读取 `C:\Users\33340\.codex\memories\user-global-memory.md`
- 已核对 `CURRENT_CONTEXT.md`、`README.md`、`spec-code-mapping.md`、`00-110`、`00-114`、`00-115`、`00-116`、`00-120`
- 已按 `00-121` 主线先证明前端权限 fallback 基础设施已无运行时消费者，再做最小退场和浏览器 smoke

## 2. 删除前证据

### 2.1 当前前端权限 fallback 基础设施已无实际消费者

本轮通过 `rg` 直接核对：

- 仍保留残留入口的文件：
  - `src/utils/permission.ts`
  - `src/stores/permission.ts`
  - `src/router/index.ts`
  - `src/types/admin.ts`
  - `src/types/router.d.ts`
  - `src/components/business/PermissionButton.vue`
- 当前未命中任何实际消费者：
  - `pagePermissionFallbacks`
  - `fallbackPermissions`
  - `permissionStore.getAccessMode(...)`

补充核对结果：

- route meta 中已无 `pagePermissionFallbacks` 配置项
- 页面按钮调用中已无传入 `fallbackPermissions` 的使用点

当前判断：

- 这层 fallback 已经不是当前运行时放通链路
- 可作为 dead infra 进入前端退场

依据：

- 全仓前端源码 `rg` 命中结果

置信度：

- 高

不确定边界：

- 本判断覆盖 `kaipai-admin/src` 当前源码
- 不外推到历史提交或其它仓分支

### 2.2 仍有过期用户可见文案

已核实：

- `D:\XM\kaipai-team\kaipai-admin\src\constants\admin-information-architecture.ts`
  - `/recruit/*` 仍写着“仍保留 admin-users fallback 兼容链路”
- `D:\XM\kaipai-team\kaipai-admin\src\views\system\RolesView.vue`
  - 矩阵提示仍写着“可继续评估清理 fallback 字段命名残留”

当前判断：

- 这些文案已落后于 `00-114 / 00-115 / 00-116`
- 需要随本轮一起清理

## 3. 本轮实施

### 3.1 前端权限 fallback 基础设施退场

已修改：

- `D:\XM\kaipai-team\kaipai-admin\src\utils\permission.ts`
  - 删除 `PermissionAccessMode`
  - 删除 `getPermissionAccessMode(...)`
  - `hasPermission(...)` 改为只按 direct permission 判断
  - `filterMenus(...)` 不再承接 `pagePermissionFallbacks`
- `D:\XM\kaipai-team\kaipai-admin\src\stores\permission.ts`
  - 删除 `resolveFallbackPermissions(...)`
  - 删除 `getAccessMode(...)`
  - `canAccess / hasAction / hasPage` 改为 direct-only
- `D:\XM\kaipai-team\kaipai-admin\src\router\index.ts`
  - 删除 `pagePermissionFallbacks` 读取
- `D:\XM\kaipai-team\kaipai-admin\src\types\admin.ts`
  - 删除 `pagePermissionFallbacks`
- `D:\XM\kaipai-team\kaipai-admin\src\types\router.d.ts`
  - 删除 `pagePermissionFallbacks`
- `D:\XM\kaipai-team\kaipai-admin\src\components\business\PermissionButton.vue`
  - 删除 `fallbackPermissions` prop

### 3.2 过期文案收口

已修改：

- `D:\XM\kaipai-team\kaipai-admin\src\constants\admin-information-architecture.ts`
  - `/recruit/*` tooling 描述改为“当前已按独立页面 / 动作权限直连放通”
- `D:\XM\kaipai-team\kaipai-admin\src\views\system\RolesView.vue`
  - AI / 招募矩阵已清零时的提示改为“沿独立页面 / 动作权限模型继续维护”

## 4. 验证结果

### 4.1 构建验证

命令：

- `cd D:\XM\kaipai-team\kaipai-admin && npm run type-check`
- `cd D:\XM\kaipai-team\kaipai-admin && npm run build`

结果：

- `type-check`：通过
- `build`：通过

保留告警：

- Sass legacy JS API deprecation
- Vite chunk size warning

### 4.2 真实浏览器 smoke

已使用 Playwright CLI 登录 `http://127.0.0.1:5100/login`，并复核：

- 正式页：`/system/settings`
- hidden tooling 页：`/recruit/projects`

当前已确认：

- `system/settings` 可正常访问
- `recruit/projects` 可正常访问
- `recruit/projects` 顶部说明已显示为：
  - “当前页面属于招募治理工具，当前已按独立页面 / 动作权限直连放通，不属于主导航。”
- 浏览器 console 当前无错误 / 警告输出

截图证据：

- `D:\XM\kaipai-team\output\playwright\00-121\system-settings-direct-after.png`
- `D:\XM\kaipai-team\output\playwright\00-121\recruit-projects-direct-after.png`

依据：

- 真实浏览器快照
- 页面截图

置信度：

- 高

不确定边界：

- 当前 smoke 只覆盖 `admin` 账号
- 本轮只验证权限主链未被破坏，不等于对全部 hidden tooling 页做完整权限回归

## 5. 文档回填

本轮已回填：

- `D:\XM\kaipai-team\.sce\specs\00-121-current-phase-admin-permission-fallback-infra-retirement\requirements.md`
- `D:\XM\kaipai-team\.sce\specs\00-121-current-phase-admin-permission-fallback-infra-retirement\design.md`
- `D:\XM\kaipai-team\.sce\specs\00-121-current-phase-admin-permission-fallback-infra-retirement\tasks.md`
- `D:\XM\kaipai-team\.sce\specs\00-121-current-phase-admin-permission-fallback-infra-retirement\execution.md`
- `D:\XM\kaipai-team\.sce\specs\README.md`
- `D:\XM\kaipai-team\.sce\specs\spec-code-mapping.md`
- `D:\XM\kaipai-team\.sce\steering\CURRENT_CONTEXT.md`

## 6. 结论

`00-121` 已完成本轮目标：

- 当前前端权限 fallback 基础设施已确认无运行时消费者，并已退场
- 招募治理 tooling 描述与角色矩阵提示已和 direct-authority 当前事实对齐
- 构建验证与真实浏览器 smoke 均通过
