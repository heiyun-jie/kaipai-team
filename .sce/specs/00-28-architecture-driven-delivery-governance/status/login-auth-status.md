# 登录鉴权与前台会话闭环状态回填

## 1. 归属切片

- `../slices/login-auth-capability-slice.md`
- `../execution/login-auth/README.md`

## 2. 当前判定

- 回填日期：`2026-04-03`
- 当前判定：`局部完成`
- 一句话结论：小程序手机号验证码登录 / 注册、`/api/user/me` 会话恢复和 `inviteCode` 透传的最小真实链路已接上，`POST /api/auth/wechat-login` 也已补到后端并由前端显式 `VITE_ENABLE_WECHAT_AUTH` 开关控制；同时登录页已开始拒绝真实环境 `mock-code` 回退，不再把微信授权失败伪装成能力可用。当前 login-auth 的真实阻塞已经继续精确到“缺合法 `WECHAT_MINIAPP_APP_SECRET` 来源”，而不是“代码未接线”或“只差再跑一次 dry-run”，所以当前仍不能写成闭环完成。

## 3. 当前已确认事实

### 3.1 前端 / 小程序

- `kaipai-frontend/src/pages/login/index.vue` 已同时承接手机号验证码登录 / 注册、`inviteCode / scene` 邀请参数和微信手机号授权入口
- `kaipai-frontend/src/api/auth.ts` 已把 `loginByWechat` 切到 `/api/auth/wechat-login`，并在真接口分支下显式拒绝空 `code`，不再回退 `mock-code`
- `kaipai-frontend/src/utils/runtime.ts` 已引入 `wechatAuth` 远端能力，并以 `VITE_ENABLE_WECHAT_AUTH === 'true'` 或 mock 演示态控制微信入口显隐
- `kaipai-frontend/.env` 当前已显式写明 `VITE_USE_MOCK=false`、`VITE_ENABLE_WECHAT_AUTH=false`，避免继续依赖隐式默认值判断是否联真
- `kaipai-frontend/src/stores/user.ts` 已以 `bootstrapSession -> syncActorRuntimeState` 为主路径，在建立会话后再同步 `verify / invite / level`
- `kaipai-frontend/src/pages/login/index.vue` 在未启用微信能力时已改成直接展示具体门禁原因：会区分 `VITE_ENABLE_WECHAT_AUTH=false`、缺少 `VITE_API_BASE_URL` 导致 runtime blocker，以及 mock 演示态，不再统一折成“稍后接入”

### 3.2 后端 / 数据

- `kaipaile-server/src/main/java/com/kaipai/module/controller/auth/AuthController.java` 已稳定提供 `sendCode / login / register / wechat-login`
- `kaipaile-server/src/main/java/com/kaipai/module/server/auth/service/impl/AuthServiceImpl.java` 已补齐微信手机号换取、老用户登录与新用户自动注册
- `kaipaile-server/src/main/java/com/kaipai/module/server/auth/service/impl/AuthServiceImpl.java` 已在微信自动注册时复用邀请注册链路，透传 `inviteCode / deviceFingerprint`
- `kaipaile-server/src/main/java/com/kaipai/module/controller/user/UserController.java` 已提供 `/user/me` 与 `/user/role`，支撑前台会话恢复和身份切换
- `kaipaile-server/src/main/resources/application.yml` 已增加 `wechat.miniapp.app-id / app-secret` 配置位

### 3.3 后台 / 运行配置治理

- 当前 `00-28` 已补入登录切片，运行时配置台账和联调准入条件不再散落在登录页需求文档之外
- 当前仓内仍未发现可直接用于真实联调的 `WECHAT_MINIAPP_APP_ID / WECHAT_MINIAPP_APP_SECRET` 与前端显式启用环境值
- `kaipai-frontend` 当前已新增 `.env.example`，并在 `App` 启动与请求层同时对“缺少 `VITE_API_BASE_URL`”给出显式阻塞：真实请求会直接失败，不再自动回退 mock
- 当前不存在独立登录治理后台页面，本轮后台交付收口为运行配置台账、阻塞项记录和联调准入条件

