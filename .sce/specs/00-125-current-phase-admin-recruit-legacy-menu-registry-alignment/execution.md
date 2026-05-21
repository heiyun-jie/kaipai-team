# 00-125 执行记录

## 1. 当前状态

- 已重新读取 `C:\Users\33340\.codex\memories\user-global-memory.md`
- 已核对 `CURRENT_CONTEXT.md`、`00-124`
- 已先核实 `menu.recruit` 的运行时边界，再按 `00-125` 做最小 registry 对齐

## 2. 修复前证据

### 2.1 `menu.recruit` 当前不参与 runtime 放通

已核实：

- `D:\XM\kaipai-team\kaipai-admin\src\constants\menus.ts`
  - `adminMenus.recruit` 无 `menuPermission`
- `D:\XM\kaipai-team\kaipai-admin\src\router\index.ts`
  - 招募页仅认 `page.recruit.*`
- `D:\XM\kaipai-team\kaipaile-server\src\main\java\com\kaipai\module\controller\admin\recruit\AdminRecruitController.java`
  - 仅认 `page.recruit.* / action.recruit.*`

当前判断：

- `menu.recruit` 不能被重新解释成 runtime 放通条件

### 2.2 `menu.recruit` 当前仍是历史角色数据的一部分

已使用后台账号：

- `account = admin`
- `password = <REDACTED>`

登录态复核结果：

- 当前角色 `ADMIN` 的 `menuPermissions` 仍包含 `menu.recruit`
- 招募矩阵首项 `hasRecruitMenu = true`

同时已核实：

- `AdminRoleServiceImpl.java`
  - 仍保留 `RECRUIT_MENU_PERMISSION = "menu.recruit"`
  - 仍把它映射到 `hasRecruitMenu`
- `RolesView.vue`
  - 仍展示 `历史 menu.recruit`

当前判断：

- `menu.recruit` 当前仍是历史登记展示项
- 更适合先纳入 registry，而不是直接删运行库角色数据

依据：

- 前后端源码
- 本机 `8010` 登录态接口

置信度：

- 高

不确定边界：

- 本判断只覆盖当前工作树与本机 dev 运行库

## 3. 本轮实施

已修改：

- `D:\XM\kaipai-team\kaipai-admin\src\constants\permission-registry.ts`

改动内容：

- 新增 `historicalMenuRegistry`
- 把 `menu.recruit` 作为：
  - `招募治理菜单（历史登记）`
  补入 `permissionRegistry`

本轮未改：

- 运行库角色数据
- 招募 controller 鉴权
- 招募矩阵 `hasRecruitMenu` 历史展示逻辑

## 4. 验证结果

### 4.1 构建验证

命令：

- `cd D:\XM\kaipai-team\kaipai-admin && npm run type-check`
- `cd D:\XM\kaipai-team\kaipai-admin && npm run build`

结果：

- `type-check`：通过
- `build`：通过

保留告警：

- Sass legacy JS API deprecation
- Vite chunk size warning

### 4.2 真实浏览器复核

已使用 Playwright CLI 登录 `http://127.0.0.1:5100/login`，并复核：

- `/system/roles`
- `编辑角色` 弹窗
- 权限编排区

截图证据：

- `D:\XM\kaipai-team\output\playwright\00-125\roles-recruit-legacy-menu-after.png`

当前已确认：

- unknown list 已完全消失
- recruit 模块中仍可见历史招募菜单登记项
- 浏览器 console 当前无错误 / 警告输出

依据：

- 真实浏览器快照
- 页面截图

置信度：

- 高

不确定边界：

- 当前复核只覆盖 `admin` 账号
- 本轮验证的是 registry 对齐效果，不等于已删除运行库中的 `menu.recruit`

## 5. 文档回填

本轮已回填：

- `D:\XM\kaipai-team\.sce\specs\00-125-current-phase-admin-recruit-legacy-menu-registry-alignment\requirements.md`
- `D:\XM\kaipai-team\.sce\specs\00-125-current-phase-admin-recruit-legacy-menu-registry-alignment\design.md`
- `D:\XM\kaipai-team\.sce\specs\00-125-current-phase-admin-recruit-legacy-menu-registry-alignment\tasks.md`
- `D:\XM\kaipai-team\.sce\specs\00-125-current-phase-admin-recruit-legacy-menu-registry-alignment\execution.md`
- `D:\XM\kaipai-team\.sce\specs\README.md`
- `D:\XM\kaipai-team\.sce\specs\spec-code-mapping.md`
- `D:\XM\kaipai-team\.sce\steering\CURRENT_CONTEXT.md`

## 6. 结论

`00-125` 已完成本轮目标：

- `menu.recruit` 已作为历史菜单登记补入前端 registry
- 角色编辑弹窗中的 unknown list 已清零
- 当前未改变招募 runtime 放通边界
