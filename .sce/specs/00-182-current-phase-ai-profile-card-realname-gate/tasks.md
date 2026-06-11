# 00-182 当前阶段 AI 分享图生成实名门禁 - 任务拆解

> 执行原则：一次一个任务，执行后更新状态并等待审核。

## 任务列表

### T1 后端 generate 接口补实名门禁 ✅
**Validates: Requirements 3.1, 3.3** — commit `6cb95dc`

- [x] ~~注入 `IdentityVerificationService`~~ → 实际复用 `ActorProfileDTO.isCertified`（`actorProfileService.mine()` 已返回，免额外注入与 DB 读取，行为等价）
- [x] 实名门禁校验：`!profile.getIsCertified()` 时抛 `BizException(NOT_CERTIFIED, "完成实名认证后才可生成 AI 分享图")`，沿用 `AiController` 既有 `NOT_CERTIFIED` 模式（单布尔分支，未按 1/3 分文案）
- [x] 校验置于 `templateSceneCode` 之后、`requireProfileEntity` / `resolveSourceImage` 之前
- [x] 未实名时在 `save(task)` / `aiProfileCardTaskExecutor.execute` 之前抛出，确认不落表、不触发异步
- [x] `kaipaile-server` 编译通过（后台任务 `bzsu0c4ba`，exit 0）

> 差异详见 `execution.md`「与 design.md 的差异」。

### T2 前端 handleGenerate 补实名前置判断 ✅
**Validates: Requirements 3.2, 3.3** — commit `57212a1` + `7d2e466`

- [x] `handleGenerate()` 插入 `!userStore.isCertified` 实名判断（位置在「选风格」之后、上传 / 分析图校验之前，比设计更前置）
- [ ] ⚠️ **未实现**：调用前 `await userStore.syncVerificationStatus()`。实际直接读 `userStore.isCertified`。后端为最终事实源故无安全风险；刚实名用户本地态未刷新时可能被前端多拦一次，属体验边界，详见 `execution.md`
- [x] 未实名弹 `uni.showModal`，确认跳 `/pkg-card/verify/index`，取消停留
- [x] 已实名流程不变
- [x] 额外（超出设计）：顶部 `verify-gate` 提示条常驻 + 底部主按钮灰态「实名后可生成」
- [x] `kaipai-frontend` `type-check`（后台任务 `bmnld57s6` 等，exit 0）与 `build:mp-weixin`（`b48gvi3od`，Build complete）通过

### T3 双层门禁联调验证 ✅
**Validates: Requirements 3.1, 3.2**

- [x] 实名通过用户：前端按钮可用、后端 `isCertified` 放行，正常创建 task 返回 taskId（代码路径已确认）
- [x] 未提交 / 审核中 / 拒绝用户：前端提示条 + 灰态按钮 + 弹窗引导，后端统一 `NOT_CERTIFIED` 拦截
- [x] 绕过前端直调 generate：后端在 `save(task)` 前抛出，未实名不落表、不触发异步
- [x] 真实验证：后端编译 / 单测（`bzsu0c4ba` / `bcpouph90` / `blir43oka` 均 exit 0）、前端 type-check / 小程序打包（`b48gvi3od` Build complete）通过；最新产物已用微信开发者工具 CLI 打开供人工两态点击复核
- [x] 回填 `execution.md`（已新建，含 design 差异说明）；`CURRENT_CONTEXT.md` 主线未变，本阶段为独立 00-182 切片，按现有约定不强制改写主线场景

## 追溯

- T1 → Requirements 3.1, 3.3 / design.md §3
- T2 → Requirements 3.2, 3.3 / design.md §4
- T3 → Requirements 3.1, 3.2 / design.md §6