### 3.4 联调现状

- 当前能确认短信登录 / 注册、会话恢复和登录后同步在代码层已具备最小真实闭环条件
- 当前能确认微信登录已不再是纯前端 mock，而是后端真实契约 + 前端显式能力开关
- `2026-04-02` 已新增 `execution/login-auth` 真实环境运行时清单、验证清单、证据包、样本台账模板与 PowerShell 采证脚本，并已实际执行 `run-login-auth-validation.ps1` 生成样本目录与报告
- `2026-04-02 19:19` 已确认当前外部后端入口可达，且不是单纯“入口不通”：
  - `GET http://101.43.57.62/api/v3/api-docs` -> `200`
  - `POST http://101.43.57.62/api/auth/sendCode` -> `200`，仍直接返回开发态验证码
  - 使用手机号 `13800138000` + 验证码完成 `POST /api/auth/login` -> `200`，返回 `userId=10000` 的真实 token
- `2026-04-03 02:49` 已通过样本目录 `execution/login-auth/samples/20260403-024908-dev-live-probe-ok3` 固化一组 live probe 证据：
  - `run-login-auth-validation.ps1 -EnableLiveProbe` 已可自动落出 `captures/live-probe-sendCode.json` 与 `captures/live-probe-wechat-login.json`
  - `POST http://101.43.57.62/api/auth/sendCode` -> transport `200` / payload `code=200`，消息 `验证码发送成功`，仍直接返回开发态验证码
  - `POST http://101.43.57.62/api/auth/wechat-login` -> transport `200` / payload `code=500`，消息 `微信登录未配置小程序 appId/appSecret`
  - 这说明当前微信阻塞已经从“缺少样本推断”升级为“真实接口业务返回已采证”，主阻塞明确收口为“前端未启微信入口 + 远端缺小程序 appId/appSecret”
- `2026-04-02 19:23` 已完成当前仓后端 jar 替换并重建容器，远端 `/opt/kaipai/kaipai-backend-1.0.0-SNAPSHOT.jar` SHA256 已变更为 `44d372ae416f06381c94ec797255ed9eacffa8d70d97ffb68f28334849f7969a`
- `2026-04-02 19:25` 已再次复测登录后主链：
  - 同一 token 下，`GET /api/user/me`、`GET /api/verify/status`、`GET /api/invite/stats`、`GET /api/level/info`、`GET /api/card/personalization` 全部返回 `200`
  - 当前外部 `/api/v3/api-docs` 已覆盖 `/auth/sendCode`、`/auth/login`、`/user/me`、`/verify/status`、`/invite/stats`、`/level/info`、`/card/scene-templates`、`/card/personalization`
  - 当前运行时登录响应已返回仓内当前 `LoginRespDTO` 需要的 `registeredAt / realAuthStatus / invitedByUserId / validInviteCount`
  - 当前运行时签发的用户 token payload 已携带仓内 `JwtUtil.generateToken(...)` 约定的 `loginType`
- `2026-04-02 19:26` 已进一步确认资格口径对齐：
  - `GET /api/verify/status` 返回 `status=2`
  - 同一用户 `GET /api/level/info` 已返回 `isCertified=true`
  - `shareCapability.reasonCodes` 与 `/api/card/personalization.capability.reasonCodes` 已不再出现 `verify_required`，当前收敛为 `profile_completion_required / fortune_missing / level_required`
- `2026-04-02 19:41` 已继续补一组“登录成功 -> actor/profile 补齐 -> level/info 升级”的真实样本：
  - 同一手机号 `13800138000` 登录后，`PUT /api/actor/profile`、`GET /api/fortune/report`、`GET /api/level/info`、`GET /api/card/personalization?actorId=10000&scene=general&loadFortune=true` 均返回 `200`
  - 同一用户 `profileCompletion` 已从 `0` 提升到 `95`
  - `shareCapability.reasonCodes` 与 personalization capability 当前已从 `profile_completion_required / fortune_missing / level_required` 收敛为仅剩 `level_required`
