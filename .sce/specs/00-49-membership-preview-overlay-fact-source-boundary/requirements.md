# 00-49 会员预览态事实源边界（Membership Preview Overlay Fact-Source Boundary）

> 状态：已完成 | 优先级：P1 | 依赖：00-28 architecture-driven-delivery-governance，05-11 fortune-driven-share-personalization
> 记录目的：把 membership 当前关于 `preview overlay` 的事实源边界从执行记录升级为独立 Spec，明确哪些字段必须以后端为准，哪些字段只允许保留为前端 session 级未保存预览态。

## 1. 背景

当前 membership 主链已经把模板、能力 gating、主题 token 与分享产物主线收口到：

- `/api/card/personalization`
- `/api/level/info`
- 后台模板发布 / 回滚链

同时，未保存的布局 / 配色预览仍需要在 `actor-card -> detail -> invite` 之间恢复，因此前端保留了 `preview overlay`。

问题已经不再是“overlay 还在不在”，而是：

- 哪些字段仍允许保留为前端 session 级预览态
- 哪些字段绝不能再被 overlay 碰触
- 何时才允许把它升级成后端临时摘要

如果这部分只写在执行记录里，后续很容易再次退回口头争论。

## 2. 范围

### 2.1 本轮必须处理

- 把 membership 的事实源边界固化为独立 Spec
- 把 `preview overlay` 的允许字段、禁止字段和升级门禁写清楚
- 同步回写 `00-28` 路线图、membership 状态卡、总体评估、任务卡、Spec 索引与映射

### 2.2 本轮不处理

- 把 `preview overlay` 立即迁入后端临时摘要
- 新增 membership 运行时代码或接口
- 推翻当前 `session-only` 决策

## 3. 需求

### 3.1 后端事实源边界

- **R1** `/api/card/personalization`、`/api/level/info`、后台模板发布 / 回滚结果，必须继续作为 membership 模板、能力、artifact 与分享主链的权威事实源。
- **R2** 前端不得再用 `preview overlay` 推导模板版本、会员能力、等级能力、artifact 锁定状态、公开分享落点或后台已发布结果。

### 3.2 前端预览态边界

- **R3** `preview overlay` 当前只允许覆盖未保存的 `layoutVariant / primaryColor / accentColor / backgroundColor`。
- **R4** `preview overlay` 当前只允许保留在“当前设备 + 当前 session + 同 actorId + 同 scene”的恢复链里。
- **R5** `preview overlay` 保存成功、重新拉取 personalization、退出当前编辑链路或超出 session 生命周期后，必须失效并回到后端事实源。

### 3.3 升级门禁

- **R6** 只有出现明确新证据时，才允许重新开启“升级为后端临时摘要 / 更强 session 模型”的实现讨论。
- **R7** 可触发升级讨论的新证据只包括：
  - 需要跨登录恢复未保存预览
  - 需要跨设备或跨端恢复未保存预览
  - overlay 字段扩展到模板、artifact、capability 等后端事实
  - session-only 已造成真实分享落点、审核链或运营回查错误

### 3.4 治理回填

- **R8** 必须通过独立 Spec 固化这次边界，不得只停留在 `preview-overlay-governance-baseline.md` 与 `preview-overlay-decision-record.md`
- **R9** `00-28` 路线图、membership 状态卡、总体评估、任务卡、Spec 索引与映射必须同步引用本 Spec

## 4. 验收标准

- [x] 已新增独立 `00-49` Spec 并登记索引与映射
- [x] 已明确区分“后端事实源”和“前端 session 级未保存预览态”
- [x] 已明确 `preview overlay` 的升级触发条件，不再靠口头判断
- [x] `00-28` 路线图、membership 状态卡与总体评估已同步引用本 Spec
