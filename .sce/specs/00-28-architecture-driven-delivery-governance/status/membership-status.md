# 会员能力与模板配置闭环状态回填

## 1. 归属切片

- `../slices/membership-template-capability-slice.md`
- `../execution/membership/README.md`

## 2. 当前判定

- 回填日期：`2026-04-02`
- 当前判定：`局部完成`
- 一句话结论：后台会员与模板治理能力相对完整，演员端已补齐 `/level/info` 能力摘要、`/card/*`、`/card/personalization`、`/fortune/*`、`/ai/*`、`/actor/profile/*` 与 `/actor/{id}` 最小输出，小程序运行时也已放开 `verify / invite / level / card / ai / fortune / actor` 真接口分支；当前 `Lv5` fortune theme 解锁样本、五页前台截图、`/card/config` 首保存回归、模板 rollback/restore 链路、后台截图、preview overlay 静态审计以及“关闭 fortune theme 后的 rollback 哈希样本”都已补齐，且最新 no-fortune 样本已证明 `actor-card / detail / invite` 三页都会随 rollback 改变并在 restore 后恢复。当前主风险已进一步收口为“preview overlay 已按 `00-49 membership-preview-overlay-fact-source-boundary` 固定为当前设备 session-only 预览态，但仍不是后端事实源”和“当前真实验证仍固定在 dev + Nacos 运行时”。

## 3. 当前已确认事实

### 3.1 前端 / 小程序

- `kaipai-frontend/src/pkg-card/membership/index.vue`、`src/pkg-card/actor-card/index.vue`、`src/pages/actor-profile/detail.vue` 已具备会员说明、模板消费和分享产物展示
- `kaipai-frontend/src/api/level.ts` 已消费 `/api/level/info`、`/api/card/scene-templates`、`/api/card/config`、`/api/ai/*`
- `kaipai-frontend/src/api/actor.ts` 当前已显式区分自我档案与公开详情：自我场景统一消费 `/api/actor/profile/mine`，公开详情统一消费 `/api/actor/{userId}`；`/api/actor/profile/{userId}` 当前仅保留给后端自校验兼容路径
- `kaipai-frontend/src/api/fortune.ts` 已消费 `/api/fortune/report`、`/api/fortune/apply-lucky-color`
- `kaipai-frontend/src/utils/runtime.ts` 已放开 `verify / invite / level / card / ai / fortune / actor` 真接口能力
- `kaipai-frontend/src/stores/user.ts`、`src/pkg-card/membership/index.vue`、`src/pkg-card/invite/index.vue`、`src/pkg-card/fortune/index.vue`、`src/pkg-card/actor-card/index.vue`、`src/pages/actor-profile/detail.vue` 已开始消费后端等级 / 会员能力摘要，不再继续硬编码公开演员为 `Lv5/member`
- `kaipai-frontend/src/api/personalization.ts`、`src/utils/personalization.ts` 已开始优先消费 `/api/card/personalization`，把主题 / 能力 gating / 分享产物从“页面内多点拼装”收口到后端汇总口径
- `kaipai-frontend/src/pkg-card/actor-card/index.vue` 已改成以 `/card/personalization` 返回的模板、能力、主题和分享产物为基线，只把未保存的布局 / 配色改动保留成本地 preview overlay
- `kaipai-frontend/src/pages/actor-profile/detail.vue` 已改成优先使用 `/card/personalization` 返回的 `publicCardPage / miniProgramCard` path 作为公开页分享态和名片入口，不再只依赖页面本地 query 组装
- `kaipai-frontend/src/pkg-card/fortune/index.vue` 已开始直接消费 personalization 模板名恢复场景文案，`src/pkg-card/membership/index.vue` 已按 `artifact.locked` 计算当前可见产物，不再把全部产物误当成已解锁
- `kaipai-frontend/src/pkg-card/invite/index.vue` 已开始恢复 `actor-card` 下发的 `scene / artifact / themeId / tone` 上下文，并在邀请页内随产物切换同步 share state，不再只在首次刷新时写一份固定邀请分享态
- `kaipai-frontend/src/utils/share-artifact.ts` 已继续收口 artifact path patch 规则，`src/pkg-card/actor-card/index.vue` 不再单独维护 `publicCardPage / inviteCard / poster` 三套路径拼装分支
- `kaipai-frontend/src/pkg-card/actor-card/index.vue`、`src/api/level.ts` 已让“保存当前场景配置”同时提交 `preferredArtifact / preferredTone / enableFortuneTheme`，不再只把分享偏好停留在前端临时态
- `kaipai-frontend/src/utils/personalization.ts` 已新增显式 preview overlay helper，`src/pkg-card/actor-card/index.vue` 与 `src/pages/actor-profile/detail.vue` 已可恢复同一份未保存布局 / 配色预览，不再继续在页面里散写 overlay query 读写；当前页面运行时也已不再兼容读取 overlay query，四个旧 query key 也已从前端运行时代码删除
- `kaipai-frontend/src/utils/personalization.ts` 已继续补齐 `read/writePersonalizationPreviewOverlaySession`，并把 overlay 主恢复路径从“跨页 query patch”收口为“当前设备 session”；`src/pkg-card/actor-card/index.vue` 会按 `actorId + scene` 写入/清理 session，`src/pages/actor-profile/detail.vue` 与 `src/pkg-card/invite/index.vue` 已开始优先读取同一份 session 预览，且 overlay path patch helper 已退场
- `execution/membership/preview-overlay-governance-baseline.md` 已明确把 preview overlay 固定为“允许暂留的前端显式编辑态”，并写清允许边界、禁止事项与升级为后端 / session 模型的触发条件；`execution/membership/preview-overlay-decision-record.md` 则进一步固定当前为何继续保持 session-only
- `execution/membership/run-preview-overlay-static-audit.py` 已把 preview overlay 的结构约束转成标准静态审计入口，可重复检查 query key、session key 与 helper 触点是否仍停留在白名单
- 小程序当前尚未完全消除 `theme-resolver / share-artifact` 等本地兜底逻辑，但分享恢复主链已开始收口；剩余本地逻辑主要集中在当前设备 session 级 preview overlay，以及 invite/login 等切片的真实环境阻塞
- `kaipai-frontend/src/utils/personalization.ts`、`src/utils/theme-resolver.ts`、`src/utils/share-artifact.ts` 仍保留主题 token 和分享产物组装逻辑，但核心 gating 与页面基线已允许由后端摘要覆盖

### 3.2 后端 / 数据

