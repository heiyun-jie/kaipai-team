# 当前阶段小程序单一测试运行入口 - 执行记录

## 2026-09-02

- 用户裁决：测试只保留一个入口，固定为 `kaipai-frontend/dist/dev/mp-weixin`；不得在 `dist/build` 与 `dist/dev` 之间切换。
- 已实现 `build-mp-weixin-runtime.ps1`：测试构建通过 `UNI_OUTPUT_DIR` 直接输出到固定 `dist/dev`，构建前只读检查微信开发者工具进程；工具运行时在任何输出写入前失败。
- 已实现 `sync-mp-weixin.ps1 -RuntimeOnly`：只归一化、清理和校验 `dist/dev`，不读取、不复制、不镜像 `dist/build`；无参数调用默认进入同一 `RuntimeOnly` 分支，隔离产物必须显式指定模式。
- `package.json` 的 `build:mp-weixin` 和 `build:mp-weixin:local` 均使用同一 Runtime builder；测试用 `postbuild:mp-weixin` 已移除。隔离 Candidate/正式发布脚本仍使用调用方提供的隔离输出目录。
- MCP 的构建、开页、刷新、截图、运行时、元素、页面和控制台工具 schema 只保留 `target=dev`，内部项目固定为 `dist/dev/mp-weixin`；不存在 build 运行项目。
- 包体审计与 AI 产物审计默认读取 `dist/dev/mp-weixin`；隔离发布审计必须显式传入 `-BuildDir`。
- `verify-test-miniapp-acceptance.py` 默认只比较冻结 `mini-program-test` 与固定 `dist/dev`；`--build-dir` 仅用于显式隔离 build 诊断，`--runtime-dir` 只能是固定 `dist/dev`。

## 验证结果

- `npm run verify:single-runtime-entry`：`PASS / exit 0`。
- `test_verify_test_miniapp_acceptance.py`：`12/12` 通过，含第二入口参数拒绝测试。
- `test_build_release_candidate_artifacts.py`：`8/8` 通过。
- `npm run type-check`：通过，exit `0`。
- `node --check tools/wechat-devtools-mcp/server.mjs`：通过，exit `0`。
- `verify:actor-card-renderer` 与 `verify:actor-card-share-detail` 默认 `dist/dev` 均通过；`verify:actor-card-skill-semantics` 当前返回 `FAIL (3)`，因为固定 dev 仍是旧 Candidate，尚未在 DevTools 退出后从最新源码重建。该失败正是单入口门禁应保留的阻断，不通过修改门禁隐藏。
- 运行时构建保护实测：微信开发者工具检测到 `12` 个进程，`npm run build:mp-weixin` 返回 exit `1`，输出“测试构建已阻断，固定运行入口保持不变”，未进入构建、同步或缓存处理。
- 当前固定 `dist/dev/mp-weixin`：`329` 文件、`2,036,714` 字节；本轮失败构建前后未写入该目录。MCP tools/list 验证所有运行 target 均为 `dev`。
- 当前 Candidate `20260901-221652-v3-draft` 的冻结产物与固定 dev 仍等价，但本轮入口治理改变了 frontend/backend 输入，准入返回 `CANDIDATE_REFREEZE_REQUIRED / exit 3`；旧 Candidate 不再作为本轮人工验收凭据。
- 正式容器、生产数据库、正式 Nginx 和正式小程序未操作；正式发布状态仍为 `NOT_AUTHORIZED`。

## MCP 最新性复核（2026-09-02）

- `wechat_devtools_status` 返回的唯一运行项目为 `D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin`；MCP 未提供 build 运行项目。
- `wechat_devtools_artifact_check(route=pkg-actor-card/generate/index)`：JS/WXML/WXSS 均存在，`complete=true`，`scopedHashConsistent=true`。MCP 返回当前固定 dev 路由哈希：JS `E4621D85D4993C0697897680D86A8231AFCBE3B12F24BF2118D62D39748FBE95`、WXML `47D40D5E0DAE46806C312C748357387E5C25DFB49CEAD2962687CABDE727BEBF`、WXSS `C22ED0465AE85EE562B674ABC707FB8756547121A17D430303E459F14624F044`。
- `wechat_devtools_runtime_info(action=currentPage)`：当前页 `pkg-actor-card/generate/index`，查询 `cardId=1&preview=1`。
- `wechat_devtools_build(timeoutMs=300000)`：MCP 返回 `code=1`，stderr 为“微信开发者工具正在运行（15 个进程）；测试构建已阻断，固定运行入口保持不变: ...\\dist\\dev\\mp-weixin”；没有进入构建或同步。
- 当前 generate 路由三件套与 `dist/build` 相同；共享 `ActorCardRenderer` 的 dev/build 三件套不同，且默认技能门禁失败 3 项。因此当前页面是旧 Candidate 的可运行入口，不是最新源码构建；必须在工具退出后通过同一 `npm run build:mp-weixin`/MCP build 重新生成 `dist/dev`，再冻结新 Candidate。

