# 00-108 设计说明

## 1. 设计目标

`00-108` 只解决 `system/ai-resume-governance` 中失败治理双表的视觉密度：

1. **wide ledger container**：把 `Failure Samples / Sensitive Hits` 从两列窄卡恢复为单列宽表台账
2. **collaboration compact cell**：把 `责任协同` 中的完整链路从逐行堆叠改为关键标签 + 轻量摘要 + `title` 全量追溯
3. **table density**：局部压低表头、表格 cell、tag、操作按钮与最近处置 cell 的行内节奏

## 2. 已核实的事实

### 2.1 当前残余集中在失败治理双表

真实运行态截图：

- current：`D:\XM\kaipai-team\output\playwright\00-108\ai-governance-before.png`

当前量化：

- `noticeGrid`：`1134 × 8409`
- `Failure Samples` card：`559 × 8409`
- `Sensitive Hits` card：`559 × 8409`
- failure first row：`2100 × 417`
- failure second row：`2100 × 440`
- first collaboration stack：`196 × 400`
- first action wrapper：`476 × 64`

这说明当前主要 residual 不在页面顶层 shell，而在失败治理双表的宽表承载方式与 `责任协同` cell 的信息堆叠方式。

### 2.2 当前运行态边界

真实浏览器 console 仍记录 `loadAuditLogs` 请求错误：

- 来源：`AiResumeGovernanceView.vue:939 loadAuditLogs`
- 表现：`操作失败`

本轮不处理该后端 / operation logs 依赖问题，只把它作为运行态边界记录；不能让它阻塞 UI 密度收口。

## 3. 设计策略

### 3.1 Notice grid 容器

本轮将：

- `notice-grid` 从 `repeat(2, minmax(0, 1fr))` 改为单列
- 让宽表获得完整 admin 内容宽度，避免两个 `559px` 窄卡同时承载 2000px 级宽表
- 两张表增加有限高度表体，让 20 条失败样本以内滚动承接，而不是继续把整页拉成长滚动

### 3.2 责任协同 compact cell

本轮将两张表的 `责任协同` cell 从：

- 责任人 + 协同状态
- 4 个主状态 tag
- 2 个来源 tag
- 签收状态
- 通知摘要
- 投递链
- 排障诊断
- 签收 SLA
- 催办摘要
- 升级目标

收口为：

- 第一行：责任人 + 协同状态
- 第二行：通知 / 回执 / 催办 / SLA 主 tag
- 第三行：通知链路轻量摘要
- 第四行：签收 SLA / 催办 / 升级目标的短摘要
- `title`：保留完整签收、通知、投递链、诊断、SLA、催办、升级目标文本

### 3.3 最近处置与操作列

本轮将：

- 最近处置 cell 保留处理人、时间、记录数量、最近备注，但把备注约束到轻量可截断行
- 操作列仍保留所有按钮，不改变权限和点击逻辑，只压低 gap、link button 高度和字号

## 4. 风险与边界

### 4.1 已确认

- 当前改动只影响 `AiResumeGovernanceView.vue`
- 本轮不改 API、不改权限、不改动作流转
- 完整协同文本仍通过 `title` 与处置记录入口可追溯

### 4.2 待验证

- 单列宽表是否比双列窄卡更适合当前页面滚动节奏
- `责任协同` compact cell 是否明显压低行高
- 操作列按钮压紧后是否仍可读、可点击

因此本轮必须结合：

- 运行态量化
- 浏览器截图
- `type-check / build`

一起验证。
