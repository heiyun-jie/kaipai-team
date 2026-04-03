# 00-28 Phase 01 路线图

## 目标

把 `00-28` 从“推进原则”推进到“可直接排开发、可持续回填状态”的第一轮执行包。

本轮仍以 4 个能力切片作为统一推进入口：

1. 实名认证闭环
2. 邀请裂变与邀请资格闭环
3. 会员能力与模板配置闭环
4. AI 简历润色闭环

## 本轮交付物

- `slices/verify-capability-slice.md`
- `slices/invite-referral-capability-slice.md`
- `slices/membership-template-capability-slice.md`
- `slices/ai-resume-polish-capability-slice.md`
- `execution/verify/*`
- `execution/invite/*`
- `execution/membership/*`
- `execution/ai-resume/*`
- `status/verify-status.md`
- `status/invite-status.md`
- `status/membership-status.md`
- `status/ai-resume-status.md`

## 当前结果

截至 `2026-04-03`，Phase 01 已完成三层沉淀：

1. 4 张能力切片卡已产出
2. 4 组前端 / 后端 / 后台 / 联调执行卡已产出
3. 状态卡、真实样本与 `00-29` 标准发布 / 诊断 / schema 记录已经开始闭环联动

当前四个能力切片的真实基线如下：

| 能力切片 | 当前判定 | 当前结论 |
|----------|----------|----------|
| 实名认证闭环 | 局部完成 | 小程序认证页、后台审核页和演员端公开接口已具备，真实环境 `提交 -> 拒绝 -> 重提 -> 通过` 样本已闭环；当前仅剩页面级证据待补 |
| 邀请裂变与邀请资格闭环 | 局部完成 | 前台邀请页、后台治理、演员端 `/invite/*` 查询接口和注册绑定落库已具备，资格链真实样本已闭环；当前阶段先按注册链接/普通二维码与资格链闭环验收，微信官方 `wxacode` 已降级为后续能力批次 |
| 会员能力与模板配置闭环 | 局部完成 | 后台治理、演员端 `/level/info`、`/card/*`、`/card/personalization`、`/fortune/*` 与最小 actor 输出已具备，后台动作 / API / DB / 小程序截图证据较完整，preview overlay 也已有静态审计入口；最新 no-fortune rollback 样本已证明 `actor-card / detail / invite` 三页都会随模板 rollback 改变并在 restore 后恢复，且 overlay 已进一步收口为 session-only 主链，但它仍不是后端事实源 |
| AI 简历润色闭环 | 局部完成（最小权威接口与后台治理入口已落位） | `/ai/quota`、`/ai/polish-resume`、history / rollback 最小真接口已补齐，编辑页 patch 流程与后台治理已接上真实数据，但目标环境角色绑定、真机联调和真实 AI 生成仍未完成 |

按架构反推后的真实开发顺序，当前建议调整为：

1. 会员能力与模板配置闭环
2. AI 简历润色闭环
3. 登录认证闭环
4. 邀请裂变与邀请资格闭环

说明：

- verify 主链的接口 / DB / 后台闭环已经通过真实样本证实，不再是第一优先级实现阻塞。
- verify 后续优先级降为“页面级证据收口”，不再占用主实现排期。

## 下一步建议

- 第一优先级：继续补 membership 的页面级边界，并基于 `run-preview-overlay-static-audit.py`、`run-admin-template-rollback-mini-program-no-fortune-theme.py` 与 `preview-overlay-decision-record.md` 维护 preview overlay 的升级门禁；没有新证据前，不再重复口头争论是否立即后端化。
- 第二优先级：为 AI 简历补目标环境角色绑定回填、真机联调和更细治理状态流转。
- 第三优先级：把 verify 的页面级截图补齐后，从“局部完成”提升到更稳定的闭环判定。
- 第四优先级：继续收口 invite / login-auth 当前版本验收面中的非微信部分；微信登录与官方 `wxacode` 保留为后续能力批次，不再作为当前阶段主阻塞。

## 本轮推进原则

1. 每张切片卡都必须覆盖数据、后端、后台、小程序、联调、验收。
2. 每张执行卡都只负责一个交付面，但必须对齐同一张能力切片。
3. 每轮实现后必须回填 `status` 文档，而不是只改任务勾选。
4. 若某条能力本轮只能做到局部完成，必须明确“局部完成”的边界。
5. 若能力涉及 DB 结构变化，必须先走 `00-29` 标准 schema 发布，再允许正式 `backend-only`。

## 建议并行方式

### Thread A

membership 页面边界与前后台一致性证据补齐

### Thread B

AI 简历目标环境角色绑定、真机联调与治理链补齐

### Thread C

verify 页面级证据与文档收尾

### Thread D

invite / login-auth 当前版本非微信验收面回填；微信能力仅保留未来批次入口

## 统一收口要求

并行产出完成后，主线程统一做四件事：

1. 校正状态文档中的“当前判定 / 联调结论 / 验收判断”
2. 回填执行卡实际完成项和遗留阻塞项
3. 更新 `00-28/tasks.md` 的下一轮执行项
4. 只有在六条闭环条件同时满足时，才允许把状态从“局部完成”改成“闭环完成”
