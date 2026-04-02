# 剧组档案、项目、角色与投递最小连通闭环后端执行卡

## 1. 执行卡名称

剧组档案、项目、角色与投递最小连通闭环 - 后端执行卡

## 2. 归属切片

- `../../slices/crew-company-project-recruit-capability-slice.md`

## 3. 负责范围

- 剧组档案、项目、角色、投递的真实接口
- 后台项目 / 角色 / 投递聚合接口
- 项目状态校准、角色状态校准接口
- 状态联动约束、最小审计日志与权限 fallback

## 4. 不负责范围

- 小程序页面样式和交互
- 后台表格布局和按钮呈现
- 独立 `project` 表迁移
- 完整审核流和复杂运营规则

## 5. 关键输入

- 上位 Spec：
  - `00-10 platform-admin-backend-architecture`
  - `00-28 architecture-driven-delivery-governance`
- 关键文件：
  - `kaipaile-server/src/main/java/com/kaipai/module/controller/company/CompanyProfileController.java`
  - `kaipaile-server/src/main/java/com/kaipai/module/controller/recruit/ProjectController.java`
  - `kaipaile-server/src/main/java/com/kaipai/module/controller/recruit/RecruitPostController.java`
  - `kaipaile-server/src/main/java/com/kaipai/module/controller/recruit/RecruitApplyController.java`
  - `kaipaile-server/src/main/java/com/kaipai/module/controller/admin/recruit/AdminRecruitController.java`
  - `kaipaile-server/src/main/java/com/kaipai/module/server/recruit/service/impl/MiniProgramRecruitServiceImpl.java`
  - `kaipaile-server/src/main/java/com/kaipai/module/server/recruit/service/impl/RecruitPostServiceImpl.java`
  - `kaipaile-server/src/main/java/com/kaipai/module/server/recruit/service/impl/RecruitApplyServiceImpl.java`
  - `kaipaile-server/src/main/java/com/kaipai/module/server/recruit/service/impl/AdminRecruitGovernanceServiceImpl.java`

## 6. 目标交付物

- 小程序侧 `company/project/role/apply` 接口稳定可用
- 后台项目 / 角色 / 投递聚合列表稳定可用
- 项目状态和角色状态可由后台校准
- 项目结束时同步收口关联角色
- 状态治理动作写入 `admin_operation_log`

## 7. 关键任务

1. 承认兼容层事实源
   - 项目继续回写 `company_profile.extendedField.projects`
   - 角色继续回写 `recruit_post`
2. 稳定小程序读写接口
   - `company / project / role / apply` 全部走真接口
3. 稳定后台聚合接口
   - 输出项目 / 角色 / 投递最小读模型
4. 增补状态治理动作
   - 项目状态校准
   - 角色状态校准
   - 项目结束级联收口角色
5. 对齐权限与日志
   - 过渡期允许 `page.system.admin-users` fallback
   - 所有状态治理动作进入审计

## 8. 依赖项

- 后台需要明确动作权限码和请求 DTO
- 前台需要消费统一状态口径，不再自行推断
- 真实环境需要至少一组剧组账号和演员账号完成联调

## 9. 验证方式

- `mvn -q -DskipTests compile` 通过
- 项目状态校准接口可更新 `company_profile.extendedField.projects`
- 角色状态校准接口可更新 `recruit_post.postStatus`
- 结束项目后，关联角色不再以 `recruiting` 暴露给演员端
- 操作日志可记录项目 / 角色状态变更

## 10. 完成定义

- 小程序和后台都能消费真实 recruit 数据
- 项目和角色最小治理动作已具备
- 状态口径不会出现“项目结束但角色仍招募中”
- 日志和权限不再缺席

## 11. 风险与备注

- 当前 `project` 仍是兼容层，不适合继续无限扩张字段
- 若后台只改项目状态而不联动角色状态，演员端会继续暴露失效招募
- 若恢复角色招募不校验项目状态，会把已结束项目重新暴露到演员端
