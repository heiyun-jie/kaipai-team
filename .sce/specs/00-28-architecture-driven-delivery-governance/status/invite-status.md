# 邀请裂变与邀请资格闭环状态回填

## 1. 归属切片

- `../slices/invite-referral-capability-slice.md`
- `../execution/invite/README.md`

## 2. 当前判定

- 回填日期：`2026-04-02`
- 当前判定：`局部完成`
- 一句话结论：小程序邀请页、登录页邀请码承接、演员端 `/invite/*` 查询接口，以及服务端注册写入 `invitedByUserId / referral_record` 的最小闭环已继续收口，`/level/info` 与登录态的有效邀请数也开始回到 `referral_record` 单一事实源；`kaipai-admin` 的记录页 / 风险页 / 规则页 / 资格页与菜单路由权限也已接上，邀请联调工具链也已能自动回填样本台账与验证报告，但真实环境联调、二维码真实生成和资格流转闭环仍未验证。

## 3. 当前已确认事实

### 3.1 前端 / 小程序

- `kaipai-frontend/src/api/invite.ts` 约定前端消费 `/api/invite/code`、`/api/invite/stats`、`/api/invite/records`、`/api/invite/qrcode`
- `kaipai-frontend/src/pages/login/index.vue` 已同时承接显式 `inviteCode` 与小程序码常见 `scene` 场景，避免真实二维码落地时丢邀请码
- `kaipai-frontend/src/pkg-card/invite/index.vue`、`src/pkg-card/membership/index.vue`、`src/stores/user.ts` 已消费邀请码、邀请统计与资格展示，并开始复用后端 `/level/info` 能力摘要而不是继续硬编码会员资格
- `kaipai-frontend/src/stores/user.ts` 已补上邀请链接本地 fallback、二维码接口兜底，以及注册 / 恢复会话后的邀请态 / 认证态 / 等级态同步
- `kaipai-frontend/src/utils/runtime.ts` 已放开 `invite / verify / level / card / ai / fortune / actor` 真接口能力，注册请求会附带 `deviceFingerprint`

### 3.2 后端 / 数据

- `kaipaile-server/src/main/java/com/kaipai/module/controller/referral/ReferralController.java` 已兼容 `/referral` 与 `/invite` 两套前缀，并补齐 `code / stats / records / qrcode` 最小演员端查询接口
- `kaipaile-server/src/main/java/com/kaipai/module/server/referral/service/InviteCodeService.java`、`InviteCodeServiceImpl.java` 已补齐邀请码生成 / 复用逻辑
- `kaipaile-server/src/main/java/com/kaipai/module/server/referral/service/ReferralRecordService.java`、`ReferralRecordServiceImpl.java` 已补齐邀请统计和邀请记录输出
- `kaipaile-server/src/main/java/com/kaipai/module/server/auth/service/impl/AuthServiceImpl.java` 已在注册事务内消费 `inviteCode`，并把注册前设置邀请关系、注册后落邀请记录拆成显式两步
- `kaipaile-server/src/main/java/com/kaipai/module/server/referral/service/ReferralRegistrationService.java`、`impl/ReferralRegistrationServiceImpl.java` 已补齐“邀请码解析 -> `user.invitedByUserId` -> `referral_record` 落库”的服务端最小闭环，并按启用中的邀请策略 / 默认阈值标记异常邀请
- `kaipaile-server/src/main/java/com/kaipai/module/server/membership/service/impl/MembershipAccountServiceImpl.java`、`src/main/java/com/kaipai/module/server/auth/service/impl/AuthServiceImpl.java` 已开始从 `referral_record` 读取有效邀请数，不再继续把 `user.validInviteCount` 作为唯一事实源
- `kaipaile-server/src/main/java/com/kaipai/module/server/referral/service/impl/ReferralRecordServiceImpl.java` 已在风控通过 / 作废 / 复核动作后回写 `user.validInviteCount`，避免登录态缓存和邀请记录长期分裂
- `kaipaile-server/src/main/java/com/kaipai/module/controller/admin/referral/AdminReferralController.java` 已具备记录、风险、策略、资格发放等后台治理接口
- `kaipaile-server/src/main/java/com/kaipai/module/server/referral/service/impl/UserEntitlementGrantServiceImpl.java` 已把 `grantCode` 唯一约束校验与数据库约束对齐，避免撤销后重复发同码时直接撞库
- 后台服务层已接入风控与资格相关操作日志，但未形成演员端统一消费契约
- `2026-04-02` 已在 `JDK 21` 环境下执行 `mvn -q -DskipTests compile` 通过

