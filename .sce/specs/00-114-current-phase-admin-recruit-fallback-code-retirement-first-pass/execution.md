# 00-114 执行记录

## 1. 当前状态

- 已重新读取 `C:\Users\33340\.codex\memories\user-global-memory.md`
- 已核对 `CURRENT_CONTEXT.md`、`README.md`、`spec-code-mapping.md`、`00-110`、`00-113`
- 已确认当前主线可从“运行库直授权前提补齐”进入“runtime fallback 代码退场”

## 2. 删除前证据

### 2.1 当前 dev 运行库门禁

承接 `00-113` 已核实结果：

- `pageFallbackRoleCount = 0`
- `actionFallbackRoleCount = 0`
- `fallbackRoleCount = 0`
- `fallbackBoundUserCount = 0`

### 2.2 当前代码侧 fallback 入口

前端：

- `D:\XM\kaipai-team\kaipai-admin\src\stores\permission.ts`
- `D:\XM\kaipai-team\kaipai-admin\src\views\recruit\ProjectsView.vue`
- `D:\XM\kaipai-team\kaipai-admin\src\views\recruit\RolesView.vue`
- `D:\XM\kaipai-team\kaipai-admin\src\views\recruit\AppliesView.vue`

后端：

- `D:\XM\kaipai-team\kaipaile-server\src\main\java\com\kaipai\module\controller\admin\recruit\AdminRecruitController.java`
- `D:\XM\kaipai-team\kaipaile-server\src\main\java\com\kaipai\common\auth\RecruitGovernanceFallbackGate.java`
- `D:\XM\kaipai-team\kaipaile-server\src\main\java\com\kaipai\module\server\adminauth\service\impl\AdminAuthServiceImpl.java`
- `D:\XM\kaipai-team\kaipaile-server\src\main\java\com\kaipai\module\model\adminauth\dto\AdminSessionInfoDTO.java`

## 3. 本轮实施

### 3.1 前端

已完成：

- `permission.ts` 不再自动给 `page.recruit.* / action.recruit.*` 注入 `page.system.admin-users` fallback
- 招募三个 hidden tooling 页已移除 runtime fallback 提示
- 招募项目 / 招募角色页的状态动作按钮已移除 `fallback-permissions` 传参

### 3.2 后端

已完成：

- `AdminRecruitController.java` 改为 direct authority only
- `RecruitGovernanceFallbackGate.java` 已删除
- `AdminAuthServiceImpl.java` 不再装配 `allowLegacyRecruit*`
- `AdminSessionInfoDTO.java` 已移除对应字段

### 3.3 矩阵文案

已完成：

- 招募矩阵用户可见文案已从“当前 runtime fallback”切换为：
  - 历史后台账号页耦合
  - 页面直授权待补
  - 动作直授权待补
  - 历史耦合已清零 / 仍有历史耦合

本轮未做：

- 未改矩阵 DTO / API 字段命名

## 4. 验证结果

### 4.1 前端

命令：

- `cd D:\XM\kaipai-team\kaipai-admin && npm run type-check`
- `cd D:\XM\kaipai-team\kaipai-admin && npm run build`

结果：

- `type-check`：通过
- `build`：通过

保留告警：

- Sass legacy JS API deprecation
- Vite chunk size warning

### 4.2 后端

命令：

- `cd D:\XM\kaipai-team\kaipaile-server && mvn -q -DskipTests compile`

结果：

- `compile`：通过

## 5. 结论

`00-114` 已完成本轮目标：

- recruit runtime fallback 第一批已退场
- 当前代码已只认 direct `page.recruit.* / action.recruit.*`
- 招募矩阵继续保留为历史耦合审计视图

当前边界：

- 本轮默认以 `00-113` migration 已先执行到目标环境为发布前提
- 若后续继续推进，应进入下一张切片，决定是否继续清理招募矩阵中的 fallback 字段命名与历史文案残留
