# 素材库游客态与错误边界收口 - 执行记录

## 2026-09-02

- 页面：`pages/assets/index`。
- 复现环境：手机体验版、未登录。
- 根因：`onShow` 无条件 `load(true)`，`load()` 无游客门禁，并把捕获异常的 `message` 原文写入 `loadError`。
- 已实现：游客以 `!userStore.hasStoredSession` 判定；`onShow/load/chooseUpload` 均在业务请求或系统 picker 前执行门禁；游客清理驻留素材状态并显示“未登录 / 去登录”。
- 已实现：素材列表加载失败统一为“素材读取失败，请稍后重试”，不再把捕获异常原文写入页面。
- `verify:asset-guest-state -- --source-only`：`10/10 / exit 0`。
- 隔离测试 API 构建：`DONE / exit 0`；专项源码+产物：`13/13 / exit 0`。
- `type-check`：`exit 0`；`verify:asset-photo-grid`：`34/34 / exit 0`；`verify:tdesign-migration`：`865/865 / exit 0`；`verify:single-runtime-entry`：`exit 0`。
- 原始 SHA256：`2947decc2a51779d75ac02400ca58aa2d806a8565c6ecca9003d531e3aa37f90`；修改 SHA256：`4b5319e5fd1a1cf602fa8c6efe9c75979a8ecf4dfa7a8b2329aff1038484f3ca`。
- 独立副本回滚：`RESTORED / exit 0`，恢复 SHA256 等于原始；工作区保持修改态。
- 新 Candidate：`20260902-174419-v3-draft`；冻结、唯一运行入口、MCP 游客态和体验版上传结果写入同 Candidate 的 ignored release record，避免执行记录回填反向改变 Candidate 输入。
- 当前状态：`IMPLEMENTED / CANDIDATE_REFREEZE_IN_PROGRESS`。
- 当前 Candidate `20260902-145540-v3-draft` 的相关人工验收被本次缺陷打断；正式发布仍为 `NOT_AUTHORIZED`。
