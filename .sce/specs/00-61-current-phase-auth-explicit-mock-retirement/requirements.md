# 00-61 当前阶段鉴权显式 Mock 退场（Current Phase Auth Explicit Mock Retirement）

> 状态：已完成 | 优先级：P1 | 依赖：00-28 architecture-driven-delivery-governance，00-48 current-phase-wechat-capability-deferral，00-51 current-phase-formal-sms-capability-deferral，00-58 current-phase-auth-runtime-boundary-alignment
> 记录目的：把当前前端最后残留的 auth 显式 mock 主链从“可演示双轨”推进到“必须直连真实 `/api/auth/*` 与 `/api/user/*`”，避免 `VITE_USE_MOCK=true` 继续伪造登录 / 注册 / 会话恢复已经可用。

## 1. 背景

`00-58` 已经删除前端 runtime capability 表，并把 auth 域收口为“显式 mock 演示态总闸 + 微信独立配置门禁”，但当前仓内仍保留最后一段 auth 显式 mock 主链：

- `kaipai-frontend/src/api/auth.ts` 仍以 `useMock()` 分流 `sendSmsCode / loginByPhone / registerByPhone / loginByWechat / getUserInfo / updateUserRole`
- `kaipai-frontend/src/stores/user.ts` 仍在 `bootstrapSession()` 中保留 `useMock()` 分支，可直接用本地存储伪造会话恢复
- `kaipai-frontend/src/mock/service.ts`
- `kaipai-frontend/src/mock/database.ts`

这会继续制造三个误导：

- 当前阶段登录主链明明已经通过真实环境样本闭环，但源码仍允许“无真实后端也能登录”
- `VITE_USE_MOCK=true` 且缺少 `VITE_API_BASE_URL` 时，登录页仍可能让人误判 auth 能力还可演示
- 仓内仍保留一整套只服务 auth 的本地假用户 / 假邀请数据，干扰后续排障与事实源判断

## 2. 范围

### 2.1 本轮必须处理

- 新增独立 `00-61` Spec，固化当前阶段 auth 显式 mock 退场边界
- 删除 `src/api/auth.ts` 中 `sendSmsCode / loginByPhone / registerByPhone / loginByWechat / getUserInfo / updateUserRole` 的 `useMock()` 分支
- 删除 `src/stores/user.ts` 中会话恢复对 auth mock 的特殊分支
- 收紧 `src/utils/runtime.ts` 中 auth 相关运行时门禁，明确阻止 `VITE_USE_MOCK=true` 但缺少 `VITE_API_BASE_URL` 时继续把登录域当成可验证环境
- 同步调整登录页对微信门禁和开发态验证码的展示逻辑，使其与“auth 只认真实接口”一致
- 删除已无运行时入口的 `src/mock/service.ts`、`src/mock/database.ts`
- 回填 `00-28` 路线图、任务、状态文档、执行入口、Spec 索引与映射

### 2.2 本轮不处理

- 推进正式短信商用能力
- 推进微信 appId/appSecret 真实配置或真实微信样本
- 删除 `useMock()` 总闸在其他能力域中的残留用途
- 重做上传、invite link fallback 或其他非 auth 演示态逻辑

## 3. 需求

### 3.1 当前阶段 auth 事实源

- **R1** 当前阶段 `sendSmsCode / loginByPhone / registerByPhone / loginByWechat` 不得继续保留 `useMock()` 双轨，必须统一调用真实 `/api/auth/*`。
- **R2** 当前阶段 `getUserInfo / updateUserRole` 不得继续保留 `useMock()` 双轨，必须统一调用真实 `/api/user/*`。
- **R3** 当前阶段 `bootstrapSession()` 不得再因为 `VITE_USE_MOCK=true` 而直接接受本地用户快照；会话恢复必须以 token 与真实 `/api/user/me` 为准。
- **R4** 当前阶段登录页若收到开发态 `sendCode` 回包中的验证码，应按真实后端返回直接展示，不得再以 `useMock()` 判定是否弹窗。

### 3.2 运行时门禁

- **R5** 当前阶段若缺少 `VITE_API_BASE_URL`，auth 域必须显式阻塞；`VITE_USE_MOCK=true` 不再构成 auth 可用的充分条件。
- **R6** 当前阶段微信登录入口不得再因为 `useMock()` 而显示可用；是否允许验证仍只由 `VITE_ENABLE_WECHAT_AUTH` 与真实运行时配置门禁决定。
- **R7** 当前阶段若 auth 接口、baseUrl 或 token 有问题，页面必须直接暴露真实错误，不得再由 auth mock 或本地会话恢复掩盖。

### 3.3 Mock 文件退场

- **R8** `src/mock/service.ts`、`src/mock/database.ts` 若已无运行时引用，必须整体删除，避免仓内继续保留 auth 假数据事实源。
- **R9** 其他仍被非 auth 场景使用的 `useMock()` 逻辑不在本轮顺手改写，防止范围失控。

### 3.4 治理回填

- **R10** 必须通过独立 Spec 固化这次 auth 显式 mock 退场，不得只改代码。
- **R11** 必须同步回填 `00-28`，让后续读文档的人能直接看到：当前阶段 login-auth 已不再保留前端 auth mock 主链，`VITE_USE_MOCK=true` 也不能再伪装登录域可用。

## 4. 验收标准

- [x] 已新增独立 `00-61` Spec 并登记索引与映射
- [x] `src/api/auth.ts` 已不再保留 auth mock 分支
- [x] `src/stores/user.ts` 已删除 auth mock 会话恢复分支
- [x] `src/utils/runtime.ts` 与登录页已对齐新的 auth 运行时门禁
- [x] `src/mock/service.ts`、`src/mock/database.ts` 已删除
- [x] `kaipai-frontend npm run type-check` 通过
- [x] `00-28` 状态页、路线图、执行入口与总体评估已明确回填“auth 显式 mock 已退场”
