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

截至 `2026-04-04`，Phase 01 已完成三层沉淀：

1. 4 张能力切片卡已产出
2. 4 组前端 / 后端 / 后台 / 联调执行卡已产出
3. 状态卡、真实样本与 `00-29` 标准发布 / 诊断 / schema 记录已经开始闭环联动

当前四个能力切片的真实基线如下：

| 能力切片 | 当前判定 | 当前结论 |
|----------|----------|----------|
| 实名认证闭环 | 闭环完成 | 小程序认证页、后台审核页和演员端公开接口已具备，真实环境 `提交 -> 拒绝 -> 重提 -> 通过` 样本、页面级证据脚本与正式页面样本均已闭环；后续进入维护态复验 |
| 邀请裂变与邀请资格闭环 | 局部完成 | 前台邀请页、后台治理、演员端 `/invite/*` 查询接口和注册绑定落库已具备，资格链真实样本已闭环；当前阶段先按注册链接/普通二维码与资格链闭环验收，微信官方 `wxacode` 已降级为后续能力批次 |
| 会员能力与模板配置闭环 | 局部完成 | 后台治理、演员端 `/level/info`、`/card/*`、`/card/personalization`、`/fortune/*` 与最小 actor 输出已具备，后台动作 / API / DB / 后台 UI / 小程序页面证据现已并入正式样本，preview overlay 也已有静态审计入口；最新 no-fortune rollback 样本已证明 `actor-card / detail / invite` 三页都会随模板 rollback 改变并在 restore 后恢复，且 overlay 已进一步收口为 session-only 主链，但它仍不是后端事实源 |
| AI 简历润色闭环 | 局部完成（主链样本、页面证据、最小治理协同、服务端定时 sweep 与 `00-60` 通知基础设施已收口） | `/ai/quota`、`/ai/polish-resume`、history / rollback 最小真接口已补齐，编辑页 patch 流程、角色矩阵、前后台页面证据、目标环境业务回归与最小治理协同已接上真实数据；当前又已通过 `00-59` 把手动 `governance-sweep` 收口为服务端内建定时任务，并已在 `2026-04-04 05:01:40 +0800` 捕获首轮目标环境运行样本；同日 `07:36 +0800` 又已按 `00-29` 标准链路跑通 `00-60` 的 delivery / dispatch / callback 基础设施样本，因此当前剩余主阻塞已从“缺真实通知基础设施”收口为“商用通知 vendor 实发链深化与真实 LLM 仍未接入” |

此外，login-auth 当前阶段也已通过手机号主链、注册链与页面证据样本收口为“当前阶段闭环完成”；微信能力与正式短信能力分别由 `00-48`、`00-51` 保留为后续能力批次；recruit 当前阶段前端 mock 退场已由 `00-53` 独立固化，actor 主线前端 mock 退场已由 `00-54` 独立固化，invite / verify / fortune 当前阶段前端 mock 退场已由 `00-55` 独立固化，membership / AI 当前阶段残留的 `level / card / ai` 运行时双轨也已由 `00-56` 独立固化，`session / upload` 的独立 runtime capability 也已由 `00-57` 收口，而前端 runtime capability 表本身也已由 `00-58` 退场。

按架构反推后的真实开发顺序，当前建议调整为：

1. AI 简历润色闭环
2. 会员能力与模板配置闭环
3. 登录认证闭环
4. 邀请裂变与邀请资格闭环

说明：

- verify 主链与页面级证据都已通过真实样本证实，当前已不再占用主实现排期。
- verify 后续进入“标准脚本复验”维护态，不再作为当前阶段主阻塞。

## 下一步建议

