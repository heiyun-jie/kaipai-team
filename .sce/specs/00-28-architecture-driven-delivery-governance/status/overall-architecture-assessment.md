# 00-28 整体架构与实现评估

## 1. 评估归属

- 上位治理：`../design.md`
- 评估输入：`verify-status.md`、`invite-status.md`、`membership-status.md`、`login-auth-status.md`、`ai-resume-status.md`、`crew-company-project-status.md`、`recruit-role-apply-status.md`
- 评估日期：`2026-04-03`

## 2. 总体判定

- 当前判定：`局部完成`
- 一句话结论：`00-28` 已经把前端、小程序后端和后台推进方式从“按页面修补”推进到“按能力切片收口”，verify / 邀请 / 会员 / 登录 / 剧组招募 / AI 简历几条主线都已形成最小真实契约、状态卡和标准发布链；`2026-04-03` 又继续把 verify 的 reject/retry/approve 真实样本、invite / recruit 的线上记录，以及 AI 简历的 actor/admin 真实样本和角色矩阵收口到同一套 spec/runbook 流程，recruit 也已把页面样本继续收口到“7/7 automator 真截图”，membership 则已把 preview overlay 的白名单边界固化成可复跑静态审计样本，并进一步用 no-fortune rollback 哈希样本把 `actor-card / detail / invite` 三页模板回滚可见性全部闭环；当前主风险已切回“membership 预览态仍不是后端事实源、AI / recruit 等切片仍存在兼容层与长期治理边界缺口，以及 verify 页面级证据尚未收齐”，微信登录与官方 `wxacode` 已降级为后续能力批次，不再构成当前阶段主阻塞，因此当前仍不能判定为整体架构闭环完成。

## 3. 已收口的架构事实

### 3.1 治理模型已从口头约束变成执行入口

- `00-28` 已补齐能力切片、执行卡、状态卡，当前推进不再只围绕页面，而是围绕“数据 / 后端 / 后台 / 小程序 / 联调”同轮收口
- `verify-status.md`、`invite-status.md`、`membership-status.md`、`login-auth-status.md`、`crew-company-project-status.md` 已能分别记录“代码已落位”和“为什么还不能宣告闭环”

### 3.2 前端主线已开始以后端摘要为事实源

- `/api/card/personalization` 已成为模板、能力 gating、主题 token、分享产物的聚合输出，前端开始从页面本地拼装回收到后端汇总口径
- 会话主链已收口为“先 `bootstrapSession`，再同步 `verify / invite / level`”，不再继续把受保护状态请求放在会话建立之前
- invite 分享恢复、artifact path patch、share preference 保存已经开始围绕单一 helper 和单一后端 DTO 收口

### 3.3 后端与后台已具备最小治理骨架

- 后端已具备会员、模板、邀请、登录、演员个性化、剧组项目 / 角色的最小真实接口
- 后台已具备会员、模板、邀请、招募角色与投递等治理入口，且多条主线已接入最小日志 / 状态治理动作
- 已有编译 / 构建验证基础：`kaipai-frontend npm run type-check`、`kaipai-admin npm run build`、`kaipaile-server mvn -q -DskipTests compile`

### 3.4 剩余 mock 风险已可按三层口径拆分

| 能力域 | 运行时是否可能退回 mock | 真实契约是否已接通 | 当前主要缺口 |
|--------|--------------------------|--------------------|--------------|
| login / invite wx 链路 | 不再因缺 `VITE_API_BASE_URL` 自动退回 mock；当前若缺配置会显式阻塞真实请求，且 `VITE_ENABLE_WECHAT_AUTH=false` | 代码主链已存在，但当前阶段不作为主验收面 | 已降级为后续能力批次，不再作为当前版本 blocker |
| invite 主线 | 仍保留显式 mock 演示总闸，但当前 `.env` 已明确 `VITE_USE_MOCK=false`，缺 base 也不会静默退 mock | 已接通，且 actor/admin/API/DB 同一样本已闭环 | 当前阶段以注册链接/普通二维码与资格链闭环验收；官方 `wxacode` 延后 |
| verify 主线 | 同上，仍保留显式 mock 演示总闸，但当前标准真实样本已采证 | 已接通，且 `提交 -> 拒绝 -> 重提 -> 通过` 已跑通 | 仅剩页面级证据与少量模板文档回填 |
| membership 主线 | 同上，仍保留显式 mock 演示总闸 | 已接通，且后台动作 / API / DB / 小程序截图证据已较完整，preview overlay 也已有静态审计样本 | preview overlay 已收口为当前设备 session 预览态，但仍不是后端事实源，且当前真实样本固定在 `dev + Nacos` |
| recruit 主线 | 小程序和后台本地开发都可能误读为“只是本地代理”，但线上接口已发布 | 已接通，且后台治理、登录态样本、小程序页面样本与后台页面样本已跑通 | `project` 仍在兼容层，新增角色治理与二期产品边界仍待继续收口 |
| AI 简历 | 受全局 mock 总闸影响，且当前仍保留本地 mock adapter | 已接通，且 actor/admin/rollback/审计、角色矩阵、前后台页面样本、最小责任协同样本、目标环境业务回归样本都已跑通，仓内与目标环境后台静态入口的 fallback 代码也已退场 | 缺通知回执 / 自动催办 / 更细 SLA 等更完整治理协同与真实 LLM 接入 |

