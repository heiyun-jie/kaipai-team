# 实名认证闭环执行卡

本目录用于承接 `slices/verify-capability-slice.md` 的下一层拆分。

## 目标

把“实名认证闭环”从能力切片继续拆成可分派、可并行推进、可单独验收的 4 张执行卡：

1. 前端执行卡
2. 后端执行卡
3. 后台执行卡
4. 联调执行卡

补充一组用于真实环境验收收口的执行资产：

5. `real-env-runtime-inventory.md`
6. `real-env-validation-checklist.md`
7. `real-env-evidence-pack.md`
8. `validation-sample-ledger-template.md`
9. `verify-validation-template.sql`
10. `collect-verify-evidence.ps1`
11. `new-verify-validation-sample.ps1`
12. `run-verify-validation.ps1`
13. `run-end-to-end-verify-closure.py`
14. `run-remote-validation-sql.py`
15. `validation-execution-example.md`
16. `run-verify-mini-program-page-evidence.py`
17. `run-verify-admin-page-evidence.py`

## 使用方式

每张执行卡都只负责一个交付面，但必须引用同一张能力切片卡：

- `../../slices/verify-capability-slice.md`

## 本轮规则

- 每张卡都要写清楚负责范围，不得跨层级抢活
- 每张卡都要标明依赖项和交付物
- 联调卡不负责补做功能，只负责收口验证、问题清单和回归要求
- 当前 verify 已完成“提交 -> 拒绝 -> 重提 -> 通过”标准样本和前后台页面级证据；后续所有推进都必须继续围绕这条标准样本链与页面脚本复验
- verify 样本必须同时固定 actor 侧状态、后台审核记录和 DB 两条申请单证据，不能再只拿 invite 闭环间接侧证 verify

## 工具补充

- `run-verify-validation.ps1` 会自动创建一份 verify 样本目录，复制 `sample-ledger.md` 与 `validation.sql`，调用 `collect-verify-evidence.ps1` 生成接口侧证据，并统一回填 `sample-ledger.md / validation-report.md`
- `run-end-to-end-verify-closure.py` 会自动创建新演员样本，跑通“提交 -> 拒绝 -> 重提 -> 通过”，并回调 `run-verify-validation.ps1` 生成正式样本目录
- `run-remote-validation-sql.py` 会把样本目录下的 `validation.sql` 上传到标准远端 helper 所在环境执行，把结果写回 `validation-result.txt`，再自动把数据库证据回填到 `sample-ledger.md / validation-report.md`
- `run-verify-mini-program-page-evidence.py` 会基于最新 verify 闭环样本回放小程序 `/pkg-card/verify/index`，并在同一份页面样本里固定 `verify/status`、`level/info` 与 `user/me` 摘要、页面截图和 `page-data`
- `run-verify-admin-page-evidence.py` 会基于最新 verify 闭环样本回放后台 `/verify/pending` 与 `/verify/history`，并同时保留待审核空队列截图、历史列表 / 详情抽屉截图，以及 `admin/verify/list`、`admin/verify/{id}` 回包

## 当前标准样本入口

- 主链闭环样本：`samples/20260403-054934-dev-remote-verify-after-schema-gated-release/validation-report.md`
- 小程序页面样本：`samples/20260404-021512-continue-verify-mini-page-evidence/summary.md`
- 后台页面样本：`samples/20260404-021512-continue-verify-admin-page-evidence/summary.md`
- 当前页面级证据入口：
  - `run-verify-mini-program-page-evidence.py`
  - `run-verify-admin-page-evidence.py`
- 当前后续要求：
  - verify 后续复验必须优先复用上述两个页面脚本，不再回退到手工零散截图
  - `validation-sample-ledger-template.md` 已补齐页面证据段，后续同类样本应把“小程序 / 后台页面目录、截图和 page-data”一起回填
