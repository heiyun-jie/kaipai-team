# 邀请裂变与邀请资格闭环状态回填

## 1. 归属切片

- `../slices/invite-referral-capability-slice.md`
- `../execution/invite/README.md`

## 2. 当前判定

- 回填日期：`2026-04-03`
- 当前判定：`局部完成`
- 一句话结论：小程序邀请页、登录页邀请码承接、演员端 `/invite/*` 查询接口，以及服务端注册写入 `invitedByUserId / referral_record` 的最小闭环已继续收口；`2026-04-03 04:00` 的真实样本已跑通“邀请注册 -> 档案补齐 -> 实名提交 -> 后台审核 -> `referral_record` 生效 -> `user_entitlement_grant(sourceType=referral)` 生成 -> 前台 `/level/info` 回显”，且随后已用同一样本补齐 DB 回读。当前 invite 剩余缺口已收敛为微信官方小程序码能力，而不再是资格链 `500` 或 DB 证据缺失。

## 3. 当前已确认事实

### 3.1 前端 / 小程序

- `kaipai-frontend/src/api/invite.ts` 约定前端消费 `/api/invite/code`、`/api/invite/stats`、`/api/invite/records`、`/api/invite/qrcode`
- `kaipai-frontend/src/pages/login/index.vue` 已同时承接显式 `inviteCode` 与小程序码常见 `scene` 场景，避免真实二维码落地时丢邀请码
- `kaipai-frontend/src/pkg-card/invite/index.vue`、`src/pkg-card/membership/index.vue`、`src/stores/user.ts` 已消费邀请码、邀请统计与资格展示，并开始复用后端 `/level/info` 能力摘要而不是继续硬编码会员资格
- `kaipai-frontend/src/stores/user.ts` 已补上邀请链接本地 fallback、二维码接口兜底，以及注册 / 恢复会话后的邀请态 / 认证态 / 等级态同步
- `kaipai-frontend/src/pkg-card/invite/index.vue`、`src/utils/invite.ts` 已开始优先消费后端 `inviteLink`、`status`、`statusLabel`，不再只靠 `buildInvitePath`、`isValid / flagged` 在页面内推导分享 path 和邀请记录状态
- `kaipai-frontend/src/pkg-card/invite/index.vue` 已在海报生成时兼容后端返回的 base64/path 二维码源，不再强依赖本地静态占位图
- `kaipai-frontend/src/pkg-card/invite/index.vue` 已开始恢复 `scene / artifact / themeId / tone` query，并在邀请页内随邀请产物切换同步 share state，避免 actor-card 带入的邀请主题上下文在页面落地后丢失
- `kaipai-frontend/src/utils/runtime.ts` 已放开 `invite / verify / level / card / ai / fortune / actor` 真接口能力，注册请求会附带 `deviceFingerprint`

### 3.2 后端 / 数据