## 4. 主要结构性风险

### 4.1 运行时已停止“缺 base 自动回退 mock”，但显式 mock 演示分支仍在

- `kaipai-frontend/src/utils/runtime.ts` 现已只在 `VITE_USE_MOCK === 'true'` 时进入 mock；若缺少 `VITE_API_BASE_URL`，`App` 启动会直接提示阻塞，请求层也会拒绝真实请求，不再静默落回 mock
- 当前大量 API 模块仍保留 `useApiMock(...) ? mock : real` 双轨调用，因此“仓内仍有 mock 适配器”这个事实没有消失；只是运行时缺配置时不再把它误当成真实联通兜底
- 这不是局部实现细节，而是整体架构判断风险；如果不先补环境证据，仍可能把“显式 mock 演示态”误当成“真实链路已打通”
- `2026-04-03` 已继续把该风险从“提示阻塞”推进到“请求级硬阻塞”：前端在缺少 `VITE_API_BASE_URL` 时不再自动发相对路径或回退 mock，而是直接抛出运行时配置错误

### 4.2 会员分享编辑态仍不是后端事实

- `kaipai-frontend/src/utils/personalization.ts` 已把 preview overlay 明确成统一 helper，并进一步收口成“当前设备 session 主恢复”；未保存 preview 已不再继续写回分享 path，overlay query key 和 query 兼容读取也都已退场
- `execution/membership/run-preview-overlay-static-audit.py` 已把 overlay query key、session key 与 helper 触点固化为可复跑静态审计；随着 `patchPathWithPersonalizationPreviewOverlay` 与页面 query 兼容读取退场，审计白名单已进一步收口为纯 session 读取/写入与 overlay 应用 helper
- 这比散落在页面里或继续靠 query patch 传递更好，但它仍是前端显式预览态，而不是后端临时摘要或更强事实源
- 当前 membership 状态卡已经明确把这点列为未闭环主因之一，且 `00-49 membership-preview-overlay-fact-source-boundary` 已把它提升为独立治理入口；因此它是收敛后的剩余主风险，不应再被视作普通 UI 细节

### 4.3 登录链路当前以手机号闭环为主，微信能力后置

- 手机号验证码登录、注册、`/user/me` 与登录后摘要同步已经跑通，当前登录切片的当前阶段主验收面不再包含微信登录
- 微信登录接口与 `00-29` 微信配置门禁继续保留，但只在未来明确推进微信能力批次时启用
- `AuthServiceImpl.sendCode(...)` 当前仍直接返回验证码，只能证明接口接通，不能视作正式短信能力闭环
- 登录切片当前仍未达成正式短信能力闭环，但其主阻塞已不再是微信配置门禁

### 4.4 真实环境主阻塞已从“旧 jar / 大面积 500”转向“页面证据与兼容层治理”

