# 执行记录

## 2026-09-01 基线调查

- 页面：`pkg-actor-card/generate/index?cardId=1`。
- 基线 Candidate：`20260901-183000-v3-draft`。
- MCP 页面数据包含完整个人简介；截图中 Hero 的个人简介末行被卡片底部硬切。
- 根因：`.actor-card-renderer__hero-card--intro` 固定为 `281 x 159rpx` 且 `overflow: hidden`，`.actor-card-renderer__hero-copy` 没有行数约束或省略号。
- 长页下方 `.actor-card-renderer__intro` 独立渲染完整原文，数据和接口没有缺失。
- 基线截图：`.sce/evidence/wechat-devtools/00-248-20260901-mcp-generate-card1-retest.png`，SHA256 `8746062FB50EB9E1E486E04FFF76F87C911D05E97032227A806D8014212BCBDC`。
- 发版兼容：纯前端包内样式修复，无后端接口或数据库变化；源码变化后必须重冻测试 Candidate。
- 正式发布：`NOT_AUTHORIZED`。

## 2026-09-01 实施

- `ActorCardRenderer` 的 Hero 简介节点增加专用 class `actor-card-renderer__hero-copy--intro`。
- 专用样式采用三行 `-webkit-line-clamp` 和省略语义；Hero 固定坐标与尺寸未改。
- 下方长页 `.actor-card-renderer__intro` 保持独立，继续渲染完整 `profile.introduction`。
- 新增 `verify:actor-card-hero-intro-summary`，覆盖源码、build/dev、三行规则、正文不截断和 scoped hash 一致性。
- `npm run type-check` 已通过；第一次专项门禁为 `26 passed / 8 failed`，修正两项门禁自身断言后为 `30 passed / 4 failed`，剩余四项均因固定 `dist/dev` 尚未切到新候选。
- `npm run build:mp-weixin` 编译成功并更新 `dist/build`；postbuild 发现微信开发者工具运行后按非干扰门禁拒绝直接同步 `dist/dev`，因此旧 Candidate 验收已失效，必须重冻新 Candidate。
- 原文件 SHA256：`F80B30C220DF678E1C63A2E77AFE6FEB3336A8F207494808DD3BF89D3CCB3987`。
- 修改后文件 SHA256：`5F7B1722C1A2B86989AA274D50DE96C470C4525DB2EAE422175765D786CF8B90`。
- 证据目录：`.sce/evidence/20260901-actor-card-hero-intro-summary/`。

## 2026-09-01 新 Candidate 与运行态复测

- 新 Candidate：`20260901-200255-v3-draft`，Manifest SHA256 `5006200d706fc7b075b28bd4cdc20a851d2dc9407a4b57d3e7ba3d177ccd54f9`。
- 冻结 `mini-program-test`、workspace build、固定 dev 完全一致：`329` 文件、`2,036,481` 字节、tree SHA256 `b22b84054bb62e8f8c67d2ccb7794f865947fe765128b64ff438a914ae8a1738`。
- Renderer 三侧 scoped hash 为 `data-v-a054e050`；`00-249` 专项门禁 `34/34`，共享门禁为 `68/68`、`91/91`、`35/35`。
- 项目级 compile cache 清理成功；缓存测试 API 命中 `3`，本地/正式 API 命中均为 `0`。
- 内部 MCP 打开 `/pkg-actor-card/generate/index?cardId=1`：Hero 个人简介为三行省略摘要，不再硬切；向下滚动后完整个人简介仍全部可见；控制台 `error/fail` 为空。
- Hero 截图 SHA256：`000B143BCE03B521580CAB60F9BE74FE326092BC13D29664FC7ADFD7B266671A`。
- 完整正文截图 SHA256：`BFAA67AB98868C253117C5E29064B37338011BEE8A9D61A3278442780DC7BB34`。
- Candidate 后端 JAR 与当前测试运行 JAR同为 `6694acf32c3d75c30227cc34045fa1b0702e2ae035c6b0d874ed4334733cc9ba`，因此未重建测试容器、未重复迁移测试库。
- 最终准入：`READY_FOR_MANUAL_ACCEPTANCE / exit 0`。
- 正式发布：`NOT_AUTHORIZED`；未执行 `00-237`、生产迁移、Nginx 切流或正式小程序上传。
