# 00-110 当前阶段后台旧路由 / 旧代码 / fallback 退场审计（Current Phase Admin Legacy Route and Fallback Retirement Audit）

> 状态：已完成 | 优先级：最高 | 依赖：00-74 current-phase-admin-reference-ui-architecture-rebuild，00-109 current-phase-admin-system-operation-logs-degraded-state-alignment
> 记录目的：在后台 reference-driven 8 页主导航已稳定后，把“仍保留的隐藏路由、fallback 兼容、候删文件、正式页真实后端绑定”做成独立审计 spec，为后续删除旧代码与下线兼容逻辑提供依据。

## 1. 背景

截至 `2026-04-22`：

- 当前后台正式导航已经恢复为 reference 的 8 页结构：
  - 仪表盘
  - 数据分析
  - 用户管理
  - 机构管理
  - 分享内容
  - 风格模板
  - 运营动作
  - 系统设置
- 当前 `00-74 ~ 00-109` 已完成连续精修，说明正式运行态框架已基本稳定
- 但用户提出的两个核心问题仍未完成独立审计闭环：
  1. 旧代码是否都已经删除
  2. 新页面是否已经连通后端

当前只读核查已确认：

1. `router/index.ts` 仍保留大量 `tooling` 路由，不在正式 8 页导航中
2. `menus.ts` 中 `adminMenus` 仍是 full capability inventory，正式侧栏只是 `adminSidebarMenus` 投影
3. `DashboardView.vue`、`ReferralRiskView.vue`、`PlaceholderView.vue` 仍在仓内，但当前 `rg` 未命中引用
4. `stores/permission.ts` 与多个治理页仍保留 `fallbackPermissions / fallback` 授权模式
5. 正式 8 页大多已绑定真实 API，但需要做一张统一审计矩阵，明确：
   - 哪些是正式主线页
   - 哪些是隐藏治理页
   - 哪些是候删文件
   - 哪些仍依赖 fallback
   - 哪些页面已接真实后端事实源

## 2. 范围

### 2.1 本轮必须处理

- 新增独立 `00-110`
- 审计以下 4 类对象：
  - 后台正式 8 页主导航
  - 隐藏治理工具页 / 兼容路由
  - 仓内疑似未引用候删文件
  - fallback 权限与兼容依赖
- 固化正式 8 页与后端事实源的绑定矩阵
- 为后续真正删除旧代码提供 retain / retire / verify-before-delete 分类依据

### 2.2 本轮不处理

- 不直接删除任何旧文件
- 不直接下线任何 fallback 逻辑
- 不改动正式 8 页 UI
- 不修 operation logs 后端事实源
- 不扩展新业务能力

## 3. 需求

### 3.1 审计边界

- **R1** 本 spec 必须区分“正式主线页”“隐藏治理页”“候删文件”“兼容 fallback”，不能把它们混在一起描述。
- **R2** 本轮所有结论必须建立在路由、菜单、代码引用、API 装配和后端 controller 存在性的事实上。
- **R3** 没有运行态或代码引用证据时，不得直接把文件判定为可删除。

### 3.2 旧代码 / 路由审计合同

- **R4** 必须列出当前正式 8 页之外仍保留在 router / adminMenus 中的隐藏治理页。
- **R5** 必须列出当前仓内疑似未被 router / menu / import 引用的候删文件。
- **R6** 必须明确哪些页面 / 权限仍依赖 fallback 模式，哪些已经完成独立授权收口。
- **R7** 必须明确“旧代码未删除”到底是因为：
  - 仍有运行态依赖
  - 仍是治理工具页
  - 只是历史残留 / 候删文件

### 3.3 新页面后端连通性合同

- **R8** 必须对正式 8 页逐页标明其真实后端事实源。
- **R9** 必须明确区分：
  - 已接真实后端
  - 已接接口但事实源异常
  - 只复用聚合接口
- **R10** 不得把“前端可访问”误判成“业务后端已闭环”。

### 3.4 交付要求

- **R11** 本轮必须回填：
  - `.sce/specs/README.md`
  - `.sce/specs/spec-code-mapping.md`
  - `.sce/steering/CURRENT_CONTEXT.md`
- **R12** 本轮必须在 `execution.md` 中记录现有审计证据与下一步删除前验证口径。
- **R13** 后续若进入真实删除阶段，必须另起实现型切片，不得在本 spec 内直接顺手删除。

## 4. 验收标准

- [x] 已新增独立 `00-110` spec，并明确它只做旧路由 / 旧代码 / fallback / API 绑定审计
- [x] 已形成正式 8 页、隐藏治理页、候删文件、fallback 依赖的分类口径
- [x] 已形成正式 8 页的后端绑定矩阵
- [x] 已回填 README / mapping / CURRENT_CONTEXT / execution