- invite 链已收口到邀请码、`referral_record`、后台规则 / 风控 / 资格发放与前台展示；`2026-04-03 03:07` 的真实自动样本已证明 `/api/invite/code`、`/api/invite/qrcode`、`/api/invite/stats`、`/api/invite/records` 与后台记录 / 风控 / 策略查询均返回 `200`，`2026-04-03 04:00` 的闭环样本又进一步证明了 `实名审核 -> referral_record.status=1 -> user_entitlement_grant(sourceType=referral) -> /level/info.membershipTier=member` 可在同一样本上打通，随后同一样本 DB 回读也已补齐，因此 invite 当前阶段主阻塞已不再是资格链；官方 `wxacode` 进入后续能力批次
- verify 链也已不再停留在“缺真实联调”：`2026-04-03 05:34` 已通过只读日志诊断确认 reject/retry 新实现上线后首次失败的真实根因为“目标库未执行新 migration”；随后 `05:42` 已通过标准 schema 发布脚本执行 `V20260403_001__identity_verification_resubmit_history.sql`，`05:47` 已通过带 schema 门禁的新 `backend-only` 再次发布，`05:49` 又已在最新运行时跑通 `提交 -> 拒绝 -> 重提 -> 通过` 标准样本，并由 `validation-result.txt` 固定 `schema_release_history / identity_verification_owner / 两条申请单 / 两条审核日志` 四类证据
- membership 链已具备后台模板 / 会员治理和前台 personalization 摘要，但仍未证明“后台发布 / 开通会员 -> 前台同步变化”的真实环境一致性
- recruit 链已具备后台最小状态治理、角色矩阵接口与建议权限包，且当前启用中的 `ADMIN` 角色已显式包含 `menu/page/action.recruit.*`；但按最新产品口径，“通告”已改为平台创建的二期产物、首页主入口应切到演员档案列表，因此当前 `recruit` 更适合作为二期能力基建保留，而不是继续占用首页主入口；`2026-04-03 10:56` 已通过 `execution/recruit/samples/20260403-105631-recruit-mini-program-page-evidence/summary.md` 补齐 7 个小程序页面的 `route + query + screenshot + page-data` 证据，`11:09` 又通过 `execution/recruit/samples/20260403-110916-recruit-admin-page-evidence/summary.md` 补齐 `/recruit/projects`、`/recruit/roles`、`/recruit/applies` 三页后台列表与详情抽屉证据，因此其余剩余问题已继续收口为“未来新增角色的持续治理约束、演员自我档案冗余路由与 `project` 兼容层问题”
- 同日小程序首页实现也已继续跟上该口径：`kaipai-frontend/src/pages/home/index.vue` 现已把演员首页主入口切到 `searchActors -> actor-profile/detail`，并修正性别 quick filter 使用后端真实枚举 `male / female`；因此 recruit 当前剩余重点不再是“首页还在读角色列表”或“后台页证据未补”，而是“演员自我档案读取路由仍有冗余，以及二期平台创建通告的后续承接边界”
- `2026-04-02 19:19` 已确认当前外部后端入口 `http://101.43.57.62/api` 可达：`/api/v3/api-docs` 返回 `200`，`/api/auth/sendCode` 返回开发态验证码，`/api/auth/login` 可直接为 `user_id=10000` 签发真实 token
- 服务器 `/opt/kaipai/docker-compose.yml` 已直接证明当前后端容器按 `NACOS_ENABLED=true + SPRING_PROFILES_ACTIVE=dev` 运行；启动日志也明确订阅 `kaipai-backend-dev.yml` 并激活 `dev` profile
- `2026-04-02 19:23` 已重新发版当前仓后端 jar，远端 `/opt/kaipai/kaipai-backend-1.0.0-SNAPSHOT.jar` SHA256 已变更为 `44d372ae416f06381c94ec797255ed9eacffa8d70d97ffb68f28334849f7969a`
- `2026-04-02 19:25` 已复测通过：`/api/user/me`、`/api/verify/status`、`/api/invite/stats`、`/api/level/info`、`/api/card/scene-templates`、`/api/card/personalization` 全部返回 `200`，旧 jar / 旧路由阻塞已解除
- `2026-04-03 03:07` invite 修复后的真实自动样本 `execution/invite/captures/invite-20260403-030705-remote-invite-auto` 已显示 14 个 actor/admin endpoint 全部 `ok`，其后 `2026-04-03 04:00` 的闭环样本已继续把 `eligibility` 补到同一样本链上，并在 `validation-result.txt` 中确认 `grant_id=2 -> source_ref_id=11`，说明当前 invite 剩余主风险已不再是资格链闭环，而是微信官方小程序码能力
- `2026-04-02 19:26` 已继续纠正资格口径：`verify-status=2` 的同一用户，`level-info.isCertified` 已对齐为 `true`，`shareCapability.reasonCodes` 与 personalization capability 当前统一为 `profile_completion_required / fortune_missing / level_required`
- `2026-04-02 19:41` 已按 `profile-fortune-backfill` 样本补齐 `user_id=10000` 的 `actor_profile / fortune_report`，并确认 `GET /api/fortune/report`、`GET /api/level/info`、`GET /api/card/personalization?actorId=10000&scene=general&loadFortune=true` 全部返回 `200`；同一用户 `profileCompletion=95`，`fortuneLuckyColor=#FF6B35`，`reasonCodes` 已收敛为仅剩 `level_required`
- `2026-04-02 19:52` 已按 `admin-membership-template-chain` 样本跑通后台会员与模板联动：同一用户 `membershipTier` 已出现 `member -> none -> member` 变化，`/api/card/personalization` 主题主色已从 `#2F6B5F -> #7A3E2B`，最新发布记录为 `publishLogId=3 / publishVersion=SMOKE_V2_ADMIN_20260402_195744`
- 同一样本的 DB 采证也已清理干净：`membership_account`、`membership_change_log`、`card_scene_template`、`template_publish_log` 与 `admin_operation_log.operation_log_id` 均已可回读，不再带 `Unknown column 'log_id'` 报错
- 本轮也已确认上一版 backfill 失败根因是远端 `docker exec mysql` 执行 SQL 文件时缺少 `--default-character-set=utf8mb4`，而不是表结构、DTO 或运行时版本不一致
- `2026-04-02 20:23` 到 `20:49` 的 DevTools 未授权阻塞已通过 `WeappLog`、CLI 重放、权限缓存和新路径探针完整固化到 membership 样本 `captures/devtools-auth-blocker.txt`
- `2026-04-02 20:53` 官方 `cli auto --project ... --auto-port 9421` 已恢复；`2026-04-02 21:09` 已通过 automator 建立真实前台会话并补齐 `membership / actor-card / detail / invite / fortune` 五页截图，实际路由回读已写入 `captures/mini-program-screenshot-capture.json`
- `2026-04-02 21:36` 已继续补齐 `execution/membership/samples/20260402-212713-dev-fortune-theme-lv5-unlock`：同一用户当前有效邀请数已提升到 `8`，`/api/level/info.level=5`，`/api/card/personalization` 已返回 `themeId=general-member-fortune / primary=#FF6B35 / enableFortuneTheme=true`，并再次补齐 `membership / actor-card / detail / invite / fortune` 五页截图
- 同一样本也保留了首保存失败历史证据：当 `actor_card_config` 不存在时，`POST /api/card/config` 曾因 `Field 'template_id' doesn't have a default value` 返回 `500`
- `2026-04-02 21:57` 已继续通过 plain `docker` 重建当前 dev 运行时，容器 `/app/app.jar` SHA256 已对齐 `88d23af6cb2934097e2dc0e149537c0e96f18951e6bddc0ad82455a94fdea641`
- `2026-04-02 21:59` 已删除 `actor_card_config / actor_share_preference` 后再次复测首保存：`POST /api/card/config` 返回 `200/200`，DB 已回读 `template_id=1 / enable_fortune_theme=1`
- `2026-04-02 22:15` 已继续补齐模板 rollback -> frontend summary -> restore publish 链路：rollback 后 `/api/card/scene-templates` 与 `/api/card/personalization.profile.template` 回到 builtin `通用 / #ff7a45`，restore publish 后恢复到 `Smoke Template / #7A3E2B`
- `2026-04-02 22:16` 已继续补齐后台页面截图：同一份 `Lv5` 样本现在包含会员账户页、模板页与回滚弹窗三张 admin 图
- `2026-04-02 22:30` 已继续补齐 rollback 前后的小程序阶段截图：`actor-card` 确认会从 `Smoke Template` 切到 `通用` 再恢复，而 `detail / invite` 仍统一落在 `general-member-fortune` 路由与主题层，说明当前 `Lv5 + enableFortuneTheme=1` 样本下 fortune 主题优先级高于模板回滚视觉变化
- `2026-04-03 11:26` 已先按 `execution/membership/samples/20260403-112652-dev-template-rollback-no-fortune-theme/summary.md` 补齐首份 no-fortune rollback 哈希样本：
  - `actor-card` SHA 从 `AB50A24F... -> 19C8615D... -> AB50A24F...`
  - `detail / invite` 当时仍保持同哈希
  - 三段 `detail / invite` 路由都已固定在 `themeId=general-member-base`
