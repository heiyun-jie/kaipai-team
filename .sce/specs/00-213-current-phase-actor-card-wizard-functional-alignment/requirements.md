# 00-213 当前阶段演员卡创建向导功能对齐

> 状态：Spec 先行。本 Spec 在实现之前建立书面合同。
> 触发证据：用户在 `pkg-actor-card/step-profile` 追问「个人资料为什么没有同步过来，需要我自己去创建？」。查证后确认这不是设计如此，而是 `00-206` 定义的行为从未实现。以该问题为切口做全向导审计，发现同类缺陷成片存在。
> 范围锚点：`00-206` 已定义本向导的完整需求合同（7 步 + 生成发布）。本 Spec **不重新定义需求**，只登记「`00-206` 合同 ↔ 实际实现」的偏离，并把偏离收敛为可验收、可门禁的对齐项。
> 与 `00-212` 的边界：`00-212` 处理这 9 页的导航壳层（标题、返回按钮、步序进度条），属视觉层；本 Spec 处理同 9 页的功能本体，属行为层。两者不重叠。

## 1. 概述

`pkg-actor-card` 9 页的 UI 壳层已按 `00-206` 建成，但功能本体大面积缺失。审计覆盖 9 个页面、`actor-card-draft` store、5 个 api 模块、`ActorCardController` 与 3 个后端 service，共登记 **6 类偏离**。

**核心结论：这条 7 步向导当前无法走通。** 存在两处相互独立的硬阻断，任一处单独存在即可使流程不可完成：

| 阻断 | 位置 | 机制 |
|------|------|------|
| **阻断 1 · 前端** | `src/stores/actor-card-draft.ts:92-95` | 步骤 3 状态硬编码 `statusCode: 'empty'`，注释称「由子页面动态更新」，但 `stepStatuses` 是纯 `computed` 且全仓无 setter，架构上不可能被更新。`requiredAllDone` 要求步骤 1/2/3/7 全 `done`，故恒为 `false` → Hub 底部按钮永远是「继续下一项」，永远进不了 `generate` 页；`nextIncompleteStep` 在 1、2 完成后恒返回 3 → 点击永远回到步骤 3，构成闭环死路 |
| **阻断 2 · 后端** | `ActorCardGenerateService.java:111-117` | `submitGenerate` 要求 `actor_card_work` 至少 1 行，而全代码库**无任何写入该表的路径**（`ActorCardWork` 仅 5 处引用：Mapper 声明、实体定义、以及此处唯一一次 `selectCount` 读取）。即使绕过阻断 1，生成也必然抛「步骤3（参演作品）至少需要 1 部作品」，且无论如何操作 UI 都无法让该计数变为非 0 |

**第三处必然失败**（不阻断流程但使核心功能不可用）：前后端异步任务状态枚举不一致。后端成功态为 `STATUS_SUCCESS = "success"`（`ActorCardExpandImageService.java:40`、`ActorCardGenerateService.java:34`），`status()` 原样回传 `task.getStatus()`；前端只认 `'done'`（`step-visual/index.vue:143`、`generate/index.vue:77`、`api/actor-card.ts:88,96`），且无归一化。两条轮询必然走到 attempts 耗尽 → 扩图约 60s 后报「扩图失败」、生成约 120s 后报「生成超时」，而后端任务表状态是 `success`、图已产出。DTO 注释写的是 `pending | running | done | failed`（`ActorCardExpandImageRespDTO.java:8`），与实现自相矛盾。

**六类偏离统计**：

| 类别 | 含义 | 条数 |
|------|------|------|
| A · 死控件 | UI 控件绑定态从未被任何提交路径读取，操作无效果 | 9 |
| B · 空承诺 | 屏幕文案承诺的行为无任何代码实现 | 8 |
| C · 占位数据 | 硬编码假数据、TODO 占位、写死统计值 | 5 |
| D · 静默失败 | 空 catch / 无反馈早退，用户无法得知操作失败 | 9 |
| E · 往返断裂 | 字段写入后重进不回填，或因守卫口径不一致无法清空 | 7 |
| F · 契约缺口 | UI 采集的字段无落库通道，或后端字段 UI 从不填充 | 7 |

