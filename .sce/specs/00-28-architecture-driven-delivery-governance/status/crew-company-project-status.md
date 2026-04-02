# 剧组档案、项目与角色管理链路状态回填

## 1. 归属切片

- `../design.md`
- `../execution/`

## 2. 当前判定

- 回填日期：`2026-04-02`
- 当前判定：`局部完成`
- 一句话结论：`kaipai-frontend` 剧组侧 `company/project/role` 已具备切真所需的最小接口与运行时开关，后端也已通过源码编译；但后台治理入口、真实环境联调和历史数据治理尚未补齐，因此当前只能判定为“剧组主线最小连通已到位”，不能宣告三端闭环完成。

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
- `kaipaile-server/src/main/java/com/kaipai/module/server/recruit/service/impl/MiniProgramRecruitServiceImpl.java` 已用兼容层方式落盘：
  - 项目元数据写入 `company_profile.extendedField`
  - 角色与项目关联写入 `recruit_post.extendedField`
- `kaipaile-server/src/main/java/com/kaipai/module/server/company/service/impl/CompanyProfileServiceImpl.java` 已补齐公司档案读写，且 `profile(userId)` 不再因读取动作落库创建空档案

### 3.3 后台治理

- `kaipai-admin` 本轮未新增剧组档案、项目或角色治理页
- 当前仍缺少后台对剧组项目、角色、投递、状态流转的统一治理入口

### 3.4 联调现状

- 小程序前端类型检查已通过
- 后端在本机切换 `JDK 21` 后已通过源码编译
- 还未完成真实账号、真实 token、真实数据的端到端手工联调

## 4. 联调结论

- 当前是否具备三端联调条件：`部分具备`
- 已确认走通的链路：
  - 剧组档案读取 / 保存接口已存在
  - 项目创建 / 查询 / 我的项目列表接口已存在
  - 角色创建 / 查询 / 按项目查询接口已存在
  - 小程序运行时已不再强制把 `company/project/role` 锁在 mock
- 当前不能宣告闭环的原因：
  - 后台治理入口未补齐
  - 未做真实环境联调与历史兼容数据校验
  - 删除 / 变更后的级联治理、运营审计与回滚策略未补齐

## 5. 验收判断

| 闭环条件 | 状态 | 说明 |
|----------|------|------|
| 上位 Spec 已存在并对齐 | 已满足 | 以 `00-27` 的小程序架构和 `00-28` 的架构驱动交付治理为准 |
| 数据模型、接口、状态流转清楚 | 部分满足 | 兼容层方案已定，但仍是 `company_profile/recruit_post` 复用，不是独立项目域 |
| 后台治理入口可操作 | 未满足 | `kaipai-admin` 本轮未补剧组治理页 |
| 小程序或前台用户侧落点可验证 | 已满足 | 页面调用路径与运行时能力已切真 |
| 关键日志、权限、限额或回滚约束已接入 | 部分满足 | 登录态与剧组账号校验已在服务侧控制，但删除级联、审计和回滚未补齐 |
| 文档、映射表、验证记录已回填 | 已满足 | 已新增本状态文档并记录验证方式 |

## 6. 当前阻塞项

- `kaipai-admin` 尚未提供剧组项目与角色治理入口
- 真实环境仍需用剧组账号完成 `company -> project -> role -> apply-manage` 手工联调
- 兼容层长期仍需评估是否沉淀为独立 `project` 域模型

## 7. 下一轮最小动作

1. 启动真实后端与小程序，用剧组账号走通 `档案保存 -> 创建项目 -> 创建角色 -> 首页展开角色 -> 投递管理`
2. 为 `kaipai-admin` 补最小剧组治理入口，至少能看到项目 / 角色 / 投递的基础列表
3. 评估 `project` 独立建模与兼容层迁移边界，避免后续继续把项目事实源分散在扩展字段里

## 8. 回填记录

### 2026-04-02

- 当前判定：`局部完成`
- 备注：补齐了剧组侧 `company/project/role` 最小真实接口与前端运行时开关；验证记录为 `kaipaile-server` 在 `JDK 21` 下 `mvn -q -DskipTests compile` 通过、`kaipai-frontend` `npm run type-check` 通过。
