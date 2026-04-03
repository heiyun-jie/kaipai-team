# 00-49 设计说明

## 1. 设计原则

- 不因为仍存在前端预览态，就否认后端主事实已经建立
- 不因为后端主事实已经建立，就把所有未保存编辑态都强行后端化
- 让“允许暂留”与“禁止越界”同时清楚

## 2. 设计策略

### 2.1 双层模型显式化

本 Spec 把 membership 当前个性化主线拆成两层：

1. 后端事实层
   - 模板
   - capability
   - artifact
   - publish / rollback 结果
   - 公开分享 path
2. 前端预览层
   - 仅当前设备 session 中的未保存布局 / 配色覆盖

### 2.2 事实源表述统一

统一口径如下：

- `/card/personalization` 是分享个性化主事实源
- `preview overlay` 只是 `unsaved preview only`
- 没有新证据前，当前继续保持 `session-only`

### 2.3 升级讨论门禁化

不再把“要不要后端化 overlay”作为常驻讨论项，而是改成证据门禁：

- 默认动作：继续维护当前 `session-only` 边界
- 只有命中新证据时，才允许新开升级 Spec

## 3. 影响文件

- `.sce/specs/00-28-architecture-driven-delivery-governance/phase-01-roadmap.md`
- `.sce/specs/00-28-architecture-driven-delivery-governance/status/membership-status.md`
- `.sce/specs/00-28-architecture-driven-delivery-governance/status/overall-architecture-assessment.md`
- `.sce/specs/00-28-architecture-driven-delivery-governance/tasks.md`
- `.sce/specs/00-28-architecture-driven-delivery-governance/execution/membership/preview-overlay-governance-baseline.md`
- `.sce/specs/00-28-architecture-driven-delivery-governance/execution/membership/preview-overlay-decision-record.md`
- `.sce/specs/README.md`
- `.sce/specs/spec-code-mapping.md`
