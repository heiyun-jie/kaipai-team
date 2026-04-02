# 邀请裂变联调实际执行示例

## 1. 目的

这份文档只回答三件事：

1. `PowerShell` 采证脚本怎么跑
2. `SQL` 模板怎么填
3. 产物会落到哪里

适用对象分两类：

1. 已经拿到真实环境 `actor token / admin token` 的联调执行人
2. 需要用标准脚本自动登录、自动发现 invite 样本，再跑正式采证的执行人

优先使用自动脚本；只有在你已经拿到固定 token 或需要复用历史样本主键时，再回到手工 token 模式。

## 1.1 标准自动入口

如果当前环境允许使用固定开发账号登录，优先跑：

```powershell
python "D:\XM\kaipai-team\.sce\specs\00-28-architecture-driven-delivery-governance\execution\invite\run-authenticated-invite-sample.py" --label "remote-invite-auto"
```

自动脚本会完成：

- `admin/admin123` 后台登录
- `13800138000` 演员端验证码登录
- 自动读取当前演员 `inviteCode`
- 自动从后台发现最新 `referralId / inviteeUserId / grantId / policyId`
- 调用 `run-invite-validation.ps1` 生成正式采证目录
- 额外落盘 `auto-discovery.json` 与 `auto-discovery-summary.md`

如果本轮必须指定环境或强制锁定某条样本，也可以补参数：

```powershell
python "D:\XM\kaipai-team\.sce\specs\00-28-architecture-driven-delivery-governance\execution\invite\run-authenticated-invite-sample.py" `
  --label "remote-invite-auto" `
  --base-url "http://101.43.57.62/api" `
  --environment "dev" `
  --referral-id "8" `
  --policy-id "1"
```

## 1.2 手工 token 模式

## 2. 推荐先初始化样本目录

先用样本初始化脚本创建目录：

```powershell
powershell -ExecutionPolicy Bypass -File `
  "D:\XM\kaipai-team\.sce\specs\00-28-architecture-driven-delivery-governance\execution\invite\new-invite-validation-sample.ps1" `
  -SampleName "sample-a" `
  -EnvironmentName "dev" `
  -ApiBaseUrl "http://127.0.0.1:8010" `
  -InviteCode "KM7P4A" `
  -InviterUserId "101" `
  -InviteeUserId "208" `
  -ReferralId "5012" `
  -GrantId "9003" `
  -PolicyId "3"
```

初始化后，目录里会自动带上：

- `sample-ledger.md`
- `validation.sql`
- `run-capture.example.ps1`
- `sample-metadata.json`

## 3. 一条命令跑完整体流程

如果你已经拿到了 `actor token / admin token`，也可以直接用总控脚本：

```powershell
$actorToken = 'REPLACE_ACTOR_TOKEN'
$adminToken = 'REPLACE_ADMIN_TOKEN'

powershell -ExecutionPolicy Bypass -File `
  "D:\XM\kaipai-team\.sce\specs\00-28-architecture-driven-delivery-governance\execution\invite\run-invite-validation.ps1" `
  -SampleName "sample-a" `
  -EnvironmentName "dev" `
  -ApiBaseUrl "http://127.0.0.1:8010" `
  -ActorToken $actorToken `
  -AdminToken $adminToken `
  -InviteCode "KM7P4A" `
  -InviterUserId "101" `
  -InviteeUserId "208" `
  -ReferralId "5012" `
  -GrantId "9003" `
  -PolicyId "3"
```

总控脚本会自动：

- 初始化样本目录
- 复制并预填 `sample-ledger.md`
- 复制并预填 `validation.sql`
- 跑 actor / admin 关键接口采证
- 生成 `capture-summary.txt`
- 根据采证 JSON 自动回填 `sample-ledger.md` 的前台 / 后台字段
- 生成带抽取事实和交叉校验结果的 `validation-report.md`

## 4. 执行前准备

先准备 8 个值：

- `ApiBaseUrl`
- `ActorToken`
- `AdminToken`
- `InviteCode`
- `InviterUserId`
- `InviteeUserId`
- `ReferralId`
- `GrantId`

说明：

- `ApiBaseUrl` 传服务根地址即可，推荐传：
  - `http://127.0.0.1:8010`
  - 或外部域名根地址
- 如果你手里只有带 `/api` 的地址，例如 `http://127.0.0.1:8010/api`
  - 现在脚本也会自动兼容
- `PolicyId` 如果当轮要核对规则详情，也一并传入

## 5. PowerShell 执行示例

