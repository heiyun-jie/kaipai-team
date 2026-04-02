# 实名认证联调样本登记模板

## 1. 样本信息

- 验证日期：2026-04-03
- 环境：dev
- 操作人：REPLACE_OPERATOR
- 目标结论：
  - 提交
  - 拒绝
  - 重提
  - 通过

## 2. 样本主键

- userId：10021
- phone：13903054934
- firstVerificationId：12
- retryVerificationId：13

## 3. actor 侧证据

- 初始 `verify/status`：见 action captures
- 首次提交返回状态：rejected
- 拒绝后 `verify/status`：rejected
- 二次提交返回状态：approved
- 最终 `verify/status`：approved
- 最终 `rejectReason`：--
- 最终 `level/info.isCertified`：True
- 最终 `profileCompletion`：95

## 4. admin 侧证据

- 首次申请单是否查到：是
- 首次申请单状态：rejected
- 首次拒绝备注：spec verify reject first pass
- 重提申请单是否查到：是
- 重提申请单状态：approved
- 申请单总数：2
- 是否保留首条拒绝记录：是
- 是否生成新申请单：是

## 5. 数据库证据

### `schema_release_history`

- `V20260403_001__identity_verification_resubmit_history.sql` 是否存在：是
- schema 发布记录 `release_id`：20260403-054130-backend-schema-verify-resubmit-history-fix

### `user`

- `user_id`：10021
- `real_auth_status`：2

### `actor_profile`

- `user_id`：10021
- `real_name`：测试4934
- `is_certified`：True

### `identity_verification`

- 首次申请单 `verification_id`：12
- 首次申请单 `status`：3
- 首次申请单 `reject_reason`：spec verify reject first pass
- 重提申请单 `verification_id`：13
- 重提申请单 `status`：2
- 重提申请单 `reviewed_at`：2026-04-02 21:49:36

### `identity_verification_owner`

- `owner_id`：5
- `user_id`：10021
- `id_card_hash`：b3d1bb9f35f920eeae0cfff51e2da464f520d950c78183952298927274334751

### `admin_operation_log`

- `reject` 日志：operation_log_id=37, target_id=12, operation_result=1, create_time=2026-04-02 21:49:35
- `approve` 日志：operation_log_id=38, target_id=13, operation_result=1, create_time=2026-04-02 21:49:36

## 6. 一致性检查

- 首次申请单已拒绝：是
- 重提申请单已通过：是
- 两条申请单主键不同：是
- actor 最终状态 = `user.real_auth_status`：是
- actor 最终状态 = `actor_profile.is_certified`：是
- 后台详情与 DB 是否一致：是

## 7. 缺陷归因

### 前端

-

### 后端

-

### 后台

-

### 环境 / 配置

-

## 8. 本轮结论

- 当前判定：闭环完成
- 一句话结论：同一样本 userId=10021（尾号 4934）已完成拒绝后重提再通过闭环；DB 已回读 release_id=20260403-054130-backend-schema-verify-resubmit-history-fix、owner.user_id=10021、verification_id=12/13，首单拒绝=是，重提通过=是。