- `kaipaile-server/src/main/java/com/kaipai/module/controller/referral/ReferralController.java` 已兼容 `/referral` 与 `/invite` 两套前缀，并补齐 `code / stats / records / qrcode` 最小演员端查询接口
- `kaipaile-server/src/main/java/com/kaipai/module/controller/referral/ReferralController.java` 已把 `qrCodeUrl` 与 `/invite/qrcode` 从 `/static/logo.png` 占位返回收口为后端实时生成的邀请码链接二维码内容
- `kaipaile-server/src/main/java/com/kaipai/module/server/card/service/impl/ActorPersonalizationServiceImpl.java` 已把 `inviteCard` 产物 path 从裸邀请页路径收口为带主题 / 场景上下文的统一 path，供演员端邀请页恢复邀请主题
- `kaipaile-server/src/main/java/com/kaipai/module/server/referral/service/InviteCodeService.java`、`InviteCodeServiceImpl.java` 已补齐邀请码生成 / 复用逻辑
- `kaipaile-server/src/main/java/com/kaipai/module/server/referral/service/ReferralRecordService.java`、`ReferralRecordServiceImpl.java` 已补齐邀请统计和邀请记录输出，并开始对演员端直接下发 `status / statusLabel / riskReason`
- `kaipaile-server/src/main/java/com/kaipai/module/server/auth/service/impl/AuthServiceImpl.java` 已在注册事务内消费 `inviteCode`，并把注册前设置邀请关系、注册后落邀请记录拆成显式两步
- `kaipaile-server/src/main/java/com/kaipai/module/server/referral/service/ReferralRegistrationService.java`、`impl/ReferralRegistrationServiceImpl.java` 已补齐“邀请码解析 -> `user.invitedByUserId` -> `referral_record` 落库”的服务端最小闭环，并按启用中的邀请策略 / 默认阈值标记异常邀请
- `kaipaile-server/src/main/java/com/kaipai/module/server/membership/service/impl/MembershipAccountServiceImpl.java`、`src/main/java/com/kaipai/module/server/auth/service/impl/AuthServiceImpl.java` 已开始从 `referral_record` 读取有效邀请数，不再继续把 `user.validInviteCount` 作为唯一事实源
- `kaipaile-server/src/main/java/com/kaipai/module/server/referral/service/impl/ReferralRecordServiceImpl.java` 已在风控通过 / 作废 / 复核动作后回写 `user.validInviteCount`，避免登录态缓存和邀请记录长期分裂
- `kaipaile-server/src/main/java/com/kaipai/module/controller/admin/referral/AdminReferralController.java` 已具备记录、风险、策略、资格发放等后台治理接口
- `kaipaile-server/src/main/java/com/kaipai/module/server/referral/service/impl/UserEntitlementGrantServiceImpl.java` 已把 `grantCode` 唯一约束校验与数据库约束对齐，避免撤销后重复发同码时直接撞库
- `2026-04-03` 已继续为 invite 补齐微信官方小程序码代码主链：`WechatMiniProgramService` 已承接 `wechat.miniapp.app-id / app-secret / env-version` 与 access token 复用；`InviteQrCodeServiceImpl` 已让 `/api/invite/code`、`/api/invite/qrcode` 优先请求 `wxa/getwxacodeunlimit`，失败时显式降级到 `link-qrcode`
- 后台服务层已接入风控与资格相关操作日志，但未形成演员端统一消费契约
- `2026-04-02` 已在 `JDK 21` 环境下执行 `mvn -q -DskipTests compile` 通过

### 3.3 后台治理

- `kaipai-admin/src/views/referral/RecordsView.vue`、`RiskView.vue`、`PoliciesView.vue`、`EligibilityView.vue` 已接上记录、风控、规则、资格四个后台页面，并补齐对应菜单 / 路由 / API / 权限树注册
- 后台服务端接口已覆盖邀请记录、风险复核、策略配置、资格发放和日志回看能力
- `2026-04-02` 已在 `kaipai-admin` 执行 `npm run type-check` 通过，后台治理前端不再缺少邀请规则配置入口

### 3.4 联调现状

- 当前能确认“前台邀请展示能力”、“演员端查询接口”、“服务端注册绑定写库”以及“后台记录 / 风控 / 规则 / 资格入口”四段能力都已落位
- 当前能确认 invite 页分享态已开始优先消费后端 `inviteLink`，邀请记录状态也已从“前端推导”收口到“后端 DTO + 前端展示”
- `2026-04-02` 已把 `run-invite-validation.ps1`、`collect-invite-evidence.ps1`、`new-invite-validation-sample.ps1` 修正为可直接执行，并让总控脚本自动解包 `actor / admin` 采证 JSON、预填 `sample-ledger.md`、生成带抽取事实和交叉校验的 `validation-report.md`
- `2026-04-03 03:07` 已以真实公网自动样本 `execution/invite/captures/invite-20260403-030705-remote-invite-auto` 跑通标准验证脚本，`capture-results.json` 显示 14 个 endpoint 全部 `ok`，`/api/invite/code` 与 `/api/invite/qrcode` 的历史业务 `500` 已被收口为 `200`
- `2026-04-03 03:54` 已按 `00-29` 标准只读诊断入口 `read-backend-runtime-logs.py` 抓到真实环境 `verify/submit` 堆栈，明确根因为 `IdentityVerificationServiceImpl.submit(...)` 回写 `user.update_user_name=null`，不是 Nacos / DB / Redis 目标漂移
- `2026-04-03 03:59` 已按标准 `backend-only` 脚本重新发布后端修复，发布记录为 `.sce/runbooks/backend-admin-release/records/20260403-035854-backend-only-invite-verify-submit-fix-rerun.md`
- `2026-04-03 04:00` 已通过真实样本 `execution/invite/captures/invite-20260403-040007-remote-invite-e2e-closure-after-verify-fix` 跑通邀请闭环：同一样本 `inviteeUserId=10017 / referralId=11 / policyId=1 / grantId=2` 在 actor/admin 共 15 个 endpoint 上全部返回 `ok`；`validation-report.md` 已明确显示 `referral_record.status=1`、`grant.sourceType=referral`、`grant.sourceRefId=11`、`actor_level_info.isCertified=true`、`membershipTier=member`
- 当前真实样本已证明 invite 二维码接口、邀请统计、邀请记录、后台记录 / 风险 / 策略查询接口，以及“资格生效 -> 前台能力摘要回显”都能基于同一邀请码 / 同一推荐记录返回一致事实；invite 主阻塞已从“查询面不可用 / 资格链未闭环”迁移为“微信官方小程序码能力待补齐”
- `2026-04-03` 已继续补充 `run-authenticated-invite-sample.py` 作为标准入口，后续 invite 联调不再要求先手工准备 `actor / admin token` 与样本主键
- 当前 API 与 DB 两侧已经共同确认“邀请 -> 注册绑定 -> 记录生成 -> 实名审核 -> 资格发放 -> 前台同步”的真实环境链路；当前仍未补齐的是微信官方扫码落地能力
- 当前仓内代码已不再停留在“没有 `wxacode` 实现”的阶段，而是进入“代码已接通、真实环境配置与扫码证据待补”的阶段

