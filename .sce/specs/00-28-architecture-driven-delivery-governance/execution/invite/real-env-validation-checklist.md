# 邀请裂变真实环境闭环验证清单

## 1. 目标

把当前“局部完成”的邀请链路，收口成一条可重复验证的真实环境样本链：

`邀请码生成 -> 注册绑定 -> referral_record 生成 -> 风险 / 资格流转 -> 前台 invite / level 状态同步`

本清单只负责真实环境验证与证据回填，不负责补做功能。

## 2. 验证前置

### 2.1 运行时确认

- 先确认当前验证环境是同一套运行时，不允许只看某一个配置文件
- 必查项：
  - DB
  - Redis
  - profile
  - 启动脚本
  - 反向代理目标
- 结论必须写清楚当前环境名称、服务地址、管理后台地址、小程序请求域名

### 2.2 账号与角色

- 准备 1 个邀请人账号：已实名、可正常进入小程序邀请页
- 准备 2 个被邀请账号：
  - 样本 A：正常链路样本
  - 样本 B：风险链路样本
- 准备 1 个后台账号：至少具备邀请记录、异常邀请、邀请规则、邀请资格四类权限
- `2026-04-03` 起，若使用标准开发样本，可直接优先执行 `run-authenticated-invite-sample.py` 自动完成 `admin / actor` 登录与样本主键发现

### 2.3 记录规范

- 每次验证必须固定记录同一组样本 ID：
  - inviterUserId
  - inviteCode
  - inviteeUserId
  - referralId
  - grantId
- 每一轮验证至少保留 4 类证据：
  - 小程序页面截图
  - 后台页面截图
  - API 响应
  - DB 查询结果

## 3. 主链路验证

### 3.1 邀请码生成

- 小程序入口：
  - `kaipai-frontend/src/pkg-card/invite/index.vue`
- 需要确认：
  - 页面能显示邀请码
  - 页面能生成邀请链接
  - 页面能拉取二维码或明确命中 fallback
- 记录证据：
  - invite 页面截图
  - `/api/invite/code` 或兼容接口响应
  - `/api/invite/qrcode` 或兼容接口响应

### 3.2 注册绑定

- 使用样本 A 通过 `inviteCode` 或 `scene` 进入注册链路
- 需要确认：
  - 登录页正确承接 `inviteCode`
  - 注册成功后没有丢失邀请关系
  - 注册请求包含 `deviceFingerprint`
- 记录证据：
  - 登录页携参截图
  - 注册成功后的用户 ID
  - 注册接口请求 / 响应摘要

### 3.3 数据落库

- 必查表：
  - `user`
  - `referral_record`
  - `user_entitlement_grant`
- 核对项：
  - `user.invitedByUserId` 是否等于邀请人 ID
  - `referral_record.inviterUserId / inviteeUserId / inviteCode / status / riskFlag` 是否与样本一致
  - 若触发资格，`user_entitlement_grant.userId / sourceType / sourceRefId / status` 是否与同一样本一致
- 结论必须能回答：
  - 邀请关系是否只绑定一次
  - 邀请记录是否已生成
  - 资格记录是否来自同一条邀请事实链

## 4. 后台治理验证

### 4.1 邀请记录页

- 后台入口：
  - `/referral/records`
- 需要确认：
  - 可按 `inviteCode / inviterUserId / inviteeUserId` 查到样本
  - 详情字段与 DB 一致

### 4.2 邀请规则页

- 后台入口：
  - `/referral/policies`
- 需要确认：
  - 当前生效策略可见
  - 可创建一条测试策略但不直接污染正式规则
  - 启用 / 停用、门槛、自动发放配置会真实影响后续验证样本

### 4.3 异常邀请页

- 后台入口：
  - `/referral/risk`
- 使用样本 B 制造风险条件：
  - 同设备重复注册
  - 同小时高频邀请
- 需要确认：
  - 风险记录能进入后台
  - 通过 / 作废 / 复核完成动作能真实改动记录状态

### 4.4 邀请资格页

- 后台入口：
  - `/referral/eligibility`
- 需要确认：
  - 自动发放或手工发放后的资格可查
  - 撤销 / 延期后状态变化可回看
  - `grantId` 能回溯到同一用户样本

## 5. 前台同步验证

### 5.1 邀请页

- 需要确认：
  - 邀请人数与后台有效记录一致
  - 风险作废后计数会回退或保持正确

### 5.2 等级 / 会员摘要

- 入口：
  - `kaipai-frontend/src/pkg-card/membership/index.vue`
  - `/level/info`
- 需要确认：
  - 登录态恢复后，邀请态 / 认证态 / 等级态会同步刷新
  - 邀请资格变化后，前台能力摘要与后台资格记录一致

### 5.3 名片 / 分享产物

- 需要确认：
  - 名片页或分享页引用的邀请码仍是当前用户真实邀请码
  - 不出现旧邀请码、空二维码、硬编码门槛文案残留

## 6. 判定标准

### 6.1 可以判定“后台治理入口已补齐”

- 记录页、规则页、异常邀请页、资格页都可打开
- 查询、详情、动作按钮和权限码一致
- `kaipai-admin` 已通过 `npm run type-check`

### 6.2 仍只能判定“局部完成”

满足以下任一条，即不能宣告邀请闭环完成：

- 真实环境没有跑通同一样本链
- `user.invitedByUserId` 与 `referral_record` 对不上
- `referral_record` 与 `user_entitlement_grant` 对不上
- 当前真实样本只证明 `/invite/code`、`/invite/qrcode`、`/invite/stats`、`/invite/records`、后台记录 / 风险 / 策略接口返回正常，但 `eligibility` 仍查不到同源 `grant`
- 后台动作后前台状态没有同步
- 二维码虽已返回真实邀请码链接二维码内容，但业务要求微信官方小程序码且未完成真实扫码验证

### 6.3 可以升级为“闭环完成”

- 样本 A 正常链路走通
- 样本 B 风险链路走通
- 后台策略、风险、资格动作都能稳定反映到前台
- 同一邀请码样本在 DB、后台、前台三端口径一致

## 7. 回填模板

每次验证结束后，按下面结构回填到 `status/invite-status.md`：

```md
### YYYY-MM-DD（联调回填）

- 当前判定：`局部完成` / `闭环完成`
- 样本：
  - inviterUserId:
  - inviteCode:
  - inviteeUserId:
  - referralId:
  - grantId:
- 已确认：
  - 
- 未确认：
  - 
- 缺陷归因：
  - 前端：
  - 后端：
  - 后台：
```