### 3.3 后台治理

- `kaipai-admin/src/views/referral/RecordsView.vue`、`RiskView.vue`、`PoliciesView.vue`、`EligibilityView.vue` 已接上记录、风控、规则、资格四个后台页面，并补齐对应菜单 / 路由 / API / 权限树注册
- 后台服务端接口已覆盖邀请记录、风险复核、策略配置、资格发放和日志回看能力
- `2026-04-02` 已在 `kaipai-admin` 执行 `npm run type-check` 通过，后台治理前端不再缺少邀请规则配置入口

### 3.4 联调现状

- 当前能确认“前台邀请展示能力”、“演员端查询接口”、“服务端注册绑定写库”以及“后台记录 / 风控 / 规则 / 资格入口”四段能力都已落位
- `2026-04-02` 已把 `run-invite-validation.ps1`、`collect-invite-evidence.ps1`、`new-invite-validation-sample.ps1` 修正为可直接执行，并让总控脚本自动解包 `actor / admin` 采证 JSON、预填 `sample-ledger.md`、生成带抽取事实和交叉校验的 `validation-report.md`
- 已使用本地 mock 样本验证工具链可落盘生成 `capture-results.json`、`sample-ledger.md`、`validation-report.md`，当前阻塞点已从“工具不可执行”收敛为“真实环境同一样本尚未跑通”
- 当前不能确认“邀请 -> 注册绑定 -> 记录生成 -> 风险复核 / 资格发放 -> 前台同步”的真实环境链路，也不能确认策略配置后的资格流转是否已形成完整运营闭环

## 4. 联调结论

- 当前是否具备三端联调条件：`已具备最小前置条件`
- 已确认走通的链路：登录页邀请码 / `scene` 承接、服务端注册消费邀请码并写入邀请关系、小程序邀请页展示、后台邀请记录 / 异常邀请 / 邀请规则 / 邀请资格入口、演员端 `/invite/*` 查询接口
- 当前不能宣告闭环的原因：真实环境下的注册绑定、记录生成、风险复核、资格发放与前台消费还没有完成联调验证，且策略配置后的资格流转效果仍未完成真实样本验证

## 5. 验收判断

| 闭环条件 | 状态 | 说明 |
|----------|------|------|
| 上位 Spec 已存在并对齐 | 已满足 | `00-28` 已为邀请裂变补齐切片和执行卡 |
| 数据模型、接口、状态流转清楚 | 部分满足 | 查询接口、注册绑定与邀请计数事实源已继续收口，但资格流转链路仍待真实联调确认 |
| 后台治理入口可操作 | 已满足 | 记录页 / 风控页 / 规则页 / 资格页已接入，后台治理前端的四类主入口已补齐 |
| 小程序或前台用户侧落点可验证 | 部分满足 | 邀请页、登录页、`scene` 承接、注册写库和演员端查询接口都已落地，但真实业务链路未闭环 |
| 关键日志、权限、限额或回滚约束已接入 | 部分满足 | 后台日志和治理动作已接入，但二维码仍为占位返回，资格发放与前台消费仍待联调 |
| 文档、映射表、验证记录已回填 | 已满足 | 当前已建立邀请切片状态回填文档，并补齐 invite 联调样本目录、SQL 模板、采证脚本与自动回填报告能力 |

## 6. 当前阻塞项

- 联调工具链虽已可执行并完成本地 mock 验证，但仍缺真实环境统一邀请码样本来验证风险命中与资格生效
- 小程序码当前仍是占位返回，未接真实二维码生成能力
- 邀请资格发放虽然后台能力已具备，但 `referral_record -> user_entitlement_grant -> 前台消费` 的同一事实链还没有收口验证

## 7. 下一轮最小动作

1. 跑通一次真实环境“邀请 -> 注册 -> 记录生成 -> 风险复核 / 资格发放 -> 前台更新”联调，并回填结论
2. 校验 `user.invitedByUserId`、`referral_record`、`user_entitlement_grant`、风险状态与前台邀请 / 等级状态是否按同一邀请码样本稳定变化
3. 验证后台策略页的启停、门槛与自动发放配置，是否会稳定反映到资格发放和前台状态
4. 视联调结果决定是否需要把占位二维码替换成真实生成链路

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
