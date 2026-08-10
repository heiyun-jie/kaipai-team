# 00-213 演员卡创建向导功能对齐 - 技术设计

> 上游需求：本目录 `requirements.md`
> 上游合同：`00-206-v2-miniapp-actor-card-creation-wizard/requirements.md`
> 同期壳层 Spec：`00-212`（导航壳层，本 Spec 不触碰）

## 1. 范围与边界

### 1.1 本 Spec 覆盖

| 层 | 文件 |
|----|------|
| 页面 | `src/pkg-actor-card/{create,step-visual,step-profile,step-works,step-photos,step-video,step-attachment,step-settings,generate}/index.vue` |
| 状态 | `src/stores/actor-card-draft.ts` |
| 接口 | `src/api/actor-card.ts`、`src/api/actor.ts`、`src/api/actor-asset.ts`；**缺失待建** `src/api/actor-work.ts` |
| 后端 | `service/actor/ActorCardDraftServiceImpl.java`、`ActorCardExpandImageService.java`、`ActorCardGenerateService.java`、`ActorCardPublishService.java`、`controller/api/actor/ActorCardController.java`、`model/actor/card/dto/*` |
| 表 | `actor_card`、`actor_card_work`、`actor_ai_profile_card_task` |

### 1.2 本 Spec 不覆盖

- 导航壳层（标题、返回按钮、`KpPageNav`、`KpStepProgress`）→ `00-212`
- `pages.json` 路由登记（9 页已全部登记，核对无缺）
- 首页改版、名片夹页、个人中心改版、底部 Tab（`00-206 §3.1`、§3.11~§3.13），本 Spec 只处理向导本体与生成链路
- `ActorCardPublishService` 写死 `0` 的 `materialCount` / `viewCount`：影响面在个人中心页，判定为范围外，按 `requirements §3.9` 末条仅登记不实施

## 2. 阻断链路分析

两处硬阻断相互独立，任一处单独存在即使流程不可完成。修复必须同时覆盖，只修一处仍然走不通。

```
用户完成 7 步
   │
   ├─ 阻断 1（前端）─────────────────────────────────────────
   │  stores/actor-card-draft.ts:92-95
   │    step 3 → statusCode: 'empty'（硬编码常量）
   │       ↑ 注释「由子页面动态更新」
   │       ↑ stepStatuses 是纯 computed，仅依赖 card.value
   │       ↑ 全仓 grep stepStatuses = 4 处，无任何 setter
   │       ⇒ 架构上不可能被更新
   │  :120  requiredAllDone = 必填(1/2/3/7) 全 done  ⇒ 恒 false
   │  :124  nextIncompleteStep = 首个非 done       ⇒ 1、2 完成后恒返回 3
   │  create/index.vue btnText ⇒ 永远「继续下一项」
   │  ⇒ 永远进不了 generate 页；点击永远回到步骤 3 → 闭环死路
   │
   └─ 阻断 2（后端）─────────────────────────────────────────
      ActorCardGenerateService.java:111-117
        workCount = selectCount(actor_card_work WHERE card_id = ?)
        if (workCount == 0) throw BizException("步骤3（参演作品）至少需要 1 部作品")
           ↑ ActorCardWork 全仓 5 处引用：
             Mapper 声明 / 实体定义 / 此处唯一一次 selectCount
           ↑ 零 insert，零 update，controller 无作品端点
           ↑ ActorCardStepSaveReqDTO 无 works 字段
           ⇒ 该计数无论如何操作 UI 都不可能非 0
      ⇒ 即使绕过阻断 1（如从 card-list 直达 generate），生成必然被拒
```

第三处必然失败（不阻断流程，但使核心功能不可用）：

```
后端 STATUS_SUCCESS = "success"
  ActorCardExpandImageService.java:40  → :144 set(status, STATUS_SUCCESS)
  ActorCardGenerateService.java:34     → :130 set(status, STATUS_SUCCESS)
  两个 status() 均 resp.setStatus(task.getStatus())  ← 原样回传，无映射
        │
        ▼
前端只认 'done'，无归一化（grep 'success' 于 api/ utils/ stores/ = 0 命中）
  step-visual/index.vue:143   if (s === 'done')
  generate/index.vue:77       if (s === 'done')
  api/actor-card.ts:88,96     status: 'pending'|'running'|'done'|'failed'
        │
        ▼
轮询走到 attempts 耗尽 ⇒ 扩图约 60s 报「扩图失败」、生成约 120s 报「生成超时」
                        而任务表状态是 success、图已产出
DTO 注释 ActorCardExpandImageRespDTO.java:8 写 /** pending | running | done | failed */
  ⇒ 注释与实现自相矛盾，是该缺陷长期未被发现的原因
```

## 3. 裁决记录

用户裁决：「按照最佳实践去修改」（2026-08-10）。5 项均按最佳实践定案，理由以既有代码事实为依据，逐项记录如下。

### D1 · 步骤 3 作品落库形态 → **取方向 A：专用端点写 `actor_card_work` 子表**

决定性事实：该表**已完整存在**且列齐备（`V20260731_001__actor_card_tables.sql:39-57`：`card_id` / `source_work_id` / `work_title` / `work_type` / `role_name` / `stills_json` / `sort_order`），实体 `ActorCardWork.java` 已按此建模，Mapper 已声明，且 `GenerateService:111` 的门禁本就读这张表。

方向 B（加 `worksJson`）会制造第二个事实源：同一份作品数据一份在 `actor_card.works_json`、一份在空置的 `actor_card_work` 表，且必须改写 `GenerateService` 的 `selectCount` 校验。这正是 C3「完整度两套口径互相矛盾」的同类成因——本 Spec 在修一个双事实源缺陷，不应同时引入另一个。

关系型子表也是唯一能满足 `00-206 §3.5`「剧照作为快照绑定演员卡，不随演艺经历原始数据变化」的形态：`source_work_id` 可空正是为「新增作品」预留的，表设计者已经想清楚了。

