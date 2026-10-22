# 微信体验版测试 Candidate 上传

## 1. 概述

将已通过全栈测试准入的 Candidate `20260902-145540-v3-draft` 上传到微信小程序开发版本，作为本轮体验版测试候选。上传对象固定为唯一测试运行入口 `kaipai-frontend/dist/dev/mp-weixin`，不得重新构建、切换环境或使用正式 API 产物。

## 2. 用户故事

- 作为测试负责人，我希望在手机体验版中验证与本地人工验收相同的冻结 Candidate。
- 作为生产维护者，我希望体验版上传不触发正式数据库、容器、Nginx、审核或正式发布操作。
- 作为电脑使用者，我希望上传期间微信开发者工具不置顶、不抢焦点，电脑保持正常使用。

## 3. 功能需求

### 3.1 上传对象

- Candidate 必须为 `20260902-145540-v3-draft`，最终准入必须返回 `READY_FOR_MANUAL_ACCEPTANCE / exit 0`。
- 上传目录必须为 `D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin`。
- 上传前目录必须保持 `329 / 2,041,422 / d1528b66647a79dacf19eb1ed0d3f6d165249b51a19e978e0a3c1fbdf6316f1e`。
- 产物只允许命中 `https://test-api.kplyyk.com`，本地和正式 API 命中必须为 0。

### 3.2 上传身份

- AppID 必须为 `wx4dcc4e1066fd0fb9`。
- 上传版本固定为 `3.0.0.20260902.145540`。
- 上传说明必须绑定 Candidate ID，不使用“正式版”“生产发布”等描述。
- 微信 CLI 登录状态必须在上传前通过。

### 3.3 非干扰上传

- 使用微信开发者工具 CLI 的 `upload` 命令，不调用会打开或揭示可见窗口的 MCP 工具。
- 不传入会启动新 IDE 窗口的 `--port`，复用当前已运行的微信工具服务。
- 不置顶、不强制前台、不抢焦点，不使用桌面截图、坐标、鼠标或键盘自动化。

### 3.4 上传结果

- CLI 退出码必须为 0，并将 `--info-output` 回执保存到 Candidate 记录目录。
- 回执必须能关联 AppID、上传版本、上传时间或代码包结果。
- 按本轮用户确认，体验测试提交以微信开发者工具 `upload` 返回成功为完成条件；公众平台版本管理不属于本轮操作入口。

### 3.5 生产边界

- 不执行 `00-237`。
- 不迁移生产数据库，不重建生产容器，不修改生产 Nginx。
- 不构建或上传正式 API 小程序，不提交审核，不发布正式版本。

## 4. 验收标准

- 上传前 Candidate 门禁、目录树和 API 目标均通过。
- CLI upload 返回 exit 0，上传回执已归档并通过 SHA256 校验。
- 上传后本地固定运行目录哈希不变。
- `desktopTopmost / desktopFocusControl / desktopAutomation` 均保持 false。
- 生产容器未变且 `PRODUCTION_MUTATION=NONE`。

## 5. 约束

- 微信公众平台的 request/upload/download 合法域名无法从仓库独立读取；体验版真机请求结果作为域名最终验收。
- 本 Spec 只处理测试 Candidate 上传，不构成正式发布授权。
