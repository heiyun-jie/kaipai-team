# 招募角色与投递链路状态回填

## 1. 当前判定

- 回填日期：`2026-04-04`
- 当前判定：`局部完成`
- 一句话结论：`role/apply` 最小后端接口、角色详情、投递确认、我的投递与投递详情所依赖的真实链路已补齐，`kaipai-frontend` 当前也已把 `role/apply` 前端 mock 分支退场并固定为真接口；相邻切片中的剧组侧 `company/project/role`、后台最小状态治理和真实角色矩阵也都已接上，且当前线上 `ADMIN` 登录态已显式包含 `menu/page/action.recruit.*`，所以 recruit 主链已不再受 fallback 权限阻塞。但按当前产品口径，“通告”已改为平台创建的二期产物，演员端首页也不再以角色列表作为主入口，因此本状态页当前只保留 `role/apply` 能力闭环事实，不再把首页角色流量入口当成当前版本目标。

## 2. 当前已确认事实

### 2.1 小程序前端

- `kaipai-frontend/src/api/role.ts` 已把 `getRole / searchRoles / getRolesByProject / create / update / delete` 全部固定为真实 `/api/role/*`
- `kaipai-frontend/src/api/apply.ts` 已把 `submit / cancel / mine / role / approve / reject / detail` 全部固定为真实 `/api/apply/*`
- `2026-04-04` 已通过 `00-53` 删除 `role.ts / apply.ts` 中的 `useApiMock(...)` 分支，`src/utils/runtime.ts` 也已同步删除 `role / roleRead / apply` capability
- `kaipai-frontend/src/pages/home/index.vue` 当前已把演员首页主入口从 `searchRoles -> role-detail` 切到 `searchActors -> actor-profile/detail`，`role/apply` 保留为从演员详情或“我的投递”继续进入的能力链
- `2026-04-04` 已通过 `00-54` 删除 `src/api/actor.ts` 中的 `useApiMock('actor')` 分支；演员首页列表、公开详情和本人档案编辑当前统一只走真实 `/api/actor*`
- 因此前端以下页面已具备消费真实 `role/apply` 的最小条件：
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

- 当前已切真的只是 `roleRead + apply` 最小读写链
- 按当前产品口径，首页主入口应切到演员档案列表；因此 `role/search` 不再承担首页主入口职责，而是保留给后续平台创建通告 / 角色能力的二期承接
- 当前演员首页的真实问题已从“还在读角色列表”进一步收口为“残留自我档案路由清理与二期平台创建通告的未来承接”；小程序与后台招募页级证据当前都已补到 spec 样本
- `2026-04-03 10:56` 已按 spec 标准页面证据入口 `execution/recruit/run-recruit-mini-program-page-evidence.py` 产出最新小程序样本 `execution/recruit/samples/20260403-105631-recruit-mini-program-page-evidence/summary.md`
- 同一样本当前已补齐 7 个页面的真实 `route + query + screenshot + page-data`
- 当前 7 个页面均已直接走 automator 真截图
- 同一样本 `captures/mini-program-screenshot-capture.json` 已记录 `visualReview.uniqueScreenshotHashCount=7`、`visualDidNotRefresh=false`，每页还保留 `captures/page-data-*.json`
- 当前前端已不再把 `role/apply` 保留为 mock 双轨；剩余问题已转向 `project` 兼容层、company/project 写链与二期产品边界，而不是“演员端还在不在用 mock”
- 当前前端也已不再把 actor 主线保留为 mock 双轨；剩余问题已转向演员自我档案冗余路由、公开详情边界与其他能力域对 `mockActors` 的历史依赖
- 当前剧组侧 `company/project/role` 写链路与后台最小状态治理入口已转入 `crew-company-project-status.md` 单独跟踪，不再在本状态页重复判定
- 因为后端当前没有独立 `project` 表，所以这轮没有强行把 `project` 与 `recruit_post` 拆成两套事实源

## 4. 验证记录

- `kaipaile-server`：`mvn -q -DskipTests compile` 通过
- `kaipai-frontend`：`npm run type-check` 通过
- `kaipai-admin`：`npm run build` 通过（招募治理页与角色矩阵页已补项目 / 角色状态校准动作）

## 5. 下一轮最小动作

1. 把 `run-recruit-mini-program-page-evidence.py` 与 `run-recruit-admin-page-evidence.py` 固化为后续 recruit 样本的标准附加步骤，避免再次回退到只看接口 smoke
2. 用后台最小状态治理动作继续回归演员端结果，确认项目 / 角色状态变化会持续真实影响角色可见性
3. 决定剧组侧是继续沿 `recruit_post` 做聚合式 `project` 视图，还是先补独立项目域模型，再切 `project/company`
4. 继续把演员端真实联调与剧组侧写链路、后台最小治理分开追踪，避免把“`role/apply` 读链路已通”误写成“通告首页已完成”或“小程序整站已闭环”

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