### D2 · 步骤 3 状态来源 → **取方向 A：后端填 `stepStatuses`，前端消费**

决定性事实：`ActorCardRespDTO.StepStatus` 的字段（`step` / `statusCode` / `statusLabel`）与前端 `StepStatus` 接口**逐字段同构**，注释也已写明「Hub 页用」。这个契约设计好了却从未 set，正是 C1 硬编码的根因。

更重要的是：步骤 3 的完成与否**只有后端知道**（取决于 `actor_card_work` 行数）。若让前端自行推导，前端必须先拿到完整作品列表才能判断，等于把「状态判定」和「数据展示」两件事耦合起来；而 Hub 页本不需要作品明细。

同时这条修掉 C3 的根源：完成度与步骤状态从此由**同一处**派生（`deriveStepStatuses` → `calcCompletion` 复用其结果），不再有 Draft 侧与 Publish 侧两套口径。

前后端职责边界：后端给「状态」（`statusCode` / `statusLabel`，数据事实），前端保留「标签」与「必填」（`label` / `required`，展示配置）。前端按 `step` 合并，不重复实现判定逻辑。

`actor_card.step_status_json` 列判定为**删除对象**（不落库）：步骤状态是纯派生值，持久化它会立刻产生「与真实数据不一致」的第三个事实源。本轮不写不读，并在 §4.9 登记该列待清理。

### D3 · 成功态枚举 → **取「后端 DTO 边界归一化」（对 A / B 的修正案）**

原两个方向都有缺陷，故取第三条路：**持久层保持 `success` 不变，在两个 `status()` 方法的 DTO 出口处映射为 `done`**。

理由：
- 方向 A（改持久层为 `done`）需要数据迁移。`actor_ai_profile_card_task` 表已有 `success` 存量行，且 `AiProfileCardServiceImpl` 有 9 处 `STATUS_SUCCESS` 共享该表语义（`:461` / `:499` / `:574` 均以 `success` 做查询条件），改持久层会波及非本 Spec 范围的链路。风险显著大于收益。
- 方向 B（前端归一化）把「契约不一致」变成「每个客户端各自打补丁」。今后任何新客户端都得重新踩一次。
- 归一化放在 DTO 边界，则 **DTO 注释里写的 `pending | running | done | failed` 从此成为真契约**——注释不必改，因为它本来就描述的是 API 契约，错的是实现没兑现它。前端零改动，任何未来客户端都拿到一致值，且无迁移风险。

这是「契约在边界处兑现」的标准做法：内部实现细节（`success`）不泄漏到 API 契约（`done`）。

### D4 · 「联系方式」→ **保留字段，补预填源，不加表列**

`profileSnapshotJson` 是**快照**语义，联系方式作为「这张卡对外展示的联系方式」存在其中是正确的——它本就该随卡冻结，而不是跟着个人资料实时变。所以不需要给 `actor_card` 加列。

从 UI 撤除是错的：演员卡的用途就是被人联系，`00-206 §3.9` 也明确要求「可配置联系方式的展示开关」。

真正的缺口只有两个，本轮补齐其一：预填源用 `UserInfo.phone`（`src/types/user.ts:11`，已确认存在）。`ActorProfileResp` 确实无联系字段，但用户手机号本就在会话里，无需新契约。

「显隐开关无消费方」属生成引擎占位问题（C2），随 §4.9 一并登记，不在本轮解决。

### D5 · 各死控件 → **必填链路实现，可选项移除并登记**

按「文案与实现必须一致」这一唯一标准判定，而非按工作量：

| 处置 | 项 | 依据 |
|------|-----|------|
| **实现** | A2 作品与剧照落库、A1 同步开关、B1 预填 | 必填链路（步骤 3 是必填）+ 用户本轮直接诉求 |
| **移除 UI** | A5/B5 拖拽排序、A6 素材库入口、A7 附件文件选择、A3 剧照管理面板 | 均为「承诺了但无实现」，且非必填链路。留着就是欺骗用户；移除后文案同步删除，并在 `00-206` 登记为已知缺口 |
| **修正行为** | A4 展示顺序（改为回读，不删功能）、A8 保存草稿（补真实请求） | 成本极低，且删掉反而降低已有能力 |
| **随生成引擎登记** | A9 风格/背景不生效、C2 预览图占位 | 需真实渲染引擎，非本轮范围 |

「先移除再补」优于「留着装饰件」：装饰件会让用户以为功能存在并反复尝试（本轮用户报「点击无反应」正是此类），而移除后用户至少知道该能力尚未提供。

## 4. 各条款技术方案

### 4.1 打通向导可完成性（§3.1，P0）

前端：
- `stores/actor-card-draft.ts` 步骤 3 分支改为读真实数据源（取值依 **D2**）。
- 同时移除「由子页面动态更新」注释——该注释描述的机制在 `computed` 架构下不成立，保留会继续误导。
- `stepStatuses` 内 `JSON.parse` 加保护（与 §3.7 合并实施，见 4.7）。

后端：
- 建立 `actor_card_work` 写入路径（形态依 **D1**）。
- `ActorCardRespDTO.stepStatuses` 与 `actor_card.step_status_json` 二选一处置（依 **D2**）：接通或删除，不留中间态。

验证：必须留一次端到端走通证据（Hub → 完成 1/2/3/7 → 进入 `generate` → 拿到非空 `previewUrl`），静态断言不可替代。

### 4.2 统一异步任务状态枚举（§3.2）

依 **D3** 落在前端或后端单侧。两侧共同要求：
- `ActorCardExpandImageRespDTO` / `ActorCardGenerateRespDTO` 的 DTO 注释必须与实现一致。
- 轮询耗尽的文案须区分「任务失败」与「轮询超时、任务可能仍在进行」。当前两者都显示为失败，掩盖了本缺陷。
- 门禁须断言前后端枚举一致（见 §6），不依赖人工记忆。

