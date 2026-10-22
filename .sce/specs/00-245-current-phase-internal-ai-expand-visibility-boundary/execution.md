# 执行记录

## 当前状态

- Spec：`00-245-current-phase-internal-ai-expand-visibility-boundary`
- 分支：`V3.0`，HEAD：`63d34ff`
- 运行态：`20260901-150906-v3-draft` 已物化到固定工程并通过小程序人工验收准入；正式发布仍为 `NOT_AUTHORIZED`
- 目标：步骤 1 仅保留首图选择/上传，首图保存/绑定后由后端自动异步扩图

## 基线

- 源文件：`kaipai-frontend/src/pkg-actor-card/step-visual/index.vue`
- 原始 SHA256：`FC08C885311743137BA0480E86B88058C847DCAD2A6E51B7B2157CEE81611A46`
- 原始字节：`29875`
- `npm run verify:actor-card-step-ui`：`Passed 19 checks`，exit `0`
- `npm run verify:actor-card-single-main-visual`：`Passed 23 checks`，另有 1 项既有显式 asset 分支断言失败，exit `1`
- `npm run type-check`：无输出错误，exit `0`

## 变更边界

本 Spec 修改小程序可见边界、后端自动扩图编排和幂等数据库迁移；迁移只进入新 Candidate，未直接执行测试/生产数据库变更，未修改 Nginx 或正式小程序。

## 已完成修改

- `step-visual/index.vue` 删除 AI 扩图标题、按钮、处理中/结果/失败状态、任务提交和轮询；保留首图模板、素材库、手机上传三种来源。
- `create/index.vue` 的步骤 1 提示改为“选择1张首图”；`pages/home/index.vue` 创建横幅去掉“智能扩图”文案。
- 页面保留 `expandedImageUrl` 的隐藏历史兼容值：初次读取承接旧草稿，来源变化时清空，下一步仍按原字段保存。
- `applySourceBinding` 改为显式 `asset` / `legacy` 分支，修复 `00-242` 来源互斥门禁断言缺口。
- 新增 `verify-00245-actor-card-internal-expand-visibility.mjs` 与 package script；后端原扩图 API/DTO 保留兼容。

## 2026-09-01 后端自动扩图实现

- 步骤 1 保存和 `source_image` 素材绑定成功后，由 `ActorCardController` 调用内部自动编排；提交阶段异常只写服务端日志，不改变演员保存响应。
- 任务以 `actor_card_id + generation_mode + source_fingerprint` 幂等复用；失败任务由后续同来源保存单次认领重试。
- 私有素材任务只持久化 `source_asset_id` 和 SHA-256 指纹，调用 Provider 前即时签发访问 URL；不持久化短时签名 URL。
- Provider 结果先转存受管存储，再由 `ActorCardExpandResultService` 锁定演员卡并重新比对当前首图；来源变化后的旧任务不得回写。
- `ActorCardMainVisualResolver` 只消费与当前来源指纹匹配的新扩图结果；无指纹历史数据继续兼容。
- 步骤 URL 或素材绑定变化时，通过显式 `SET expanded_image_url = NULL, expanded_source_fingerprint = NULL` 失效旧结果，避免 `updateById` 忽略 null。
- 新增 `V20260901_001__actor_card_internal_auto_expand.sql`：任务稳定来源字段、`source_image_url` 可空、来源唯一键和演员卡扩图来源指纹；真实 MySQL 8 连续执行两次通过。
- 专项测试：`56/56`；后端全量测试：`736/736`；候选构建/manifest/准入脚本测试：`21/21`。

## 验证状态

- 源码 SHA256：`527D3EFF4EB3FBAD11A2838F3AA0255835AF5B69057FA9C5DCCD16AF89F5C5B6`（24813 bytes）。
- `npm run type-check`：exit `0`。
- `npm run prepare:tdesign; & .\\node_modules\\.bin\\uni.cmd build -p mp-weixin`：`DONE  Build complete.`，exit `0`。
- `powershell -ExecutionPolicy Bypass -File scripts/sync-mp-weixin.ps1 -ArtifactOnly`：`dist/build scoped style hash consistent`，exit `0`；只处理 build，未镜像 dev。
- build 步骤页检查：WXML/JS/WXSS 扩图标记均为 `False`；build 三件套已更新。
- `npm run verify:actor-card-internal-expand-visibility`：`Passed 12 checks`，dev 侧 5 项失败（dev 仍为人工验收旧候选），exit `1`。
- `npm run verify:actor-card-step-ui`：`Passed 18 checks`，仅 dev scoped hash 等价失败，exit `1`。
- `npm run verify:actor-card-single-main-visual`：`Passed 23 checks`，仅 build/dev 等价失败，exit `1`。
- `npm run audit:mp-package`：所有包体积门禁通过（主包 `1.33 MB / 2 MB`），但沿袭的 4 处本地 `http://` 字符串审计阻塞，exit `1`；未因本 Spec 新增。
- `npm run audit:steering`：`steering audit passed`，exit `0`。

标准 `npm run build:mp-weixin` 的编译阶段成功，但当时 postbuild 因检测到 15 个微信开发者工具进程而 exit `1`；未绕过保护，也未重启工具。该历史阻断已通过新 Candidate 的冻结产物物化流程关闭。

## 回滚验证

- `ROLLBACK.sh` 在另一个副本执行成功，输出 `ROLLBACK_RESULT=restored_original`。
- 回滚副本 SHA256 与原始文件均为 `FC08C885311743137BA0480E86B88058C847DCAD2A6E51B7B2157CEE81611A46`，`ROLLBACK_MATCH=True`。
- 实际源文件和 `MODIFIED_FILE.vue` 保持修改态；正式环境仍为 `NOT_AUTHORIZED`。

## 2026-09-01 新 Candidate 与运行态准入

- Candidate：`20260901-150906-v3-draft`；manifest SHA256 `38398cb1f57031fd25eb84df1b5f47ac2fc828a078cf65b73a56d0e23a3205e6`。
- 冻结 `mini-program-test`、`dist/build/mp-weixin`、`dist/dev/mp-weixin` 均为 `329` 文件、`2,036,252` 字节、tree SHA256 `747df92fc5152a183c2ea37e131f4b44a22fd146b0337e65afb4c715c9e6d6a1`。
- 三项演员卡门禁分别通过 `17/17`、`19/19`、`24/24`；步骤页 WXML/WXSS/JS build/dev 完全一致，演员可见 AI 扩图标记为零。
- 固定工程项目级 compile cache 清理 exit `0`；缓存测试 API 命中 `3`，本地/正式 API 命中 `0`。内部打开 `pages/home/index` 后读取到已登录测试账号、3 个经典模板和测试存储桶资源，控制台错误为空。
- `verify-test-miniapp-acceptance.py --candidate-id 20260901-150906-v3-draft` 返回 `READY_FOR_MANUAL_ACCEPTANCE / exit 0`。
- 回滚只在独立副本执行，副本恢复旧 tree SHA256 `4e9f6ca58d11aa88e9f9b2cc49fce5de999d3832cbd31ee17e3525dd742927ce`；实际固定 dev 保持新候选。
- 证据：`.sce/runbooks/backend-admin-release/records/20260901-150906-v3-draft/00-243/VERIFICATION.txt`。