- `kaipaile-server/src/main/java/com/kaipai/module/controller/admin/membership/AdminMembershipController.java` 已具备会员产品、账户、日志等后台接口
- `kaipaile-server/src/main/java/com/kaipai/module/controller/admin/content/AdminContentController.java` 已具备模板、发布、回滚、主题 token、分享产物等后台接口
- `kaipaile-server/src/main/java/com/kaipai/module/controller/level/LevelController.java` 已提供包含等级能力 / 分享能力摘要的 `/level/info`
- `kaipaile-server/src/main/java/com/kaipai/module/controller/card/CardController.java` 已提供 `/card/scene-templates`、`/card/config`、`/card/personalization` 查询接口与配置保存接口
- `kaipaile-server/src/main/java/com/kaipai/module/server/card/service/ActorPersonalizationService.java`、`impl/ActorPersonalizationServiceImpl.java` 已补齐模板、能力摘要、命理摘要、主题 token 与分享产物的统一汇总输出
- `kaipaile-server/src/main/java/com/kaipai/module/server/card/service/impl/ActorPersonalizationServiceImpl.java` 已把 `inviteCard` 产物 path 从裸 `/pkg-card/invite/index` 收口为带 `actorId / scene / artifact / themeId / tone / shared` 的统一上下文路径
- `kaipaile-server/src/main/java/com/kaipai/module/server/card/service/impl/ActorCardConfigServiceImpl.java` 已让 `/card/config` 保存时同步回写 `ActorSharePreference`，把 `preferredArtifact / preferredTone / enableFortuneTheme` 纳入同一条保存链
- `kaipaile-server/src/main/java/com/kaipai/module/controller/fortune/FortuneController.java` 已提供 `/fortune/report`、`/fortune/apply-lucky-color`
- `kaipaile-server/src/main/java/com/kaipai/module/controller/ai/AiController.java` 已提供 `/ai/quota`、`/ai/polish-resume`
- `kaipaile-server/src/main/java/com/kaipai/module/controller/card/CardController.java` 已补齐 `/card/personalization` 聚合接口
- `kaipaile-server/src/main/java/com/kaipai/module/controller/actor/ActorProfileController.java`、`ActorController.java` 已补齐 `/actor/profile/mine`、`/actor/profile/{userId}`、`PUT /actor/profile`、`/actor/{userId}`、`/actor/search`
- `kaipaile-server/src/main/java/com/kaipai/module/server/membership/service/MembershipAccountService.java`、`impl/MembershipAccountServiceImpl.java` 已补齐演员端等级信息、等级能力与分享能力摘要输出
- `kaipaile-server/src/main/java/com/kaipai/module/server/actor/service/ActorProfileService.java`、`impl/ActorProfileServiceImpl.java` 已补齐 actor 档案 DTO 映射、经历恢复、扩展字段读写与搜索最小实现
- `kaipaile-server/src/main/java/com/kaipai/module/server/card/service/CardSceneTemplateService.java`、`ActorCardConfigService.java` 及其实现类已补齐模板列表、默认配置、配置保存的最小 actor 输出
- `kaipaile-server/src/main/java/com/kaipai/module/server/fortune/service/FortuneReportService.java`、`impl/FortuneReportServiceImpl.java` 已补齐当前用户命理报告读取与幸运色应用最小实现
- `kaipaile-server/src/main/java/com/kaipai/module/server/ai/service/AiQuotaService.java`、`impl/AiQuotaServiceImpl.java` 已补齐月度 AI 配额查询与消费最小实现
- `kaipaile-server/src/main/java/com/kaipai/module/server/card/service/ActorPersonalizationService.java`、`impl/ActorPersonalizationServiceImpl.java` 已补齐模板 / fortune / theme / artifact 聚合最小实现
- `2026-04-02` 已在 `JDK 21` 环境下执行 `mvn -q -DskipTests compile` 通过

### 3.3 后台治理

- 后台已具备会员产品 / 账户治理和模板发布 / 回滚治理入口
- 服务层已接入多类后台操作日志，具备后台自证和审计基础

### 3.4 联调现状

- 当前能确认“后台治理链路”、“演员端最小输出链路”、“AI / Fortune 最小权威接口”、“个性化汇总接口”和“小程序真接口开关”五段能力都已具备，`actor-card` 与 `actor-profile detail` 的分享恢复主链也已开始直接消费后端 artifact path
- `2026-04-02` 已补齐 `execution/membership` 的真实环境运行时清单、验证清单、证据包、样本台账模板与 PowerShell 采证脚本，并已实际执行 `run-membership-validation.ps1` 生成样本目录与报告
- `2026-04-02 19:19` 已确认当前外部后端入口 `http://101.43.57.62/api` 可达：
  - `GET /api/v3/api-docs` -> `200`
  - `POST /api/auth/sendCode` -> `200`
  - `POST /api/auth/login` -> `200`，可获得 `userId=10000` 真实 token
- `2026-04-02 19:19` 已确认匿名访问 `GET /api/card/scene-templates`、`GET /api/card/personalization?actorId=10000&scene=default` 均返回 `200`，说明 `card` 公开链路和安全白名单已在真实运行时生效
- `2026-04-02 19:23` 已完成当前仓后端 jar 替换并重建容器，远端 `/opt/kaipai/kaipai-backend-1.0.0-SNAPSHOT.jar` SHA256 已变更为 `44d372ae416f06381c94ec797255ed9eacffa8d70d97ffb68f28334849f7969a`
- `2026-04-02 19:25` 已再次复测 membership 主链：
  - 同一登录态下 `GET /api/user/me`、`GET /api/verify/status`、`GET /api/invite/stats`、`GET /api/level/info`、`GET /api/card/personalization?actorId=10000&scene=default` 全部返回 `200`
  - `/api/card/personalization` 已真实返回模板、主题、分享产物、`sharePreferences` 与 capability 摘要；当前样本命中 `Smoke Template`
  - `verify-status=2` 的同一用户，`level-info.isCertified` 已对齐为 `true`，`reasonCodes` 当前收敛为 `profile_completion_required / fortune_missing / level_required`
- `2026-04-02 19:41` 已按 `profile-fortune-backfill` 样本补齐同一用户的演员资料与命理样本：
  - 远端 `kaipai_dev.actor_profile` 已存在 `user_id=10000 / birth_hour=午时 / is_certified=1`
  - 远端 `kaipai_dev.fortune_report` 已存在 `report_month=2026-04-01 / lucky_color=#FF6B35 / lucky_color_name=落日橘 / birth_hour=午时`
  - `GET /api/fortune/report`、`GET /api/level/info`、`GET /api/card/personalization?actorId=10000&scene=general&loadFortune=true` 全部返回 `200`
  - 同一用户 `profileCompletion=95`，`/api/level/info.shareCapability.reasonCodes` 与 personalization capability 当前已收敛为仅剩 `level_required`
- `2026-04-02 19:52` 已按 `execution/membership/samples/20260402-195202-dev-admin-membership-template-chain` 跑通真实 admin 会员 / 模板联动样本：
  - 后台 `close` 会员后，同一用户 `membershipTier` 从 `member -> none`，`reasonCodes` 变为 `member_required, level_required`
  - 后台 `open` 会员后，同一用户 `membershipTier` 从 `none -> member`，`reasonCodes` 回到仅剩 `level_required`
  - 后台主题更新并发布后，`/api/card/personalization` 返回的主题主色从 `#2F6B5F -> #7A3E2B`，最新发布记录为 `publishLogId=3 / publishVersion=SMOKE_V2_ADMIN_20260402_195744`
  - 同一样本的 DB 采证已清理干净：`membership_account`、`membership_change_log`、`card_scene_template`、`template_publish_log` 与 `admin_operation_log.operation_log_id` 已全部可回读，不再带 `Unknown column 'log_id'` 报错
