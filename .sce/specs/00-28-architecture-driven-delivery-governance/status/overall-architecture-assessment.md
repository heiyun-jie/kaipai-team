# 00-28 整体架构与实现评估

## 1. 评估归属

- 上位治理：`../design.md`
- 评估输入：`verify-status.md`、`invite-status.md`、`membership-status.md`、`login-auth-status.md`、`ai-resume-status.md`、`crew-company-project-status.md`、`recruit-role-apply-status.md`
- 评估日期：`2026-04-03`

## 2. 总体判定

- 当前判定：`局部完成`
- 一句话结论：`00-28` 已经把前端、小程序后端和后台推进方式从“按页面修补”推进到“按能力切片收口”，verify / 邀请 / 会员 / 登录 / 剧组招募 / AI 简历几条主线都已形成最小真实契约、状态卡和标准发布链；`2026-04-03` 又继续把 verify 的 reject/retry/approve 真实样本、invite / recruit 的线上记录，以及 AI 简历的 actor/admin 真实样本和角色矩阵收口到同一套 spec/runbook 流程，当前主风险已经进一步切换为“微信链路仍缺真实配置与样本、会员分享编辑态仍保留前端显式 overlay，以及 AI / recruit 等切片仍存在兼容层与页面级证据缺口”，因此当前仍不能判定为整体架构闭环完成。

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
| login / invite wx 链路 | 会；若小程序缺 `VITE_API_BASE_URL` 会整段退回 mock，且当前 `VITE_ENABLE_WECHAT_AUTH=false` | 已接通到真实后端，但当前真实返回是显式失败 | 缺 `WECHAT_MINIAPP_APP_ID / APP_SECRET`、缺微信真实样本 |
| invite 主线 | 小程序运行时有全局 mock 总闸，但当前 `.env` 已明确 `VITE_USE_MOCK=false` | 已接通，且 actor/admin/API/DB 同一样本已闭环 | 缺微信官方 `wxacode` 与真实扫码落地证据 |
| verify 主线 | 同上，存在全局 mock 总闸但当前标准真实样本已采证 | 已接通，且 `提交 -> 拒绝 -> 重提 -> 通过` 已跑通 | 仅剩页面级证据与少量模板文档回填 |
| membership 主线 | 同上，仍受全局 mock 总闸影响 | 已接通，且后台动作 / API / DB / 小程序截图证据已较完整 | preview overlay 已收口为当前设备 session 预览态，但仍不是后端事实源，且当前真实样本固定在 `dev + Nacos` |
| recruit 主线 | 小程序和后台本地开发都可能误读为“只是本地代理”，但线上接口已发布 | 已接通，且后台治理与登录态样本已跑通 | 缺页面级证据，`project` 仍在兼容层 |
| AI 简历 | 受全局 mock 总闸影响，且当前仍保留本地 mock adapter | 已接通，且 actor/admin/rollback/审计与角色矩阵收口样本已跑通，仓内 fallback 代码也已退场 | 缺真机页面级证据、目标环境发布复验与更完整治理协同 |

## 4. 主要结构性风险

### 4.1 运行时仍保留自动回退 mock 机制，但已开始显式暴露阻塞

- `kaipai-frontend/src/utils/runtime.ts` 仍以 `VITE_USE_MOCK === 'true'` 或“缺少 `VITE_API_BASE_URL`”作为全局 mock 总闸；这意味着目标环境只要运行时配置缺失，就会整段退回 mock，而不是显式失败
- 当前大量 API 模块仍保留 `useApiMock(...) ? mock : real` 双轨调用，因此“页面能跑起来”不等于“架构已连通”
- 这不是局部实现细节，而是整体架构判断风险；如果不先补环境证据，就可能把演示态误当成联通态
- `2026-04-02` 已先把该风险显式化：前端 `App` 启动时会直接提示“缺少 `VITE_API_BASE_URL` 导致自动回退 mock”或“`VITE_USE_MOCK=false` 但缺少 base URL”，并且 `normalizeApiBaseUrl()` 不再错误移除 `:8080`

### 4.2 会员分享编辑态仍不是后端事实

- `kaipai-frontend/src/utils/personalization.ts` 已把 preview overlay 明确成统一 helper，并进一步补成“query 兼容读取 + 当前设备 session 主恢复”
- 这比散落在页面里或继续靠 query patch 传递更好，但它仍是前端显式预览态，而不是后端临时摘要或更强事实源
- 当前 membership 状态卡已经明确把这点列为未闭环主因之一，因此它是收敛后的剩余主风险，不应再被视作普通 UI 细节

### 4.3 登录链路仍停留在“真实契约 + 开发态能力”