```powershell
$actorToken = 'REPLACE_ACTOR_TOKEN'
$adminToken = 'REPLACE_ADMIN_TOKEN'
$outputDir = 'D:\XM\kaipai-team\.sce\specs\00-28-architecture-driven-delivery-governance\execution\invite\captures\invite-20260402-sample-a'

powershell -ExecutionPolicy Bypass -File `
  "D:\XM\kaipai-team\.sce\specs\00-28-architecture-driven-delivery-governance\execution\invite\collect-invite-evidence.ps1" `
  -ApiBaseUrl "http://127.0.0.1:8010" `
  -ActorToken $actorToken `
  -AdminToken $adminToken `
  -InviteCode "KM7P4A" `
  -InviterUserId "101" `
  -InviteeUserId "208" `
  -ReferralId "5012" `
  -GrantId "9003" `
  -PolicyId "3" `
  -OutputDir $outputDir
```

也可以直接打开样本目录里的 `run-capture.example.ps1`，只补 token 后运行。

## 6. PowerShell 产物示例

执行完成后，输出目录下至少会出现：

- `capture-context.json`
- `capture-results.json`
- `capture-summary.txt`
- `sample-ledger.md`（已预填可确定的 API 字段）
- `validation.sql`
- `validation-report.md`（已汇总抽取事实与 API 侧一致性检查）

如果接口抓取成功，还会出现类似文件：

- `actor_invite_code.json`
- `actor_invite_stats.json`
- `actor_invite_records.json`
- `actor_invite_qrcode.json`
- `actor_level_info.json`
- `admin_referral_policies.json`
- `admin_referral_records_by_invite_code.json`
- `admin_referral_record_detail.json`
- `admin_referral_eligibility_detail.json`

判断方式：

- `capture-summary.txt` 里每一行都会标记 `[OK]` 或 `[ERROR]`
- 先看这里，不要一上来逐个翻 JSON

## 7. SQL 执行示例

脚本会自动把模板复制成输出目录下的 `validation.sql`。

执行前只改头部变量：

```sql
SET @invite_code = 'KM7P4A';
SET @inviter_user_id = 101;
SET @invitee_user_id = 208;
SET @referral_id = 5012;
SET @grant_id = 9003;
SET @policy_id = 3;
```

然后按目标环境执行整份 SQL。

优先使用标准脚本：

```powershell
python "D:\XM\kaipai-team\.sce\specs\00-28-architecture-driven-delivery-governance\execution\invite\run-remote-validation-sql.py" `
  --sample-dir "D:\XM\kaipai-team\.sce\specs\00-28-architecture-driven-delivery-governance\execution\invite\captures\invite-20260403-040007-remote-invite-e2e-closure-after-verify-fix"
```

脚本会：

- 上传同目录下的 `validation.sql`
- 通过标准 backend helper 在远端 `kaipai-mysql` 容器执行
- 把结果写回同目录下的 `validation-result.txt`

如果脚本当前不适用，再退回数据库客户端截图，但必须与同目录下的 `sample-ledger.md` 放在一起。

## 8. 推荐执行顺序

1. 先确认 [real-env-runtime-inventory.md](/D:/XM/kaipai-team/.sce/specs/00-28-architecture-driven-delivery-governance/execution/invite/real-env-runtime-inventory.md) 里的运行时值
2. 优先跑 `run-authenticated-invite-sample.py`
3. 如果自动脚本不适用，再回退到 `run-invite-validation.ps1`
4. 打开 `capture-summary.txt` 和 `validation-report.md`
5. 先复核 `sample-ledger.md` 里的自动回填字段是否与本轮样本一致
6. 再执行 `validation.sql`
7. 把 DB 结果补回 `sample-ledger.md`
8. 最后回填 [invite-status.md](/D:/XM/kaipai-team/.sce/specs/00-28-architecture-driven-delivery-governance/status/invite-status.md)

如果你只想先建目录、不想立即抓接口，再单独使用 `new-invite-validation-sample.ps1`。

## 9. 常见判断口径

### 可以接受

- `/api/invite/*` 抓取成功
- `/api/level/info` 抓取成功
- 后台记录 / 资格 / 规则详情能查到同一样本
- `validation.sql` 能把 `invite_code -> user -> referral_record -> grant` 串起来

### 不能误判为闭环完成

- 二维码接口虽然已返回真实二维码内容，但仍未验证是否满足微信官方小程序码要求
- `capture-summary.txt` 里只有 actor 侧成功，admin 侧失败
- `referral_record` 已存在，但 `grant` 没有同源关联
- 前台 `validInviteCount` 与 `/api/level/info inviteCount` 不一致

## 10. 本轮最小交付要求

一次真实环境 invite 联调，至少要提交这 4 类证据：

- `capture-summary.txt`
- `validation-report.md`
- 至少 1 份 actor 侧 JSON
- 至少 1 份 admin 侧 JSON
- 1 份 SQL 结果或截图

如果这四类证据都没有，就还不算进入真实闭环验证。
