# 「开拍了」Spec 索引

> 命名格式：`XX-YY-功能名称/`（XX=大类, YY=子编号）
> 全局技术约定见 `SHARED_CONVENTIONS.md`，Spec↔代码映射见 `spec-code-mapping.md`

## 增量登记

- `00-12 admin-role-permission-tree`：后台角色权限树形编排，详见 `00-12-admin-role-permission-tree/`
- `00-13 admin-user-role-binding-guard`：后台账号角色绑定联动校验，详见 `00-13-admin-user-role-binding-guard/`
- `00-14 admin-user-form-guard`：后台账号表单校验与高风险原因约束，详见 `00-14-admin-user-form-guard/`
- `00-15 finance-date-range-filters`：财务后台日期范围筛选回接，详见 `00-15-finance-date-range-filters/`
- `00-16 admin-operator-copy-optimization`：后台运营文案优化，详见 `00-16-admin-operator-copy-optimization/`
- `00-17 admin-dashboard-hierarchy-optimization`：后台工作台层级优化，详见 `00-17-admin-dashboard-hierarchy-optimization/`
- `00-18 admin-page-style-alignment`：后台页面共享壳层对齐工作台风格，详见 `00-18-admin-page-style-alignment/`
- `00-19 admin-verify-page-refinement`：实名认证审核页二次优化，详见 `00-19-admin-verify-page-refinement/`
- `00-20 admin-filter-inline-alignment`：后台筛选区横向对齐，详见 `00-20-admin-filter-inline-alignment/`
- `00-22 admin-table-action-overflow-fix`：后台表格操作列防穿透，详见 `00-22-admin-table-action-overflow-fix/`
- `00-21 admin-filter-control-reuse`：后台筛选输入样式复用，详见 `00-21-admin-filter-control-reuse/`
- `00-23 admin-fixed-column-layer-fix`：后台固定列层级防穿透修复，详见 `00-23-admin-fixed-column-layer-fix/`
- `00-24 admin-fixed-column-hover-layer-fix`：后台固定列悬浮层级修复，详见 `00-24-admin-fixed-column-hover-layer-fix/`
- `00-25 admin-fixed-column-sticky-cell-fix`：后台固定列 sticky 单元格层级修复，详见 `00-25-admin-fixed-column-sticky-cell-fix/`
- `00-27 mini-program-frontend-architecture`：小程序前端架构总览，详见 `00-27-mini-program-frontend-architecture/`
- `00-28 architecture-driven-delivery-governance`：架构驱动的项目推进治理，详见 `00-28-architecture-driven-delivery-governance/`

---

## Spec 目录

### 00 — 全局基础

| 编号 | Spec | 说明 | 文件 |
|------|------|------|------|
| 00-01 | global-style-system | Design Tokens + SCSS 变量 + 玻璃拟态 Mixin + 页面骨架 | requirements.md, design.md |
| 00-02 | shared-components | 23 个 Kp 前缀共享组件（Props/Events/Slots/复用矩阵） | requirements.md, design.md |
| 00-03 | shared-utils-api | TypeScript 类型 + 请求封装 + Store + 6 个 API 模块 | requirements.md, design.md |
| 00-04 | document-governance | 当前主线文档、归档策略、Spec 入口与映射治理 | requirements.md, design.md, tasks.md |
| 00-05 | mini-program-package-governance | 微信小程序包体治理、2MB 约束、审计脚本与分包迁移基线 | requirements.md, design.md, tasks.md |
| 00-06 | bundle-size-first-pass | 首批减体积优化：去组件 barrel 聚合层与失效入口 | requirements.md, design.md, tasks.md |
| 00-07 | first-subpackage-migration | 第一批真实分包迁移：名片 / 会员 / 工具页迁出主包 | requirements.md, design.md, tasks.md |
| 00-08 | style-system-governance | 样式体系减负和升级治理：Sass `@import` 收口到 `@use/@forward` | requirements.md, design.md, tasks.md |
| 00-09 | shared-style-shells | 公共样式壳层抽离：返回按钮与底部操作栏 mixin 收敛 | requirements.md, design.md, tasks.md |
| 00-10 | platform-admin-backend-architecture | 平台后台与服务端架构：运营后台、会员订单退款、邀请资格、模板配置与数据库蓝图 | requirements.md, design.md, tasks.md |
| 00-11 | platform-admin-console | 平台后台管理端：后台 Web 菜单、页面、权限、审核与配置产品基线 | requirements.md, design.md, tasks.md |
| 00-12 | admin-role-permission-tree | 后台角色权限树形编排：角色编辑从原始权限码多选升级为结构化树形授权 | requirements.md, design.md, tasks.md |
| 00-16 | admin-operator-copy-optimization | 后台运营文案优化：把接口导向文案收敛为运营任务说明 | requirements.md, design.md, tasks.md |
| 00-17 | admin-dashboard-hierarchy-optimization | 后台工作台层级优化：拉开状态、按钮和正文的视觉主次 | requirements.md, design.md, tasks.md |
| 00-18 | admin-page-style-alignment | 后台页面风格统一：通过共享页头、筛选区和卡片壳层对齐工作台视觉语言 | requirements.md, design.md, tasks.md |
| 00-19 | admin-verify-page-refinement | 实名认证审核页二次优化：修复筛选输入可见性，并补齐概览、空态和详情层级 | requirements.md, design.md, tasks.md |
| 00-20 | admin-filter-inline-alignment | 后台筛选区横向对齐：标签与输入同一行，并在共享筛选壳层中统一垂直居中 | requirements.md, design.md, tasks.md |
| 00-22 | admin-table-action-overflow-fix | 后台表格固定操作列防穿透：共享按钮组换行容器并回接高风险页面 | requirements.md, design.md, tasks.md |
| 00-27 | mini-program-frontend-architecture | 小程序前端架构总览：页面层、共享组件层、状态/API 层、分包治理与当前主线总纲 | requirements.md, design.md, tasks.md |
| 00-28 | architecture-driven-delivery-governance | 架构驱动的项目推进治理：工作流分组、能力切片、优先级顺序与跨工程闭环验收 | requirements.md, design.md, tasks.md |