- `2026-04-03 12:03` 已继续在前端补齐 `detail / invite` 的模板 / artifact 首屏文案消费，重新执行 `kaipai-frontend npm run type-check`、`npm run build:mp-weixin`，并先产出样本 `execution/membership/samples/20260403-120307-dev-template-rollback-no-fortune-theme/summary.md`
  - `actor-card` SHA：`AB50A24F... -> 19C8615D... -> AB50A24F...`
  - `detail` SHA：`97E4C31E... -> CCC4BB27... -> 97E4C31E...`
  - `invite` SHA：`213439AE... -> 4D126C62... -> 213439AE...`
  - `detail` 页首屏文案已从 `Smoke Template公开名片页` 切到 `通用公开名片页`
  - `invite` 页首屏文案已从 `Smoke Template风格邀请卡` 切到 `通用风格邀请卡`
- 同一轮也已把 membership 小程序采证脚本补成和 recruit 一样的阶段 `page-data` 证据粒度，因此 membership 当前缺的已不再包含“detail / invite 是否真正消费到可回滚的模板视觉层”，而是“preview overlay 是否要从已可审计的前端边界继续升级为后端事实”以及“其余切片是否也补齐同等级真实样本”
- `2026-04-03 12:13` 已再次执行 `execution/membership/run-preview-overlay-static-audit.py preview-overlay-static-audit-post-session-decision`，新样本 `execution/membership/samples/20260403-121354-preview-overlay-static-audit-post-session-decision/summary.md` 继续 `findingCount=0`，且 helper 白名单已不再包含 overlay path patch；这说明当前边界又进一步从“session 恢复 + 少量历史 patch”收口为“session 恢复 + query 兼容读取”
- `2026-04-03 12:14` 又已重跑 `execution/membership/run-admin-template-rollback-mini-program-no-fortune-theme.py`，最新样本 `execution/membership/samples/20260403-121415-dev-template-rollback-no-fortune-theme/summary.md` 与 `admin-template-rollback-mini-program-summary.md` 继续稳定复现 `actor-card / detail / invite` 三页截图哈希变化，并首次把 `before / after-rollback / after-restore` 三段 `page-data` 文件直接写进摘要。由此可把 membership 当前关于 preview overlay 的工程结论固定为：在没有跨登录、跨设备证据前，继续保持 `preview-overlay-decision-record.md` 规定的 session-only 模型，不再继续发明新的 overlay path patch 或无证据后端化。
- `2026-04-03 12:26` 已继续删除 `readPersonalizationPreviewOverlay` 与四个旧 overlay query key，并重跑样本 `execution/membership/samples/20260403-122635-preview-overlay-static-audit-no-query-keys/summary.md`；结果继续 `findingCount=0`，且对 `kaipai-frontend/src` 的全文搜索已无 `previewLayout / previewPrimary / previewAccent / previewBackground / readPersonalizationPreviewOverlay(` 命中。这说明 membership 当前 overlay 已不仅是“运行时 session-only”，而是“代码结构也已完全去掉历史 query 兼容包袱”。