- 本轮也已确认上一版 backfill 失败的根因不是表结构错误，而是远端 `docker exec mysql` 在执行 SQL 文件时缺少 `--default-character-set=utf8mb4`，导致中文 `birth_hour` 通过重定向写入时报 `Data too long for column 'birth_hour'`
- `2026-04-02` 已进一步核对数据库与运行时配置：
  - 服务器 `/opt/kaipai/docker-compose.yml` 明确把后端容器环境固定为 `NACOS_ENABLED=true`、`SPRING_PROFILES_ACTIVE=dev`
  - 容器启动日志显示其订阅 `kaipai-backend-dev.yml` 并激活 `dev` profile
  - MySQL 容器内同时存在 `kaipai` 与 `kaipai_dev`；其中 `kaipai` 当前为空库，而 `kaipai_dev` 才具备 `user / membership_account / invite_code / referral_record / actor_card_config / identity_verification` 等核心表与 `user_id=10000` 样本
- `2026-04-02 21:09` 已通过 `automator + ws://127.0.0.1:9421` 为同一样本建立真实前台会话，并补齐 `membership / actor-card / detail / invite / fortune` 五页截图；截图路径与实际路由回读均已对齐 `captures/mini-program-screenshot-capture.json`
- `2026-04-02 21:36` 已按 `execution/membership/samples/20260402-212713-dev-fortune-theme-lv5-unlock` 跑通高等级解锁样本：
  - `user_id=10000` 当前有效邀请数已从 `1 -> 8`，`/api/level/info.level=5`，`shareCapability.reasonCodes=[]`
  - `/api/card/personalization?actorId=10000&scene=general&loadFortune=true` 当前返回 `themeId=general-member-fortune / primary=#FF6B35 / enableFortuneTheme=true`
  - 同一样本已再次补齐 `membership / actor-card / detail / invite / fortune` 五页截图，且 `actor-card / detail / invite` 路由都已切到 `themeId=general-member-fortune`
  - 本轮也新增暴露了运行时首存缺口：当 `actor_card_config` 不存在时，`POST /api/card/config` 会因 `Field 'template_id' doesn't have a default value` 返回 `500`；样本 `captures/card-config-first-save-failure.txt` 已保留此证据
  - 当前源码已在 `ActorCardConfigServiceImpl` 中补上 `templateId` 赋值链，后续已继续进入运行时回归验证
- `2026-04-02 21:57` 已通过 plain `docker` 重建当前 dev 运行时：
  - `captures/remote-redeploy-plain-docker.json` 已保留 `docker build / docker rm -f / docker run` 全链路输出
  - 容器 `/app/app.jar` SHA256 已对齐 `88d23af6cb2934097e2dc0e149537c0e96f18951e6bddc0ad82455a94fdea641`
  - 当前容器环境仍保持 `NACOS_ENABLED=true / SPRING_PROFILES_ACTIVE=dev / SERVER_PORT=8080`
- `2026-04-02 21:59` 已按 `verify-card-config-first-save.py` 补齐首保存回归样本：
  - 先删除 `kaipai_dev.actor_card_config / actor_share_preference` 中 `user_id=10000 / scene=general` 的样本行
  - 同一登录态下再次执行 `POST /api/card/config` 返回 `200`，`response.code=200`
  - DB 回读已确认 `actor_card_config.template_id=1`、`actor_share_preference.enable_fortune_theme=1`
  - `GET /api/card/personalization?actorId=10000&scene=general&loadFortune=true` 继续返回 `themeId=general-member-fortune / primary=#FF6B35`
- `2026-04-02 22:15` 已按 `run-admin-template-rollback-chain.py` 补齐模板回滚到前台的恢复链路：
  - rollback 前：`/api/card/scene-templates` 命中 `Smoke Template / #7A3E2B`
  - rollback 后：模板状态变为 `2`，`/api/card/scene-templates` 回到 builtin `通用 / #ff7a45`，`/api/card/personalization.profile.template.name=通用`
  - restore publish 后：模板状态恢复 `1`，`/api/card/scene-templates` 与 `/api/card/personalization` 又切回 `Smoke Template / #7A3E2B`
  - `template_publish_log` 与 `admin_operation_log` 已回读到 `rollback + publish` 连续记录
- `2026-04-02 22:16` 已按 `capture-admin-membership-template-screenshots.py` 补齐同一份 `Lv5` 样本的后台页面证据：
  - `screenshots/admin-membership-accounts.png`
  - `screenshots/admin-content-templates.png`
  - `screenshots/admin-content-templates-rollback-dialog.png`
  - `captures/admin-screenshot-capture.json` 已保留本地 `kaipai-admin` + `127.0.0.1:8010` 代理的截图上下文
- `2026-04-02 22:30` 已按 `run-admin-template-rollback-mini-program-chain.py` 补齐同一份 `Lv5` 样本的 rollback 前台阶段截图：
  - `actor-card` 在 rollback 后从 `Smoke Template` 切到 `通用`，restore 后恢复
  - `detail / invite` 三段截图的 query 与截图哈希保持一致，仍统一落在 `general-member-fortune` 路由与主题层
  - 这说明当前 `Lv5 + enableFortuneTheme=1` 样本里，公开页与邀请页的模板视觉回滚会被 fortune 主题层覆盖
- `2026-04-03 11:16` 已按 `execution/membership/run-preview-overlay-static-audit.py` 产出首份样本 `execution/membership/samples/20260403-111647-preview-overlay-static-audit/summary.md`
- 同一样本当前静态审计结果为：
  - `previewLayout / previewPrimary / previewAccent / previewBackground` 四个 query key 仍只存在于 `src/utils/personalization.ts`
  - `kp:personalization-preview-overlay-session` 当前仍只存在于 `src/utils/personalization.ts`
  - `PersonalizationPreviewOverlay` 与相关 helper 当前只命中：
    - `src/utils/personalization.ts`
    - `src/types/personalization.ts`
    - `src/pkg-card/actor-card/index.vue`
    - `src/pages/actor-profile/detail.vue`
    - `src/pkg-card/invite/index.vue`
  - 当前 `findingCount=0`，说明 overlay 结构边界没有再次扩散到其它页面
- `2026-04-03 11:26` 已按 `execution/membership/run-admin-template-rollback-mini-program-no-fortune-theme.py` 产出首份样本 `execution/membership/samples/20260403-112652-dev-template-rollback-no-fortune-theme/summary.md`
- 该样本先证明了两件事：
  - 三段 `detail / invite` 路由已都固定在 `themeId=general-member-base`，说明已成功排除 `general-member-fortune` 路由遮罩
  - 但当时 `actor-card` 哈希会变化，`detail / invite` 三段哈希仍保持一致，因此 blocker 被继续收口到“页面首屏仍未显式消费模板差异”
