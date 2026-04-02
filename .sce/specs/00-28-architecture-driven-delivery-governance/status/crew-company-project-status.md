# 剧组档案、项目与角色管理链路状态回填

## 1. 归属切片

- `../design.md`
- `../slices/crew-company-project-recruit-capability-slice.md`
- `../execution/recruit/`

## 2. 当前判定

- 回填日期：`2026-04-03`
- 当前判定：`局部完成`
- 一句话结论：`kaipai-frontend` 剧组侧 `company/project/role` 已具备切真所需的最小接口与运行时开关，`kaipai-admin` 已具备项目 / 角色 / 投递真实治理页与状态处置动作，后端已在 `JDK 17` 基线下完成标准发布并用真实登录态样本验证 `company -> project -> role -> admin governance`；`2026-04-03` 已继续把招募治理角色矩阵上线并为当前启用中的 `ADMIN` 角色显式补齐 `menu/page/action.recruit.*`，因此 recruit 不再依赖 `page.system.admin-users` fallback，但小程序页面级证据与兼容层长期治理仍未补齐，所以当前仍判定为“剧组主线最小闭环已验证，长期治理未完成”。

## 3. 当前已确认事实

### 3.1 前端 / 小程序

- `kaipai-frontend/src/utils/runtime.ts` 已放开 `upload`、`company`、`project`、`role` 真接口能力
- `kaipai-frontend/src/api/company.ts` 已按 `/company`、`/company/mine` 对接
- `kaipai-frontend/src/utils/upload.ts` 已可直接走后端文件上传接口，满足剧组头像上传前置条件
- `kaipai-frontend/src/api/project.ts` 已按 `/project`、`/project/{id}`、`/project/mine`、`/project/list` 对接
- `kaipai-frontend/src/api/role.ts` 已按 `/role`、`/role/{id}`、`/role/project/{projectId}` 对接剧组写侧与项目角色列表
- 因此前端以下剧组页已具备切真条件：
  - `src/pages/company-profile/edit.vue`
  - `src/pages/project/create.vue`
  - `src/pages/project/role-create.vue`
  - `src/pages/home/index.vue` 的剧组项目总览与项目角色展开

### 3.2 后端 / 数据

- `kaipaile-server/src/main/java/com/kaipai/module/controller/company/CompanyProfileController.java` 已提供 `/company`、`/company/mine`、`/company/{userId}`
- `kaipaile-server/src/main/java/com/kaipai/module/controller/recruit/ProjectController.java` 已提供 `/project`、`/project/{projectId}`、`/project/mine`、`/project/list`
- `kaipaile-server/src/main/java/com/kaipai/module/controller/recruit/RecruitPostController.java` 已扩展 `POST /role`、`PUT /role/{roleId}`、`DELETE /role/{roleId}`、`GET /role/project/{projectId}`
- `kaipaile-server/src/main/java/com/kaipai/module/controller/admin/recruit/AdminRecruitController.java` 已提供 `POST /admin/recruit/projects/{id}/status`、`POST /admin/recruit/roles/{id}/status`
- `kaipaile-server/src/main/java/com/kaipai/module/server/recruit/service/impl/MiniProgramRecruitServiceImpl.java` 已用兼容层方式落盘：
  - 项目元数据写入 `company_profile.extendedField`
  - 角色与项目关联写入 `recruit_post.extendedField`
- `kaipaile-server/src/main/java/com/kaipai/module/server/recruit/service/impl/AdminRecruitGovernanceServiceImpl.java` 已补最小治理规则：
  - 项目结束会同步收口该项目下仍未结束的角色
  - 恢复角色招募前会校验关联项目仍为进行中
  - 项目 / 角色状态治理动作已写入 `admin_operation_log`
- `kaipaile-server/src/main/java/com/kaipai/module/server/company/service/impl/CompanyProfileServiceImpl.java` 已补齐公司档案读写，且 `profile(userId)` 不再因读取动作落库创建空档案

### 3.3 后台治理

