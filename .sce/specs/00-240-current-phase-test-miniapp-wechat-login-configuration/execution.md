# 测试环境小程序微信登录配置 - 执行记录

## 结果

- 状态：`COMPLETED`
- Nacos 发布：`20260828-161707-backend-nacos-test-wechat-login-config`
- 测试容器配置批次：`test-wechat-20260828-05`
- TAT invocation：`inv-s7x927gvf3`
- 变更范围：仅 `kaipai-backend-test.yml`、`/opt/kaipai/test/test-secrets.env` 和 `kaipai-backend-test`
- 正式环境：容器 ID、startedAt、restartCount 前后完全一致，数据库和 Nacos 正式 dataId 未修改

## 运行证据

- 测试 Nacos 新增 `wechat.miniapp.app-id/app-secret`，远端发布 helper 生成 before 备份。
- 测试 secret env before SHA256：`C51E126870862573CA2E42B10E318874C1E9075D18C0B39A8EE8CB75BF677D67`。
- 测试 secret env after SHA256：`64E8E9A6B713E7A48EEB018BB0D67435014FDC502FF32B054AB7BCCA37508647`。
- 运行时 appId/appSecret SHA256 与本机受控输入一致；文件权限为 `0600 root:root`。
- 测试容器数据库目标为 `kaipai_test`，Redis DB 为 `1`。
- 无效 code 响应已从“微信登录未配置”切换为微信上游 `invalid code`，证明运行配置生效。
- 测试 API docs、正式 API docs、测试后台均为 HTTP 200。
- `check-dual-env-preflight.py` 返回 `passed=true`，DNS、SSH/helper、双 Nacos dataId 和双数据库门禁全部通过。

## 自动化与回滚

- `test_test_environment_scripts.py`：2 项通过。
- `test_tencent_tat_test_wechat_config.py`：4 项通过。
- provisioning、`ROLLBACK.sh` Bash 语法通过。
- 回滚只在 `MODIFIED_FILE` 副本执行，结果恢复 `STATE=UNCONFIGURED`；原 `MODIFIED_FILE` 保持 `STATE=CONFIGURED`，远端测试环境保持配置后状态。
- 脱敏证据：`.sce/evidence/20260828-test-wechat-login-config/VERIFICATION.txt`。

## 发布兼容

后端代码、接口合同和数据库结构均未改变。测试环境修复不要求重建正式容器，也不解锁 `00-237`；用户完成 `00-236` 人工验收并明确签署 GO 后，才能进入正式发布。
