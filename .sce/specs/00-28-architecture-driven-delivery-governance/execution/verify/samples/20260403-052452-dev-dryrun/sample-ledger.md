# 实名认证联调样本登记模板

## 1. 样本信息

- 验证日期：
- 环境：
- 操作人：
- 目标结论：
  - 提交
  - 拒绝
  - 重提
  - 通过

## 2. 样本主键

- userId：
- phone：
- firstVerificationId：
- retryVerificationId：

## 3. actor 侧证据

- 初始 `verify/status`：
- 首次提交返回状态：
- 拒绝后 `verify/status`：
- 二次提交返回状态：
- 最终 `verify/status`：
- 最终 `rejectReason`：
- 最终 `level/info.isCertified`：
- 最终 `profileCompletion`：

## 4. admin 侧证据

- 首次申请单是否查到：
- 首次申请单状态：
- 首次拒绝备注：
- 重提申请单是否查到：
- 重提申请单状态：
- 申请单总数：
- 是否保留首条拒绝记录：
- 是否生成新申请单：

## 5. 数据库证据

### `user`

- `user_id`：
- `real_auth_status`：

### `actor_profile`

- `user_id`：
- `real_name`：
- `is_certified`：

### `identity_verification`

- 首次申请单 `verification_id`：
- 首次申请单 `status`：
- 首次申请单 `reject_reason`：
- 重提申请单 `verification_id`：
- 重提申请单 `status`：
- 重提申请单 `reviewed_at`：

### `admin_operation_log`

- `reject` 日志：
- `approve` 日志：

## 6. 一致性检查

- 首次申请单已拒绝：是 / 否
- 重提申请单已通过：是 / 否
- 两条申请单主键不同：是 / 否
- actor 最终状态 = `user.real_auth_status`：是 / 否
- actor 最终状态 = `actor_profile.is_certified`：是 / 否
- 后台详情与 DB 是否一致：是 / 否

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

- 当前判定：
  - 未开始
  - 局部完成
  - 可继续联调
  - 闭环完成
- 一句话结论：
