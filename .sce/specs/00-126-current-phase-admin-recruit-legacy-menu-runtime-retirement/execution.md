# 00-126 执行记录

## 1. 当前状态

- 已重新读取 `C:\Users\33340\.codex\memories\user-global-memory.md`
- 已核对 `CURRENT_CONTEXT.md`、`00-125`
- 已按 `00-126` 主线先验证 `menu.recruit` 的运行时边界，再处理 dev 运行库对齐与运行态复核

## 2. 删除前证据

### 2.1 `menu.recruit` 当前不参与 runtime 放通

已核实：

- `D:\XM\kaipai-team\kaipai-admin\src\constants\menus.ts`
  - `adminMenus.recruit` 无 `menuPermission`
- `D:\XM\kaipai-team\kaipai-admin\src\router\index.ts`
  - 招募页只认 `page.recruit.*`
- `D:\XM\kaipai-team\kaipaile-server\src\main\java\com\kaipai\module\controller\admin\recruit\AdminRecruitController.java`
  - 只认 `page.recruit.* / action.recruit.*`

当前判断：

- `menu.recruit` 已不再承担运行时放通作用

### 2.2 当前 dev 运行库仍残留 `menu.recruit`

已使用后台账号：

- `account = admin`
- `password = <REDACTED>`

刷新前登录态 API 复核结果：

- `ADMIN` 角色详情 `menuPermissions` 仍包含 `menu.recruit`
- 登录态 session `adminUserInfo.menuPermissions` 仍包含 `menu.recruit`
- 招募矩阵首项：
  - `hasRecruitMenu = true`
  - `recruitReady = true`
  - `missingPermissions = []`

当前判断：

- 当前运行库中 `menu.recruit` 只剩历史残留
- 且唯一角色已满足完整招募直授权门禁，适合执行最小数据退场

依据：

- 登录态接口直接返回

置信度：

- 高

不确定边界：

- 本判断只覆盖本机 dev 运行库

## 3. 本轮实施

### 3.1 新增幂等 migration

已新增：

- `D:\XM\kaipai-team\kaipaile-server\src\main\resources\db\migration\V20260423_009__admin_recruit_legacy_menu_runtime_retirement.sql`

逻辑：

- 仅对同时具备：
  - `page.recruit.projects`
  - `page.recruit.roles`
  - `page.recruit.applies`
  - `action.recruit.project.status`
  - `action.recruit.role.status`
  的角色清理 `menu.recruit`
- migration 幂等，重复执行无副作用

### 3.2 刷新并对齐本机 dev 运行库

已执行：

- 停掉旧 `8010` 进程
- 重新启动本机后端到 `8010`
- 由于项目当前未接 `Flyway / Liquibase`，migration 不会自动应用

依据：

- `D:\XM\kaipai-team\kaipaile-server\src\main\resources\db\migration\README.md`

因此本轮实际做法：

1. 新增 migration 文件保留可复现 SQL 变更
2. 通过现有后台角色编辑接口先对齐当前 dev 运行库
3. 再手工执行一次 `009` migration SQL

手工执行 `009` 结果：

- `affected_rows = 0`

当前判断：

- 在执行 migration 之前，dev 运行库已被接口更新到目标状态
- `009` 已经和当前运行库状态对齐，重复执行保持 no-op

### 3.3 后端运行态刷新

新日志路径：

- `D:\XM\kaipai-team\output\runtime\00-126\backend-8010.out.log`
- `D:\XM\kaipai-team\output\runtime\00-126\backend-8010.err.log`

当前已确认：

- 本机 `8010` 新实例进程 PID：`44040`
- 新实例已在 `dev` profile 下启动成功
- err 日志为空

## 4. 验证结果

### 4.1 登录态 API 复核

重新登录后已确认：

- session `menuPermissions` 已不再包含 `menu.recruit`
- 角色详情 `menuPermissions` 已不再包含 `menu.recruit`
- 招募矩阵首项：
  - `hasRecruitMenu = false`
  - `rolloutStage = recruit_ready`
  - `missingPermissions = []`
  - `recruitReady = true`

依据：

- 本机 `127.0.0.1:8010` 登录态接口直接返回

置信度：

- 高

不确定边界：

- 只覆盖本机 dev 运行库

### 4.2 真实浏览器复核

已使用 Playwright CLI 登录 `http://127.0.0.1:5100/login`，并复核：

- `/system/roles`
- `编辑角色` 弹窗

截图证据：

- `D:\XM\kaipai-team\output\playwright\00-126\roles-recruit-runtime-after.png`

当前已确认：

- 招募矩阵不再显示 `历史 menu.recruit`
- 角色目录中的菜单数已从 `7` 收到 `6`
- 编辑角色弹窗中的 unknown list 继续保持 `0`
- 浏览器 console 当前无错误 / 警告输出

## 5. 文档回填

本轮已回填：

- `D:\XM\kaipai-team\.sce\specs\00-126-current-phase-admin-recruit-legacy-menu-runtime-retirement\requirements.md`
- `D:\XM\kaipai-team\.sce\specs\00-126-current-phase-admin-recruit-legacy-menu-runtime-retirement\design.md`
- `D:\XM\kaipai-team\.sce\specs\00-126-current-phase-admin-recruit-legacy-menu-runtime-retirement\tasks.md`
- `D:\XM\kaipai-team\.sce\specs\00-126-current-phase-admin-recruit-legacy-menu-runtime-retirement\execution.md`
- `D:\XM\kaipai-team\.sce\specs\README.md`
- `D:\XM\kaipai-team\.sce\specs\spec-code-mapping.md`
- `D:\XM\kaipai-team\.sce\steering\CURRENT_CONTEXT.md`

## 6. 结论

`00-126` 已完成本轮目标：

- dev 运行库中的 `menu.recruit` 已从当前角色数据退场
- 招募矩阵与登录态运行态均已不再暴露 `menu.recruit`
- 当前未改变招募 runtime 放通边界