若选 D3-A（后端改 `done`）：须先确认 `actor_ai_profile_card_task` 表已有 `success` 存量行的读取兼容，以及 `AiProfileCardServiceImpl` 的 9 处 `STATUS_SUCCESS` 是否共享同一张表。**此项须实测查库，不可仅凭静态阅读**。

### 4.3 步骤 2 预填与同步回写（§3.3）

字段映射（来源已确认存在于 `src/types/profile.ts` `ActorProfileResp`）：

| 表单字段 | 预填来源 | 同步回写目标 |
|---------|---------|-------------|
| 姓名 | `publicName` | `core.publicName` |
| 身高 | `height` | `core.height` |
| 城市 | `currentCity` | `core.currentCity` |
| 学校 | `schoolName` | `career.schoolName` |
| 自我介绍 | `intro` | `intro` |
| 联系方式 | **无来源** | 依 **D4** |

- 预填时机：`onMounted` 中草稿快照为空时才拉取；快照非空则优先快照，避免覆盖用户在本卡内的修改（`00-206 §6` 规则④）。
- 缺失字段提示：`00-206 §3.4` 要求的「去个人资料完善」入口当前完全缺失，须新增。
- 同步回写：`updateMyActorProfile` 已存在（`api/actor.ts:31`），需注意其入参 `ActorProfileMineUpdate` 带 `expectedProfileVersion`（乐观锁），回写前须先读当前版本。**实施时发现本条判断不足：`saveMine` 是全量替换且多字段 `@NotNull`，仅带本页字段回写会清空个人资料。修正后的方案见 §7.1 T3。**
- 开关持久化：需新增落库字段（`ActorCardStepSaveReqDTO` 现无对应字段），或明确判定开关为「单次生效、不持久化」并在 UI 上体现该语义。

### 4.4 死控件收口（§3.4）

逐项处置表（「处置」列待 **D5** 裁决后填定）：

| 偏离 | 位置 | 现状 | 处置 |
|------|------|------|------|
| A2 | `step-works:135` | `saveStep({ currentStep: 3 })`，作品/剧照/新增作品全丢 | 实现（P0 链路必需，依 D1） |
| A3 | `step-works:116` | `manageStills = (work) => addStill(work)`，满 3 张时 `count:0` 点击无反应 | 待裁决 |
| A4 | `step-settings:25-26,53-60` | `order` 单向写入，前端不回读、后端不解析 | 待裁决 |
| A5 | `step-photos:26,65` | 「调整顺序」「长按拖拽」无任何实现 | 待裁决 |
| A6 | `step-photos:58` | 「素材库即将开放」占位，而 `getActorAssets` 已可用 | 待裁决 |
| A7 | `step-attachment:42-45` | 「文件选择即将接入」占位，致该页所有控件不可达 | 待裁决 |
| A8 | `generate:109-113` | 「保存草稿」零请求 | 待裁决（低危：各步已逐步保存） |
| A9 | `step-visual:16,26` | `style` 落库但后端不消费；`backgroundImageUrl` 后端零读取点 | 与 §3.9 生成引擎占位联动 |
| A1 | `step-profile:36` | 同步开关空转 | 实现（见 4.3） |

### 4.5 消除空承诺文案（§3.5）

原则：文案与实现同步收敛。凡处置为「移除能力」的，文案一并删除；凡处置为「实现」的，文案保留。

`step-works` 硬编码示例作品（`:89-93` 三条：夏日未央 / 逆光而行 / 城市边缘）须换真实来源：
- 后端 `/api/actor/works` 已存在（`ActorWorkController.java:22`）
- 前端缺 `src/api/actor-work.ts`，须新建
- 剧照来源 `GET /api/actor/works/{id}/assets` 后端已有，前端未接

### 4.6 上传通道接入（§3.6）

4 处临时路径落库点：`step-visual:116`（首图）、`step-photos:61`（生活照）、`step-video:43`（视频）、`step-works:109-110`（剧照）。

- 统一走 `uploadActorAsset`（`api/actor-asset.ts:28`，已被 `pkg-profile/assets` 使用，含 `mediaType` / `categoryCode`）。
- 首图链路须实测：临时路径当前被原样提交给 `submitExpandImage` 并透传给 AI provider（`ActorCardExpandImageService.java:69,108`），provider 需可公网访问地址。实测方式：跑一次 `POST /api/actor-card/draft/{id}/expand-image`，查 `actor_ai_profile_card_task.failure_reason`。
- 是否需要 `assetId` 关联：`ActorCardStepSaveReqDTO` 现只有 URL 字符串。若需按 `00-206 §6` 规则⑥「删除演员卡不删除原始素材」做资产追溯，须评估加 `assetId` 类字段。
- 上传约束沿用 `SHARED_CONVENTIONS.md`：图片 ≤ 10MB、视频 ≤ 100MB。

### 4.7 消除静默失败（§3.7）

| 偏离 | 位置 | 改法方向 |
|------|------|---------|
| D1 | `store:66` `flushSave` 空 catch | 失败须 reject，使各页 `await saveStep` 后的 `navigateTo` 不再无条件执行 |
| D2 | `store:49` `reload` 空 catch | 失败须可被调用方感知，并阻止后续步骤以空值覆盖 |
| D3 | `store:55,61,72` `if (!cardId) return` | 不得静默 no-op 后仍带 `cardId=null` 跳转（下一页 `Number('null')`=`NaN` → `GET /draft/NaN`） |
| D4 | `store:98-100` `JSON.parse` 无保护 | computed 内解析须加保护，避免打挂整个 Hub 页 |
| D5 | `generate:56,70,93` 三处早退 | 不得永久停留 `loading`；须有超时、提示、重试入口 |
| D6 | `step-visual:125` 早退无提示 | 补反馈 |
| D7 | `step-visual:103` 背景库失败降级空列表 | 区分「该风格无背景图」与「加载失败」，后者给重试 |
| D8 | `step-visual:95`、`generate:84` 定时器无清理 | 页面卸载须清理轮询 |
| D9 | `step-profile:67`、`step-photos:76`、`step-settings:86` 快照解析静默 | 提示数据异常，不得静默空表单后覆盖原快照 |

