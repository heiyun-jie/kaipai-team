# 00-236 测试环境人工验收与 GO/NO-GO - 执行记录

## 当前状态

- Candidate: `20260902-145540-v3-draft`
- Manifest SHA256: `8a1d6807ff985d33a140a887c5239c3829ab4b9527359e22a6a0c91c3f6ff8a1`
- Status: `READY_FOR_MANUAL_ACCEPTANCE`
- Production decision: `NOT_AUTHORIZED`
- Evidence: `.sce/runbooks/backend-admin-release/records/20260902-145540-v3-draft/00-243/acceptance-gate.json`
- Evidence SHA256: `d8053e9f5dead068ae26e4ea0400392a3f398026a4f20144bff8568c9096aac5`
- Latest mini-program readiness evidence: `.sce/runbooks/backend-admin-release/records/20260902-145540-v3-draft/00-243/acceptance-gate.json`

## 2026-08-28 最新候选测试发布

- `00-242` 单一首图前后端改动已进入 `20260828-190255-v3-draft`，四类候选产物构建和 API 目标证明通过。
- `kaipai-backend-test` 已更新为候选 JAR；测试 API、测试后台、正式 API 均为 HTTP 200。
- 固定微信工程已更新为 `mini-program-test`：328 文件、2,042,821 字节、manifest mismatch=0，测试 API 命中 4、正式/本地 API 命中 0。
- 微信内部刷新成功，当前页为首页；`step-visual` build/dev 三件套一致，刷新后无旧缓存回写。
- 双环境预检 `passed=true`；正式容器 ID、startedAt、restartCount 完全未变。
- 当前可开始人工验收；正式发布、生产迁移和切流继续保持未授权。

## 验收入口

- 小程序固定工程：`D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin`
- API：`https://test-api.kplyyk.com`
- 测试后台：`https://test.kplyyk.com`
- 后台测试账号 alias：`test_admin_full`（密码只在当前任务中交付，不写入 Spec）
- 测试短信：开发态固定验证码流程，页面/接口会直接给出测试验证码。

## 自动前置结果

- 冻结测试产物与 `mini-program-test.json`：`328/328`，mismatch=`0`。
- 测试 API 命中 `4`；正式/本地 API 命中 `0`。
- type-check、导航、附件、TDesign、三列素材、结构化演员卡、分享详情和 steering 门禁全部通过。
- test API、test admin、prod API 公网 smoke 均为 `HTTP 200`。
- 测试后台账号登录为 `HTTP 200 / business 200`。
- 微信开发者工具进程保持运行，未退出、未置顶、未抢焦点；MCP 内部刷新成功，当前页为 `pages/home/index`。

## 2026-08-27 登录页缺陷修复增量

- 人工测试发现 `pages/login/index` 协议勾选框出现偏心双圆，已由 `00-239` 修复并完成未选/选中运行态截图。
- `dist/dev/mp-weixin` 仍只访问 `https://test-api.kplyyk.com`，可继续做缺陷确认和探索性测试。
- 本次前端字节变化使 `20260826-1625-v3-draft` manifest 对应的小程序产物失效；修复后的正式验收计数必须从下一版冻结候选重新开始。
- 数据库迁移、后端合同和测试数据均未变化，`00-235 TEST_DATA_READY` 无需重跑；重新冻结后重跑小程序自动门禁与人工核心矩阵。

## 2026-08-28 测试微信登录配置解阻

- `00-240` 已完成测试 Nacos 与 `test-secrets.env` 的微信配置，并只重建 `kaipai-backend-test`。
- 无效微信 code 已进入微信上游校验并返回 `invalid code`，不再返回“微信登录未配置小程序 appId/appSecret”。
- 测试 API docs、正式 API docs、测试后台均为 HTTP 200；双环境预检 `passed=true`。
- 测试数据库仍为 `kaipai_test`、Redis DB 仍为 `1`；正式容器 ID、startedAt、restartCount 未变化。
- 登录运行配置阻断已解除，候选重新冻结已完成，可以继续人工历史账号/新账号矩阵；用户 GO 仍未完成，正式发布继续保持未授权。

## 人工验收清单

