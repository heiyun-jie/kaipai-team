# 实名认证闭环状态回填

## 1. 归属切片

- `../slices/verify-capability-slice.md`
- `../execution/verify/README.md`

## 2. 当前判定

- 回填日期：`2026-04-04`
- 当前判定：`闭环完成`
- 一句话结论：实名认证前端、小程序后端、后台审核和真实环境“提交 -> 拒绝 -> 重提 -> 通过”标准样本已经闭环，且 `00-29` 已补齐标准 schema 发布脚本与门禁；`2026-04-04` 又继续把小程序 `/pkg-card/verify/index` 与后台 `/verify/pending | /verify/history` 的页面级证据收口成标准脚本与真实样本，`validation-sample-ledger-template.md` 也已补齐页面证据段，因此 verify 当前阶段已从“只差页面证据”提升为“页面 + 接口 + DB + 审计”四类证据并存的闭环完成状态。

## 3. 当前已确认事实

### 3.1 前端 / 小程序

- `kaipai-frontend/src/pkg-card/verify/index.vue` 已提供认证资料填写、档案完成度校验、拒绝原因展示与重提入口。
- 认证页提交前置判断已复用 `/level/info` 返回的后端 `profileCompletion`，不再使用前端本地算法。
- `stores/user.ts`、`pkg-card/membership/index.vue`、`pkg-card/actor-card/index.vue` 已统一消费 `realAuthStatus / isCertified`。
- `2026-04-04` 已通过 `00-55` 删除 `src/api/verify.ts` 中的 `useApiMock('verify')` 分支，verify 当前统一只走真实 `/api/verify/status`、`/api/verify/submit`。

### 3.2 后端 / 数据

- `VerifyController`、`AdminVerifyController`、`IdentityVerificationServiceImpl` 已覆盖演员端提交 / 状态查询与后台列表 / 详情 / 通过 / 拒绝。
- `IdentityVerificationServiceImpl.submit(...)` 现已改为：
  - 同证件跨账号仍按 `id_card_hash` 去重。
  - 同账号拒绝后重提允许新建申请单，保留历史审核记录。
- 本轮已新增：
  - `identity_verification_owner` 归属表
  - `V20260403_001__identity_verification_resubmit_history.sql`
- 该 migration 已在真实环境执行，`schema_release_history` 已留档 `V20260403_001__identity_verification_resubmit_history.sql`，且 `identity_verification.uk_identity_verification_id_card_hash` 已替换为普通索引 `idx_identity_verification_id_card_hash`。

### 3.3 后台治理

- `kaipai-admin/src/views/verify/VerificationBoard.vue` 已具备待审核 / 历史记录、详情抽屉、通过 / 拒绝动作。
- `admin_operation_log` 已固定保留 `reject / approve` 两条审核动作，可回看每次处理结果。

### 3.4 发布治理

- `00-29` 已补齐标准 schema 发布入口 `run-backend-schema-migration.py`。
- `run-backend-only-release.py` 已新增 schema 前置门禁：远端 `schema_release_history` 未建或本地 `db/migration` 存在未执行脚本时，标准 `backend-only` 会直接中止。
- 本轮真实记录：
  - `.sce/runbooks/backend-admin-release/records/20260403-054040-backend-schema-verify-history-baseline.md`
  - `.sce/runbooks/backend-admin-release/records/20260403-054130-backend-schema-verify-resubmit-history-fix.md`
  - `.sce/runbooks/backend-admin-release/records/20260403-054754-backend-only-verify-resubmit-history-fix-schema-gated.md`

### 3.5 页面级证据入口

- `execution/verify/run-verify-mini-program-page-evidence.py` 已成为 verify 小程序页面级证据的标准入口。
- `execution/verify/run-verify-admin-page-evidence.py` 已成为 verify 后台页面级证据的标准入口。
- `validation-sample-ledger-template.md` 已补齐“小程序 / 后台页面证据”段，后续 verify 正式样本不再只回填接口、日志与 DB。

## 4. 联调现状

- `2026-04-03 05:33` 已按 `00-29` 标准只读诊断入口确认新代码上线后首次 `verify/submit` 仍失败的真实根因为：目标库缺少 `identity_verification_owner`，不是后端代码再次写错。
- `2026-04-03 05:40` 已通过标准 schema 发布脚本先把 `V20260331_001 / 002` 基线登记到 `schema_release_history`。
- `2026-04-03 05:42` 已通过同一标准 schema 发布脚本正式执行 `V20260403_001__identity_verification_resubmit_history.sql`。
- `2026-04-03 05:49` 已在最新 `backend-only` 发布后的运行时再次跑通真实样本 `execution/verify/samples/20260403-054934-dev-remote-verify-after-schema-gated-release/`：
  - `userId=10021`
  - `phone=13903054934`
  - `firstVerificationId=12`
  - `retryVerificationId=13`
- 同一样本 `validation-report.md` 已确认：
  - `verifyRecordCount=2`
  - 第一条 `rejected`
  - 第二条 `approved`
  - actor 最终 `status=2`
  - `/level/info.isCertified=True`
- 同一样本 `validation-result.txt` 已继续确认：
  - `schema_release_history` 中存在 `V20260403_001__identity_verification_resubmit_history.sql`
  - `identity_verification` 当前只保留普通索引 `idx_identity_verification_id_card_hash`
  - `identity_verification_owner.user_id=10021`
  - `identity_verification` 两条记录主键不同：`12 / 13`
  - `admin_operation_log` 中存在 `reject(target_id=12)` 与 `approve(target_id=13)` 两条动作
