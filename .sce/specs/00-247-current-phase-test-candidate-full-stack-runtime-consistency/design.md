# 测试候选全栈运行态一致性与演员卡生成约束修复 - 技术设计

_Requirements: 3.1-3.4, 4, 5_

## 1. 根因链路

```text
private source asset
  -> ActorCardGenerateService generationInput = null
  -> INSERT actor_ai_profile_card_task without source_image_url
  -> old kaipai_test schema requires NOT NULL
  -> DataIntegrityViolationException
  -> generate page displays 数据约束校验失败
```

`00-245` 已实现正确业务合同并提供 `V20260901_001__actor_card_internal_auto_expand.sql`。本次不增加第二份业务修复迁移，而是补齐 Candidate 后端和迁移进入测试运行态的部署证据。

## 2. 测试数据库读回

只读 SQL 输出稳定字段：

- `actor_ai_profile_card_task.source_image_url` 的 `IS_NULLABLE`；
- `actor_card_id/source_asset_id/source_fingerprint` 是否存在；
- `uk_actor_card_expand_source` 的列顺序与唯一性；
- `actor_card.expanded_source_fingerprint` 是否存在。

不读取或输出数据库密码、用户资料、素材 URL、Provider key。

## 3. 测试部署顺序

1. 记录测试与生产容器身份、启动时间和重启次数。
2. 对 `kaipai_test` 创建部署前备份并记录 SHA256。
3. 从冻结 Candidate 提取并校验内嵌迁移，应用到 `kaipai_test`。
4. 使用冻结 Candidate 的 backend JAR 重建 `kaipai-backend-test`。
5. 读回测试容器内 JAR SHA256、数据库 DDL和 API health。
6. 再次读取生产容器身份，要求完全未变。
7. 通过微信内部 MCP 重试 `cardId=1` 生成链路。

## 4. 全栈准入证明

新增结构化 `test-stack-readiness.json`，至少包含：

```json
{
  "schemaVersion": 1,
  "candidateId": "CANDIDATE",
  "candidateBackendJarSha256": "SHA256",
  "runtimeBackendJarSha256": "SHA256",
  "database": "kaipai_test",
  "migration": "V20260901_001__actor_card_internal_auto_expand.sql",
  "schemaContractPassed": true,
  "apiHealthPassed": true,
  "productionContainerUnchanged": true,
  "status": "PASSED"
}
```

`verify-test-miniapp-acceptance.py` 扩展为同时校验该文件与 Candidate 后端 JAR；缺失、Candidate 不匹配、JAR 哈希不匹配、schema/API/生产未变证明任一失败时返回 `TEST_STACK_NOT_READY`。

## 5. 测试与回滚

- 准入脚本单测覆盖证明缺失、Candidate 不匹配、JAR 不匹配和完整通过。
- 数据库回滚只针对 `kaipai_test` 使用部署前备份验证；生产数据库不进入回滚路径。
- 文件修改保留原始哈希，`ROLLBACK.sh` 只在独立副本恢复准入脚本，不改变实际工作区或远端运行态。

## 6. 桌面边界

MCP 只使用微信工具内部接口读取、导航和触发页面动作；不退出、不重启、不置顶、不抢焦点，不使用桌面截图、坐标、鼠标或键盘自动化。