- 本轮也已确认上一版资料 / 命理 backfill 失败并不是登录态或后端契约问题，而是远端 `docker exec mysql` 在执行 SQL 文件时缺少 `--default-character-set=utf8mb4`，导致中文 `birth_hour` 被错误解释
- `2026-04-02` 已进一步核对运行时配置与数据库：
  - 服务器 `/opt/kaipai/docker-compose.yml` 明确把后端容器环境固定为 `NACOS_ENABLED=true`、`SPRING_PROFILES_ACTIVE=dev`
  - 容器启动首屏日志显示其订阅的是 `kaipai-backend-dev.yml`，并明确打印 `The following 1 profile is active: "dev"`
  - 同一份启动日志也显示登录链路已在查询 `user` 表并命中 `user_id=10000 / phone=13800138000`
  - MySQL 容器内同时存在 `kaipai` 与 `kaipai_dev`，其中 `kaipai` 当前为空库，而 `kaipai_dev` 才具备 `user / membership_account / referral_record` 等主链表与 `user_id=10000` 样本
- 当前不能确认真实环境下的微信老用户登录、新用户自动注册、`inviteCode` 透传和登录后摘要同步是否全部稳定；但当前主阻塞已经从“外部运行时漂移”切换为“真实微信样本缺失”

## 4. 联调结论

- 当前是否具备三端联调条件：`已命中真实外部入口，登录后主链已恢复`
- 已确认走通的链路：短信验证码发送、手机号登录、真实 token 签发、`user.me`、`verify.status`、`invite.stats`、`level.info`、`card.personalization`
- 当前不能宣告闭环的原因：真实微信配置与样本仍缺；当前已补出“登录成功 -> actor/profile 补齐 -> level/info 升级”的真实样本，但这仍只能证明手机号登录链与登录后摘要同步已恢复，不能替代微信真实链路闭环

## 5. 验收判断

| 闭环条件 | 状态 | 说明 |
|----------|------|------|
| 上位 Spec 已存在并对齐 | 已满足 | `00-28` 已新增登录鉴权与前台会话切片、执行卡和状态卡 |
| 数据模型、接口、状态流转清楚 | 部分满足 | 手机号 / 微信 / 会话恢复主链已清楚，但真实环境微信样本仍未验 |
| 后台或运行治理入口明确 | 已满足 | 本轮明确收口为运行配置台账与联调准入条件，不再隐形处理 |
| 小程序用户侧落点可验证 | 部分满足 | 登录页与会话恢复已落地，但微信真实能力仍缺环境验证 |
| 关键日志、权限、限额或阻塞口径已接入 | 部分满足 | 配置缺失会显式报错，但缺真实环境证据与回填 |
| 文档、映射表、验证记录已回填 | 已满足 | 当前已纳入 `00-28` 治理并回填状态结论 |

## 6. 当前阻塞项

