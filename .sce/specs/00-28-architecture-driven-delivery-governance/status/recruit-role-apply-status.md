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
