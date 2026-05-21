# 00-130 当前阶段后台 contact-requests IA 元数据对齐（Current Phase Admin Contact Requests IA Metadata Alignment）

> 状态：已完成 | 优先级：中 | 依赖：00-110 current-phase-admin-legacy-route-and-fallback-retirement-audit、00-74 current-phase-admin-reference-ui-architecture-rebuild
> 记录目的：在 `00-110` 审计线下，把 `/content/contact-requests` 当前前后失真的 IA 元数据做成单页最小对齐切片，避免 hidden tooling 页面继续被 route meta 误标为 mainline。

## 1. 背景

截至 `2026-04-23`：

- `admin-information-architecture.ts` 当前把：
  - `/content/contact-requests`
  识别为：
  - `tooling`
- `00-110 legacy-inventory-matrix.md` 当前也已把：
  - `/content/contact-requests`
  定义为：
  - `Retain as hidden tooling`
- 但当前 `router/index.ts` 中该路由仍写成：
  - `architectureLayer: 'mainline'`
  - `architectureArea: 'user-center'`

本轮进一步核实到：

- `AdminTopbar.vue` 的 mainline / tooling 壳层判断依赖：
  - `route.meta.architectureLayer`
- `AdminTopbar.vue` 的 eyebrow / description 依赖：
  - `admin-information-architecture.ts`
- 这意味着当前 `/content/contact-requests` 会出现：
  - 路径口径是 tooling
  - topbar 壳层却按 mainline 渲染

当前判断：

- 这是 IA 元数据失真
- 当前更合理的下一手不是继续删代码，而是先把这一路由的元数据口径收正

## 2. 范围

### 2.1 本轮必须处理

- 新增独立 `00-130`
- 将 `/content/contact-requests` 的 route meta 改回：
  - `architectureLayer = 'tooling'`
  - `architectureArea = 'tooling'`
- 在 `admin-information-architecture.ts` 中补齐该页的明确 tooling 描述
- 通过前端 `type-check` / `build`
- 真实浏览器复核 `/content/contact-requests`

### 2.2 本轮不处理

- 不修改 `page.content.contact-requests` 权限合同
- 不将该页加入正式 8 页侧栏
- 不扩展到其它 hidden tooling 页
- 不修改该页 API、列表、详情或交互逻辑

## 3. 需求

### 3.1 IA 对齐要求

- **R1** `/content/contact-requests` 的 route meta 必须与当前 IA 常量和 `00-110` 审计结论一致，明确归为 hidden tooling。
- **R2** 本轮只修正：
  - `architectureLayer`
  - `architectureArea`
  - tooling 描述文案
  不得顺手扩大到其它页面的 IA 重构。
- **R3** 当前用户可见文案应明确该页属于联系方式授权链路治理工具，而不是正式主导航 mainline 页。

### 3.2 运行态要求

- **R4** `/content/contact-requests` 的页面权限、路由路径和内容治理功能必须保持不变。
- **R5** `AdminTopbar.vue` 在该页应按 tooling 页壳层渲染，不再按 mainline 页隐藏 summary / meta chips。

### 3.3 验证要求

- **R6** 必须通过：
  - `kaipai-admin` 的 `npm run type-check`
  - `kaipai-admin` 的 `npm run build`
- **R7** 必须基于真实浏览器复核：
  - `http://127.0.0.1:5100/content/contact-requests`
- **R8** 截图产物必须落到：
  - `D:\XM\kaipai-team\output\playwright\00-130\`

## 4. 验收标准

- [x] 已新增独立 `00-130`
- [x] `/content/contact-requests` route meta 已切回 tooling 口径
- [x] `admin-information-architecture.ts` 已补齐该页的明确 tooling 描述
- [x] 前端 `type-check` / `build` 已通过
- [x] 真实浏览器已复核 `/content/contact-requests`
- [x] README / mapping / CURRENT_CONTEXT / execution 已回填