本 Spec 不改变 `00-206` 已定义的任何需求语义、不改动 `pages.json` 登记、不改动导航壳层（属 `00-212`）。

## 2. 用户故事

作为演员用户，我希望在「个人资料」步骤看到我已填写的资料被自动带入，而不是面对 6 个空输入框重打一遍。

作为演员用户，我希望我认真填完 7 步之后能真的生成出演员卡，而不是在步骤 3 无限打转。

作为演员用户，我希望我拨动的每一个开关、点击的每一个按钮都真的有效果；如果某项能力尚未做好，我希望它不出现在界面上，而不是拨了没反应。

作为演员用户，我希望保存失败时被明确告知并留在当前页，而不是内容悄悄丢失、页面照常前进。

作为演员用户，我希望我上传的照片和视频在换设备后依然可见，而不是只在本机本次会话有效。

作为开发者，我希望「UI 已建但功能未接」这类偏离有一条门禁能拦住，而不是等用户逐页试出来。

## 3. 功能需求

> 编号规则：`3.x` 对应一组偏离的收口。每条标注其对应的 `00-206` 上游条款，以及审计中的偏离编号（A1/B1/… 见 `design.md` 附录全量清单）。

### 3.1 打通向导可完成性（最高优先级）

**描述**：消除阻断 1 与阻断 2，使 7 步向导可被走通。这是本 Spec 唯一的 P0，其余各条在此之前均不可端到端验证。

_对应 `00-206` §3.2、§3.5、§3.10；偏离 C1、F1、F5_

**验收标准**：
- WHEN 步骤 3 已选择至少 1 部作品且每部剧照数 ≥ 1 THEN Hub 页步骤 3 必须显示为 `done`，且状态来源必须是真实数据，不得是硬编码常量。
- WHEN 步骤 3 状态改为真实来源 THEN 必须消除 `stores/actor-card-draft.ts` 中「由子页面动态更新」这一在架构上无法成立的注释与其硬编码值。
- WHEN 必填步骤（1/2/3/7）全部完成 THEN `requiredAllDone` 必须为 `true`，Hub 底部按钮文案必须变为「生成演员卡」，点击必须能进入 `generate` 页。
- WHEN 用户在步骤 3 选定作品并保存 THEN `actor_card_work` 必须实际落行，使 `ActorCardGenerateService` 的 `workCount` 校验可被满足。
- WHEN 后端 `ActorCardRespDTO.stepStatuses`（注释「Hub 页用」）与 `actor_card.step_status_json` 列被判定为死字段 THEN 必须二选一明确处置：或接通为步骤状态的权威来源、或作为死契约删除。不得保留「声明了能力但从不读写」的中间态。
- WHEN 本条完成 THEN 必须有一次记录在案的端到端走通证据：从 Hub 进入、完成 4 个必填步骤、成功进入 `generate` 页并拿到非空 `previewUrl`。

### 3.2 统一异步任务状态枚举

**描述**：消除前后端成功态命名不一致，使扩图与生成两条轮询能识别成功。

_对应 `00-206` §3.3、§3.10；偏离 F3_

**验收标准**：
- WHEN 后端任务成功 THEN 前端轮询必须能识别为成功态，不得走到 attempts 耗尽。
- WHEN 统一枚举 THEN 必须选定单一权威命名并在前后端一致落地；`ActorCardExpandImageRespDTO` 与 `ActorCardGenerateRespDTO` 的 DTO 注释必须与实现一致，不得再出现注释写 `done`、实现写 `success` 的矛盾。
- WHEN 前端类型声明（`api/actor-card.ts:88,96`）与后端实际返回值 THEN 两者必须可对齐，且该对齐关系必须由门禁断言，不得依赖人工记忆。
- WHEN 轮询超出上限 THEN 失败文案必须能区分「任务确实失败」与「轮询超时但任务可能仍在进行」，不得把后者一律显示为失败。

