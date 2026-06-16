# 00-185 当前阶段同机测试 / 生产双环境治理 - 技术设计

## 1. 改动范围

| 层 | 文件 | 改动 |
|----|------|------|
| Runbook | `.sce/runbooks/backend-admin-release/same-host-dual-environment-runbook.md` | 新增同机双环境治理流程 |
| Runbook | `.sce/runbooks/backend-admin-release/production-release-runbook.md` | 补充生产发布前必须确认测试环境保留 |
| Runbook 索引 | `.sce/runbooks/backend-admin-release/README.md` | 登记双环境 runbook |
| SCE 索引 | `.sce/specs/README.md` | 登记 `00-185` |

本轮只写文档，不修改远端服务器和生产代码。

_Requirements: 3.1, 3.2, 3.3, 3.4_

## 2. 目标拓扑

| 项 | 测试环境 | 生产环境 |
|----|----|----|
| API 域名 | `test-api.kplyyk.com` | `api.kplyyk.com` |
| 管理端域名 | `test.kplyyk.com` | `kplyyk.com` |
| 后端 profile | `test` | `prod` |
| Nacos dataId | `kaipai-backend-test.yml` | `kaipai-backend-prod.yml` |
| 后端容器 | `kaipai-backend-test` | `kaipai-backend` |
| 后端端口 | `18080` | `8080` |
| 管理端静态目录 | `/opt/kaipai/nginx/html-test` | `/opt/kaipai/nginx/html` |
| 数据库 | `kaipai_test` | `kaipai_prod` |
| Redis | 独立 DB index 或独立实例 | 独立 DB index 或独立实例 |

说明：生产环境保留现有正式域名和默认后端服务名；测试环境新增独立名字和端口。这样生产域名语义清晰，测试环境也能继续保留。

_Requirements: 3.1_

## 3. 落地顺序

1. 只读盘点当前远端 compose、Nginx、容器、Nacos 与数据库。
2. 建立测试环境独立 Nacos dataId：`kaipai-backend-test.yml`。
3. 建立测试后端服务：`kaipai-backend-test` / `18080` / `SPRING_PROFILES_ACTIVE=test` / `NACOS_ENABLED=true`。
4. 建立测试 Nginx 域名：`test-api.kplyyk.com`、`test.kplyyk.com`。
5. 完成测试 smoke。
6. 切换生产环境到 `prod + Nacos`。
7. 执行生产后端和管理端发布。
8. 完成生产 smoke。
9. 分别写入测试与生产发布记录。

_Requirements: 3.2, 3.3, 3.4_

## 4. 发布记录规则

- 测试记录：`YYYYMMDD-HHMM-test-<scope>-<label>.md`
- 生产记录：`YYYYMMDD-HHMM-prod-<scope>-<label>.md`
- 生产记录必须包含“测试环境保留验证结果”。

_Requirements: 3.4_

## 5. 验证方案

本轮文档验证：

- 检查双环境 runbook 已创建并登记。
- 检查生产发布 runbook 已引用测试环境保留门禁。
- 检查文档未新增明文密钥。

后续真实落地验证：

- 测试域名 smoke 通过。
- 生产域名 smoke 通过。
- 容器 env 分别回读为 `test + Nacos` 与 `prod + Nacos`。
- Nacos dataId 分别可读。

_Requirements: 3.1, 3.2, 3.3, 3.4_
