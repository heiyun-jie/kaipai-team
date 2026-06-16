# 00-184 当前阶段生产环境发布运维流程 - 执行记录

## 1. 改动摘要

- 新增 `.sce/runbooks/backend-admin-release/production-release-runbook.md`
  - 记录生产环境发布流程。
  - 明确后端生产运行必须为 `SPRING_PROFILES_ACTIVE=prod`、`NACOS_ENABLED=true`。
  - 明确生产 Nacos dataId 为 `kaipai-backend-prod.yml`。
  - 记录后端 / 管理端 / 联合发布、smoke、回滚和发布记录要求。
- 更新 `.sce/runbooks/backend-admin-release/README.md`
  - 登记 `production-release-runbook.md`。
- 更新 `.sce/specs/README.md`
  - 登记 `00-184 current-phase-production-release-ops-runbook`。

## 2. 验证记录

### 2.1 文档存在性

命令：

```powershell
Test-Path .sce\runbooks\backend-admin-release\production-release-runbook.md
```

结果：`True`

### 2.2 入口登记

命令：

```powershell
Select-String -Path .sce\runbooks\backend-admin-release\README.md -Pattern "production-release-runbook"
Select-String -Path .sce\specs\README.md -Pattern "00-184"
```

结果：

- `README.md` 已登记 `production-release-runbook.md`
- `specs/README.md` 已登记 `00-184`

### 2.3 敏感值扫描

命令：

```powershell
rg -n "password:|secret:|secret-id:|secret-key:|app-secret:|kaipainacos|Bearer\s+[A-Za-z0-9]|AKID|mysql.*password|redis.*password" .sce\runbooks\backend-admin-release\production-release-runbook.md .sce\specs\00-184-current-phase-production-release-ops-runbook -S
```

结果：无命中。

## 3. 结论

本轮只创建生产发布运维流程文档，不执行真实生产发布，不修改远端服务器，不改 Nacos 内容，不改发布脚本。