### 01 — 公共页面

| 编号 | Spec | 页面路径 | 文件 |
|------|------|---------|------|
| 01-01 | page-login | pages/login/index | requirements.md, design.md |
| 01-02 | page-role-select | pages/role-select/index | requirements.md, design.md |

### 02 — 首页

| 编号 | Spec | 页面路径 | 文件 |
|------|------|---------|------|
| 02-01 | page-home-actor | pages/home/index (role=1) | requirements.md, design.md |
| 02-02 | page-home-crew | pages/home/index (role=2) | requirements.md, design.md |

### 03 — 演员端页面

| 编号 | Spec | 页面路径 | 文件 |
|------|------|---------|------|
| 03-01 | page-role-detail | pages/role-detail/index | requirements.md, design.md |
| 03-02 | page-apply-confirm | pages/apply-confirm/index | requirements.md, design.md |
| 03-03 | page-my-applies | pages/my-applies/index | requirements.md, design.md |
| 03-04 | page-actor-profile-edit | pages/actor-profile/edit | requirements.md, design.md |
| 03-05 | page-mine | pages/mine/index (Tab 2) | requirements.md, design.md |

### 04 — 剧组端页面（已迁移至平台后台，代码保留）

| 编号 | Spec | 页面路径 | 文件 |
|------|------|---------|------|
| 04-01 | page-project-create | pages/project/create | requirements.md, design.md |
| 04-02 | page-role-create | pages/project/role-create | requirements.md, design.md |
| 04-03 | page-apply-manage | pages/apply-manage/index | requirements.md, design.md |
| 04-04 | page-actor-profile-detail | pages/actor-profile/detail | requirements.md, design.md |
| 04-05 | page-company-profile-edit | pages/company-profile/edit | requirements.md, design.md |

### 05 — 演员增强功能（V1.1 新增）

| 编号 | Spec | 页面路径 | 文件 |
|------|------|---------|------|
| 05-01 | actor-card | pages/actor-card/index | requirements.md, design.md, tasks.md |
| 05-02 | actor-profile-enhance | pages/actor-profile/edit（增强） | requirements.md, design.md, tasks.md |
| 05-03 | credit-score | pages/credit-score/index, pages/credit-record/index, pages/credit-rank/index | requirements.md, design.md, tasks.md |
| 05-04 | ai-resume-polish | pages/actor-profile/edit（AI 对话式全档案文本润色） | requirements.md |
| 05-05 | card-share-membership (v2) | pkg-card/actor-card/index, pkg-card/membership/index, pages/actor-profile/detail | requirements.md, design.md, tasks.md |
| 05-06 | mainline-residual-cleanup | pages/mine/index, pages/actor-profile/edit（当前主线残余清理） | requirements.md, design.md, tasks.md |
| 05-07 | mainline-component-refactor | 当前主线重复代码抽取（导航 / 媒体选择 / 轻量展示组件 / 包体约束） | requirements.md, design.md, tasks.md |
| 05-08 | fortune-personalization | pkg-card/fortune/index（命理画像：生肖/星座/紫微斗数/幸运色） | requirements.md, design.md, tasks.md |
| 05-09 | identity-verification | pkg-card/verify/index（实名认证提交与审核） | requirements.md, design.md, tasks.md |
| 05-10 | invite-referral | pkg-card/invite/index（邀请裂变：邀请码/计数/等级驱动） | requirements.md, design.md, tasks.md |
| 05-11 | fortune-driven-share-personalization | pkg-card/actor-card/index, pkg-card/membership/index, pkg-card/fortune/index, pkg-card/invite/index, pages/actor-profile/detail（命理驱动的千人千面分享主线） | requirements.md, design.md, tasks.md |

