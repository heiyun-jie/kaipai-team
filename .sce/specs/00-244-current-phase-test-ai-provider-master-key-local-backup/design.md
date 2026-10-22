# 测试环境 AI Provider 主密钥本地备份与隔离使用 - 技术设计

_Requirements: 3.1-3.4, 4, 5_

## 1. 数据流

```text
production compose (read-only)
  -> local .sce/config/local-secrets/ai-provider-runtime.env (0600, gitignored)
  -> test-only runtime secret env (backup + replace)
  -> kaipai-backend-test only
```

## 2. 来源与提取

- 通过受控远端只读命令提取 `AI_PROVIDER_CONFIG_MASTER_KEY` 的值。
- 终端只记录 source path、长度、SHA256，不记录值。
- 若来源缺失或格式为空，立即停止，不写测试环境。

## 3. 本地文件

- 路径：`.sce/config/local-secrets/ai-provider-runtime.env`。
- 使用 `umask 077` / Windows ACL 等价保护；写入后再次读取只校验 key 存在、长度和摘要。
- 不把 provider API SecretId/SecretKey 写入该文件。

## 4. 测试环境应用

- 通过 Tencent TAT 目标实例执行测试专用脚本。
- 脚本在 `/opt/kaipai/test/test-secrets.env` 变更前创建备份，并只替换/追加 `AI_PROVIDER_CONFIG_MASTER_KEY`。
- 重新创建 `kaipai-backend-test` 后检查 API、数据库、Redis 和生产容器指纹。
- 不启用生产 Nginx，不触碰 `kaipai-backend`。

## 5. 回滚

- 使用同批次测试备份恢复 `/opt/kaipai/test/test-secrets.env`，只重建测试服务。
- 回滚验证必须在副本或测试环境执行，保留生产容器指纹不变证明。
