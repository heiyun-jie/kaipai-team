# 邀请裂变与邀请资格闭环执行卡

本目录用于承接 `slices/invite-referral-capability-slice.md` 的下一层拆分。

## 目标

把“邀请裂变与邀请资格闭环”从能力切片继续拆成可分派、可并行推进、可单独验收的 4 张执行卡：

1. 前端执行卡
2. 后端执行卡
3. 后台执行卡
4. 联调执行卡

补充一张用于真实环境验收收口的执行清单：

5. `real-env-validation-checklist.md`
6. `real-env-evidence-pack.md`
7. `real-env-runtime-inventory.md`
8. `validation-sample-ledger-template.md`
9. `collect-invite-evidence.ps1`
10. `invite-validation-template.sql`
11. `validation-execution-example.md`

## 使用方式

每张执行卡都只负责一个交付面，但必须引用同一张能力切片卡：

- `../../slices/invite-referral-capability-slice.md`

## 本轮规则

- 每张卡都要写清楚负责范围，不得跨层级抢活
- 每张卡都要标明依赖项和交付物
- 联调卡不负责补做功能，只负责收口验证、问题清单和回归要求
- 当前必须先收口小程序 `invite` 命名与服务端 `referral` 模块的契约断层，再继续三端联调
- 真实环境验证必须按“邀请码样本 -> 注册绑定 -> 记录生成 -> 风险 / 资格 -> 前台同步”的同一样本链追踪，不允许分段各自口头确认
