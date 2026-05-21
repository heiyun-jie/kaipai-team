# 00-141 执行记录

## 1. 当前状态

- 已重新读取 `C:\Users\33340\.codex\memories\user-global-memory.md`
- 已核对 `CURRENT_CONTEXT.md`、`00-140`
- 已确认本轮按用户指定顺序先执行 A：彻底删除机构管理页面本体

## 2. 删除前证据

### 2.1 目标残留

删除前后台前端仍存在：

- `D:\XM\kaipai-team\kaipai-admin\src\router\index.ts`
  - `/users/orgs`
  - `component: () => import('@/views/user/OrganizationsView.vue')`
- `D:\XM\kaipai-team\kaipai-admin\src\views\user\OrganizationsView.vue`
- `D:\XM\kaipai-team\kaipai-admin\src\api\company.ts`
- `D:\XM\kaipai-team\kaipai-admin\src\types\company.ts`

### 2.2 consumer 核查

删除前搜索确认：

- `fetchCompanyProfile` 只被 `OrganizationsView.vue` 使用
- `CompanyProfile` 只被 `OrganizationsView.vue` 使用
- `@/api/company` 与 `@/types/company` 只服务机构管理页面

依据：

- `rg "机构管理|/users/orgs|OrganizationsView|fetchCompanyProfile|CompanyProfile|api/company|types/company" kaipai-admin/src .sce`
- `router/index.ts`
- `OrganizationsView.vue`
- `api/company.ts`
- `types/company.ts`

置信度：

- 高

不确定边界：

- `.sce` 与 release records 中仍有历史追溯文字，不作为运行时残留。
- 后端 `/company/{userId}` 与小程序端公司档案能力未纳入本轮。

## 3. 本轮实施

### 3.1 删除 route

已从 `router/index.ts` 删除：

- `/users/orgs`
- `users-orgs`
- `OrganizationsView.vue` 动态 import

### 3.2 删除页面与专用依赖

已删除：

- `D:\XM\kaipai-team\kaipai-admin\src\views\user\OrganizationsView.vue`
- `D:\XM\kaipai-team\kaipai-admin\src\api\company.ts`
- `D:\XM\kaipai-team\kaipai-admin\src\types\company.ts`

### 3.3 范围边界

本轮未处理：

- 小程序端 `pages/company-profile/edit`
- 后端 company controller / service / DTO
- `.sce` 历史 specs 与历史截图中的追溯文字

## 4. 验证结果

### 4.1 静态搜索

删除后已执行：

- `rg "OrganizationsView|fetchCompanyProfile|CompanyProfile|@/api/company|@/types/company|/users/orgs" kaipai-admin/src`

结果：

- `kaipai-admin/src` 内无命中。

### 4.2 文件存在性

删除后已确认：

- `OrganizationsView.vue` -> `False`
- `api/company.ts` -> `False`
- `types/company.ts` -> `False`

### 4.3 静态构建验证

已执行：

- `cd D:\XM\kaipai-team\kaipai-admin && npm run type-check`
- `cd D:\XM\kaipai-team\kaipai-admin && npm run build`

结果：

- `type-check`：通过
- `build`：通过

保留告警：

- Sass legacy JS API deprecation
- Vite chunk size warning

### 4.4 真实浏览器复核

已重新启动本机运行态：

- 前端：`http://127.0.0.1:5100`
- 后端：`http://127.0.0.1:8010/api`

已使用 Playwright CLI 登录并访问：

- `http://127.0.0.1:5100/users/orgs`

结果：

- 页面标题为 `页面不存在 | 开拍了后台`
- 已不再进入机构管理页面

截图证据：

- `D:\XM\kaipai-team\output\playwright\00-142\users-orgs-not-found.png`

## 5. 结论

`00-141` 已完成 A：

- 后台 `/users/orgs` route 已删除
- 机构管理页面本体已删除
- 页面专用 company API / 类型已删除
- 静态搜索、`type-check`、`build` 与真实浏览器直达验证均通过