注意 D1+D2 与 E6 构成组合缺陷：`reload` 静默失败使本地 ref 为空后，步骤 4/5/6 的「下一步」会因 `photosJson`/`videoUrl`/`attachmentUrl` 走 `!= null` 判定而**真实清零**已存内容。修 D2 是该组合的关键。

### 4.8 往返与守卫口径（§3.8）

`ActorCardDraftServiceImpl.saveStep` 现有两套口径：

| 口径 | 字段 | 后果 |
|------|------|------|
| `StringUtils.hasText`（`:38-43,47`） | `title`、`style`、`backgroundImageUrl`、`sourceImageUrl`、`expandedImageUrl`、`profileSnapshotJson`、`settingsJson` | 空值被跳过 ⇒ 无法清空 |
| `!= null`（`:44-46`） | `photosJson`、`videoUrl`、`attachmentUrl` | 空值落库 ⇒ 可清空，但配合 D2 会静默覆盖 |

统一方向须同时满足「清空语义可达」与「读取失败时不误清」，两者不可只顾一头——这正是当前两套口径各自踩中一边的原因。

`expandedImageUrl` 污染（E5，`step-visual:162`）：`expandedImageUrl.value || sourceImageUrl.value` 使未扩图也落值，连带步骤 1 恒 `done`、重进渲染出两张相同图、扩图入口消失。须让未扩图时该字段保持空。

### 4.9 后端契约缺口（§3.9）

| 偏离 | 内容 |
|------|------|
| F1 | 作品无落库通道（依 **D1**） |
| F2 | 联系方式无列无源无消费方（依 **D4**） |
| F3 | 状态枚举不一致（依 **D3**） |
| F4 | `title` 有 DTO 有落库，UI 无采集入口 ⇒ 恒 `null`，名片夹标题为空。可由 `publicName` + `style` 自动生成，或补采集入口 |
| F5 | `stepStatuses` / `step_status_json` 死字段（依 **D2**） |
| F6 | 前后端 DTO 字段差异（`stepStatuses`、`createTime`；`lastUpdate` 对 `LocalDateTime` 的序列化形态未验证）——宽松兼容，无实际故障，登记备查 |
| F7 | 上传通道存在但向导不接（见 4.6） |
| C3 | 完整度两套口径互相矛盾：`Impl:105-113` 累计 3 项除以 7（满填 43%）；`PublishService:118-127` 另一套且作品项无条件 `done++`。注释 `settlingsJson` 为拼写错误且所述「视为完成」未实现 |
| C2 | `runGenerate:88-90` TODO 占位，预览图 = 主视觉原图，资料/作品/照片/视频/附件/设置全不体现，而等待文案承诺「组合长页面」。本轮若不实现真实渲染，须登记为已知占位并同步文案 |

## 5. 偏离全量清单（附录）

审计口径：读全 9 页 + store + 5 个 api 模块 + 组件 + controller + 3 个 service + 8 个 DTO + 2 个实体 + 迁移 SQL。结论均来自静态代码阅读，未做运行验证。`CONFIRMED` = 代码证据明确；`PLAUSIBLE` = 依赖未验证的运行态或库数据。

### A · 死控件（9）

| # | 位置 | 证据 | 用户后果 | 置信 |
|---|------|------|---------|------|
| A1 | `step-profile:36`（`:55` 定义） | `syncToProfile` 全文件仅 2 处出现；`handleNext:58-61` 只提交 `profileSnapshotJson`；未 import `updateMyActorProfile` | 开启同步 → 期望写回个人资料 → 实际个人资料零变更，开关本身也不落库 | CONFIRMED |
| A2 | `step-works:135` | `saveStep({ currentStep: 3 })`；`works:89`、`selected:103`、`stills:108,114`、`newWork:99,118` 均不进 payload；注释自陈「通过 settingsJson 临时承接」而连 `settingsJson` 都没传 | 勾选 3 部作品 + 9 张剧照 + 新增 1 部 → 期望存入 → 实际只改 `current_step`，全部随页面卸载消失 | CONFIRMED |
| A3 | `step-works:116` | `manageStills = (work) => addStill(work)` | 点「管理剧照」→ 期望排序/替换/删除 → 实际直接弹相册追加；满 3 张时 `count: 3 - 3 = 0`，点击无反应无提示 | CONFIRMED（`count:0` 是否抛错未实测） |
| A4 | `step-settings:25-26,53-60` | `order` 进 `settingsJson:67`；`onMounted:74-88` 只回填 3 个 `enabled`，从不读 `order`；后端无解析 `order` 代码 | 把视频调到第 1 位 → 期望生成按此顺序且重进保持 → 实际重进复位，生成结果与顺序无关 | CONFIRMED |
| A5 | `step-photos:26,65` | `showOrderHint` 仅 toast；全文件 `longpress|longtap|touchstart|movable` = 0 命中 | 点「调整顺序」或长按 → 期望拖拽改序 → 实际只有 toast，顺序恒等于选择顺序 | CONFIRMED |
| A6 | `step-photos:58` | `fromAssets` = toast「素材库即将开放」；`getActorAssets`（`api/actor-asset.ts:8`）已被 `pkg-profile/assets` 使用 | 点「从素材库选择」→ 期望复用已上传素材 → 实际只能重新从相册选 | CONFIRMED |
| A7 | `step-attachment:42-45` | `pickFile` = toast「文件选择即将接入」；`attachmentUrl` 只可能来自 `onMounted:58` 回填 | 点添加附件 → 期望选 PDF/PPT → 实际无法选中任何文件；`:20` 删除、`:14-21` 文件卡、`:51` 传值分支在新建流程永远不可达，步骤 6 恒「未添加」 | CONFIRMED |
| A8 | `generate:109-113` | `saveDraft` 只 `reset()` + toast，零请求 | 点「保存草稿」→ 期望触发保存 → 实际纯装饰（各步已逐步保存，故低危；但 `title` 等可编辑项无处落库） | CONFIRMED |
| A9 | `step-visual:16,26` | `style`/`backgroundImageUrl` 落库（`Impl:39-40`）；`runGenerate:88-90` 只取 `expandedImageUrl ?: sourceImageUrl`；`backgroundImageUrl` 全 server 零读取点 | 切「古风」+ 选背景 → 期望生成套用 → 实际预览就是首图本身，风格与背景零影响 | CONFIRMED |

