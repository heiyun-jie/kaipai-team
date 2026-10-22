# 执行记录

## 2026-09-01 基线调查

- 页面：`pkg-actor-card/generate/index?cardId=1`。
- Candidate：`20260901-150906-v3-draft`。
- 测试库：只读查询 `kaipai_test`，未访问或修改生产库。
- 当前首图：`actor_card_media_set.set_id=1`、`actor_card_media_item.asset_id=1`，绑定时间 `2026-08-28T08:51:04`。
- 当前来源指纹：`05872e925e35d07fb73ba9cabc6c054e6202a88b7d243bd0f591e65208fc925e`。
- `actor_card.expanded_image_url`：空。
- `actor_card.expanded_source_fingerprint`：空。
- 当前卡片 `expand_image` 任务数：`0`；因此本次不是 Provider 失败，而是任务从未创建。
- 测试后端部署时间：`2026-09-01T08:20:23Z`；历史首图绑定早于自动扩图后端部署。
- 现有触发点只有步骤 1 保存和 `source_image` 绑定替换；重新生成演员卡不会触发扩图。
- Renderer Hero 当前使用 `mode="scaleToFill"`，导致回退原图填充固定 750 x 1334 画布时改变宽高比。
- 正式发布状态：`NOT_AUTHORIZED`；基线调查未修改测试或生产运行环境。

## 当前状态

- Spec 与实现已完成；后端全量测试 `745/745`、前端类型检查及 `00-248 / 00-228 / 00-245 / 00-242` 专项门禁通过。
- 卡主读取草稿和直接生成现在都会复用既有幂等、非阻断的内部扩图入口；匿名公开页仍不触发扩图。
- 共享 Renderer Hero 已从 `scaleToFill` 改为 `aspectFill`，源码、build、dev 三侧专项检查通过。
- 修改/差异/验证/回滚证据位于 `.sce/evidence/20260901-actor-card-legacy-auto-expand-recovery/`；独立副本已恢复原始双文件 SHA256，实际工作区仍保持修改态。
- 新 Candidate `20260901-183000-v3-draft` 已仅部署测试环境；冻结小程序、workspace build、固定 dev 均为 `329 / 2,036,251 / 559379b9ca7f7566e1d8a2f1c99c96f5f17cb96e7f6160b2c40332ff3f41d1bb`。
- 内部 MCP 与测试库只读复测通过，最终准入为 `READY_FOR_MANUAL_ACCEPTANCE / exit 0`；正式发布保持 `NOT_AUTHORIZED`。

## 2026-09-01 Candidate 运行态复测追加发现

- Candidate `20260901-174738-v3-draft` 已只部署到测试后端并通过 MCP 打开固定 dev 工程；生产容器指纹前后相同，生产变更为 `NONE`。
- 卡主读取已补建 `expand_image` 任务：`status=success`、`assetId=1`、来源指纹 `05872e925e35d07fb73ba9cabc6c054e6202a88b7d243bd0f591e65208fc925e`，卡片扩图字段和任务生成 URL 均已写入。
- 追加缺陷：测试私有桶中的扩图稳定 URL 未签名，MCP 重新读取后 Hero 进入“主视觉资源暂不可用”；这不是 Provider 失败，而是成功产物的读 URL 合同缺口。
- 本 Candidate 不生成 `runtime-readiness.json`，不得进入人工验收；需要完成响应期短时签名与来源回退后再次冻结。

## 2026-09-01 私有桶读 URL 修复

- `AiGeneratedImageStorage.issueReadUrl` 仅为当前 bucket/region 的受管 HTTPS 对象签发 10 分钟读 URL；外部 HTTPS URL 原样返回。
- `ActorCardPublicServiceImpl` 和 `ActorCardPublishService` 只在响应组装期签名扩图 URL，不把签名写回数据库。
- 签名异常时通过 `ActorCardMainVisualResolver.resolveSourceDisplayUrl` 回退当前来源绑定或历史来源图，详情和列表读取不中断。
- 后端专项测试 `38/38`、全量测试 `745/745`、前端类型检查、`00-248` 门禁 `35/35`、共享 Renderer 门禁 `68/68` 全部通过。
- 扩展事务证据已在 `rollback-test-v11` 独立副本恢复 10 个原始文件 SHA256 并删除 2 个新增测试/门禁文件；实际工作区保持修复态。
- `20260901-174738-v3-draft` 保持失效；下一步必须使用全新 Candidate，仅部署测试环境并完成内部 MCP 运行态复测。

