# 00-149 设计说明

## 删除策略

旧 fortune 域采用物理删除，不做兼容层：

- 后端删除 `fortune` 包、`FortuneController`、命理 DTO、Entity、Mapper、Service。
- 分享个性化链路删除命理输入，主题 token 固定为当前风格与能力层级的基础主题。
- 能力分层删除幸运色、命理主题权限字段。
- 分享偏好只保留当前仍使用的产物偏好，不再保存命理主题开关。
- 小程序删除 fortune 路由和页面，所有请求不再携带 `loadFortune`。
- 组件删除命理关键词、幸运色一键应用入口。

## 数据库策略

执行新增迁移：

- 如果 `fortune_report` 表存在，复制到 `zz_bak_20260426_022_fortune_report`。
- 如果 `actor_share_preference.enable_fortune_theme` 字段存在，复制字段快照到 `zz_bak_20260426_022_actor_share_preference_enable_fortune_theme`。
- 备份后物理删除 `actor_share_preference.enable_fortune_theme`。
- 备份后物理删除 `fortune_report`。

迁移只用于删除旧域，不引入替代表或兜底字段。

## API 策略

- `/api/fortune/report` 和 `/api/fortune/apply-lucky-color` 从源码和 OpenAPI 中消失。
- 线上访问旧路径应进入框架标准无路由结果，不得返回旧业务错误，不得返回 500 以上错误。
- `/api/card/personalization` 响应不再包含 `fortuneProfile` 或命理偏好。
- `/api/actor/level` 相关响应不再包含幸运色、命理主题权限。

## 前端策略

- 删除 `pkg-card/fortune/index` 页面及 `pages.json` 注册。
- 删除 `api/fortune.ts`、`types/fortune.ts`、`utils/fortune.ts`。
- 删除所有 `loadFortune` 请求参数。
- 删除命理关键词、幸运色、命理主题文案。
- 构建后在 `dist/build/mp-weixin` 和 `dist/dev/mp-weixin` 中做关键词残留审查。

## 文档策略

当前文档必须描述最新主线：演员档案、风格详情、分享卡创建、公开卡片、收藏/作品集、后台管理与发布审查。

历史 fortune spec 可以作为历史记录保留，但当前文档和 steering 不得把它列为当前主线。