### B · 空承诺（8）

| # | 位置 | 证据 | 用户后果 | 置信 |
|---|------|------|---------|------|
| B1 | `step-profile:8` | `onMounted:64-68` 只读 `profileSnapshotJson`；新草稿该字段为 `null`（`createDraft:24-32` 只设 status/currentStep/publishedVersion）；未 import 任何 profile api | 已填好个人资料 → 期望「自动填入」→ 实际 6 框全空 | CONFIRMED |
| B2 | `step-works:9` + `:89-93` | 列表是 3 条硬编码示例；`/api/actor/works` 后端已存在（`ActorWorkController:22`），前端无 `api/actor-work.ts` | 切「从演艺经历选择」→ 期望看到自己的作品 → 实际看到与本人无关的示例，勾选等于把别人的作品放进自己演员卡 | CONFIRMED |
| B3 | `step-visual:9` | `pickHeroImage:113-121` 只设 `sourceImageUrl` 并复位 `expandStatus`，扩图需另点 `:62` 按钮；`:143` 判 `done` vs 后端 `success` | 选完首图 → 期望自动扩图出结果 → 实际需手点，然后 30×2s≈60s 后「扩图失败」，即使后端已成功产图 | CONFIRMED |
| B4 | `create:17` | 三重阻断：C1 + F1 + F3 | 完成 7 步 → 期望生成主页 → 实际按钮永远「继续下一项」在步骤 3 打转；走名片夹入口则报「至少需要 1 部作品」或 120s 后「生成超时」 | CONFIRMED |
| B5 | `step-photos:39` | 同 A5 | 同 A5 | CONFIRMED |
| B6 | `step-attachment:8,12` | 同 A7 | 按文案准备好 PDF → 期望能选 → 实际无法选中 | CONFIRMED |
| B7 | `step-video:43,50` | `videoUrl.value = res.tempFilePath`；`pkg-actor-card` 全目录 `uploadActorAsset|uploadFile` = 0 命中 | 选视频看到「已选择」→ 期望进入演员卡 → 实际库里存了仅本机本次会话有效的 `wxfile://tmp_*`，换设备不可播，服务端取不到文件 | CONFIRMED |
| B8 | `step-photos:58`、`step-attachment:44`、`step-photos:65` | 三条「即将开放/即将接入/长按可拖拽」 | 自认未完成的承诺留在界面上 | CONFIRMED |

### C · 占位数据（5）

| # | 位置 | 证据 | 用户后果 | 置信 |
|---|------|------|---------|------|
| C1 | `store:92-95` | `statusCode: 'empty'` 硬编码 + 注释「由子页面动态更新」；`stepStatuses` 是 computed，全仓无 setter | 做完 7 步 → 期望 7/7 且按钮变「生成演员卡」→ 实际封顶 6/7、步骤 3 恒「未添加」、按钮恒「继续下一项」、点击恒回步骤 3 | CONFIRMED |
| C2 | `ActorCardGenerateService:88-90` | `// TODO: 接入真实长页渲染引擎`，`previewUrl = expandedImageUrl ?: sourceImageUrl` | 等「组合长页面」→ 期望含资料/作品/照片的长页 → 实际就是自己那张首图 | CONFIRMED |
| C3 | `ActorCardDraftServiceImpl:105-113`、`ActorCardPublishService:118-127` | 前者累计 3 项除以 7（满填 43%），注释 `settlingsJson` 拼写错误且所述「视为完成」未实现；后者另一套口径且 `:122` 作品项无条件 `done++` | 填完 7 步 → 期望 100% → 实际详情 43%、列表另一偏高值，两处互相矛盾 | CONFIRMED |
| C4 | `step-visual:116`、`step-photos:61`、`step-video:43`、`step-works:109-110` | 4 处 `tempFilePath(s)` 直接落库；首图还被 `:128` 提交给 `submitExpandImage`，后端原样交 provider（`:69,108`） | 上传首图并扩图 → 期望 AI 读到图 → 实际 provider 拿到 `wxfile://tmp_*` 无法取图 | PLAUSIBLE（前端存临时路径、后端原样透传已确认；provider 失败形态需实跑一次 expand-image 查 `failure_reason`） |
| C5 | `ActorCardPublishService:72-73` | `materialCount(0)` / `viewCount(0)` 占位 | 已上传素材 → 期望个人中心显示数量 → 实际恒 0（该接口不被这 9 页调用） | CONFIRMED |

### D · 静默失败（9）

