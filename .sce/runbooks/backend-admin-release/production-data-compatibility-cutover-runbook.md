# 生产数据兼容验证与双环境切流 Runbook

> 对应 Spec：`00-230 current-phase-production-data-compatibility-and-dual-environment-cutover`
>
> 上游：`same-host-dual-environment-runbook.md`、`production-release-runbook.md`
>
> 本文是执行顺序和中止门禁。没有用户明确授权时，只允许执行只读预检。

## 1. 核心原则

1. 同一 MySQL 实例可以，测试和生产共用同一 schema 不可以。
2. 测试库每批从生产完整副本重建，才能验证真实历史数据。
3. 迁移顺序固定，测试和生产文件 SHA256 必须一致。
4. 先 Schema、再后端、最后小程序；新后端必须兼容仍在线的旧小程序。
5. 正常回滚只回切应用和流量，不用旧备份覆盖仍在产生新写入的生产库。

## 2. 阶段门禁

```text
候选冻结
  -> 测试基础设施 READY
  -> 生产/测试备份 SHA256 一致
  -> 生产副本恢复到 kaipai_test
  -> 14 个迁移 PASS
  -> 历史素材回填 PASS
  -> 数据兼容断言 PASS
  -> 人工测试 GO
  -> 生产备份 PASS
  -> 生产同批迁移 PASS
  -> 候选后端旧客户端 smoke PASS
  -> Nginx 切流
  -> 正式小程序发布
  -> 稳定观察和旧容器退场
```

任何箭头前的门禁失败都停止推进，不允许带病进入下一阶段。

## 3. 发布前只读预检

### 3.1 工作树和候选

- 根仓库和三个子项目提交已固定。
- 后端脏改已经提交，或形成严格 overlay 清单。
- `V20260818_001__actor_card_media_binding.sql` 不再是未跟踪文件。
- test / release 小程序构建能够分别证明 API Base URL。

### 3.2 远端安全

先运行本地脱敏测试，确认通过后再同步 helper：

```powershell
python .sce/runbooks/backend-admin-release/scripts/tests/test_backend_runtime_diagnostics.py
```

旧 helper 未替换前，禁止执行 runtime diagnostics。同步 helper、修改 DNS/Nacos/Nginx 均属于远端变更，需要用户授权。

### 3.3 双环境预检

安全 helper 就绪后使用：

```powershell
python .sce/runbooks/backend-admin-release/scripts/check-dual-env-preflight.py --allow-fail
```

进入发布门禁时去掉 `--allow-fail`，要求 `passed=true`。

## 4. 测试环境准备

### 4.1 外部前置

- DNS：`test-api.kplyyk.com`、`test.kplyyk.com` 指向正式服务器。
- HTTPS：两个测试域名证书有效。
- 微信公众平台：把 test API 加入 request/upload/download 合法域名。
- Nacos：`kaipai-backend-test.yml` 的数据库目标为 `kaipai_test`。
- Redis：测试 DB index 与生产不同。
- COS：测试使用独立 bucket；当前代码不支持环境 key 前缀，不能仅靠 UUID 认为已隔离。
- 短信/实名/AI：禁用真实副作用，或限制在明确测试白名单和额度。

### 4.2 测试服务

目标运行态：

```text
container: kaipai-backend-test
profile: test
nacos: true
port: 18080
database: kaipai_test
```

启动后必须回读安全字段，确认没有连接 `kaipai_prod`。

## 5. 生产副本克隆

此步骤会重建 `kaipai_test`，执行前必须由用户明确授权。

1. 停止测试后端。
2. 备份 `kaipai_prod`。
3. 备份当前 `kaipai_test`。
4. 对两份备份计算远端和本地 SHA256。
5. 精确确认目标 schema 为 `kaipai_test`。
6. 重建 `kaipai_test` 并恢复生产备份。
7. 记录恢复后的表数量、schema 大小和关键业务计数。

禁止使用未校验的环境变量、通配符或动态拼接名称执行 DROP。备份文件和日志不得包含命令行密码。

## 6. Schema 迁移

固定文件顺序：

```text
V20260723_001__career_profile_domain_foundation.sql
V20260723_002__actor_media_asset_relations.sql
V20260723_003__share_card_favorite.sql
V20260723_004__ai_profile_import_governance.sql
V20260723_005__ai_profile_import_permission_alignment.sql
V20260724_001__ai_profile_import_request_scene.sql
V20260726_001__ai_profile_import_prompt_template_governance.sql
V20260726_002__ai_profile_import_prompt_permission_alignment.sql
V20260731_001__actor_card_tables.sql
V20260731_002__actor_card_background_seed.sql
V20260810_001__actor_card_attachment_asset_binding.sql
V20260814_001__actor_card_background_style_cleanup.sql
V20260814_002__actor_card_background_provision.sql
V20260818_001__actor_card_media_binding.sql
```

标准入口示意：

