# 00-194 当前阶段生产林夏测试账号迁移与手机号绑定 - 技术设计

## 1. 范围

_Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6_

本轮最终执行生产数据迁移与绑定。最初按单库手机号绑定设计，但只读 precheck 发现当前生产库没有林夏资产，旧线上库 `kaipai_dev` 才存在目标林夏账号。因此执行入口调整为：

| 层 | 文件 / 入口 | 策略 |
|----|-------------|------|
| SCE 记录 | `.sce/specs/00-194-current-phase-production-linxia-test-account-phone-binding/` | 固化需求、设计、任务和执行结果 |
| 执行脚本 | `scripts/run-production-linxia-phone-binding.py` | 使用远端 backend helper 执行 MySQL migration-precheck / migration-apply / cleanup，并提供真实登录 API 续验模式 |
| 源库 | `kaipai_dev` | 旧线上林夏账号及资产事实源，只读 |
| 目标库 | `kaipai_prod` | 当前生产库，备份空壳账号后迁入源账号资产 |
| 资产域 | `user_share_card` 等 | 按原主键迁入直接资产，避免重写外键 |

不修改 `kaipaile-server`、`kaipai-frontend` 或 `kaipai-admin` 运行时代码。

## 2. 数据事实源

_Requirements: 3.3, 3.4, 3.5_

当前后端登录链路事实：

- `AuthServiceImpl.login(...)` 使用 `user.phone` 查询登录账号。
- `AuthServiceImpl.loginByWechat(...)` 通过小程序手机号授权拿到手机号后，同样使用 `user.phone` 查询或注册。
- `JwtUtil.generateToken(...)` 把 `userId` 作为 subject，`phone` 只是 token claim。
- `ActorProfileServiceImpl.buildProfile(...)` 对联系手机号使用 `actor_profile.phone`，再兜底 `user.phone`。

因此本轮必须至少对齐：

- `user.phone`
- `user.account`（仅当原值为空或等于旧手机号）
- `actor_profile.phone`

迁移采用保留原主键策略，迁入：

- `user_share_card.user_id`
- `user_share_card.actor_profile_id`
- `actor_card_config.share_card_id`
- `actor_share_preference.share_card_id`
- `identity_verification.user_id`
- `identity_verification_owner.user_id`
- `invite_code.user_id`
- `referral_record.inviter_user_id / invitee_user_id`
- `capability_account.user_id`
- `capability_change_log.user_id`
- `user_entitlement_grant.user_id`
- `actor_ai_profile_card_task.user_id / actor_profile_id / share_card_id`
- `actor_ai_profile_card_page.task_id / share_card_id`
- `share_card_contact_request.share_card_id`
- `share_card_view_history.share_card_id`

原因：这些资产在旧线上本来就归属于 `userId=10007 / actorProfileId=10010 / shareCardId` 主键集合，保留主键迁移可以避免重写分享卡、配置、AI 页面和历史记录关系。

## 3. 脚本输入

_Requirements: 3.1, 3.2_

脚本不接受完整手机号作为命令行参数，避免进入 shell history。完整手机号通过环境变量注入：

```powershell
$env:KP_BIND_TARGET_PHONE = "<target-phone>"
```

源账号锚点默认为 `source_user_id=10007`；如需覆盖，使用：

```powershell
$env:KP_BIND_SOURCE_USER_ID = "<linxia-user-id>"
```

只读迁移预检：

```powershell
python .sce/specs/00-194-current-phase-production-linxia-test-account-phone-binding/scripts/run-production-linxia-phone-binding.py `
  --mode migration-precheck `
  --operator codex `
  --source-database kaipai_dev `
  --mysql-database kaipai_prod
```

只有 `migration-precheck` 通过后才允许执行：

```powershell
python .sce/specs/00-194-current-phase-production-linxia-test-account-phone-binding/scripts/run-production-linxia-phone-binding.py `
  --mode migration-apply `
  --operator codex `
  --source-database kaipai_dev `
  --mysql-database kaipai_prod
```

数据库迁移完成后，可在用户确认能接收短信验证码时执行真实登录续验：

```powershell
python .sce/specs/00-194-current-phase-production-linxia-test-account-phone-binding/scripts/run-production-linxia-phone-binding.py `
  --mode send-code `
  --operator codex
```

收到验证码后只通过环境变量注入，不写入命令行：

```powershell
$env:KP_BIND_LOGIN_CODE = "<sms-code>"
python .sce/specs/00-194-current-phase-production-linxia-test-account-phone-binding/scripts/run-production-linxia-phone-binding.py `
  --mode api-verify `
  --operator codex
```