## 4. 联调结论

- 当前是否具备三端联调条件：`已具备最小前置条件`
- 已确认走通的链路：登录页邀请码 / `scene` 承接、服务端注册消费邀请码并写入邀请关系、小程序邀请页展示、后台邀请记录 / 异常邀请 / 邀请规则 / 邀请资格入口、演员端 `/invite/*` 查询接口、真实环境 `invite` 二维码生成、后台记录/风控/策略联查，以及同一样本下的 `实名审核 -> referral_record 生效 -> user_entitlement_grant(sourceType=referral) -> /level/info 回显`
- 当前不能宣告全量闭环的原因：当前二维码仍是“邀请码链接二维码”而不是微信官方 `wxacode`；虽然同一样本 `inviteCode=SMK100 -> inviteeUserId=10017 -> referralId=11 -> grantId=2` 的 API 与 DB 证据都已补齐，但微信官方扫码打开链路仍未验证

## 5. 验收判断

| 闭环条件 | 状态 | 说明 |
|----------|------|------|
| 上位 Spec 已存在并对齐 | 已满足 | `00-28` 已为邀请裂变补齐切片和执行卡 |
| 数据模型、接口、状态流转清楚 | 部分满足 | 查询接口、注册绑定、资格流转与前台能力摘要已通过同一样本 API + DB 双侧证据继续收口，但微信官方小程序码能力仍未补齐 |
| 后台治理入口可操作 | 已满足 | 记录页 / 风控页 / 规则页 / 资格页已接入，后台治理前端的四类主入口已补齐 |
| 小程序或前台用户侧落点可验证 | 部分满足 | 邀请页、登录页、`scene` 承接、注册写库和演员端查询接口都已落地，且真实样本已证明资格发放后的前台能力摘要回显；当前剩余缺口是微信官方扫码落地证据 |
| 关键日志、权限、限额或回滚约束已接入 | 部分满足 | 后台日志、风险/资格治理与标准化运行时诊断已接入，二维码也已脱离占位图；当前剩余缺口是微信官方小程序码能力 |
| 文档、映射表、验证记录已回填 | 已满足 | 当前已建立邀请切片状态回填文档，并补齐 invite 联调样本目录、SQL 模板、采证脚本与自动回填报告能力 |

## 6. 当前阻塞项

