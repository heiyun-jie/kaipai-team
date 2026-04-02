# 实名认证真实环境证据包要求

## 1. 最低必交

每次 verify 真实环境联调，至少要提交以下 5 类证据：

1. actor 侧最终状态 JSON
2. admin 侧两条审核详情 JSON
3. `capture-summary.txt`
4. `validation-report.md`
5. `validation-result.txt` 或同等级数据库回读

## 2. 推荐证据结构

### actor 侧

- `actor_verify_status_initial.json`
- `actor_verify_submit_first.json`
- `actor_verify_status_after_reject.json`
- `actor_verify_submit_second.json`
- `actor_verify_status_final.json`
- `actor_level_info_final.json`

### admin 侧

- `admin_verify_list_after_first_submit.json`
- `admin_verify_detail_first.json`
- `admin_verify_reject_first.json`
- `admin_verify_list_after_resubmit.json`
- `admin_verify_detail_retry.json`
- `admin_verify_approve_retry.json`
- `admin_verify_list_final.json`

### 汇总

- `capture-context.json`
- `capture-results.json`
- `capture-summary.txt`
- `sample-ledger.md`
- `validation-report.md`
- `validation.sql`
- `validation-result.txt`

## 3. 不能替代的证据

- 不能只拿 invite 闭环样本里的 `isCertified=true` 侧证 verify 完成
- 不能只拿后台列表截图代替两条申请单详情
- 不能只拿接口 `200` 代替状态流转验证