- 后端微信登录接口和邀请码透传已接好，但真实环境仍缺 `WECHAT_MINIAPP_APP_ID / WECHAT_MINIAPP_APP_SECRET` 与微信样本联调证据
- `AuthServiceImpl.sendCode(...)` 当前仍直接返回验证码，只能证明接口接通，不能视作正式短信能力闭环
- 登录切片已经从“前端 mock 成功”推进到“真实接口 + 显式失败”，但还没有推进到“真实环境闭环”

### 4.4 真实环境主阻塞已从“旧 jar / 大面积 500”转向“微信配置、页面证据与兼容层治理”

- invite 链已收口到邀请码、`referral_record`、后台规则 / 风控 / 资格发放与前台展示；`2026-04-03 03:07` 的真实自动样本已证明 `/api/invite/code`、`/api/invite/qrcode`、`/api/invite/stats`、`/api/invite/records` 与后台记录 / 风控 / 策略查询均返回 `200`，`2026-04-03 04:00` 的闭环样本又进一步证明了 `实名审核 -> referral_record.status=1 -> user_entitlement_grant(sourceType=referral) -> /level/info.membershipTier=member` 可在同一样本上打通，随后同一样本 DB 回读也已补齐，因此 invite 主阻塞已从“查询面 500 / 资格链未闭环”收口为“微信官方小程序码能力待补齐”
- verify 链也已不再停留在“缺真实联调”：`2026-04-03 05:34` 已通过只读日志诊断确认 reject/retry 新实现上线后首次失败的真实根因为“目标库未执行新 migration”；随后 `05:42` 已通过标准 schema 发布脚本执行 `V20260403_001__identity_verification_resubmit_history.sql`，`05:47` 已通过带 schema 门禁的新 `backend-only` 再次发布，`05:49` 又已在最新运行时跑通 `提交 -> 拒绝 -> 重提 -> 通过` 标准样本，并由 `validation-result.txt` 固定 `schema_release_history / identity_verification_owner / 两条申请单 / 两条审核日志` 四类证据
- membership 链已具备后台模板 / 会员治理和前台 personalization 摘要，但仍未证明“后台发布 / 开通会员 -> 前台同步变化”的真实环境一致性
- recruit 链已具备后台最小状态治理、角色矩阵接口与建议权限包，且当前启用中的 `ADMIN` 角色已显式包含 `menu/page/action.recruit.*`；但页面级证据、未来新增角色的持续治理约束和 `project` 兼容层问题仍未收口
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
- 这说明 membership 当前缺的已不再是“DevTools 账号是否有权限”“小程序页面有没有编译出来”“首存配置修复是否已进入运行时”或“模板回滚 / 后台截图证据是否齐备”，而是“preview overlay 边界是否继续收口”以及“其余切片是否也补齐同等级真实样本”

## 5. 分工作流评估

| 工作流 | 当前判定 | 评估结论 |
|--------|----------|----------|
| 基础治理与共享基线 | 较稳 | `00-28`、状态卡、切片卡、共享 helper 已建立，治理入口已真实存在 |
| 平台核心域与后台治理 | 局部完成 | 会员 / 邀请 / 模板 / 登录 / 招募后台入口已基本具备，recruit 当前启用角色权限矩阵已收口，但其余切片的真实环境证据与长期治理边界仍未完全收口 |
| 小程序演员主线与分享主线 | 局部完成 | 主事实源已从页面拼装转向后端 personalization 摘要，但 preview overlay 与部分运行时 fallback 仍是结构缺口 |
| AI 与个性化增强 | 演进中 | 已有最小 quota / polish 能力，且 AI 简历已补 actor/admin 真实样本并完成目标环境角色矩阵收口，仓内 fallback 代码也已移除；但真机页面证据未补、目标环境尚未完成退场后复验、真实 LLM 仍未接入 |

## 6. 当前不宜误判为“已完成”的点

1. 不能因为页面已切到真接口分支，就认定环境已经真实连通；当前仍存在运行时静默 mock 回退。
2. 不能因为 `/card/personalization` 已上线，就认定分享链已经完全后端化；preview overlay 仍是前端显式态。
3. 不能因为微信登录契约已存在，就认定登录链闭环；真实环境配置与样本验证仍缺。
4. 不能因为后台页面已出现，就认定治理完成；recruit 仍缺页面层证据与兼容层长期治理，AI 虽已补真实环境样本并完成角色矩阵收口，但仍缺页面级证据、fallback 退场验证与完整协同流转。
5. 不能因为 invite API + DB 闭环已经跑通，就认定邀请切片全部完成；当前仍缺微信官方 `wxacode` 与真实扫码落地证据。

## 7. 优先级建议

