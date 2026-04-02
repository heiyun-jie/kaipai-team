# 招募角色与投递链路状态回填

## 1. 当前判定

- 回填日期：`2026-04-02`
- 当前判定：`局部完成`
- 一句话结论：演员端首页角色列表、角色详情、投递确认、我的投递与投递详情所依赖的 `role/apply` 最小后端接口已补齐，`kaipai-frontend` 也已把角色读取与投递切到真接口；但剧组侧 `project/company` 仍未整体切真，所以当前只能宣告“演员主线招募切片已具备最小真实链路”，不能误判成小程序整站都已连通。

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
  - 剧组侧 `role` 管理写接口与 `getRolesByProject`
- 因为后端当前没有独立 `project` 表，所以这轮没有强行把 `project` 与 `recruit_post` 拆成两套事实源

## 4. 验证记录

- `kaipaile-server`：`mvn -q -DskipTests compile` 通过
- `kaipai-frontend`：`npm run type-check` 通过

## 5. 下一轮最小动作

1. 补一轮真实环境联调，确认演员端 `search -> detail -> submit -> my-applies` 真实可用
2. 决定剧组侧是继续沿 `recruit_post` 做聚合式 `project` 视图，还是先补独立项目域模型，再切 `project/company`
3. 在剧组写侧方案明确前，不把 `createRole / updateRole / deleteRole / getRolesByProject` 一起放开，避免前后端事实源再次分裂