- 缺真实环境 `WECHAT_MINIAPP_APP_ID / WECHAT_MINIAPP_APP_SECRET`
- 缺前端真实环境 `VITE_ENABLE_WECHAT_AUTH=true` 的已验证配置
- 缺至少一组“老用户登录 / 新用户自动注册 + inviteCode”真实样本链路
- 当前 `sendCode` 仍是开发期直返验证码，只能说明接口已接通，不能当成正式短信能力闭环
- 当前 `wechat-login` 虽已命中真实后端，但固定返回 `code=500`、`message=微信登录未配置小程序 appId/appSecret`
- `2026-04-03 04:56` 已继续通过 `00-29` 标准 Nacos 只读诊断样本确认：`kaipai-backend`、`kaipai-backend.yml`、`kaipai-backend-dev.yml` 三个 dataId 也都没有微信 `app-id / app-secret`；当前微信登录阻塞已从“容器没看到变量”进一步收口为“compose 与 Nacos 双侧都缺配置来源”
- `2026-04-03 06:24` 已通过 `00-29` 新增统一门禁样本 `.sce/runbooks/backend-admin-release/records/diagnostics/20260403-062424-invite-wxacode-wechat-config-gate/summary.md` 把 compose 来源、compose 渲染、容器 env 与 Nacos dataId 一次性并表：当前四侧均缺 `WECHAT_MINIAPP_APP_ID / WECHAT_MINIAPP_APP_SECRET`，因此 login-auth 微信链路还不具备进入真实样本验证的运行时门禁条件
- `2026-04-03 06:29` 已通过 `00-29` 本地输入检查样本 `.sce/runbooks/backend-admin-release/records/diagnostics/20260403-062919-invite-login-local-input-gate/summary.md` 进一步确认：当前本地机器没有 `WECHAT_MINIAPP_APP_ID / WECHAT_MINIAPP_APP_SECRET` 输入，只有前端固定 `appid=wxd38339082a9cfa4e`；因此 login-auth 当前也还不能直接进入标准 compose/Nacos 同步，而必须先取得合法 secret 输入来源
- `2026-04-03 06:33` 已通过 `00-29` 微信配置同步总控 dry-run 记录 `.sce/runbooks/backend-admin-release/records/20260403-063339-backend-wechat-config-pipeline-invite-login-wechat-sync.md` 验证：当前总控会在第 1 步 `local-input` 因缺 secret 直接中止，因此 login-auth 的下一步已明确不是“继续尝试远端同步”，而是“先取得合法 secret 输入”
- `2026-04-03` 已继续把 `00-29` 微信输入门禁从“只看有没有值”收口到“拒绝 placeholder / fake secret”：
  - `scripts/read-local-wechat-config-inputs.py` 当前会把 `replace-with-real-app-secret`、`fake-*`、`example` 等值判定为 not ready
  - `scripts/run-backend-compose-env-sync.py` 与 `scripts/run-backend-nacos-config-sync.py` 当前也会直接拒绝把 placeholder / fake secret 写入 compose 或 Nacos
  - `scripts/init-local-wechat-secret-file.py` 已成为新的标准本地入口，用于初始化被 `.gitignore` 排除的 `.sce/config/local-secrets/wechat-miniapp.env`，但不会把 placeholder 文件误判成已具备合法输入
- 当前真实运行时虽已恢复到仓内 DTO / JWT 约定，但仍固定跑在 `SPRING_PROFILES_ACTIVE=dev`
- 当前虽然已补出“登录成功 -> actor/profile 补齐 -> level.info 升级”的真实样本，但该样本仍走手机号验证码，不代表微信链路已闭环
- 当前本地 `run-login-auth-validation.ps1` 已实际扫出阻塞：`kaipai-frontend/.env` 中 `VITE_ENABLE_WECHAT_AUTH=false`，因此当前环境不能验证真实微信链路

## 7. 下一轮最小动作

1. 继续保留 `NACOS_ENABLED=true + SPRING_PROFILES_ACTIVE=dev` 组合，并把本轮“登录成功 -> actor/profile 完成度提升 -> level/info 变化”的真实样本补回登录样本台账
2. 先以 `python .sce/runbooks/backend-admin-release/scripts/run-backend-wechat-config-sync-pipeline.py --label <label> [--dry-run]` 固定“本地输入 + 远端门禁 + 同步顺序”的总控结论，避免前端继续把当前环境当成可验证微信链路
3. 在拿到合法 `appSecret` 输入并通过同一总控补齐后端 compose 与 Nacos 的微信配置来源后，再跑真实环境微信老用户登录和新用户自动注册，并验证 `inviteCode` 透传
4. 把本轮 `remote-smoke-after-port-fix` 与 `remote-smoke-after-capability-fix` 两组样本证据补回同一份登录样本台账
5. 若本机仍缺 gitignored secret 文件，先执行 `python .sce/runbooks/backend-admin-release/scripts/init-local-wechat-secret-file.py` 建立本地输入位，再由人工填入真实 secret；不得再用 fake secret dry-run 代替合法输入

## 8. 回填记录

