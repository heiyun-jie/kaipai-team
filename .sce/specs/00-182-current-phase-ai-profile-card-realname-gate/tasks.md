# 00-182 当前阶段 AI 分享图生成实名门禁 - 任务拆解

> 执行原则：一次一个任务，执行后更新状态并等待审核。

## 任务列表

### T1 后端 generate 接口补实名门禁
**Validates: Requirements 3.1, 3.3**

- [ ] `AiProfileCardServiceImpl` 注入 `IdentityVerificationService`
- [ ] 新增私有方法 `requireCertified(Long userId)`，按 `currentStatus(userId).getStatus()` 分支：`2` 放行，`1/3/其它` 抛 `BizException(NOT_CERTIFIED, ...)`，沿用 `AiController` 对 `NOT_CERTIFIED` 的既有抛出模式
- [ ] 在 `generate()` 中把 `requireCertified` 置于 `templateSceneCode` / 档案 / 源图校验之前
- [ ] 确认未实名时不落 `actor_ai_profile_card_task`、不触发异步执行
- [ ] `kaipaile-server` 编译通过

### T2 前端 handleGenerate 补实名前置判断
**Validates: Requirements 3.2, 3.3**

- [ ] `handleGenerate()` 在分析图校验之后、调用 `generateAiProfileCard` 之前插入实名判断
- [ ] 调用前 `await userStore.syncVerificationStatus()` 再读 `userStore.isCertified`；同步失败按未实名保守处理
- [ ] 未实名弹 `uni.showModal`，确认跳 `/pkg-card/verify/index`，取消停留
- [ ] 已实名流程不变
- [ ] `kaipai-frontend` `type-check` 与 `build:mp-weixin` 通过

### T3 双层门禁联调验证
**Validates: Requirements 3.1, 3.2**

- [ ] 实名通过用户：前后端均放行，正常返回 taskId
- [ ] 未提交 / 审核中 / 拒绝用户：前端弹窗引导，后端强制拦截
- [ ] 绕过前端直调 generate：后端仍拦截未实名请求
- [ ] 真实接口 / 真实小程序复核，不凭静态推断
- [ ] 回填 `execution.md` 与 `CURRENT_CONTEXT.md`

## 追溯

- T1 → Requirements 3.1, 3.3 / design.md §3
- T2 → Requirements 3.2, 3.3 / design.md §4
- T3 → Requirements 3.1, 3.2 / design.md §6