- `2026-04-03 12:03` 已在前端补齐 `detail / invite` 的模板 / artifact 首屏文案消费，并重新执行 `kaipai-frontend npm run type-check`、`npm run build:mp-weixin` 后，先产出样本 `execution/membership/samples/20260403-120307-dev-template-rollback-no-fortune-theme/summary.md`
- 最新样本当前已用截图 SHA256 + 分阶段 `page-data` 固化 rollback 前后页面差异：
  - `actor-card` 哈希：`AB50A24F... -> 19C8615D... -> AB50A24F...`
  - `actor-profile-detail` 哈希：`97E4C31E... -> CCC4BB27... -> 97E4C31E...`
  - `invite-card` 哈希：`213439AE... -> 4D126C62... -> 213439AE...`
  - `detail` 页 `page-data.f` 已从 `Smoke Template公开名片页 · ...` 切换到 `通用公开名片页 · ...`
  - `invite` 页首屏截图已从 `Smoke Template风格邀请卡` 切换到 `通用风格邀请卡`
- 同一轮也已把 membership 小程序采证脚本补到与 recruit 一致的 page-data 粒度：
  - `capture-mini-program-screenshots.js` 现会为 `before / after-rollback / after-restore` 三段分别保留 `page-data-*.json`
  - 最新样本已包含 `before-rollback-page-data-actor-profile-detail.json`、`after-rollback-page-data-actor-profile-detail.json`、`before-rollback-page-data-invite-card.json`、`after-rollback-page-data-invite-card.json` 等阶段数据

## 4. 联调结论

- 当前是否具备三端联调条件：`代码侧与外部运行时主链已接通`
- 已确认走通的链路：后台治理能力、演员端 `/level/info` 能力摘要、`/card/*`、`/card/personalization`、`/fortune/*`、`/ai/*`、`/actor/profile/*`、`/actor/{id}` 输出、配置保存链路、小程序 `verify / invite / level / card / ai / fortune / actor` 真接口开关，以及真实外部 `user / verify / invite / level / card` 主链访问
- 当前不能宣告闭环的原因：当前 `Lv5` fortune theme 解锁样本、admin 会员 / 模板样本、API 返回、数据库证据、小程序截图、`/card/config` 首保存回归、模板 rollback/restore、后台截图、overlay 静态审计以及 no-fortune rollback 哈希样本都已具备；`actor-card / detail / invite` 的模板回滚可见性也已通过最新样本闭环，但 `preview overlay` 当前虽已明确继续保留为当前设备 session-only 预览态，仍不是后端事实源，因此还不能宣告完全闭环

## 5. 验收判断

| 闭环条件 | 状态 | 说明 |
|----------|------|------|
| 上位 Spec 已存在并对齐 | 已满足 | `00-28` 已完成会员与模板切片及执行卡 |
| 数据模型、接口、状态流转清楚 | 部分满足 | 演员端 `actor/level/card/fortune/ai` 最小契约已落地，但模板态与 AI patch 流转仍待继续收口 |
| 后台治理入口可操作 | 已满足 | 会员产品、账户、模板、发布、回滚入口均已存在 |
| 小程序或前台用户侧落点可验证 | 部分满足 | 前台页面存在，且 `verify / invite / level / card / actor` 已可走真实分支，但还未完成整页真实联调与能力判断收口 |
| 关键日志、权限、限额或回滚约束已接入 | 部分满足 | 后台日志和发布 / 回滚具备，演员端 AI 配额与等级 / 会员 gating 已开始权威化，但真实回滚与联调仍待继续收口 |
| 文档、映射表、验证记录已回填 | 已满足 | 当前已建立会员与模板切片状态基线 |

## 6. 当前阻塞项

- `actor-card` 虽已优先使用后端 artifact path，未保存 preview overlay 也已从 query patch 收口到当前设备 session 恢复，但该 overlay 仍是前端显式预览模型；`invite/login` 分享链路则已继续收口，仍待真实环境确认
- preview overlay 虽已被治理基线明确成“允许暂留的当前设备 session 显式态”，但它仍不是后端事实源；是否进一步迁入后端仍取决于真实环境样本结果
- AI 配额虽已具备最小真接口，但仍缺编辑页 patch 流程和更完整的失败 / 回滚约束
- 当前真实运行时虽已恢复，但仍固定跑在 `dev + Nacos`
- `2026-04-02 20:23` 到 `20:49` 的 DevTools 未授权阻塞已完整保留在样本 `captures/devtools-auth-blocker.txt`，但它已不再是当前阻塞：`2026-04-02 20:53` `cli auto --project ... --auto-port 9421` 已恢复，`2026-04-02 21:09` 已完成 automator 截图采证

## 7. 下一轮最小动作

1. 按 `00-49 membership-preview-overlay-fact-source-boundary` 继续维护 preview overlay 的事实源边界；没有跨登录 / 跨设备 / 高阶事实字段新证据前，不再直接推进后端化
   继续动 overlay 前，先重跑 `run-preview-overlay-static-audit.py`
2. 以 `20260403-121415-dev-template-rollback-no-fortune-theme` 为新的 page-level 基线，后续 membership 回归统一要求同时保留截图哈希和阶段 `page-data`，避免再次把“路由已切换”误判成“页面已体现模板差异”
3. 保持当前 `dev + Nacos` 运行时与 `/app/app.jar` SHA256=`88d23af6cb2934097e2dc0e149537c0e96f18951e6bddc0ad82455a94fdea641`，避免后续回退到旧能力集合
4. 在 invite / login-auth 切片继续沿用同样的“后台动作 + API + DB + 页面截图”成组采证方式

## 8. 回填记录

### 2026-04-01

- 当前判定：`局部完成`
- 备注：当前阶段明确把“后台治理较完整、前台展示较丰富、演员端输出缺失”写入状态文档，避免把本地 resolver 误判成后端闭环

### 2026-04-01（二次回填）

- 当前判定：`局部完成`
- 备注：`kaipaile-server` 已补齐 `/level/info`、`/card/scene-templates`、`/card/config` 最小 actor 输出，并在 `JDK 21` 环境下执行 `mvn -q -DskipTests compile` 通过；当前仍缺前台真实切换与联调

### 2026-04-02

- 当前判定：`局部完成`
- 备注：`kaipai-frontend` 运行时已放开 `verify / invite / level / card` 真接口分支，并把 `card` 与 `ai` 能力拆分，避免误切到未完成 AI 接口；`kaipaile-server` 再次在 `JDK 21` 环境下执行 `mvn -q -DskipTests compile` 通过，`kaipai-frontend` 已执行 `npm run type-check` 通过，当前仍缺 `actor/profile` 权威接口、公开访客链路收口和真实环境联调

### 2026-04-02（二次回填）

- 当前判定：`局部完成`
- 备注：`kaipaile-server` 已补齐 `/actor/profile/mine`、`/actor/profile/{userId}`、`PUT /actor/profile`、`/actor/{userId}`、`/actor/search`，并放开公开详情页和名片页所需的只读接口；`kaipai-frontend` 已放开 `actor` 真接口分支，`mvn -q -DskipTests compile` 与 `npm run type-check` 均通过，当前仍缺主题 / 能力 gating 与 AI 配额的权威化，以及真实环境联调

