# 00-232 Schema 迁移安全与校验和门禁 - 技术设计

_Requirements: 3.1-3.5, 4, 5_

## 1. Runner 校验模型

当前 `run-backend-schema-migration.py` 只把 history 加载为脚本名集合。目标改为：

```text
script -> recorded checksum, applied mode, release id
```

决策逻辑：

```text
history missing script -> run per-migration preflight
history checksum == manifest checksum -> skip-same-checksum
history checksum != manifest checksum -> CHECKSUM_MISMATCH / NO-GO
```

不允许已有记录通过 upsert 被新 checksum 覆盖。

## 2. 迁移状态分类

每个非幂等迁移定义三个状态：

- `CLEAN_NOT_APPLIED`：目标表/列/索引/seed 均未出现，满足原脚本前置。
- `FULLY_APPLIED`：目标结构和 seed 全部存在，且 history checksum 一致。
- `PARTIAL_OR_AMBIGUOUS`：只存在部分目标，或结构存在但 history 缺失/不一致。

只有前两种存在自动动作。第三种必须输出实际对象差异，由新版本 repair migration 处理。

## 3. 五个重点 Preflight

| Migration | Clean 条件 | Fully applied 条件 |
|---|---|---|
| `V20260724_001` | request audit 有表且无 `scene` | `scene` 存在、NOT NULL，历史空值已归一 |
| `V20260726_001` | 三张 prompt 表、六个 request lineage 列和外键均不存在 | 三表、列、外键和两套模板/版本 seed 完整 |
| `V20260731_001` | 三张 actor card 表均不存在 | 三表结构、索引完整 |
| `V20260731_002` | background 表存在且目标 seed 为 0 | 原 10 行 seed 的稳定业务键集合完整 |
| `V20260810_001` | actor_card 存在且无 attachment 列/索引 | 列和索引均存在 |

`V20260814_001/002` 在 actor card seed 后执行，继续保持既有清理与最终 7 行 provision 合同。

## 4. Repair Migration 规则

若检测 partial state：

1. 保存 information_schema 差异证据。
2. 停止当前批次，不写原 migration history。
3. 创建新版本、幂等、只修缺口的 migration。
4. 在 fresh fixture、partial fixture、fully-applied fixture 上验证。
5. 重新冻结 `00-231` 候选并重跑全部测试。

Repair migration 不改写原 migration 文件，也不伪造原脚本已完整执行。

## 5. 测试矩阵

| 场景 | 期望 |
|---|---|
| 生产旧 Schema fresh apply | 14 个成功，history 14 条 |
| 同库同 manifest 重跑 | 14 个安全跳过 |
| 同名 migration 改 1 字节 | checksum mismatch，执行 0 个 |
| DDL 已有、history 缺失 | partial/ambiguous，执行 0 个 |
| history 有名、结构缺失 | schema drift，NO-GO |
| seed 缺行/重复 | seed drift，NO-GO 或 repair |
| 文件顺序交换 | manifest mismatch，NO-GO |

测试使用 MySQL 8，不用 H2 模拟 generated column、JSON、CHECK 和 DDL 提交行为。

## 6. Schema 断言

验证内容分为：

- 表存在：19 张目标表。
- 字段存在：`actor_profile`、`actor_experience`、`actor_card` 和 request audit 增量字段。
- 索引与约束：素材唯一键、卡片查询索引、prompt 外键、media CHECK。
- Seed：后台权限去重、prompt 模板/版本、最终 background 7 行。
- History：文件名、checksum、applied mode、release id。

所有结果保存为 JSON/Markdown 聚合，不包含行内容。

## 7. 发布顺序

1. 从 `00-231` manifest 读取 14 个 checksum。
2. 执行全批 preflight。
3. 逐文件执行 migration；每个文件成功后立即核验目标并登记 history。
4. 执行全局 schema assertion。
5. 输出阶段证据 SHA256。

测试和生产调用相同代码路径，只改变显式 `--mysql-database` 和 release label。

## 8. 回滚边界

- 本阶段不设计自动 DROP 回滚。
- 失败后保留已提交的扩展式 DDL，先分类实际状态。
- 应用可回滚到旧版本；Schema repair 通过新 migration 前进。
