# 00-202 执行记录

## 当前状态

- 状态：数据库镜像恢复完成；源数据不一致与应用 schema 兼容缺口已单独记录
- 日期：2026-07-27
- 源：生产 `kaipai_prod`（只读）
- 目标：本机 Docker `kaipai_dev`

## 已完成

- 已确认本地尾号 6737 当前命中空壳 `userId=8`，实名状态为 0，演员档案、实名申请、实名归属和分享卡均为 0。
- 已确认 `00-194` 生产迁移记录中尾号 6737 对应林夏 `userId=10007`，具有演员档案、已通过实名和 3 张分享卡。
- 已确认权威生产入口为 `101.43.57.62` / `kaipai-mysql` / `kaipai_prod`。
- 已确认生产 SSH 专用 release key 和远程受控 helper 可用。
- 生产只读预检确认：`userId=10007` 的用户实名标志为 2、演员档案已认证、实名归属存在、分享卡 3 张；唯一实名申请仍为待审状态 1，且没有后台审核日志。本轮只做原样镜像，不把该状态不一致写回生产。

## 备份与完整性

- 批次目录：`.sce/runbooks/backend-admin-release/records/local-backups/20260727-161922-production-to-local-restore/`（gitignored）。
- 本地执行前回滚 dump：`local-before/kaipai_dev.sql.gz`，15404 字节，SHA256 `CC150630BAE4DC6BF5F3B221A9E2642D9E718343C552F2464A2788B706579D76`。
- 生产 dump：`remote/kaipai_prod.sql.gz`，56521 字节；远端 helper 与本地文件 SHA256 均为 `FF61DF6CB5A7D6DD2C4C747A4B461870AC476D4965B210098640568743E8BFDE`。
- 数据库名中立恢复 dump：`restore/kaipai_prod-to-kaipai_dev.sql.gz`，56453 字节，SHA256 `18B352A413F58356A511F305CDE0691A7DDCEE86CFDC303DC76D89311A5E0DE1`。
- 三个 gzip 均已完整解压到 EOF 并通过 CRC 校验；批次内已生成 `SHA256SUMS.txt` 与 `execution-summary.md`。

## 镜像验证

以下证据在登录 smoke 前采集：

- `kaipai_prod` / `kaipai_dev` 基础表为 `94 / 94`，表名差异 0、列定义差异 0、结构 dump 差异 0。
- 两库有效用户为 `16 / 16`；94 张表逐表精确 `COUNT(*)` 差异为 0。
- 索引条目为 `589 / 589`、约束为 `163 / 163`，表级引擎 / 行格式 / 排序规则差异为 0；全部基础表均为 InnoDB。
- 视图、routine、trigger、event 均为 `0 / 0`。
- 尾号 6737 的唯一有效用户为 `userId=10007`；用户实名标志 2、已认证演员档案 1、实名申请桶 `status=1 / deleted=0 / count=1`、实名归属 1、分享卡 3。

## 后端与 API smoke

- 本地后端已在 PID `42112`、端口 `8010` 重启，`GET /api/doc.html` 返回 HTTP 200。
- 使用只存在于进程内存和本地 Redis 临时键中的验证码登录；未调用真实短信接口，JWT、验证码和完整手机号均未落盘。
- `POST /api/auth/login`、`GET /api/user/me`、`GET /api/verify/status`、`GET /api/card/my-cards` 的业务码均为 200。
- 脱敏结果：`userId=10007`、手机号 `137****6737`、`user/me.realAuthStatus=2`、`verify/status.status=1`、分享卡 3。
- 登录更新了本地 `user.last_login_time` / `last_update`，这是 smoke 的预期本地运行写入；远程生产库未被写入。镜像一致性结论指登录前门禁，不把登录后的两个审计时间差异误报为恢复偏差。
- `GET /api/actor/profile/mine` 返回业务码 500。只读根因核对确认，当前本地后端 `ActorProfile` 实体会查询的 12 个职业档案列在生产镜像中存在 0 个，且生产镜像没有 `flyway_schema_history`；仓库中对应 `V20260723_001__career_profile_domain_foundation.sql` 尚未进入该生产 schema。本次保持生产原样，未擅自升级本地镜像。

## 结论与后续

- 生产 `kaipai_prod` 已成功恢复到本地 `kaipai_dev`，本地执行前库可由 `local-before` dump 回滚。
- “用户 / 演员已认证，但最新实名申请仍待审核”来自生产源数据；不能判定为恢复失败，也未在本任务中静默改成 2。
- 小程序旧 token 可能仍指向恢复前的 `userId=8`，本地联调前必须退出登录或清理本地登录态后重新登录。
- 如需让当前职业资料页调用 `/api/actor/profile/mine`，应另建 schema 兼容 / 本地迁移任务，先确认是否将待发布迁移应用到本地生产镜像；不得把该升级伪装成原样恢复的一部分。

## 数据库恢复后的微信配置恢复

- 2026-07-27 18:33 再次调用本地 `POST /api/auth/wechat-login` 时返回“微信登录未配置小程序 appId/appSecret”。只读定位确认该异常与数据库镜像无关：数据库恢复后的 PID `42112` 由裸 `java -jar` 启动，未加载已经存在且通过门禁的 `.sce/config/local-secrets/wechat-miniapp.env`；Spring 不会自动加载该自定义 dotenv 文件。
- 已新增统一入口 `.sce/tools/start-kaipai-local-backend.ps1`。入口在停止现有进程前校验微信输入及前端 AppID 一致性，仅通过启动器临时进程环境把配置传给 Java 子进程，并固定 `dev / NACOS_ENABLED=false / 8010 / kaipai_dev:3309 / Redis:6379`；AppSecret 未进入 JVM 命令行、日志、Git 文件或用户 / 机器环境变量。
- 使用数据库恢复时实际运行的同一份 JAR 重启，SHA256 仍为 `679DA69C4C76B109AB9C75CD0C5556F37E4D847D154AE2CA1D5C44D2B4A0F5F4`；加固后按 runbook 标准无参数入口复跑的最终 PID 为 `22112`，`GET /api/doc.html` 返回 HTTP 200。运行库仍为 `kaipai_dev`，职业资料迁移列计数仍为 0，未在本修复中执行 schema migration。
- 删除本地 Redis 中旧的 `wechat:miniapp:access-token` 后，以明确虚构的 code 调用微信登录。响应不再进入“未配置”分支，而是进入微信服务商手机号换取并返回 `invalid code`；随后本地 Redis 生成有效期内的 access token 缓存，证明 AppID/AppSecret 组合已成功生效。虚构 code 在用户查询 / 注册前失败，没有产生用户数据写入。
- 最终 PID `22112` 另以本地 Redis 临时验证码执行脱敏认证 smoke，得到 `userId=10007 / 137****6737 / realAuthStatus=2 / verifyStatus=1 / cardCount=3`；临时验证码键已在 `finally` 清理。该结果证明重启后的应用仍使用本地 Redis 并可读取恢复后的目标账号，同时再次确认 `verifyStatus=1` 是既有源数据状态不一致，不是本次微信配置修复造成的回归。
- 微信开发者工具已打开固定目录 `kaipai-frontend/dist/dev/mp-weixin`，UI Automation 回读确认项目路径正确、模拟器已加载 `pages/login/index`，构建产物请求地址为 `http://127.0.0.1:8010`。真实手机号快捷登录仍需用户在模拟器点击一次授权按钮以生成新的单次 code；旧 code 不可复用，本执行记录不把该必要交互误写为已完成。
