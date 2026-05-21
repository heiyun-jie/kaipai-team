# Share Card MVP 与正式短信能力桥接说明

## 1. 目的

`share-card-mvp` 当前业务链已经收口到：

- API / 治理样本
- 小程序页面样本
- 后台页面样本
- 发布后检查清单与执行结果留档

当前唯一仍被反复提及的能力缺口，是：

- `sendCode` 仍返回开发态验证码

这件事不应继续在 share-card 域内被反复口头描述，而应显式桥接到：

- `00-51 current-phase-formal-sms-capability-deferral`
- `execution/login-auth/`

## 2. 当前桥接入口

### 2.1 上位 Spec

- `D:\XM\kaipai-team\.sce\specs\00-51-current-phase-formal-sms-capability-deferral\requirements.md`
- `D:\XM\kaipai-team\.sce\specs\00-51-current-phase-formal-sms-capability-deferral\design.md`
- `D:\XM\kaipai-team\.sce\specs\00-51-current-phase-formal-sms-capability-deferral\execution.md`

### 2.2 当前桥接样本

- `D:\XM\kaipai-team\.sce\specs\00-28-architecture-driven-delivery-governance\execution\login-auth\samples\20260405-233350-dev-share-card-sms-bridge\summary.md`

### 2.3 当前桥接脚本

- `D:\XM\kaipai-team\.sce\specs\00-28-architecture-driven-delivery-governance\execution\login-auth\run-login-auth-phone-session-sample.py`

### 2.4 正式短信验证门禁

- `D:\XM\kaipai-team\.sce\specs\00-28-architecture-driven-delivery-governance\execution\login-auth\formal-sms-validation-gate.md`

### 2.5 正式短信 future batch 样本模板

- `D:\XM\kaipai-team\.sce\specs\00-28-architecture-driven-delivery-governance\execution\login-auth\formal-sms-validation-sample-template.md`

## 3. 当前桥接样本证明了什么

当前样本已证明：

- `POST /api/auth/sendCode` 当前可达
- `sendCode -> login -> user.me -> verify.status -> invite.stats -> level.info` 可正常走通
- 样本已改为兼容 share-card 当前主线：
  - 先回读 `/card/my-cards`
  - 再解析默认 `general` 卡 `shareCardId`
  - 再调用 `/card/personalization?shareCardId=...`

当前样本还明确固定了：

- `sendCode` 返回 `code=200`
- `message=验证码发送成功`
- 但 `data` 仍直接暴露开发态验证码

## 4. 当前桥接样本不能证明什么

当前样本 **不能** 证明：

- 正式短信服务商已接入
- 短信真实送达稳定
- 发送失败治理已闭环
- 频控 / 模板 / 通道配置已商用

因此当前 share-card 域内应统一口径：

- 可以证明登录与会话接口接通
- 不能据此宣告正式短信能力闭环

## 5. 推荐使用方式

当 share-card 发布后需要判断“当前还缺什么”时，固定按下面顺序看：

1. `evidence-bundle-index.md`
2. `release-post-checklist.md`
3. 若唯一剩余问题仍是 `sendCode` 口径，再看本文件
4. 再跳转 `execution/login-auth/samples/20260405-233350-dev-share-card-sms-bridge/summary.md`
5. 若要判断是否已具备正式短信验证前提，再跳 `execution/login-auth/formal-sms-validation-gate.md`
6. 若准备正式进入 future batch 样本建设，再跳 `execution/login-auth/formal-sms-validation-sample-template.md`

## 6. 当前结论

对 share-card 当前阶段来说：

- `sendCode` 开发态直返验证码，是**外部已知能力缺口**
- 它当前应通过 `00-51 + login-auth bridge sample` 承接
- 不应再在 share-card 主业务链里被误写成“未联通”或“主链未闭环”

## 7. 后续何时重进正式短信治理

只有在下面情况之一出现时，才需要从 share-card 回到正式短信批次：

1. 明确要推进真实短信商用能力
2. 发布后 `sendCode` 不再稳定返回 `200`
3. 登录 / 注册主链因短信口径变化再次受阻
4. 用户明确要求把正式短信能力纳入当前批次验收
