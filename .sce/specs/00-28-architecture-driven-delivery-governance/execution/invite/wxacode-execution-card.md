# 邀请裂变微信官方小程序码收口执行卡

## 1. 执行卡名称

邀请裂变与邀请资格闭环 - 微信官方小程序码收口执行卡

## 2. 归属切片

- `../../slices/invite-referral-capability-slice.md`

## 3. 负责范围

- 把 invite 当前“链接二维码”能力收口到“微信官方 `wxacode`”能力
- 固化微信小程序码生成所需的后端配置、接口契约和失败口径
- 固化前端对 `scene` 落地、邀请码恢复和失败兜底的唯一消费方式
- 固化真实环境验证口径，避免再把“二维码图片能显示”误判成“官方小程序码闭环已完成”

## 4. 不负责范围

- `referral_record`、`user_entitlement_grant`、实名审核、资格生效主链
- 后台邀请规则、风险复核、资格发放页面
- 邀请海报视觉设计和非微信渠道二维码物料
- 微信支付、订阅消息、客服消息等其他微信能力

## 5. 当前已确认事实

1. 前端小程序工程已固定 `appid`：
   - `kaipai-frontend/project.config.json`
   - 当前值：`wxd38339082a9cfa4e`
2. 后端已具备微信 access token 基础能力，并已开始抽成可复用服务：
   - `kaipaile-server/src/main/java/com/kaipai/module/server/auth/service/impl/AuthServiceImpl.java`
   - `kaipaile-server/src/main/java/com/kaipai/module/server/wechat/service/WechatMiniProgramService.java`
   - 已存在 `wechat.miniapp.app-id`、`wechat.miniapp.app-secret`、`env-version`
   - 已存在 `cgi-bin/token` access token 获取与 Redis 缓存
3. invite 模块已补上官方码实现入口，但真实环境 smoke 尚未补齐：
   - `kaipaile-server/src/main/java/com/kaipai/module/server/referral/service/impl/InviteQrCodeServiceImpl.java`
   - `kaipaile-server/src/main/java/com/kaipai/module/controller/referral/ReferralController.java`
   - 当前实现会优先请求 `wxa/getwxacodeunlimit`，失败时显式降级到链接二维码
4. 前端对官方小程序码必需的 `scene` 落地已具备最小消费基础：
   - `kaipai-frontend/src/utils/invite.ts`
   - `resolveInviteCodeFromLaunchOptions(...)` 已支持从 `scene` 解析 `inviteCode`
5. 当前仍未补齐：
   - 官方小程序码真实环境 smoke 或扫码样本
   - 目标环境 `wechat.miniapp.app-id/app-secret` 已配置证据
   - 前端对 `qrCodeType / fallbackReason` 的显式展示或告警
6. `2026-04-03 04:34` 已通过真实样本 `invite-20260403-043423-remote-invite-wxacode-fallback-post-release` 确认当前线上结果：
   - `/api/invite/code` 返回 `qrCodeType=link-qrcode`
   - `qrCodeFallbackReason=微信小程序 appId/appSecret 未配置`
   - 这证明新代码主链已上线，但目标环境仍缺微信配置
7. `2026-04-03 04:41` 已通过 `00-29` 标准只读诊断样本 `20260403-044108-invite-wxacode-compose-source-precheck` 补齐配置来源证据：
   - `compose-backend-source.txt` 显示远端 `/opt/kaipai/docker-compose.yml` 的 `kaipai` 服务只注入了 `NACOS_ENABLED / SPRING_PROFILES_ACTIVE / SERVER_PORT`
   - `compose-rendered-backend.txt` 显示 `docker compose config` 渲染后的后端服务定义同样缺少 `WECHAT_MINIAPP_APP_ID / WECHAT_MINIAPP_APP_SECRET`
   - 因此当前 blocker 已明确位于 compose / env source 层，而不是 Nacos 后续覆盖
8. `2026-04-03` 已按 `00-29` 补齐后端 compose 来源同步标准入口：
   - `python .sce/runbooks/backend-admin-release/scripts/run-backend-compose-env-sync.py --label <label> --from-local-env WECHAT_MINIAPP_APP_ID --from-local-env WECHAT_MINIAPP_APP_SECRET`
   - 该入口只负责把微信配置写入 compose / env source 并留档，不替代后续 `backend-only` 发布
