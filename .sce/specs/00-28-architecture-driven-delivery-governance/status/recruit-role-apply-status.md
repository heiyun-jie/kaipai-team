# 招募角色与投递链路状态回填

## 1. 当前判定

- 回填日期：`2026-04-02`
- 当前判定：`局部完成`
- 一句话结论：演员端首页角色列表、角色详情、投递确认、我的投递与投递详情所依赖的 `role/apply` 最小后端接口已补齐，`kaipai-frontend` 也已把角色读取与投递切到真接口；相邻切片中的剧组侧 `company/project/role` 和后台最小状态治理也已接上，但真实环境联调仍未完成，所以当前仍不能误判成小程序整站都已闭环。

## 2. 当前已确认事实

### 2.1 小程序前端

- `kaipai-frontend/src/utils/runtime.ts` 已新增 `roleRead` 能力并放开 `apply` 真接口
- `kaipai-frontend/src/api/role.ts` 已把 `getRole / searchRoles` 切到 `roleRead` 真接口分支
- `kaipai-frontend/src/api/apply.ts` 当前会随 `apply` 能力走真接口
- 因此前端以下页面已具备消费真实 `role/apply` 的最小条件：
  - `src/pages/home/index.vue` 的演员端角色列表
  - `src/pages/role-detail/index.vue`
  - `src/pages/apply-confirm/index.vue`
  - `src/pages/my-applies/index.vue`
  - `src/pages/apply-detail/index.vue`

### 2.2 后端服务

- `kaipaile-server/src/main/java/com/kaipai/module/controller/recruit/RecruitPostController.java` 已改为提供 `/role/search`、`/role/{id}` 最小演员端接口
- `kaipaile-server/src/main/java/com/kaipai/module/controller/recruit/RecruitApplyController.java` 已改为提供 `/apply`、`/apply/mine`、`/apply/{id}`、`/apply/role/{roleId}`、`/apply/{id}/approve`、`/apply/{id}/reject`、`DELETE /apply/{id}`
- `kaipaile-server/src/main/java/com/kaipai/module/server/recruit/service/impl/RecruitPostServiceImpl.java` 已把 `recruit_post + company_profile + user` 组装成前端需要的 `Role + Project + Company` 最小读模型
- `kaipaile-server/src/main/java/com/kaipai/module/server/recruit/service/impl/RecruitApplyServiceImpl.java` 已补齐提交投递、我的投递、角色投递列表、通过 / 拒绝 / 取消、详情与权限校验

## 3. 当前边界

- 当前已切真的只是演员主线 `roleRead + apply`
- 当前仍未切真的主要是：
  - `project`
  - `company`
- 当前剧组侧 `company/project/role` 写链路与后台最小状态治理入口已转入 `crew-company-project-status.md` 单独跟踪，不再在本状态页重复判定
- 因为后端当前没有独立 `project` 表，所以这轮没有强行把 `project` 与 `recruit_post` 拆成两套事实源

## 4. 验证记录

- `kaipaile-server`：`mvn -q -DskipTests compile` 通过
- `kaipai-frontend`：`npm run type-check` 通过
- `kaipai-admin`：`npm run build` 通过（招募治理页已补项目 / 角色状态校准动作）

## 5. 下一轮最小动作

1. 补一轮真实环境联调，确认演员端 `search -> detail -> submit -> my-applies` 真实可用
2. 用后台最小状态治理动作回归一次演员端结果，确认项目 / 角色状态变化会真实影响角色可见性
3. 决定剧组侧是继续沿 `recruit_post` 做聚合式 `project` 视图，还是先补独立项目域模型，再切 `project/company`
4. 继续把演员端真实联调与剧组侧写链路、后台最小治理分开追踪，避免把“演员读链路已通”误写成“小程序整站已闭环”

## 6. 回填记录

### 2026-04-03