### 2026-04-03（四次回填）

- 当前判定：`局部完成`
- 备注：
  - 已按 `00-29` 标准 `admin-only` 脚本完成管理端线上发布，记录为 `20260403-021050-admin-only-recruit-governance-pages.md`
  - 发布后已补做真实登录态治理页 smoke：
    - `GET /api/admin/recruit/projects?pageNo=1&pageSize=2&keyword=` -> `200`
    - `GET /api/admin/recruit/roles?pageNo=1&pageSize=2&keyword=` -> `200`
    - `GET /api/admin/recruit/applies?pageNo=1&pageSize=2&keyword=` -> `200`
    - `/recruit/projects`、`/recruit/roles`、`/recruit/applies` 均返回当前 SPA 入口 HTML
  - 随后已继续把 recruit 权限矩阵收口到真实角色分配链路，而不是长期停在 fallback 过渡态

### 2026-04-03（五次回填）

- 当前判定：`局部完成`
- 备注：
  - 已按 recruit 权限收口说明新增并上线 `/api/admin/system/roles/recruit-governance-matrix`
  - `2026-04-03` 当前公网真实回读结果为：
    - `POST http://101.43.57.62/api/admin/auth/login` -> `200`
    - 当前 `ADMIN` 登录回包已显式包含：
      - `menu.recruit`
      - `page.recruit.projects`
      - `page.recruit.roles`
      - `page.recruit.applies`
      - `action.recruit.project.status`
      - `action.recruit.role.status`
    - `GET http://101.43.57.62/api/admin/system/roles/recruit-governance-matrix` -> `200`
    - 矩阵返回 `recruitReadyRoleCount=1`、`fallbackRoleCount=0`、`canRetireFallback=true`
    - 唯一启用角色 `ADMIN` 当前为 `rolloutStage='recruit_ready'`
    - `GET http://101.43.57.62/api/admin/recruit/roles?pageNo=1&pageSize=1&keyword=` -> `200`
  - 这说明 recruit 当前主风险已不再是“后台角色还要靠 `page.system.admin-users` fallback 才能进入治理页”
  - recruit 当前剩余风险已进一步收口为：
    - 小程序页面级真实截图 / 交互证据仍未补齐
    - `project` 仍是 `company_profile.extendedField.projects` 兼容层
    - 后续新增后台角色仍需按 `execution/recruit/role-authorization-closure.md` 显式分配 recruit 权限，不能回退到 fallback 授权方式

### 2026-04-03（六次回填）

- 当前判定：`局部完成`
- 备注：
  - `2026-04-03 06:51` 已再次按 spec 标准样本入口 `execution/recruit/run-authenticated-recruit-sample.py continue-recheck` 重跑真实环境；最新样本为 `execution/recruit/samples/20260403-065131-continue-recheck/summary.md`
  - 本轮样本再次确认同一条真实登录态链路全部通过：
    - `company save -> project create -> role create -> actor search -> role detail -> apply -> my applies`
    - `admin projects/roles/applies`
    - `pause role -> resume role -> end project -> block resume role -> resume project(no auto role resume) -> final resume role`
  - `2026-04-03 06:57` 已继续按 `00-29` 标准 `backend-only` 脚本完成后端发布，记录为 `.sce/runbooks/backend-admin-release/records/20260403-065616-backend-only-recruit-role-search-undefined-guard.md`
  - 本轮发布后的真实复测结果为：
    - `POST http://101.43.57.62/api/admin/auth/login` -> `200`
    - 带 `ADMIN` token 的 `GET /api/admin/recruit/roles?pageNo=1&pageSize=20&keyword=` -> `200`
    - 带真实演员 token 且故意传 `minAge=undefined&maxAge=undefined` 的 `GET /api/role/search?...` -> transport `200` / payload `code=200`
  - 这说明当前 recruit 线上已不再停留在“`undefined` 筛选值直接把角色搜索打成 `400`”的状态；后端现在已对 query 中的 `undefined / null / 空串` 数字参数做兼容收口，旧缓存前端或手工请求不会再把可选筛选项打挂
  - 同时也已补充澄清“本地为什么还是 127”：`kaipai-admin` 当前 `5174` 只是本地 Vite dev server，默认通过 `VITE_API_PROXY_TARGET=http://127.0.0.1:8010` 代理到本机后端；线上访问仍统一走 nginx 承接的站点与相对路径 `/api`

### 2026-04-03（七次回填）