9. `2026-04-03 04:56` 已通过 `00-29` 标准 Nacos 只读诊断样本 `20260403-045556-invite-wxacode-nacos-precheck` 补齐覆盖层证据：
   - `nacos-config-presence-summary.txt` 显示 `kaipai-backend`、`kaipai-backend.yml`、`kaipai-backend-dev.yml` 全部缺少微信 `app-id / app-secret`
   - 因此当前 blocker 已不是“只差 compose 写入”，而是 compose 与 Nacos 两侧都缺合法微信配置来源
10. `2026-04-03` 已按 `00-29` 补齐 Nacos 配置同步标准入口：
   - `python .sce/runbooks/backend-admin-release/scripts/run-backend-nacos-config-sync.py --label <label> --nacos-data-id kaipai-backend-dev.yml --from-local-env WECHAT_MINIAPP_APP_ID --from-local-env WECHAT_MINIAPP_APP_SECRET`
   - 该入口只负责把微信配置写入目标 dataId 并留档，不替代后续 `backend-only` 发布
11. `2026-04-03 05:08` 已通过 `20260403-050801-backend-nacos-noop-remote-verify` 对 `kaipai-backend-dev.yml` 完成一次原文回写验证：
   - Nacos 标准写入链已确认可用
   - 当前剩余 blocker 已不再是“不会写 Nacos”，而是“缺真实微信配置值”
12. `2026-04-03` 已补齐 `00-29` 统一微信配置门禁入口：
   - `python .sce/runbooks/backend-admin-release/scripts/read-backend-wechat-config-precheck.py --label <label>`
   - 该入口会一次性固化 compose 来源、compose 渲染、容器 env 与 Nacos dataId presence summary，后续 `wxacode` 预检查不再手工串两份诊断脚本
13. `2026-04-03 06:29` 已补齐 `00-29` 本地微信输入检查样本 `.sce/runbooks/backend-admin-release/records/diagnostics/20260403-062919-invite-login-local-input-gate/summary.md`：
   - 当前机器没有 `WECHAT_MINIAPP_APP_ID / WECHAT_MINIAPP_APP_SECRET` 本地环境输入
   - `kaipai-frontend/project.config.json` 仅能证明前端固定 `appid=wxd38339082a9cfa4e`
   - 当前 blocker 已进一步收口为“本地缺合法 secret 输入 + 远端 compose/Nacos 也未配置”，而不是“只差执行同步脚本”
14. `2026-04-03 06:33` 已通过 `00-29` 微信配置同步总控 dry-run 记录 `.sce/runbooks/backend-admin-release/records/20260403-063339-backend-wechat-config-pipeline-invite-login-wechat-sync.md` 验证：
   - 总控顺序已固定为 `local-input -> remote-gate -> compose sync -> nacos sync`
   - 在当前无 secret 输入环境下，总控会在第 1 步标准中止，不再继续误打远端
15. 当前 `00-29` 已把 invite / login-auth 共用的微信配置门禁收口到单页 runbook：
   - `.sce/runbooks/backend-admin-release/wechat-config-gate-runbook.md`
   - 后续不再散落执行“初始化本地 secret 文件 / 判定合法输入 / 总控同步 / backend-only 重建 / 门禁复检”这几步
16. `2026-04-03 08:33` 已继续把 blocker 从“本地缺输入位”收口到“缺合法 secret 来源”：
   - `scripts/init-local-wechat-secret-file.py` 已可在 `.sce/config/local-secrets/wechat-miniapp.env` 初始化 gitignored secret 文件，并预填当前小程序 `appId`
   - 最新本地样本 `20260403-083329-continue-wechat-local-gate-local-input` 已证明：即使 secret 文件已经存在，只要 `WECHAT_MINIAPP_APP_SECRET=replace-with-real-app-secret` 之类的 placeholder，仍会判定 `Release Ready=no`
   - 同批总控记录 `20260403-083329-backend-wechat-config-pipeline-continue-wechat-local-gate.md` 已确认：总控会以 `local_input_not_ready` 在第 1 步标准中止

## 6. 目标交付物

