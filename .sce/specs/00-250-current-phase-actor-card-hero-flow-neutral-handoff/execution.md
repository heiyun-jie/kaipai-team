# 执行记录

## 2026-09-01 基线调查

- 页面：`pkg-actor-card/generate/index?cardId=1`。
- 基线 Candidate：`20260901-200255-v3-draft`，准入在修改前为 `READY_FOR_MANUAL_ACCEPTANCE / exit 0`。
- Hero 最后两张卡底部为 `1236rpx`，Hero 底部为 `1334rpx`，背景图片尾部为 `98rpx`；flow 顶部另有 `16rpx` padding，总交接高度约 `114rpx`。
- 用户截图显示这段背景图片为大面积黄色，统计摘要与 Hero 视觉断裂。
- 发版兼容：纯前端样式修复，无 API、后端或数据库变化；修改后必须重新冻结 Candidate。
- 正式发布：`NOT_AUTHORIZED`。

## 2026-09-01 实施

- `.actor-card-renderer__hero::after` 增加 `98rpx`、`$kp-color-surface-muted` 的中性尾部，图层为 `z-index:1`。
- `.actor-card-renderer__flow` 改为 `position:relative / z-index:3 / margin-top:-74rpx / padding-top:0`，统计卡顶部为 `1260rpx`，与末卡保持 `24rpx`。
- Hero `1334rpx`、`aspectFill`、七区坐标、`00-249` 简介摘要和正文结构保持不变。
- 新增 `verify:actor-card-hero-flow-handoff`；源码门禁通过，初次构建后为 `40 passed / 4 failed`，剩余四项均因固定 `dist/dev` 仍是旧 Candidate。
- `npm run type-check` 已通过；MCP 构建编译成功并更新 `dist/build`，postbuild 按非干扰门禁拒绝直接覆盖运行中的 `dist/dev`。
- 原文件 SHA256：`5F7B1722C1A2B86989AA274D50DE96C470C4525DB2EAE422175765D786CF8B90`。
- 修改后文件 SHA256：`778F94FD262BA724A67B5C26ADD10722DAE71C4CA85F98F3F8A8F290F87AF490`。
- 证据目录：`.sce/evidence/20260901-actor-card-hero-flow-handoff/`。

## 2026-09-01 新 Candidate 与运行态复测

- 新 Candidate：`20260901-221652-v3-draft`，Manifest SHA256 `6b5281f48e402fe3fa133cc141e7ef909f0162f320be86699bda27a31aa5e281`。
- 冻结 `mini-program-test`、workspace build、固定 dev 完全一致：`329` 文件、`2,036,714` 字节、tree SHA256 `f56091d374def4ceca034f00cee362b72473e897676083618716172ecd1bee83`。
- `verify:actor-card-hero-flow-handoff` 为 `44/44`；个人简介、共享 Renderer、分享详情、扩图恢复门禁分别为 `34/34`、`68/68`、`91/91`、`35/35`，类型检查退出 `0`。
- 项目级 compile cache 清理成功；测试 API 命中 `3`，本地业务 API `127.0.0.1:8010` 与正式 API均为 `0`。
- 内部 MCP 在 `pkg-actor-card/generate/index?cardId=1` 确认黄色图片尾带消失、统计卡左右为中性浅灰、长页可滚动到 `2822px`、完整简介和底部 spacer 正常，控制台 `error/fail` 为空。
- Hero 交接截图 SHA256：`4C146A9A7F2F077ACC5638E457877B7563E36EA692B16191FC23960967C9E37D`；长页截图 SHA256：`4FD8140C75A49BCB3836CF243186F438D256326E269DDB5D9E3FBAD9A6224F48`。
- Candidate 后端 JAR 与测试运行 JAR同为 `6694acf32c3d75c30227cc34045fa1b0702e2ae035c6b0d874ed4334733cc9ba`，因此未重建测试容器、未重复迁移测试库。
- 最终准入：`READY_FOR_MANUAL_ACCEPTANCE / exit 0`。
- 正式发布：`NOT_AUTHORIZED`；未执行 `00-237`、生产迁移、Nginx 切流或正式小程序上传。
