# 00-58 当前阶段鉴权运行时边界对齐（Current Phase Auth Runtime Boundary Alignment）

> 状态：已完成 | 优先级：P1 | 依赖：00-28 architecture-driven-delivery-governance，00-48 current-phase-wechat-capability-deferral，00-51 current-phase-formal-sms-capability-deferral，00-57 current-phase-session-upload-runtime-boundary-alignment
> 记录目的：把当前前端 runtime 中最后残留的 `auth / wechatAuth` capability 表收口为“显式 mock 演示态总闸 + 微信独立配置门禁”，避免手机号主链、正式短信后续批次与微信后续批次继续混在 capability 判断里。

## 1. 背景

当前 `00-57` 已把 `userInfo / roleSwitch / upload` 从独立 runtime capability 收口掉，但前端仍保留：

- `src/utils/runtime.ts` 中的 `ApiCapability = 'auth' | 'wechatAuth'`
- `src/api/auth.ts` 中的 `useApiMock('auth')`
- `src/api/auth.ts` 中的 `useApiMock('wechatAuth')`

这会继续造成两个混淆：

- 手机号 `sendCode / login / register` 当前阶段已经闭环，但源码仍把它理解成一个 capability 级别的 mock 分支
- 微信登录当前已由 `00-48` 明确降级为后续批次，真正的门禁应该是 `VITE_ENABLE_WECHAT_AUTH` 与合法配置来源，而不是 capability 表

## 2. 范围

### 2.1 本轮必须处理

- 新增独立 `00-58` Spec，固化当前阶段 auth runtime 边界
- 删除 `src/utils/runtime.ts` 中的 `ApiCapability`、`REMOTE_CAPABILITIES` 与 `useApiMock(...)`
- 将 `src/api/auth.ts` 中的 auth 分支统一收口为：
  - 显式 mock 演示态时走 mock
  - 非显式 mock 环境统一走真实 `/api/auth/*`
- 将 `src/api/auth.ts` 中的微信登录分支统一收口为：
  - 显式 mock 演示态时走 mock
  - 非显式 mock 环境统一走真实 `/api/auth/wechat-login`
  - 真正的是否展示 / 是否允许验证，由 `VITE_ENABLE_WECHAT_AUTH` 和现有门禁 helper 控制
- 回填 `00-28` 路线图、任务、状态文档、Spec 索引与映射

### 2.2 本轮不处理

- 删除 auth mock 基础数据
- 推进正式短信商用能力
- 推进微信真实配置、真实联调或官方小程序码
- 修改 login 页面产品结构

## 3. 需求

### 3.1 当前阶段 runtime 口径

- **R1** 当前阶段 `sendSmsCode / loginByPhone / registerByPhone` 不得继续使用 `useApiMock('auth')`；必须改为“显式 mock 演示态或真实 `/api/auth/*`”。
- **R2** 当前阶段 `loginByWechat` 不得继续使用 `useApiMock('wechatAuth')`；必须改为“显式 mock 演示态或真实 `/api/auth/wechat-login`”。
- **R3** 当前阶段是否允许微信登录，必须继续由 `VITE_ENABLE_WECHAT_AUTH`、`getWechatAuthBlocker()` 与现有配置门禁负责，不得再由 capability 表承担。
- **R4** 当前阶段若 auth 接口、鉴权或环境有问题，页面必须直接暴露真实错误，不得再由 capability 级别分支掩盖。

### 3.2 保留边界

- **R5** 显式 mock 演示态 `VITE_USE_MOCK=true` 仍可保留 auth mock 主链，不在本轮误删。
- **R6** `00-51` 已定义的开发态 `sendCode` 口径仍属于后端真实运行时事实，不因为前端 runtime 边界收口而被误写成正式短信能力完成。
- **R7** `00-48` 已定义的微信能力后续批次入口必须继续保留，不因为 capability 表删除而被误判成“当前阶段必须打通”。

### 3.3 治理回填

- **R8** 必须通过独立 Spec 固化这次 auth runtime 边界对齐，不得只改代码。
- **R9** 必须同步回填 `00-28`，让后续读文档的人能直接看到：前端 runtime 已不再维护 capability 表，剩余的只是“显式 mock 演示态总闸 + 微信配置门禁”。

## 4. 验收标准

- [x] 已新增独立 `00-58` Spec 并登记索引与映射
- [x] `src/utils/runtime.ts` 已删除 `ApiCapability / REMOTE_CAPABILITIES / useApiMock(...)`
- [x] `src/api/auth.ts` 已不再调用 `useApiMock('auth' | 'wechatAuth')`
- [x] `kaipai-frontend npm run type-check` 通过
- [x] `00-28` 状态页和总体评估已明确回填“前端 runtime capability 表已退场”
