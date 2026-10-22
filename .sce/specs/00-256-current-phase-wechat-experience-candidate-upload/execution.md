# 微信体验版测试 Candidate 上传 - 执行记录

## 2026-09-02

- Candidate：`20260902-145540-v3-draft`。
- 上传版本：`3.0.0.20260902.145540`。
- CLI 登录：`true`。
- AppID：`wx4dcc4e1066fd0fb9`。
- 微信 CLI `upload`：`PASSED / exit 0`，上传总包 `2,815,332` 字节，主包 `1,922,725` 字节。
- 上传回执：`.sce/runbooks/backend-admin-release/records/20260902-145540-v3-draft/00-256/upload-info.json`，SHA256 `3f1bec22662d72ce69b1884a31571a77a18bfb70b0655db41430159130153be3`。
- 上传后 Candidate 准入仍为 `READY_FOR_MANUAL_ACCEPTANCE / exit 0`，`dist/dev` 仍为 `329 / 2,041,422 / d1528b66647a79dacf19eb1ed0d3f6d165249b51a19e978e0a3c1fbdf6316f1e`。
- 当前状态：`DEVTOOLS_EXPERIENCE_CANDIDATE_UPLOADED`。按用户确认，本轮以微信开发者工具 `upload` 成功作为体验测试候选提交完成条件，不进入公众平台页面执行额外操作。
- 全程未调用微信工具可见开窗、置顶、前台激活、桌面截图、坐标或键鼠自动化。
- 正式发布：`NOT_AUTHORIZED`。
