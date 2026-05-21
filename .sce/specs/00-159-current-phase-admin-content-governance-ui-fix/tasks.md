# 00-159 任务清单

## 开头先回答三个问题

1. 先做什么：先落规格和最小代码改动，避免把这批后台问题继续散落处理。
2. 怎么判断做完：前后端本地验证通过，并且四个用户可见问题都有明确代码落点。
3. 哪些风险要盯：权限动作新增后需要角色数据同步；模板历史 JSON 只能兼容缺失字段，不能吞掉根 JSON 非对象错误。

## 1. SCE 规格

- [x] 新建 00-159 requirements / design / tasks / execution。

## 2. 后台前端

- [x] 模板编辑兼容旧 `artifactPresetJson` 缺失的 `miniProgramCard` / `shareCard`、`poster`、`pageConfig`。
- [x] 统一修复表格固定右侧操作列 hover 透层。
- [x] 联系方式申请列表补同意 / 拒绝按钮、确认弹窗和接口调用。
- [x] 用户管理详情抽屉删除资金概览展示。

## 3. 后端

- [x] 后台内容 Controller 补联系方式申请同意 / 拒绝接口。
- [x] 联系方式申请 Service 补后台审批方法。
- [x] 数据库迁移补 `ADMIN` 角色联系方式审批动作权限。

## 4. 验证

- [x] `kaipai-admin npm run type-check`。
- [x] `kaipai-admin npm run build`。
- [x] `kaipaile-server mvn -q -DskipTests compile`。