### 3.3 步骤 2 个人资料预填与同步回写

**描述**：本轮用户提问的直接落点。实现 `00-206 §3.4` 已定义但从未实现的预填与同步。

_对应 `00-206` §3.4；偏离 B1、A1、E2、F2_

**验收标准**：
- WHEN 进入步骤 2 且草稿快照为空 THEN 必须从演员资料读取并预填。可用来源已确认存在于 `ActorProfileResp`：`publicName` → 姓名、`height` → 身高、`currentCity` → 城市、`schoolName` → 学校、`intro` → 自我介绍。
- WHEN 草稿快照已存在 THEN 必须优先使用快照，不得用资料覆盖用户在本卡内的修改。
- WHEN 资料存在缺失字段 THEN 必须显示「去个人资料完善」入口（`00-206 §3.4` 已定义，当前完全缺失），同时允许仅填写当前演员卡。
- WHEN 「同步到个人资料」开关开启并保存 THEN 对应字段必须写回演员资料（`updateMyActorProfile` 已存在于 `api/actor.ts:31`，向导内无任何引用）。
- WHEN 开关关闭（默认）THEN 必须不写回，与 `00-206 §6` 全局规则④一致。
- WHEN 开关状态被改变 THEN 该状态必须能持久化并在重进时回填；当前 `ActorCardStepSaveReqDTO` 无对应字段，恒复位为 `false`。
- 「联系方式」字段必须明确处置：`ActorProfileResp` 无 phone/wechat/contact 任一字段，`actor_card` 表无联系方式列，该字段当前仅沉在 `profileSnapshotJson` 内且后端无任何消费方，同时 `step-settings` 的「联系方式」显隐开关所控制的正是这份无消费方的数据。必须在「补齐契约」与「从 UI 撤除」之间二选一，不得保留现状。

### 3.4 死控件收口：实现或移除，不留装饰件

**描述**：9 处 UI 控件的绑定态从未被提交路径读取。每处必须明确二选一，不得保留「拨了没反应」的中间态。

_对应 `00-206` §3.5、§3.6、§3.9；偏离 A2~A9、B5、B6、B8、A5、A6、A7_

**验收标准**：
- WHEN 任一控件被判定为死控件 THEN 必须或实现其承诺行为、或从模板中移除该控件及其文案，不得保留仅改本地 `ref` 而不进入任何提交路径的控件。
- 逐项覆盖（每项均须给出「实现」或「移除」的明确处置）：
  - `step-works` 作品勾选 / 剧照 / 新增作品：全量数据未进入任何 payload，`handleNext` 只提交 `currentStep`，源码注释自陈「通过 settingsJson 临时承接」而实际连 `settingsJson` 都未传。
  - `step-works` 「管理剧照」：实现为 `manageStills = (work) => addStill(work)`，无排序/替换/删除能力；剧照已满 3 张时 `count` 计算为 `0`，点击无任何反应也无提示。
  - `step-settings` 展示顺序上下箭头：`order` 写入 `settingsJson` 但 `onMounted` 从不回读，后端亦无任何解析 `order` 的代码，重进复位且不影响生成结果。
  - `step-photos` 「调整顺序」与「长按拖拽排序」提示：全文件无 `longpress`/`touchstart`/`movable` 任一实现。
  - `step-photos` 「从素材库选择」：占位 toast「素材库即将开放」，而 `getActorAssets` 已存在且 `pkg-profile/assets` 已在使用。
  - `step-attachment` 两个文件选择入口：均为占位 toast「文件选择即将接入」，导致该页「删除」「文件卡片」「handleNext 传值分支」在新建流程中永远不可达，步骤 6 永远「未添加」。
  - `generate` 「保存草稿」：不发起任何请求，只清 store 并跳转。
  - `step-visual` 风格 Tab 与背景图选择：`style` / `backgroundImageUrl` 确实落库，但 `backgroundImageUrl` 在整个后端无任何读取点，`runGenerate` 只取主视觉 URL 作预览，风格与背景对结果零影响。
