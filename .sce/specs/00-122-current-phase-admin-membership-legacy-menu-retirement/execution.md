# 00-122 执行记录

## 1. 当前状态

- 已重新读取 `C:\Users\33340\.codex\memories\user-global-memory.md`
- 已核对 `CURRENT_CONTEXT.md`、`00-110`、`00-121`
- 已先核实 `menu.membership` 的源码与运行态依赖，再按 `00-122` 做最小退场

## 2. 删除前证据

### 2.1 `menu.membership` 仅剩前端 registry 残留

已核实：

- `D:\XM\kaipai-team\kaipai-admin\src\constants\permission-registry.ts`
  - 存在 `legacyMenuRegistry`
  - 其中只登记 `menu.membership`
- `D:\XM\kaipai-team\kaipaile-server\src\main\java`
  - 未命中 `menu.membership`
  - 仍命中 `page.membership.* / action.membership.*`

当前判断：

- `menu.membership` 不属于当前后端鉴权合同
- membership 页面 / 动作权限仍属于后端合同，本轮不能删除

依据：

- 前后端源码 `rg`

置信度：

- 高

不确定边界：

- 本判断只覆盖当前工作树源码

### 2.2 当前运行库角色未携带 `menu.membership`

已使用后台账号：

- `account = admin`
- `password = <REDACTED>`

登录态复核：

- `GET /admin/system/roles?pageNo=1&pageSize=100`
- 逐个 `GET /admin/system/roles/{adminRoleId}`

当前结果：

- 角色 `ADMIN` 未携带 `menu.membership`
- 当前运行库角色中未发现 `menu.membership`

依据：

- 本机 `127.0.0.1:8010` 登录态 API 返回

置信度：

- 高

不确定边界：

- 本判断只覆盖当前本机 dev 运行库
- 不外推到其它环境数据库

### 2.3 为什么不处理阶段枚举

本轮同时核查了 AI / 招募矩阵阶段枚举：

- 当前运行态返回：
  - AI：`ai_ready`
  - 招募：`recruit_ready`
- 但后端 `AdminRoleServiceImpl.java` 仍会主动计算：
  - `compat_transition`
  - `fallback_only`
  - `partial_ai`
  - `partial_recruit`
  - `not_granted`

当前判断：

- 阶段枚举是前后端接口合同的一部分，不是纯前端 dead code
- 不应与 `menu.membership` 这条最小退场切片混在一起删除

## 3. 本轮实施

已修改：

- `D:\XM\kaipai-team\kaipai-admin\src\constants\permission-registry.ts`

改动内容：

- 删除 `legacyMenuRegistry`
- 从 `permissionRegistry` 拼接中移除 `legacyMenuRegistry`
- 继续保留：
  - `page.membership.*`
  - `action.membership.*`

## 4. 验证结果

### 4.1 源码核销

命令：

- `rg -n "menu\.membership|legacyMenuRegistry" D:\XM\kaipai-team\kaipai-admin\src\constants\permission-registry.ts`

结果：

- 无命中

### 4.2 构建验证

命令：

- `cd D:\XM\kaipai-team\kaipai-admin && npm run type-check`
- `cd D:\XM\kaipai-team\kaipai-admin && npm run build`

结果：

- `type-check`：通过
- `build`：通过

保留告警：

- Sass legacy JS API deprecation
- Vite chunk size warning

### 4.3 真实浏览器 smoke

已使用 Playwright CLI 登录 `http://127.0.0.1:5100/login`，并复核：

- `/system/roles`
- `编辑角色` 弹窗
- 权限编排区

截图证据：

- `D:\XM\kaipai-team\output\playwright\00-122\roles-directory-after.png`
- `D:\XM\kaipai-team\output\playwright\00-122\roles-edit-dialog-after.png`

当前已确认：

- 角色治理页可正常访问
- 角色编辑弹窗可打开
- 权限编排区可渲染
- 浏览器 console 当前无错误 / 警告输出

补充发现：

- 角色编辑弹窗仍显示 `page.membership.* / action.membership.*` 为“未登记权限”
- 这不是 `menu.membership` 历史菜单退场问题，而是 membership 页面 / 动作权限与前端 permission tree 对齐问题
- 下一步若继续推进，应该另起 spec 处理该 registry 对齐，而不是在本轮删除页面 / 动作权限

依据：

- 真实浏览器快照
- 页面截图

置信度：

- 高

不确定边界：

- 当前 smoke 只覆盖 `admin` 账号与本机 `5100 / 8010`
- 未对所有角色编辑 / 保存路径做写入回归

## 5. 文档回填

本轮已回填：

- `D:\XM\kaipai-team\.sce\specs\00-122-current-phase-admin-membership-legacy-menu-retirement\requirements.md`
- `D:\XM\kaipai-team\.sce\specs\00-122-current-phase-admin-membership-legacy-menu-retirement\design.md`
- `D:\XM\kaipai-team\.sce\specs\00-122-current-phase-admin-membership-legacy-menu-retirement\tasks.md`
- `D:\XM\kaipai-team\.sce\specs\00-122-current-phase-admin-membership-legacy-menu-retirement\execution.md`
- `D:\XM\kaipai-team\.sce\specs\README.md`
- `D:\XM\kaipai-team\.sce\specs\spec-code-mapping.md`
- `D:\XM\kaipai-team\.sce\steering\CURRENT_CONTEXT.md`

## 6. 结论

`00-122` 已完成本轮目标：

- `menu.membership` 已确认不是当前后端和运行库消费的权限项
- 前端 permission registry 中的 membership 历史菜单残留已退场
- 角色治理页与权限编排区已通过构建和真实浏览器 smoke
