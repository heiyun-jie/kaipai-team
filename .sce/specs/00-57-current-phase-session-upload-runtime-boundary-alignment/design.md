# 00-57 设计说明

## 1. 设计原则

- 当前阶段真实能力默认直连，不再为 `userInfo / roleSwitch / upload` 保留独立 runtime capability
- 显式 mock 演示态仍可用，但只收口到 auth 域统一开关，不再把 session / upload 拆成独立双轨
- 不混入微信登录、正式短信或上传后端能力重做

## 2. 当前阶段收口边界

| 模块 | 当前阶段策略 | 本轮不做 |
|------|--------------|----------|
| `src/api/auth.ts` | `getUserInfo / updateUserRole` 非显式 mock 环境统一走真实 `/api/user/*` | 不删除 `sendCode / login / register / wechat-login` mock 边界 |
| `src/utils/upload.ts` | 非显式 mock 环境统一走真实 `/api/file/upload/*` | 不重做上传 UI 和后端 COS 实现 |
| `src/utils/runtime.ts` | 删除 `userInfo / roleSwitch / upload` capability | 保留 `auth / wechatAuth` |
| `src/mock/service.ts` | 保留 auth 显式 mock 仍依赖的 `getUserInfoMock / updateUserRoleMock` | 不误删 auth 演示态基础逻辑 |

## 3. 实现方案

### 3.1 Session 摘要 / 身份切换

- `src/api/auth.ts` 中：
  - `getUserInfo()` 改为 `useMock() ? getUserInfoMock() : GET /api/user/me`
  - `updateUserRole()` 改为 `useMock() ? updateUserRoleMock() : PUT /api/user/role`
- 这样会把当前阶段真实环境口径统一压到 `/user/*`，同时让显式 mock 演示态继续可用

### 3.2 上传

- `src/utils/upload.ts` 改为 `useMock()` 判断，而不是 `useApiMock('upload')`
- 当前阶段真实环境默认直连 `/api/file/upload/*`
- 显式 mock 演示态保留本地 filePath 回显，以便本地 demo 不断链

### 3.3 Runtime 能力表

- `ApiCapability` 删除：
  - `userInfo`
  - `roleSwitch`
  - `upload`
- `REMOTE_CAPABILITIES` 同步删除这三项

## 4. 风险与约束

### 4.1 当前阶段真实错误会直接暴露

- 本轮完成后，`/api/user/me`、`/api/user/role`、`/api/file/upload/*` 的问题会直接暴露为真实错误
- 这是预期行为，用来阻止 session / upload 继续伪装成独立 mock 可兜底能力

### 4.2 auth 域边界不能被误删

- 当前阶段手机号主链虽已闭环，但 `sendCode` 与微信登录仍分别受 `00-51 / 00-48` 约束
- 本轮只收 session / upload 的 runtime boundary，不动这两条后续批次入口

## 5. 影响文件

- `.sce/specs/00-57-current-phase-session-upload-runtime-boundary-alignment/requirements.md`
- `.sce/specs/00-57-current-phase-session-upload-runtime-boundary-alignment/design.md`
- `.sce/specs/00-57-current-phase-session-upload-runtime-boundary-alignment/tasks.md`
- `.sce/specs/00-57-current-phase-session-upload-runtime-boundary-alignment/execution.md`
- `.sce/specs/README.md`
- `.sce/specs/spec-code-mapping.md`
- `.sce/specs/00-28-architecture-driven-delivery-governance/tasks.md`
- `.sce/specs/00-28-architecture-driven-delivery-governance/phase-01-roadmap.md`
- `.sce/specs/00-28-architecture-driven-delivery-governance/status/login-auth-status.md`
- `.sce/specs/00-28-architecture-driven-delivery-governance/status/crew-company-project-status.md`
- `.sce/specs/00-28-architecture-driven-delivery-governance/status/membership-status.md`
- `.sce/specs/00-28-architecture-driven-delivery-governance/status/overall-architecture-assessment.md`
- `kaipai-frontend/src/api/auth.ts`
- `kaipai-frontend/src/utils/upload.ts`
- `kaipai-frontend/src/utils/runtime.ts`