1. 登录微信开发者工具并确认工程路径是固定 `dist/dev/mp-weixin`。
2. 历史账号：资料、头像、演艺经历、自我介绍、旧素材、实名状态与旧分享页。
3. 新账号：注册、资料、素材上传、取消/返回/重试。
4. 演员卡：7 步创建、生成、预览、发布、分享、复制创建。
5. 后台：7 页正式导航、用户、分享内容、风格模板、运营动作和系统设置。
6. 记录 P0/P1/P2；任何候选代码、迁移或配置变化都会使本次验收失效。

## 裁决边界

当前只解锁人工测试，不解锁正式迁移、Nginx 切流或正式小程序发布。用户明确签署 `GO` 后才可进入 `00-237`。

## 2026-08-31 人工验收增量

- 脱敏记录：`.sce/evidence/20260828-test-full-access/MANUAL_ACCEPTANCE_20260831.md`
- 记录 SHA256：`278596807F888B58672BD6E4D135A82FF64B526C702D66F68CADA158D4D542F8`
- 演员卡步骤 1、2、3、4、5、6、7 的页面结构、空态/守卫态和步骤推进按当前候选运行态核验通过；步骤 4 素材库选择入口打开后暴露 9 个照片 tile，确认选择栏正确显示 `1 / 12`。
- 生成页对未完成步骤 3 返回明确业务守卫；未发布演员卡详情页返回明确公开守卫；控制台 `grep -i error` 为空，仅保留系统弃用警告。
- 测试后台公开登录页返回 HTTP 200；未登录直达 `/users/index` 重定向到 `/login?redirect=/users/index`。本轮无已登录后台会话，7 页登录后矩阵仍待业务负责人登录后人工执行。
- 路由核验期间 DevTools 临时生成的 `project.private.config.json` 已移除；`dist/build` 与 `dist/dev` 均恢复 `328` 文件，`dist/dev` `2,042,821` 字节，测试 API 命中 `4`，禁用 API 命中 `0`，manifest mismatch=`0`。
- 状态保持 `READY / AWAITING_MANUAL_ACCEPTANCE`，Production decision 保持 `NOT_AUTHORIZED`；未执行 `00-237`、生产迁移、Nginx 切流或正式小程序上传。

## 2026-08-31 运行态域名校验恢复

- 用户提供的运行态截图复现 `request:fail url not in domain list`；固定 `dist/dev/mp-weixin` 的 `project.private.config.json` 缺失，导致 DevTools 默认启用 `urlCheck`。
- 仅恢复本地 `project.private.config.json`（`setting.urlCheck=false`），没有重启或切换微信开发者工具，也没有修改候选业务产物、后端、数据库或生产环境。
- 内部刷新并回到 `pages/card-list/index` 后，错误字段为空，页面显示“还没有已发布的演员卡 / 开始创建演员卡”；控制台 `grep -i error` 为空。
- `WeappCompileCache` 复核：测试 API 命中 `8`，本地/正式 API 命中均为 `0`；排除本地私有配置后候选仍为 `328` 文件、manifest mismatch=`0`。
- 证据：`.sce/evidence/20260828-test-full-access/runtime-domain-check-20260831/VERIFICATION.txt`；状态继续 `READY / AWAITING_MANUAL_ACCEPTANCE`，正式发布继续 `NOT_AUTHORIZED`。

## 2026-09-01 测试 AI 主密钥隔离同步

- 测试容器缺少 `AI_PROVIDER_CONFIG_MASTER_KEY`，导致 AI 扩图请求返回主密钥未配置。已从生产 compose 只读提取并写入本地 gitignored 密钥文件，再通过测试专用 TAT 脚本同步到 `kaipai-backend-test`。
- 测试 API / 后台公网 smoke 均为 `HTTP 200`；测试数据库仍为 `kaipai_test`，Redis DB 仍为 `1`。
- 生产容器 `ID / startedAt / restartCount` 前后完全一致；没有生产配置写入、生产数据库迁移、Nginx 切流或正式小程序上传。
- 由于测试运行时配置变化，AI 扩图人工验收需要在 DevTools 重新登录后重跑；当前自动化会话返回 `APPID_ERROR / 需要重新登录`，未使用桌面自动化恢复。
- 证据：`.sce/evidence/20260901-test-ai-key-isolation/VERIFICATION.txt`。状态保持 `READY / AWAITING_MANUAL_ACCEPTANCE`，正式发布继续 `NOT_AUTHORIZED`。