- `kaipai-admin/src/views/recruit/ProjectsView.vue` 已接入 `/api/admin/recruit/projects`，并支持恢复进行 / 结束项目
- `kaipai-admin/src/views/recruit/RolesView.vue` 已接入 `/api/admin/recruit/roles`，并支持恢复招募 / 暂停 / 结束角色
- `kaipai-admin/src/views/recruit/AppliesView.vue` 已接入 `/api/admin/recruit/applies`，可查看投递记录基础列表
- `kaipai-admin/src/constants/permission.ts`、`permission-registry.ts` 已登记 `action.recruit.project.status`、`action.recruit.role.status`
- `2026-04-03 02:11` 已按 `00-29` 标准 `admin-only` 脚本完成线上发布，记录为 `.sce/runbooks/backend-admin-release/records/20260403-021050-admin-only-recruit-governance-pages.md`
- `2026-04-03 02:25` / `02:26` 已继续按 `00-29` 标准脚本完成角色矩阵相关 `backend-only` 与 `admin-only` 发布，记录为：
  - `.sce/runbooks/backend-admin-release/records/20260403-022433-backend-only-recruit-role-matrix.md`
  - `.sce/runbooks/backend-admin-release/records/20260403-022552-admin-only-recruit-role-matrix.md`
- `kaipai-admin/src/views/system/RolesView.vue` 已上线招募治理授权矩阵与建议权限包
- `GET /api/admin/system/roles/recruit-governance-matrix` 当前返回 `200`，并显示 `recruitReadyRoleCount=1`、`fallbackRoleCount=0`、`canRetireFallback=true`
- 当前后台已具备“先看见真实数据 + 最小状态治理 + 真实角色矩阵收口”的入口，但仍未补完整项目编辑、审核流和更细运营处置动作

### 3.4 联调现状

- 小程序前端类型检查已通过
- 后台管理端构建已通过
- 后端在本机 `JDK 17` 基线下已通过源码编译，并已按 `00-29` 标准脚本完成线上发布
- 已通过真实账号、真实 token、真实数据样本完成 `company -> project -> role -> admin governance` 接口级联调，样本记录为 `execution/recruit/samples/20260403-020306-recruit-fixes-post-company-fix/summary.md`
- `2026-04-03 02:12` 已补做管理端线上业务 smoke：
  - `GET /api/admin/recruit/projects?pageNo=1&pageSize=2&keyword=` -> `200`
  - `GET /api/admin/recruit/roles?pageNo=1&pageSize=2&keyword=` -> `200`
  - `GET /api/admin/recruit/applies?pageNo=1&pageSize=2&keyword=` -> `200`
  - `/recruit/projects`、`/recruit/roles`、`/recruit/applies` 均返回当前 SPA 静态入口
- `2026-04-03` 当前再次回读公网状态：
  - `POST /api/admin/auth/login` 回包已包含 `menu.recruit`
  - 同一登录态已包含 `page.recruit.projects`、`page.recruit.roles`、`page.recruit.applies`
  - 同一登录态已包含 `action.recruit.project.status`、`action.recruit.role.status`
  - `GET /api/admin/system/roles/recruit-governance-matrix` -> `200`，`ADMIN.rolloutStage='recruit_ready'`
  - `GET /api/admin/recruit/roles?pageNo=1&pageSize=1&keyword=` -> `200`
- 当前仍未补齐小程序页面层面的真实截图 / 交互证据

## 4. 联调结论

- 当前是否具备三端联调条件：`部分具备`
- 已确认走通的链路：
  - 剧组档案读取 / 保存接口已存在
  - 项目创建 / 查询 / 我的项目列表接口已存在
  - 角色创建 / 查询 / 按项目查询接口已存在
  - 小程序运行时已不再强制把 `company/project/role` 锁在 mock
  - 后台已能查看项目 / 角色 / 投递三张真实聚合列表
  - 后台已能执行项目状态校准、角色状态校准，并带最小审计日志
- 当前不能宣告闭环的原因：
  - 小程序页面级真实截图 / 交互证据仍未补齐
  - `project` 仍运行在 `company_profile.extendedField.projects` 兼容层，不适合把当前最小闭环误判成长期架构完成
  - 删除 / 变更后的更完整级联治理、运营审计与回滚策略仍未补齐

## 5. 验收判断

