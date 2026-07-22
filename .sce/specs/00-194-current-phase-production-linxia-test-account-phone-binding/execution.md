# 00-194 执行记录

## 当前状态

- 状态：`database-migration-and-cleanup-passed`
- 创建日期：`2026-07-09`
- 目标：把旧线上库「林夏」测试演员账号及直接资产迁移到当前生产库，并绑定目标推广手机号。
- 隐私约束：完整手机号不写入本文件；执行记录只保留脱敏值。

## 已确认代码事实

- `AuthServiceImpl.login(...)` 使用 `user.phone` 查询登录账号。
- `AuthServiceImpl.loginByWechat(...)` 使用小程序授权手机号查询或注册用户。
- `ActorProfileServiceImpl.buildProfile(...)` 联系电话优先读取 `actor_profile.phone`，再兜底 `user.phone`。
- 登录链路使用 `user.phone` 查询账号；当前生产库同一手机号只能保留一个未删除用户。
- 分享卡、配置、实名、邀请、能力和 AI 资产均以 `user_id / actor_profile_id / share_card_id / task_id` 关联；本轮保留旧线上原主键迁移，避免重写关系。

## 已完成只读诊断

### 当前生产库 `kaipai_prod`

`precheck` / `diagnose` / `roster` 结果：

- 目标手机号：`137****6737`
- 当前生产目标手机号账号：`userId=5`
- 当前生产目标账号名称：`开拍用户6737`
- 当前生产目标账号资产：演员档案 `0`、分享卡 `0`、实名 `0`、邀请码 `0`、能力账号 `0`
- 当前生产库总量：有效用户 `5`、演员档案 `0`、分享卡 `0`
- 结论：`kaipai_prod` 不是旧线上林夏资产所在库，目标手机号账号是空壳账号。

### 旧线上源库 `kaipai_dev`

`diagnose` / `inventory` 结果：

- 源账号：`userId=10007`
- 源演员档案：`actorProfileId=10010`
- 源名称：`nickName=林夏`、`realName=林夏`
- 源手机号：`137****6737`
- 源分享卡：`3`
- 源实名：`1`
- 源邀请码：`1`
- 源能力账号：`1`
- 源邀请记录：`8`
- 源 AI 任务：`16`
- 源 AI 页面：`3`
- 源联系请求：`1`
- 源浏览历史：`14`

### 迁移预检

`migration-precheck` 已通过：

- 源库：`kaipai_dev`
- 目标库：`kaipai_prod`
- 源账号门禁：`SOURCE_USER_COUNT=1`
- 源林夏名称门禁：`SOURCE_LINXIA_NAME_COUNT=1`
- 源演员档案门禁：`SOURCE_ACTOR_PROFILE_COUNT=1`
- 生产目标手机号空壳账号：`TARGET_EMPTY_USER_ID=5`
- 生产空壳资产门禁：`TARGET_EMPTY_USER_ASSET_COUNT=0`
- 目标库源账号主键冲突：`0`
- 目标库源档案主键冲突：`0`
- 目标库源分享卡主键冲突：`0`
- 目标库源实名 / 邀请 / 能力主键冲突：`0`

## 执行结果

### 生产迁移 apply

- 执行时间：`2026-07-09 12:20:31 +0800`
- run id：`20260709-122031-migration-apply`
- 脚本模式：`migration-apply`
- 源库：`kaipai_dev`
- 目标库：`kaipai_prod`
- 目标手机号：`137****6737`
- 源账号：`userId=10007`
- 源演员档案：`actorProfileId=10010`
- 生产空壳账号：`userId=5`
- 备份表前缀：`zz194_`
- 状态：`passed`

关键结果：

- `ARCHIVED_TARGET_USER_ROWS=1`
- `INSERTED_USER_ROWS=1`
- `INSERTED_ACTOR_PROFILE_ROWS=1`
- `INSERTED_SHARE_CARD_ROWS=3`
- `INSERTED_ACTOR_CONFIG_ROWS=3`
- `INSERTED_SHARE_PREFERENCE_ROWS=3`
- `INSERTED_IDENTITY_ROWS=1`
- `INSERTED_IDENTITY_OWNER_ROWS=1`
- `INSERTED_INVITE_CODE_ROWS=1`
- `INSERTED_REFERRAL_RECORD_ROWS=8`
- `INSERTED_CAPABILITY_ACCOUNT_ROWS=1`
- `INSERTED_AI_TASK_ROWS=16`
- `INSERTED_AI_PAGE_ROWS=3`
- `INSERTED_CONTACT_REQUEST_ROWS=1`
- `INSERTED_VIEW_HISTORY_ROWS=14`
- `POST_TARGET_PHONE_USER_COUNT=1`
- `POST_SOURCE_ACTOR_PROFILE_COUNT=1`
- `POST_SOURCE_SHARE_CARD_COUNT=3`