### 2026-04-02

- 当前判定：`局部完成`
- 备注：`kaipaile-server` 已补 `POST /auth/wechat-login` 与 `wechat.miniapp.app-id / app-secret` 配置位，`kaipai-frontend` 也已将微信登录入口切到真实后端契约并受显式运行时开关控制；本轮继续移除真实环境 `mock-code` 回退，并把这段能力正式纳入 `00-28` 治理。当前仍缺真实环境配置和联调证据，因此状态保持 `局部完成`

### 2026-04-02（二次回填）

- 当前判定：`局部完成`
- 备注：`kaipai-frontend` 的 `src/utils/runtime.ts` 已停止错误移除 `:8080` 端口，并新增运行时阻塞显式提示：当缺少 `VITE_API_BASE_URL` 导致自动回退 mock，或 `VITE_USE_MOCK=false` 但缺少 base URL 时，会在 `App` 启动阶段直接提示“当前环境不可作为真实联调依据”；同时仓内已补 `kaipai-frontend/.env.example` 作为最小真实环境示例。本轮目标是先阻止“静默假联通”，当前仍缺真实环境配置和样本验证，因此状态继续保持 `局部完成`

### 2026-04-02（三次回填）

- 当前判定：`局部完成`
- 备注：`execution/login-auth` 已补齐 `real-env-runtime-inventory.md`、`real-env-validation-checklist.md`、`real-env-evidence-pack.md`、`validation-sample-ledger-template.md` 与 `collect/new/run-login-auth-validation.ps1`。本轮已实际执行 `run-login-auth-validation.ps1 -EnvironmentName dev -SampleLabel local-smoke`，成功生成样本目录、`capture-results.json`、`runtime-summary.md`、`validation-report.md`，并明确扫出当前本地阻塞为 `VITE_ENABLE_WECHAT_AUTH=false`，因此此环境暂不能验证真实微信链路。当前治理已从“缺工具”推进到“可重复采证”，但真实微信配置与样本联调仍未完成。

### 2026-04-02（四次回填）

- 当前判定：`局部完成`
- 备注：已直接探测当前小程序 `.env` 指向的 `http://101.43.57.62`，根路径和 `/api/user/me`、`/api/level/info` 均返回 `403`，`http://101.43.57.62:8010/api/level/info` 返回 `502`，`https://101.43.57.62/api/level/info` 超时。该结果说明当前 `.env` 指向值并不能直接证明“已命中真实后端联调入口”，反而更像反代 / WAF / 错误入口阻塞。因此 login-auth 下一步优先级应收口为“确认真实外部访问入口或代理策略”，而不是继续拿这套地址做样本联调。

### 2026-04-02（五次回填）

- 当前判定：`局部完成`
- 备注：已进一步确认 `http://101.43.57.62/api` 的确能命中外部后端：`/api/v3/api-docs` 返回 `200`，`/api/auth/sendCode` 返回开发态验证码，`/api/auth/login` 可用手机号 `13800138000` 登录并签发 `userId=10000` token。但同一 token 下 `/api/user/me`、`/api/verify/status`、`/api/invite/stats`、`/api/level/info`、`/api/card/*` 全部统一返回 `500`。同时只读核对数据库后发现：Nacos `prod` 指向的 `kaipai` 库连基础 `user` 表都不存在，而 `kaipai_dev` 才具备当前主链核心表和 `user_id=10000` 样本。这说明当前主阻塞已经从“入口未确认”切换为“运行时 jar / profile / 数据库链路漂移”，下一步必须优先做整组运行时核对，而不是继续拿外部地址做业务样本联调。

### 2026-04-02（六次回填）

