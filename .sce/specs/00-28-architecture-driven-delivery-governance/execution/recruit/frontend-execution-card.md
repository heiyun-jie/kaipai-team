# 剧组档案、项目、角色与投递最小连通闭环前端执行卡

## 1. 执行卡名称

剧组档案、项目、角色与投递最小连通闭环 - 小程序前端执行卡

## 2. 归属切片

- `../../slices/crew-company-project-recruit-capability-slice.md`

## 3. 负责范围

- 剧组档案、项目、角色、投递管理页面接真
- 运行时 mock 开关收口
- 演员端 `role/apply` 真接口消费

## 4. 不负责范围

- 后台权限和运营动作
- 后端聚合和状态审计
- 独立项目域迁移

## 5. 关键输入

- `kaipai-frontend/src/utils/runtime.ts`
- `kaipai-frontend/src/api/company.ts`
- `kaipai-frontend/src/api/project.ts`
- `kaipai-frontend/src/api/role.ts`
- `kaipai-frontend/src/api/apply.ts`
- `kaipai-frontend/src/pages/company-profile/edit.vue`
- `kaipai-frontend/src/pages/project/create.vue`
- `kaipai-frontend/src/pages/project/role-create.vue`
- `kaipai-frontend/src/pages/apply-manage/index.vue`
- `kaipai-frontend/src/pages/role-detail/index.vue`
- `kaipai-frontend/src/pages/apply-confirm/index.vue`
- `kaipai-frontend/src/pages/my-applies/index.vue`
- `kaipai-frontend/src/pages/apply-detail/index.vue`

## 6. 目标交付物

- `company/project/role/apply` 不再强依赖 mock
- 剧组端写侧与演员端读侧都能消费真实接口
- 项目 / 角色状态变化后，页面不出现明显错口径

## 7. 关键任务

1. 放开运行时真实能力开关
2. 对齐 `company / project / role / apply` API 契约
3. 让剧组创建和演员投递都走真实接口
4. 为后续真实环境联调保留足够日志和错误提示

## 8. 依赖项

- 后端接口必须先稳定
- 测试账号必须具备真实 token 和剧组 / 演员身份

## 9. 验证方式

- `npm run type-check` 通过
- 剧组账号可保存档案、创建项目、创建角色
- 演员账号可查看角色、投递、查看我的投递

## 10. 完成定义

- 前端真实链路可跑
- mock 不再是默认事实源
- 状态变化能被页面真实消费

## 11. 风险与备注

- 当前项目状态仍是兼容层字段，前端不能自己再推一套项目真相
- 若联调只验证创建、不验证状态变化，后面仍会把后台治理动作做成假闭环
