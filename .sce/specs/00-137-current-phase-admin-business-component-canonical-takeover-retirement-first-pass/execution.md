# 00-137 执行记录

## 1. 当前状态

- 已重新读取 `C:\Users\33340\.codex\memories\user-global-memory.md`
- 已核对 `CURRENT_CONTEXT.md`、`00-110`、`00-136`
- 已确认本轮继续沿 `00-110` 的实现型删除前验证主线推进，不扩展到 hidden tooling 或 fallback

## 2. 删除前证据

### 2.1 本轮目标文件

- `D:\XM\kaipai-team\kaipai-admin\src\components\PageContainer.vue`
- `D:\XM\kaipai-team\kaipai-admin\src\components\PermissionButton.vue`
- `D:\XM\kaipai-team\kaipai-admin\src\components\StatusTag.vue`
- `D:\XM\kaipai-team\kaipai-admin\src\components\layout\PageContainer.vue`
- `D:\XM\kaipai-team\kaipai-admin\src\components\layout\FilterPanel.vue`

### 2.2 business canonical 接管证据

已核实当前运行页大量直接 import：

- `@/components/business/PageContainer.vue`
- `@/components/business/FilterPanel.vue`
- `@/components/business/PermissionButton.vue`
- `@/components/business/StatusTag.vue`

说明：

- 当前后台页面已经由 business 目录承接页面容器、筛选面板、权限按钮和状态标签组件

### 2.3 旧入口无运行时 consumer

已核实 `kaipai-admin/src` 内未命中任何对以下路径的 import / dynamic import：

- `@/components/PageContainer.vue`
- `@/components/PermissionButton.vue`
- `@/components/StatusTag.vue`
- `@/components/layout/PageContainer.vue`
- `@/components/layout/FilterPanel.vue`

### 2.4 文档追溯引用

已核实 `.sce / docs` 当前未发现上述路径追溯引用。

### 2.5 本轮排除对象

已核实：

- `D:\XM\kaipai-team\kaipai-admin\src\components\SearchTableLayout.vue`
- `D:\XM\kaipai-team\kaipai-admin\src\components\tables\SearchTableLayout.vue`

当前也未发现 consumer。

但本轮不处理它们，原因是：

- 它们不属于“business canonical 接管后旧入口”这一证据链
- 更适合后续单独起 spec 核销

依据：

- 组件源码
- `kaipai-admin/src` 搜索结果
- `.sce / docs` 搜索结果

置信度：

- 高

不确定边界：

- 当前判断基于仓内静态证据；删除后仍需以 `type-check/build` 结果做最终闭环。

## 3. 本轮实施

### 3.1 删除动作

本轮已删除：

- `D:\XM\kaipai-team\kaipai-admin\src\components\PageContainer.vue`
- `D:\XM\kaipai-team\kaipai-admin\src\components\PermissionButton.vue`
- `D:\XM\kaipai-team\kaipai-admin\src\components\StatusTag.vue`
- `D:\XM\kaipai-team\kaipai-admin\src\components\layout\PageContainer.vue`
- `D:\XM\kaipai-team\kaipai-admin\src\components\layout\FilterPanel.vue`

### 3.2 本轮明确未处理

本轮保留：

- `D:\XM\kaipai-team\kaipai-admin\src\components\SearchTableLayout.vue`
- `D:\XM\kaipai-team\kaipai-admin\src\components\tables\SearchTableLayout.vue`

原因：

- 当前虽然未发现 consumer
- 但它们不属于本轮“business canonical 接管后旧入口”证据链

## 4. 验证结果

### 4.1 删除后文件状态

删除后已确认：

- `Test-Path 'D:\XM\kaipai-team\kaipai-admin\src\components\PageContainer.vue'` -> `False`
- `Test-Path 'D:\XM\kaipai-team\kaipai-admin\src\components\PermissionButton.vue'` -> `False`
- `Test-Path 'D:\XM\kaipai-team\kaipai-admin\src\components\StatusTag.vue'` -> `False`
- `Test-Path 'D:\XM\kaipai-team\kaipai-admin\src\components\layout\PageContainer.vue'` -> `False`
- `Test-Path 'D:\XM\kaipai-team\kaipai-admin\src\components\layout\FilterPanel.vue'` -> `False`

### 4.2 静态构建验证

命令：

- `cd D:\XM\kaipai-team\kaipai-admin && npm run type-check`
- `cd D:\XM\kaipai-team\kaipai-admin && npm run build`

结果：

- `type-check`：通过
- `build`：通过

保留告警：

- Sass legacy JS API deprecation
- Vite chunk size warning

## 5. 结论

`00-137` 已完成本轮目标：

- 第一批已被 business canonical 接管的旧组件入口已退场
- 当前删除不影响 `components/business/*` 的运行态消费
- `SearchTableLayout` 双版本已显式留待后续独立核销
- 删除后 `type-check` 与 `build` 均通过
