# 00-237 正式环境扩展迁移与原子切流

> 状态：Spec 完成，实施未开始
>
> 上游：`00-231`、`00-232`、`00-233`、`00-236`；下游：`00-238`

## 1. 概述

本 Spec 在人工验收明确 `GO` 后，对 `kaipai_prod` 执行测试已验证的同一 Schema 和媒体兼容批次，启动不接公网的新生产候选，完成旧客户端兼容 smoke，再原子切换 API/管理端流量并发布正式小程序。

## 2. 用户故事

作为发布负责人，我希望生产切流先完成数据库扩展和候选后端验证，旧版本小程序不因新版本上线而中断。

作为线上用户，我希望切流失败时能快速回到旧后端，且切流后新产生的数据不会被旧备份覆盖。

## 3. 功能需求

### 3.1 生产发布前置

**验收标准**：

- WHEN 开始生产操作 THEN `00-236` 已签署 `GO`，candidateId、manifest 和测试证据可核对。
- WHEN GO 之后候选、迁移、回填工具或配置变化 THEN GO 失效，必须重新走受影响阶段。
- WHEN 生产备份未完成或 SHA256 未验证 THEN 不执行生产迁移。

### 3.2 扩展式生产迁移

**验收标准**：

- WHEN 执行生产迁移 THEN 目标 schema 精确为 `kaipai_prod`，测试脚本/环境目标不被带入。
- WHEN 执行迁移 THEN 使用与测试完全相同的 14 个文件、顺序、checksum 和 runner 版本。
- WHEN 迁移部分失败 THEN 停止并按 `00-232` partial 状态处理，不盲目重跑或 DROP。
- WHEN 迁移完成 THEN production Schema/history/data assertion 全部通过。

### 3.3 生产媒体兼容回填

**验收标准**：

- WHEN 在生产 apply THEN 使用 `00-233` 同版本工具、`environment=prod` 和正式 private bucket。
- WHEN apply 完成 THEN 历史可读取媒体全部有 ready asset/关系，旧 URL 字段未改变。
- WHEN 生产对象复制或关系写入异常 THEN 不切流，保留旧应用可用。

### 3.4 候选后端验证

**验收标准**：

- WHEN 启动候选 THEN 使用 `prod + Nacos`、`kaipai_prod` 和独立候选端口/容器。
- WHEN 候选未通过健康、后台登录、历史账号和旧客户端 smoke THEN 不接正式 upstream。
- WHEN 候选通过 THEN 记录候选容器、JAR SHA256、配置摘要和 smoke 证据。

### 3.5 原子切换正式流量

**验收标准**：

- WHEN 修改 Nginx THEN 先备份配置并通过 `nginx -t`。
- WHEN reload THEN API 和管理端上游同时或按定义顺序切换到候选，不出现半套配置。
- WHEN reload 失败或公网 smoke 失败 THEN 立即回切旧 upstream，不删除旧容器。
- WHEN 切流成功 THEN 正式域名仍使用 HTTPS、正式 API 和正式管理端目录。

### 3.6 正式小程序发布

**验收标准**：

- WHEN 构建 release THEN API Base URL 只指向正式 API，不包含 test/local URL，包体和专项门禁通过。
- WHEN 后端正式 API 稳定 THEN 才上传/提交正式小程序版本。
- WHEN 小程序发布失败 THEN 正式后端仍兼容旧线上版本，不影响当前用户。

### 3.7 输出切流签收

**验收标准**：

- WHEN 全部完成 THEN 输出生产备份、迁移、回填、候选 smoke、Nginx reload 和正式 API 验证证据。
- WHEN 任一核心门禁失败 THEN 阶段结论为 `NO-GO` 或 `ROLLED_BACK`。
- WHEN 进入 `00-238` THEN 必须保留旧生产容器和可回切配置。

## 4. 非功能需求

- 迁移窗口内旧生产后端继续运行，除必要的短暂锁等待外不主动停机。
- 切流操作必须可在分钟级完成并明确负责人。
- 生产记录不得包含秘密、PII、完整签名 URL 或原始请求体。

## 5. 约束条件

- 生产数据库、Nacos、Nginx、容器和微信发布均需用户明确授权。
- 不通过全库恢复回滚正常应用错误。
- 不在本阶段停止测试环境；测试环境由 `00-238` 继续验证保留。
