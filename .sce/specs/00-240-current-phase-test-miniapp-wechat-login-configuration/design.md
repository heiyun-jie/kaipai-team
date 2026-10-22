# 测试环境小程序微信登录配置 - 技术设计

_Requirements: 2.1-2.4, 3_

## 1. 根因与目标状态

`application.yml` 将 `wechat.miniapp.app-id/app-secret` 映射到 `WECHAT_MINIAPP_APP_ID/APP_SECRET`。当前测试 compose 的 `env_file` 只有 COS 两项，因此 `WechatMiniProgramServiceImpl.isConfigured()` 返回 false。

目标状态为双层一致：

1. `kaipai-backend-test.yml` 保存测试环境所需微信属性，并由标准 Nacos 发布 helper 备份和脱敏记录。
2. `/opt/kaipai/test/test-secrets.env` 持久化同一组环境变量，测试容器重建后直接生效；文件继续为 `0600 root:root`。

## 2. 执行顺序

1. 记录正式/测试容器状态与脱敏微信配置摘要。
2. 从本机受控 secret file 生成只用于远端传输的临时候选；临时文件不得进入 Git，使用后删除。
3. 通过标准 Nacos helper 更新 `kaipai-backend-test.yml` 并保留 before 备份。
4. 备份测试 `test-secrets.env`，写入两项微信变量，原 COS 变量保持不变。
5. 只执行测试 compose 的 `up -d --force-recreate kaipai-test`。
6. 校验测试容器哈希、接口行为和正式容器不变量。

远端普通 SSH 账号没有 Docker socket 权限，现有免密 helper 也未开放测试 compose 重建。执行入口因此使用腾讯云 TAT 的固定命令：目标只允许上海区目标 Lighthouse 实例、`/opt/kaipai/test/docker-compose.yml` 和 `kaipai-test`；命令从正式运行容器读取同组微信变量到进程内存，写入测试 secret env 后立即清理临时文件。命令前后必须比较正式容器 ID、启动时间和 restartCount，任一变化即失败。

## 3. 回滚

- 恢复 `test-secrets.env.before` 与 Nacos before 配置。
- 只重建 `kaipai-backend-test`。
- 回滚验证必须确认测试接口恢复为未配置状态，正式容器仍未变化。

## 4. 防复发

更新 `provision-test-environment.sh`：从已批准的正式运行时读取成组微信变量，写入测试 secret env，并在启动后检查两项均存在。脚本不打印变量值。
