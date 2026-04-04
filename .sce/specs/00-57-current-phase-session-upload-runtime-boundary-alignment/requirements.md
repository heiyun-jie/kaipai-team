# 00-57 当前阶段会话摘要 / 身份切换 / 上传运行时边界对齐（Current Phase Session Upload Runtime Boundary Alignment）

> 状态：已完成 | 优先级：P1 | 依赖：00-28 architecture-driven-delivery-governance，00-48 current-phase-wechat-capability-deferral，00-51 current-phase-formal-sms-capability-deferral，00-56 current-phase-level-card-ai-runtime-mock-retirement
> 记录目的：把 `/api/user/me`、`/api/user/role` 与 `/api/file/upload/*` 的当前阶段口径，从“仍保留独立 capability 双轨”收口为“真实能力默认直连，显式 mock 仅保留给 auth 演示态”，避免会话摘要、身份切换和上传链继续以独立 mock 能力存在。

## 1. 背景

当前 `00-56` 已把 `level / card / ai` 前端运行时双轨退场，但前端 runtime 仍保留三项 capability：

- `userInfo`
- `roleSwitch`
- `upload`

同时源码里仍有：

- `src/api/auth.ts` 用 `useApiMock('userInfo') / useApiMock('roleSwitch')`
- `src/utils/upload.ts` 用 `useApiMock('upload')`

这会继续制造两个误导：

- 登录鉴权当前阶段明明已通过 `/api/user/me` 样本闭环，但源码仍把会话摘要与身份切换理解成独立 mock 能力
- 上传接口和后端 `FileController` 已存在，但前端 runtime 仍暗示上传能力是一个独立可回退 mock 的当前阶段口子

## 2. 范围

### 2.1 本轮必须处理

- 新增独立 `00-57` Spec，固化当前阶段会话摘要 / 身份切换 / 上传运行时边界
- 将 `src/api/auth.ts` 中 `getUserInfo / updateUserRole` 的双轨收口为：
  - 显式 mock 演示态继续走本地 mock
  - 非显式 mock 环境统一走真实 `/api/user/me`、`/api/user/role`
- 将 `src/utils/upload.ts` 中 `upload` 双轨收口为：
  - 显式 mock 演示态继续走本地 filePath 回显
  - 非显式 mock 环境统一走真实 `/api/file/upload/*`
- 删除 `src/utils/runtime.ts` 中已无必要的 `userInfo / roleSwitch / upload` capability
- 回填 `00-28` 路线图、任务、状态文档、Spec 索引与映射

### 2.2 本轮不处理

- 删除 `auth` mock 主链
- 删除 `wechatAuth` mock 分支
- 推进正式短信或微信登录真实配置
- 重做上传后端能力、对象存储实现或图片/视频页面 UI

## 3. 需求

### 3.1 当前阶段真实能力口径

- **R1** 当前阶段 `getUserInfo()` 不得继续以 `useApiMock('userInfo')` 作为独立能力判断；除显式 mock 演示态外，必须统一调用 `GET /api/user/me`。
- **R2** 当前阶段 `updateUserRole()` 不得继续以 `useApiMock('roleSwitch')` 作为独立能力判断；除显式 mock 演示态外，必须统一调用 `PUT /api/user/role`。
- **R3** 当前阶段 `uploadFile()` 不得继续以 `useApiMock('upload')` 作为独立能力判断；除显式 mock 演示态外，必须统一调用：
  - `POST /api/file/upload/avatar`
  - `POST /api/file/upload/photo`
  - `POST /api/file/upload/video`
  - `POST /api/file/upload/license`
- **R4** 当前阶段若这些接口、鉴权或环境有问题，页面必须直接暴露真实错误，不得再由独立 `userInfo / roleSwitch / upload` capability 掩盖。

### 3.2 当前阶段保留边界

- **R5** `sendCode / login / register` 当前仍属于 `auth` 域的显式 mock 演示能力，不在本轮误删。
- **R6** `wechat-login` 当前仍属于 `wechatAuth` 后续能力批次，不在本轮误删。
- **R7** `src/mock/service.ts` 中 `getUserInfoMock / updateUserRoleMock` 只要仍服务于显式 mock auth 演示态，可继续保留，不在本轮误删。
- **R8** `src/utils/runtime.ts` 中 `userInfo / roleSwitch / upload` capability 必须删除，避免继续把它们理解为独立运行时双轨。

### 3.3 治理回填

- **R9** 必须通过独立 Spec 固化这次会话摘要 / 身份切换 / 上传运行时边界对齐，不得只改代码。
- **R10** 必须同步回填 `00-28`，让后续读文档的人能直接看到：当前阶段剩余显式 mock 已进一步收口到 `auth / wechatAuth` 域，而不是散落在 session / upload 运行时能力表。

## 4. 验收标准

- [x] 已新增独立 `00-57` Spec 并登记索引与映射
- [x] `src/api/auth.ts` 已不再使用 `useApiMock('userInfo' | 'roleSwitch')`
- [x] `src/utils/upload.ts` 已不再使用 `useApiMock('upload')`
- [x] `src/utils/runtime.ts` 已删除 `userInfo / roleSwitch / upload` capability
- [x] `kaipai-frontend npm run type-check` 通过
- [x] `00-28` 状态页和总体评估已明确回填“session / upload 当前阶段已不再保留独立 runtime capability”
