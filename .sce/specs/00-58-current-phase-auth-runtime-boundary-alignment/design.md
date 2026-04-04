# 00-58 设计说明

## 1. 设计原则

- 前端 runtime 不再维护 capability 表
- 显式 mock 演示态只保留一个总闸：`useMock()`
- 微信是否可用继续由专门门禁控制，不再和 runtime capability 混写

## 2. 当前阶段收口边界

| 模块 | 当前阶段策略 | 本轮不做 |
|------|--------------|----------|
| `src/utils/runtime.ts` | 删除 capability 表，只保留 `useMock()`、运行时阻塞与微信门禁 helper | 不改运行时 blocker 文案模型 |
| `src/api/auth.ts` | auth / wechatAuth 统一收口为“显式 mock 演示态或真实接口” | 不删除 mock service 基础数据 |
| `src/pages/login/index.vue` | 继续沿用 `canUseWechatAuth / getWechatAuthBlocker` 作为微信入口门禁 | 不重做页面结构 |

## 3. 实现方案

### 3.1 Runtime 层

- 删除：
  - `ApiCapability`
  - `REMOTE_CAPABILITIES`
  - `useApiMock(...)`
- 保留：
  - `useMock()`
  - `getRuntimeConfigBlocker()`
  - `canUseWechatAuth()`
  - `getWechatAuthBlocker()`

### 3.2 Auth API 层

- `sendSmsCode / loginByPhone / registerByPhone / loginByWechat` 全部改为 `useMock()` 判断
- 微信登录的“是否展示 / 是否允许点击”继续由页面层和 runtime helper 决定，不由 API capability 再做一层语义重复

## 4. 风险与约束

### 4.1 当前阶段真实错误会直接暴露

- 本轮完成后，非显式 mock 环境下 auth 错误只会直接暴露为真实 `/api/auth/*` 错误
- 这是预期行为

### 4.2 后续批次边界不能丢

- 删除 capability 表不等于微信和正式短信已经闭环
- 这两条边界继续由 `00-48 / 00-51` 承接

## 5. 影响文件

- `.sce/specs/00-58-current-phase-auth-runtime-boundary-alignment/requirements.md`
- `.sce/specs/00-58-current-phase-auth-runtime-boundary-alignment/design.md`
- `.sce/specs/00-58-current-phase-auth-runtime-boundary-alignment/tasks.md`
- `.sce/specs/00-58-current-phase-auth-runtime-boundary-alignment/execution.md`
- `.sce/specs/README.md`
- `.sce/specs/spec-code-mapping.md`
- `.sce/specs/00-28-architecture-driven-delivery-governance/tasks.md`
- `.sce/specs/00-28-architecture-driven-delivery-governance/phase-01-roadmap.md`
- `.sce/specs/00-28-architecture-driven-delivery-governance/status/login-auth-status.md`
- `.sce/specs/00-28-architecture-driven-delivery-governance/status/membership-status.md`
- `.sce/specs/00-28-architecture-driven-delivery-governance/status/overall-architecture-assessment.md`
- `kaipai-frontend/src/utils/runtime.ts`
- `kaipai-frontend/src/api/auth.ts`