## 2026-09-02 直接执行结果

- MCP `wechat_devtools_status` 首次确认无运行进程后，调用 `wechat_devtools_build(timeoutMs=300000)`，唯一输出为 `D:\\XM\\kaipai-team\\kaipai-frontend\\dist\\dev\\mp-weixin`，嵌套命令 `code=0`，`RUNTIME_BUILD=PASS`；未切换或镜像 `dist/build`。
- `npm run verify:actor-card-skill-semantics`：`00-251 actor-card skill semantics: PASS (source+generated)`，exit `0`。
- `npm run verify:single-runtime-entry`：`00-252 single runtime entry: PASS`，`RUNTIME_PROJECT=dist/dev/mp-weixin`、`BUILD_RUNTIME_MIRROR=REMOVED`、`MCP_BUILD_TARGET=REMOVED`，exit `0`。
- MCP `wechat_devtools_artifact_check(route=pkg-actor-card/generate/index)`：build/dev JS、WXML、WXSS 均存在，`complete.build=true`、`complete.dev=true`、`buildDevEquivalent=true`；三件套 SHA256 均一致：JS `E4621D85D4993C0697897680D86A8231AFCBE3B12F24BF2118D62D39748FBE95`，WXML `47D40D5E0DAE46806C312C748357387E5C25DFB49CEAD2962687CABDE727BEBF`，WXSS `C22ED0465AE85EE562B674ABC707FB8756547121A17D430303E459F14624F044`。
- MCP `wechat_devtools_open_page(target=dev, route=pkg-actor-card/generate/index, query=cardId=1&preview=1)` 后，`runtime_info(currentPage)` 返回 `pkg-actor-card/generate/index?cardId=1&preview=1`；`page_action(getData)` 返回技能数组 12 项，未写入 AI 扩图输入或虚构说明。
- MCP `wechat_devtools_screenshot(target=dev, path=.sce/evidence/wechat-devtools/20260902-generate-skill-latest.png, wait=3)`：返回 `success=true`，截图已保存；画面首屏技能标签为 `影视表演`、`短剧`、`情绪戏`、`+9`。
- 新建并构建 Candidate `20260902-113826-v3-draft`：`build-release-candidate-artifacts.py` 返回 `status=PASSED`、`artifactCount=4`，产物目录 329/328 文件已捕获；刷新 manifest 后准入返回 `INVALID_CANDIDATE`，原因为 `DEPENDENCY_AUDIT_REVIEW_PENDING`（未复核 `browserslist`、`postcss-selector-parser`）。因此不绕过门禁，不标记 `AWAITING_MANUAL_ACCEPTANCE`；正式发布继续 `NOT_AUTHORIZED`。

## 用户复测（2026-09-02）

- MCP `wechat_devtools_status`、`wechat_devtools_artifact_check` 和 `wechat_devtools_runtime_info` 均使用固定 `dist/dev/mp-weixin`；当前页仍为 `pkg-actor-card/generate/index?cardId=1&preview=1`，路由三件套完整且 scoped hash 一致。
- MCP `wechat_devtools_build(timeoutMs=300000)` 返回 nested `code=1`，检测到微信开发者工具 `15` 个进程，前置保护保持唯一运行目录不变。
- `CHECK_MP_TARGET=build npm run verify:actor-card-skill-semantics`：`PASS (source+generated) / exit 0`；默认 `npm run verify:actor-card-skill-semantics`：`FAIL (3) / exit 1`。
- `ActorCardRenderer` 三件套 dev/build 当前均不等价：JS `c2741376...` vs `9b16c50c...`，WXML `24058de4...` vs `2ec2bf39...`，WXSS `815361bf...` vs `eaac9398...`。结论仍为打包产物未进入唯一运行目录，非技能数据再次混入。

完整命令、输入、字面输出、退出码、哈希和副本回滚记录见本目录 `evidence/VERIFICATION.txt`。
