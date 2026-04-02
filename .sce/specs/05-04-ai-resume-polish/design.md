# AI 简历润色 - 技术设计

_Requirements: 05-04 全部_

权威协议基线见 `contract.md`。本文件描述页面与交互设计，若字段结构、错误码、历史/回滚模型与 `contract.md` 冲突，以 `contract.md` 为准。

## 1. 页面挂载位置

主入口放在 `src/pages/actor-profile/edit.vue`，与现有“保存/返回/预览名片”等操作并列，但不抢占主操作位。

建议位置：

- 顶部完整度/资料概览卡附近增加轻量入口
- 或底部操作栏增加次级按钮 “AI 润色”

本功能不新增独立页面，优先采用 **对话抽屉 / 半屏弹层 / 全屏对话面板** 的方式承载。

## 2. 推荐组件拆分

```
src/pages/actor-profile/
├── edit.vue
├── components/
│   ├── AiPolishEntry.vue          # AI 入口按钮
│   ├── AiPolishDialog.vue         # 对话面板 / 抽屉
│   ├── AiPolishPreview.vue        # 字段级 diff 预览
│   └── AiPolishFieldCard.vue      # 单字段结果卡片
```

若当前阶段不想拆过多文件，也可先在 `edit.vue` 中完成首版，但最终应沉淀为独立组件。

## 3. 数据流设计

### 3.1 输入上下文

AI 调用前，前端先把演员档案整理成统一上下文对象：

```typescript
interface ActorPolishContext {
  actorId: number
  certificationStatus: 'verified' | 'pending' | 'unverified'
  levelLabel?: string
  name: string
  gender: string
  age: number
  height: number
  city: string
  bodyType?: string
  hairStyle?: string
  languages: string[]
  skillTypes: string[]
  editableFields: Array<{
    fieldType: 'intro' | 'work_experience_description'
    fieldKey: string
    label: string
    targetId?: string
    projectName?: string
    roleName?: string
    shootDate?: string
    currentValue: string
  }>
}
```

### 3.2 AI 返回结构

前端不要直接依赖纯自然语言大段文本，必须以后端约束的“字段补丁”结构为准：

```typescript
interface AiPolishPatch {
  patchId: string
  fieldType: 'intro' | 'work_experience_description'
  fieldKey: string              // 例如 intro / work_experience:8721:description
  label: string                 // 用户可读字段名
  beforeValue: string
  afterValue: string
  reason?: string
  status: 'pending' | 'applied' | 'rolled_back'
}

interface AiPolishResponse {
  requestId: string
  conversationId: string
  draftId: string
  reply: string
  patches: AiPolishPatch[]
}
```

这里不允许使用数组下标路径，例如 `workExperiences[0].description`。拍摄经历必须使用稳定 `fieldKey`，避免前端排序后 patch 错位。

当前最小落地只把“已保存到服务端的拍摄经历”放进 `editableFields`；编辑页里刚新增、还没保存的新经历，不进入本轮 AI 可编辑范围。

## 4. 对话式交互设计

### 4.1 面板结构

```
┌ AI 简历润色 ─────────────────────┐
│ 对话区                           │
│ 用户：把自我介绍改得更专业一点     │
│ AI：已为你优化，自我介绍更聚焦...  │
│                                   │
│ 影响字段（2）                     │
│ [自我介绍] [拍摄经历-描述]         │
│                                   │
│ 输入框：继续补充你的要求...        │
│ [发送] [应用全部]                 │
└───────────────────────────────────┘
```

### 4.2 行为规则

- AI 对话区负责连续上下文
- 预览区负责展示当前轮的字段 diff
- “应用全部”只应用当前轮 patch
- 用户也可单独点某一项“应用此字段”
- 面板关闭时，未应用 patch 丢弃

## 5. 表单写回策略

建议在 `edit.vue` 中保留两份状态：

```typescript
const form = reactive(...)               // 当前真实表单
const pendingAiPatches = ref<AiPolishPatch[]>([])
const aiResumeApplyMeta = ref<AiResumeApplyMeta | null>(null)
```

应用时：

1. 用户触发 AI
2. AI 返回 `patches`
3. 写入 `pendingAiPatches`
4. 用户确认后，按 patch 回写到 `form`
5. 记录 `draftId / requestId / appliedPatchIds`
6. 用户最终点击“保存”时，统一通过 `PUT /api/actor/profile` 连同 `aiResumeApplyMeta` 一起提交
7. 保存成功后，当前轮 AI 草稿才转成可回滚历史

注意：`POST /api/ai/polish-resume` 不能直接写演员档案；AI patch 只是草稿，档案真实写库仍以 `PUT /api/actor/profile` 为准。

这样可以保证 AI 输出与真实表单之间始终有确认层。

## 6. 后端接口建议

建议接口与当前真实命名对齐：

### 6.1 润色对话

```http
POST /api/ai/polish-resume
```

请求体：