- WHEN 选择「移除」THEN 对应文案、样式规则不得成为死残留。
- WHEN 选择「移除」且该能力属 `00-206` 已承诺范围 THEN 必须在 `00-206` 或本 Spec 中登记为「已知未实现」，不得静默降低合同。

### 3.5 消除空承诺文案

**描述**：8 处屏幕文案承诺了无实现的行为。文案与实现必须一致。

_对应 `00-206` §3.2~§3.9；偏离 B1~B8_

**验收标准**：
- WHEN 模板文案承诺某行为 THEN 必须存在对应实现；否则必须改写或删除该文案。
- 逐项覆盖：`step-profile:8`「确认信息，将自动填入演员卡」（无预填）；`step-works:9`「可从个人资料勾选」（列表是 3 条硬编码示例：夏日未央/逆光而行/城市边缘，勾选等于把与本人无关的作品放进自己的演员卡）；`step-visual:9`「上传首图后由 AI 自动扩图」（不自动，需另点按钮，且轮询永不成功）；`create:17`「完成后即可由 AI 自动生成专业演员主页」（三重阻断）；`step-photos:39`「长按照片可调整展示顺序」（无实现）；`step-attachment:8,12`「支持 PDF · PPT · PPTX，最多 1 份」（无法选中任何文件）；`step-video`「最多 1 条视频 / 已选择」（存的是本地临时路径）；3 条自认未完成的「即将开放 / 即将接入」提示。
- WHEN `step-works` 的作品列表接入真实来源 THEN 必须消除硬编码示例数据。后端 `/api/actor/works` 已存在（`ActorWorkController.java:22`），前端缺 `src/api/actor-work.ts`。

### 3.6 停止把本地临时路径当 URL 持久化

**描述**：4 处上传点把微信本地临时路径直接写入数据库字段，未经任何上传通道。

_对应 `00-206` §3.3~§3.7；偏离 C4、B7、F7_

**验收标准**：
- WHEN 用户选择图片 / 视频 THEN 必须先经上传通道取得可持久访问的地址，再写入草稿字段，不得把 `wxfile://tmp_*` 形态的本机临时路径落库。
- 逐项覆盖：`step-visual` 首图 → `source_image_url`；`step-photos` 生活照 → `photos_json`；`step-video` 视频 → `video_url`；`step-works` 剧照 → `work.stills`。
- WHEN 首图落库为临时路径 THEN 该路径会被原样提交给 `submitExpandImage` 并透传给 AI provider，而 provider 需要可公网访问的地址。本条必须实测一次扩图链路，确认 provider 侧能取到图。
- WHEN 接入上传 THEN 必须评估是否需要把素材主键关联到演员卡：`uploadActorAsset` 已存在（`api/actor-asset.ts:28`）但向导 9 页无一引用，且 `ActorCardStepSaveReqDTO` 只有 URL 字符串、无 `assetId` 类字段。
- 上传约束沿用 `SHARED_CONVENTIONS.md`：图片 ≤ 10MB、视频 ≤ 100MB。

### 3.7 消除静默失败

**描述**：9 处空 catch 或无反馈早退，使用户无法得知操作已失败，其中两处会导致数据静默丢失或被覆盖。

_对应 `00-206` §4「实时自动保存」；偏离 D1~D9_