- 联调工具链已具备真实环境样本能力，且 `2026-04-03 04:00` 已跑通“注册发起、资格生效与前台消费”同一样本闭环，并已通过 `validation-result.txt` 补齐同一样本 DB 回读；当前缺口不再是资格链 `500`、脚本不可执行或 DB 证据缺失
- 当前二维码虽已不再返回占位图，但仍只是“邀请码链接二维码”，不是微信官方小程序码；仓内代码主链虽已接入 `wxacode.getUnlimited`，但仓内仍未发现可直接用于真实环境的微信 `appSecret` 来源，因此真实扫码打开路径和微信侧能力仍属外部依赖阻塞
- `wxacode` 当前已拆到独立执行入口：`../execution/invite/wxacode-execution-card.md`；后续不得再把它和 invite 资格闭环是否完成混写
- 当前 invite 页虽已开始优先命中后端 `inviteLink / status / statusLabel / qrCodeUrl`，但仍保留本地 fallback，需继续确认真实环境是否完全命中后端字段
- `2026-04-03 04:34` 的真实样本 `execution/invite/captures/invite-20260403-043423-remote-invite-wxacode-fallback-post-release/actor_invite_code.json` 已明确回出 `qrCodeType=link-qrcode`、`qrCodeFallbackReason=微信小程序 appId/appSecret 未配置`；当前线上已从“静默普通二维码”升级为“官方码主链 + 显式降级原因”
- `2026-04-03 04:41` 的 `00-29` 标准诊断样本 `.sce/runbooks/backend-admin-release/records/diagnostics/20260403-044108-invite-wxacode-compose-source-precheck/` 又进一步证明：远端 `/opt/kaipai/docker-compose.yml` 与 `docker compose config` 渲染结果都只包含 `NACOS_ENABLED / SPRING_PROFILES_ACTIVE / SERVER_PORT`，没有 `WECHAT_MINIAPP_APP_ID / WECHAT_MINIAPP_APP_SECRET`；当前 blocker 已从“容器内看不到变量”收束为“compose / env source 本身未配置”
- `2026-04-03` 已补齐 `00-29` 标准 compose 来源同步入口 `run-backend-compose-env-sync.py`；后续微信配置补齐必须先走该脚本留档，再走正式 `backend-only` 发布 / 重建

## 7. 下一轮最小动作

1. 按 `../execution/invite/wxacode-execution-card.md` 收口微信官方 `wxacode`，不再把它和当前已跑通的 invite 资格闭环混在一起
2. 评估 invite 页当前 fallback 是否仍有真实环境命中，如果已不再需要，继续按 spec 收口 `inviteLink / status / statusLabel / qrCodeUrl` 的本地兜底
3. 先按 `00-29` 把后端 compose / env source 的微信配置来源补齐，再补微信小程序 `appid / secret / getUnlimited` 与真实扫码落地证据，避免继续把“链接二维码可用”误判成“小程序码闭环完成”
4. 后续 invite 真实环境联调继续统一走 `run-authenticated-invite-sample.py` 或 `run-end-to-end-invite-closure.py`，DB 校验统一走 `run-remote-validation-sql.py`，不再回退到手工 token / 主键拼接

## 8. 回填记录

### 2026-04-01

- 当前判定：`局部完成`
- 备注：先把“前台邀请页存在”和“后台治理存在”拆开记录，避免把两端各自完成误判成邀请闭环完成

### 2026-04-01（二次回填）

- 当前判定：`局部完成`
- 备注：`kaipaile-server` 已补齐演员端 `/invite/*` 兼容查询接口，并在 `JDK 21` 环境下执行 `mvn -q -DskipTests compile` 通过；当前仍缺真实闭环联调

### 2026-04-02

- 当前判定：`局部完成`
- 备注：`kaipaile-server` 已在 `/auth/register` 内消费 `inviteCode`，并通过 `ReferralRegistrationService` 写入 `user.invitedByUserId` 与 `referral_record`；`kaipai-frontend` 运行时也已放开 `invite / verify / level / card` 真接口分支；已在 `JDK 21` 环境下再次执行 `mvn -q -DskipTests compile` 通过，当前仍缺真实环境联调与资格发放后的前台同步验证

### 2026-04-02（二次回填）

- 当前判定：`局部完成`
- 备注：`kaipai-frontend` 邀请页已开始消费 `/level/info` 的等级 / 会员能力摘要，不再继续在页面内硬编码邀请卡片资格；`kaipaile-server` 与 `kaipai-frontend` 已再次通过 `mvn -q -DskipTests compile` / `npm run type-check`，当前仍缺真实环境“邀请 -> 注册 -> 风控 / 资格 -> 前台同步”联调验证

### 2026-04-02（三次回填）

- 当前判定：`局部完成`
- 备注：`kaipaile-server` 已把注册邀请绑定拆成“注册前设置邀请关系 / 注册后落邀请记录”两步，并让 `/level/info` 与登录态里的有效邀请数开始回到 `referral_record` 单一事实源；`ReferralRecordServiceImpl` 也已在风险处理后同步 `user.validInviteCount`，`UserEntitlementGrantServiceImpl` 还补齐了 `grantCode` 唯一约束校验；`kaipai-frontend` 已补上登录页 `scene` 承接、邀请链接 / 二维码 fallback、注册后的邀请态同步，并移除 invite 页与海报里硬编码的“50%”阈值文案；本轮再次通过 `mvn -q -DskipTests compile` / `npm run type-check`，当前剩余高优先级缺口是 `kaipai-admin` 记录页 / 资格页未接，以及真实环境资格流转链未联调