- 当前判定：`局部完成`
- 备注：已直接登录目标服务器核对运行时：`/opt/kaipai/docker-compose.yml` 把后端容器固定为 `NACOS_ENABLED=true`、`SPRING_PROFILES_ACTIVE=dev`；启动日志也明确订阅 `kaipai-backend-dev.yml` 并激活 `dev` profile。更关键的是，宿主机当前运行 jar 扫描只看到 `AuthController / UserController / JwtUtil / UserServiceImpl` 等旧链路类，未看到仓内当前主链需要的 `CardController / LevelController / ActorPersonalizationServiceImpl / MembershipAccountServiceImpl`。同一时间窗日志已把 `/api/user/me`、`/api/verify/status`、`/api/invite/stats`、`/api/level/info`、`/api/card/*` 全部记成 `NoResourceFoundException`。因此当前结论已经从“运行时漂移”进一步收口为“线上实际跑的是 `dev + Nacos + 旧能力集合`”，下一步优先级应切到重新发版当前仓后端 jar，而不是继续拿旧运行时做登录样本联调。

### 2026-04-02（七次回填）

- 当前判定：`局部完成`
- 备注：已重新打包并替换目标环境后端 jar，远端 `/opt/kaipai/kaipai-backend-1.0.0-SNAPSHOT.jar` SHA256 已变更为 `44d372ae416f06381c94ec797255ed9eacffa8d70d97ffb68f28334849f7969a`。复测结果显示 `GET /api/v3/api-docs`、`POST /api/auth/sendCode`、`POST /api/auth/login`、`GET /api/user/me`、`GET /api/verify/status`、`GET /api/invite/stats`、`GET /api/level/info`、`GET /api/card/personalization` 全部返回 `200`，运行时旧 jar 阻塞已解除。当前真实阻塞已收口为“微信真实样本仍缺”和“当前 smoke 用户资料完备度不足”。

### 2026-04-02（八次回填）

- 当前判定：`局部完成`
- 备注：已继续修正资格口径：`verify-status` 返回 `status=2` 的同一用户，`level-info.isCertified` 已对齐为 `true`，`/api/level/info.shareCapability.reasonCodes` 与 `/api/card/personalization.capability.reasonCodes` 也都已从错误的 `verify_required` 改为 `profile_completion_required / fortune_missing / level_required`。这说明当前主阻塞不再是认证状态分叉，而是 `actor_profile` 缺失导致的真实资料完备度不足。

### 2026-04-02（九次回填）

- 当前判定：`局部完成`
- 备注：已按 `execution/login-auth/samples/20260402-193327-dev-profile-fortune-backfill` 重跑“登录成功 -> actor/profile 补齐 -> level/info 升级”的真实样本：同一手机号登录后，`PUT /api/actor/profile`、`GET /api/fortune/report`、`GET /api/level/info`、`GET /api/card/personalization?actorId=10000&scene=general&loadFortune=true` 全部返回 `200`，`profileCompletion` 已提升为 `95`，`reasonCodes` 已收敛为仅剩 `level_required`。本轮也同步确认上一版 backfill 失败根因是远端 `mysql` CLI 缺少 `--default-character-set=utf8mb4`，而不是登录态或后端 DTO 漂移。

### 2026-04-03

- 当前判定：`局部完成`
- 备注：
  - 当日早些时候真实环境一度再次出现 `POST /api/admin/auth/login -> 500`，因此没有直接沿用 `2026-04-02` 的联通结论，而是先按 `00-29` 新增的 `backend-only` 标准脚本链路重发后端
  - `2026-04-03 01:35` 已通过发布记录 `20260403-013415-backend-only-auth-runtime-check-final.md` 完成一次真实 `backend-only` 标准发布：本地 `JDK 17 + Maven` 构建 jar，经 `scp + sudo helper + docker compose build/up` 落到目标环境
  - 同批公网 smoke 已再次确认：
    - `GET http://101.43.57.62/api/v3/api-docs` -> `200`
    - `POST http://101.43.57.62/api/admin/auth/login` -> `200`
  - 这说明今天的登录/鉴权主阻塞已经从“后端运行时 500”重新收口回“微信真实样本缺失”和“当前后台/演员端其他接口仍需带 token 补样本”，不再是后端基础链路失活

### 2026-04-03（二次回填）

