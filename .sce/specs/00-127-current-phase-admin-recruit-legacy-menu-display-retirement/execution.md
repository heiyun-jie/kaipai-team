# 00-127 执行记录

## 1. 当前状态

- 已重新读取 `C:\Users\33340\.codex\memories\user-global-memory.md`
- 已核对 `CURRENT_CONTEXT.md`、`00-126`
- 已对当前 live `8010` 登录态招募矩阵做删除前复核

## 2. 删除前证据

### 2.1 live API 仍暴露 `hasRecruitMenu`

使用后台账号：

- `account = admin`
- `password = <REDACTED>`

当前 live API：

- `GET /admin/system/roles/recruit-governance-matrix`

删除前已确认首项字段仍包含：

- `hasRecruitMenu`

且当前值为：

- `hasRecruitMenu = false`
- `recruitReady = true`

角色详情：

- `GET /admin/system/roles/1`
- `menuPermissions = menu.dashboard, menu.verify, menu.referral, menu.content, menu.system, menu.users`
- 不再包含 `menu.recruit`

依据：

- 本机 `127.0.0.1:8010` 登录态接口直接返回

置信度：

- 高

不确定边界：

- 当前只覆盖本机 dev 运行库；其它环境若仍残留 `menu.recruit`，本轮通过保留前端 registry 历史登记承接编辑 / 详情展示兼容。

### 2.2 代码命中点

已确认 `hasRecruitMenu / menu.recruit` 当前命中：

- `kaipaile-server/src/main/java/com/kaipai/module/model/system/dto/AdminRoleRecruitGovernanceMatrixItemDTO.java`
- `kaipaile-server/src/main/java/com/kaipai/module/server/system/service/impl/AdminRoleServiceImpl.java`
- `kaipai-admin/src/types/system.ts`
- `kaipai-admin/src/views/system/RolesView.vue`
- `kaipai-admin/src/constants/permission.ts`
- `kaipai-admin/src/constants/permission-registry.ts`

本轮判断：

- DTO / service / RolesView / types / 死常量应收口
- `permission-registry.ts` 中历史登记应保留

## 3. 本轮实施

### 3.1 后端矩阵合同收口

已修改：

- `D:\XM\kaipai-team\kaipaile-server\src\main\java\com\kaipai\module\model\system\dto\AdminRoleRecruitGovernanceMatrixItemDTO.java`
- `D:\XM\kaipai-team\kaipaile-server\src\main\java\com\kaipai\module\server\system\service\impl\AdminRoleServiceImpl.java`

本轮已移除：

- `hasRecruitMenu`
- `RECRUIT_MENU_PERMISSION`
- 招募矩阵装配中的 `menuPermissions` 读取和 DTO 回填

当前招募矩阵继续只围绕：

- `page.recruit.*`
- `action.recruit.*`
- `page.system.admin-users` 历史耦合

### 3.2 前端矩阵展示收口

已修改：

- `D:\XM\kaipai-team\kaipai-admin\src\types\system.ts`
- `D:\XM\kaipai-team\kaipai-admin\src\views\system\RolesView.vue`
- `D:\XM\kaipai-team\kaipai-admin\src\constants\permission.ts`

本轮已移除：

- 招募矩阵的 `row.hasRecruitMenu` 标签
- 表单提示中“当前只配置了历史 menu.recruit”的特殊分支
- `PERMISSIONS.menu.recruit` 死常量

同时继续保留：

- `D:\XM\kaipai-team\kaipai-admin\src\constants\permission-registry.ts`
  - `menu.recruit`
  - `招募治理菜单（历史登记）`

当前判断：

- 角色详情 / 编辑弹窗继续具备历史权限可读兼容
- 招募矩阵与提示文案不再继续暴露过期运行态合同

### 3.3 本机 `8010` 运行态刷新

已执行：

- 停掉旧 `8010` Java 进程 `PID 44040`
- 以 `dev` profile 重新启动本机后端到 `8010`

新实例信息：

- 新进程 PID：`23892`
- 日志：
  - `D:\XM\kaipai-team\output\runtime\00-127\backend-8010.out.log`
  - `D:\XM\kaipai-team\output\runtime\00-127\backend-8010.err.log`

日志关键事实：

- `The following 1 profile is active: "dev"`
- `Tomcat started on port 8010 (http) with context path '/api'`

### 3.4 构建验证

已通过：

- `D:\XM\kaipai-team\kaipai-admin`：
  - `npm run type-check`
  - `npm run build`
- `D:\XM\kaipai-team\kaipaile-server`：
  - `mvn -q -DskipTests compile`

补充说明：

- 前端 build 仍输出既有 chunk size warning 与 Sass legacy JS API warning
- 当前未新增新的构建报错

## 4. 验证结果

### 4.1 登录态 API 复核

重新登录后已确认：

- `GET /admin/auth/me`
  - `menuPermissions` 仍为：
    - `menu.dashboard`
    - `menu.verify`
    - `menu.referral`
    - `menu.content`
    - `menu.system`
    - `menu.users`
  - 不包含 `menu.recruit`
- `GET /admin/system/roles/1`
  - `menuPermissions` 仍不包含 `menu.recruit`
- `GET /admin/system/roles/recruit-governance-matrix`
  - 首项字段已不再包含 `hasRecruitMenu`
  - 首项：
    - `recruitReady = true`
    - `rolloutStage = recruit_ready`

依据：

- 本机 `127.0.0.1:8010` 登录态接口直接返回

置信度：

- 高

不确定边界：

- 只覆盖本机 dev 运行库；其它环境若仍保留 `menu.recruit`，当前仅继续由前端 registry 历史登记承接详情 / 编辑兼容。

### 4.2 真实浏览器复核

已使用 Playwright CLI 登录 `http://127.0.0.1:5100/login` 并复核：

- `/system/roles`

截图证据：

- `D:\XM\kaipai-team\output\playwright\00-127\roles-recruit-display-after.png`

当前已确认：

- 招募矩阵说明文案已不再提 `menu.recruit`
- 招募矩阵“权限覆盖”列已不再显示 `历史 menu.recruit`
- 角色目录菜单数仍为 `6`
- 浏览器 console `error` 当前为 `0`

## 5. 结论

`00-127` 已完成本轮目标：

- 招募矩阵 live contract 已不再暴露 `hasRecruitMenu`
- 前后端矩阵展示已完全回到 `page.recruit.* / action.recruit.* + page.system.admin-users` 历史耦合口径
- `menu.recruit` 的历史兼容仅保留在前端 permission registry，可继续承接详情 / 编辑场景，不再污染矩阵运行态合同
