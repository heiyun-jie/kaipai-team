# 00-213 演员卡创建向导功能对齐 - 执行步骤

> 执行原则：一次只做一个任务，做完停下等用户审核。
> 每个任务开工前读 `requirements.md` + `design.md` + `SHARED_CONVENTIONS.md`。

**状态：T0 已裁决（见 design.md §3）、T1 已完成（端到端实测待补）、T2 已完成。下一步 T3。实施记录见 design.md §7.1。**

审计结论全部来自静态代码阅读，未做运行验证。凡标注「须实测」的任务，不得以静态阅读或 grep 结论代替。

## T0 裁决待定项（阻塞门）— 已完成

就 `design.md §3` 的 D1~D5 取得用户裁决并回填进 `design.md`：

- **D1** 作品落库形态：专用端点写 `actor_card_work` 子表 / 扩 DTO 加 `worksJson`
- **D2** 步骤 3 状态来源：后端接通 `stepStatuses` / 前端自行计算并删后端死字段
- **D3** 成功态枚举统一方向：后端改 `done` / 前端归一化 `success`
- **D4** 「联系方式」处置：补契约 / 从 UI 撤除
- **D5** 各死控件逐项「实现 or 移除」

D1 与 D2 联动决定后端结构，D3 决定改动落在哪一侧。未裁决即开工，翻转会返工。

**Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.9**

## T1 打通向导可完成性（P0）— 已完成，端到端实测待补

按 `design.md §4.1` 消除两处硬阻断：

- 前端 `stores/actor-card-draft.ts:92-95` 步骤 3 状态改为真实来源（依 D2），并删除「由子页面动态更新」这一在 `computed` 架构下不成立的注释
- 后端建立 `actor_card_work` 写入路径（依 D1），使 `ActorCardGenerateService:111-117` 的 `workCount` 校验可被满足
- `ActorCardRespDTO.stepStatuses` 与 `actor_card.step_status_json` 二选一处置（依 D2）：接通或删除，不留「声明了能力但从不读写」的中间态

**须实测**：留一次端到端走通证据 —— Hub 进入 → 完成必填 1/2/3/7 → 进入 `generate` → 拿到非空 `previewUrl`。此前其余任务均无法端到端验证。

**Validates: Requirements 3.1**

## T2 统一异步任务状态枚举 — 已完成（取 D3 修正案：后端 DTO 边界归一化）

按 `design.md §4.2` 依 D3 落在单侧。两侧共同要求：DTO 注释与实现一致、轮询耗尽文案区分「任务失败」与「轮询超时」。

~~若选 D3-A（后端改 `done`）：**须实测查库**确认存量 `success` 行的读取兼容。~~
D3 取修正案（DTO 边界归一化，持久层不动），故该查库前置条件不再适用 —— 持久层与 `AiProfileCardServiceImpl` 的 `success` 语义均未改动，无迁移风险。

**Validates: Requirements 3.2**

## T3 步骤 2 预填与同步回写

按 `design.md §4.3`：

- `onMounted` 在草稿快照为空时拉取演员资料预填（`publicName`/`height`/`currentCity`/`schoolName`/`intro` 五字段映射已确认）；快照非空则优先快照，不得覆盖用户在本卡内的修改
- 新增 `00-206 §3.4` 要求但当前完全缺失的「去个人资料完善」入口
- 「同步到个人资料」开关接 `updateMyActorProfile`，注意其 `expectedProfileVersion` 乐观锁需先读当前版本；关闭时（默认）不写回
- 开关状态持久化，或明确判定为「单次生效」并在 UI 上体现该语义
- 「联系方式」按 D4 处置

本任务是用户本轮提问的直接落点。

**Validates: Requirements 3.3**

## T4 死控件收口

按 `design.md §4.4` 逐项处置 9 条（A1~A9），每条必须明确「实现」或「移除」，不留拨了没反应的中间态。选择移除时，文案与样式不得成为死残留；若该能力属 `00-206` 已承诺范围，须显式登记为已知缺口，不得静默降低合同。

