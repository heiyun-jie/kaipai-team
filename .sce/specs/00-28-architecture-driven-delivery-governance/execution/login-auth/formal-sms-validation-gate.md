# 正式短信能力验证门禁说明

## 1. 目的

本文件用于明确：

- 什么情况下才允许把 `sendCode` 从“开发态直返验证码”推进到“正式短信能力验证”
- 进入正式短信验证前，必须先具备哪些前提
- 正式短信验证完成后，至少要留下哪些证据

当前它对应的上位入口是：

- `D:\XM\kaipai-team\.sce\specs\00-51-current-phase-formal-sms-capability-deferral\requirements.md`

## 2. 当前事实

当前 dev 运行时已知事实：

- `POST /api/auth/sendCode` 可返回 `code=200`
- 但 `data` 仍直接返回验证码

当前事实已经被下面样本固定：

- `D:\XM\kaipai-team\.sce\specs\00-28-architecture-driven-delivery-governance\execution\login-auth\samples\20260405-233350-dev-share-card-sms-bridge\summary.md`

这说明：

- 登录 / 注册主链接口接通
- 不能说明正式短信已经闭环

## 3. 何时允许进入正式短信验证

只有同时满足以下条件，才允许把“正式短信能力”当作当前批次验证目标：

### 3.1 运行时条件

- 后端已切到目标环境最新版本
- 小程序 / H5 / 后台确认指向同一环境
- `sendCode` 不再直接在 `data` 字段返回验证码

### 3.2 配置条件

- 已明确短信服务商 / 通道
- 已明确短信模板 ID 或模板编码
- 已明确运行时所用配置来源：
  - compose env
  - Nacos
  - 远端 secret
- 已明确频控 / 限流 / 失败重试的最小口径

### 3.3 样本条件

- 至少准备 2 个手机号：
  - 1 个正常可收短信样本
  - 1 个异常 / 不可达 / 触发失败口径样本（若环境允许）
- 至少准备 1 组可追踪的时间窗与 request id

## 4. 进入正式短信验证前必须先跑什么

### 4.1 先跑当前桥接样本

先执行：

```powershell
python .sce/specs/00-28-architecture-driven-delivery-governance/execution/login-auth/run-login-auth-phone-session-sample.py --label share-card-sms-bridge
```

目的：

- 证明当前 auth 主链仍可跑通
- 证明 share-card 当前主链也没有因为 auth 口径变化而断掉

### 4.2 再做 live probe

再执行：

```powershell
powershell -File .sce/specs/00-28-architecture-driven-delivery-governance/execution/login-auth/run-login-auth-validation.ps1 -EnableLiveProbe
```

目的：

- 固定 `sendCode` 的真实返回
- 确认当前到底还是开发态直返，还是已经变成真实短信发送口径

## 5. 正式短信验证至少要留下哪些证据

至少要有 4 组证据：

### 5.1 请求证据

- `POST /api/auth/sendCode`
- 请求手机号
- 请求时间
- 返回 `code/message`
- 若有 requestId / bizId / traceId，必须落盘

### 5.2 结果证据

- 成功发送样本
- 若环境允许，再补 1 组失败样本
- 失败时不能只记录“失败了”，必须记录：
  - 错误码
  - 错误信息
  - 是否为频控
  - 是否为模板/签名/通道问题

### 5.3 登录链证据

- `sendCode -> login -> user.me`
- 证明短信口径变更后，登录主链仍可继续

### 5.4 配置来源证据

- compose / env / nacos 配置来源
- 目标 dataId 或变量名
- 当前环境是否真的切到了正式短信配置

## 6. 当前不能误判为正式短信闭环的情况

满足以下任一条，都不能写“正式短信能力闭环完成”：

- `sendCode` 仍直接返回验证码
- 只有接口 `200`，没有真实发送/失败口径
- 没有配置来源证据
- 没有登录主链回归样本
- 只有成功样本，没有任何失败/阻塞口径说明

## 7. 推荐留档位置

当未来真的推进正式短信能力时，建议最少新增：

1. `execution/login-auth/samples/<timestamp>-formal-sms-validation/summary.md`
2. `captures/send-code-success.json`
3. `captures/send-code-failure.json`（如果环境允许）
4. `captures/runtime-config-source.json`
5. `formal-sms-validation-sample-template.md`

## 8. 与 share-card 的关系

对 share-card 当前阶段来说：

- 这件事只应视为“外部剩余能力缺口”
- 不应重新降级 share-card 当前主链结论

share-card 当前桥接入口：

- `D:\XM\kaipai-team\.sce\specs\00-28-architecture-driven-delivery-governance\execution\share-card-mvp\sms-capability-bridge.md`

因此后续判断顺序应固定为：

1. 先看 share-card 总包与检查清单
2. 若唯一剩余问题仍是 `sendCode`
3. 再跳到本文件判断是否已具备正式短信验证前提
