# 00-149 执行记录

## 2026-04-26 任务建立

触发原因：

- 用户线上验收仍看到旧响应：`{"code":400,"message":"命理报告暂未生成完成","data":null}`。
- 该响应证明旧 `fortune` / 命理域仍在当前后端和线上 OpenAPI 中。
- 此前审查只覆盖局部分享卡流程，未覆盖旧域物理下线，审查口径错误。

本轮执行规则：

- 锁定目标为旧 `fortune` / 命理 / 幸运色域物理下线，不漂移到其他业务。
- 不做兼容接口，不做兜底提示，不保留隐藏页面。
- 先备份，再物理删除数据库表字段。
- 未完成本地构建、残留审查、线上模拟审查、发布记录前，不得标记完成。

## 初始残留确认

- 后端存在 `FortuneController`、`FortuneReportServiceImpl`，并抛出“命理报告暂未生成完成”。
- 后端 OpenAPI 暴露 `/fortune/report`、`/fortune/apply-lucky-color`。
- 数据库 baseline 存在 `fortune_report` 表和 `actor_share_preference.enable_fortune_theme` 字段。
- 小程序存在 `pkg-card/fortune/index`、`api/fortune.ts`、`types/fortune.ts`、`utils/fortune.ts`。
- 当前产品文档仍把命理驱动个性化描述为当前主线。

## 实施结果

后端删除内容：

- 删除旧 `fortune` Controller、DTO、Entity、Mapper、Service。
- 删除个性化链路中的 `loadFortune`、`fortuneProfile`、旧主题字段和旧关键词逻辑。
- 删除能力响应中的旧权限字段。
- 删除分享偏好和卡片配置中的旧开关与旧应用动作。
- 增加无路由异常映射，旧路径进入标准 404，不再被框架包装成 500。

数据库删除内容：

- 发布迁移 `V20260426_022__fortune_domain_physical_retirement.sql`。
- `fortune_report` 已备份到 `zz_bak_20260426_022_fortune_report` 后物理删除。
- `actor_share_preference.enable_fortune_theme` 已备份到 `zz_bak_20260426_022_actor_share_preference_enable_fortune_theme` 后物理删除。

小程序删除内容：

- 删除旧页面、API、类型和工具函数。
- 删除路由注册。
- 删除请求参数、响应类型、UI 组件和构建产物中的旧字段与旧文案。

当前文档清理：

- `docs/product-design.md` 不再把旧域描述为当前产品能力。
- `docs/dev-playbook.md` 不再把历史业务主线写成可沿用实现依据。
- 删除 `output/online-api-audit` 中 2026-04-26 早期失败审查 JSON，避免历史失败快照继续作为当前残留被误判。

## 发布记录

- 数据库迁移发布：`20260426-203604-backend-schema-fortune-domain-physical-retirement`。
- 后端发布：`20260426-203649-backend-only-fortune-domain-physical-retirement`。
- 404 修正后后端发布：`20260426-204246-backend-only-fortune-domain-physical-retirement-not-found-fix`。

## 本地审查

- `mvn -q -DskipTests compile`：通过。
- `npm run type-check`：通过。
- `npm run build:mp-weixin`：通过。
- `npm run audit:mp-package`：通过，主包和分包未超限。
- 运行时代码关键词审查：后端 Java、小程序 src、后台 src 无旧域命中。
- 小程序构建产物关键词审查：`dist/build/mp-weixin` 与 `dist/dev/mp-weixin` 无旧域命中。

## 线上审查

线上域名：`https://kplyyk.com`。

- `GET /api/v3/api-docs`：旧域关键词无命中。
- 登录态 `GET /api/fortune/report`：`HTTP 404`，响应 `{"code":404,"message":"接口不存在","data":null}`。
- 登录态 `POST /api/fortune/apply-lucky-color`：`HTTP 404`，响应 `{"code":404,"message":"接口不存在","data":null}`。
- 全量线上 OpenAPI 模拟审查：`totalOperations=161`，`serverFailureCount=0`，`businessCodeGte500WarningCount=0`。

## 数据库审查

线上结构核对：

```text
fortune_report_exists=0
enable_fortune_theme_exists=0
fortune_report_backup_exists=1
enable_fortune_theme_backup_exists=1
```

## 2026-04-26 20:48 追加核查

用户再次反馈仍看到：

```json
{"code":400,"message":"命理报告暂未生成完成","data":null}
```

复核结论：

- 该旧响应存在于早期 `output/online-api-audit` 失败审查 JSON，不存在于当前运行时代码、小程序构建产物和线上 OpenAPI。
- 已删除早期失败审查 JSON，保留最终无旧域命中的审查报告。
- 带 Token 访问线上旧路径已复核为 404，不再返回旧业务 400。

## 2026-04-26 20:53 最终复查

- `mvn -q -DskipTests compile`：通过。
- `npm run type-check`：通过。
- `npm run build:mp-weixin`：通过，并已同步到 `dist/dev/mp-weixin`。
- `npm run audit:mp-package`：通过，主包 `508.52 KB`，`pkg-card 111.58 KB`，`pkg-tools 28.21 KB`，均低于 `2 MB`。
- `rg` 复查后端 Java、小程序 src、后台 src、当前 docs、当前 output：旧域关键词无命中。
- `rg` 复查 `dist/build/mp-weixin`、`dist/dev/mp-weixin`：旧域关键词无命中。
- 重新拉取 `https://kplyyk.com/api/v3/api-docs` 后关键词审查：无命中。
- 重新执行线上全量 OpenAPI 模拟审查，报告 `output/online-api-audit/20260426-2053-fortune-domain-retirement-recheck.json`：

```json
{
  "totalOperations": 161,
  "serverFailureCount": 0,
  "businessCodeGte500WarningCount": 0,
  "failures": []
}
```

## 审查状态

当前状态：已完成。

内部审查评分：95 / 95。

不得降级说明：本轮没有新增兼容接口、兜底提示或旧页面隐藏保留；旧域以删除源码、删除路由、删除数据库表字段、发布线上验证的方式闭环。