说明：

- 生产原空壳账号已备份并软删除，手机号和 account 均改为归档值，避免登录查询冲突。
- 林夏账号按旧线上原主键迁入当前生产库，直接资产按原外键关系迁入，未重建分享卡。
- `capability_change_log` 与 `user_entitlement_grant` 源库计数为 `0`，本轮插入为 `0` 属预期。

### 迁移后数据库复核

第一轮迁移后只读复核：

- `20260709-122122-diagnose`
- `20260709-122122-inventory`
- `20260709-122123-roster`

第二轮 cleanup 后只读复核：

- `20260709-122654-diagnose`
- `20260709-122654-inventory`
- `20260709-122654-roster`

第二轮复核结果：

- 目标手机号：`137****6737`
- 当前生产未删除目标用户：`userId=10007`
- 目标手机号其它未删除用户：`0`
- 演员档案：`actorProfileId=10010`
- 档案名称：`nickName=林夏`、`realName=林夏`
- 演员档案数：`1`
- 分享卡数：`3`
- 实名记录：`1`
- 邀请码：`1`
- 能力账号：`1`
- 当前生产有效用户总数：`5`
- 当前生产演员档案总数：`1`
- 当前生产分享卡总数：`3`

### 清理结果

- run id：`20260709-122621-cleanup`
- 脚本模式：`cleanup`
- 状态：`passed`
- 结果：`MIGRATION_HELPER_PROCEDURE_DROPPED=1`

说明：本轮清理只删除迁移脚本临时创建的 `kp_194_insert_common_columns` 存储过程，不修改业务数据表。

### 真实登录 API 验证

- send-code run id：`20260710-165327-send-code`
- api-verify run id：`20260710-165410-api-verify`
- 状态：`passed`

验证结果：

- `LOGIN_TOKEN_PRESENT=1`
- `LOGIN_USER_ID=10007`
- `LOGIN_USER_TYPE=1`
- `ME_USER_ID=10007`
- `ME_USER_TYPE=1`
- `ACTOR_PROFILE_USER_ID=10007`
- `ACTOR_PROFILE_NAME=林夏`
- `ACTOR_PROFILE_REAL_NAME=林夏`
- `ACTOR_PROFILE_CERTIFIED=True`
- `API_CARD_COUNT=3`
- `API_TEMPLATE_COUNT=3`

说明：

- 验证码只通过执行时环境变量注入，未写入本文件或样本文件。
- JWT 只用于当次 API 调用，未写入本文件或样本文件。
- 真实登录 API 已确认目标手机号可登录到迁移后的 `userId=10007`，林夏档案和 3 张分享卡均可由同一 token 读取。

### 尚未完成的小程序人工验证

以下验证需要用户侧小程序登录后的人工操作，当前未由 Codex 独立完成：

- 在微信开发者工具或真机小程序打开「我的」和「我的作品集」，确认推广账号可用。

当前数据库事实已满足上述登录链路前置条件：`AuthServiceImpl.login(...)` 按 `user.phone` 查询，当前生产库目标手机号唯一未删除用户即 `userId=10007`。

已补充续验脚本能力：

- `send-code`：触发 `POST https://api.kplyyk.com/api/auth/sendCode`，只记录脱敏手机号和验证码请求状态。
- `api-verify`：从环境变量 `KP_BIND_LOGIN_CODE` 读取 6 位验证码，执行 `/api/auth/login`、`/api/user/me`、`/api/actor/profile/mine`、`/api/card/my-cards`，只记录 token 是否存在、用户 ID、档案名和卡片数量。本轮已通过。
- 续验脚本不会把 JWT、验证码或完整手机号写入样本文件。

### 回滚判断

- 当前数据库迁移、cleanup 和迁移后只读复核均通过。
- 未观察到需要回滚的数据库异常。
- 回滚表已按 `zz194_` 前缀保留在生产库；如后续真实登录或小程序人工复核失败，应先保留现场，再基于备份表执行回滚或补救 Spec。
