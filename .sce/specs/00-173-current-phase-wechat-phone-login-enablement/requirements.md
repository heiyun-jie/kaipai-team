# 00-173 当前阶段微信手机号一键登录启用

## 1. 概述

用户已在微信后台开通手机号授权能力。当前项目仍因前端构建开关关闭、后端微信自动注册身份不完整，导致“微信一键登录”不能作为真实登录入口使用。

本 Spec 负责把微信手机号一键登录从“配置门禁保留入口”推进到“当前小程序真实可用入口”。

## 2. 用户故事

作为新用户，我希望在登录页勾选协议后点击“微信一键登录”，授权手机号即可完成登录或注册，并进入小程序主流程。

作为已注册用户，我希望授权的微信手机号如果已存在账号，可以直接登录，不需要再输入短信验证码。

作为运维人员，我希望后端对微信配置缺失、微信接口失败和手机号缺失给出明确错误，便于线上排障。

## 3. 功能需求

### 3.1 小程序入口启用

**描述**：小程序正式构建默认启用微信手机号登录入口；只有显式配置 `VITE_ENABLE_WECHAT_AUTH=false` 时才关闭。

**验收标准**：

- WHEN `VITE_API_BASE_URL` 已配置且未显式设置 `VITE_ENABLE_WECHAT_AUTH=false` THEN 登录页微信按钮应挂载 `open-type="getPhoneNumber"`。
- WHEN 用户未勾选协议 THEN 点击微信登录不应直接发起手机号授权，应先提示协议确认。
- WHEN 用户勾选协议并点击微信登录 THEN 小程序应调用微信 `getPhoneNumber` 授权流程。

### 3.2 前端请求合同

**描述**：前端使用微信 `getPhoneNumber` 返回的 `code` 调用 `/api/auth/wechat-login`，并保留邀请码与设备指纹。

**验收标准**：

- WHEN 微信返回 `getPhoneNumber:ok` 和 `code` THEN 前端请求体包含 `code`、`inviteCode`、`deviceFingerprint`。
- WHEN 微信拒绝授权或未返回 code THEN 页面展示明确错误，不向后端发送空 code。
- WHEN 后端返回 token 和用户信息 THEN 前端写入登录态并进入演员或剧组主流程。

### 3.3 后端微信手机号换取

**描述**：后端使用小程序 `appId/appSecret` 获取 access token，并调用微信 `wxa/business/getuserphonenumber` 换取手机号。

**验收标准**：

- WHEN `WECHAT_MINIAPP_APP_ID` 或 `WECHAT_MINIAPP_APP_SECRET` 缺失 THEN `/api/auth/wechat-login` 返回“微信登录未配置小程序 appId/appSecret”。
- WHEN 微信接口返回错误 THEN 后端返回包含微信错误信息的业务错误。
- WHEN 微信返回 `purePhoneNumber` 或 `phoneNumber` THEN 后端使用该手机号登录或注册。

### 3.4 微信首次注册身份

**描述**：微信手机号首次登录自动注册时，后端必须创建移动端可用身份。

**验收标准**：

- WHEN 授权手机号尚未注册 THEN 后端自动创建账号，`registerSource=3`，默认 `userType=1` 演员。
- WHEN 授权手机号已注册 THEN 后端不覆盖既有 `userType`，只刷新登录时间。
- WHEN 后端返回新账号 THEN 前端不应因 `userType=0` 把用户踢出移动端。

### 3.5 本地后端微信配置启动门禁

**描述**：当小程序开发产物请求本地 `http://127.0.0.1:8010` 时，本地后端必须通过统一脚本读取并校验 gitignored 微信配置，禁止继续使用未注入配置的裸 `java -jar` 启动方式。

**验收标准**：

- WHEN `.sce/config/local-secrets/wechat-miniapp.env` 或主启动器进程环境包含合法且成组的 `WECHAT_MINIAPP_APP_ID / WECHAT_MINIAPP_APP_SECRET` THEN `scripts/start-local-backend.ps1` 应通过隔离子启动器环境向 Java 传播配置，且不得修改主启动器自身的进程环境。
- WHEN `kaipai-frontend/project.config.json` 缺失、appId 大小写敏感比对不一致、appSecret 缺失或仍为 placeholder THEN 启动脚本必须在创建 Java 进程前失败。
- WHEN 同一 workspace / port 已有启动器处于运行中 THEN 后续启动必须由命名互斥锁拒绝；WHEN 不同 port 并发启动 THEN PID 与日志产物必须按 port 隔离。
- WHEN `-Restart` 检查已有 listener THEN 只有全部 owner 同时匹配规范化完整 jar 路径、精确 `--server.port` 和原启动时间后才能进入统一停止阶段，任一 owner 不匹配时不得停止任何 owner。
- WHEN 新 Java 已创建 THEN 正式 `backend.pid` 只能在 `/api/v3/api-docs/swagger-config` 直接返回 `200 application/json`、`url/configUrl` 合同匹配且请求前后 listener owner 均为同一新 PID 后原子发布。
- WHEN 本地后端通过统一脚本启动 THEN 使用无效微信手机号授权 code 探测 `/api/auth/wechat-login` 时，应进入微信接口错误分支，不得再返回“微信登录未配置小程序 appId/appSecret”。
- WHEN 启动脚本运行 THEN appSecret 不得出现在 PowerShell / Java 命令行参数、控制台输出、日志、Spec 或 Git 跟踪文件中；隔离子启动器在 Java 创建后必须清除自身的微信凭据环境值。

## 4. 非功能需求

- 不引入前端 mock 微信登录。
- 不在前端保存或暴露微信 `appSecret`。
- 不在本地后端命令行、日志或 Git 跟踪文件中暴露微信 `appSecret`。
- 不改变手机号验证码登录 / 注册主链。
- 不改用户表结构。

## 5. 约束条件

- 小程序 AppID 继续使用 `wx4dcc4e1066fd0fb9`。
- 线上后端必须配置与小程序 AppID 匹配的 `WECHAT_MINIAPP_APP_ID / WECHAT_MINIAPP_APP_SECRET`。
- 本地 `8010` 后端必须通过 `kaipaile-server/scripts/start-local-backend.ps1` 启动；真实值继续只存放在 `.sce/config/local-secrets/wechat-miniapp.env` 或进程环境中。
- 本轮不在代码仓库提交真实 appSecret。
