# 剧组档案、项目、角色与投递最小连通闭环切片卡

## 1. 切片名称

剧组档案、项目、角色与投递最小连通闭环

## 2. 切片目标

把历史剧组线 `company -> project -> role -> apply-manage` 从“页面有表单 / mock 可演示”推进到“后端可落库、后台可看见、最小治理动作可执行”的真实链路。

本切片的目标不是把剧组侧一次性做成完整项目域，而是在不脱离当前仓库事实的前提下，先建立：

- 剧组档案、项目、角色、投递的真实前后端连接
- 后台对项目 / 角色 / 投递的最小治理入口
- 项目结束与角色暂停 / 结束的最小状态处置能力
- 与演员端 `role/apply` 读链路之间不互相打架的状态口径

## 3. 上位 Spec

- `00-03 shared-utils-api`
- `00-10 platform-admin-backend-architecture`
- `00-11 platform-admin-console`
- `00-27 mini-program-frontend-architecture`
- `00-28 architecture-driven-delivery-governance`
- `04-01 page-project-create`
- `04-02 page-role-create`
- `04-03 page-apply-manage`
- `04-05 page-company-profile-edit`

## 4. 业务范围

### 4.1 本轮范围

- 剧组档案读写真实接口接通
- 项目创建 / 查询 / 我的项目列表真实接口接通
- 角色创建 / 更新 / 删除 / 按项目查询真实接口接通
- 演员端角色读取 / 投递与剧组侧写链路的最小事实模型对齐
- 后台项目 / 角色 / 投递真实列表
- 后台项目状态校准、角色状态校准最小治理动作
- 最小审计日志与权限兜底

### 4.2 不在本轮范围

- 独立 `project` 表建模与迁移
- 完整项目 CRUD 治理台
- 项目审核流、角色审核流、投递 SLA 治理
- 项目删除后的复杂回滚和批量恢复
- 作为当前主线继续扩张剧组端历史页面

## 5. 数据与状态模型

### 5.1 关键实体 / 表

- `company_profile`
- `company_profile.extendedField.projects`
- `recruit_post`
- `recruit_post.extendedField.projectId`
- `recruit_apply`
- `admin_operation_log`

### 5.2 关键状态

#### 项目状态

- `1 进行中`
- `2 已结束`

#### 角色状态

- `recruiting` -> `recruit_post.postStatus = 1`
- `closed` -> `recruit_post.postStatus = 2`
- `paused` -> `recruit_post.postStatus = 3`

#### 投递状态

- 待处理
- 已通过
- 已拒绝
- 已取消

### 5.3 状态流转

```text
剧组档案保存
  -> company_profile / extendedField 回写

项目创建 / 更新
  -> company_profile.extendedField.projects 回写

角色创建 / 更新
  -> recruit_post 落库
  -> recruit_post.extendedField.projectId 关联项目

后台结束项目
  -> project.status = 2
  -> 该项目下未结束角色同步收口为 closed

后台校准角色状态
  -> recruit_post.postStatus 更新
  -> 若目标为 recruiting，则必须校验关联项目仍为进行中
```

## 6. 后端交付

### 6.1 核心接口

#### 小程序 / 前台

- `GET /api/company/mine`
- `PUT /api/company`
- `POST /api/project`
- `PUT /api/project/{projectId}`
- `GET /api/project/{projectId}`
- `GET /api/project/mine`
- `GET /api/project/list`
- `POST /api/role`
- `PUT /api/role/{roleId}`
- `DELETE /api/role/{roleId}`
- `GET /api/role/project/{projectId}`
- `GET /api/role/search`
- `GET /api/role/{id}`
- `POST /api/apply`
- `GET /api/apply/mine`
- `GET /api/apply/{id}`
- `GET /api/apply/role/{roleId}`
- `PUT /api/apply/{id}/approve`
- `PUT /api/apply/{id}/reject`

#### 后台

- `GET /api/admin/recruit/projects`
- `GET /api/admin/recruit/roles`
- `GET /api/admin/recruit/applies`
- `POST /api/admin/recruit/projects/{id}/status`
- `POST /api/admin/recruit/roles/{id}/status`

### 6.2 核心服务规则

- 当前没有独立 `project` 表，本轮必须承认项目事实仍在 `company_profile.extendedField.projects`
- 角色与项目关联只能以 `recruit_post.extendedField.projectId` 为准
- 演员端可投递的角色只能是 `recruiting`
- 结束项目时必须同步收口该项目下仍未结束的角色，否则演员端会继续看到失效招募
- 恢复项目只回写项目状态，不自动恢复项目下角色状态
- 恢复角色招募前必须校验关联项目仍为进行中

