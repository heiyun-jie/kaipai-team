# AI 简历润色 - 技术设计

_Requirements: 05-04 全部_

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
  basic: {
    name: string
    gender: string
    age: string
    height: string
    city: string
  }
  intro: string
  skills: string[]
  appearance: {
    bodyType?: string
    hairStyle?: string
    languages: string[]
  }
  workExperiences: Array<{
    projectName: string
    roleName?: string
    description?: string
  }>
  targetTone?: string
}
```

### 3.2 AI 返回结构

前端不要直接依赖纯自然语言大段文本，建议后端或前端约束 AI 返回为“字段补丁”结构：

```typescript
interface AiPolishPatch {
  field: string                 // 例如 intro / workExperiences[0].description
  label: string                 // 用户可读字段名
  before: string
  after: string
  reason?: string
}

interface AiPolishResponse {
  reply: string                 // 对话回复
  patches: AiPolishPatch[]
}
```

这样可以直接支持字段级预览、字段级确认和整批应用。

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
```

应用时：

1. 用户触发 AI
2. AI 返回 `patches`
3. 写入 `pendingAiPatches`
4. 用户确认后，按 patch 回写到 `form`
5. 清空当前轮 `pendingAiPatches`

这样可以保证 AI 输出与真实表单之间始终有确认层。

## 6. 后端接口建议

建议新增接口：

### 6.1 润色对话

```http
POST /api/actor/profile/polish
```

请求体：

```json
{
  "instruction": "把自我介绍改得更专业一些，突出短剧表演经验",
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
  "reply": "已根据你的要求优化。",
  "patches": [
    {
      "field": "intro",
      "label": "自我介绍",
      "before": "...",
      "after": "..."
    }
  ]
}
```

### 6.2 润色次数查询

```http
GET /api/actor/profile/polish/quota
```

返回体：

```json
{
  "dailyLimit": 10,
  "usedToday": 3,
  "remaining": 7
}
```

### 6.3 润色历史

```http
GET /api/actor/profile/polish/history?page=1&size=5
```

返回体：

```json
{
  "list": [
    {
      "id": 1,
      "instruction": "把自我介绍改得更专业",
      "patches": [...],
      "appliedAt": "2026-03-24T10:30:00",
      "snapshotBefore": { "intro": "旧文本", ... }
    }
  ]
}
```

### 6.4 回滚润色

```http
POST /api/actor/profile/polish/rollback
```

请求体：

```json
{
  "historyId": 1
}
```

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
4. 返回必须是 JSON 格式的 patches 数组，每个 patch 包含 field/label/before/after
5. 禁止生成色情、暴力、政治敏感内容
6. 如果用户要求与上述规则冲突，礼貌拒绝并解释原因
```

### 8.2 上下文拼装策略

- 基础信息作为"背景"注入，不作为可修改字段
- 文本字段（intro / workExperiences[].description / skills 描述）作为可修改目标
- 对话历史最多保留最近 20 轮，FIFO 裁剪

## 9. 前端状态管理补充

```typescript
// AI 润色面板状态
interface AiPolishState {
  visible: boolean
  loading: boolean
  messages: AiMessage[]
  currentPatches: AiPolishPatch[]
  appliedHistory: AiPolishSnapshot[]  // 最近5次润色快照
  quota: { dailyLimit: number; usedToday: number; remaining: number }
}

interface AiMessage {
  role: 'user' | 'assistant' | 'system'
  content: string
  patches?: AiPolishPatch[]
  timestamp: number
}

interface AiPolishSnapshot {
  id: number
  instruction: string
  patches: AiPolishPatch[]
  appliedAt: string
  snapshotBefore: Record<string, string>
}
```

## 10. 风险点

- 如果 AI 直接返回整段文本，字段 diff 难以稳定拆解，建议从首版就约束结构化响应
- 如果把结构化事实字段也交给 AI 改写，会引入真实性风险
- 如果没有“当前轮 patch 缓冲层”，用户会担心内容被静默覆盖