## 2026-09-01 候选单一事实源准入纠偏

- 新增 `00-246` 只读准入门禁后，对 `20260828-190255-v3-draft` 重新执行真实检查。
- 冻结 `mini-program-test` 本身仍完整：328 文件、2,042,821 字节、tree SHA256 `bf48cd77ebd0f21abc30c11113f8f78dbbcc01b9227f00b2cf84e1aa8449ed7c`。
- backend/admin 输入仍与候选一致；frontend 输入已从 82 个 overlay 变为 83 个，候选后实现变化未进入旧 Candidate。
- 工作区 build 为 328 文件、2,036,084 字节，12 个文件相对候选变化；固定 dev 的候选应用文件未变化，但 DevTools 增加了 45 字节 `project.private.config.json`。
- 运行目录仍只命中测试 API；旧记录没有 `runtime-readiness.json`，不能满足新的 Candidate/目录树/缓存/实时请求绑定合同。
- 门禁裁决：`CANDIDATE_REFREEZE_REQUIRED / exit 3 / readyForManualAcceptance=false`。
- 本文件顶部状态和所有早期 `AWAITING_MANUAL_ACCEPTANCE` 描述以本节为准。旧人工验收计数停止；生成新 Candidate、部署同一冻结目录并获得准入 exit 0 后重新开始。
- 本次只读检查和文档纠偏未同步 build/dev、未清微信缓存、未重启工具、未改变测试或生产环境。

## 2026-09-01 新候选小程序准入恢复

- `00-245` 修复已进入 Candidate `20260901-150906-v3-draft`；演员步骤 1 仅保留首图选择/上传，演员可见 AI 扩图入口、状态、失败和重试均已退出产物。
- 冻结 `mini-program-test` 已同源物化到 build/dev：`329` 文件、`2,036,252` 字节、tree SHA256 `747df92fc5152a183c2ea37e131f4b44a22fd146b0337e65afb4c715c9e6d6a1`，三侧完全一致。
- compile cache：测试 API `3`，本地/正式 API `0`；内部页面 `pages/home/index` 已读取测试账号、3 个经典模板和测试存储桶资源，控制台错误为空。
- 最终准入：`READY_FOR_MANUAL_ACCEPTANCE / exit 0`。本文件顶部状态与本节覆盖前述 `CANDIDATE_REFREEZE_REQUIRED`。
- 本次恢复只解锁固定小程序工程的人工验收，不构成正式发布授权；`00-237`、生产迁移、Nginx 切流和正式小程序上传均未执行。

## 2026-09-01 全栈候选准入纠偏与恢复

- 在 `pkg-actor-card/generate/index?cardId=1` 复现“生成失败 / 数据约束校验失败”；测试后端精确日志为 `Field 'source_image_url' doesn't have a default value`。
- 根因是新 Candidate 只切换了冻结小程序，Candidate 后端 JAR 和 `V20260901_001` 尚未进入测试运行态；旧测试库仍要求 `source_image_url NOT NULL`。
- `00-247` 将准入扩展到候选/运行 JAR、`kaipai_test` 迁移、DDL、API 和生产未变证明。缺证明时真实门禁返回 `TEST_STACK_NOT_READY / exit 5`，先前仅凭小程序目录得出的 ready 结论失效。
- 完整备份 `kaipai_test` 后，只对测试库应用既有幂等迁移，只重建 `kaipai-backend-test`。运行 JAR SHA256 已与 Candidate 一致：`6e24be2b2b63afa8612c801a985ed7444552dd9252ff69c6febcb53abd001e3d`。
- MCP 在原页面直接重试后，结构化长页和“发布演员卡”按钮出现，失败区消失；最新生成任务为 `success`，私有素材的 `source_image_url` 保持 `NULL` 且无失败原因。
- 最终全栈准入恢复 `READY_FOR_MANUAL_ACCEPTANCE / exit 0`。生产容器指纹前后不变，正式发布仍为 `NOT_AUTHORIZED`。

## 2026-09-01 历史演员卡扩图修复候选恢复

