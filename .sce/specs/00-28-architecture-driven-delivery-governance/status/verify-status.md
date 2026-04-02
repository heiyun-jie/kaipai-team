# 实名认证闭环状态回填

## 1. 归属切片

- `../slices/verify-capability-slice.md`
- `../execution/verify/README.md`

## 2. 当前判定

- 回填日期：`2026-04-03`
- 当前判定：`局部完成`
- 一句话结论：小程序认证页、后台审核页和演员端公开接口都已具备，认证页的档案完成度判断也已切到后端权威口径，拒绝后重提会保留历史审核记录；`2026-04-03 04:00` 又已借同一份 invite 真实样本跑通“实名提交 -> 后台审核 -> `level/info.isCertified=true` -> 邀请资格放行”的 happy path，因此实名认证已不再停留在“没有真实联调”的阶段，但拒绝 / 重提专项样本仍未补齐，所以仍不能宣告闭环完成。

## 3. 当前已确认事实

### 3.1 前端 / 小程序

- `kaipai-frontend/src/pkg-card/verify/index.vue` 已提供认证资料填写、档案完成度校验和提交入口，且提交前置判断已改为复用 `/level/info` 返回的后端 `profileCompletion`
- `kaipai-frontend/src/api/verify.ts` 约定前端消费 `/api/verify/status`、`/api/verify/submit`
- `kaipai-frontend/src/api/actor.ts`、`src/utils/runtime.ts` 已支持 `actor` 真接口分支，认证页计算档案完成度时不再只能依赖 mock actor 档案
- `kaipai-frontend/src/stores/user.ts`、`src/pkg-card/membership/index.vue`、`src/pkg-card/actor-card/index.vue` 已统一消费 `realAuthStatus` / `isCertified`

### 3.2 后端 / 数据

- `kaipaile-server/src/main/java/com/kaipai/module/controller/verify/VerifyController.java` 已暴露 `/verify/status`、`/verify/submit` 两个演员端公开接口
- `kaipaile-server/src/main/java/com/kaipai/module/server/verify/service/IdentityVerificationService.java`、`impl/IdentityVerificationServiceImpl.java` 已补齐演员端实名状态查询、提交、重复提交拦截、档案完成度校验和后台审核回写复用逻辑
- `IdentityVerificationServiceImpl.submit(...)` 现已在“拒绝后重提”场景下新建申请单，而不是覆盖旧记录，保留后台历史审核轨迹
- `kaipaile-server/src/main/java/com/kaipai/module/controller/actor/ActorProfileController.java`、`ActorController.java` 已补齐认证页所需的 `/actor/profile/mine`、`/actor/profile/{userId}`、`/actor/{userId}` 最小 actor 输出
- `kaipaile-server/src/main/java/com/kaipai/module/controller/admin/verify/AdminVerifyController.java` 已具备列表、详情、通过、拒绝等后台接口
- `kaipaile-server/src/main/java/com/kaipai/module/server/verify/service/impl/IdentityVerificationServiceImpl.java` 已接入后台操作日志

### 3.3 后台治理

- `kaipai-admin/src/views/verify/VerificationBoard.vue` 已具备待审核 / 历史记录、详情抽屉、通过 / 拒绝动作
- 后台侧已覆盖权限码与审核操作按钮，具备治理入口基础

### 3.4 联调现状

- 当前能确认“前端提交接口 -> actorside verify service -> 后台审核 service”的源码链路已打通
- 当前能确认认证页前置完成度判断与服务端提交校验已改成同一份后端事实口径，不再依赖前端独立算法
- `2026-04-03 03:54` 已按 `00-29` 标准只读诊断入口抓到真实环境 `verify/submit` 失败堆栈，明确根因为 `IdentityVerificationServiceImpl.submit(...)` 回写 `user.update_user_name=null`，不是配置漂移或目标库错误
- `2026-04-03 03:59` 已按标准 `backend-only` 脚本完成后端修复发布，记录为 `.sce/runbooks/backend-admin-release/records/20260403-035854-backend-only-invite-verify-submit-fix-rerun.md`
- `2026-04-03 04:00` 已通过真实样本 `execution/invite/captures/invite-20260403-040007-remote-invite-e2e-closure-after-verify-fix/validation-report.md` 跑通同一样本链路：`inviteeUserId=10017` 在 actor/admin 共 15 个 endpoint 上全部 `ok`，且 `actor_level_info.isCertified=true`、`membershipTier=member`
- 同一样本 DB 回读 `validation-result.txt` 已继续确认：`user_id=10017.real_auth_status=2`、`referral_record.referral_id=11.status=1`、`user_entitlement_grant.grant_id=2.source_ref_id=11`
- 因此当前已能证明“实名提交 -> 后台审核 -> 实名状态回写 -> 邀请资格发放 -> 前台能力摘要同步”至少一条 happy path 在真实环境可用；当前尚未补的是“拒绝 -> 重提 -> 再审核”专项样本

