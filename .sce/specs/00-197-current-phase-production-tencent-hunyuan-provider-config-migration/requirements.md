# 00-197 当前阶段生产腾讯混元生图 Provider 配置迁移

## 1. 概述

当前生产数据库 `kaipai_prod` 的 `ai_image_provider_config` 与 `ai_image_provider_config_audit` 均为空。后端因此无法解析数据库中的 active provider，回退到容器环境变量 `AI_PROFILE_CARD_PROVIDER_CODE=kplyyk`，导致新的 AI 分享图任务继续调用已经失效的 KPLYYK 公网代理。

旧线上数据库 `kaipai_dev` 仍保留结构完整、历史上经过真实测试的腾讯混元配置：`tencent-hunyuan` 为启用且 active，endpoint 为 `https://aiart.tencentcloudapi.com`，model 为 `hunyuan-image-3.0`，加密密钥存在，历史 provider test 与真实 AI 分享图任务均有成功记录。历史 test 状态只作为迁移来源证明，不能替代迁移后的实时腾讯调用。

本轮是生产配置迁移，不修改后端业务代码。目标是通过受控、可备份、可验证的数据库迁移，把旧库中唯一的 `tencent-hunyuan` 配置迁入 `kaipai_prod` 并设为唯一 active provider，随后执行一次生产 provider 真实生图 smoke。

## 2. 用户故事

- 作为演员用户，我希望生产 AI 分享图继续使用已经验证过的腾讯混元生图，不再因为 KPLYYK 旧代理失效而立即失败。
- 作为维护者，我希望只迁移腾讯混元配置，不把旧库其它 provider 或无关审计数据带入生产。
- 作为维护者，我希望加密密钥始终在数据库之间直接复制，不进入本地文件、命令输出、Spec 或聊天记录。
- 作为维护者，我希望迁移前有目标表备份，迁移后有数据库验证和真实 provider smoke，失败时可以恢复迁移前状态。

## 3. 功能需求

### 3.1 源配置门禁

源库 `kaipai_dev` 必须唯一存在一条有效 `tencent-hunyuan` 配置，并满足：

- `enabled = 1`
- `active = 1`
- endpoint 为 `https://aiart.tencentcloudapi.com`
- model 为 `hunyuan-image-3.0`
- `secret_config_ciphertext` 非空

任一条件不满足时必须阻断迁移。

`last_test_status=success` 不作为凭据当前仍有效的充分条件；普通业务任务失败不会自动覆盖 provider test 状态，最终有效性必须由生产实时 provider test 证明。

### 3.2 目标配置门禁

当前目标库 `kaipai_prod` 的 provider 配置表已确认为空。正式 apply 前必须重新确认目标表没有 provider 行和 active 行；若状态发生变化，必须停止并重新评估，不能覆盖未知配置。

### 3.3 备份

apply 前必须在 `kaipai_prod` 创建本轮唯一的 `zz197_` 配置表和审计表备份。备份表名必须写入执行结果，并满足 MySQL 64 字符标识符限制。

### 3.4 精确迁移与激活

- 只允许从 `kaipai_dev.ai_image_provider_config` 复制 `provider_code='tencent-hunyuan'` 的有效行。
- 迁移后 `kaipai_prod` 必须只有一条有效腾讯配置，且为 `enabled=1 / active=1`。
- 迁移后必须写一条不含密钥明文的 `migration_restore` 审计记录。
- 源库不得被修改。
- 不迁移 KPLYYK、火山、阿里、百度、HTTP 或 OpenAI provider 行。

### 3.5 密钥安全

- 初始迁移的密钥密文只能通过同一 MySQL 实例内的 `INSERT ... SELECT` 从源库复制到目标库；后续凭据轮换必须通过生产后台调用后端加密保存能力完成。
- SQL 输出、脚本日志、执行记录和测试断言不得包含 `secret_config_ciphertext` 或密钥明文。
- 验证只允许输出 `HAS_SECRET=0|1` 和已有脱敏 mask。

### 3.6 生产验证

迁移后必须依次确认：

1. 数据库 active provider 为 `tencent-hunyuan`。
2. endpoint/model 与源配置一致。
3. 密钥密文存在。
4. 通过现有后台 provider test 接口执行一次真实腾讯生图。
5. provider test 返回 success、持久化测试图片，并把生产 `last_test_status` 更新为 success。
6. 若实时测试明确返回凭据不存在或失效，必须在授权登录态下轮换腾讯云 API 密钥、通过生产后台重新加密保存，再重复真实测试；不得输出或落盘密钥明文。

### 3.7 回滚边界

如果数据库结构、唯一 active provider 或公开配置验证失败，不得继续让用户重试生成，应保留现场并使用本轮 `zz197_` 备份恢复目标 provider 配置与审计表。若数据库迁移正确、失败点被隔离为源凭据在迁移前已经失效，则保留正确的 provider 路由配置，在授权操作下轮换凭据并重新执行真实测试；源库始终保持不变。

## 4. 非功能需求

- 不重启后端；当前 provider 解析每次从数据库读取 active 配置，迁移后应即时生效。
- 不修改 `userId=4` 的三条历史失败任务，不伪造成功状态。
- 不在本轮修复 KPLYYK `/v0` Nginx 代理；该能力作为独立兜底治理处理。
- 所有生产 SQL 必须通过标准 backend helper 执行并留下 SCE 记录。

## 5. 验收标准

- `kaipai_prod.ai_image_provider_config` 中 `tencent-hunyuan` 唯一、启用且 active。
- active provider 总数为 1。
- 腾讯密钥可被生产后端成功解密并完成真实测试生成。
- `ai_image_provider_config_audit` 存在本轮迁移审计和 provider test 审计。
- 迁移过程中未输出或落盘任何密钥明文/密文。
- 备份表和回滚路径已记录。