### 2026-04-02（四次回填）

- 当前判定：`局部完成`
- 备注：`kaipai-admin` 已新增 `RecordsView` / `EligibilityView`，并补齐邀请模块的菜单、路由、API、状态映射与权限树登记；`kaipai-admin` 已通过 `npm run type-check`，后台不再只有风险页可用；当前剩余高优先级缺口收敛为“邀请规则页仍未接到管理前端”、“二维码仍是占位返回”以及“真实环境下 `referral_record -> user_entitlement_grant -> 前台状态` 的联调尚未验证”

### 2026-04-02（五次回填）

- 当前判定：`局部完成`
- 备注：`kaipai-admin` 已新增 `PoliciesView`，并补齐邀请规则的菜单、路由、API 与页面治理入口；本轮再次通过 `npm run type-check`，后台治理前端已补齐记录 / 风控 / 规则 / 资格四类入口；当前剩余高优先级缺口收敛为“真实环境邀请链路联调仍未完成”、“二维码仍是占位返回”以及“`referral_record -> user_entitlement_grant -> 前台状态` 的资格流转尚未验证”

### 2026-04-02（六次回填）

- 当前判定：`局部完成`
- 备注：invite 联调工具链已从“文档模板”推进到“可执行工具”。`run-invite-validation.ps1` 现在会自动解包 `actor / admin` 采证 JSON，并预填 `sample-ledger.md`、生成包含抽取事实和 API 交叉校验的 `validation-report.md`；`collect-invite-evidence.ps1` 与 `new-invite-validation-sample.ps1` 也已修正为可直接执行，并兼容当前 Windows PowerShell 运行环境。本轮已用本地 mock 样本验证工具链可落盘生成完整产物，但仍未拿真实环境同一样本完成“邀请 -> 注册 -> 风控 / 资格 -> 前台同步”闭环验证，因此状态继续保持 `局部完成`

### 2026-04-02（七次回填）

- 当前判定：`局部完成`
- 备注：`kaipaile-server` 的 `ActorReferralRecordRespDTO` 与 `ReferralRecordServiceImpl` 已开始对演员端直接输出 `status / statusLabel / riskReason`，`kaipai-frontend` 的 `src/pkg-card/invite/index.vue` 与 `src/utils/invite.ts` 也已改成优先消费后端 `inviteLink` 和邀请状态字段，不再只靠 `buildInvitePath`、`isValid / flagged` 在页面内推导。当前仍需继续用真实环境样本确认“邀请记录状态、资格流转与前台展示”是否完全按同一事实链变化。

### 2026-04-02（八次回填）

- 当前判定：`局部完成`
- 备注：`ReferralController` 已改成直接生成邀请码链接二维码内容，`/api/invite/code.qrCodeUrl` 与 `/api/invite/qrcode` 不再返回 `/static/logo.png`；`kaipai-frontend` 的 `src/pkg-card/invite/index.vue` 已在海报绘制前兼容解析 base64/path 二维码源。本轮再次通过 `kaipaile-server mvn -q -DskipTests compile` 与 `kaipai-frontend npm run type-check`。当前剩余高优先级缺口收敛为“二维码仍不是微信官方小程序码”和“真实环境邀请码样本的资格流转闭环尚未联调”。

### 2026-04-02（九次回填）

- 当前判定：`局部完成`
- 备注：`ActorPersonalizationServiceImpl` 已把 `inviteCard` 产物 path 收口为带 `actorId / scene / artifact / themeId / tone / shared` 的统一上下文路径；`kaipai-frontend` 的 `src/pkg-card/invite/index.vue` 也已开始恢复这些 query，并在邀请页内随产物切换同步 share state。与此同时，`src/pkg-card/actor-card/index.vue` 在选中 `inviteCard` 时已把真正分享落点优先切到带 `inviteCode` 的登录链路，而不是继续先落到内部邀请页。本轮再次通过 `kaipai-frontend npm run type-check` 与 `kaipaile-server mvn -q -DskipTests compile`，当前剩余高优先级缺口继续收敛为“二维码仍不是微信官方小程序码”和“真实环境邀请码样本的资格流转闭环尚未联调”。