## 2026-09-01 新 Candidate 测试运行态闭合

- Candidate：`20260901-183000-v3-draft`；Manifest SHA256 `4cdfd25173538ce79330f1014c0987edeb91d83f3eea883387d4de3214fb6754`；Artifact Evidence SHA256 `abf90ae7c52eb90b6376b54a3eca5be11bf5751eca1628e4ce60fe29b3f34232`。
- Candidate 与测试运行后端 JAR SHA256 均为 `6694acf32c3d75c30227cc34045fa1b0702e2ae035c6b0d874ed4334733cc9ba`；只备份和迁移 `kaipai_test`，只重建 `kaipai-backend-test`。
- 内部 MCP 固定打开 `dist/dev/mp-weixin` 的 `pkg-actor-card/generate/index?cardId=1`；Hero 使用带 `q-sign-algorithm` 的 `actor-card-expand` 私有桶读 URL，运行 WXML 为 `mode="aspectFill"`，没有 Hero placeholder，控制台 `error/fail` 均为空。
- MCP 截图 `.sce/evidence/wechat-devtools/00-248-20260901-183000-generate-card1.png` 显示真实扩图，没有原图纵向拉伸或资源占位。
- 标准 release helper 对 `kaipai_test` 的只读查询确认：`CARD_EXPANDED_URL=1`；卡片指纹为 `05872e925e35d07fb73ba9cabc6c054e6202a88b7d243bd0f591e65208fc925e`；最新任务为 `success / expand_image / asset_id=1 / generated_url=1 / failure=NULL`，任务指纹与卡片一致。
- 数据库只读证据：`.sce/runbooks/backend-admin-release/records/20260901-183000-v3-draft/00-248/runtime-db/`。
- `runtime-readiness.json` 与 `test-stack-readiness.json` 已绑定同一 Candidate；`verify-test-miniapp-acceptance.py` 返回 `READY_FOR_MANUAL_ACCEPTANCE / exit 0`。
- 生产容器前后均为 `1195a88da11fc2e4141091ee6494c291c287bb48a61725c469d420f32b82bea1 / 2026-07-21T14:10:50.90030867Z / restart=0 / running`，`productionMutation=NONE`。未执行 `00-237`、生产迁移、Nginx 切流或正式小程序上传。

## 2026-09-01 MCP 截图复测

- 仅使用微信 DevTools 内部 MCP，固定工程为 `dist/dev/mp-weixin`；未控制桌面、窗口焦点、坐标、鼠标或键盘。
- MCP 内部打开 `pkg-actor-card/generate/index?cardId=1`，当前 `pageId=135`；页面数据确认 `backgroundImageUrl` 与 `previewImageUrl` 相同，均为测试桶 `actor-card-expand` 的 `q-sign-algorithm` 签名 URL。
- 目标截图：`.sce/evidence/wechat-devtools/00-248-20260901-mcp-generate-card1-retest.png`，`293 x 633`、`61,914` 字节、SHA256 `8746062FB50EB9E1E486E04FFF76F87C911D05E97032227A806D8014212BCBDC`。
- 视觉复核：真实扩图已显示，无资源 placeholder，人物比例未被纵向拉伸，首屏内容和固定底部操作区正常可见。
- 截图同时确认技能数据为 `12` 项；Hero 摘要按既有 `skillItems.slice(0, 4)` 只展示前 `4` 项，长页下方完整技能区遍历全部 `skillItems`。这是既有摘要规则，不属于本 Spec 的扩图修复通过项。
- generate 页 build/dev JS、WXML、WXSS SHA256 完全一致；控制台 `grep -i error` 与 `grep -i fail` 均为空。
- 验证记录：`.sce/evidence/wechat-devtools/00-248-20260901-mcp-generate-card1-retest-VERIFICATION.txt`；结论 `PASSED`。