## 5. 分工作流评估

| 工作流 | 当前判定 | 评估结论 |
|--------|----------|----------|
| 基础治理与共享基线 | 较稳 | `00-28`、状态卡、切片卡、共享 helper 已建立，治理入口已真实存在 |
| 平台核心域与后台治理 | 局部完成 | 会员 / 邀请 / 模板 / 登录 / 招募后台入口已基本具备，recruit 当前启用角色权限矩阵已收口，但其余切片的真实环境证据与长期治理边界仍未完全收口 |
| 小程序演员主线与分享主线 | 局部完成 | 主事实源已从页面拼装转向后端 personalization 摘要，preview overlay 也已有统一 helper 和静态审计，但其本体与部分运行时 fallback 仍是结构缺口 |
| AI 与个性化增强 | 演进中 | 已有最小 quota / polish 能力，且 AI 简历已补 actor/admin 真实样本、最小治理协同样本、目标环境业务回归样本、角色矩阵收口、前后台页面证据与目标环境 fallback 退场复验，仓内 fallback 代码也已移除；但更完整治理协同仍缺、真实 LLM 仍未接入 |

## 6. 当前不宜误判为“已完成”的点

1. 不能因为页面已切到真接口分支，就认定环境已经真实连通；当前虽已停止“缺 base 静默回退 mock”，但显式 mock 演示分支仍在。
2. 不能因为 `/card/personalization` 已上线，就认定分享链已经完全后端化；preview overlay 仍是前端显式态。
3. 不能因为微信登录契约已存在，就把未来微信能力混进当前阶段闭环；当前阶段仍应以手机号登录主链验收。
4. 不能因为后台页面已出现或已有一轮页面样本，就认定治理完成；recruit 当前虽已补小程序与后台页面级证据，但兼容层长期治理、新增角色约束和二期产品边界仍未完成，AI 虽已补真实环境样本、角色矩阵收口、前后台页面证据与 fallback 退场复验，但仍缺完整协同流转。
5. 不能因为 invite API + DB 闭环已经跑通，就忽略当前版本仍有页面边界和展示收口；但微信官方 `wxacode` 已不再是当前阶段必达项。

## 7. 优先级建议

1. 保持当前已修正的线上运行时，继续核对 `NACOS_ENABLED / SPRING_PROFILES_ACTIVE / Nacos dataId / datasource`，避免后续回退到旧能力集合。
2. 继续补闭环证据，并跑三组真实样本回填：
   - 在已有 `admin-membership-template-chain` 与 `fortune-theme-lv5-unlock` 两组样本基础上，继续核对后台开通会员 / 发布模板 -> 前台变化，以及首次保存配置是否已恢复
   - 邀请 -> 注册 -> `referral_record` -> 风控 / 资格 -> 前台状态
     当前已新增 `execution/invite/run-authenticated-invite-sample.py` 作为标准登录态入口，后续 invite 样本应统一走该脚本生成，不再手工拼 token 与样本主键
