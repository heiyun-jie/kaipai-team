# 00-234 隔离测试环境基础设施

> 状态：`INFRA_READY`（2026-08-27 自动门禁通过；微信体验版合法域名仍需在公众平台侧人工确认）
>
> 上游：`00-185`、`00-230`、`00-231`；下游：`00-235`、`00-236`

## 1. 概述

本 Spec 在不影响正式服务的前提下建立同机测试运行时，确保域名、TLS、容器、端口、Nacos、Schema、Redis、COS 和所有外部副作用能力与生产隔离。

## 2. 用户故事

作为测试人员，我希望使用真实公网 HTTPS 的测试 API 和管理端完成体验版人工测试。

作为线上用户，我希望测试登录、上传、短信、实名和 AI 操作不会改变正式数据或产生未经控制的正式外部调用。

## 3. 功能需求

### 3.1 建立测试网络入口

**验收标准**：

- WHEN 查询 DNS THEN `test-api.kplyyk.com`、`test.kplyyk.com` 指向目标服务器。
- WHEN 访问两个域名 THEN TLS 证书有效、域名匹配且无明文 HTTP 回退。
- WHEN 微信体验版调用 THEN test API 已进入 request/upload/download 合法域名。
- WHEN 测试请求进入 Nginx THEN 只路由到测试后端/测试静态目录。

### 3.2 建立独立后端运行时

**验收标准**：

- WHEN 测试容器启动 THEN 容器名为 `kaipai-backend-test`，端口为 `18080`，profile 为 `test`，Nacos enabled。
- WHEN 回读数据源 THEN schema 为 `kaipai_test`，不得为 `kaipai_prod`、`kaipai` 或 `kaipai_dev`。
- WHEN 生产容器运行 THEN 仍使用 `8080` 且不被重建、不停机。

### 3.3 隔离缓存和对象存储

**验收标准**：

- WHEN 回读 Redis 配置 THEN test/prod DB index 不同，或使用不同实例。
- WHEN 测试上传 THEN 目标是测试 private bucket，不能写生产 bucket。
- WHEN 测试删除素材 THEN 只能删除测试 bucket 对象。
- WHEN 容器启动前置检查失败 THEN 测试服务保持停止。

### 3.4 控制外部副作用

**验收标准**：

- WHEN 测试发送短信 THEN 仅允许测试白名单或固定验证码实现。
- WHEN 测试实名、AI 生图、DeepSeek 或回调 THEN 默认禁用真实调用，或使用明确白名单、额度和测试配置。
- WHEN 未配置安全策略 THEN 相关接口返回可识别的测试环境禁用结果，不回退生产 provider。

### 3.5 建立测试管理端和小程序构建

**验收标准**：

- WHEN 访问 `test.kplyyk.com` THEN 静态文件来自独立 `html-test` 目录，API 指向 test API。
- WHEN 构建测试小程序 THEN API Base URL 为 test API，不能上传为正式版。
- WHEN 构建 release 小程序 THEN 不包含 test/local URL。

### 3.6 输出隔离证明

**验收标准**：

- WHEN 环境预检完成 THEN 自动输出 DNS、TLS、容器、端口、Nacos、DB、Redis、COS 和外部能力矩阵。
- WHEN 任一 test/prod 目标相同 THEN 结论为 `NO-GO`。
- WHEN 环境未装载生产副本迁移 THEN 可标记 `INFRA_READY`，但不得标记 `TEST_READY`。

## 4. 非功能需求

- 不把密钥写入仓库、日志或发布记录。
- 新增测试容器不得抢占生产 CPU/内存到影响线上；必须配置资源边界或至少监控。
- Nginx 配置修改前备份并通过配置检查。

## 5. 约束条件

- DNS、证书、Nacos、Nginx、容器和微信域名均属外部变更，需要用户明确授权。
- 测试服务在 `00-235` 恢复/迁移测试库期间必须停止。
- 不允许通过 hosts 文件伪造最终公网验收。