### 2026-04-03

- 当前判定：`局部完成`
- 备注：已按标准发布脚本完成后端修复发布，发布记录为 `.sce/runbooks/backend-admin-release/records/20260403-025900-backend-only-invite-qrcode-fix.md`；随后使用自动入口 `execution/invite/run-authenticated-invite-sample.py` 跑通真实公网样本 `invite-20260403-030705-remote-invite-auto`，并由其调用 `run-invite-validation.ps1` 生成正式证据目录。`capture-results.json` 显示 actor/admin 共 14 个 endpoint 全部返回 `ok`，`/api/invite/code` 与 `/api/invite/qrcode` 已从业务 `500` 收口为 `200`。当前新的主阻塞不再是 invite 查询接口不可用，而是同一样本 `inviteCode=SMK100 -> referralId=8 -> inviteeUserId=10014` 在后台 `eligibility` 列表中仍无同源 `grant`，因此 `referral_record -> user_entitlement_grant -> 前台消费` 事实链仍待继续收口。

### 2026-04-03（二次回填）

- 当前判定：`局部完成`
- 备注：为避免 invite 联调继续停留在“先人工拿 token、再手工拼样本主键”的不稳定模式，已新增 `execution/invite/run-authenticated-invite-sample.py` 作为标准入口。该脚本会自动完成 `admin/admin123` 与 `13800138000` 登录、发现当前 `inviteCode / referralId / inviteeUserId / grantId / policyId`，再调用 `run-invite-validation.ps1` 生成正式证据目录。当前 invite 切片的下一步，应围绕这套标准入口补齐“注册刚发生样本”和“资格生效样本”，而不是继续人工散点采证。

### 2026-04-03（三次回填）

- 当前判定：`局部完成`
- 备注：`2026-04-03 03:54` 已按 `00-29` 标准只读诊断入口 `read-backend-runtime-logs.py` 固化真实环境 `verify/submit` 堆栈，定位根因为 `IdentityVerificationServiceImpl.submit(...)` 回写 `user.update_user_name=null`；随后已按标准 `backend-only` 脚本完成修复发布，记录为 `.sce/runbooks/backend-admin-release/records/20260403-035854-backend-only-invite-verify-submit-fix-rerun.md`。`2026-04-03 04:00` 又通过真实样本 `invite-20260403-040007-remote-invite-e2e-closure-after-verify-fix` 跑通 `inviteCode=SMK100 -> inviteeUserId=10017 -> referralId=11 -> grantId=2 -> /level/info.membershipTier=member`，`validation-report.md` 已显示 actor/admin 共 15 个 endpoint 全部 `ok`。当前 invite 剩余高优先级缺口已收敛为“微信官方小程序码”和“同一样本 DB 回读证据”，不再是资格链 `500`。

### 2026-04-03（四次回填）

- 当前判定：`局部完成`
- 备注：已继续按标准远端脚本 `execution/invite/run-remote-validation-sql.py` 对同一样本 `invite-20260403-040007-remote-invite-e2e-closure-after-verify-fix` 执行 `validation.sql`，并将结果落盘到 `validation-result.txt`。当前已能以同一样本同时证明 `invite_code_id=1 / invitee_user_id=10017 / referral_id=11 / grant_id=2 / policy_id=1 / grant.source_type=referral / grant.source_ref_id=11`，因此 invite 主线的剩余高优先级缺口已进一步收敛为“微信官方小程序码能力”，不再包含 DB 手工回读。

### 2026-04-03（五次回填）

- 当前判定：`局部完成`
- 备注：已按 `00-29` 标准 `backend-only` 脚本完成后端发布，记录为 `.sce/runbooks/backend-admin-release/records/20260403-043255-backend-only-invite-wxacode-fallback-mainline.md`；随后又按 `00-28` 标准入口 `execution/invite/run-authenticated-invite-sample.py --label remote-invite-wxacode-fallback-post-release` 补做真实样本 smoke。当前 `actor_invite_code.json` 已明确返回 `qrCodeType=link-qrcode` 与 `qrCodeFallbackReason=微信小程序 appId/appSecret 未配置`，说明 invite 的微信官方码代码主链已经上线，但目标环境配置仍未补齐，所以线上当前表现是“显式降级”而不是“官方码已打通”。
