# 正式短信 future batch 样本模板

## 1. 样本头信息

- Environment:
- Sample Label:
- Validate At:
- Operator:
- SMS Provider:
- Channel / Template Id:
- Runtime Config Source:

## 2. 样本上下文

- Success Phone:
- Failure Phone:
- Request Window:
- Request Id / Biz Id / Trace Id:
- share-card bridge sample:
- Related release record:

## 3. 成功发送样本

### 3.1 sendCode 请求

- Request:
  - `POST /api/auth/sendCode`
  - phone:
  - headers:
  - body:

### 3.2 sendCode 返回

- HTTP Status:
- code:
- message:
- provider receipt / biz id:
- 是否仍直返验证码:

### 3.3 成功样本结论

- 是否确认已真正发送短信:
- 送达证据:
- 失败重试是否触发:

## 4. 失败 / 阻塞样本

### 4.1 请求上下文

- Failure Type:
  - 频控 / 模板错误 / 签名错误 / 通道异常 / 手机号不可达 / 其它
- Phone:
- Request:

### 4.2 返回与治理口径

- HTTP Status:
- code:
- message:
- provider error code:
- 是否暴露业务可读错误:
- 是否可区分配置问题 / 频控问题 / 通道问题:

### 4.3 失败样本结论

- 是否符合预期:
- 是否留下可追踪 request id / trace id:
- 是否具备后续治理入口:

## 5. 配置来源证据

- compose env:
- nacos dataId:
- secret file / env key:
- 当前环境是否确认切到正式短信配置:
- 回读命令 / 只读诊断记录:

## 6. 登录回归证据

在短信口径变更后，至少再验证一条主链：

- `sendCode -> login -> user.me`

若当前业务还要求证明 share-card 未受影响，再补：

- `/card/my-cards`
- `/card/personalization?shareCardId=...`

记录：

- login userId:
- user.me userId:
- shareCardId:
- personalization status:

## 7. 页面 / 终态证据

- 登录页截图:
- 验证码发送成功提示截图:
- 验证码发送失败提示截图:
- 页面级 blocker / 降级提示截图:

## 8. 判定

- Current Status:
  - `未进入正式短信验证`
  - `已进入正式短信验证`
  - `正式短信能力闭环完成`
- Confirmed:
  -
- Blockers:
  -
- Next Action:
  -

## 9. 最低通过条件

只有同时满足以下条件，才允许把样本判成“正式短信能力闭环完成”：

- `sendCode` 不再直返验证码
- 至少有 1 个成功发送样本
- 若环境允许，至少有 1 个失败 / 阻塞样本
- 配置来源证据清楚
- `sendCode -> login -> user.me` 主链未受影响

## 10. 建议落盘文件

- `summary.md`
- `captures/send-code-success.json`
- `captures/send-code-failure.json`
- `captures/runtime-config-source.json`
- `captures/login-after-send-code.json`
- `screenshots/login-page.png`
- `screenshots/send-code-success.png`
- `screenshots/send-code-failure.png`
