# 00-149 旧 fortune/命理域物理下线需求

## 目标

按用户 2026-04-26 最新要求，删除旧框架遗留的 `fortune` / 命理 / 幸运色能力。该能力不再属于当前项目主线，不能通过兼容、兜底、改提示、隐藏入口等方式保留。

本轮目标是让线上 `https://kplyyk.com` 不再出现：

- `{"code":400,"message":"命理报告暂未生成完成","data":null}`
- `/api/fortune/*` 旧接口
- 小程序 `pkg-card/fortune/index` 旧页面
- 数据库 `fortune_report` 表和 `actor_share_preference.enable_fortune_theme` 字段
- `loadFortune`、`enableFortuneTheme`、`canApplyFortuneTheme`、`canUseLuckyColor` 等旧能力字段

## 范围

- 后端 API、Controller、Service、Mapper、DTO、Entity、OpenAPI。
- 数据库迁移与测试迁移清单。
- 小程序 API、类型、工具函数、页面、组件、路由、构建产物。
- 当前文档、SCE 当前主线说明、页面流转说明。
- 发布脚本与发布记录中的线上审查证据。

## 禁止项

- 禁止保留 `/api/fortune/report` 或 `/api/fortune/apply-lucky-color` 兼容接口。
- 禁止把旧接口改成返回其他业务错误作为“下线”。
- 禁止前端保留旧页面但隐藏入口。
- 禁止 `loadFortune`、`enableFortuneTheme`、`canApplyFortuneTheme`、`canUseLuckyColor` 字段继续参与请求、响应、类型或 UI。
- 禁止当前产品文档继续把命理描述为当前主线能力。
- 禁止未完成本地构建、残留审查、线上 OpenAPI/API 审查就标记完成。

## 验收标准

- 后端源码无 fortune 域 Controller、Service、Mapper、DTO、Entity。
- OpenAPI 不再暴露 `fortune`、`命理`、`幸运色`。
- 访问线上 `/api/fortune/report` 和 `/api/fortune/apply-lucky-color` 不得返回旧 400 文案，不得返回 500 以上错误。
- 数据库迁移先备份再物理删除 `fortune_report` 和 `actor_share_preference.enable_fortune_theme`。
- 小程序源码和构建产物无 fortune 页面、API、类型、工具函数、命理 UI 文案和旧能力字段。
- 后台管理源码无旧 fortune 字段或页面残留。
- 当前文档不再把命理作为当前主线，只允许历史 spec 中作为已退役历史存在。
- 内部审查评分必须达到 95 / 95；人工验收预留 5 分。

## 审查评分

- 后端 API 与 OpenAPI 清理：25 分。
- 数据库表字段备份后物理删除：20 分。
- 小程序页面、请求、类型、构建产物清理：25 分。
- 后台管理与当前文档清理：10 分。
- 本地构建、静态残留、线上模拟审查：15 分。

内部评分低于 95 分必须继续修改，不能收尾。