## 4. 联调结论

- 当前是否具备三端联调条件：`已具备，并已跑通一条真实 happy path`
- 已确认走通的链路：前台契约、演员端公开接口、后台审核治理侧能力都已落位，且真实环境已跑通“提交 -> 审核通过 -> 实名状态回写 -> 前台能力放行”
- 当前不能宣告闭环的原因：仍缺“拒绝 -> 重提 -> 再审核”专项样本与页面级证据，不能只凭一条通过样本就认定实名认证所有状态分支都已闭环

## 5. 验收判断

| 闭环条件 | 状态 | 说明 |
|----------|------|------|
| 上位 Spec 已存在并对齐 | 已满足 | `00-28` 切片卡、执行卡已齐备 |
| 数据模型、接口、状态流转清楚 | 部分满足 | 演员端接口已补齐，完成度口径和重提历史已收口，且真实 happy path 已跑通；但拒绝 / 重提分支仍缺专项样本 |
| 后台治理入口可操作 | 已满足 | 后台列表、详情、通过 / 拒绝已存在 |
| 小程序或前台用户侧落点可验证 | 部分满足 | 页面、状态消费和演员端接口均已落地，且真实 happy path 已采证；但页面级截图和拒绝 / 重提回归仍未补齐 |
| 关键日志、权限、限额或回滚约束已接入 | 部分满足 | 后台权限与操作日志已接入，真实环境也已通过日志诊断定位并修复 `verify/submit` 失败根因；但拒绝 / 重提专项回归仍未完成 |
| 文档、映射表、验证记录已回填 | 已满足 | `00-28` 已补齐切片、执行卡和当前状态基线 |

## 6. 当前阻塞项

- 当前真实 happy path 已补齐，不再是“完全缺真实联调”
- 仍缺一组 verify 自身的标准样本去验证“提交 / 拒绝 / 重提 / 通过”完整回归，当前只能借 invite 闭环侧证实名通过分支
- 仍缺认证页 / 后台审核页页面级证据，当前主要是接口、日志和 DB 证据

## 7. 下一轮最小动作

1. 按 `execution/verify` 单独补一组真实样本，跑通“提交 -> 后台拒绝 -> 前台刷新 -> 重提 -> 后台通过”
2. 校验 `档案完成度 >= 70%`、重复提交拦截、拒绝后重提历史保留和审核回写口径，不再只借 invite 主线侧证
3. 补认证页 / 后台审核页页面级证据，再决定是否把 verify 从“局部完成”进一步提升

## 8. 回填记录

### 2026-04-01

- 当前判定：`局部完成`
- 备注：先建立状态基线，结论以当前仓内代码现实为准，不把后台自证完成误判为实名认证闭环完成

### 2026-04-01（二次回填）

- 当前判定：`局部完成`
- 备注：`kaipaile-server` 已补齐演员端实名接口，并在 `JDK 21` 环境下执行 `mvn -q -DskipTests compile` 通过；当前仍未完成真实联调

### 2026-04-02

- 当前判定：`局部完成`
- 备注：`kaipaile-server` 已补齐认证页所需的 `actor/profile` 最小输出，`kaipai-frontend` 运行时也已放开 `actor` 真接口分支；`mvn -q -DskipTests compile` 与 `npm run type-check` 均通过，当前仍缺真实环境下“提交 -> 审核 -> 回写 -> 前台放行”的联调验证

### 2026-04-02（二次回填）

- 当前判定：`局部完成`
- 备注：认证页的档案完成度前置判断已切到 `/level/info` 返回的后端 `profileCompletion`，不再继续使用前端本地算法；`kaipaile-server` 也已把“拒绝后重提”改成新建申请单以保留历史审核记录，`mvn -q -DskipTests compile` 与 `npm run type-check` 均通过，当前仍缺真实环境联调

### 2026-04-03

- 当前判定：`局部完成`
- 备注：
  - 已按 `00-29` 标准只读诊断入口抓到真实环境 `verify/submit` 堆栈，明确根因为 `IdentityVerificationServiceImpl.submit(...)` 回写 `user.update_user_name=null`
  - 已按标准 `backend-only` 脚本完成修复发布，记录为 `.sce/runbooks/backend-admin-release/records/20260403-035854-backend-only-invite-verify-submit-fix-rerun.md`
  - 随后已通过真实样本 `execution/invite/captures/invite-20260403-040007-remote-invite-e2e-closure-after-verify-fix/validation-report.md` 跑通“实名提交 -> 后台审核 -> `level/info.isCertified=true` -> 邀请资格发放”的同一样本 happy path
  - `validation-result.txt` 已继续确认 `user_id=10017.real_auth_status=2`、`referral_id=11.status=1`、`grant_id=2.source_ref_id=11`
  - 因此 verify 当前真实阻塞已从“完全缺真实联调”收口为“拒绝 / 重提专项样本和页面级证据仍未补齐”
