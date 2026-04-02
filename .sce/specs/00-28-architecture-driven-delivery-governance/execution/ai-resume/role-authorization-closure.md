# AI 简历治理角色授权收口说明

## 1. 文档目的

- 把 AI 简历治理从“已定义独立权限码”推进到“可在真实角色分配流程中落地”
- 明确当前代码里角色权限树、角色保存、会话权限聚合的真实数据流
- 给出建议角色包、环境收口步骤与 `operation-logs` fallback 下线条件

## 2. 当前代码事实

### 2.1 角色管理页权限树数据源

- `kaipai-admin/src/views/system/RolesView.vue`
  - 角色新建 / 编辑使用 `PermissionTreeEditor`
  - 角色列表页已新增 AI 授权矩阵，直接盘点 fallback 依赖角色
- `kaipai-admin/src/components/forms/PermissionTreeEditor.vue`
  - 权限树展示、勾选、分类拆分都在前端完成
- `kaipai-admin/src/constants/permission-registry.ts`
  - 权限树数据来自本地 registry
  - `page.system.ai-resume-governance`
  - `action.system.ai-resume.review`
  - `action.system.ai-resume.resolve`
  - 均已登记到 `system` 模块

### 2.2 角色保存与回显数据源

- `kaipai-admin/src/api/system.ts`
  - 角色管理页通过 `/admin/system/roles` 读写角色
  - 角色管理页通过 `/admin/system/roles/ai-governance-matrix` 拉取 AI 授权矩阵
- `kaipaile-server/src/main/java/com/kaipai/module/controller/admin/system/AdminSystemController.java`
  - 角色列表、详情、创建、编辑、复制、启停用，以及 AI 授权矩阵均走真实后端接口
- `kaipaile-server/src/main/java/com/kaipai/module/server/system/service/impl/AdminRoleServiceImpl.java`
  - 角色的 `menuPermissionsJson`、`pagePermissionsJson`、`actionPermissionsJson` 会按原样落库并回显
  - 会额外汇总角色是否补齐 AI 页面 / 动作权限、是否仍依赖 fallback、绑定账号数与 fallback 下线判断

### 2.3 会话权限聚合

- `kaipaile-server/src/main/java/com/kaipai/module/server/adminauth/service/impl/AdminAuthServiceImpl.java`
  - 登录态会把角色的菜单 / 页面 / 动作权限聚合到当前后台会话
  - 因此只要角色里配置了 AI 新权限码，登录后的真实后台账号就能拿到对应 authority

## 3. 当前结论

- AI 新页面 / 动作权限已经能在真实角色分配流程中出现
- `2026-04-03 07:21` 已通过标准样本 `samples/20260403-072120-continue-ai-role-closure/summary.md` 把目标环境 `ADMIN` 从 `fallback_only` 推进到 `ai_ready`
- 同一样本已确认：
  - `aiReadyRoleCount=1`
  - `fallbackRoleCount=0`
  - `canRetireFallback=true`
  - 重新登录后的后台会话已拿到 `page.system.ai-resume-governance`、`action.system.ai-resume.review`、`action.system.ai-resume.resolve`
- 仓内已移除 `page.system.operation-logs` 对 AI 治理入口和动作的权限兜底，但目标环境仍需按 runbook 发布并补一轮退场后复验；`page.system.operation-logs` 不应再作为新授权入口

## 4. 建议角色包

| 角色包 | 适用对象 | 菜单权限 | 页面权限 | 动作权限 |
|--------|----------|----------|----------|----------|
| AI 治理只读 | 运营查看、风控查看、问题排查 | `menu.system` | `page.system.ai-resume-governance` | 无 |
| AI 治理处置 | 运营处置、风控处置 | `menu.system` | `page.system.ai-resume-governance` | `action.system.ai-resume.review`、`action.system.ai-resume.resolve` |

补充说明：

- 若账号需要继续查看系统操作日志，可额外保留 `page.system.operation-logs`
- 但这项权限不应再被当作 AI 治理入口的替代品

## 5. 环境收口步骤

1. 先在角色管理页 AI 授权矩阵中确认哪些角色处于 `fallback_only / compat_transition / partial_ai`
2. 为目标角色套用“AI 治理只读”或“AI 治理处置”权限包
3. 在后台账号管理页把目标角色绑定到真实后台账号
4. 使用该账号重新登录后台，确认当前会话返回了独立 AI 页面 / 动作权限
5. 验证 AI 治理页入口、失败样本处理按钮、治理动作审计是否与角色范围一致
6. 把验证结果回填到 `status/ai-resume-status.md`

## 5.1 最新标准样本结果

- 样本脚本：`run-ai-role-authorization-closure.py`
- 样本目录：`samples/20260403-072120-continue-ai-role-closure/summary.md`
- 收口结果：
  - `matrix-before-detected`：`ADMIN` 初始阶段为 `fallback_only`
  - `role-detail-updated`：AI 页面 / review / resolve 三枚权限已写入角色详情
  - `matrix-after-ai-ready`：角色阶段变为 `ai_ready`
  - `fallback-retired`：矩阵聚合变为 `aiReadyRoleCount=1 / fallbackRoleCount=0 / canRetireFallback=true`
  - `session-permissions-refreshed`：重新登录后后台会话已拿到独立 AI 页面 / 动作权限
  - `role-update-operation-log-visible`：可按 `X-Request-Id=20260403-072120-continue-ai-role-closure-update-role` 回看角色变更审计

## 6. Fallback 下线条件

只有同时满足以下条件，才建议删除 `page.system.operation-logs` 对 AI 治理的兼容兜底：

1. 目标环境里至少一组启用中的角色已显式配置 `page.system.ai-resume-governance`
2. 需要人工处置的角色已显式配置 `action.system.ai-resume.review` 与 `action.system.ai-resume.resolve`
3. 已确认不再存在“仅靠 `page.system.operation-logs` 才能进入 AI 治理页”的后台账号
4. 已完成一次真实账号登录验证，并确认当前会话权限中出现独立 AI 权限码
5. 已完成一次治理动作验证，并能在 AI 治理页回看到对应审计日志

## 7. 下线时需要一起改动的文件

- `kaipai-admin/src/constants/menus.ts`
- `kaipai-admin/src/router/index.ts`
- `kaipai-admin/src/views/system/AiResumeGovernanceView.vue`
- `kaipaile-server/src/main/java/com/kaipai/module/controller/admin/ai/AdminAiResumeController.java`
- `status/ai-resume-status.md`

## 8. 本轮新增支撑物

- `kaipai-admin/src/views/system/RolesView.vue`
  - 已补 AI 授权矩阵与 AI 治理建议授权包，减少手工检索权限码的操作成本
- `kaipaile-server/src/main/java/com/kaipai/module/server/system/service/impl/AdminRoleServiceImpl.java`
  - 已补 `/admin/system/roles/ai-governance-matrix` 汇总，直接产出角色迁移阶段、绑定账号数与 fallback 下线判断
- 本文档
  - 作为角色矩阵收口与 fallback 下线的统一说明