```powershell
python .sce/runbooks/backend-admin-release/scripts/run-backend-schema-migration.py `
  --label test-prod-copy-v3 `
  --operator <name> `
  --mysql-database kaipai_test `
  --migration-file V20260723_001__career_profile_domain_foundation.sql `
  --migration-file V20260723_002__actor_media_asset_relations.sql `
  --migration-file V20260723_003__share_card_favorite.sql `
  --migration-file V20260723_004__ai_profile_import_governance.sql `
  --migration-file V20260723_005__ai_profile_import_permission_alignment.sql `
  --migration-file V20260724_001__ai_profile_import_request_scene.sql `
  --migration-file V20260726_001__ai_profile_import_prompt_template_governance.sql `
  --migration-file V20260726_002__ai_profile_import_prompt_permission_alignment.sql `
  --migration-file V20260731_001__actor_card_tables.sql `
  --migration-file V20260731_002__actor_card_background_seed.sql `
  --migration-file V20260810_001__actor_card_attachment_asset_binding.sql `
  --migration-file V20260814_001__actor_card_background_style_cleanup.sql `
  --migration-file V20260814_002__actor_card_background_provision.sql `
  --migration-file V20260818_001__actor_card_media_binding.sql
```

生产执行时只把 `--mysql-database` 改为 `kaipai_prod`，其余文件和顺序不变，并使用新的 `prod` label。

警告：`V20260724_001`、`V20260726_001`、`V20260731_001/002`、`V20260810_001` 当前不是完全幂等。它们硬化或一次性副本演练未完成前，不进入生产。

## 7. 历史数据兼容

### 7.1 结构断言

- 19 张缺失表全部存在。
- `actor_profile` 和 `actor_experience` 候选代码所需字段全部存在。
- `schema_release_history` 含本批 14 个文件。
- history 校验和与发布候选一致。

### 7.2 数据断言

对比迁移前后：

- 用户、档案、经历、旧分享卡、浏览历史、实名记录有效行数不减少。
- 旧 `avatar_url`、`photo_urls`、`video_url` 非空计数不减少。
- 不存在无用户档案、无档案经历、无用户实名、无 owner 素材。
- 历史作品的项目名、角色名等旧字段没有被默认值覆盖。

### 7.3 素材回填

运行专用兼容程序的 dry-run，先输出：

- 待处理头像/照片/视频数量。
- 可读取、不可读取、不受信任 host、重复 URL 数量。
- 预计写入对象数和字节数。

dry-run 全通过后执行 apply。测试写测试 bucket，生产写正式 private bucket。apply 后所有可读取旧素材都必须有 ready asset 和正确关系；旧 URL 不删除。

## 8. 人工测试

### 8.1 小程序测试构建

测试构建只用于开发版/体验版，API 指向：

```text
https://test-api.kplyyk.com
```

正式线上版本仍指向：

```text
https://api.kplyyk.com
```

不得把指向 test API 的产物提交正式发布。

### 8.2 必测路径

1. 历史账号登录、退出、会话恢复。
2. 个人资料旧头像显示和保存。
3. 演艺经历旧数据读取、新增、编辑、删除。
4. 自我介绍读取和保存。
5. 素材库旧照片/视频展示，新素材上传/预览/删除。
6. 演员卡 7 步创建、素材选择、生成、预览、发布。
7. 新旧分享详情页匿名访问。
8. 实名状态读取，不输出或覆盖敏感数据。
9. 后台登录、角色权限、AI 配置页面。

每项记录账号类型、结果、关联错误码和截图；记录中只使用内部测试标识，不写 PII。

## 9. 生产切流

人工测试结论为 GO 后：

1. 再备份 `kaipai_prod` 并校验 SHA256。
2. 执行与测试完全相同的 14 个迁移。
3. 执行同版本历史素材回填。
4. 重跑数据断言；计数减少立即停止。
5. 启动新的生产候选容器，先不挂公网 Nginx。
6. 对候选端口执行健康、登录、历史数据和旧前端 smoke。
7. 备份现有 Nginx 配置，更新 upstream。
8. 执行 `nginx -t`；失败时不 reload。
9. reload 后验证 `https://api.kplyyk.com`。
10. 构建 `npm run build:mp-weixin:release`，执行 `npm run audit:mp-package`，确认无 test/local URL。
11. 上传并发布微信小程序正式版。
12. 观察稳定后停止旧容器；测试环境继续保留。

## 10. 中止和回滚

任一情况为 NO-GO：

- 测试后端实际连接 `kaipai_prod`。
- 备份 SHA256 不一致。
- 迁移部分失败且实际结构不明确。
- 核心业务计数减少或出现新孤儿关系。
- 任一有效历史素材在新 UI 不可见。
- 旧版本小程序 smoke 失败。
- Nginx 配置检查失败或正式 API 5xx 异常。

回滚顺序：

1. Nginx 上游回切旧容器。
2. 保留新增表、字段和兼容回填，不紧急 DROP。
3. 必要时回退小程序版本。
4. 只对明确异常行做定点修复。
5. 全库备份只作为灾难恢复材料，不覆盖发布后新写入。

## 11. 完成定义

- 测试、生产两个后端和两个 schema 继续隔离。
- 正式 API 已承接新后端，正式小程序只访问正式 API。
- 历史用户的数据在新 UI 可见、可编辑、可继续分享。
- 旧客户端合同仍可用。
- 测试/生产发布记录、迁移历史、备份校验和和人工验收记录齐全。
- 旧生产容器在观察期后停止，测试环境保留。