- 当前判定：`局部完成`
- 备注：
  - 已继续把 recruit 切片按“真实链路先稳定”推进，而不是回到页面 mock 修补：`kaipai-admin/src/api/recruit.ts` 已对项目 / 角色 / 投递三张治理页统一补 query sanitization，过滤 `undefined / null / '' / NaN`，避免继续把无效筛选值带到 `/admin/recruit/*`
  - `kaipai-frontend/src/api/role.ts` 已补演员端角色搜索参数收口，明确过滤字符串 `'undefined'` 与空筛选值，避免再次出现 `/api/role/search?...&minAge=undefined&maxAge=undefined` 这种 400
  - `kaipaile-server/.../AdminRecruitGovernanceServiceImpl.java` 已补 legacy 空值防守：`company_profile.extendedField.projects` 中若存在 `null` 项，不再让后台聚合列表或项目状态动作直接踩空；`RoleExtraDTO.tags` 与 `CompanyProfileExtrasDTO.projects` 也已补齐非空兜底
  - 同日重新探测线上运行时后发现，当前真实环境结论已发生变化，不能继续沿用 `2026-04-02` 的联通结论：`POST http://101.43.57.62/api/admin/auth/login` 当前返回 `500`，未携带 token 的 `GET /api/role/search` 当前直接返回 `401`
  - 因此 recruit 当前主阻塞已经从“页面是否还在 mock”切到“当前线上运行时是否与昨日验证样本一致”；下一步应先按 00-29 发布治理把本轮 recruit 修复发到目标环境，再重新跑 `admin projects/roles/applies` 与演员端 `role/apply` 的真实样本

### 2026-04-03（二次回填）

- 当前判定：`局部完成`
- 备注：
  - 已按 `00-29` 新增的 `backend-only` 标准发布链路完成真实后端重发，发布记录为 `20260403-013415-backend-only-auth-runtime-check-final.md`
  - 重发后公网回读结果已从上午的 `500` 收敛为：
    - `POST http://101.43.57.62/api/admin/auth/login` -> `200`
    - 未携带 token 的 `GET /api/admin/recruit/roles?pageNo=1&pageSize=1&keyword=` -> `401`
    - 未携带 token 的 `GET /api/role/search?page=1&size=1&keyword=&gender=` -> `401`
  - 这说明当前 recruit 线上主风险已不再是“后端异常 500”，而是“需要按真实鉴权前置补带 token 样本”，以及继续确认后台治理页与演员端读链路在已登录场景下是否返回正确业务数据

### 2026-04-03（三次回填）

- 当前判定：`局部完成`
- 备注：
  - 已把 recruit 真实联调从临时命令改成 spec 内标准样本脚本：`execution/recruit/run-authenticated-recruit-sample.py`
  - 已按 `00-29` 再执行两次标准 `backend-only` 发布，记录为：
    - `20260403-015836-backend-only-recruit-auth-sample-fixes.md`
    - `20260403-020152-backend-only-recruit-company-save-fix.md`
  - 最新真实样本证据为：`execution/recruit/samples/20260403-020306-recruit-fixes-post-company-fix/summary.md`
  - 同一条真实登录态样本已确认以下链路全部通过：
    - `company save -> project create -> role create -> actor search -> role detail -> apply -> my applies`
    - `admin projects/roles/applies` 三张治理聚合列表可按样本关键字回读
    - `pause role -> resume role -> end project -> block resume role -> resume project(no auto role resume) -> final resume role` 状态治理链路符合执行卡约束
    - `GET /role/project/{projectId}` 与 `GET /apply/role/{roleId}` 已通过脚本化 params 请求验证，不再被 query string 拼接错误污染
  - 本轮后端已收口 4 个真实问题：
    - `MybatisPlusConfig` 补齐 `PaginationInnerInterceptor`，修复 `total=0 / list 非空`
    - `RecruitPostServiceImpl` 改为按 `RoleExtra.projectId + company_profile.extendedField.projects` 回填项目，修复演员端 `projectId` 错映射
    - `AdminRecruitGovernanceServiceImpl` 改为更新项目真实引用而不是副本，修复“项目结束表面成功、实际未落库”
    - `CompanyProfileServiceImpl` 补齐 `user.update_user_name` 审计字段，修复 `PUT /api/company` 返回 `code=500`
  - 因此 recruit 当前主风险已不再是“核心接口 400/500 或状态治理失效”，而是：
    - 小程序页面层面的真实 UI/交互证据仍未补齐
    - 后台权限矩阵仍保留 `page.system.admin-users` fallback
    - `project` 仍是 `extendedField` 兼容层，不适合继续无限扩张