| # | 位置 | 证据 | 用户后果 | 置信 |
|---|------|------|---------|------|
| D1 | `store:66` | `catch { /* 静默 */ }` 后 resolve；各页 `await saveStep` 后无条件 `navigateTo`（`step-profile:59-60`、`step-photos:68-69`、`step-video:50-51`、`step-attachment:51-52`、`step-visual:158-164`、`step-settings:69-70`） | 弱网点「下一步」→ 期望失败留原页 → 实际闪一条通用 toast 后照常前进，本页输入永久丢失；回退看到空表单，无从判断没存上还是被清空 | CONFIRMED |
| D2 | `store:49` | `reload` 空 catch，`card` 保持 null | 从名片夹「继续编辑」→ 期望回填 → 实际全空白形同新建；此后步骤 4/5/6 会用空值真实覆盖已存内容 | CONFIRMED |
| D3 | `store:55,61,72` | `if (!cardId.value) return`；各页 `` ?cardId=${draftStore.cardId} `` | 草稿创建失败后点「下一步」→ 期望保存 → 实际零请求零提示，进入下一页并触发 `GET /draft/NaN` | CONFIRMED（后端对 NaN 返回码未实测） |
| D4 | `store:98-100` | computed 内 `JSON.parse(c.photosJson)` 无 try | `photos_json` 非法时 → 期望看到步骤列表 → 实际 `doneCount`/`btnText`/`v-for` 同时失效，Hub 页 7 个入口全消失 | PLAUSIBLE（代码路径确定；触发需库中确有非法值。正常写入路径不会触发） |
| D5 | `generate:56,70,93` | 三处 `if (!id) return`；`status` 初值 `'loading'`，早退不改状态 | `loadDraft` 静默失败后 → 期望看到错误或重试 → 实际永久转圈「AI 生成中，请稍候…」，无超时无提示无重试；点「发布」同样静默无反应 | CONFIRMED |
| D6 | `step-visual:125` | `if (!cardId || !sourceImageUrl.value) return` | 点「开始 AI 扩图」→ 期望开始 → 实际（`cardId` 缺失时）毫无变化 | CONFIRMED |
| D7 | `step-visual:103` | `catch { bgImages.value = []; }` | 切风格时接口失败 → 期望知道可重试 → 实际背景区空白无重试，误以为该风格未配图 | CONFIRMED |
| D8 | `step-visual:95`、`generate:84` | `pollTimer` 有声明无 `onUnmounted`/`clearTimeout`；`generate` 的 `setTimeout` 不留句柄 | 轮询期间返回上一页 → 期望停止 → 实际继续请求至 attempts 耗尽，对已销毁页面 ref 赋值 | CONFIRMED |
| D9 | `step-profile:67`、`step-photos:76`、`step-settings:86` | `catch { /* ignore */ }` | 快照损坏时重进 → 期望提示 → 实际静默空表单，「下一步」以空值覆盖原快照 | CONFIRMED |

### E · 往返断裂（7）

| # | 位置 | 证据 | 用户后果 | 置信 |
|---|------|------|---------|------|
| E1 | `ActorCardDraftServiceImpl:38-43,47` | 7 字段用 `hasText`，3 字段用 `!= null`，同一方法两种口径 | 选了背景想改「不用背景」→ 期望清空 → 实际传 `''` 被跳过，旧背景永久留存，UI 也无取消选中交互 | CONFIRMED |
| E2 | `step-profile:55,59` + DTO | 无落库字段 | 开启开关后重进 → 期望保持 → 实际恒 false | CONFIRMED |
| E3 | `step-works:135`、`onMounted:141-143` | 只传 `currentStep`，不做任何回填 | 勾选作品+9 张剧照+新增 1 部，下一步后返回 → 期望都在 → 实际回到 3 条硬编码示例、全未勾选、剧照全空、「已选择 0 部作品」 | CONFIRMED |
| E4 | `step-settings:67` vs `:74-88` | `order` 写入不回读 | 调整顺序后重进 → 期望保持 → 实际复位 | CONFIRMED |
| E5 | `step-visual:162` | `expandedImageUrl: expandedImageUrl.value \|\| sourceImageUrl.value`；连带 `store:83` 恒 done、`:174` 置 `expandStatus='done'`、`:48` 渲染对比区 | 没扩图就下一步再回步骤 1 → 期望看到「开始 AI 扩图」→ 实际看到两张一模一样的「原图/扩图」，扩图入口消失，系统认为已完成 | CONFIRMED |
| E6 | `Impl:44-46` + D2 | `!= null` 允许空值落库（清空语义正确），但本地 ref 因 D2 为空时会真实清零 | 重进已有草稿（读取恰好失败）并点过步骤 4/5/6 → 期望原内容不变 → 实际 12 张生活照、视频、附件被空值覆盖 | CONFIRMED（组合缺陷，需 `getDraft` 实际失败才触发） |
| E7 | `step-visual:176-179` | `find(b => b.imageUrl === c.backgroundImageUrl)`，`loadBgLibrary` 只加载当前风格，`found` 为 undefined 时无兜底 | 以古风选好背景后改 style 再回来 → 期望看到已选或提示失效 → 实际无选中态无提示，而 DB 里旧背景仍在且无法清除（E1） | CONFIRMED |

### F · 契约缺口（7）

