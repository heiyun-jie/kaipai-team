# 00-184 当前阶段生产环境发布运维流程

## 1. 概述

当前后端已支持通过 `SPRING_PROFILES_ACTIVE` 与 `NACOS_ENABLED` 做环境切换，并已具备 `prod + Nacos` 的本地打包验证入口。下一步准备发布生产环境时，需要把“生产发布前置检查、远端运行环境切换、后端 / 管理端发布、smoke、回滚与留档”固化成运维文档，避免发布时只打包但没有切换远端运行环境。

本 Spec 只负责创建生产发布运维流程文档，不实际执行生产发布。

## 2. 用户故事

作为发布操作人，我希望按一份文档执行生产发布，知道每一步的命令、检查点和中止条件。

作为维护者，我希望生产发布记录能明确区分“本地打包验证成功”和“远端运行环境已切到 prod”，避免误把构建结果当成线上生效。

作为项目负责人，我希望生产发布有可追溯的 Nacos、compose/env、产物、smoke 与回滚记录。

## 3. 功能需求

### 3.1 新增生产发布 runbook

**描述**：在 `.sce/runbooks/backend-admin-release/` 下新增生产发布运维流程文档，覆盖后端、管理端、Nacos、compose/env、smoke、回滚与记录。

**验收标准**：

- WHEN 阅读 runbook THEN 能明确生产发布入口、前置门禁、执行顺序和回滚方式。
- WHEN 后端发布到生产 THEN 文档明确要求远端 `SPRING_PROFILES_ACTIVE=prod`、`NACOS_ENABLED=true`。
- WHEN 后端使用 Nacos THEN 文档明确要求只读核验 `kaipai-backend-prod.yml`。
- WHEN 发布完成 THEN 文档明确要求生成发布记录并包含生产环境检查结果。

### 3.2 文档入口登记

**描述**：发布目录 README 必须登记新增生产发布 runbook，方便后续入口检索。

**验收标准**：

- WHEN 查看 `.sce/runbooks/backend-admin-release/README.md` THEN 能看到生产发布 runbook 文件名。
- WHEN 查看 `.sce/specs/README.md` THEN 能看到 `00-184` Spec 登记。

### 3.3 不暴露生产密钥

**描述**：运维文档可以描述变量名和检查方式，但不得新增真实生产密钥、数据库密码、云密钥或管理员密码。

**验收标准**：

- WHEN 查看新增文档 THEN 不出现新的明文生产密钥。
- WHEN 需要使用敏感值 THEN 文档使用环境变量、gitignored secret 文件或占位符表达。

## 4. 非功能需求

- 文档必须和现有 `backend-admin-standard-release.md`、`00-183` 环境切换方式一致。
- 文档要明确“同一份 JAR 多环境复用”，不要引导维护者为 prod 改源码。
- 文档要明确现有 `backend-only` 标准脚本仍需要远端运行环境先完成 prod 切换。

## 5. 约束条件

- 本轮不执行真实生产发布。
- 本轮不修改远端服务器、不改 Nacos 内容、不改 release 脚本逻辑。
