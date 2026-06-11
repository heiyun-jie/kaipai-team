# 00-182 当前阶段 AI 分享图生成实名门禁 - 技术设计

## 1. 改动范围

| 层 | 文件 | 改动 |
|----|------|------|
| 后端 Service | `kaipaile-server/.../service/ai/impl/AiProfileCardServiceImpl.java` | `generate()` 内新增实名门禁校验 |
| 后端依赖 | `kaipaile-server/.../service/verify/IdentityVerificationService.java`（已有 `currentStatus`） | 注入并复用，不改其逻辑 |
| 后端错误码 | `kaipaile-server/.../model/ai/dto/AiResumeErrorCode.java`（已有 `NOT_CERTIFIED=403`） | 复用，不新增 |
| 前端页面 | `kaipai-frontend/src/pkg-card/ai-profile-card/index.vue` | `handleGenerate()` 内新增实名前置判断 |
| 前端 store | `kaipai-frontend/src/stores/user.ts`（已有 `isCertified` / `syncVerificationStatus`） | 复用，不改其逻辑 |

不新增接口、不新增 DTO、不新增数据库字段、不新增 migration。

_Requirements: 3.1, 3.2, 3.3_

## 2. 实名状态事实源

- 后端实体：`User.realAuthStatus`（Integer）、`IdentityVerification.status`（Integer）
- 通过值：`2`，常量 `IdentityVerificationServiceImpl.STATUS_APPROVED = 2`、`REAL_AUTH_APPROVED = 2`
- 查询入口：`IdentityVerificationService.currentStatus(Long userId)` → `IdentityVerificationStatusRespDTO`（含 `status`）
- 前端：`userStore.realAuthStatus`（计算属性）、`userStore.isCertified`（`=== 2`）、`getVerifyStatus()`（`GET /verify/status`）

_Requirements: 3.3_

## 3. 后端门禁设计

### 3.1 校验位置

在 `AiProfileCardServiceImpl.generate(Long currentUserId, dto)` 方法体内，置于参数 / 档案 / 源图校验之前（鉴权已由 Controller `currentUserId()` 完成）。建议顺序：

```
generate():
  1. 实名门禁校验（新增）   ← 未通过即抛 BizException，不再往下
  2. templateSceneCode 校验（现状）
  3. profile / profileEntity / sourceImage 解析（现状）
  4. 创建 task + 异步执行（现状）
```

把实名校验提到档案 / 源图加载之前，可避免对未实名用户做无意义的 DB 读取。

### 3.2 校验实现

- 注入 `IdentityVerificationService`（已是 `@Service`，构造 / `@Resource` 注入）。
- 取 `currentStatus(currentUserId).getStatus()`，按值分支：
  - `2` → 放行。
  - `1` → 抛 `BizException(NOT_CERTIFIED, "实名认证审核中，请通过后再生成 AI 分享图")`。
  - `3` → 抛 `BizException(NOT_CERTIFIED, "实名认证未通过，请重新完成认证后再生成 AI 分享图")`。
  - 其它（含 `0` / null）→ 抛 `BizException(NOT_CERTIFIED, "请先完成实名认证后再生成 AI 分享图")`。
- 抽成私有方法 `requireCertified(Long userId)`，与现有 `requireProfileEntity` / `resolveSourceImage` 风格一致。

> 说明：`BizException` 是否携带 code 入参取决于现有构造签名。若现有 `BizException` 仅支持 message，则按现状抛 message 并由全局异常处理映射；保持与 `AiController` 简历润色对 `NOT_CERTIFIED` 的既有用法一致（实现前对照 `AiController` / `AiResumeService` 中 `NOT_CERTIFIED` 的实际抛出方式，沿用同一模式）。

_Requirements: 3.1_

### 3.3 副作用约束

- 校验失败时方法在创建 `ActorAiProfileCardTask` 之前返回，保证不落表、不触发 `aiProfileCardTaskExecutor.execute(...)`。

_Requirements: 3.1_

## 4. 前端门禁设计

### 4.1 校验位置

`handleGenerate()` 现有校验顺序：选择风格 → 风格解锁 → 分析图上传中 → 分析图存在 → `generateAiProfileCard(...)`。

实名判断插入在「分析图存在校验之后、调用 `generateAiProfileCard` 之前」：

```
handleGenerate():
  ...现有前置校验...
  await ensureCertified()        // 新增：未实名则拦截+引导，return false
  if (未通过) return
  generateAiProfileCard(...)     // 现状
```

### 4.2 实名状态新鲜度

- 调用前先 `await userStore.syncVerificationStatus()`，再读 `userStore.isCertified`，避免本地过期态误拦截刚实名完成的用户。
- 同步失败（网络异常）时按未实名保守处理：提示并引导，不强行放行。

### 4.3 拦截与引导

未实名（`isCertified === false`）时：

```js
uni.showModal({
  title: '需要实名认证',
  content: '生成 AI 分享图需先完成实名认证',
  confirmText: '去认证',
  cancelText: '暂不',
  success: (res) => {
    if (res.confirm) {
      uni.navigateTo({ url: '/pkg-card/verify/index' })
    }
  }
})
```

确认跳实名页，取消停留当前页。两种情况都不调用生成接口。

_Requirements: 3.2_

## 5. 交互流程

```
用户点击「一键生成」
  → 现有前置校验（风格/分析图）通过
  → 同步实名状态
    → 已实名(2)：调用 generate
        → 后端再次强制校验(2) → 创建任务 → 返回 taskId → 弹窗提示10分钟后查看
    → 未实名(0/1/3)：弹窗提示 → 确认跳 /pkg-card/verify/index / 取消停留
  （即使前端被绕过直接调 generate，后端门禁仍拦截未实名请求）
```

_Requirements: 3.1, 3.2_

## 6. 验证方案

- 后端：`kaipaile-server` 编译通过；针对 generate 接口分别用实名通过 / 未提交 / 审核中 / 拒绝四种用户态验证返回（可借助登录态接口 + 改库状态或现有测试数据）。确认未实名时 `actor_ai_profile_card_task` 无新增行。
- 前端：`kaipai-frontend` `type-check` 与 `build:mp-weixin` 通过；真实小程序 / 浏览器复核未实名用户点击生成时弹窗 + 跳转，已实名用户流程无变化。
- 真实接口复核优先于静态推断（沿用本项目后台验证口径）。

_Requirements: 3.1, 3.2, 3.3_

## 7. 不做什么

- 不改 `/verify/submit` 与腾讯云二要素核验。
- 不改 AI provider / 质量门禁 / 异步执行。
- 不给简历润色等其它 AI 入口加本轮门禁。
- 不新增实名校验专用接口或并行实名字段。
