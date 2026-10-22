# 00-237 正式环境扩展迁移与原子切流 - 技术设计

_Requirements: 3.1-3.7, 4, 5_

## 1. Go/No-Go 前置卡

生产执行卡必须同时包含：

- `candidateId`、manifest SHA256。
- `00-236` 用户签署 GO 记录和验收证据 SHA256。
- 14 个 migration checksum。
- `00-233` media tool version/config hash。
- 目标环境摘要：`prod`、Nacos、`kaipai_prod`、prod Redis/COS。
- 备份路径、大小、SHA256、恢复负责人。
- 回切 upstream、旧容器、Nginx 备份路径。

缺一项就停止。

## 2. 生产备份与窗口

1. 通知发布窗口和冻结写入风险。
2. 记录当前容器/JAR/Nginx/Nacos 运行摘要。
3. 备份 `kaipai_prod`，验证 SHA256 和最小可读性。
4. 备份 compose/Nginx/当前 JAR/管理端目录。
5. 记录迁移前业务 baseline。

旧后端继续承接正式流量，生产备份使用一致性模式。

## 3. Schema 扩展迁移

通过 `00-232` runner 显式调用：

```text
--mysql-database kaipai_prod
```

逐文件：preflight -> apply -> object assertion -> history checksum。任何 partial/ambiguous 状态都进入停机决策，不自动 DROP。

生产迁移后重跑：

- 19 张表和字段。
- 索引/约束/seed。
- history 14 条和 checksum。
- 旧数据 count/hash/孤儿。

## 4. 生产媒体回填

按 `00-233` 先 dry-run 再 apply。生产 apply 必须确认：

- `environment=prod`。
- target bucket 与正式配置一致。
- candidate/manifest 一致。
- dry-run 报告中永久异常已裁决。

回填失败不影响旧后端继续读旧 URL，但不允许切换新后端/小程序，直到新 UI 的历史数据兼容结论清楚。

## 5. 候选后端

候选容器独立于旧 `kaipai-backend`：

- 使用同 JAR manifest SHA256。
- `SPRING_PROFILES_ACTIVE=prod`。
- `NACOS_ENABLED=true`。
- 连接 `kaipai_prod`。
- 使用候选端口（不占用正式监听）。

候选 smoke：API docs/health、后台登录、旧账号读取/保存不破坏、演员卡公开接口、旧分享接口、数据库连接池和关键日志无缺表/缺列。

## 6. Nginx 原子切流

1. 备份当前配置。
2. 写候选 API upstream 和管理端静态 root。
3. `nginx -t`。
4. 在本机/公网分别验证候选健康。
5. reload。
6. 验证正式 API、管理端首页、登录和公开分享。

若 API 与管理端需要分次切换，必须先切后端再切管理端，或保证旧管理端也可调用新后端；不允许先发布调用新接口的前端而后端尚未就绪。

## 7. 小程序 release

- 运行 `npm run build:mp-weixin:release`。
- 运行 `npm run audit:mp-package` 和项目专项 verify。
- 扫描产物：正式 API 存在，test/local API 不存在。
- 检查 `dist/build`/release 产物一致和 scoped hash 门禁。
- 上传微信开发者工具，提交正式版本。

后端已先完成兼容，因此旧线上小程序在正式小程序审核/发布期间仍可用。

## 8. 失败与回切

| 失败点 | 动作 |
|---|---|
| 备份/迁移失败 | 停止，保留旧后端，处理 schema 状态 |
| 回填失败 | 停止切流，旧后端继续运行 |
| 候选 smoke 失败 | 停止 upstream 切换，修复或回滚候选 |
| nginx -t 失败 | 不 reload，恢复配置 |
| 公网 smoke 失败 | 回切旧 upstream，保留证据 |
| 小程序上传/审核失败 | 保持后端新旧兼容，暂不影响线上旧版本 |

应用回切不恢复数据库。只有数据物理损坏且全部写入停止时，才进入灾难恢复流程。

## 9. 证据包

```text
.sce/runbooks/backend-admin-release/records/<release-id>/production-cutover/
```

记录 go/no-go 卡、备份 manifest、migration/history、media backfill、candidate smoke、Nginx config test/reload、公网 smoke 和最终状态。

## 10. 回滚边界

旧容器、旧 JAR、旧 Nginx 配置和旧管理端目录在 `00-238` 观察期结束前不得删除。新表/新列/新 asset 关系保留。
