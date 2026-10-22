# 00-243 测试候选发布与人工测试就绪 - 执行记录

## 当前状态

- Candidate：`20260902-145540-v3-draft`
- Manifest SHA256：`8a1d6807ff985d33a140a887c5239c3829ab4b9527359e22a6a0c91c3f6ff8a1`
- Status：`READY_FOR_MANUAL_ACCEPTANCE`
- Production decision：`NOT_AUTHORIZED`
- Evidence：`.sce/runbooks/backend-admin-release/records/20260902-145540-v3-draft/00-243/acceptance-gate.json`

## 候选与产物

- 后端 JAR SHA256：`5dd678378ae02c48677f1dc4a73707b03c73b534db749986a63e4b69ce129a98`。
- 测试后台：`90` 文件、`2,168,430` 字节；远端 `index.html` SHA256 与候选一致。
- 测试小程序：`329` 文件、`2,041,422` 字节，目录树 mismatch=`0`。
- 测试小程序只命中 `https://test-api.kplyyk.com` `3` 个文件；正式/本地业务 API 命中 `0`。
- 冻结 `mini-program-test` 与唯一人工运行入口 `dist/dev/mp-weixin` 的目录树 SHA256 均为 `d1528b66647a79dacf19eb1ed0d3f6d165249b51a19e978e0a3c1fbdf6316f1e`。

## 测试环境发布

- TAT invocation：`inv-r85r7f0882`，exit=`0`。
- 测试容器：`kaipai-backend-test`，ID `eeb3ae52cf76fa3969c9de959897d299765597b2cad87a66373b221faac59ad1`。
- 端口 / DB / Redis：`18080` / `kaipai_test` / `1`。
- 公网测试 API、测试后台、正式 API 均为 HTTP `200`。
- 微信无效 code 已进入上游并返回 `invalid code`，不存在“未配置小程序”错误。
- 双环境预检：`passed=true`；test/prod Nacos 分别指向 `kaipai_test` / `kaipai_prod`。

## 生产未受影响证明

发布前后正式容器指纹完全一致：

```text
1195a88da11fc2e4141091ee6494c291c287bb48a61725c469d420f32b82bea1
startedAt=2026-07-21T14:10:50.90030867Z
restartCount=0
status=running
```

正式 actor-card OpenAPI 路径仍为 `0`，测试环境为 `17`，证明新后端能力只进入测试环境。本轮未执行生产数据库迁移、生产 Nginx 切流或正式小程序上传。

## 人工测试入口

- 小程序固定工程：`D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin`
- 测试 API：`https://test-api.kplyyk.com`
- 测试后台：`https://test.kplyyk.com`
- 当前微信内部页面：`pkg-actor-card/generate/index?cardId=1`

人工验收按 `00-236` 历史账号、新账号、7 步演员卡、分享详情和后台 7 页矩阵执行。任何候选源码、迁移或配置变化都会使验收计数失效。

## 运行态缓存纠偏（2026-08-28 20:42 +08:00）

- 用户提供的 Network 证据显示请求仍指向本地 `127.0.0.1:8010`。
- 固定工程与磁盘候选均正确，但 `WeappCompileCache` 仍保留 `17:04` 生成的本地 API App Service：本地地址命中 `3`，测试地址命中 `0`。
- 对固定 `dist/dev/mp-weixin` 工程执行项目级 `cache --clean compile`，命令退出 `0`；未结束微信开发者工具，未置顶、未抢焦点、未操作桌面。
- 内部重新打开并刷新 `pages/home/index` 后，新编译缓存本地地址命中 `0`、测试地址命中 `3`，三个缓存文件更新时间均为 `20:42:06`。
- 同一已登录会话下拉刷新后，首页从“模板加载失败”恢复为 `3` 个经典模板，并读取到测试存储桶资源；控制台无请求错误。
- 结论：运行态已从本地 API 纠偏到测试 API，状态恢复为 `PASSED / AWAITING_MANUAL_ACCEPTANCE`；候选文件、远端测试部署和生产环境均未改变。

## 候选单一事实源准入复核（2026-09-01）

- `00-246` 将冻结 `mini-program-test` 固定为唯一测试事实源，并新增 `verify-test-miniapp-acceptance.py`。
- 对本 Candidate 复核：manifest SHA256 `e073829eda572e27f75629f01478da27e40a9256fb28401d301f272987a01672` 与 artifact evidence SHA256 `1d7a25a9ccd736c2ad29d4cefb476785cfd916942a874aa29aa21bd81993b760` 完整；冻结小程序仍为 `328 / 2,042,821`。
- frontend 候选输入已漂移，workspace build 相对候选有 12 个文件变化；这些修改不能以旧 Candidate 继续验收。
- dev 仅额外出现 DevTools 自动生成的 `project.private.config.json`；候选构建器已改为从下一 Candidate 起把该确定性文件纳入 `mini-program-test`，正式候选不包含。
- 本文件顶部状态与本节覆盖前述旧结论：`CANDIDATE_REFREEZE_REQUIRED`，不再是 `PASSED / AWAITING_MANUAL_ACCEPTANCE`。
- 未重新部署测试环境，未执行生产数据库迁移、Nginx 切流或正式小程序上传。