1. 保持当前已修正的线上运行时，继续核对 `NACOS_ENABLED / SPRING_PROFILES_ACTIVE / Nacos dataId / datasource`，避免后续回退到旧能力集合。
2. 继续补闭环证据，并跑三组真实样本回填：
   - 在已有 `admin-membership-template-chain` 与 `fortune-theme-lv5-unlock` 两组样本基础上，继续核对后台开通会员 / 发布模板 -> 前台变化，以及首次保存配置是否已恢复
   - 邀请 -> 注册 -> `referral_record` -> 风控 / 资格 -> 前台状态
     当前已新增 `execution/invite/run-authenticated-invite-sample.py` 作为标准登录态入口，后续 invite 样本应统一走该脚本生成，不再手工拼 token 与样本主键
   - 微信老用户登录 / 新用户自动注册 + `inviteCode` 透传
3. 再决定 preview overlay 是否迁入后端临时摘要或 session 级状态；如果不迁，至少把它明确标注为长期保留边界，而不是继续隐藏成局部页面逻辑。
4. 把 invite / login-auth / AI 剩余真实样本和回滚约束继续收口，同时把 recruit 页面层证据与新增角色授权标准继续固化，避免后台治理长期停留在“最小可操作”阶段。
5. 保持当前 `dev + Nacos` 运行时与 `/app/app.jar` 已验证版本，避免后续环境切换再次把已证实链路打回旧能力集合。

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
- 因此当前整体评估还应补一条：recruit 主线的最新线上阻塞已不再包含“旧缓存或手工请求把 `undefined` 数字筛选值打成 `400`”；剩余重点仍是页面层证据、长期兼容层治理，以及微信配置主线
- 因此当前整体评估应更新为：recruit 主线的真实阻塞已从“核心接口与治理规则不稳定、角色仍靠 fallback”收口为“页面层证据与兼容层长期治理仍待补齐”
- 同日 invite 主线也已继续收口：后端二维码修复发布后，公网 `/api/invite/code` 与 `/api/invite/qrcode` 均已恢复 `200`，并已通过标准 validation 样本固定证据目录；随后又按 `00-29` 新增的标准只读诊断入口抓到 `verify/submit` 的真实堆栈，定位根因为 `IdentityVerificationServiceImpl.submit(...)` 回写 `user.update_user_name=null`
- `2026-04-03 03:59` 已按标准 `backend-only` 脚本完成 invite 实名修复发布，记录为 `.sce/runbooks/backend-admin-release/records/20260403-035854-backend-only-invite-verify-submit-fix-rerun.md`
- `2026-04-03 04:00` 已继续通过真实样本 `execution/invite/captures/invite-20260403-040007-remote-invite-e2e-closure-after-verify-fix/validation-report.md` 跑通同一样本闭环：`inviteeUserId=10017`、`referralId=11`、`grantId=2`、`policyId=1`，actor/admin 共 15 个 endpoint 全部 `ok`，并已证明 `referral_record.status=1 -> grant.sourceType=referral/sourceRefId=11 -> /level/info.membershipTier=member`
- 因此当前整体评估应更新为：invite 主线的真实阻塞已从“二维码查询面 500 / 资格链未闭环”收口为“微信官方小程序码与真实扫码落地证据仍待补齐”
- `2026-04-03` 已继续把 invite 前端的静默 fallback 收紧到 mock 演示态：当前 `src/stores/user.ts` 不再在真实环境自动补 `/api/invite/qrcode`，`src/pkg-card/invite/index.vue` 也不会在后端缺少 `inviteLink` 时继续伪装分享落点可用；因此 invite 主线后续若再缺字段，会直接暴露为显式阻塞，而不是被前端本地 path 掩盖
- 同日 AI 简历主线也已继续收口：`execution/ai-resume/run-ai-resume-validation.py` 已成为 AI 标准真实样本入口，最新样本 `execution/ai-resume/samples/20260403-071241-continue-rerun/summary.md` 已跑通 actor `quota -> polish -> save -> history -> rollback` 与 admin `overview -> histories -> failures -> sensitive-hits -> review -> close -> operation-logs`
- 随后 `2026-04-03 07:21` 又已通过标准角色收口样本 `execution/ai-resume/samples/20260403-072120-continue-ai-role-closure/summary.md` 把公网 `ADMIN` 角色从 `fallback_only` 推进到 `ai_ready`，并确认 `aiReadyRoleCount=1`、`fallbackRoleCount=0`、`canRetireFallback=true`，重新登录后的会话也已拿到三枚 AI 独立权限
- 因此当前整体评估应再更新为：AI 简历主线的真实阻塞已从“缺真实环境样本 / 角色尚未绑定”收口为“真机页面级证据仍缺、fallback 退场后的目标环境复验仍待补齐，以及真实 LLM 未接入”
