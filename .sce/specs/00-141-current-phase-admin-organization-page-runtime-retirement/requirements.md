# 00-141 当前阶段后台机构管理页面本体退场（Current Phase Admin Organization Page Runtime Retirement）

> 状态：已完成 | 优先级：最高 | 依赖：00-140 current-phase-admin-shell-ia-and-template-config-alignment、00-110 current-phase-admin-legacy-route-and-fallback-retirement-audit
> 记录目的：在 `00-140` 已让机构管理退出正式导航和正式矩阵后，继续按用户指定的 A 步骤，彻底删除后台机构管理页面本体及其前端专用 API / 类型残留。

## 1. 背景

截至 `2026-04-23`：

- `00-140` 已完成：
  - 正式侧栏不再展示 `机构管理`
  - 仪表盘正式页面矩阵不再展示 `机构管理`
  - `/users/orgs` 已从 `mainline / growth` 降为 `retire-candidate / tooling`
- 当前最新架构已经明确删除机构相关后台信息，不再把机构管理作为正式后台模块维护。
- 当前代码中仍存在机构管理页面本体：
  - `kaipai-admin/src/views/user/OrganizationsView.vue`
  - `kaipai-admin/src/router/index.ts` 中 `/users/orgs`
  - `kaipai-admin/src/api/company.ts`
  - `kaipai-admin/src/types/company.ts`

当前判断：

- `/users/orgs` 已经退出正式架构，因此继续保留页面本体会让后台存在可直达的过期模块。
- `fetchCompanyProfile / CompanyProfile` 当前只被 `OrganizationsView.vue` 消费，随页面一起退场风险可控。
- 本轮只处理后台管理端机构管理页面本体，不处理小程序端剧组档案编辑页，也不删除后端 `/company/{userId}` 公共接口。

依据：

- `00-140` 执行记录
- `rg "机构管理|/users/orgs|OrganizationsView|fetchCompanyProfile|CompanyProfile" kaipai-admin/src .sce`
- 当前 `router/index.ts / OrganizationsView.vue / api/company.ts / types/company.ts`

置信度：

- 高

不确定边界：

- `.sce` 历史 specs 和 release records 中会继续保留机构管理的历史追溯文字，不作为运行时残留判定。
- 后端 `/company/{userId}` 可能仍被小程序端使用，本轮不触碰后端接口。

## 2. 范围

### 2.1 本轮必须处理

- 删除后台 `/users/orgs` route。
- 删除后台机构管理页面：
  - `kaipai-admin/src/views/user/OrganizationsView.vue`
- 删除后台机构管理页面专用 API / 类型：
  - `kaipai-admin/src/api/company.ts`
  - `kaipai-admin/src/types/company.ts`
- 删除后核查 `kaipai-admin/src` 内不再命中：
  - `OrganizationsView`
  - `/users/orgs`
  - `fetchCompanyProfile`
  - `@/api/company`
  - `@/types/company`
- 通过：
  - `npm run type-check`
  - `npm run build`
- 回填：
  - `.sce/specs/README.md`
  - `.sce/specs/spec-code-mapping.md`
  - `.sce/steering/CURRENT_CONTEXT.md`
  - `execution.md`

### 2.2 本轮不处理

- 不删除小程序端 `pages/company-profile/edit`。
- 不删除后端 company controller / service / DTO。
- 不清理 `.sce` 历史 specs 中的历史追溯记录。
- 不扩展处理其它 `retire-candidate` 或 hidden tooling 页面。

## 3. 需求

### 3.1 删除门禁

- **R1** 删除前必须确认目标文件和 route 的当前唯一职责是后台机构管理页面本体。
- **R2** 删除前必须确认 `fetchCompanyProfile / CompanyProfile` 没有其它后台前端 consumer。
- **R3** 删除必须限于本轮列出的页面、route、API 与类型，不扩大到后端或小程序端。

### 3.2 运行态要求

- **R4** 后台路由中不得继续存在 `/users/orgs`。
- **R5** 后台源码中不得继续存在 `OrganizationsView` 动态导入或页面文件。
- **R6** 后台源码中不得继续存在 `@/api/company` 与 `@/types/company` consumer。

### 3.3 验证要求

- **R7** 删除后必须通过 `npm run type-check`。
- **R8** 删除后必须通过 `npm run build`。
- **R9** 执行记录必须写明删除前证据、删除动作、删除后搜索结果与验证结果。

## 4. 验收标准

- [x] 已删除 `/users/orgs` route
- [x] 已删除 `OrganizationsView.vue`
- [x] 已删除 `api/company.ts`
- [x] 已删除 `types/company.ts`
- [x] `kaipai-admin/src` 内不再命中机构管理页面本体运行时引用
- [x] `type-check / build` 通过
- [x] README / mapping / CURRENT_CONTEXT / execution 已回填