### 2026-04-02（三次回填）

- 当前判定：`局部完成`
- 备注：`kaipaile-server` 已补齐 `/level/info` 等级 / 会员能力摘要、`/fortune/report`、`/fortune/apply-lucky-color`、`/ai/quota`、`/ai/polish-resume` 最小 actor 输出；`kaipai-frontend` 已放开 `ai / fortune` 真接口分支，并让 `membership / invite / fortune / actor-card / actor-profile detail` 开始消费后端能力摘要，`mvn -q -DskipTests compile` 与 `npm run type-check` 均通过，当前仍缺主题 token 全量后端化与真实环境联调

### 2026-04-02（四次回填）

- 当前判定：`局部完成`
- 备注：`kaipaile-server` 已新增 `/card/personalization` 汇总接口，把模板、能力摘要、命理摘要、主题 token 与分享产物收口到统一后端口径；`kaipai-frontend` 已让 `api/utils/personalization` 优先消费该汇总接口，并让公开详情页切到后端个性化摘要，`mvn -q -DskipTests compile` 与 `npm run type-check` 均通过，当前仍缺编辑态主题配置与真实环境联调

### 2026-04-02（五次回填）

- 当前判定：`局部完成`
- 备注：`kaipai-frontend` 的 `src/pkg-card/actor-card/index.vue` 已改成以 `/api/card/personalization` 返回的模板、能力、主题与分享产物为主事实源，未保存的布局 / 配色仅作为本地 preview overlay；原先页面内直连 `scene-templates / card-config / fortune-report` 再本地拼 `personalizationProfile` 的主链已移除，`npm run type-check` 通过。当前剩余高优先级缺口收敛为“分享恢复 path 与剩余 preview 逻辑仍有页面级本地拼装”以及“后台配置变化到前台恢复的真实联调尚未完成”

### 2026-04-02（六次回填）

- 当前判定：`局部完成`
- 备注：`kaipai-frontend` 的 `src/pkg-card/actor-card/index.vue` 已改成优先使用 `/api/card/personalization` 返回的 artifact path，并只在未保存 preview overlay 时做本地 query patch；`src/pages/actor-profile/detail.vue` 已改成复用后端 `publicCardPage / miniProgramCard` path 作为公开页分享态与名片入口；`src/pkg-card/fortune/index.vue` 与 `src/pkg-card/membership/index.vue` 也已开始直接消费 personalization 模板名和 `artifact.locked` 状态。`npm run type-check`、`kaipai-admin npm run build` 与 `kaipaile-server mvn -q -DskipTests compile` 已再次通过，当前剩余高优先级缺口收敛为“invite/login 分享链路与未保存 preview overlay 仍有本地逻辑”以及“真实环境联调尚未完成”。

### 2026-04-02（七次回填）

- 当前判定：`局部完成`
- 备注：`ActorPersonalizationServiceImpl` 已把 `inviteCard` 产物 path 收口为带 `actorId / scene / artifact / themeId / tone / shared` 的统一上下文路径；`kaipai-frontend` 的 `src/pkg-card/invite/index.vue` 已开始恢复这些 query，并在邀请页内随产物切换同步 share state；`src/pkg-card/actor-card/index.vue` 在选中 `inviteCard` 时也已把真正分享落点优先切到带 `inviteCode` 的登录链路，而不是继续先落到内部邀请页。本轮再次通过 `kaipai-frontend npm run type-check` 与 `kaipaile-server mvn -q -DskipTests compile`。当前剩余高优先级缺口继续收敛为“未保存 preview overlay 仍有本地 query patch”以及“真实环境联调尚未完成”。

### 2026-04-02（八次回填）

- 当前判定：`局部完成`
- 备注：`kaipai-frontend` 的 `src/utils/share-artifact.ts` 已继续承接统一 artifact path patch 规则，`src/pkg-card/actor-card/index.vue` 不再单独维护 `publicCardPage / inviteCard / poster` 三套路径拼装分支，而是统一走 helper 覆盖后端 artifact path。`npm run type-check` 已再次通过。当前剩余高优先级缺口进一步收敛为“未保存 preview overlay 仍需本地 query patch”以及“真实环境联调尚未完成”。

### 2026-04-02（九次回填）

- 当前判定：`局部完成`
- 备注：`kaipaile-server` 的 `src/main/java/com/kaipai/module/server/card/service/impl/ActorCardConfigServiceImpl.java` 已让 `/card/config` 保存时同步回写 `ActorSharePreference`；`kaipai-frontend` 的 `src/pkg-card/actor-card/index.vue` 也已把 `preferredArtifact / preferredTone / enableFortuneTheme` 一并提交，不再只停留在前端临时态。本轮再次通过 `kaipai-frontend npm run type-check` 与 `kaipaile-server mvn -q -DskipTests compile`。当前剩余高优先级缺口继续收敛为“未保存 preview overlay 仍需本地 query patch”以及“真实环境联调尚未完成”。

### 2026-04-02（十次回填）

- 当前判定：`局部完成`
- 备注：`kaipai-frontend` 的 `src/utils/personalization.ts` 已新增显式 preview overlay helper，`src/pkg-card/actor-card/index.vue` 在分享路径生成和 `onShow` 重载时会保留同一份未保存布局 / 配色预览，`src/pages/actor-profile/detail.vue` 也已开始读取同一份 overlay 来恢复主题预览；本轮再次通过 `kaipai-frontend npm run type-check`。当前剩余高优先级缺口继续收敛为“未保存 preview overlay 仍是前端编辑态显式模型，而非后端摘要”和“真实环境联调尚未完成”。

### 2026-04-02（十一次回填）

- 当前判定：`局部完成`
- 备注：`execution/membership` 已补齐 `real-env-runtime-inventory.md`、`real-env-validation-checklist.md`、`real-env-evidence-pack.md`、`validation-sample-ledger-template.md` 与 `collect/new/run-membership-validation.ps1`。本轮已实际执行 `run-membership-validation.ps1 -EnvironmentName dev -SampleLabel local-smoke-fixed`，成功生成样本目录、`capture-results.json`、`runtime-summary.md`、`validation-report.md`，且当前本地运行时 smoke 未扫出配置级阻塞。这说明 membership 联调已从“缺少统一采证入口”推进到“可重复建样本并记录证据”，但真实后台发布 / 回滚样本、小程序恢复截图和数据库比对仍未完成，因此状态继续保持 `局部完成`。

### 2026-04-02（十二次回填）

- 当前判定：`局部完成`
- 备注：`execution/membership/preview-overlay-governance-baseline.md` 已把 preview overlay 从“口头风险”推进成显式治理基线：当前允许它只作为未保存布局 / 配色预览的前端显式态存在，且禁止参与会员能力、artifact 锁定或后台模板主事实判定；同时也明确了何时必须升级为后端临时摘要或 session 级状态。当前这部分已从“边界模糊”推进到“边界明确”，但真实环境样本仍未决定是否需要升级模型，因此状态保持 `局部完成`。

