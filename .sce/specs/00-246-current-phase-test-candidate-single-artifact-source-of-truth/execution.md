# 测试小程序候选单一事实源与人工验收准入 - 执行记录

## 2026-09-01

- 用户裁决：`dist/build` 只用于生成候选；测试只认带 Candidate ID 的冻结 `mini-program-test`；`dist/dev` 必须是该候选的运行镜像；只有候选、镜像和项目级编译缓存全部一致才能进入人工验收。
- 基线测试：现有 release candidate 生成/构建测试 `13/13` 通过。
- 当前实现中候选构建器已经从隔离快照 `dist/build/mp-weixin` 复制冻结 `mini-program-test`，但缺少统一人工验收准入命令。
- 当前 Candidate `20260828-190255-v3-draft` 与工作区最新 build 已出现分叉，因此完成新门禁后预期裁决为 `CANDIDATE_REFREEZE_REQUIRED`，不能继续沿用旧候选验收计数。
- 本 Spec 不同步 `dist/dev`、不清微信缓存、不改变测试或生产运行环境。

## 实现与真实门禁结果

- 新增 `verify-test-miniapp-acceptance.py`，状态/退出码为 ready=0、invalid=2、refreeze=3、runtime-not-switched=4。
- 新增 7 项准入单测；现有候选构建/manifest 测试扩展为 14 项，合计 `21/21` 通过。
- 候选构建器只为 `mini-program-test` 冻结确定性 `project.private.config.json`，其字节 SHA256 为 `88b903ddaaebfd05316394e807c589b217c877a8192ead6a9e6970a8a037d898`；正式小程序产物不新增该文件。
- 当前真实门禁：候选完整，backend/admin 输入 current，frontend 输入 invalidated，workspace build mismatch，最终 `CANDIDATE_REFREEZE_REQUIRED / exit 3`。
- 当前固定 dev 仍只命中测试 API；没有执行目录替换或运行态操作。

## 新 Candidate 实际准入结果

- 新 Candidate：`20260901-150906-v3-draft`；manifest SHA256 `38398cb1f57031fd25eb84df1b5f47ac2fc828a078cf65b73a56d0e23a3205e6`。
- 冻结、build、dev 三侧统一为 `329` 文件、`2,036,252` 字节、tree SHA256 `747df92fc5152a183c2ea37e131f4b44a22fd146b0337e65afb4c715c9e6d6a1`。
- compile cache 与内部实时页面证明均绑定同一固定 dev：测试 API `3`，本地/正式 API `0`，当前页 `pages/home/index`。
- 最终门禁：`READY_FOR_MANUAL_ACCEPTANCE / exit 0 / readyForManualAcceptance=true`。
- 回滚脚本仅在独立副本恢复旧运行树；实际 build/dev 保持新候选。正式发布仍为 `NOT_AUTHORIZED`。

## 2026-09-02 - 00-252 单入口收口

- 测试运行入口固定为 `kaipai-frontend/dist/dev/mp-weixin`。`npm run build:mp-weixin` 直接写入该目录，删除测试用 `postbuild:mp-weixin` build→dev 镜像；`dist/build/mp-weixin` 仅由隔离 Candidate/正式发布构建使用。
- `verify-test-miniapp-acceptance.py` 默认不读取工作区 `dist/build`；只有显式传入 `--build-dir` 才执行隔离 build 诊断。默认准入只比较冻结 `mini-program-test` 与固定 `dist/dev`，并校验测试 API、运行证明和全栈证明。
- MCP 的构建、开页、刷新、截图、运行时、元素、页面及控制台工具均只注册 `target=dev`，内部项目路径固定为 `dist/dev/mp-weixin`；不存在 build 运行项目。
- 包体和 AI 产物审计默认读取固定 `dist/dev/mp-weixin`，隔离发布审计必须显式传入 `-BuildDir`。
- 静态门禁 `npm run verify:single-runtime-entry` 与准入门禁单测均通过；当前微信开发者工具运行中，Runtime builder 在任何输出写入前返回进程占用并保持当前运行态不变。正式发布仍为 `NOT_AUTHORIZED`。
