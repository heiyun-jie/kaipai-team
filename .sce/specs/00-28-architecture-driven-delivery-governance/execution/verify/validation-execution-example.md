# 实名认证联调执行示例

## 1. 推荐自动入口

优先使用标准自动链：

```powershell
python "D:\XM\kaipai-team\.sce\specs\00-28-architecture-driven-delivery-governance\execution\verify\run-end-to-end-verify-closure.py" --label "remote-verify-reject-retry-approve"
```

自动脚本会完成：

- `admin/admin123` 后台登录
- 自动创建新的 actor 样本账号
- 自动补齐 actor 档案，使 `profileCompletion >= 70`
- 自动执行 `提交 -> 拒绝 -> 重提 -> 通过`
- 自动生成正式样本目录
- 自动调用 `run-verify-validation.ps1` 生成 `validation-report.md`

## 2. 手工 token 模式

如果本轮已经固定好了 `userId / verificationId`，也可以直接跑：

```powershell
$actorToken = 'REPLACE_ACTOR_TOKEN'
$adminToken = 'REPLACE_ADMIN_TOKEN'

powershell -ExecutionPolicy Bypass -File `
  "D:\XM\kaipai-team\.sce\specs\00-28-architecture-driven-delivery-governance\execution\verify\run-verify-validation.ps1" `
  -SampleName "sample-a" `
  -EnvironmentName "dev" `
  -ApiBaseUrl "http://101.43.57.62" `
  -ActorToken $actorToken `
  -AdminToken $adminToken `
  -UserId "10018" `
  -VerificationId "21" `
  -RetryVerificationId "22"
```

## 3. DB 回读

自动或手工样本完成后，再执行：

```powershell
python "D:\XM\kaipai-team\.sce\specs\00-28-architecture-driven-delivery-governance\execution\verify\run-remote-validation-sql.py" `
  --sample-dir "D:\XM\kaipai-team\.sce\specs\00-28-architecture-driven-delivery-governance\execution\verify\samples\20260403-000000-dev-sample-a"
```

脚本会：

- 上传当前样本目录下的 `validation.sql`
- 通过标准 backend helper 在远端 `kaipai-mysql` 容器执行
- 把结果写回 `validation-result.txt`
- 自动回填 `sample-ledger.md / validation-report.md` 里的数据库证据与一致性检查

## 4. 最小交付

一次 verify 真实联调，至少要补齐：

- `capture-summary.txt`
- `validation-report.md`
- 两条审核详情 JSON
- `validation-result.txt`
- `sample-ledger.md`
