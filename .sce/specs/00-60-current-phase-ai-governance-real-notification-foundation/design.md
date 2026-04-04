# 00-60 设计说明

## 1. 设计原则

- 不重复定义 `00-50` 已完成的协同状态模型，也不重复定义 `00-59` 已完成的调度入口
- 只处理一个核心问题：让 AI 治理从“人工记录通知事实”升级为“真实通知基础设施 + 真实回执事实源”
- 明确切断与 login-auth `sendCode` 的概念混用

## 2. 设计策略

### 2.1 三层拆分

本 Spec 将 AI 治理通知链拆成三层：

1. 协同业务层
   - failure / assignee / notificationStatus / receiptStatus / autoRemindStage / slaStatus
   - 已由 `00-50` 建模
2. 调度触发层
   - `governance-sweep` / scheduler / lock / requestId
   - 已由 `00-59` 收口
3. 真实通知基础设施层
   - recipient resolution
   - provider adapter
   - delivery record
   - receipt ingest
   - audit correlation
   - 本 Spec 负责定义

### 2.2 主链与人工兜底拆分

后续实现时统一口径如下：

- 主链：`assign / auto_remind / timeout_escalation` 触发真实通知基础设施
- 回写：真实发送结果与真实回执回写 AI failure 协同事实
- 兜底：后台 `record-notification` / `record-notification-receipt` 仅在供应商异常、历史补录、人工修正时使用

这意味着：

- 后台动作不再是假装“真实通知”
- 人工补录必须显式标成 manual source
- 自动治理动作不能绕过真实通知层直接改协同状态

### 2.3 通道适配边界

本 Spec 不绑定具体供应商，但要求后续实现具备标准适配层：

- 出站请求构造
- 供应商响应解析
- 外部 messageId / taskId / bizId 等追踪字段回收
- 入站回执归并
- 渠道失败重试或显式失败暴露

不允许直接把第三方 SDK 调用散落在 `AdminAiResumeGovernanceServiceImpl` 或页面动作里。

### 2.4 接收人解析

当前仓内已知可复用信息：

- `AdminUser` 已有 `phone / email`
- AI failure 已有 `assignedAdminId / assignedAdminName`

后续实现建议：

- 先建立“治理通知接收人解析器”
- 由解析器统一判断当前责任人是否具备可用接收地址
- 若缺联系方式，失败样本应显式进入“notification_not_ready / recipient_missing”类阻塞，而不是直接假设通知已发

### 2.5 回执采集

真实回执必须有独立入站链路：

- 外部回执原文入站
- 安全校验 / 签名校验
- 归并到 delivery record
- 再映射回 AI failure 的 `notificationReceiptStatus`

后台手工“记录回执”只保留为：

- 历史数据修正
- 供应商缺失回执时的人工补录
- 应急回填

### 2.6 验证与发布

后续实现时应在现有执行入口下继续扩展：

- 优先扩展 `run-ai-resume-collaboration-validation.py` 的真实通知验证段
- 必要时新增独立的通知回执回放脚本，但仍挂在 `execution/ai-resume/` 下统一管理
- schema / nacos / runtime / smoke 必须继续走 `00-29`

### 2.7 `provider-code=http` bridge 输入契约

`http` provider 当前虽然已经具备统一适配层，但目标环境仍不能跳过 bridge 输入契约直接发布。

后续固定口径：

- AI 通知基础 secret 继续只负责：
  - `enabled`
  - `callback-header`
  - `callback-token`
  - provider-aware runtime key
- 新增独立 bridge 输入文件，专门承接：
  - 真实 bridge endpoint
  - 对外 callback base url
  - callback path
  - bridge auth header/token
- `provider=http` 总控必须先读 bridge 输入，再把派生出的 `callback-url / http.endpoint / auth` 注入 `00-29`
- 若 bridge 输入不存在，则标准结果必须是 blocked 记录，而不是继续在 spec 中停留“后续再说”

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

- 建立 AI 治理通知基础设施模型与发送入口
- 建立真实 delivery record 与 receipt ingest 链
- 让 `governance-sweep` 复用真实通知服务，而不是继续只改 failure 状态

### 4.2 后台

- 显式区分“真实发送结果 / 真实回执 / 人工补录”
- 显示接收人联系方式缺失、通道失败、回执异常等基础设施级问题
- 保留人工修正，但不再把它包装成默认主链

### 4.3 验证

- 扩展标准脚本，产出真实通知发送 / 回执样本
- 记录 messageId / callback / failure correlation
- 回写 AI 状态卡与总体评估