- `2026-04-04 02:15` 已通过 `execution/verify/run-verify-mini-program-page-evidence.py` 产出样本 `execution/verify/samples/20260404-021512-continue-verify-mini-page-evidence/summary.md`：
  - 页面实际路由固定为 `pkg-card/verify/index`
  - 截图当前走 `automator`，无窗口兜底
  - 同一样本 `page-data-verify-page.json` 已固定 `verify/status.status=2`、`level/info.isCertified=true`、`user/me.realAuthStatus=2`
- 同时也已通过 `execution/verify/run-verify-admin-page-evidence.py` 产出样本 `execution/verify/samples/20260404-021512-continue-verify-admin-page-evidence/summary.md`：
  - `/verify/pending` 已固定“当前没有待审核申请”的队列清空截图与 `admin/verify/list(status=1)` 回包
  - `/verify/history` 已固定 2 条历史记录列表、详情抽屉，以及 `admin/verify/{retryVerificationId}` 的真实回包
  - 同一样本 `page-data-admin-verify-history.json` 已证明历史页列表与详情抽屉均和接口明细一致

## 5. 联调结论

- 当前是否具备三端联调条件：`已具备，且标准 reject/retry/approve 样本与页面证据均已闭环`
- 已确认走通的链路：
  - 小程序实名提交
  - 后台拒绝并写回原因
  - 前台刷新看到 `status=3`
  - 同账号重提生成新申请单
  - 后台审核通过
  - `user.real_auth_status=2`
  - `actor_profile.is_certified=true`
  - `/level/info.isCertified=true`
- 当前闭环依据：
  - 接口、DB、审计链已由 `20260403-054934-dev-remote-verify-after-schema-gated-release` 固定
  - 小程序认证页已由 `20260404-021512-continue-verify-mini-page-evidence` 固定
  - 后台审核页已由 `20260404-021512-continue-verify-admin-page-evidence` 固定

## 6. 验收判断

| 闭环条件 | 状态 | 说明 |
|----------|------|------|
| 上位 Spec 已存在并对齐 | 已满足 | `05-09`、`00-28`、`00-29` 与 verify 执行资产已对齐 |
| 数据模型、接口、状态流转清楚 | 已满足 | 拒绝后重提、跨账号证件去重、审核回写与历史保留均已通过真实样本与 DB 回读证实 |
| 后台治理入口可操作 | 已满足 | 列表、详情、通过 / 拒绝与操作日志均可用 |
| 小程序或前台用户侧落点可验证 | 已满足 | `/pkg-card/verify/index` 已有真实页面截图、`page-data` 与 `verify/status / level/info / user/me` 同包证据 |
| 关键日志、权限、限额或回滚约束已接入 | 已满足 | 标准日志诊断、schema 发布、backend-only 门禁和审核操作日志都已接通 |
| 文档、映射表、验证记录已回填 | 已满足 | 样本、发布记录、页面级证据入口、样本模板与状态卡均已同步 |

## 7. 当前阻塞项

- 当前阶段无高优先级阻塞项。
- verify 后续已进入“闭环维护”状态；只有当认证契约、后台页面结构或审计链再次变化时，才需要重跑标准样本复验。

## 8. 下一轮最小动作

1. 后续 verify 复验统一复用 `run-verify-mini-program-page-evidence.py` 与 `run-verify-admin-page-evidence.py`，不再手工截图。
2. 若后续再次涉及 schema 或审核链改动，继续先走 `00-29` schema 发布，再重跑主链闭环样本与页面样本。
3. 主推进重心已可切到 membership `00-49` 门禁维护、AI `00-50` 治理协同升级，以及 invite / login-auth 当前版本非微信验收面。

## 9. 回填记录

### 2026-04-01

- 当前判定：`局部完成`
- 备注：先建立状态基线，结论以当前仓内代码现实为准，不把后台自证完成误判为实名认证闭环完成

### 2026-04-02

- 当前判定：`局部完成`
- 备注：认证页完成度前置判断已切到后端 `profileCompletion`，但真实环境联调仍未补齐

### 2026-04-03（第一次回填）

- 当前判定：`局部完成`
- 备注：已借 invite 样本跑通实名 happy path，但拒绝 / 重提专项样本仍缺

### 2026-04-03（第二次回填）

- 当前判定：`局部完成`
- 备注：
  - 已通过标准诊断确认 reject/retry 新代码上线后仍失败的根因为目标库未执行新 migration
  - 已通过标准 schema 发布脚本补齐 baseline 与 `V20260403_001`
  - 已通过 verify 样本 `20260403-054934-dev-remote-verify-after-schema-gated-release` 在最新标准 `backend-only` 运行时上再次跑通 `提交 -> 拒绝 -> 重提 -> 通过`
  - 当前 verify 剩余缺口已从“真实链路未闭环”收口为“页面级证据仍待补齐”

### 2026-04-04

- 当前判定：`闭环完成`
- 备注：
  - 已新增并执行标准页面级证据脚本：
    - `execution/verify/run-verify-mini-program-page-evidence.py`
    - `execution/verify/run-verify-admin-page-evidence.py`
  - 最新小程序样本 `execution/verify/samples/20260404-021512-continue-verify-mini-page-evidence/summary.md` 已固定 `/pkg-card/verify/index` 的真实截图、路由和 `verify/status / level/info / user/me` 同包证据
  - 最新后台样本 `execution/verify/samples/20260404-021512-continue-verify-admin-page-evidence/summary.md` 已固定 `/verify/pending` 空队列截图、`/verify/history` 双记录列表、详情抽屉与真实接口回包
  - `validation-sample-ledger-template.md` 也已补齐页面证据段，因此 verify 当前阶段已不再停留在“缺页面级证据”的状态，可正式改判为闭环完成