**验收标准**：
- WHEN 保存失败 THEN 必须阻断跳转并给出明确反馈。当前 `store` 的 `flushSave` 吞掉异常后 `resolve` 而非 `reject`，各页 `await saveStep(...)` 后无条件 `navigateTo`，结果是弱网下点「下一步」页面照常前进、本页输入永久丢失、回退后看到空表单且无法判断是没存上还是被清空。
- WHEN 草稿读取失败 THEN 必须给出反馈并阻止后续步骤以空值覆盖已存内容。当前 `reload` 静默失败使 `card` 保持 `null`，各页 `onMounted` 回填全得 `undefined`；此后步骤 4/5/6 的「下一步」会因 `photosJson`/`videoUrl`/`attachmentUrl` 走 `!= null` 判定而真实清零已存的生活照、视频、附件。
- WHEN `cardId` 缺失 THEN 不得静默 no-op 后仍带 `cardId=null` 跳转（导致下一页 `Number('null')` = `NaN` 并发出注定失败的 `GET /api/actor-card/draft/NaN`）。
- WHEN 轮询早退（`generate` 三处 `if (!id) return`）THEN 不得让页面永久停留在 `loading` 态且无超时、无提示、无重试入口。
- WHEN 在 `computed` 内解析 JSON THEN 必须有保护。当前 `stepStatuses` 内 `JSON.parse(c.photosJson)` 无 try，一旦脏数据抛错会同时打挂 `doneCount`、`btnText` 与步骤列表 `v-for`，Hub 页 7 个入口全部消失。
- WHEN 页面卸载 THEN 进行中的轮询定时器必须被清理。当前 `step-visual` 的 `pollTimer` 有声明无清理，`generate` 的 `setTimeout` 连句柄都不保存，返回上一页后仍持续请求并对已销毁页面的 ref 赋值。
- WHEN 快照解析失败（3 处 `catch { /* ignore */ }`）THEN 必须提示数据异常，不得静默空表单后以空值覆盖原快照。

### 3.8 修复往返断裂与守卫口径不一致

**描述**：7 处字段写入后无法回填或无法清空。

_对应 `00-206` §4「实时自动保存」、§6 全局规则②；偏离 E1~E7_

**验收标准**：
- WHEN 同一方法内处理同类字段 THEN 守卫口径必须一致。当前 `ActorCardDraftServiceImpl.saveStep` 对 `title`/`style`/`backgroundImageUrl`/`sourceImageUrl`/`expandedImageUrl`/`profileSnapshotJson`/`settingsJson` 用 `StringUtils.hasText`，对 `photosJson`/`videoUrl`/`attachmentUrl` 用 `!= null`。
- WHEN 用户需要清空某字段 THEN 清空语义必须可达。当前 `hasText` 守卫使 7 个字段无法被显式清空（例如选了背景图后无法改为「不用背景」，且 UI 上也没有取消选中的交互）。
- WHEN 用户未做扩图 THEN 不得把原图写入 `expandedImageUrl`。当前 `expandedImageUrl: expandedImageUrl.value || sourceImageUrl.value` 使步骤 1 恒判 `done`，重进时因该字段非空而置 `expandStatus = 'done'`，渲染出「原图/扩图」两张一模一样的图，扩图入口消失且系统认为扩图已完成。
- WHEN 重进步骤 3 THEN 已勾选作品与已上传剧照必须回填（当前 `onMounted` 不做任何回填，全部丢失）。
- WHEN 重进步骤 7 THEN 展示顺序必须回填（当前只回填 3 个 `enabled`，从不读 `order`）。
- WHEN 已存背景图不属当前风格库或库中 URL 有变动 THEN 必须有兜底或明确提示，不得表现为「无选中态、无提示，而 DB 里旧背景仍在且无法清除」。

### 3.9 补齐后端契约缺口

**描述**：7 处 UI 与后端契约不对齐。

_对应 `00-206` §3.5、§3.9~§3.11；偏离 F1~F7_