## 新 Candidate 小程序固定完成（2026-09-01）

- Candidate `20260901-150906-v3-draft` 的四类产物隔离构建通过；新后端 JAR SHA256 `6e24be2b2b63afa8612c801a985ed7444552dd9252ff69c6febcb53abd001e3d`，测试后台仍为 `90 / 2,168,430`。
- 冻结 `mini-program-test` 是唯一事实源；冻结、workspace build、固定 dev 均为 `329 / 2,036,252 / 747df92fc5152a183c2ea37e131f4b44a22fd146b0337e65afb4c715c9e6d6a1`。
- 固定 dev 只命中 `https://test-api.kplyyk.com`；本地和正式 API 均为 `0`。演员卡步骤页三件套 build/dev SHA256 完全一致。
- 项目级 compile cache 清理和内部 `pages/home/index` 打开均成功；没有结束、重启、置顶或抢焦点微信开发者工具，也没有使用桌面截图、坐标或键鼠自动化。
- `runtime-readiness.json` 已绑定 Candidate、固定工程路径、运行树、缓存扫描和实时测试页面结果；最终门禁返回 `READY_FOR_MANUAL_ACCEPTANCE / exit 0`。
- 本次只完成新候选小程序本地运行态固定，未声称把新 JAR/迁移部署到测试后端；相关测试环境服务升级必须另按测试部署步骤执行。生产继续 `NOT_AUTHORIZED`。

## 新 Candidate 全栈测试运行态完成（2026-09-01）

- `00-247` 发现并关闭了“小程序 ready 但后端/数据库仍是旧 Candidate”的准入缺口；修复前状态为 `TEST_STACK_NOT_READY / exit 5`。
- 测试库备份完成后应用 Candidate 内嵌的 `V20260901_001__actor_card_internal_auto_expand.sql`，只重建 `kaipai-backend-test`。
- Candidate/运行后端 JAR SHA256 均为 `6e24be2b2b63afa8612c801a985ed7444552dd9252ff69c6febcb53abd001e3d`；`source_image_url` 已可空，稳定来源列、唯一索引及演员卡来源指纹 DDL 读回通过。
- MCP 对 `pkg-actor-card/generate/index?cardId=1` 原地重试成功：失败区不存在，结构化长页和“发布演员卡”按钮存在；最新生成任务为 `success`。
- `test-stack-readiness.json` 已绑定同一 Candidate；最终门禁 `READY_FOR_MANUAL_ACCEPTANCE / exit 0`。
- TAT invocation `inv-h84h8sgdkw`；生产容器 ID、启动时间、重启次数和状态前后完全一致，生产 mutation 为 `NONE`。

## 00-248 修复候选重新准入（2026-09-01）

- `00-248` 的历史卡片懒补偿、私有 COS 响应期读签名、来源图回退和 Hero `aspectFill` 已进入 Candidate `20260901-183000-v3-draft`。
- 冻结 `mini-program-test`、workspace build、固定 dev 均为 `329` 文件、`2,036,251` 字节、tree SHA256 `559379b9ca7f7566e1d8a2f1c99c96f5f17cb96e7f6160b2c40332ff3f41d1bb`；测试 API 命中 `3`，本地/正式 API 命中 `0`。
- Candidate/运行 JAR SHA256 均为 `6694acf32c3d75c30227cc34045fa1b0702e2ae035c6b0d874ed4334733cc9ba`；测试库备份 SHA256 `810c8f415a4181123a1f4c7b5b95a9a944f9308116e5ee27cded4f3ad83300f9`。
- 内部 MCP 在 `pkg-actor-card/generate/index?cardId=1` 读取到签名扩图，Hero 为 `aspectFill` 且无 placeholder；控制台错误为空。
- `kaipai_test` 只读复测确认卡片和任务扩图 URL 均非空、指纹一致，任务为 `success / expand_image / asset_id=1 / failure=NULL`。
- 最终准入 `READY_FOR_MANUAL_ACCEPTANCE / exit 0`；从本 Candidate 重新开始受影响的演员卡人工验收计数。生产容器未变，正式发布继续 `NOT_AUTHORIZED`。

## 00-249 个人简介摘要修复候选重新准入（2026-09-01）

