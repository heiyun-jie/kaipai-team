# 执行记录

## 当前状态

- Candidate：`20260828-190255-v3-draft`
- 测试目标：`kaipai-backend-test` / `kaipai_test` / Redis DB `1`
- 生产决策：`NOT_AUTHORIZED`
- 运行状态：已完成本地备份并同步到测试运行时，等待 DevTools 重新登录后复测 AI 扩图。

## 约束

- 不修改生产容器、生产 compose、生产数据库、Nginx 或正式小程序。
- 不在记录和输出中保存密钥明文。

## 本地备份

- 来源：`/opt/kaipai/docker-compose.yml`，SSH 只读提取。
- 文件：`.sce/config/local-secrets/ai-provider-runtime.env`（Git ignored，Windows 当前用户 ACL）。
- `KEY_LENGTH=64`，`KEY_SHA256=A1B06FD87C797201118B5D34943DF27BB48B61E569B5ADAF4B3B84D3C5185645`；明文未进入终端、日志或 Spec。

## 测试环境同步

- 脚本：`.sce/runbooks/backend-admin-release/scripts/run-tencent-tat-test-ai-master-key.py`。
- TAT：`ap-shanghai/lhins-cm8k27ii`，invocation `inv-r847mj099a`，command `cmd-0nges4ww`，exit `0`。
- 测试容器已备份 `/opt/kaipai/test/test-secrets.env` 后写入主密钥并重建；API 与后台均返回 `HTTP 200`。
- 测试边界：数据库 `kaipai_test`，Redis DB `1`，未修改测试 compose 的 provider 禁用策略。

## 生产未受影响

- `PROD_BEFORE` 与 `PROD_AFTER` 完全一致：
  `1195a88da11fc2e4141091ee6494c291c287bb48a61725c469d420f32b82bea1|2026-07-21T14:10:50.90030867Z|0`
- 未执行生产容器重建、生产配置写入、生产数据库迁移、Nginx 切流或正式小程序上传。

## 回滚与证据

- 本地回滚副本结果：`ROLLBACK_RESULT=restored_absent`，实际备份文件保持存在。
- 证据：`.sce/evidence/20260901-test-ai-key-isolation/VERIFICATION.txt`。
- 由于测试运行时配置发生变化，AI 扩图相关人工验收需在 DevTools 重新登录后重新执行；生产决策仍为 `NOT_AUTHORIZED`。

## 2026-09-01 运行态复核

- 测试容器运行态摘要：主密钥存在、长度 `64`、SHA256 与本地备份一致；测试 secret 权限 `600|root|root`。
- 通过测试 API 的隔离账号提交一次扩图任务：提交 `HTTP 200 / pending`，轮询 `HTTP 200 / done`，`failureReason=null`；当前测试后端不再返回“主密钥未配置”。
- 生产容器指纹复核仍为：`1195a88da11fc2e4141091ee6494c291c287bb48a61725c469d420f32b82bea1|2026-07-21T14:10:50.90030867Z|0|running`。
- 本次复核未重启或修改微信开发者工具；其内部自动化会话仍等待用户重新登录。人工验收入口和候选产物保持不变。
