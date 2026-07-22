# 00-195 当前阶段小程序手机号快捷登录入口回归定位

## 1. 概述

用户反馈上一版小程序登录页 `pages/login/index` 中存在「手机号快捷登录」，但当前开发者工具截图中仅剩手机号验证码登录表单，没有「手机号快捷登录」入口。

本 Spec 只负责定位和文档沉淀，不修改小程序运行时代码。调查范围限定为：

- `kaipai-frontend/src/pages/login/index.vue`
- `kaipai-frontend/src/api/auth.ts`
- `kaipai-frontend/src/utils/runtime.ts`
- `kaipai-frontend/src/static/icons/wechat-login.png`
- 相关 SCE：`00-173 / 00-187 / 00-188 / 00-190`

## 2. 用户故事

作为产品负责人，我需要知道上一版存在的「手机号快捷登录」入口是被哪个提交删除或隐藏的，以及当时的修改依据。

作为开发者，我需要明确 `00-187` 中哪些记录是正确的，哪些记录把审核整改误扩大为删除入口，避免后续继续沿用错误门禁。

作为审核整改执行者，我需要区分「去微信官方 logo / 去微信品牌化文案」和「删除 `getPhoneNumber` 快捷登录入口」这两类不同动作。

## 3. 功能需求

### 3.1 定位入口回归来源

**描述**：必须通过 git 历史证明「手机号快捷登录」在上一次相关版本中存在，并定位后续被删除的提交。

**验收标准**：

- WHEN 查看 `kaipai-frontend` 历史 THEN 能找到引入或保留 `getPhoneNumber` 手机号快捷登录入口的提交。
- WHEN 查看 `kaipai-frontend` 历史 THEN 能找到把按钮文案改为「手机号快捷登录」的提交。
- WHEN 查看 `kaipai-frontend` 历史 THEN 能找到删除「手机号快捷登录」入口的提交。
- WHEN 输出结论 THEN 明确该入口不是 CSS 隐藏，而是模板、API helper、runtime helper 和图标资源链路被删除。

### 3.2 核对 `pages/login/index` 当前状态

**描述**：必须记录当前 `pages/login/index` 的源码状态，说明当前只存在验证码登录，不存在 `getPhoneNumber` 快捷登录按钮。

**验收标准**：

- WHEN 查看当前 `kaipai-frontend/src/pages/login/index.vue` THEN 记录当前存在 `请输入手机号`、`请输入验证码`、`获取验证码`、`登录 / 注册`。
- WHEN 查看当前 `kaipai-frontend/src/pages/login/index.vue` THEN 记录当前不存在 `getPhoneNumber`、`handleWechatLogin`、`手机号快捷登录`。
- WHEN 输出结论 THEN 不把「短信验证码登录存在」误判为「手机号快捷登录存在」。

### 3.3 记录 00-187 文档冲突

**描述**：必须记录 `00-187` 内部对同一问题存在互相冲突的描述：设计和任务要求保留入口并去品牌化，但 requirements、execution 和验收脚本固化了删除入口。

**验收标准**：

- WHEN 查看 `00-187/design.md` THEN 记录其设计结论是去除官方 logo、文案统一为「手机号快捷登录」。
- WHEN 查看 `00-187/tasks.md` THEN 记录其任务是移除按钮中的 `wechat-login.png`，不是删除按钮。
- WHEN 查看 `00-187/requirements.md` THEN 记录其错误写成「不暴露 `getPhoneNumber` 手机号快速验证入口」。
- WHEN 查看 `00-187/scripts/verify-miniapp-review-login-gate.mjs` THEN 记录其错误把 `getPhoneNumber|手机号快捷登录|phone-quick` 作为失败项。

### 3.4 给出后续修复边界

**描述**：本 Spec 只产出定位结论，不直接恢复按钮。后续如恢复入口，应另起修复 Spec 或在本 Spec 补充执行任务。

**验收标准**：

- WHEN 本轮完成 THEN 不修改 `kaipai-frontend` 运行时代码。
- WHEN 本轮完成 THEN 更新 `.sce/specs/README.md` 和 `.sce/specs/spec-code-mapping.md`。
- WHEN 本轮完成 THEN 在 `execution.md` 中明确后续修复建议：恢复 `getPhoneNumber` 入口时必须移除官方 logo、避免「微信登录 / 微信一键登录 / 微信授权」可见文案，并同步修正 00-187 验收脚本。

## 4. 非功能需求

- 不写入手机号、验证码、JWT 或其他敏感数据。
- 不重跑生产发布，不触发小程序上传或提审。
- 不改动 `kaipai-frontend` 源码，避免把调查记录和修复代码混在同一轮。

## 5. 约束条件

- 调查以 `kaipai-frontend` 子仓库 git 历史为准。
- 根仓库当前已有 `00-194` 未提交文档变更，本轮只追加 `00-195` 和索引，不回滚或覆盖既有变更。
- 当前日期为 `2026-07-10`，所有 git 提交时间必须按绝对时间记录。
