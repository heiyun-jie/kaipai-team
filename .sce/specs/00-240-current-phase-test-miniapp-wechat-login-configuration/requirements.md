# 测试环境小程序微信登录配置

> 状态：已完成（2026-08-28）。
>
> 上游：`00-173`、`00-234`、`00-236`；影响目标仅为 `kaipai-backend-test` 与 `kaipai-backend-test.yml`。

## 1. 问题

`POST https://test-api.kplyyk.com/api/auth/wechat-login` 返回“微信登录未配置小程序 appId/appSecret”。测试容器未注入 `WECHAT_MINIAPP_APP_ID` 和 `WECHAT_MINIAPP_APP_SECRET`，而正式容器已配置。本问题属于测试环境运行配置缺口，不涉及接口合同、数据库或正式环境发布。

## 2. 功能需求

### 2.1 受控密钥来源

- 只允许从 gitignore 的 `.sce/config/local-secrets/wechat-miniapp.env` 或服务器现有正式运行配置读取成组凭据。
- 日志、Spec、diff、命令输出和证据不得包含 `appSecret` 明文，只记录存在性、长度和 SHA-256。
- `appId` 与 `appSecret` 必须成组验证，任一缺失、占位或格式错误时拒绝写入。

### 2.2 测试环境注入

- 测试 Nacos dataId 仅允许为 `kaipai-backend-test.yml`。
- 测试密钥文件仅允许为 `/opt/kaipai/test/test-secrets.env`，权限保持 `0600 root:root`。
- 只允许重建 `kaipai-backend-test`，端口继续为 `18080`、数据库继续为 `kaipai_test`、Redis DB 继续为 `1`。
- 标准测试环境 provisioning 必须同步注入微信变量，避免后续重建再次丢失。

### 2.3 运行验证

- 测试容器运行态必须存在两项微信变量，且 SHA-256 与本机受控源一致。
- 用无效微信 code 调用接口时，不得再返回“未配置”；预期进入微信上游校验并返回可识别的无效 code 错误。
- `GET /api/v3/api-docs` 继续返回 HTTP 200。

### 2.4 正式保护

- 操作前后正式容器 `kaipai-backend` 的 ID、启动时间和 restartCount 必须一致。
- 不修改正式 compose、正式 Nacos dataId、正式端口 `8080` 或正式数据库。

## 3. 发布兼容

本次只补充测试环境运行配置和可重复 provisioning，不改变后端代码、请求体、响应体或数据库结构。测试候选仍需按 `00-236` 重新冻结后再正式签收。
