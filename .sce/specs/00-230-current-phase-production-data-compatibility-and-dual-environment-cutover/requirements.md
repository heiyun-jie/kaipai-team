# 00-230 生产数据兼容验证与双环境正式切流

> 状态：调查完成，实施待授权
>
> 上游：`00-185` 同机测试 / 生产双环境治理、`00-184` 生产发布、`00-202` 生产库恢复、`00-203` Schema 兼容门禁

## 1. 概述

本 Spec 负责把当前已经完成的前后端候选版本安全发布到线上：在同一台服务器和同一个 MySQL 实例内保留 `kaipai_test`、`kaipai_prod` 两个独立 schema，先用生产数据完整副本验证 Schema 迁移、历史数据兼容和人工业务流程，再对生产库执行完全相同的迁移批次并切换正式流量。

本 Spec 不允许测试环境直接写 `kaipai_prod`，也不把“同一个数据库实例”误解为“测试和生产共用同一个 schema”。

## 2. 当前事实基线（2026-08-25）

- 正式后端当前运行在 `101.43.57.62`，容器端口为 `8080`，运行态为 `prod + Nacos`，连接 `kaipai_prod`。
- 测试后端容器和 `18080` 监听尚未建立。
- `test-api.kplyyk.com`、`test.kplyyk.com` 尚未建立可用 DNS。
- `kaipai-backend-test.yml` 虽已存在，但当前数据库目标不是 `kaipai_test`，不得直接启动。
- `kaipai_prod` 当前约 94 张表、7.27 MB；`kaipai_test` 约 40 张表、2.77 MB。生产数据量较小，完整备份和克隆适合放在同日发布窗口执行。
- `kaipai_prod.schema_release_history` 只登记到 `V20260705_001__identity_verification_status_compat.sql`。
- 当前候选代码依赖的 19 张新增表和 `actor_profile` / `actor_experience` 新字段尚未进入生产库，直接换新 JAR 会触发缺表或缺列错误。
- 新素材库只查询 `actor_media_asset`；历史头像、照片、视频仍保存在 `avatar_url`、`photo_urls`、`video_url`。只做 DDL 不做兼容回填，会造成老用户数据仍在库中但新 UI 不可见或不可编辑。
- 远端旧版 release helper 的运行诊断存在脱敏缺陷；在同步当前仓库的安全版本前，不得再次使用旧 helper 采集 runtime diagnostics。

## 3. 用户故事

作为发布负责人，我希望先在不影响线上用户的测试环境中验证新版本，并在确认业务和历史数据都兼容后再切换正式环境。

作为已有用户，我希望发布后原有账号、档案、作品、照片、视频、分享卡、浏览记录和实名状态仍可查询、展示和继续编辑。

作为运维人员，我希望生产切流失败时只回退应用流量，不通过直接恢复旧数据库覆盖发布后的新写入。

## 4. 功能需求

### 4.1 冻结唯一发布候选

**验收标准**：

- WHEN 开始搭建测试环境 THEN 必须固定根仓库、后端、管理端和小程序的候选提交或可复现 overlay 清单。
- WHEN 生成迁移清单 THEN 测试和生产必须使用同一文件名、同一顺序、同一 SHA256。
- WHEN 候选仍含未跟踪的 `V20260818_001__actor_card_media_binding.sql` THEN 不允许进入生产发布。

### 4.2 建立生产副本测试库

**验收标准**：

- WHEN 重建 `kaipai_test` THEN 先分别备份 `kaipai_prod` 和现有 `kaipai_test`，并保存 SHA256。
- WHEN 克隆完成 THEN `kaipai_test` 是 `kaipai_prod` 的完整数据副本，不是空库或旧测试种子库。
- WHEN 测试后端启动 THEN 数据源必须明确连接 `kaipai_test`，Redis 使用独立 DB，外部副作用能力处于禁用或测试白名单状态。
- WHEN 测试人员产生数据 THEN 不得改变 `kaipai_prod` 的任何行数、更新时间或对象存储文件。

### 4.3 按固定顺序完成 Schema 迁移

**验收标准**：

- WHEN 在 `kaipai_test` 执行迁移 THEN 必须按 `design.md` 定义的 14 个文件顺序执行。
- WHEN 任一迁移失败 THEN 不得继续启动候选后端，必须先判断是否发生 MySQL DDL 部分提交。
- WHEN 迁移完成 THEN `schema_release_history` 必须登记全部 14 个文件及校验和。
- WHEN 同一迁移已登记 THEN 发布脚本必须跳过，禁止重复执行非幂等 SQL。