### 2026-04-02（十三次回填）

- 当前判定：`局部完成`
- 备注：已直接探测当前小程序 `.env` 指向的 `http://101.43.57.62`，`/api/card/scene-templates` 与 `/api/level/info` 均返回 `403`，`http://101.43.57.62:8010/api/card/scene-templates` 返回 `502`。这说明当前 `.env` 指向值并不能直接证明“membership 主链已可对外联调”，真实阻塞已经从“本地配置未准备好”推进到“外部访问入口或反代策略未确认”。因此下一步不应继续拿该地址做模板 / 会员样本联调，而应先确认真正可访问的后端入口。

### 2026-04-02（十四次回填）

- 当前判定：`局部完成`
- 备注：已进一步确认 `http://101.43.57.62/api` 的确能命中外部后端，且手机号验证码登录可以为 `user_id=10000` 签发真实 token；但同一 token 下 `/api/user/me`、`/api/verify/status`、`/api/invite/stats`、`/api/level/info`、`/api/card/scene-templates`、`/api/card/personalization` 全部统一返回 `500`。同时只读 JDBC 回读发现：Nacos `prod` 指向的 `kaipai` 库并不具备会员主链基础表，而 `kaipai_dev` 才具备 `user / membership_account / invite_code / referral_record / actor_card_config` 等核心表与 `user_id=10000` 样本。这说明 membership 当前主阻塞已经从“入口未确认”切换为“运行时 jar / profile / 数据库链路漂移”，真实会员样本联调必须等运行时链路核对完成后再继续。

### 2026-04-02（十五次回填）

- 当前判定：`局部完成`
- 备注：已直接登录目标服务器核对运行时：`/opt/kaipai/docker-compose.yml` 把后端容器固定为 `NACOS_ENABLED=true`、`SPRING_PROFILES_ACTIVE=dev`；启动日志也明确订阅 `kaipai-backend-dev.yml` 并激活 `dev` profile。更关键的是，宿主机当前运行 jar 扫描未发现仓内当前 membership 主链所需的 `CardController / LevelController / ActorPersonalizationServiceImpl / MembershipAccountServiceImpl`，而 `2026-04-02 10:58` 的后台异常已把 `/api/user/me`、`/api/verify/status`、`/api/invite/stats`、`/api/level/info`、`/api/card/*` 全部记录为 `NoResourceFoundException`。这说明 membership 当前不是“命中业务后查库炸掉”，而是“线上跑着旧 jar，核心路由根本没挂上”，所以下一步必须先发版当前仓后端能力，再继续模板 / 会员真实联调。

### 2026-04-02（十六次回填）

- 当前判定：`局部完成`
- 备注：已重新打包并替换目标环境后端 jar，远端 `/opt/kaipai/kaipai-backend-1.0.0-SNAPSHOT.jar` SHA256 已变更为 `44d372ae416f06381c94ec797255ed9eacffa8d70d97ffb68f28334849f7969a`。复测结果显示匿名 `GET /api/card/scene-templates`、`GET /api/card/personalization?actorId=10000&scene=default` 以及登录态 `GET /api/user/me`、`GET /api/verify/status`、`GET /api/invite/stats`、`GET /api/level/info`、`GET /api/card/personalization` 全部返回 `200`，membership 旧运行时阻塞已解除。

### 2026-04-02（十七次回填）

- 当前判定：`局部完成`
- 备注：已继续修正资格口径：`verify-status` 返回 `status=2` 的同一用户，`level-info.isCertified` 已对齐为 `true`，`/api/level/info.shareCapability.reasonCodes` 与 `/api/card/personalization.capability.reasonCodes` 当前统一为 `profile_completion_required / fortune_missing / level_required`。这说明 membership 当前真实阻塞已从“认证口径错误”收口为“演员资料完备度与真实业务样本不足”。

### 2026-04-02（十八次回填）

- 当前判定：`局部完成`
- 备注：已按 `execution/membership/samples/20260402-193327-dev-profile-fortune-backfill` 重跑资料 / 命理回填样本，并确认远端 `kaipai_dev` 已真实写入 `actor_profile` 与 `fortune_report`。同一用户 `GET /api/fortune/report`、`GET /api/level/info`、`GET /api/card/personalization?actorId=10000&scene=general&loadFortune=true` 全部返回 `200`，`profileCompletion=95`，`fortuneLuckyColor=#FF6B35`，`reasonCodes` 已收敛为仅剩 `level_required`。本轮也同步确认上一版 SQL 失败根因是远端 `mysql` CLI 缺少 `--default-character-set=utf8mb4`，而不是表结构或 DTO 不兼容。

### 2026-04-02（十九次回填）

- 当前判定：`局部完成`
- 备注：已按 `execution/membership/samples/20260402-195202-dev-admin-membership-template-chain` 跑通后台会员关闭 / 开通、模板主题更新 / 发布的真实链路，并确认同一样本下 `membershipTier` 已出现 `member -> none -> member` 变化，`/api/card/personalization` 主题主色也已从 `#2F6B5F -> #7A3E2B`；`template_publish_log.publish_log_id=3 / publish_version=SMOKE_V2_ADMIN_20260402_195744` 与 `admin_operation_log.operation_log_id` 采证已清理干净。当前仍不能升为闭环完成，因为微信开发者工具当前可见页不是这组 membership 样本页，小程序 `membership / actor-card / detail / invite / fortune` 五页截图仍缺失。

### 2026-04-02（二十次回填）

- 当前判定：`局部完成`
- 备注：`2026-04-02 20:53` 官方 `cli auto --project ... --auto-port 9421` 已恢复可连，`2026-04-02 21:09` 已通过 `miniprogram-automator` 建立真实前台会话并补齐 `execution/membership/samples/20260402-195202-dev-admin-membership-template-chain` 的 `membership / actor-card / detail / invite / fortune` 五页截图，实际路由回读已写入 `captures/mini-program-screenshot-capture.json`。其中 `fortune-general.png` 也已证明当前 fortune 主题的未解锁状态来自真实业务 gating `Lv5 后可应用`，而不是前台运行时异常。因此 membership 当前剩余主阻塞已进一步收口为“更高等级样本缺失”和“preview overlay / 回滚链路仍待继续验证”。 

### 2026-04-02（二十一次回填）

- 当前判定：`局部完成`
- 备注：已按 `execution/membership/samples/20260402-212713-dev-fortune-theme-lv5-unlock` 补齐高等级解锁样本：`user_id=10000` 当前有效邀请数已提升到 `8`，`/api/level/info.level=5`，`/api/card/personalization` 已返回 `themeId=general-member-fortune / primary=#FF6B35 / enableFortuneTheme=true`，并再次补齐 `membership / actor-card / detail / invite / fortune` 五页截图。与此同时，本轮也暴露出新的运行时首存缺口：当 `actor_card_config` 不存在时，`POST /api/card/config` 会因 `Field 'template_id' doesn't have a default value` 返回 `500`；当前源码已在 `ActorCardConfigServiceImpl` 中补上 `templateId` 赋值链，但当前 dev 运行时尚未带上这次修复重新发版。因此 membership 当前剩余主阻塞已进一步收口为“preview overlay 仍是前端显式态”、“模板回滚链路待继续验证”和“后端首存修复待发版”。 

