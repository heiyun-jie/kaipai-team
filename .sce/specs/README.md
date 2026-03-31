# 「开拍了」Spec 索引

> 命名格式：`XX-YY-功能名称/`（XX=大类, YY=子编号）
> 全局技术约定见 `SHARED_CONVENTIONS.md`，Spec↔代码映射见 `spec-code-mapping.md`

## 增量登记

- `00-12 admin-role-permission-tree`：后台角色权限树形编排，详见 `00-12-admin-role-permission-tree/`
- `00-13 admin-user-role-binding-guard`：后台账号角色绑定联动校验，详见 `00-13-admin-user-role-binding-guard/`
- `00-14 admin-user-form-guard`：后台账号表单校验与高风险原因约束，详见 `00-14-admin-user-form-guard/`
- `00-15 finance-date-range-filters`：财务后台日期范围筛选回接，详见 `00-15-finance-date-range-filters/`

---

## Spec 目录

### 00 — 全局基础

| 编号 | Spec | 说明 | 文件 |
|------|------|------|------|
| 00-01 | global-style-system | Design Tokens + SCSS 变量 + 玻璃拟态 Mixin + 页面骨架 | requirements.md, design.md |
| 00-02 | shared-components | 19 个 Kp 前缀共享组件（Props/Events/Slots/复用矩阵） | requirements.md, design.md |
| 00-03 | shared-utils-api | TypeScript 类型 + 请求封装 + Store + 6 个 API 模块 | requirements.md, design.md |

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
| 05-01 | actor-card | pages/actor-card/index | requirements.md, design.md |
| 05-02 | actor-profile-enhance | pages/actor-profile/edit（增强） | requirements.md, design.md |
| 05-03 | credit-score | pages/credit-score/index, pages/credit-record/index, pages/credit-rank/index | requirements.md, design.md |
| 05-04 | ai-resume-polish | pages/actor-profile/edit（AI 对话式全档案文本润色） | requirements.md, design.md |

> 05-03 单轨积分制：从 0 叠加到 100，积分区间直接映射演员等级 LV.1-7

---

## 组件复用矩阵

| 组件 | 01-01 | 01-02 | 02-01 | 02-02 | 03-01 | 03-02 | 03-03 | 03-04 | 03-05 | 04-01 | 04-02 | 04-03 | 04-04 | 04-05 | 05-01 | 05-02 | 05-03 | 05-04 |
|------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|
| KpPageLayout | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| KpNavBar | | | | | ✓ | ✓ | ✓ | ✓ | | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | | ✓ | |
| KpButton | ✓ | ✓ | | ✓ | ✓ | ✓ | | ✓ | | ✓ | ✓ | | | ✓ | ✓ | ✓ | | ✓ |
| KpCard | | ✓ | | | | | | | | | | | | | ✓ | | ✓ | ✓ |
| KpInput | ✓ | | | | | | | ✓ | | ✓ | ✓ | | | ✓ | | ✓ | | |
| KpTextarea | | | | | | ✓ | | ✓ | | ✓ | ✓ | | | ✓ | | ✓ | | ✓ |
| KpFormItem | ✓ | | | | | | | ✓ | | ✓ | ✓ | | | ✓ | | ✓ | | |
| KpTag | | | ✓ | | ✓ | | | ✓ | | | ✓ | | ✓ | | ✓ | ✓ | | |
| KpStatusTag | | | ✓ | ✓ | | | ✓ | | | | | ✓ | | | | | | |
| KpRoleCard | | | ✓ | | | | | | | | | | | | | | | |
| KpProjectCard | | | | ✓ | | | | | | | | | | | | | | |
| KpApplyCard | | | | | | | ✓ | | | | | ✓ | | | | | | |
| KpActorBrief | | | | | | ✓ | | | | | | ✓ | | | | | | |
| KpFilterBar | | | ✓ | | | | | | | | | | | | | | | |
| KpImageUploader | | | | | | | | ✓ | | | | | | | | ✓ | | |
| KpVideoUploader | | | | | | | | ✓ | | | | | | | | | | |
| KpEmpty | | | ✓ | ✓ | | | ✓ | | | | | ✓ | | | | | ✓ | |
| KpTabBar | | | ✓ | ✓ | | | | | ✓ | | | | | | | | | |
| KpConfirmDialog | | ✓ | | | | ✓ | | | ✓ | | | ✓ | | | | | | |
| KpCreditBadge | | | | | | | | | | | | | | | ✓ | | ✓ | |
| KpLevelTag | | | | | | | | | | | | | | | ✓ | ✓ | ✓ | |

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
  → 05-01（分享明信片：actor-card + 改造 actor-profile/detail）
  → 05-03（信用积分：预留）
```