- 当前判定：`局部完成`
- 备注：
  - `execution/login-auth/run-login-auth-validation.ps1` 与 `collect-login-auth-evidence.ps1` 已补成“本地配置扫描 + 可选真实接口预探测”，当前可直接用 `-EnableLiveProbe` 把 `sendCode / wechat-login` 的真实返回固化进样本目录
  - 已实际执行样本 `execution/login-auth/samples/20260403-024908-dev-live-probe-ok3`
  - 当前样本已固化的关键事实：
    - 小程序 `.env` 仍是 `VITE_API_BASE_URL=http://101.43.57.62`、`VITE_USE_MOCK=false`、`VITE_ENABLE_WECHAT_AUTH=false`
    - `POST /api/auth/sendCode` -> transport `200` / payload `code=200`
    - `POST /api/auth/wechat-login` -> transport `200` / payload `code=500` / `message=微信登录未配置小程序 appId/appSecret`
  - 因此当前 login-auth 剩余阻塞已经明确收口为“前端显式关闭微信入口 + 远端缺微信小程序配置 + 缺真实微信样本”，而不是“仍在走 mock”或“接口未发布”

### 2026-04-03（三次回填）

- 当前判定：`局部完成`
- 备注：
  - `kaipai-frontend/src/utils/runtime.ts` 已继续把 mock 进入条件收口为“仅 `VITE_USE_MOCK=true` 时才允许演示态”，不再因为缺少 `VITE_API_BASE_URL` 自动退回 mock
  - `kaipai-frontend/src/utils/request.ts` 也已新增请求级运行时门禁：当前若缺少 `VITE_API_BASE_URL`，会直接拒绝真实请求并返回显式 blocker，而不是继续发错误相对路径或偷偷走 mock
  - 因此 login-auth 当前关于运行时的结构风险，已从“可能静默假联通”收口为“显式阻塞 + 显式 mock 两种可判定状态”；剩余 blocker 继续集中在微信真实配置和真实样本

### 2026-04-03（四次回填）

- 当前判定：`局部完成`
- 备注：
  - `00-29` 微信配置链路已继续补强为“合法输入门禁 + 本地输入位初始化”而不是只看文件是否存在：`scripts/read-local-wechat-config-inputs.py` 当前会拒绝 placeholder / fake secret，`scripts/run-backend-compose-env-sync.py` 与 `scripts/run-backend-nacos-config-sync.py` 也不会再把这类值写入远端
  - `scripts/init-local-wechat-secret-file.py` 已新增为标准本地入口，可初始化被 `.gitignore` 排除的 `.sce/config/local-secrets/wechat-miniapp.env` 并自动预填当前小程序 `appId`
  - 因此 login-auth 当前微信门禁已从“缺值”进一步收口为“缺合法 secret 来源”；下一步不再是反复 dry-run，而是取得真实 secret 后直接按总控脚本推进

### 2026-04-03（五次回填）

- 当前判定：`局部完成`
- 备注：
  - `execution/login-auth/collect-login-auth-evidence.ps1` 已继续补成和 `00-29` 单页 runbook 一致的门禁口径：当前采证会同时区分“后端源码是否暴露配置位”“本地 secret 文件是否存在”“本地 `WECHAT_MINIAPP_APP_SECRET` 是否通过合法输入门禁”
  - 已实际执行样本 `execution/login-auth/samples/20260403-122932-dev-legal-secret-gate-aligned`
  - 当前样本已继续固定三类 blocker：
    - 前端 `VITE_ENABLE_WECHAT_AUTH=false`
    - 本地 `.sce/config/local-secrets/wechat-miniapp.env` 中 `WECHAT_MINIAPP_APP_SECRET` 仍不是合法输入
    - 远端 `POST /api/auth/wechat-login` 仍返回 `微信登录未配置小程序 appId/appSecret`
  - 这说明 login-auth 当前微信主线的下一步不应再是“继续补 live probe”或“再做一轮 dry-run”，而是先拿到合法 secret，再按 `wechat-config-gate-runbook.md -> backend-only -> precheck -> real sample` 固定顺序推进