| # | 内容 | 证据 | 用户后果 | 置信 |
|---|------|------|---------|------|
| F1 | 作品零写入路径且被设为生成硬门禁 | UI 采集 `title/type/role/stills`（`step-works:54,58,64,109`）；DTO 无 works 字段；controller 无作品端点；`ActorCardWork` 全 server 5 处引用中仅 1 次 `selectCount`；`GenerateService:115-117` `workCount == 0` 即抛 | 填完作品点「生成」→ 期望开始 → 实际必然报「步骤3（参演作品）至少需要 1 部作品」，且无论怎么操作都无法让计数非 0 | CONFIRMED |
| F2 | 联系方式无列无源无消费方 | `step-profile:28` 仅混入 `profileSnapshotJson`；`actor_card` 表无该列（迁移 `V20260731_001` 已核）；`ActorProfileResp:30-50` 无 phone/contact/wechat 任一字段；legacy `ActorProfile.contactPhone`（`types/actor.ts:44`）存在但本页未引用；`step-settings:48` 的显隐开关所控正是这份数据 | 填微信号 → 期望被结构化保存可用于联系流程 → 实际沉在 JSON 里，后端无列可查无逻辑可用，显隐开关也无消费方 | CONFIRMED |
| F3 | 状态枚举前后端不一致，DTO 注释与实现自相矛盾 | 后端 `STATUS_SUCCESS="success"`（`ExpandImage:40`、`Generate:34`），`status()` 原样回传；DTO 注释写 `pending\|running\|done\|failed`；前端只认 `done`（`step-visual:143`、`generate:77`、`api:88,96`），无归一化 | 等扩图/生成 → 期望成功 → 实际 60s 后「扩图失败」、120s 后「生成超时」，而任务表是 success、图已产出 | CONFIRMED |
| F4 | `title` UI 无采集入口 | DTO 有（`:37`）、落库有（`Impl:38`）、9 页无采集或自动生成 | 所有演员卡 `title` 恒 null，名片夹列表标题为空 | CONFIRMED |
| F5 | `stepStatuses` / `step_status_json` 死字段 | 列存在、实体有 `stepStatusJson`（`ActorCard:35`），全 server 仅此一处，从不读写；`ActorCardRespDTO.stepStatuses:32` 注释「Hub 页用」但 `toDto:81-103` 从未 set，恒 null；前端 `ActorCardDTO:48-67` 也无该字段 | 后端声明「Hub 页用」→ 实际 Hub 拿不到也不用 → 步骤 3 只能硬编码，构成 C1 的根因 | CONFIRMED |
| F6 | 前后端 DTO 字段不对齐 | 后端有前端无：`stepStatuses`、`createTime`；前端 `lastUpdate: string` 对后端 `LocalDateTime`；`createActorCardDraft` 前端声明返回 `{id,status}`、后端返回完整 DTO | 宽松兼容，无实际故障 | CONFIRMED（`lastUpdate` 序列化形态需看全局 ObjectMapper，未验证） |
| F7 | 上传通道存在但向导不接 | `uploadActorAsset`（`api/actor-asset.ts:28`）已被 `pkg-profile/assets` 使用，9 页无一引用；DTO 只有 URL 字符串无 `assetId` 类字段 | 见 C4/B7 | CONFIRMED |

## 6. 门禁设计

新增 `scripts/verify-actor-card-wizard-alignment.mjs`，接入 `package.json` 为 `verify:wizard-alignment`。

断言分组（对应 `requirements §3.10`）：

| 组 | 断言 |
|----|------|
| `[1]` 可完成性 | 步骤 3 状态非硬编码常量；`requiredAllDone` 可达 `true` 的结构前提存在；`actor_card_work` 有写入路径（后端侧以 grep insert/save 断言） |
| `[2]` 枚举一致 | 前端类型声明的成功态字面量 == 后端 `STATUS_SUCCESS` 值；DTO 注释与实现一致 |
| `[3]` 无占位 | 模板中不存在「即将开放」「即将接入」类文案；`step-works` 无硬编码示例作品名 |
| `[4]` 无静默 | `store` 内无 `catch {}` / `catch { /* 静默 */ }`；computed 内 JSON 解析有保护 |
| `[5]` 无临时路径 | 向导内不存在 `tempFilePath` 直接进入 `saveStep` payload 的路径 |
| `[6]` 守卫一致 | `saveStep` 内同类字段守卫口径统一 |
| `[7]` 文案实现一致 | 各条「承诺型」文案存在对应实现符号 |

形态要求（沿用既有教训）：
- 收集全部失败项后再非零退出，不得首错即停（`00-211`）
- 必须接入 `package.json`，未接入不计门禁（`00-205`）
- 必须以反向注入证明非空转：临时改坏一条被断言的事实，确认脚本确实失败

**门禁能力边界**：存在性 grep 对「视觉」与「运行时行为」结构性无效。本 Spec 的 §3.1 端到端走通、§3.2 枚举实际对齐、§3.6 provider 取图三项**必须实测**，门禁只能守住结构不回退，不能替代运行验证。这一点在 `00-212` 已有先例（grep 对 `data-v` 哈希分叉与垂直居中缺陷均盲）。

## 7. 验证策略

| 层 | 手段 |
|----|------|
| 类型 | `npx vue-tsc --noEmit` 必须 0 |
| 结构门禁 | `npm run verify:wizard-alignment`（新建）+ `npm run verify:nav-title`（`00-212`，不得回归） |
| 构建 | `npm run build:mp-weixin`，postbuild 双侧 scoped hash 一致 |
| 产物 | 关键字进入 `dist/build` 与 `dist/dev`。**注意本项目 wxss 为换行美化格式，单行 grep 匹配不到，须用多行 dump**（`00-212` 已踩） |
| 包体 | 主包 apparent bytes 对 2048 KB 预算；MAIN = TOTAL − 四个分包根（`pkg-actor-card`/`pkg-card`/`pkg-tools`/`pkg-profile`）。当前基线 424.29 KB |
| 后端 | 编译 + 涉及表的迁移核对 |
| 运行 | §3.1 端到端走通、§3.2 枚举对齐、§3.6 provider 取图必须实测留证 |

## 7.1 实施记录

### T1 打通向导可完成性（已完成，端到端实测待补）

后端：
- 新增 `PUT/GET /actor-card/draft/{cardId}/works`，`replaceWorks` 整体替换写入 `actor_card_work`（`ActorCardDraftServiceImpl`）。`actor_card_work` 迁移已存在于 `V20260731_001__actor_card_tables.sql:39`，无需新增。
- `BaseEntity` 带 `@TableLogic`，故 `replaceWorks` 的 delete 为逻辑删除：旧行留库但被 `selectCount`/`selectList` 自动过滤，重复提交不会虚高作品数，代价是反复编辑累积历史行（可接受）。
- `deriveStepStatuses(card)` 成为步骤状态唯一真源；`toDto` 填 `stepStatuses`，`calcCompletion` 改为消费同一份结果 —— C3「两套完整度口径」的根因由此消除。
- `actor_card.step_status_json` 按 D2 保持不读不写，仍为 §4.9 待清理项。

