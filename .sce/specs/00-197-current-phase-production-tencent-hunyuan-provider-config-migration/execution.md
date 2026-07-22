# 00-197 执行记录

## 当前状态

- 状态：`completed-provider-smoke-passed`
- 创建日期：`2026-07-21`
- 目标：把旧运行库中已验证的 `tencent-hunyuan` 配置迁移到当前生产库并恢复腾讯混元生图主链路。

## 已确认事实

- 当前生产后端连接 `kaipai_prod`。
- 迁移前 `kaipai_prod.ai_image_provider_config` 行数为 0。
- 迁移前 `kaipai_prod.ai_image_provider_config_audit` 行数为 0。
- 旧库 `kaipai_dev` 中 `tencent-hunyuan` 为 `enabled=1 / active=1`。
- 源 endpoint 为 `https://aiart.tencentcloudapi.com`，model 为 `hunyuan-image-3.0`。
- 源密钥密文与脱敏 mask 存在，历史 provider test 为 success，但该状态停留在 `2026-05-16`。
- 历史任务存在 3 次腾讯混元成功记录。
- `userId=4` 于 `2026-07-21` 提交的 3 个新任务均因回退到 KPLYYK 并收到 HTTP 301 而失败。
- 同一份源凭据从 `2026-05-29` 起已在旧库真实任务中连续返回 `AuthFailure.SecretIdNotFound`，早于 `2026-06-29` 生产切库。

## 脚本验证

- 红灯：实现文件不存在时，单测因 `FileNotFoundError` 失败。
- 绿灯：实现后 8 个 Python `unittest` 全部通过。
- `python -m py_compile` 通过。
- 覆盖范围：跨库门禁、容器名安全校验、备份顺序、精确 provider 复制、密钥不输出、迁移审计和 verify marker。

## 生产 Precheck

- 执行时间：`2026-07-21 16:16:03 +0800`
- source database：`kaipai_dev`
- target database：`kaipai_prod`
- 结果：`passed`
- 源 provider 数：`1`
- 源状态：`enabled=1 / active=1`
- 源 endpoint：`https://aiart.tencentcloudapi.com`
- 源 model：`hunyuan-image-3.0`
- 源密钥：`HAS_SECRET=1`
- 源最后测试：`success`
- 目标配置数：`0`
- 目标 active 数：`0`

## 生产 Apply

- 执行时间：`2026-07-21 16:17:36 +0800`
- 结果：`passed`
- 配置备份表：`zz197_aipcfg_20260721161717apply`
- 审计备份表：`zz197_aipaud_20260721161717apply`
- 迁移 provider：`tencent-hunyuan`
- 迁移 model：`hunyuan-image-3.0`
- 迁移后 active provider 数：`1`
- 迁移后腾讯配置数：`1`
- 迁移后密钥：`HAS_SECRET=1`
- 迁移审计数：`1`
- `MIGRATION_APPLIED=1`
- 未重启后端，旧库未修改，历史 AI 任务未修改。

## 独立 Verify

- 执行时间：`2026-07-21 16:18:35 +0800`
- 结果：`passed`
- `ACTIVE_PROVIDER=tencent-hunyuan`
- `ENDPOINT=https://aiart.tencentcloudapi.com`
- `MODEL=hunyuan-image-3.0`
- `HAS_SECRET=1`
- `TARGET_ACTIVE_COUNT=1`
- `VERIFY_PASSED=1`
- `LAST_TEST_STATUS=NULL`，符合迁移后等待生产真实 provider test 的设计。

## 迁移后真实用户 Smoke

- 执行时间：`2026-07-21 19:15:50 +0800`
- 用户：`userId=4`
- 任务：`aipf_effa9f3116264e86a193aebec5af476f`
- provider/model：`tencent-hunyuan / hunyuan-image-3.0`
- 结果：`failed`
- 腾讯错误：`AuthFailure.SecretIdNotFound`
- 说明：KPLYYK 301 路由问题已消失，请求已进入腾讯；生成图与 `share_card_id` 均为空。

## 凭据根因确认

- 源库与生产库 `secret_config_ciphertext` 逐字节一致，长度均为 227 字节，secret mask 也一致，排除迁移漏字段或密文损坏。
- 生产容器 `AI_PROVIDER_CONFIG_MASTER_KEY` 已配置并与当前 compose 配置一致；若主密钥错误，AES-GCM 解密会在本地失败，不会进入腾讯 API。
- 旧库同一密文于 `2026-05-21` 真实生图成功，自 `2026-05-29` 起连续出现相同 `SecretIdNotFound`，证明凭据失效早于生产切库与本次迁移。
- 腾讯云 CAM 中旧配置对应的 SecretId 已不存在；现有旧“生产环境”密钥从未访问且 SecretKey 已不可恢复。

## 腾讯云生产密钥轮换

- 用户在操作前明确确认禁用、删除旧生产密钥并创建替代密钥。
- 保留仍有调用记录的“测试环境”密钥，不做修改。
- 禁用并永久删除从未使用、SecretKey 已不可恢复的旧“生产环境”密钥。
- `2026-07-21 20:31:20 +0800` 创建替代密钥并标注为“生产环境-开拍了AI生图”。
- 新 SecretId/SecretKey 仅在受控 Chrome 会话内转入生产后台，未持久化到终端、Spec、项目文件或本地密钥文件。
- `2026-07-21 20:32:22 +0800` 通过生产后台保存密钥，审计动作 `secret_update=success`。

## 生产 Provider Smoke

- 执行时间：`2026-07-21 20:33:12 +0800`
- 入口：`https://kplyyk.com/system/ai-image-providers`
- provider/model：`tencent-hunyuan / hunyuan-image-3.0`
- 结果：`测试生成成功`
- 后台页面已显示测试结果图片。
- 数据库 `last_test_status=success`、`last_test_message=测试生成成功`。
- 审计动作 `test=success` 已持久化。

## 最终独立 Verify

- 执行时间：`2026-07-21 20:41:20 +0800`
- 门禁命令：`--mode verify --require-test-success`
- 结果：`passed`
- `enabled=1 / active=1`
- endpoint：`https://aiart.tencentcloudapi.com`
- model：`hunyuan-image-3.0`
- `HAS_SECRET=1`
- 密钥更新时间：`2026-07-21 20:32:22`
- 最后测试时间：`2026-07-21 20:33:12`
- 最后测试状态：`success`
- `VERIFY_PASSED=1`
- 历史失败任务保持原状；需要用户重新发起生成，才能验证新的分享卡业务任务。

## 回滚状态

- 数据库迁移、凭据轮换、真实 provider smoke 与独立 verify 均通过，不需要回滚。
- 旧凭据失效早于迁移，回滚会重新落入 KPLYYK 301 兜底，因此本轮保留正确的腾讯 active provider 配置。

## 安全约束

- 不输出源或目标 `secret_config_ciphertext`。
- 不输出腾讯 SecretId/SecretKey 明文。
- 不修改旧库源配置。
- 不修改历史 AI 任务状态。
- 不重启生产服务。