| 闭环条件 | 状态 | 说明 |
|----------|------|------|
| 上位 Spec 已存在并对齐 | 已满足 | 以 `00-27` 的小程序架构和 `00-28` 的架构驱动交付治理为准 |
| 数据模型、接口、状态流转清楚 | 部分满足 | 兼容层方案已定，但仍是 `company_profile/recruit_post` 复用，不是独立项目域 |
| 后台治理入口可操作 | 已满足 | 已补项目 / 角色 / 投递真实列表，以及项目状态 / 角色状态最小治理动作 |
| 小程序或前台用户侧落点可验证 | 已满足 | 页面调用路径与运行时能力已切真 |
| 关键日志、权限、限额或回滚约束已接入 | 部分满足 | 项目 / 角色状态治理已接入 `admin_operation_log`，且当前启用角色已完成 recruit 显式授权；但回滚和更复杂处置仍未补齐 |
| 文档、映射表、验证记录已回填 | 已满足 | 已新增本状态文档并记录验证方式 |

## 6. 当前阻塞项

- 小程序页面级真实截图 / 交互证据仍未补齐
- 兼容层长期仍需评估是否沉淀为独立 `project` 域模型
- 后续新增后台角色仍需按 `execution/recruit/role-authorization-closure.md` 继续显式分配 recruit 权限，不能回退到 fallback 思路

## 7. 下一轮最小动作

1. 启动真实后端与小程序，用剧组账号走通 `档案保存 -> 创建项目 -> 创建角色 -> 首页展开角色 -> 投递管理`
2. 补后台页面级截图 / 浏览器交互证据，避免当前只停留在接口 smoke + SPA 入口回读
3. 把当前 `ADMIN` 角色已完成的显式 recruit 授权沉淀为标准角色包与发布后校验步骤，约束后续新增角色
4. 评估 `project` 独立建模与兼容层迁移边界，避免后续继续把项目事实源分散在扩展字段里

## 8. 回填记录

### 2026-04-02

- 当前判定：`局部完成`
- 备注：补齐了剧组侧 `company/project/role` 最小真实接口，后台已从项目 / 角色 / 投递只读治理页推进到项目状态 / 角色状态最小治理动作；验证记录为 `kaipaile-server` 在 `JDK 21` 下 `mvn -q -DskipTests compile` 通过、`kaipai-frontend` `npm run type-check` 通过、`kaipai-admin` `npm run build` 通过。

### 2026-04-03

- 当前判定：`局部完成`
- 备注：
  - 已新增 spec 内标准真实样本脚本：`execution/recruit/run-authenticated-recruit-sample.py`
  - 已按 `00-29` 两次标准 `backend-only` 发布收口剧组主线问题，最新记录为 `20260403-020152-backend-only-recruit-company-save-fix.md`
  - 最新真实样本 `20260403-020306-recruit-fixes-post-company-fix` 已确认：
    - `PUT /api/company` 保存成功
    - `POST /api/project`、`POST /api/role`、`GET /api/role/project/{projectId}` 通过
    - 后台结束项目会同步收口角色，恢复项目不会自动恢复角色，项目结束时恢复角色会被正确拦截
  - 本轮已修复的真实后端问题包括：
    - 项目状态治理写副本未落库
    - 公司资料保存时 `user.update_user_name` 为空导致数据库拒绝更新
    - 角色搜索项目映射与总数字段异常
  - 随后已按 `00-29` 标准 `admin-only` 脚本完成管理端线上发布，记录为 `20260403-021050-admin-only-recruit-governance-pages.md`
  - 发布后已补做线上治理页业务 smoke：
    - 登录态 `GET /api/admin/recruit/projects|roles|applies` 均返回 `200`
    - `/recruit/projects`、`/recruit/roles`、`/recruit/applies` 均返回当前 SPA 静态入口
  - 同日后续已继续收口角色矩阵：`GET /api/admin/system/roles/recruit-governance-matrix` 当前返回 `recruitReadyRoleCount=1`、`fallbackRoleCount=0`、`canRetireFallback=true`
  - 当前启用中的 `ADMIN` 角色登录回包已显式包含 `menu.recruit`、`page.recruit.*` 与 `action.recruit.*`
  - 因此 recruit 当前已不再依赖 `page.system.admin-users` fallback；后续重点已切到页面层证据与兼容层长期治理
