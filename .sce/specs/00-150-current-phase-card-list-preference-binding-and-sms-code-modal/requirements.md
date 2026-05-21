# 00-150 分享页下一步偏好绑定与验证码弹窗需求

## 目标

修复用户 2026-04-26 验收发现的两个当前阻断问题：

- `pkg-card/card-list/index` 点击“下一步”进入预览页时，不得弹出 `分享偏好未绑定`。
- `https://kplyyk.com/api/auth/sendCode` 返回 `验证码发送成功` 时，弹窗必须展示响应 `data` 中的验证码。

## 范围

- 小程序登录页验证码发送成功交互。
- 分享卡创建链路的后端数据绑定。
- 已存在缺失分享偏好的线上数据修复迁移。
- 本地编译、类型检查、小程序构建、线上 API 审查与发布记录。

## 禁止项

- 禁止在 `ActorPersonalizationService` 读取时用默认值兜底。
- 禁止前端吞掉 `分享偏好未绑定` 后假装成功。
- 禁止只改提示文案不修数据绑定。
- 禁止未发布后端和数据库迁移就标记线上通过。

## 验收标准

- 新创建分享卡必须同时创建 `actor_share_preference`。
- 已存在 active 分享卡缺失 `actor_share_preference` 的线上数据必须通过迁移修复，并备份缺失样本。
- `pkg-card/card-list/index` 下一步进入 `pkg-card/actor-card/index` 时，`/api/card/personalization` 不返回 `分享偏好未绑定`。
- 登录页发送验证码成功后，弹窗内容包含后端返回的验证码。
- 本地 `mvn -q -DskipTests compile`、`npm run type-check`、`npm run build:mp-weixin`、`npm run audit:mp-package` 通过。
- 线上模拟审查不得出现 500 以上错误。

## 审查评分

- 后端创建链路严格绑定：30 分。
- 数据迁移修复线上缺失偏好：25 分。
- 登录页验证码弹窗展示 `data`：15 分。
- 本地构建与类型审查：15 分。
- 线上发布后 API 审查：10 分。

内部评分低于 95 分必须继续修改，不能收尾。