3. 再决定 preview overlay 是否迁入后端临时摘要或更强 session 级状态；当前若没有跨登录、跨端、跨设备的新证据，应继续遵守 `preview-overlay-decision-record.md` 的 session-only 决策，不再把它隐藏成局部页面逻辑。
4. 把 AI 剩余真实样本和回滚约束继续收口，同时把 recruit 页面层证据与新增角色授权标准继续固化，避免后台治理长期停留在“最小可操作”阶段。
5. 微信登录与官方 `wxacode` 保留到未来明确能力批次时再通过 `wechat-config-gate-runbook.md` 推进，不再占用当前阶段主推进顺位。

## 8. 结论

- 当前整体架构方向是对的，且比“到处 still mock”阶段前进明显
- 当前最大的风险已经不再是“有没有开始连后端”，也不再是“线上跑着旧能力集合”，而是“真实业务样本和前后台一致性证据还没补齐”
- 因此下一步的主线不再是继续排查旧运行时，而是围绕真实样本把 `verify / invite / membership / login-auth` 四条主链判定收口，并补全后台动作、小程序页面和数据库三类证据

### 2026-04-03 补充说明

- 今日重新探测真实环境时，确实先出现过 runtime 漂移：`POST /api/admin/auth/login` 一度返回 `500`，因此没有直接沿用 `2026-04-02` 的联通结论
- 本轮已先在本地补两类收口修复，防止把参数脏值和历史脏数据误判成架构阻塞：
  - 前端 / 后台 recruit 查询统一过滤 `undefined / null / '' / NaN`
  - 后端 admin recruit 聚合统一过滤 `company_profile.extendedField.projects` 中的 `null` 项
- 随后已按 `00-29` 新增的 `backend-only` 标准发布链路完成真实后端重发，发布记录为 `20260403-013415-backend-only-auth-runtime-check-final.md`
- 重发后的公网结果已恢复到：
  - `GET http://101.43.57.62/api/v3/api-docs` -> `200`
  - `POST http://101.43.57.62/api/admin/auth/login` -> `200`
  - 未携带 token 的 `GET /api/admin/recruit/roles...` 与 `GET /api/role/search...` -> `401`
- 这说明今天的主阻塞已经从“后端运行时继续 500”重新收口为“接口鉴权前置与真实带 token 样本还未补齐”；下一步应继续按真实登录态重跑后台招募页与演员端读链路样本，而不是再把问题归咎为后端未发版
- 随后已继续按 spec 收口 recruit 真实样本，不再使用临时命令联调：
  - `execution/recruit/run-authenticated-recruit-sample.py` 已成为 recruit 真实登录态样本的标准入口
  - 最新样本 `execution/recruit/samples/20260403-020306-recruit-fixes-post-company-fix/summary.md` 已完整跑通 `company save -> project -> role -> apply -> admin projects/roles/applies -> project/role governance`
  - 本轮 recruit 后端已真实修复并上线：
    - 分页拦截器缺失导致 `total=0 / list 非空`
    - 角色搜索 `projectId` 错映射到 `recruitPostId`
    - 项目状态治理只改副本不落库，导致“项目结束后仍可恢复角色”
    - 公司资料保存时 `update_user_name` 为空，导致 `/api/company` 返回 `code=500`
- `2026-04-03 02:11` 已继续按 `00-29` 标准 `admin-only` 脚本完成管理端发布，记录为 `.sce/runbooks/backend-admin-release/records/20260403-021050-admin-only-recruit-governance-pages.md`
- 发布后已补做管理端 recruit 线上业务 smoke：
  - 登录态 `GET /api/admin/recruit/projects`、`/roles`、`/applies` 均返回 `200`
  - `/recruit/projects`、`/recruit/roles`、`/recruit/applies` 均返回当前 SPA 静态入口
- 随后已继续按同一套 spec/runbook 把 recruit 角色矩阵收口到真实角色分配流程：
  - `/api/admin/system/roles/recruit-governance-matrix` 已上线并返回 `200`
  - `2026-04-03` 当前公网登录回包已显式包含 `menu.recruit`、`page.recruit.*` 与 `action.recruit.*`
  - 当前矩阵返回 `recruitReadyRoleCount=1`、`fallbackRoleCount=0`、`canRetireFallback=true`
  - 唯一启用角色 `ADMIN` 当前已是 `rolloutStage='recruit_ready'`
- `2026-04-03 06:51` 已再次通过标准 recruit 样本 `execution/recruit/samples/20260403-065131-continue-recheck/summary.md` 重跑真实链路，actor/admin 全部检查继续 `PASS`
- `2026-04-03 06:57` 又已按 `00-29` 标准 `backend-only` 脚本完成后端发布 `.sce/runbooks/backend-admin-release/records/20260403-065616-backend-only-recruit-role-search-undefined-guard.md`，并在发布后确认：
  - 带 `ADMIN` token 的 `GET /api/admin/recruit/roles?pageNo=1&pageSize=20&keyword=` -> `200`
  - 带真实演员 token 且故意传 `minAge=undefined&maxAge=undefined` 的 `GET /api/role/search?...` -> transport `200` / payload `code=200`