- 第一优先级：以 `00-60 current-phase-ai-governance-real-notification-foundation` 为入口，继续补 AI 简历商用通知 vendor 实发链 / 更真实 provider 回执链；当前 delivery / dispatch / callback 基础设施已在真实环境验证通过，`http provider` 也已补 bridge 输入契约和标准总控，后续缺口已进一步收口为真实 bridge endpoint/credential 与真实 LLM。
- 第二优先级：membership 继续以 `00-49 membership-preview-overlay-fact-source-boundary` 作为治理入口，基于 `run-preview-overlay-static-audit.py`、`run-admin-template-rollback-mini-program-no-fortune-theme.py` 与 `preview-overlay-decision-record.md` 维护 preview overlay 的升级门禁；没有新证据前，不再新开 overlay 后端化实现项。
- 第三优先级：以 `00-52 current-phase-invite-record-page-boundary-alignment` 为入口，继续把 invite 当前阶段边界收口到“记录页 + 登录承接邀请码 + 分享入口留在 actor-card/membership”；login-auth 当前阶段转入维护态复验，微信登录、官方 `wxacode` 与正式短信能力分别保留在 `00-48 / 00-51` 后续批次，不再作为当前阶段主阻塞。
- 第四优先级：verify 仅在认证契约、审核页或 schema 变化时复用标准页面脚本增量复验，不再单独开新实现项。
- recruit 补充说明：`00-53 current-phase-crew-recruit-mock-retirement` 已把 `company / project / role / apply` 的前端 mock 分支退场；recruit 后续剩余问题不再回到页面 mock 修补，而只围绕兼容层长期治理、后台持续授权和二期产品边界继续推进。
- actor 补充说明：`00-54 current-phase-actor-mainline-mock-retirement` 已把 `actor search / detail / mine / update` 的前端 mock 分支退场；演员主线后续剩余问题不再是“要不要继续保留 actor mock”，而是公开详情路由边界、本人档案冗余读取链与其他能力域对 `mockActors` 的历史依赖何时继续退场。
- invite / verify / fortune 补充说明：`00-55 current-phase-invite-verify-fortune-mock-retirement` 已把三条当前阶段辅助能力的前端 mock 分支退场；后续 invite 的主问题回到页面边界与微信后续批次，verify 转入维护态复验，fortune 则继续作为 membership 主线真实样本的一部分维护。
- membership / AI 补充说明：`00-56 current-phase-level-card-ai-runtime-mock-retirement` 已把 `level / card / ai` 前端双轨与 personalization 本地 fallback 退场；后续 membership 的主问题继续收口为 `00-49` 定义的 preview overlay 事实源边界，AI 的主问题则继续收口为 `00-60` 定义的商用通知 vendor 实发链 / 更真实 provider 回执链，以及真实 LLM 接入。
- login-auth / upload 补充说明：`00-57 current-phase-session-upload-runtime-boundary-alignment` 已把 `userInfo / roleSwitch / upload` 从独立 runtime capability 收口为“显式 mock 演示态或真实接口”；后续登录域剩余问题只回到 `00-48 / 00-51`，上传域若继续推进则应围绕真实样本和错误暴露，而不是恢复独立 mock 能力。
- auth runtime 补充说明：`00-58 current-phase-auth-runtime-boundary-alignment` 已删除前端 runtime capability 表；后续 auth 域若继续推进，只允许围绕“显式 mock 演示态总闸”与 `00-48 / 00-51` 的微信 / 正式短信门禁继续治理。

## 本轮推进原则

1. 每张切片卡都必须覆盖数据、后端、后台、小程序、联调、验收。
2. 每张执行卡都只负责一个交付面，但必须对齐同一张能力切片。
3. 每轮实现后必须回填 `status` 文档，而不是只改任务勾选。
4. 若某条能力本轮只能做到局部完成，必须明确“局部完成”的边界。
5. 若能力涉及 DB 结构变化，必须先走 `00-29` 标准 schema 发布，再允许正式 `backend-only`。

## 建议并行方式

### Thread A

AI 简历 `00-60 / 00-59` 商用通知 vendor / 回执深化与治理调度维护

### Thread B

membership `00-49` 门禁维护与正式样本复用

### Thread C

verify 闭环维护与标准脚本复验

### Thread D

invite 当前阶段记录页边界治理（`00-52`）+ login-auth 维护态复验；微信与正式短信能力仅保留未来批次入口

## 统一收口要求

并行产出完成后，主线程统一做四件事：

1. 校正状态文档中的“当前判定 / 联调结论 / 验收判断”
2. 回填执行卡实际完成项和遗留阻塞项
3. 更新 `00-28/tasks.md` 的下一轮执行项
4. 只有在六条闭环条件同时满足时，才允许把状态从“局部完成”改成“闭环完成”