- 当前判定：`局部完成`
- 备注：
  - 已继续按最新产品口径收口演员首页：`kaipai-frontend/src/pages/home/index.vue` 现已稳定为演员档案列表首页，性别 quick filter 也已改为后端真实枚举 `male / female`，不再把 `男 / 女` 直接送入 `searchActors`
  - `kaipai-frontend/src/constants/options.ts`、`src/pages/role-select/index.vue` 与前端链路文档 `docs/link-analysis.md`、`docs/page-mindmap.md` 也已同步去掉“演员首页看角色列表 / 寻找通告”旧口径，避免实现已切换但文档继续把首页误指向 `role/search`
  - 因此当前 recruit 切片剩余重点已进一步明确为：
    - 小程序页面级真实截图 / 交互证据仍待补齐
    - 后端 `/api/actor/profile/{userId}` 目前只剩自校验兼容价值，后续可评估是否退场
    - `project` 仍是兼容层，未来若进入“平台创建通告”二期，需要先明确独立项目事实源

### 2026-04-03（八次回填）

- 当前判定：`局部完成`
- 备注：
  - `2026-04-03 10:56` 已把 recruit 小程序页面级证据收口到 spec 内标准脚本：`execution/recruit/run-recruit-mini-program-page-evidence.py`
  - 最新样本为 `execution/recruit/samples/20260403-105631-recruit-mini-program-page-evidence/summary.md`
  - 同一样本已为 `crew-home-projects`、`crew-apply-manage`、`actor-home-archive`、`actor-role-detail`、`actor-apply-confirm`、`actor-my-applies`、`actor-apply-detail` 七个页面补齐真实 `route + query + screenshot + page-data`
  - 当前截图链已完全恢复为 automator 真截图：7/7 页面均不再依赖 `PrintWindow`
  - `captures/mini-program-screenshot-capture.json` 当前已写入：
    - `visualReview.uniqueScreenshotHashCount=7`
    - `visualReview.uniqueActualPathCount=6`
    - `visualReview.visualDidNotRefresh=false`
  - 因此 recruit 当前剩余重点已继续收口为：
    - 小程序页面级证据已补齐一轮，且当前 7/7 页面均已恢复 automator 真截图
    - 后端 `/api/actor/profile/{userId}` 只剩兼容价值，后续可评估退场
    - `project` 仍是兼容层，未来若进入“平台创建通告”二期，需要先明确独立项目事实源

### 2026-04-03（九次回填）

- 当前判定：`局部完成`
- 备注：
  - `2026-04-03 11:09` 已把 recruit 后台页面级证据也收口到 spec 内标准脚本：`execution/recruit/run-recruit-admin-page-evidence.py`
  - 最新样本为 `execution/recruit/samples/20260403-110916-recruit-admin-page-evidence/summary.md`
  - 同一样本已为 `/recruit/projects`、`/recruit/roles`、`/recruit/applies` 三张后台治理页补齐：
    - 列表页真实截图
    - 详情抽屉真实截图
    - `captures/page-data-admin-recruit-*.json` 页面数据快照
    - 同筛选条件下的真实 `/api/admin/recruit/*` 回包
  - 当前三页样本都已命中 `20260403-065131-continue-recheck` 的稳定实体：
    - `projectId=1775170290915996`
    - `roleId=10003`
    - `applyId=10003`
    - `actorUserId=10000`
  - 因此 recruit 当前剩余重点已继续收口为：
    - 小程序页面级证据与后台页面级证据都已补齐一轮
    - 后端 `/api/actor/profile/{userId}` 只剩兼容价值，后续可评估退场
    - `project` 仍是兼容层，未来若进入“平台创建通告”二期，需要先明确独立项目事实源

### 2026-04-04

- 当前判定：`局部完成`
- 备注：
  - 已新增 `00-53 current-phase-crew-recruit-mock-retirement`，把 recruit 当前阶段前端 mock 退场从状态说明提升为独立 Spec
  - `kaipai-frontend/src/api/role.ts`、`src/api/apply.ts` 已删除 `useApiMock(...)` 分支；角色搜索保留 query sanitization 后统一走真实接口
  - `kaipai-frontend/src/mock/service.ts` 与 `src/mock/database.ts` 中无运行时入口的 role/apply mock 服务与假数据已同步删除
  - 重新执行 `kaipai-frontend npm run type-check` 通过
  - 因此 recruit 当前剩余重点已从“页面是否还可能退回 mock”进一步收口为：兼容层长期治理、二期平台创建通告边界，以及后台持续授权和页面证据维护
  - 同日又已新增 `00-54 current-phase-actor-mainline-mock-retirement`，并删除 `kaipai-frontend/src/api/actor.ts` 中 `searchActors / getActorDetail / getMyActorProfile / updateActorProfile` 的 mock 分支
  - `kaipai-frontend/src/utils/runtime.ts` 已同步删除 `actor` capability；`src/mock/service.ts` 中已无入口的 actor API mock 函数也已退场
  - 因此演员首页与演员档案主线当前也不再保留前端 mock 双轨；后续不再把“首页 actor 数据是否可能来自 mock”作为主阻塞判断
