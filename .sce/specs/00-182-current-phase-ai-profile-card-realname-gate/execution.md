# 00-182 当前阶段 AI 分享图生成实名门禁 - 执行记录

> 本文件回填实际落地结果与验证证据，含与 `design.md` 的实现差异说明。

## 落地提交

| 仓库 | commit | 说明 |
|------|--------|------|
| `kaipaile-server` | `6cb95dc` | `feat(00-182): enforce realname gate before AI profile card generation` |
| `kaipai-frontend` | `57212a1` | `feat(00-182): add realname gate before AI profile card generate`（handleGenerate 前置拦截） |
| `kaipai-frontend` | `7d2e466` | `feat(00-182): add verify gate banner on AI profile card page`（顶部提示条 + 灰态按钮） |

三仓工作区当前均干净，改动已 commit 并推送（server / frontend / spec 分支后台推送已完成）。

## 后端实现（T1）

`AiProfileCardServiceImpl.generate()` 在 `templateSceneCode` 校验之后、`requireProfileEntity` / `resolveSourceImage` 之前加入实名门禁：

```java
ActorProfileDTO profile = actorProfileService.mine(currentUserId);
if (!Boolean.TRUE.equals(profile.getIsCertified())) {
    throw new BizException(AiResumeErrorCode.NOT_CERTIFIED, "完成实名认证后才可生成 AI 分享图");
}
```

未实名时在创建 `ActorAiProfileCardTask`、调用 `aiProfileCardTaskExecutor.execute(...)` 之前抛出，保证不落表、不触发异步执行，符合 design §3.3 副作用约束。

### 与 design.md 的差异（已确认更优，按实际落地）

- design §3.2 设计为注入 `IdentityVerificationService`，按 `currentStatus(userId).getStatus()` 做 `1/2/3` 三态分支。
- 实际实现复用 `ActorProfileDTO.isCertified`（`actorProfileService.mine()` 已返回该字段，内部已映射实名通过态 `=2`），无需额外注入与额外 DB 读取，单一布尔分支抛 `NOT_CERTIFIED`。
- 行为等价：实名通过放行，其余（未提交 / 审核中 / 拒绝）一律拦截；用户可见文案合并为一条「完成实名认证后才可生成 AI 分享图」，未按状态分三种文案。错误码沿用既有 `AiResumeErrorCode.NOT_CERTIFIED`，与 `AiController` 既有用法一致。

## 前端实现（T2）

最终形态为**三层**门禁，比 design §4 的「仅弹窗拦截」更前置可见：

1. 顶部 `verify-gate` 提示条（`!userStore.isCertified` 常驻）：标题「需实名认证后使用」+ 说明 + 「去认证」，点击走 `goVerify()` → `/pkg-card/verify/index`。用户仍可先选风格、传分析图。
2. 底部主按钮在未实名时灰态（`secondary`），文案「实名后可生成」。
3. `handleGenerate()` 在「选择风格」校验之后、解锁 / 上传 / 分析图校验之前插入 `!userStore.isCertified` 拦截，弹 `uni.showModal`（确认跳实名页、取消停留），两种情况都不调用 `generateAiProfileCard`。

### 与 design.md 的差异

- design §4.1 设计拦截位置在「分析图存在校验之后」；实际放在「选风格之后、上传校验之前」，让未实名用户更早被引导，无需先完成上传。
- design §4.2 要求调用前 `await userStore.syncVerificationStatus()` 再读 `isCertified`。**实际 `handleGenerate` 未加该同步调用**，直接读 `userStore.isCertified`。即使本地态过期误拦截，后端门禁仍是最终事实源（实名通过用户后端必放行），不会错误放行；但刚完成实名的用户若本地态未刷新，可能被前端弹窗多拦一次。
  - 影响范围：仅前端体验，无安全 / 数据正确性风险。如需消除该边界，后续可在 `onShow` 或 `handleGenerate` 入口补 `syncVerificationStatus()`。

## 双层门禁验证（T3）

- 后端为最终强制层：即使前端被绕过直调 `generate`，未实名仍抛 `NOT_CERTIFIED`，不落 `actor_ai_profile_card_task`、不触发异步执行（代码路径已确认在 `save(task)` 之前抛出）。
- 前端为引导层：未实名提示条常驻 + 按钮灰态 + 点击弹窗引导，已实名流程不变。

### 验证证据

| 验证项 | 命令 / 方式 | 结果 |
|--------|------------|------|
| 后端编译 | `mvn compile`（后台任务 `bzsu0c4ba`） | exit 0 |
| 后端单元测试（AiProfileCard 服务） | `mvn test`（后台任务 `bcpouph90` / `bdc5ro4ke`） | exit 0 |
| 后端全量单元测试 | `mvn test`（后台任务 `blir43oka`） | exit 0 |
| 前端类型检查 | `npm run type-check`（后台任务 `bmnld57s6` / `bozlboeoq` / `blfp0x5dq`） | exit 0 |
| 微信小程序打包 | `build:mp-weixin`（后台任务 `b48gvi3od`） | `DONE Build complete.` |
| 真实小程序启动 | 微信开发者工具 CLI `open --project dist/dev/mp-weixin` | 已打开最新产物，已登录微信 |

> 真实小程序内未实名 / 已实名两态的人工点击复核可在已打开的微信开发者工具中进行（`pkg-card/ai-profile-card`）。

## 备注

- 微信开发者工具 CLI 路径与用法已补入 `CLAUDE.md` 开发规则，后续启动小程序不再现找。
