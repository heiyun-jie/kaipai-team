# 00-184 当前阶段生产环境发布运维流程 - 技术设计

## 1. 改动范围

| 层 | 文件 | 改动 |
|----|------|------|
| Runbook | `.sce/runbooks/backend-admin-release/production-release-runbook.md` | 新增生产发布流程 |
| Runbook 索引 | `.sce/runbooks/backend-admin-release/README.md` | 登记生产发布入口 |
| SCE 索引 | `.sce/specs/README.md` | 登记 `00-184` |

不修改生产代码、不修改发布脚本、不执行发布动作。

_Requirements: 3.1, 3.2, 3.3_

## 2. Runbook 结构

新增文档采用以下结构：

1. 适用范围与核心结论
2. 生产环境基线
3. 发布前门禁
4. 后端生产发布流程
5. 管理端生产发布流程
6. backend+admin 联合发布顺序
7. 生产 smoke 清单
8. 回滚流程
9. 发布记录模板
10. 中止条件

_Requirements: 3.1_

## 3. 关键规则

文档必须明确：

- 同一份 Spring Boot JAR 多环境复用。
- 本地打包验证可执行 `kaipaile-server/scripts/package-backend.ps1 -Environment prod -SkipTests`。
- 真正线上生效取决于远端运行环境：
  - `SPRING_PROFILES_ACTIVE=prod`
  - `NACOS_ENABLED=true`
- 生产 Nacos 目标 dataId：
  - `kaipai-backend-prod.yml`
  - `DEFAULT_GROUP`
- 生产公网 smoke 默认：
  - API：`https://api.kplyyk.com`
  - 管理端：`https://kplyyk.com`

_Requirements: 3.1, 3.3_

## 4. 验证方案

- 静态检查新增文档存在并可读。
- 静态检查 README 与 Spec 索引已登记。
- 检查新增文档不新增真实密钥。

_Requirements: 3.2, 3.3_
