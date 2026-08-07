# 00-197 当前阶段生产腾讯混元生图 Provider 配置迁移 - 技术设计

## 1. 范围

_Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7_

本轮只新增 SCE 运维脚本和执行记录，不修改后端、管理端或小程序运行时代码。

| 层 | 入口 | 策略 |
|----|------|------|
| 源库 | `kaipai_dev.ai_image_provider_config` | 只读腾讯混元配置事实源 |
| 目标库 | `kaipai_prod.ai_image_provider_config` | 备份后写入唯一腾讯配置 |
| 审计 | `kaipai_prod.ai_image_provider_config_audit` | 写入脱敏 `migration_restore` 记录 |
| 执行 | `scripts/run-production-tencent-provider-migration.py` | 通过标准 helper 执行 precheck/apply/verify |
| 真实验证 | `/api/admin/ai/image-providers/tencent-hunyuan/test` | 使用既有生产管理员权限执行一次真实生图 |
| 凭据补救 | 腾讯云 CAM + 生产后台密钥页 | 仅当实时测试证明源凭据已失效时执行受控轮换 |

## 2. 脚本模式

```powershell
python .sce/specs/00-197-current-phase-production-tencent-hunyuan-provider-config-migration/scripts/run-production-tencent-provider-migration.py --mode precheck --operator codex
python .sce/specs/00-197-current-phase-production-tencent-hunyuan-provider-config-migration/scripts/run-production-tencent-provider-migration.py --mode apply --operator codex
python .sce/specs/00-197-current-phase-production-tencent-hunyuan-provider-config-migration/scripts/run-production-tencent-provider-migration.py --mode verify --operator codex
```

默认参数：

- host：`101.43.57.62`
- SSH user：`kaipaile`
- identity：`~/.ssh/kaipai_release_ed25519`
- source database：`kaipai_dev`
- target database：`kaipai_prod`
- MySQL container：`kaipai-mysql`

## 3. Precheck 设计

_Requirements: 3.1, 3.2, 3.5_

precheck 只输出非敏感 marker：

```text
SOURCE_PROVIDER_COUNT
SOURCE_ENABLED
SOURCE_ACTIVE
SOURCE_ENDPOINT
SOURCE_MODEL
SOURCE_HAS_SECRET
SOURCE_LAST_TEST_STATUS
TARGET_CONFIG_COUNT
TARGET_ACTIVE_COUNT
TARGET_TENCENT_COUNT
PRECHECK_PASSED
```

脚本同时校验 helper `FINAL_STATUS=passed`。任何 marker 不符合要求时返回非 0，不执行 apply。

`SOURCE_LAST_TEST_STATUS` 只证明源配置曾经通过测试。由于普通业务任务不会回写 provider test 状态，precheck 不得把历史 success 解释为凭据当前有效，实时有效性仍由迁移后 provider test 决定。

## 4. Apply 设计

_Requirements: 3.3, 3.4, 3.5_

apply SQL 在目标库执行，顺序固定：

1. 重跑源/目标门禁，并在失败时用 `SIGNAL SQLSTATE '45000'` 阻断。
2. 创建 `zz197_aipcfg_<timestamp>` 与 `zz197_aipaud_<timestamp>` 备份表。
3. 备份目标 provider 配置表和审计表当前内容。
4. 开启事务。
5. 将目标现有 active 行设为 inactive；门禁正常时当前应为 0 行。
6. 使用显式列清单从源库复制唯一 `tencent-hunyuan` 行。
7. 保留公开配置、密钥密文和 secret mask；把旧库 test 状态清空，等待生产真实测试覆盖。
8. 写 `migration_restore` 审计，只记录公开配置和脱敏 mask。
9. 提交并输出脱敏 marker。

密钥不会经过 Python 字符串或 SQL 输出：

```sql
INSERT INTO `kaipai_prod`.`ai_image_provider_config` (..., `secret_config_ciphertext`, ...)
SELECT ..., `secret_config_ciphertext`, ...
FROM `kaipai_dev`.`ai_image_provider_config`
WHERE `provider_code` = 'tencent-hunyuan' AND `deleted` = 0;
```

## 5. Verify 设计

_Requirements: 3.5, 3.6_

verify 查询并校验：

- target Tencent count = 1
- active provider count = 1
- active provider = `tencent-hunyuan`
- endpoint = `https://aiart.tencentcloudapi.com`
- model = `hunyuan-image-3.0`
- has secret = 1
- migration audit count >= 1

真实 provider test 必须通过现有受权限保护的后台接口执行，使生产后端完成密钥解密、腾讯签名、任务轮询、测试图片持久化和 test audit 更新。数据库存在密文不能替代这一验证。

若首次实时测试返回腾讯侧凭据不存在，先确认源/目标密文一致、生产主密钥可正常解密且同一错误是否早于迁移出现。只有证据把故障隔离到腾讯云凭据后，才允许在用户确认下删除不可恢复且未使用的旧生产密钥、创建替代密钥，并直接通过生产后台保存和测试。密钥只在浏览器会话内传递，不进入终端、Spec 或聊天输出。

## 6. 回滚设计

_Requirements: 3.7_

如需要回滚：

1. 记录当前失败现场，不覆盖本轮备份。
2. 清空目标 `ai_image_provider_config` 与本轮新增审计。
3. 从 `zz197_aipcfg_<timestamp>` 和 `zz197_aipaud_<timestamp>` 恢复迁移前内容。
4. 再次执行 verify，确认回到迁移前 active provider 状态。

当前目标表为空，因此预期回滚结果为重新回到无动态 provider 配置、环境变量兜底状态。实时测试失败时先判定失败边界：迁移结构错误才回滚；若 provider 路由正确而源凭据在迁移前已失效，则轮换凭据并重复测试，不回滚到已知失效的 KPLYYK 兜底。

## 7. 测试设计

- Python `unittest` 覆盖 precheck/apply/verify SQL 合同、密钥不输出、备份顺序和目标唯一 active provider。
- 生产 precheck 验证源/目标真实数据。
- 生产 verify 验证迁移结果。
- 后台真实 provider test 验证密钥解密和腾讯生图链路。
