# 00-150 设计说明

## 分享偏好绑定

`actor_share_preference` 是当前分享卡个性化读取的强约束数据。修复方式不是在读取时默认 `miniProgramCard`，而是在写入链路保证绑定存在。

策略：

- `UserShareCardServiceImpl#createCard` 新建 `user_share_card` 后立即创建 `actor_share_preference`。
- 如果用户重复选择已存在 active 分享卡，通过创建入口复核偏好记录，缺失时写入真实绑定。
- `ActorPersonalizationServiceImpl` 继续保持缺失偏好即报错，避免掩盖数据污染。

## 数据迁移

新增迁移：

- 先备份 active 分享卡中缺失有效偏好的记录到 `zz_bak_20260426_023_share_card_missing_preference`。
- 再为缺失偏好的 active 分享卡补入 `preferred_artifact='miniProgramCard'`。

该迁移修复的是当前模型的必需绑定，不是旧代码兼容。

## 验证码弹窗

`sendCode` 后端响应的 `data` 是当前开发阶段验证码。登录页发送成功后使用 `uni.showModal`：

- 标题：`验证码发送成功`
- 内容：`验证码：{data}`
- 不显示取消按钮

## 审查

- 本地编译覆盖后端构造器注入和迁移语法基本校验。
- 小程序类型检查覆盖 `sendSmsCode` 返回值使用。
- 构建和包体审查确认 `dist/build/mp-weixin` 与 `dist/dev/mp-weixin` 已更新。
- 发布后用业务域名进行线上接口审查。