### 6.3 安全 / 权限 / 审计

- 项目列表、角色列表、投递列表都要有后台页面权限
- 项目状态校准、角色状态校准必须具备独立动作权限
- 当前过渡期允许使用 `page.system.admin-users` 作为后台权限 fallback，避免真实环境角色矩阵尚未迁移时完全无法验证
- 项目状态校准、角色状态校准必须写 `admin_operation_log`

## 7. 后台交付

### 7.1 管理页 / 治理动作

- `kaipai-admin/src/views/recruit/ProjectsView.vue`
- `kaipai-admin/src/views/recruit/RolesView.vue`
- `kaipai-admin/src/views/recruit/AppliesView.vue`
- 路由、菜单、权限登记与状态标签映射
- 项目：恢复进行 / 结束项目
- 角色：恢复招募 / 暂停 / 结束

### 7.2 运营侧关键动作

- 先确认真实数据是否已接通
- 对失效项目执行结束并同步收口角色
- 对异常角色执行恢复 / 暂停 / 结束
- 查看项目、角色、投递的基础事实与联系信息

## 8. 小程序 / 前台交付

### 8.1 页面落点

- `src/pages/company-profile/edit.vue`
- `src/pages/project/create.vue`
- `src/pages/project/role-create.vue`
- `src/pages/apply-manage/index.vue`
- `src/pages/home/index.vue`
- `src/pages/role-detail/index.vue`
- `src/pages/apply-confirm/index.vue`
- `src/pages/my-applies/index.vue`
- `src/pages/apply-detail/index.vue`

### 8.2 前端 gating / 展示 / 回写

- 剧组侧不再强制走 mock `company / project / role`
- 演员侧 `roleRead + apply` 走真接口
- 角色状态与项目状态必须以后端返回和后台治理结果为准
- 不允许前端自己再推断一套“项目已结束但角色还可投递”的展示结果

## 9. 联调点

- 剧组账号可保存档案、创建项目、创建角色
- 首页剧组项目展开和项目下角色列表读取真实数据
- 演员端可完成 `search -> detail -> submit -> my-applies`
- 后台结束项目后，项目状态与角色状态同步收口
- 后台暂停 / 恢复 / 结束角色后，演员端角色搜索结果同步变化

## 10. 当前阻塞项

- 真实环境 `company -> project -> role -> apply-manage` 还未做完整手工联调
- `project` 仍是兼容层事实源，不是独立项目域模型
- 后台当前只有最小状态治理动作，仍未覆盖更完整的运营处置
- 目标环境后台角色矩阵还未显式下发新的 recruit 动作权限

## 11. 建议推进顺序

1. 锁定兼容层事实源和状态口径
2. 补齐后端读写与后台聚合接口
3. 落后台最小治理动作与审计
4. 校正小程序真实读写链路
5. 真实环境联调并回填状态

### 11.1 第一步：锁定事实源

- 明确项目继续复用 `company_profile.extendedField.projects`
- 明确角色继续复用 `recruit_post`
- 明确项目状态与角色状态的映射和约束关系

### 11.2 第二步：补齐后端

- 打通剧组档案 / 项目 / 角色 / 投递真实接口
- 后台聚合读取项目 / 角色 / 投递
- 增补项目状态、角色状态的最小治理接口

### 11.3 第三步：落后台治理动作

- 不再停留在只读列表
- 至少要能结束项目、暂停 / 恢复 / 结束角色
- 高风险动作进入操作日志

### 11.4 第四步：校正前台

- 让剧组页和演员页都消费真实状态
- 避免项目结束后角色仍出现在演员端

### 11.5 第五步：联调与验收

- 跑通真实账号、真实 token、真实项目和真实角色
- 回填状态页，不把“最小连通”误判成“整站闭环”

## 12. 完成定义

### 12.1 局部完成

以下只能算局部完成：

- 小程序能创建项目 / 角色，但后台完全不可见
- 后台能看项目 / 角色 / 投递，但没有任何治理动作
- 角色读链路已通，但真实环境还没跑过一次端到端联调
- 项目结束后，角色仍然留在演员端可投递

### 12.2 闭环完成

以下同时满足，才能算闭环完成：

- 剧组档案、项目、角色、投递真实链路可用
- 后台可查看并执行最小状态治理动作
- 项目状态与角色状态不会出现互相矛盾
- 项目 / 角色状态治理动作可追溯
- 演员端与剧组端都完成真实环境联调
- 当前兼容层边界和后续独立建模风险已在状态文档中明确记录