- Candidate `20260901-200255-v3-draft` 已冻结；Manifest SHA256 `5006200d706fc7b075b28bd4cdc20a851d2dc9407a4b57d3e7ba3d177ccd54f9`。
- 冻结测试小程序、workspace build、固定 dev 完全一致：`329` 文件、`2,036,481` 字节、tree SHA256 `b22b84054bb62e8f8c67d2ccb7794f865947fe765128b64ff438a914ae8a1738`。
- 固定工程只命中测试 API `3` 个文件；本地/正式 API 均为 `0`。compile cache 同样为测试 `3`、本地/正式 `0`。
- 内部 MCP 在原页面确认 Hero 简介为三行省略摘要，下方完整简介未截断，控制台错误为空。
- Candidate 后端 JAR 与测试运行 JAR SHA256完全一致，本轮没有重建测试容器或修改测试数据库；测试/正式 API只读健康检查均为 `200`。
- 最终准入 `READY_FOR_MANUAL_ACCEPTANCE / exit 0`；生产决策保持 `NOT_AUTHORIZED`。

## 00-254 名片夹草稿发布入口全栈候选恢复（2026-09-02）

- `00-254` 增加前后端准备度合同后，旧 Candidate 已失效；本轮重新冻结 `20260902-145540-v3-draft`。
- Candidate manifest SHA256：`8a1d6807ff985d33a140a887c5239c3829ab4b9527359e22a6a0c91c3f6ff8a1`；artifact evidence SHA256：`9be2ceec3f922a6c2d3765704770d0957815973c51643b7ca36286fd82244f44`。
- 后端 JAR SHA256：`5dd678378ae02c48677f1dc4a73707b03c73b534db749986a63e4b69ce129a98`；JAR 已确认包含 `ActorCardListItemDTO.generateReady / publishReady`。
- 测试容器 `kaipai-backend-test` 已切换到该 JAR，测试库备份 SHA256：`ffcb9751ea570b0c8195a9682d4642bfa375d02ef07947b5e7382a2ab802af7e`；Schema 合同和测试 API `200`。
- 生产容器的 ID、启动时间、重启次数和 running 状态前后完全一致，`PRODUCTION_MUTATION=NONE`。
- `mini-program-test` 与固定 `dist/dev/mp-weixin` 均为 `329 / 2,041,422 / d1528b66647a79dacf19eb1ed0d3f6d165249b51a19e978e0a3c1fbdf6316f1e`；本地 API 命中 `0`、测试 API 文件 `3`、正式 API 命中 `0`。
- 测试后台入口 JS/CSS 与 Candidate 哈希逐文件相同，因此复用已运行的相同后台静态产物，没有重启后台或 Nginx。
- 内部 MCP 在 `pages/card-list/index` 的真实草稿 Tab 验证“预览并发布”和“生成预览”两种三列操作，控制台错误为空；未置顶、抢焦点或控制桌面。
- 最终准入输出 `READY_FOR_MANUAL_ACCEPTANCE / exit 0`，证据见 `records/20260902-145540-v3-draft/00-243/VERIFICATION.txt`。
- `00-237` 未开始；生产数据库迁移、生产容器重建、正式 Nginx 切流和正式小程序上传仍为 `NOT_AUTHORIZED`。

## 00-250 Hero 中性交接修复候选重新准入（2026-09-01）

- Candidate `20260901-221652-v3-draft` 已冻结；Manifest SHA256 `6b5281f48e402fe3fa133cc141e7ef909f0162f320be86699bda27a31aa5e281`，artifact evidence SHA256 `bfb84504db37623ca50395b43db272b085468f839ba10f09ddf582d1851ca1dc`。
- 冻结测试小程序、workspace build、固定 dev 完全一致：`329` 文件、`2,036,714` 字节、tree SHA256 `f56091d374def4ceca034f00cee362b72473e897676083618716172ecd1bee83`。
- `00-250` 门禁 `44/44`；共享 Renderer `68/68`、分享详情 `91/91`、扩图恢复 `35/35`、Hero 简介 `34/34`，类型检查退出 `0`。
- 项目级 compile cache 清理后，测试 API 命中 `3`，本地业务 API `127.0.0.1:8010` 与正式 API均为 `0`；微信工具自身 `127.0.0.1:11774` 单独统计，不属于业务环境漂移。
- 内部 MCP 在固定 dev 打开 `pkg-actor-card/generate/index?cardId=1`：黄色图片尾带消失，统计卡叠接处为中性浅灰，长页、完整个人简介、底部 spacer 与固定操作栏正常，控制台无 `error/fail`。
- Candidate 后端 JAR 与测试运行 JAR SHA256 均为 `6694acf32c3d75c30227cc34045fa1b0702e2ae035c6b0d874ed4334733cc9ba`，没有重建测试容器或修改测试数据库；测试/正式 API只读健康检查均为 `200`。
- 最终准入 `READY_FOR_MANUAL_ACCEPTANCE / exit 0`；生产决策保持 `NOT_AUTHORIZED`。