**验收标准**：
- WHEN UI 采集某字段 THEN 必须有落库通道。当前「参演作品」全部子字段（作品勾选、剧照、新增作品）在 `ActorCardStepSaveReqDTO` 无任何对应字段，`ActorCardController` 无作品相关端点。
- WHEN 后端 DTO 声明某字段 THEN UI 必须填充或该字段必须删除。当前 `title` 有 DTO 字段、有落库实现，但 9 页无任何采集入口或自动生成，导致所有演员卡 `title` 恒为 `null`、名片夹列表标题为空。
- WHEN 完整度被计算 THEN 全链路口径必须一致。当前 `ActorCardDraftServiceImpl` 只累计 3 项却除以 7（全填满也只有 43%），`ActorCardPublishService.calcCardCompletion` 是另一套口径且其中作品项无条件 `done++`，两处数字互相矛盾。注释中的 `settlingsJson` 为拼写错误且所述「视为完成」并未实现。
- WHEN 生成引擎仍为占位 THEN 必须明确登记。当前 `runGenerate` 的 TODO 使预览图直接等于主视觉原图，资料、作品、生活照、视频、附件、设置全部不体现，而用户看到的等待文案是「正在处理背景、扩图，组合长页面」。本条若本轮不实现，必须在 `00-206` 与本 Spec 中登记为「已知占位」并同步文案，不得让文案继续承诺未实现的能力。
- `ActorCardPublishService` 中写死 `0` 的 `materialCount` / `viewCount` 必须登记处置（该接口不被这 9 页调用，影响面在个人中心页，可判定为本轮范围外，但须显式记录）。

### 3.10 回归门禁

**描述**：新增可执行校验脚本，把本 Spec 的结构性断言固化。

_对应本 Spec 全部条款_

**验收标准**：
- WHEN 执行校验脚本 THEN 必须至少断言：步骤 3 状态非硬编码、`stepStatuses` 内 JSON 解析有保护、`store` 无空 catch、前后端成功态枚举一致、模板中不存在「即将开放 / 即将接入」类占位文案、`step-works` 无硬编码示例作品、向导内无 `wxfile` 形态路径直接落库、`saveStep` 守卫口径一致。
- WHEN 任一断言失败 THEN 脚本必须打印全部失败项后再以非零码退出，不得首错即停（`00-211` 已记录该形态缺陷）。
- WHEN 脚本落地 THEN 必须接入 `package.json` 成为可调用命令；未接入的脚本不计入门禁（`00-205` 已记录该形态问题）。
- WHEN 门禁建立 THEN 必须以反向注入证明其非空转：临时改坏一条被断言的事实，确认脚本确实失败。

## 4. 非功能需求

- 本 Spec 跨前后端。后端改动涉及 `actor_card_work` 写入路径与状态枚举，属共享系统改动，实施前须逐项确认影响面。
- 前端改动后主包体积增量必须实测记录，仍需满足微信单包 `2048 KB` 约束。
- `vue-tsc --noEmit` 必须 `0` 报错。
- 本 Spec 条款数量较多，实施必须分任务逐条推进，一次只做一个任务，做完停下等审核。§3.1 为 P0，其余各条在其之后。

## 5. 约束条件

- 改前端 `src` 后必须执行 `npm run build:mp-weixin`，并核对关键字进入 `dist/build` 与 `dist/dev` 双层产物，否则不得声称完成。
- AI 调用统一由后端封装，前端不直接调用（`00-206 §5` 与项目全局规则）。
- 演员卡 / 个人资料 / 素材库三者相互独立；删除演员卡不删除原始素材（`00-206 §6` 规则⑤⑥）。
- 当前演员卡修改默认不覆盖个人资料（`00-206 §6` 规则④）——§3.3 的同步开关是该规则的显式例外，默认关闭。
- 身份证号后端加密存储、前端只展示脱敏值。
- 本 Spec 的审计结论全部来自静态代码阅读。凡标注需实测的条款（§3.1 端到端走通、§3.6 provider 取图、§3.2 枚举对齐），实施时必须补实测证据，不得以静态阅读结论代替运行验证。
- 若某条偏离在实施时被判定为「本轮不做」，必须在 `design.md` 的偏离清单中标注为已知缺口并说明理由，不得静默删除该条。