### 2026-04-02（二十二次回填）

- 当前判定：`局部完成`
- 备注：已继续通过 plain `docker` 重建当前 dev 运行时，并确认容器 `/app/app.jar` SHA256=`88d23af6cb2934097e2dc0e149537c0e96f18951e6bddc0ad82455a94fdea641`。随后按 `execution/membership/verify-card-config-first-save.py` 删除 `user_id=10000 / scene=general` 的 `actor_card_config / actor_share_preference` 后再次执行首保存，`POST /api/card/config` 已真实返回 `200/200`，DB 已回读 `template_id=1 / enable_fortune_theme=1`，说明此前 `template_id` 首存缺口已随当前运行时修复。membership 当前剩余主阻塞进一步收口为“preview overlay 仍是前端显式态”、“模板回滚到前台待继续验证”和“后台截图仍未并入同一份 Lv5 样本”。 

### 2026-04-02（二十三次回填）

- 当前判定：`局部完成`
- 备注：已在同一份 `execution/membership/samples/20260402-212713-dev-fortune-theme-lv5-unlock` 样本里继续补齐两段证据。其一，`run-admin-template-rollback-chain.py` 已跑通 `rollback -> /card/scene-templates 与 /card/personalization 切回 builtin 通用 -> restore publish 恢复 Smoke Template`，并把 `template_publish_log`、`admin_operation_log` 一并回读。其二，`capture-admin-membership-template-screenshots.py` 已通过本地 `kaipai-admin` + `127.0.0.1:8010` 代理补齐后台会员账户页、模板页与回滚弹窗三张截图。membership 当前剩余主阻塞已进一步收口为“preview overlay 仍是前端显式态”和“当前真实验证仍固定在 dev + Nacos 运行时”。 

### 2026-04-02（二十四次回填）

- 当前判定：`局部完成`
- 备注：已继续在同一份 `execution/membership/samples/20260402-212713-dev-fortune-theme-lv5-unlock` 样本里补齐 `run-admin-template-rollback-mini-program-chain.py`。结果显示：`actor-card` 在 rollback 后会从 `Smoke Template` 切到 `通用` 并在 restore 后恢复，但 `detail / invite` 三段截图仍保持 `general-member-fortune` 路由与相同截图哈希。这说明当前 `Lv5 + enableFortuneTheme=1` 样本里 fortune 主题层优先级高于模板回滚视觉变化，因此 membership 当前剩余主阻塞继续收口为“preview overlay 仍是前端显式态”和“当前真实验证仍固定在 dev + Nacos 运行时”；若要继续验证公开页视觉回滚，应改用未启 fortune theme 的样本。 

### 2026-04-03

- 当前判定：`局部完成`
- 备注：`kaipai-frontend/src/utils/personalization.ts` 已继续补 `read/writePersonalizationPreviewOverlaySession`，并把 overlay 主恢复路径从“query patch 跨页传递”收口为“当前设备 session 恢复”；`src/pkg-card/actor-card/index.vue` 现在会按 `actorId + scene` 持久化/清理未保存预览，`src/pages/actor-profile/detail.vue` 与 `src/pkg-card/invite/index.vue` 已优先读取同一份 session overlay。与此同时，真实分享 path 已不再携带 overlay query，因此 membership 当前剩余主阻塞已进一步从“前端 query 显式态”收口为“当前设备 session 预览态仍不是后端事实源”。 

### 2026-04-03（二次回填）

- 当前判定：`局部完成`
- 备注：已新增 spec 内标准审计脚本 `execution/membership/run-preview-overlay-static-audit.py`，并在 `2026-04-03 11:16` 实际产出样本 `execution/membership/samples/20260403-111647-preview-overlay-static-audit/summary.md`。本轮审计确认：
  - overlay query key 仍只定义在 `src/utils/personalization.ts`
  - session storage key 仍只定义在 `src/utils/personalization.ts`
  - overlay 相关 helper 当前只命中 `utils / types / actor-card / detail / invite` 白名单
  - 当前 `findingCount=0`
  这说明 membership 当前关于 preview overlay 的剩余问题，已经从“边界可能再次散开”进一步收口为“边界已可重复审计，但是否升级为后端临时摘要仍待真实样本决定”。

### 2026-04-03（三次回填）

- 当前判定：`局部完成`
- 备注：已继续把 preview overlay 的当前结论从“口头偏好”固化成 `execution/membership/preview-overlay-decision-record.md`，明确当前继续保持 `session-only`，不升级为后端临时摘要。同时本轮已删除 `kaipai-frontend/src/utils/personalization.ts` 中已无运行时引用的 `patchPathWithPersonalizationPreviewOverlay`，并重新执行 `execution/membership/run-preview-overlay-static-audit.py preview-overlay-static-audit-post-session-decision` 产出样本 `execution/membership/samples/20260403-121354-preview-overlay-static-audit-post-session-decision/summary.md`；审计结果继续 `findingCount=0`，且 helper 白名单已不再包含 path patch。随后又重跑 `execution/membership/run-admin-template-rollback-mini-program-no-fortune-theme.py` 产出最新样本 `execution/membership/samples/20260403-121415-dev-template-rollback-no-fortune-theme/summary.md`，其 `admin-template-rollback-mini-program-summary.md` 已直接列出 `before / after-rollback / after-restore` 三段 `actor-card / detail / invite` 的 `page-data` 文件名。这个结果说明 membership 当前关于 overlay 的下一步不再是“继续发明 path patch 或立即后端化”，而是“在现有 session-only 门禁下继续观察是否出现跨登录 / 跨设备的新证据”。

### 2026-04-03（四次回填）

- 当前判定：`局部完成`
- 备注：已继续按 `preview-overlay-governance-baseline.md` 的“收口类”动作减少 query 兼容读取分支：`kaipai-frontend/src/pages/actor-profile/detail.vue` 不再读取旧 overlay query，公开详情页现已只从当前设备 session 恢复未保存预览；旧 query overlay 兼容入口已收口为 `src/pkg-card/actor-card/index.vue` 单点。与此同时，`execution/membership/run-preview-overlay-static-audit.py` 的白名单也已同步收紧，不再允许 `detail.vue` 命中 `readPersonalizationPreviewOverlay`。这说明 membership 当前 overlay 结构又进一步从“多页兼容读取”收口为“单入口兼容 + 多页 session 恢复”。

### 2026-04-03（五次回填）

- 当前判定：`局部完成`
- 备注：已继续把最后一个历史 overlay query 兼容入口从 `kaipai-frontend/src/pkg-card/actor-card/index.vue` 移除。当前 `actor-card / detail / invite` 三页都只从当前设备 session 恢复未保存预览，页面运行时和真实分享 path 均不再读取或写入 overlay query。与此同时，`execution/membership/run-preview-overlay-static-audit.py` 已再次同步收紧，不再允许任何业务页命中 `readPersonalizationPreviewOverlay`。这说明 membership 当前 overlay 边界已经从“单入口兼容 + 多页 session 恢复”继续收口为“纯 session-only 恢复链”，后续若再讨论 overlay 升级，只能基于跨登录 / 跨设备的新证据，而不是历史 query 兼容包袱。

