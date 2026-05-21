# 00-141 设计说明

## 1. 设计目标

`00-141` 只处理 A：彻底删除后台机构管理页面本体。

本轮目标不是重新定义机构数据，也不是删除公司档案业务能力，而是把已经退出最新后台架构的机构管理后台页面从运行时代码中退场。

## 2. 已核实事实

### 2.1 当前仍存在的运行时残留

当前仍存在：

- `router/index.ts`
  - `/users/orgs`
  - `component: () => import('@/views/user/OrganizationsView.vue')`
- `views/user/OrganizationsView.vue`
  - 页面标题、筛选、目录、详情抽屉
  - 消费 `fetchCompanyProfile`
- `api/company.ts`
  - 仅导出 `fetchCompanyProfile`
- `types/company.ts`
  - 仅导出 `CompanyProfile`

### 2.2 当前退场理由

`00-140` 已经确认：

- 最新正式侧栏不再展示机构管理。
- 最新仪表盘正式矩阵不再展示机构管理。
- `/users/orgs` 已降为 `retire-candidate`。

用户随后明确要求继续执行 A，即彻底删除机构管理页面本体。

## 3. 设计策略

### 3.1 删除 route

从 `router/index.ts` 删除 `/users/orgs` route 对象。

理由：

- route 仍会让模块可通过 URL 直达。
- 既然页面本体删除，route 必须同步删除，不能留下动态 import 指向不存在文件。

### 3.2 删除页面本体

删除：

- `kaipai-admin/src/views/user/OrganizationsView.vue`

理由：

- 当前页面已经不是正式后台主线页。
- 页面本体保留会继续制造过期功能维护成本。

### 3.3 删除专用 API 与类型

删除：

- `kaipai-admin/src/api/company.ts`
- `kaipai-admin/src/types/company.ts`

理由：

- 当前 `fetchCompanyProfile / CompanyProfile` 的后台前端 consumer 只剩 `OrganizationsView.vue`。
- 页面删除后继续保留会成为零 consumer 残留。

## 4. 风险与边界

### 4.1 已确认

- 本轮不触碰小程序端公司 / 剧组档案页面。
- 本轮不触碰后端 `/company/{userId}`。
- 本轮不清理 `.sce` 历史记录中的机构管理历史文字。

### 4.2 待验证

- 删除后 `kaipai-admin/src` 是否仍有隐式 import 或字符串依赖。

验证方式：

- `rg` 静态搜索
- `npm run type-check`
- `npm run build`
