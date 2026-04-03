# 00-50 设计说明

## 1. 设计原则

- 不重复证明已经收口的最小协同链，而是把剩余治理缺口单独建模
- 不让“通知回执 / 自动催办 / SLA”继续散落在状态文档里
- 继续遵守 `00-28` 的能力切片方式：数据、后端、后台、验证同轮收口

## 2. 设计策略

### 2.1 三层协同模型

本 Spec 把 AI 失败样本的治理协同拆成三层：

1. 人工基础层
   - assign
   - acknowledge
   - manual remind
2. 协同增强层
   - notification send
   - receipt status
   - remind plan
   - SLA window
3. 自动治理层
   - auto remind
   - timeout escalation
   - manual takeover / skip

当前仓内已完成第 1 层，本 Spec 负责把第 2、3 层定义成下一轮标准推进入口。

### 2.2 事实源统一

后续实现时统一口径如下：

- 协同状态、通知回执、催办阶段和 SLA 结果以后端为准
- 后台页只负责展示、筛选、人工干预和审计回看
- 标准验证脚本负责生成可复跑样本，不允许再退回手工临时命令

### 2.3 标准样本扩展点

现有样本入口 `run-ai-resume-collaboration-validation.py` 已覆盖：

- `assign -> acknowledge`
- `assign -> remind`
- 协同状态筛选
- 审计回看

后续应基于同一入口继续扩展：

- 通知发送与回执样本
- 自动催办样本
- SLA 超时与升级样本

## 3. 影响文件

- `.sce/specs/00-28-architecture-driven-delivery-governance/phase-01-roadmap.md`
- `.sce/specs/00-28-architecture-driven-delivery-governance/status/ai-resume-status.md`
- `.sce/specs/00-28-architecture-driven-delivery-governance/status/overall-architecture-assessment.md`
- `.sce/specs/00-28-architecture-driven-delivery-governance/tasks.md`
- `.sce/specs/00-28-architecture-driven-delivery-governance/execution/ai-resume/README.md`
- `.sce/specs/README.md`
- `.sce/specs/spec-code-mapping.md`

## 4. 后续实现分层

### 4.1 后端

- 补齐协同状态模型与通知回执字段
- 补齐自动催办与 SLA 规则执行入口
- 补齐新增操作日志与只读查询接口

### 4.2 后台

- 补齐通知状态、自动催办阶段、SLA 超时筛选
- 补齐手工接管、跳过自动催办、查看回执等治理动作
- 补齐协同时间线展示

### 4.3 验证

- 扩展 `run-ai-resume-collaboration-validation.py`
- 产出通知回执、自动催办、SLA 超时三类标准样本
- 回写 `ai-resume-status.md` 与 `overall-architecture-assessment.md`