### 2026-04-03（六次回填）

- 当前判定：`局部完成`
- 备注：已继续删除 `kaipai-frontend/src/utils/personalization.ts` 中最后残留但已无调用方的历史 query 兼容代码：`readPersonalizationPreviewOverlay` 与 `previewLayout / previewPrimary / previewAccent / previewBackground` 四个旧 key 已从前端运行时代码移除。`execution/membership/run-preview-overlay-static-audit.py` 也已从“只允许 owner 文件持有 query key”升级为“全仓禁止 overlay query key”。这意味着 membership 当前 overlay 已不再只是“行为上 session-only”，而是“代码结构上也已完全 session-only”。

### 2026-04-03（七次回填）

- 当前判定：`局部完成`
- 备注：已在删除旧 query key 后再次执行 `execution/membership/run-preview-overlay-static-audit.py preview-overlay-static-audit-no-query-keys`，产出样本 `execution/membership/samples/20260403-122635-preview-overlay-static-audit-no-query-keys/summary.md`，结果继续 `findingCount=0`。同时对 `kaipai-frontend/src` 执行全文搜索 `previewLayout|previewPrimary|previewAccent|previewBackground|readPersonalizationPreviewOverlay(` 已无任何命中。这说明 membership 当前 overlay 已从“session-only 主链”进一步收口为“仓内已无历史 query 兼容代码残留”的状态。

### 2026-04-03（八次回填）

- 当前判定：`局部完成`
- 备注：已继续按 `mp-ui-change-verification` 收口公开详情页的页面锚点：`kaipai-frontend/src/pages/actor-profile/detail.vue` 顶部已从 `KpNavBar` 切到 `KpFloatingBackButton`，首屏主块已改为 `actor-detail-page__hero-card` 名片化 hero，分节标题已统一复用 `KpSectionHead`，`查看联系方式` 也已从正文操作区移到底部固定 `actor-detail-page__action-bar`。本轮再次通过 `kaipai-frontend npm run type-check` 与 `npm run build:mp-weixin`，并已核对三层产物：
  - `src/pages/actor-profile/detail.vue` 命中 `actor-detail-page__hero-card`、`actor-detail-page__action-bar`、`当前公开名片已开放联系入口，登录后可查看联系方式。`
  - `dist/build/mp-weixin/pages/actor-profile/detail.wxml|wxss|js` 已命中 `kp-floating-back-button`、`actor-detail-page__hero-card`、`actor-detail-page__action-bar`、`查看分享名片`，且 `detail.wxss` 已落出 `margin-top:-198rpx` 与底部固定 action bar 样式
  - `dist/dev/mp-weixin/pages/actor-profile/detail.wxml|wxss|js` 已同步命中同一批类名、文案和 `margin-top:-198rpx`
  这说明本轮不是只改了源码结构，而是公开详情页已经实际切到“名片首屏 + 底部联系入口”布局。

### 2026-04-03（九次回填）

- 当前判定：`局部完成`
- 备注：已继续完成 `05-11` 的页面级收口尾项，把 `actor-card / invite / pages/actor-profile/edit` 内重复散落的认证 CTA 文案统一下沉到 `kaipai-frontend/src/utils/verify.ts` 的场景化 helper，并让 `actor-card / membership` 继续共用 `KpDualActionRow.vue` 作为双 CTA 分享动作区。同时也已明确保留 `invite` 页四宫格为页内实现，因为它同时承担二维码状态反馈、复制邀请码 / 邀请链接、海报生成和分享门禁，不是简单双按钮变体。本轮再次通过 `kaipai-frontend npm run type-check` 与 `npm run build:mp-weixin`，说明 membership / share 主线当前又从“页面各写一份认证与分享按钮口径”收口为“共享 helper + 共享组件 + 有意保留的页内特例”。

### 2026-04-03（十次回填）

- 当前判定：`局部完成`
- 备注：已在新增 `00-49 membership-preview-overlay-fact-source-boundary` 后继续执行静态审计样本 `execution/membership/samples/20260403-234229-post-00-49-fact-boundary/summary.md`。最新样本继续 `findingCount=0`，且当前实际 touchpoint 已收口为 `src/utils/personalization.ts`、`src/types/personalization.ts`、`src/pkg-card/actor-card/index.vue`、`src/pages/actor-profile/detail.vue` 四处；`invite/index.vue` 虽仍保留在白名单中，但本轮已不再命中实际 helper。这个结果说明 `00-49` 落地后，membership 当前关于 overlay 的剩余问题没有重新扩散，后续应继续按“没有跨登录 / 跨设备 / 高阶事实字段新证据前，不再直接后端化”的门禁推进。

### 2026-04-03（十一次回填）

- 当前判定：`局部完成`
- 备注：已在刚完成 `backend-only + admin-only` 标准发布后，继续用正式样本 `execution/membership/samples/20260403-234959-dev-post-release-membership-chain/` 重跑 `run-admin-membership-template-chain.py`。最新样本再次证明：同一用户 `membershipTier` 仍稳定出现 `member -> none -> member`，`after-close.reasonCodes` 继续收口为 `member_required`，而模板发布记录也已推进到 `publishLogId=26 / publishVersion=SMOKE_V2_ADMIN_20260403_235012`。与此同时，本轮已把 membership 几条标准样本脚本统一补成 `sendCode -> login` 最多 3 次重试，避免后续再因为瞬时 `code=1006` 把联调入口误判成主链回退。这个结果说明当前发布后的 membership 主链仍稳定，剩余问题继续聚焦在 overlay 事实源边界与页面级证据，而不是后台发布 / 会员开关主链失效。

### 2026-04-04（一次回填）

- 当前判定：`局部完成`
- 备注：已继续把正式样本 `execution/membership/samples/20260403-234959-dev-post-release-membership-chain/` 补齐小程序页面证据。`capture-mini-program-screenshots.js` 当前已在同一样本目录生成 `captures/mini-program-screenshot-capture.json`，并为 `membership / actor-card / detail / invite / fortune` 五页同时保留 route、query、page-data 与 screenshot SHA256。当前关键事实为：`themeId=general-member-fortune`、`preferredArtifact=miniProgramCard`、`enableFortuneTheme=true` 在五页证据中保持一致；`actor-card` 命中 `artifact=miniProgramCard`，`detail` 命中 `pages/actor-profile/detail?actorId=10000&scene=general&themeId=general-member-fortune&shared=1`，`invite` 命中 `artifact=inviteCard&themeId=general-member-fortune&tone=natural`。这说明当前发布后 membership 正式样本已不再只停留在 API + DB 侧，而是已经补到小程序页面证据层；剩余高优先级缺口继续收口为“后台 UI 截图尚未并入同一样本”与 `00-49` 已定义的 overlay 事实源边界。