### 4.4 验证历史结构化数据兼容

**验收标准**：

- WHEN 对比迁移前后 THEN `user`、`actor_profile`、`actor_experience`、旧分享卡、浏览历史、实名记录的有效行数不得减少。
- WHEN 新字段加入历史行 THEN 旧字段不得被清空或覆盖；新增字段的默认值必须符合兼容合同。
- WHEN 检查关联 THEN 不得新增孤儿档案、孤儿作品、孤儿分享卡、孤儿实名记录或无归属素材。
- WHEN 旧版本前端访问新后端 THEN 既有接口响应结构和鉴权行为仍可用。

### 4.5 兼容历史头像、照片和视频

**验收标准**：

- WHEN 历史用户只有 `avatar_url` THEN 发布后头像仍可展示，且可以进入新资料编辑流程。
- WHEN 历史用户只有 `photo_urls` / `video_url` THEN 发布后素材仍可在新 UI 中查看并被演员卡选择。
- WHEN 执行兼容回填 THEN 必须保留旧 URL 字段，新增素材使用 `source_type=migration` 和可追溯批次标识，不覆盖原值。
- WHEN 旧 URL 不属于受信任 COS、对象不存在或无法读取 THEN 该记录进入异常清单并阻断正式发布，不能静默丢弃。
- WHEN 重跑兼容回填 THEN 不得重复创建素材或关系。

### 4.6 完成人工测试和自动门禁

**验收标准**：

- WHEN 测试 API 可用 THEN 小程序测试构建或体验版必须指向 `https://test-api.kplyyk.com`，线上正式版继续指向 `https://api.kplyyk.com`。
- WHEN 使用体验版测试 THEN `test-api.kplyyk.com` 已加入微信合法 request/upload/download 域名并具备有效 HTTPS 证书。
- WHEN 人工测试 THEN 至少覆盖登录、个人资料、演艺经历、自我介绍、素材库、演员卡 7 步、生成预览、发布分享、旧分享页、实名状态和后台登录。
- WHEN 任一核心流程失败或出现历史数据不可见 THEN 结论为 NO-GO。

### 4.7 生产扩展式迁移与原子切流

**验收标准**：

- WHEN 测试通过 THEN 先重新备份 `kaipai_prod`，再执行与测试完全相同的迁移和兼容回填批次。
- WHEN 生产迁移执行 THEN 旧生产后端保持运行，扩展式 Schema 不得破坏旧版本。
- WHEN 新生产候选启动 THEN 先在未承接公网流量的候选端口完成健康检查和旧客户端 smoke。
- WHEN 切流 THEN 必须先通过 `nginx -t`，再原子 reload 上游；切换失败立即恢复旧上游。
- WHEN 后端稳定 THEN 才允许上传和发布指向正式 API 的小程序 release 构建。

### 4.8 回滚不覆盖新增业务写入

**验收标准**：

- WHEN 新后端 smoke 失败 THEN 回切旧后端，新增表和新增列保留，不执行紧急 DROP。
- WHEN 小程序新版本异常 THEN 使用微信版本回退能力，并保持旧后端可用。
- WHEN 发布后已有新写入 THEN 不得用发布前全库备份直接覆盖生产库；备份只用于灾难恢复和定点修复依据。
- WHEN 稳定观察期完成 THEN 才停止旧生产容器；测试环境继续保留给下一批发布，不与生产合并。

## 5. 非功能需求

- 生产发布目标 RPO 为 0：正常应用回滚不得丢失切流后的新写入。
- Nginx 切流本身应在秒级完成；数据库 DDL 以测试副本实测耗时作为生产窗口上限依据。
- 所有备份、迁移、数据回填和 smoke 均需生成分环境记录，记录中不得包含密钥、手机号、身份证号、Token 或完整资源 URL。
- 数据迁移遵循 expand-first：只新增表、列和关系；旧字段物理退场另行立项。

## 6. 本轮边界

- 本轮完成调查、Spec 和 Runbook，不修改远端数据库、Nacos、Nginx、DNS 或容器。
- 真实备份、克隆、迁移、部署和切流必须在用户明确授权后执行。