> 05-01 保留为早期名片方案；当前主线以 05-05 v2 为准。
> 05-03 信用积分 / 排行榜在当前产品阶段搁置，不进入当前分支实现。
> 05-05 v2 架构重设计：从 basic/pro 二元会员改为邀请驱动 6 级 + 场景名片 + 命理个性化，当前主线代码已切到 `level + scene + config + quota`。
> 05-06 用于承接 05-05 重构后的主线残余清理，不新增业务能力。
> 05-07 用于承接当前主线的高重复代码重构，先抽行为逻辑，再补低风险展示组件，并显式约束小程序包体增长。
> 05-08 独立功能模块，命理数据供名片定制消费，依赖外部 AI 大模型。
> 05-09 等级体系前置条件，05-10 邀请资格前置条件。
> 05-10 等级计算数据来源，改造注册流程支持邀请码。
> 05-11 为当前下一阶段架构治理 Spec：命理从独立功能升级为个性化输入源，会员能力从页面级升级为分享产物级；后续 05-05 / 05-08 / 05-10 的实现调整必须以 05-11 为准。

---

## 组件复用矩阵

| 组件 | 01-01 | 01-02 | 02-01 | 02-02 | 03-01 | 03-02 | 03-03 | 03-04 | 03-05 | 04-01 | 04-02 | 04-03 | 04-04 | 04-05 | 05-01 | 05-02 | 05-03 | 05-04 | 05-05 |
|------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|
| KpPageLayout | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | |
| KpNavBar | | | | | ✓ | ✓ | ✓ | ✓ | | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | | ✓ | | ✓ |
| KpButton | ✓ | ✓ | | ✓ | ✓ | ✓ | | ✓ | | ✓ | ✓ | | | ✓ | ✓ | ✓ | | ✓ | ✓ |
| KpCard | | ✓ | | | | | | | | | | | | | ✓ | | ✓ | ✓ | |
| KpInput | ✓ | | | | | | | ✓ | | ✓ | ✓ | | | ✓ | | ✓ | | | |
| KpTextarea | | | | | | ✓ | | ✓ | | ✓ | ✓ | | | ✓ | | ✓ | | ✓ | |
| KpFormItem | ✓ | | | | | | | ✓ | | ✓ | ✓ | | | ✓ | | ✓ | | | |
| KpTag | | | ✓ | | ✓ | | | ✓ | | | ✓ | | ✓ | | ✓ | ✓ | | | |
| KpStatusTag | | | ✓ | ✓ | | | ✓ | | | | | ✓ | | | | | | | |
| KpRoleCard | | | ✓ | | | | | | | | | | | | | | | | |
| KpProjectCard | | | | ✓ | | | | | | | | | | | | | | | |
| KpApplyCard | | | | | | | ✓ | | | | | ✓ | | | | | | | |
| KpActorBrief | | | | | | ✓ | | | | | | ✓ | | | | | | | |
| KpFilterBar | | | ✓ | | | | | | | | | | | | | | | | |
| KpImageUploader | | | | | | | | ✓ | | | | | | | | ✓ | | | |
| KpVideoUploader | | | | | | | | ✓ | | | | | | | | | | | |
| KpEmpty | | | ✓ | ✓ | | | ✓ | | | | | ✓ | | | | | ✓ | | |
| KpTabBar | | | ✓ | ✓ | | | | | ✓ | | | | | | | | | | |
| KpConfirmDialog | | ✓ | | | | ✓ | | | ✓ | | | ✓ | | | | | | | |

---

## 追溯关系

- 每个页面 `design.md` 通过 `_Requirements: 3.X_` 追溯到对应 `requirements.md`
- 每个页面 `design.md` 的依赖清单引用 `00-02-shared-components` 的组件编号
- 每个页面 `design.md` 的 API 依赖引用 `00-03-shared-utils-api` 的函数签名
- 所有样式引用 `00-01-global-style-system` 的 Design Tokens

## 开发顺序建议

```
V1 基础（已完成）：
00-01 → 00-02 → 00-03（全局基础）
  → 01-01 → 01-02（登录流程）
  → 02-01 → 03-01 → 03-02（演员主链路：首页→详情→投递）
  → 03-05 → 03-04 → 03-03（演员辅助：我的→编辑→投递记录）
  → 02-02 → 04-01 → 04-02（剧组主链路：首页→发项目→发角色）
  → 04-03 → 04-04 → 04-05（剧组辅助：投递管理→演员详情→剧组编辑）

V1.1 演员增强：
  → 05-02（档案美化：先拆分 edit.vue，再加新板块）
  → 05-04（AI 简历润色：对话式优化全档案文本）
  → 05-05（名片分享主线：actor-card + membership + 公开详情页）
  → 05-01（早期名片方案，历史保留）
  → 05-03（信用积分：当前阶段搁置）

V1.2 架构治理：
  → 05-11（命理驱动的分享定制主线：统一主题、分享产物、会员分层）
  → 05-05 / 05-08 / 05-10（按 05-11 约束依次回接实现）
```