- `00-248` 修复已进入 Candidate `20260901-183000-v3-draft`；旧 Candidate 的人工验收计数不再沿用。
- 冻结候选、workspace build、固定 dev 完全一致：`329 / 2,036,251 / 559379b9ca7f7566e1d8a2f1c99c96f5f17cb96e7f6160b2c40332ff3f41d1bb`。
- 内部 MCP 已在生成页验证历史卡片自动补偿后的真实扩图、私有桶短时签名和 `aspectFill`；只读数据库验证任务为 `success` 且没有失败原因。
- 最终门禁返回 `READY_FOR_MANUAL_ACCEPTANCE / exit 0`。人工验收从本 Candidate 重新执行受影响项：历史演员卡生成页、主视觉比例、长页首屏、发布后公开页和签名 URL 过期后的重新读取。
- 生产容器未变化，`00-237` 未开始；生产数据库迁移、Nginx 切流和正式小程序上传仍未授权。

## 2026-09-01 个人简介摘要修复候选恢复

- 人工验收发现 Hero 固定个人简介卡会把完整长文本从末行中部硬切；`00-249` 已将其收口为三行省略摘要，下方正文继续完整展示。
- 新 Candidate `20260901-200255-v3-draft`、workspace build、固定 dev 统一为 `329 / 2,036,481 / b22b84054bb62e8f8c67d2ccb7794f865947fe765128b64ff438a914ae8a1738`。
- 内部 MCP 已同时验证 Hero 三行摘要和下方完整简介，控制台无 `error/fail`；最终准入为 `READY_FOR_MANUAL_ACCEPTANCE / exit 0`。
- 受影响验收项从本 Candidate 重新开始：生成页 Hero 简介、长页完整简介、发布后公开页共享 Renderer。正式发布继续 `NOT_AUTHORIZED`。

## 2026-09-01 Hero 中性交接修复候选恢复

- 人工验收发现 Hero 最后两张内容卡结束后仍露出约 `98rpx` 的背景图黄色尾带；`00-250` 已用中性浅灰尾部替代该图片区域，并将统计卡上移 `74rpx`，末卡到统计卡保持 `24rpx`。
- 新 Candidate `20260901-221652-v3-draft`、workspace build、固定 dev 统一为 `329 / 2,036,714 / f56091d374def4ceca034f00cee362b72473e897676083618716172ecd1bee83`。
- 内部 MCP 已验证黄色尾带消失、统计卡两侧为中性背景、长页可滚动到 `2822px`、完整个人简介及底部 spacer 正常，控制台无 `error/fail`。
- compile cache 中测试 API 命中 `3`，本地业务 API `127.0.0.1:8010` 与正式 API均为 `0`；最终准入为 `READY_FOR_MANUAL_ACCEPTANCE / exit 0`。
- 受影响验收项从本 Candidate 重新开始：生成页 Hero/统计卡交接、长页滚动和公开页共享 Renderer。正式发布继续 `NOT_AUTHORIZED`。

## 2026-09-02 00-254 候选恢复

- 当前人工验收 Candidate 更新为 `20260902-145540-v3-draft`，全栈准入为 `READY_FOR_MANUAL_ACCEPTANCE / exit 0`。
- 名片夹草稿列表真实测试数据已验证两种新入口：“预览并发布”和“生成预览”；旧的两列回退兼容测试也已保留。
- 人工验收从本 Candidate 继续执行 `00-236` 清单，名片夹草稿下一步分流加入受影响回归项。
- P0/P1/P2/P3 裁决规则不变；正式发布仍需用户另行明确 `GO`，当前为 `NOT_AUTHORIZED`。

## 2026-09-02 体验版素材库游客态缺陷

- 手机体验版未登录进入 `pages/assets/index` 时显示微信底层 `request:fail url not in domain list`；页面无条件请求素材 API 且直出捕获异常原文。
- `00-258` 已完成游客零请求、未登录登录引导、上传门禁和素材加载错误文案收口；隔离测试 API 构建及源码/产物门禁通过。
- 本次前端字节变化使 `20260902-145540-v3-draft` 的受影响人工验收失效；状态转为 `CANDIDATE_REFREEZE_REQUIRED`，新 Candidate 分配为 `20260902-174419-v3-draft`。
- `00-257` 合法域名准入仍独立存在：游客态修复不能替代已登录体验版的微信网络准入。
- 正式发布继续 `NOT_AUTHORIZED`；未执行生产数据库迁移、生产容器重建、Nginx 切流或正式小程序发布。
