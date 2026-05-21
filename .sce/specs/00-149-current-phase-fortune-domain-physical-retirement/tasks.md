# 00-149 任务清单

## 1. 后端清理

- [x] 删除 fortune Controller、DTO、Entity、Mapper、Service 源码。
- [x] 清理个性化服务中的 `loadFortune`、`fortuneProfile`、幸运色主题、命理关键词。
- [x] 清理能力响应中的 `canUseLuckyColor`、`canApplyFortuneTheme`。
- [x] 清理分享偏好中的 `enableFortuneTheme`。
- [x] 清理卡片配置服务中的 `applyLuckyColor`。
- [x] 清理迁移测试清单中的 `fortune_report`。

## 2. 数据库迁移

- [x] 新增迁移，备份 `fortune_report` 后物理删除。
- [x] 新增迁移，备份 `actor_share_preference.enable_fortune_theme` 后物理删除。
- [x] 本地编译确认迁移文件不会破坏启动期校验。

## 3. 小程序清理

- [x] 删除 fortune 页面、API、类型、工具函数。
- [x] 删除 `pages.json` 中 `pkg-card/fortune/index`。
- [x] 清理 personalization、theme、share artifact、level、capability、actor-card、profile detail 中旧字段。
- [x] 清理组件中的幸运色和命理关键词展示。
- [x] 构建后审查 `dist/build/mp-weixin` 与 `dist/dev/mp-weixin` 无旧内容。

## 4. 后台管理与文档

- [x] 后台管理源码确认无旧 fortune 残留。
- [x] 更新 `docs/product-design.md` 当前主线。
- [x] 更新 `docs/dev-playbook.md`、`.sce/steering/ENVIRONMENT.md`。
- [x] 更新 spec/code mapping 或执行记录。

## 5. 审查与发布

- [x] `mvn -q -DskipTests compile`。
- [x] `npm run type-check`。
- [x] `npm run build:mp-weixin`。
- [x] `npm run audit:mp-package`。
- [x] 源码关键词残留审查。
- [x] 构建产物关键词残留审查。
- [x] 执行数据库迁移发布。
- [x] 执行后端发布。
- [x] 线上 `https://kplyyk.com/api/v3/api-docs` 残留审查。
- [x] 线上 `/api/fortune/report`、`/api/fortune/apply-lucky-color` 旧接口审查。
- [x] 发布与审查结果写入记录。
