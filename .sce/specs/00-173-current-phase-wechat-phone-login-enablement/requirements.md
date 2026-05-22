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

## 4. 非功能需求

- 不引入前端 mock 微信登录。
- 不在前端保存或暴露微信 `appSecret`。
- 不改变手机号验证码登录 / 注册主链。
- 不改用户表结构。

## 5. 约束条件

- 小程序 AppID 继续使用 `wx4dcc4e1066fd0fb9`。
- 线上后端必须配置与小程序 AppID 匹配的 `WECHAT_MINIAPP_APP_ID / WECHAT_MINIAPP_APP_SECRET`。
- 本轮不在代码仓库提交真实 appSecret。