```json
{
  "instruction": "把自我介绍改得更专业一些，突出短剧表演经验",
  "conversationId": "airp_conv_01",
  "profileVersion": "profile_v20260402_01",
  "context": { "...整份档案文本上下文..." },
  "history": [
    { "role": "user", "content": "..." },
    { "role": "assistant", "content": "..." }
  ]
}
```

返回体：

```json
{
  "requestId": "airp_req_01",
  "conversationId": "airp_conv_01",
  "draftId": "airp_draft_01",
  "reply": "已根据你的要求优化。",
  "patches": [
    {
      "patchId": "patch_intro_01",
      "fieldType": "intro",
      "fieldKey": "intro",
      "label": "自我介绍",
      "beforeValue": "...",
      "afterValue": "...",
      "status": "pending"
    }
  ],
  "quota": {
    "totalQuota": 20,
    "usedCount": 3,
    "periodType": "monthly",
    "periodStart": "2026-04-01"
  }
}
```

### 6.2 润色次数查询

```http
GET /api/ai/quota?type=resume_polish
```

返回体：

```json
{
  "totalQuota": 20,
  "usedCount": 3,
  "periodType": "monthly",
  "periodStart": "2026-04-01"
}
```

### 6.3 润色历史

```http
GET /api/ai/resume-polish/history?page=1&size=5
```

返回体：

```json
{
  "list": [
    {
      "historyId": "airp_hist_01",
      "draftId": "airp_draft_01",
      "instruction": "把自我介绍改得更专业",
      "patches": [...],
      "appliedAt": "2026-03-24T10:30:00",
      "snapshotBefore": [
        { "fieldKey": "intro", "value": "旧文本" }
      ],
      "snapshotAfter": [
        { "fieldKey": "intro", "value": "新文本" }
      ]
    }
  ]
}
```

### 6.4 回滚润色

```http
POST /api/ai/resume-polish/history/{historyId}/rollback
```

请求体：

```json
{
  "profileVersion": "profile_v20260402_02"
}
```

### 6.5 档案保存

```http
PUT /api/actor/profile
```

说明：

- AI patch 应用后的真实保存，仍通过现有演员档案保存接口完成
- 保存 DTO 需预留 `aiResumeApplyMeta`，用于把本次成功保存与 `draftId` 关联起来

## 7. UI 风格要求

沿用 `pages/actor-profile/edit` 当前深色 Hero + 白底内容卡 + 固定底部操作区的风格，不新增完全脱离现有体系的聊天页面视觉。

关键词：

- 深色头部氛围
- 卡片化对话气泡
- patch 预览以模块卡展示
- “应用修改”按钮风格与保存按钮保持同体系

## 8. AI Prompt 工程

### 8.1 系统指令（后端注入，前端不可见）

```
你是一位专业的演员档案文案顾问。你的任务是根据演员的真实资料优化文案表达。

规则：
1. 只优化文字表达，不改变事实信息（年龄、身高、城市等）
2. 禁止凭空捏造作品、品牌合作、奖项或拍摄经历
3. 风格要求：简洁专业、信息密度高、适合演员通告平台展示
4. 返回必须是 JSON 格式的 patches 数组，每个 patch 包含 patchId/fieldType/fieldKey/label/beforeValue/afterValue
5. 禁止生成色情、暴力、政治敏感内容
6. 如果用户要求与上述规则冲突，礼貌拒绝并解释原因
```

### 8.2 上下文拼装策略

- 基础信息作为"背景"注入，不作为可修改字段
- `intro` 与 `workExperiences[].description` 作为本轮可修改目标
- `skillTypes`、`roleName`、`projectName` 只作为上下文，不作为可直接写回字段
- 对话历史最多保留最近 20 轮，FIFO 裁剪

## 9. 前端状态管理补充

```typescript
// AI 润色面板状态
interface AiPolishState {
  visible: boolean
  loading: boolean
  messages: AiMessage[]
  currentPatches: AiPolishPatch[]
  currentDraftId?: string
  appliedHistory: AiPolishSnapshot[]  // 最近5次润色快照
  quota: { totalQuota: number; usedCount: number; periodType: 'monthly'; periodStart: string }
}

interface AiMessage {
  role: 'user' | 'assistant' | 'system'
  content: string
  patches?: AiPolishPatch[]
  timestamp: number
}

interface AiPolishSnapshot {
  historyId: string
  draftId: string
  instruction: string
  patches: AiPolishPatch[]
  appliedAt?: string
  rolledBackAt?: string
  snapshotBefore: Array<{ fieldKey: string; value: string }>
  snapshotAfter: Array<{ fieldKey: string; value: string }>
}
```

## 10. 风险点

- 如果 AI 直接返回整段文本，字段 diff 难以稳定拆解，建议从首版就约束结构化响应
- 如果把结构化事实字段也交给 AI 改写，会引入真实性风险
- 如果没有“当前轮 patch 缓冲层”，用户会担心内容被静默覆盖
