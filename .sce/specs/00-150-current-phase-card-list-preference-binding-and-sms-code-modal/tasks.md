# 00-150 任务清单

## 1. 后端

- [x] 创建分享卡时写入 `actor_share_preference`。
- [x] 已存在 active 分享卡通过创建入口复核偏好绑定。
- [x] 保持个性化读取强校验，不增加读取兜底。

## 2. 数据库

- [x] 新增迁移，备份缺失偏好的 active 分享卡。
- [x] 新增迁移，补齐缺失的 `actor_share_preference`。

## 3. 小程序

- [x] 登录页验证码发送成功弹窗展示响应 `data`。
- [x] 重新构建并同步 `dist/dev/mp-weixin`。

## 4. 审查与发布

- [x] `mvn -q -DskipTests compile`。
- [x] `npm run type-check`。
- [x] `npm run build:mp-weixin`。
- [x] `npm run audit:mp-package`。
- [x] 数据库迁移发布。
- [x] 后端发布。
- [x] 线上 `sendCode` 审查。
- [x] 线上分享卡创建到个性化读取审查。
- [x] 审查结果写入执行记录。
