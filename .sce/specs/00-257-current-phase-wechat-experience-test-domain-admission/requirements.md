# 微信体验版测试域名准入修复

> 状态：实施中。
>
> 上游：`00-230`、`00-234`、`00-236`、`00-256`。

## 1. 概述

Candidate `20260902-145540-v3-draft` 已通过微信开发者工具 CLI 上传，但手机体验版未登录进入素材库时显示 `request:fail url not in domain list`。本 Spec 修复 AppID `wx4dcc4e1066fd0fb9` 的测试 API 服务器域名准入，不修改小程序代码、冻结产物或生产运行时。

## 2. 用户故事

- 作为体验测试人员，我希望手机体验版能访问测试 API，并继续进入正常的未登录业务流程。
- 作为生产维护者，我希望增加测试域名时完整保留现有生产域名和 websocket 域名，不中断正式小程序使用。
- 作为电脑使用者，我希望修复全程通过微信 API/CLI 完成，不置顶或控制微信开发者工具。

## 3. 功能需求

### 3.1 基线与凭据

- 仅从 gitignore 的 `.sce/config/local-secrets/wechat-miniapp.env` 读取 AppID/AppSecret。
- AppID 必须等于 `wx4dcc4e1066fd0fb9`；任何日志和证据不得包含 AppSecret 或 access token。
- 修改前通过微信 API 读回 request、upload、download、websocket 等全部服务器域名并保存脱敏原始响应及 SHA256。

### 3.2 只增不删

- 只向 `requestdomain`、`uploaddomain`、`downloaddomain` 增加 `https://test-api.kplyyk.com`。
- 使用增量 `add` 语义；不得用不完整列表覆盖远端配置。
- 原有 request、upload、download、websocket 及其他返回域名逐项保留，任一基线项消失即失败。

### 3.3 素材域名核对

- 从体验 Candidate 与测试 API 合同识别实际资源主机名，不凭经验猜测 COS 域名。
- 只有实际真机下载/预览所需且属于测试环境的 HTTPS 主机才允许登记；本轮未证明需要的域名不修改。

### 3.4 验证与回滚

- 修改后再次读回远端配置，确认三个目标列表均包含测试 API，所有基线域名均未减少。
- 保存 `ORIGINAL_FILE.json`、`MODIFIED_FILE.json`、`DIFF_FILE.patch`、`VERIFICATION.txt` 和可执行 `ROLLBACK.sh`。
- 回滚逻辑只在独立副本上演练；远端保持增加后的配置，除非后续明确授权回滚。
- 用户在手机体验版点击“重新加载”后，错误应退出微信域名门禁并进入测试 API 的正常响应。

### 3.5 生产与桌面边界

- 不执行 `00-237`，不修改生产数据库、容器、Nginx、正式 API 或正式小程序版本。
- 共享 AppID 的原有域名必须完整保留；外部变更只有测试域名增量。
- 不打开、置顶、强制前台或控制微信开发者工具；不使用桌面截图、坐标、鼠标或键盘自动化。

## 4. 发版兼容

本次不改变代码、接口、数据库或 Candidate 字节。合法域名为向后兼容增量：旧正式版本继续使用原有域名，体验版新增访问测试 API 的权限。

## 5. 验收标准

- 微信 API 基线读回成功且凭据未泄露。
- 三个目标域名列表读回均包含 `https://test-api.kplyyk.com`。
- 所有修改前域名均存在于修改后读回结果，websocket 列表完全不变。
- 独立副本回滚恢复为原始 JSON，实际远端仍保持修改态。
- `00-236` 记录当前体验版阻断及修复结果，正式发布仍为 `NOT_AUTHORIZED`。
