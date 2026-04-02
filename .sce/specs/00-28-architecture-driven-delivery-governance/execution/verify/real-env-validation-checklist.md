# 实名认证真实环境验证清单

## 1. 运行时前置

- [ ] 已确认后端真实入口
- [ ] 已确认当前运行时仍是 `dev + Nacos`
- [ ] 已确认 `/api/v3/api-docs` 可读
- [ ] 已确认 admin 登录态具备 `page.verify.*` 与 `action.verify.*`
- [ ] 已确认小程序 `VITE_USE_MOCK=false`
- [ ] 已确认小程序 `VITE_API_BASE_URL` 非空

## 2. 样本前置

- [ ] 本轮样本使用单一 `userId`
- [ ] 该用户当前不是已实名通过状态
- [ ] 该用户 `profileCompletion >= 70`
- [ ] 已固定本轮 `firstVerificationId`
- [ ] 已固定本轮 `retryVerificationId`

## 3. 流程验证

- [ ] actor 首次 `POST /verify/submit` 返回 `code=200`
- [ ] admin `GET /admin/verify/list` 可查到第一条待审核记录
- [ ] admin `POST /admin/verify/{id}/reject` 返回 `code=200`
- [ ] actor `GET /verify/status` 可看到 `status=3`
- [ ] actor 第二次 `POST /verify/submit` 返回 `code=200`
- [ ] admin `GET /admin/verify/list` 可同时查到两条记录
- [ ] admin `POST /admin/verify/{retryId}/approve` 返回 `code=200`
- [ ] actor `GET /verify/status` 最终返回 `status=2`
- [ ] actor `GET /level/info` 最终返回 `isCertified=true`

## 4. 一致性验证

- [ ] 第一条申请单状态为拒绝
- [ ] 第一条申请单 `rejectReason` 与后台拒绝备注一致
- [ ] 第二条申请单状态为通过
- [ ] 第二条申请单 `verificationId` 与第一条不同
- [ ] `user.real_auth_status=2`
- [ ] `actor_profile.is_certified=1`
- [ ] `admin_operation_log` 中存在 `verify/reject`
- [ ] `admin_operation_log` 中存在 `verify/approve`

## 5. 交付物

- [ ] `capture-summary.txt`
- [ ] `validation-report.md`
- [ ] `sample-ledger.md`
- [ ] `validation.sql`
- [ ] `validation-result.txt` 或同等级 DB 证据