- 后端提供稳定的 invite 官方小程序码生成能力，而不是继续返回普通链接二维码
- 官方码生成失败时返回明确的“配置缺失 / 微信接口失败 / 页面参数非法”口径，不能再静默退回成功态
- 前端统一消费 `scene`，并明确区分“官方小程序码”和“链接二维码 fallback”
- 真实环境验证材料中新增“扫码打开 -> 登录页恢复 inviteCode -> 注册 / 登录落地”的证据链

## 7. 关键任务

1. 固化后端基础能力边界
   - 将微信 access token 能力从 `AuthServiceImpl` 中提炼为 invite 可复用的基础服务，或建立明确复用入口
   - 明确 `wechat.miniapp.app-id/app-secret` 为 invite 官方码生成的必备配置
   - 明确 invite 允许落地的 page 固定为 `/pages/login/index`
2. 补齐官方小程序码接口
   - 在 invite 域引入 `wxacode.getUnlimited`
   - 固定 `scene` 编码方案，至少覆盖 `inviteCode`
   - 若还要承接 `artifact / themeId / tone / shared`，必须先证明不超微信 `scene` 长度限制
   - DTO 中显式标注当前返回的是 `wxacode` 还是 `link-qrcode`
3. 收口前端消费方式
   - 登录页继续以 `inviteCode > scene` 的优先级恢复邀请码
   - invite 页和海报页不得再把“有二维码图片”直接等价为“官方小程序码已可用”
   - 若保留 fallback，必须把 fallback 限定为明确的降级态，而不是默认主链路
4. 固化真实环境验证
   - 以同一样本记录官方码扫码落地结果
   - 验证扫码后是否打开登录页并恢复 `inviteCode`
   - 验证注册或登录后仍能进入现有 invite 闭环样本链
5. 固化发布前检查
   - 发布前必须确认当前运行时存在 `wechat.miniapp.app-id/app-secret`
   - 当前 invite / login-auth 的微信门禁顺序，以 `.sce/runbooks/backend-admin-release/wechat-config-gate-runbook.md` 为单页入口
   - 只有在本地输入通过“合法 secret”门禁后，才允许继续 compose / Nacos 同步；不得再用 fake secret 或 placeholder 文件做“已就绪”替代
   - 发布前优先执行 `python .sce/runbooks/backend-admin-release/scripts/run-backend-wechat-config-sync-pipeline.py --label <label> [--dry-run]` 固定总控顺序；若只需只读核对，再退回 `read-local-wechat-config-inputs.py` 与 `read-backend-wechat-config-precheck.py`
   - 发布后必须补官方码接口 smoke，不能只测 `/api/invite/qrcode` 返回 `200`

## 8. 依赖项

- 微信小程序后台 `appid` 必须与 `kaipai-frontend/project.config.json` 一致
- 当前目标环境 `dev + Nacos` 必须提供可用的 `wechat.miniapp.app-id/app-secret`
- 登录页路由 `/pages/login/index` 必须保持可作为官方码落地点
- 邀请链现有 API + DB 闭环必须继续保持通过，避免在补官方码时回归到旧阻塞

## 9. 验证方式

- `GET /api/invite/qrcode` 或等效新接口能明确返回官方小程序码结果，而不是普通链接二维码
- 真实扫码后，小程序登录页能恢复出同一 `inviteCode`
- 继续使用同一邀请码样本时，注册 / 实名 / 后台审核 / 资格发放主链不回归
- 缺少微信配置时，接口返回明确失败原因，状态文档与发布记录可追溯

## 10. 完成定义

- invite 官方小程序码不再依赖 `QrCodeBase64Util` 生成登录链接图片
- 后端、前端、验证脚本和状态文档对 `wxacode` / `link-qrcode` 的口径一致
- 同一样本已补齐“官方码扫码落地 -> inviteCode 恢复 -> 闭环主链继续可用”的真实证据
- 发布记录中已补微信配置检查和官方码 smoke

## 11. 风险与备注

- 当前最容易误判的点不是“二维码接口 500”，而是“返回了二维码图片”被误写成“官方小程序码已完成”
- 当前第二个高频误判点是“本地 secret 文件已存在”被误写成“微信配置已就绪”；现在只有合法 `appSecret` 才能进入总控
- `scene` 长度、编码规则和未来是否承载更多分享上下文必须先收口，否则很容易因为参数超长再次回退到普通链接二维码
- 若目标环境只补了前端 `appid`、没补后端 `app-secret`，invite 页面仍可能显示二维码，但不会真正具备官方码能力