**Validates: Requirements 3.4**

## T5 消除空承诺文案

按 `design.md §4.5` 收敛 8 条（B1~B8），文案与实现同步。`step-works` 硬编码示例作品（夏日未央/逆光而行/城市边缘）换真实来源：新建 `src/api/actor-work.ts` 对接已存在的 `/api/actor/works`，剧照对接 `GET /api/actor/works/{id}/assets`。

**Validates: Requirements 3.5**

## T6 上传通道接入

按 `design.md §4.6` 修 4 处临时路径落库（`step-visual` 首图、`step-photos` 生活照、`step-video` 视频、`step-works` 剧照），统一走 `uploadActorAsset`。评估是否需要 `assetId` 关联以满足 `00-206 §6` 规则⑥的资产追溯。约束：图片 ≤ 10MB、视频 ≤ 100MB。

**须实测**：跑一次 `POST /api/actor-card/draft/{id}/expand-image`，查 `actor_ai_profile_card_task.failure_reason`，确认 provider 侧能取到图。

**Validates: Requirements 3.6**

## T7 消除静默失败

按 `design.md §4.7` 修 9 条（D1~D9）。优先 `store` 两处空 catch：`flushSave` 失败须 reject 以阻断跳转，`reload` 失败须可被感知以阻止后续步骤空值覆盖。注意 D1+D2+E6 构成组合缺陷，修 D2 是关键。

**Validates: Requirements 3.7**

## T8 往返与守卫口径

按 `design.md §4.8` 统一 `saveStep` 的 `hasText` / `!= null` 两套口径，须同时满足「清空语义可达」与「读取失败时不误清」。修 `expandedImageUrl` 被原图污染（E5）、步骤 3 与步骤 7 回填缺失（E3/E4）、背景图跨风格回填无兜底（E7）。

**Validates: Requirements 3.8**

## T9 后端契约缺口

按 `design.md §4.9` 处置 F4（`title` 无采集入口，恒 null 致名片夹标题为空）、C3（完整度两套口径互相矛盾，含 `settlingsJson` 拼写错误）、C2（生成引擎 TODO 占位 —— 若本轮不实现真实渲染，须在 `00-206` 与本 Spec 登记为已知占位并同步等待文案，不得让文案继续承诺未实现的能力）。F6 宽松兼容，登记备查。

**Validates: Requirements 3.9**

## T10 回归门禁脚本

按 `design.md §6` 新建 `scripts/verify-actor-card-wizard-alignment.mjs`，7 组断言，接入 `package.json` 为 `verify:wizard-alignment`。**必须收集全部失败项后再非零退出**（不得首错即停，见 `00-211`），**必须接入 `package.json`**（未接入不计门禁，见 `00-205`），**必须反向注入证明非空转**。

同时确认 `npm run verify:nav-title`（`00-212`）不回归。

**Validates: Requirements 3.10**

## T11 构建与产物核验

`npx vue-tsc --noEmit` 须 `0`；`npm run build:mp-weixin` 须 DONE 且双侧 scoped hash 一致；核对关键字进入 `dist/build` 与 `dist/dev` —— **本项目 wxss 为换行美化格式，单行 grep 匹配不到，须用多行 dump**（`00-212` 已踩）；实测主包 apparent bytes 对 2048 KB 预算（当前基线 424.29 KB，MAIN = TOTAL 减四个分包根）。后端须编译通过并核对涉及表的迁移。

**Validates: Requirements 4, 5**

## T12 文档同步

同步 `.sce/specs/README.md`（新增 00-213 索引）、`spec-code-mapping.md`（9 页 + store + 新增 api/脚本 + 后端 service 映射）、`CURRENT_CONTEXT.md`、`00-206`（登记本轮已实现项与仍为已知缺口项，使其合同与实现一致）。若 `SHARED_CONVENTIONS.md` 需补「上传通道」或「异步任务状态枚举」约定，一并回填。

**Validates: Requirements 5**