## 4. Migration Precheck SQL 设计

_Requirements: 3.1, 3.2, 3.5_

脚本会生成临时 SQL 并上传到远端执行，SQL 内容不落本地仓库。migration-precheck 只读：

1. 校验 `KP_BIND_TARGET_PHONE` 为 11 位手机号。
2. 校验源库 `kaipai_dev.user_id=10007`：
   - `user.phone` 等于目标推广手机号
   - 演员身份、未删除
   - 有 1 个有效演员档案
   - 命中「林夏」名称条件
   - 分享卡数量不小于 1
3. 校验目标库 `kaipai_prod`：
   - 目标手机号有效用户数量为 1
   - 该用户资产计数为 0，可视为空壳账号
   - 源账号相关主键在目标库无冲突
4. 输出：
   - `TARGET_PHONE_MASK`
   - `SOURCE_USER_ID`
   - `SOURCE_ACTOR_PROFILE_ID`
   - 各源表资产计数
   - `TARGET_EMPTY_USER_ID`
   - `TARGET_EMPTY_USER_ASSET_COUNT`
   - 各目标表主键冲突计数

任何门禁失败时，migration-precheck 退出非 0，并在样本目录写入脱敏摘要。

## 5. Migration Apply SQL 设计

_Requirements: 3.3, 3.4, 3.6_

migration-apply 会重新执行同一套门禁，然后在单事务中执行：

1. 创建备份表：
   - `zz194_<table-alias>_<timestamp>`
2. 备份：
   - 当前生产空壳账号及相关目标表可能受影响行
   - 目标库中源主键可能冲突行（应为空，作为防线）
3. 软删除生产空壳账号：
   - `deleted = 1`
   - `phone = archived-00-194-<userId>-<targetPhone>`
   - `account = archived-00-194-<userId>-<targetPhone>`
4. 从源库按原主键插入林夏账号和直接资产。
   - 插入时通过 `information_schema.COLUMNS` 计算源库 / 目标库共同列，避免旧线上库与当前生产库列数不一致导致 `INSERT ... SELECT *` 失败。
5. 提交前校验：
   - 软删除空壳账号 1 行
   - 插入源 `user` 1 行
   - 迁入档案、分享卡数量与源库一致
   - 目标手机号未删除用户数量为 1
6. 提交后输出脱敏结果、插入行数和备份表前缀。

如果事务内任一门禁失败，使用 `SIGNAL SQLSTATE '45000'` 中止，不会执行 UPDATE。

## 6. 验证设计

_Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

验证顺序：

1. `migration-precheck` 返回 `passed`。
2. `migration-apply` 返回 `passed`。
3. 迁移完成后执行 `diagnose / inventory / roster`，确认：
   - 当前生产目标手机号未删除用户为 `userId=10007`。
   - 当前生产 `actor_profile` 数量为 1。
   - 当前生产 `user_share_card` 数量为 3。
   - 当前生产分享配置、偏好、实名、邀请、能力和 AI 资产计数与源库预检一致。
4. 执行 `cleanup`，删除迁移过程中创建的临时存储过程 `kp_194_insert_common_columns`。
5. 使用目标手机号走真实小程序登录或脚本 API 续验：
   - `POST /api/auth/sendCode`
   - 输入收到的验证码登录
   - `GET /api/user/me`
   - `GET /api/actor/profile/mine`
   - `GET /api/card/my-cards`
   - 脚本只记录 token 是否存在、用户 ID、档案名和卡片数量，不记录 JWT、验证码或完整手机号。
6. 小程序人工复核：
   - 「我的」页显示林夏账号状态。
   - 「我的作品集」仍可进入。
   - 首页或风格详情可继续打开已有分享页。

## 7. 回滚设计

_Requirements: 3.6_

如登录验证异常，按 apply 输出的 `zz194_` 备份表回滚。回滚原则：

- 先备份当前生产现场，不直接覆盖本轮备份表。
- 删除或软删除本轮按原主键迁入的 `userId=10007 / actorProfileId=10010 / shareCardId` 相关资产。
- 从 `zz194_usr_<timestamp>` 恢复原生产空壳账号 `userId=5` 的 `deleted / phone / account / status` 等字段。
- 回滚后再次执行 `diagnose / inventory / roster`，确认目标手机号恢复到回滚预期状态。

回滚 SQL 不在本轮直接落库执行；如后续真实登录或小程序人工复核失败，应先保留现场，再另建回滚执行记录或补救 Spec。
