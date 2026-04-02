# 剧组档案、项目、角色与投递最小连通闭环后台执行卡

## 1. 执行卡名称

剧组档案、项目、角色与投递最小连通闭环 - 后台执行卡

## 2. 归属切片

- `../../slices/crew-company-project-recruit-capability-slice.md`

## 3. 负责范围

- 招募治理菜单、页面、权限登记
- 项目 / 角色 / 投递列表
- 项目状态、角色状态最小治理按钮与确认弹窗
- 权限 fallback 呈现策略

## 4. 不负责范围

- 后端状态规则和落库细节
- 小程序项目创建、角色创建页面
- 完整项目编辑台和复杂审核流

## 5. 关键输入

- 上位 Spec：
  - `00-11 platform-admin-console`
  - `00-28 architecture-driven-delivery-governance`
- 关键文件：
  - `kaipai-admin/src/views/recruit/ProjectsView.vue`
  - `kaipai-admin/src/views/recruit/RolesView.vue`
  - `kaipai-admin/src/views/recruit/AppliesView.vue`
  - `kaipai-admin/src/api/recruit.ts`
  - `kaipai-admin/src/types/recruit.ts`
  - `kaipai-admin/src/constants/permission.ts`
  - `kaipai-admin/src/constants/permission-registry.ts`
  - `kaipai-admin/src/router/index.ts`

## 6. 目标交付物

- 项目 / 角色 / 投递三张真实治理页可访问
- 项目页支持恢复进行、结束项目
- 角色页支持恢复招募、暂停、结束
- 动作统一经过确认弹窗
- 过渡期老管理员无需先改角色表也能验证按钮和接口

## 7. 关键任务

1. 保留真实列表只读能力
2. 增补项目状态治理按钮
3. 增补角色状态治理按钮
4. 接入确认弹窗、成功提示和局部刷新
5. 登记新的 recruit 动作权限码并提供 fallback

## 8. 依赖项

- 后端必须先提供 `/admin/recruit/projects/{id}/status`、`/admin/recruit/roles/{id}/status`
- 状态文案和状态枚举必须与后端口径一致
- 权限树和角色矩阵后续仍要显式补齐 recruit 新动作

## 9. 验证方式

- `npm run build` 通过
- 无权限账号看不到或无法触发对应动作
- 有 fallback 的管理员可在真实后台执行状态动作
- 列表和详情抽屉的状态回显保持一致

## 10. 完成定义

- 后台不再停留在只读招募页
- 项目 / 角色具备最小治理动作
- 权限码、页面按钮和后端接口一一对应

## 11. 风险与备注

- 若按钮只在列表出现、不在详情出现，运营会继续依赖来回切表格
- 若前端自己推断可恢复条件，而不是交给后端校验，状态容易再分叉
- recruit 新动作当前仍处于 fallback 过渡期，后续要回到真实角色授权