- 因此当前整体评估还应补一条：recruit 主线的最新线上阻塞已不再包含“旧缓存或手工请求把 `undefined` 数字筛选值打成 `400`”；剩余重点已继续收口为长期兼容层治理、持续角色收口，以及微信配置主线
- `2026-04-03 10:56` 已继续通过 `execution/recruit/run-recruit-mini-program-page-evidence.py` 产出样本 `execution/recruit/samples/20260403-105631-recruit-mini-program-page-evidence/summary.md`：
  - `crew-home-projects`、`crew-apply-manage`、`actor-home-archive`、`actor-role-detail`、`actor-apply-confirm`、`actor-my-applies`、`actor-apply-detail` 七页均已保留 `route + query + screenshot + page-data`
  - 脚本当前已收口为“bootstrap 先断开 + 每页独立 automator 连接”，`captures/mini-program-screenshot-capture.json` 记录 `fallbackCount=0`
  - 同一样本当前 `visualReview.uniqueScreenshotHashCount=7`、`visualDidNotRefresh=false`
- 因此当前整体评估应更新为：recruit 主线的真实阻塞已从“核心接口与治理规则不稳定、角色仍靠 fallback”收口为“页面证据已补齐后的兼容层长期治理、角色持续收口与微信配置主线仍待继续收口”
- 同日 invite 主线也已继续收口：后端二维码修复发布后，公网 `/api/invite/code` 与 `/api/invite/qrcode` 均已恢复 `200`，并已通过标准 validation 样本固定证据目录；随后又按 `00-29` 新增的标准只读诊断入口抓到 `verify/submit` 的真实堆栈，定位根因为 `IdentityVerificationServiceImpl.submit(...)` 回写 `user.update_user_name=null`
- `2026-04-03 03:59` 已按标准 `backend-only` 脚本完成 invite 实名修复发布，记录为 `.sce/runbooks/backend-admin-release/records/20260403-035854-backend-only-invite-verify-submit-fix-rerun.md`
- `2026-04-03 04:00` 已继续通过真实样本 `execution/invite/captures/invite-20260403-040007-remote-invite-e2e-closure-after-verify-fix/validation-report.md` 跑通同一样本闭环：`inviteeUserId=10017`、`referralId=11`、`grantId=2`、`policyId=1`，actor/admin 共 15 个 endpoint 全部 `ok`，并已证明 `referral_record.status=1 -> grant.sourceType=referral/sourceRefId=11 -> /level/info.membershipTier=member`
- 因此当前整体评估应更新为：invite 主线的真实阻塞已从“二维码查询面 500 / 资格链未闭环”收口为“微信官方小程序码与真实扫码落地证据仍待补齐”
- 同日 `00-29` 微信配置同步链也已继续补齐“本地输入位初始化 + placeholder/fake secret 拒绝”规则：`init-local-wechat-secret-file.py` 已可创建 gitignored 的本地 secret 文件，但 `read-local-wechat-config-inputs.py` 与总控样本 `20260403-083329-backend-wechat-config-pipeline-continue-wechat-local-gate.md` 已证明 placeholder secret 仍会被拦在 `local_input_not_ready`。因此当前微信主线的精确 blocker 已从“本地缺输入位”收口为“缺合法 secret 来源”
- 同日 login-auth 也已继续用样本 `execution/login-auth/samples/20260403-122932-dev-legal-secret-gate-aligned/validation-report.md` 把三层门禁放进同一份证据：前端 `VITE_ENABLE_WECHAT_AUTH=false`、本地 secret 文件虽存在但仍不合法、远端 `POST /api/auth/wechat-login` 继续返回 `微信登录未配置小程序 appId/appSecret`。因此整体评估里关于微信主线的 blocker 现在应统一理解为“缺合法 secret 来源 + 前端真实开关未放开”，而不再只是“代码已接但缺样本”
- `2026-04-03` 已继续把 invite 前端的静默 fallback 收紧到 mock 演示态：当前 `src/stores/user.ts` 不再在真实环境自动补 `/api/invite/qrcode`，`src/pkg-card/invite/index.vue` 也不会在后端缺少 `inviteLink` 时继续伪装分享落点可用；因此 invite 主线后续若再缺字段，会直接暴露为显式阻塞，而不是被前端本地 path 掩盖
- 同日 AI 简历主线也已继续收口：`execution/ai-resume/run-ai-resume-validation.py` 已成为 AI 标准真实样本入口，最新样本 `execution/ai-resume/samples/20260403-071241-continue-rerun/summary.md` 已跑通 actor `quota -> polish -> save -> history -> rollback` 与 admin `overview -> histories -> failures -> sensitive-hits -> review -> close -> operation-logs`
- 随后 `2026-04-03 07:21` 又已通过标准角色收口样本 `execution/ai-resume/samples/20260403-072120-continue-ai-role-closure/summary.md` 把公网 `ADMIN` 角色从 `fallback_only` 推进到 `ai_ready`，并确认 `aiReadyRoleCount=1`、`fallbackRoleCount=0`、`canRetireFallback=true`，重新登录后的会话也已拿到三枚 AI 独立权限
- 同日 AI 页面级证据与目标环境发布复验也已继续收口：`execution/ai-resume/run-ai-admin-page-evidence.py` 已实际产出样本 `execution/ai-resume/samples/20260403-161131-ai-admin-page-evidence/summary.md`，固定 `/system/ai-resume-governance` 的 overview、history detail、failure detail 三组后台页面证据；`16:17` 又已通过官方 `cli auto --project ... --auto-port 9421` 恢复 DevTools 自动化，恢复现场固定在 `execution/ai-resume/samples/20260403-161755-ai-mini-program-devtools-replay/`；随后 `16:22` 复跑 `execution/ai-resume/run-ai-mini-program-page-evidence.py` 产出样本 `execution/ai-resume/samples/20260403-162122-ai-mini-program-page-evidence-rerun/summary.md`，确认 `actor-card / actor-profile-edit / actor-profile-edit-ai-panel / actor-profile-detail` 四页全部走 `automator`。随后又发现公网首页仍加载旧 bundle `index-C-pIOoT5.js` 且保留 `pagePermissionFallbacks:["page.system.operation-logs"]`，因此 `16:29` 已按 `00-29` 标准 `admin-only` 脚本完成目标环境后台静态资源发布，记录为 `.sce/runbooks/backend-admin-release/records/20260403-162902-admin-only-ai-fallback-retirement-static-sync.md`；发布后公网首页切到 `index-bd3NuCPI.js`，且新的 bundle 已不再包含该 fallback 片段
- `16:41` 又已通过新增标准样本 `execution/ai-resume/run-ai-resume-collaboration-validation.py` 产出 `execution/ai-resume/samples/20260403-164135-continue-ai-collaboration-closure/summary.md`，在真实环境固定 `collaboration-catalog -> assign -> acknowledge` 与 `collaboration-catalog -> assign -> remind` 两条最小责任协同链，并确认 `pending_ack / acknowledged` 筛选和 `ai_resume_assign / ai_resume_acknowledge / ai_resume_remind` 审计回看同时成立
- `16:50` 又已通过新增汇总脚本 `execution/ai-resume/run-ai-resume-business-regression-summary.py` 产出 `execution/ai-resume/samples/20260403-165026-continue-ai-business-regression-summary/summary.md`，把同一轮 `quota -> polish -> save -> history -> rollback` 主链样本与 `actor-card / actor-profile-edit / actor-profile-edit-ai-panel / actor-profile-detail` 四页真机页面证据固定为一条标准业务回归记录，且本轮页面样本继续 `visualDidNotRefresh=false`
- 因此当前整体评估应再更新为：AI 简历主线的真实阻塞已从“缺真实环境样本 / 角色尚未绑定 / 页面证据未补 / 最小协同未复验 / 业务回归未补 / 目标环境 fallback 退场未复验”收口为“通知回执 / 自动催办 / 更细 SLA 等更完整治理协同仍未闭环，以及真实 LLM 未接入”
- 同日演员首页产品切换的实现与文档也已同步：前端身份选择文案、首页 quick filter 与 `kaipai-frontend/docs/link-analysis.md`、`docs/page-mindmap.md` 已统一改为“演员档案首页”口径；因此 00-28 后续对 recruit 的判断应继续以“保留能力链 + 二期基建”记录，而不再把首页演员入口当作 role/search 验收面
- 同日分享个性化主线也已继续把页面级重复逻辑下沉：`05-11` 的 `T11` 已收口完成，`actor-card / invite / actor-profile/edit` 内重复的认证 CTA 文案已统一沉到 `src/utils/verify.ts` 的场景化 helper，`actor-card / membership` 继续共用 `KpDualActionRow.vue`，而 `invite` 四宫格也已被明确判定为“带二维码状态与多动作门禁的页内特例”，不再作为待抽象的悬而未决项。这说明当前分享主线的剩余风险，已不再包括“页面各自分叉一套认证/分享按钮口径”，而重新聚焦到微信真实样本与 preview overlay 事实源边界。