前端：
- `stores/actor-card-draft.ts` 删除步骤 3 硬编码 `'empty'` 与「由子页面动态更新」注释，7 步状态改取后端派生值，前端仅保留 `label`/`required`。
- `api/actor-card.ts` 新增 `replaceActorCardWorks`/`listActorCardWorks` 与 `stepStatuses` 类型。
- `step-works`「下一步」真正落库且失败阻断跳转；`onMounted` 回填已存作品。占位作品 `sourceWorkId` 一律 null，真实来源留待 T5。

验证：后端 `mvn compile` 通过；前端 `vue-tsc` 0、`verify:nav-title` 95/0、构建 DONE 且双侧 hash 一致、主包 423.64 KB / 2048 KB。
**仍缺 T1 要求的端到端走通证据**（需后端运行）：Hub → 完成必填 1/2/3/7 → `generate` → 非空 `previewUrl`。注意该 `previewUrl` 目前仍是 C2 的占位实现（拿主视觉 URL 顶替），走通只证明门禁可满足，不代表长页渲染已实现。

### T2 统一异步任务状态枚举（已完成）

按 D3 落在后端 DTO 边界：
- 新增 `ActorCardTaskStatus.toApi()`，持久层 `success` → 契约 `done`，其余三态同名原样透出。持久层与 `AiProfileCardServiceImpl` 的 `success` 查询条件均不受影响，无数据迁移。
- 两处 `status()` 出口接入归一化（`ActorCardExpandImageService:93`、`ActorCardGenerateService:77`）。两个 RespDTO 的 `pending | running | done | failed` 注释无需修改 —— 它本就描述 API 契约，此前是实现没兑现它。
- 前端零改动即可正确判定（`generate/index.vue`、`step-visual/index.vue` 本就判 `'done'`）。

轮询耗尽文案已与真失败区分（两处）：`generate` 改为「等待超时，生成任务可能仍在进行，可稍后回到名片夹查看结果」；`step-visual` 新增 `expandFailureReason`，区分提交失败／任务失败／轮询超时／网络异常，此前四种情况都只显示「扩图失败」。

范围核实：`AiProfileCardServiceImpl` 另有 3 处 `setStatus(task.getStatus())` 原样透出，但其 DTO 未声明任何状态枚举、且前端无任何消费方（已 grep 确认），不构成契约不一致，不在本 Spec 范围内。

前后端枚举一致性的门禁断言留待 T10。

### T3 步骤 2 预填与同步回写（已完成）

处置 A1（同步开关空转）、B1（「自动填入」无预填）、E2（开关不持久化）、F2（联系方式无源），并补 `00-206 §3.4` 缺失的「去个人资料完善」入口。

**实施中发现的关键约束（推翻了 §4.3 对同步回写的原判断）**：
`ActorProfileWriteServiceImpl.saveMine` 是**全量替换** —— `applyCore`/`applyCareer` 无条件覆盖每个字段。且 `ActorProfileCoreUpdateDTO` 对 `publicName`/`gender`/`age`/`height`/`currentCity` 是 `@NotBlank`/`@NotNull`，`ActorProfileMineUpdateDTO.avatarAssetId` 亦为 `@NotNull`。

由此两条结论：
1. **写回必须先读后合并**。若按 §4.3 原文直接用本页 6 个字段构造 payload，会清空 `gender`/`age`/`weight`/`originPlace`/`majorName`、四个标签数组与 `avatarAssetId` —— 即「同步」会静默毁掉用户的个人资料。实现为 `onMounted` 读 `getMyCareerProfile` 存入 `loadedProfile`，写回时合并。
2. **本向导不采集 `gender`/`age`/`avatarAssetId`，因此资料不全时写回必然被后端拒**。故新增 `missingForSync` 判定：缺失时不发请求，弹窗说明缺哪几项并提供「去完善」，而不是发一个注定 400 的请求或静默跳过。

其余实现：
- 预填顺序：快照非空则优先快照（不覆盖用户在本卡内的修改），快照为空才用资料预填五字段。无论哪条路径都要读资料，因为写回需要 `profileVersion` 与本页不采集的字段。
- 联系方式按 D4 保留字段，预填源用 `userStore.userInfo.phone`（个人资料无任何联系字段，已核 `ActorProfileResp`）。
- 开关按 E2 明确为**单次生效、不落库**，并在 UI 上以副文案体现该语义（「仅本次生效」/「还需补齐…才能同步」）。它是一次写回动作的意图，不是这张卡的属性；落库要新增列且会混淆语义。
- 「下一步」补姓名必填校验；保存失败与同步失败均阻断跳转且不静默，同步失败时明确告知「本步骤已保存」。
- 「去个人资料完善」入口指向 `/pages/actor-profile/edit`（已核该页覆盖 `gender`/`age`/`avatar`）。箭头沿用 00-212 的边框旋转手法，不用 `›` 字形。

未在本任务解决（保持登记）：`step-profile` 快照解析仍未提示用户（D9），归 T7；快照损坏时现已退化为资料预填而非留空表单，属改善但非完整修复。

验证：`vue-tsc` 0、`verify:nav-title` 95/0、`audit:steering` 通过、构建 DONE 双侧 hash 一致、产物双侧关键字与 wxss 均已核对、主包 423.64 KB / 2048 KB。同步回写链路须后端运行才能实测，尚未取得运行证据。

## 8. 实施顺序约束

1. 先裁决 §3 待裁决项（D1~D5），未裁决不进入实现——D1/D2 联动决定后端结构，D3 决定改动落在哪侧，翻转会返工。
2. §3.1 为 P0 且必须先落地：其余条款在向导走不通的前提下无法端到端验证。
3. §3.2 紧随其后：不解决则扩图与生成两条核心链路始终表现为失败。
4. 其余条款按 `requirements` 编号推进，一次一个任务，做完停下等审核。

_Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9, 3.10_
