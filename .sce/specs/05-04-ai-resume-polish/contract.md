# AI 简历润色 - 协议冻结

_Frozen on 2026-04-02_

## 1. 适用范围

本文件是 `05-04 ai-resume-polish` 的实现口径基线，覆盖：

- 小程序 `pages/actor-profile/edit` 的 AI 调用、patch 预览、应用与撤销
- 服务端 `/api/ai/*` 的简历润色协议、历史与回滚协议
- `PUT /api/actor/profile` 与 AI patch 应用的衔接方式

若 `design.md`、`00-28 execution/*`、前后端代码与本文件冲突，以本文件为准。

## 2. 字段边界

### 2.1 本轮允许 AI 直接产出 patch 的字段

| fieldType | fieldKey 格式 | 最终保存目标 | 说明 |
|----------|---------------|--------------|------|
| `intro` | `intro` | `ActorProfileSaveDTO.intro` | 演员自我介绍，可直接做文案润色 |
| `work_experience_description` | `work_experience:{experienceKey}:description` | `ActorWorkExperienceDTO.description` | 单条拍摄经历描述，`experienceKey` 当前只允许使用已持久化的服务端 `id`；未保存的新经历需先保存档案，再进入 AI 可编辑字段 |

### 2.2 只读上下文字段

以下字段可作为 AI 上下文输入，但本轮不得由 AI 直接写回：

- `name`
- `gender`
- `age`
- `height`
- `city`
- `avatar`
- `photos`
- `photoCategories`
- `videoUrl`
- `skillTypes`
- `bodyType`
- `hairStyle`
- `languages`
- `workExperiences[].projectName`
- `workExperiences[].roleName`
- `workExperiences[].shootDate`

原因：

- 这些字段要么是结构化事实，要么受前端固定枚举 / 上传资源约束
- 一旦允许 AI 自行改写，会直接引入虚构履历、枚举漂移或资源错配

## 3. 核心设计决定

### 3.1 patch 只代表草稿，不代表已保存

- `POST /api/ai/polish-resume` 只返回草稿 patch，不直接修改演员档案
- 用户在编辑页“按字段应用 / 整批应用”时，只是把 patch 写回本地 `form`
- 真实入库仍然统一走 `PUT /api/actor/profile`

### 3.2 AI 应用记录跟随档案保存确认

- AI 服务在生成 patch 时返回 `draftId`
- 编辑页若把某轮 patch 应用到表单，提交 `PUT /api/actor/profile` 时，必须带上 `aiResumeApplyMeta`
- 只有档案保存成功后，这轮 AI patch 才算正式形成可回滚历史

这样做的原因：

- 保持演员档案写库只有一个权威入口，避免 `/ai/*` 和 `/actor/profile` 双写
- 历史回滚基于“已保存成功”的应用记录，而不是基于编辑页未提交的临时表单

## 4. 请求协议

### 4.1 `POST /api/ai/polish-resume`

请求体：

```json
{
  "instruction": "把自我介绍改得更专业一些，突出短剧和广告拍摄经验",
  "conversationId": "airp_conv_01",
  "profileVersion": "profile_v20260402_01",
  "context": {
    "actorId": 10001,
    "certificationStatus": "verified",
    "levelLabel": "Lv3",
    "name": "张三",
    "gender": "female",
    "age": 24,
    "height": 168,
    "city": "杭州",
    "bodyType": "标准",
    "hairStyle": "中长",
    "languages": ["普通话", "英语"],
    "skillTypes": ["短剧", "广告"],
    "editableFields": [
      {
        "fieldType": "intro",
        "fieldKey": "intro",
        "label": "自我介绍",
        "currentValue": "..."
      },
      {
        "fieldType": "work_experience_description",
        "fieldKey": "work_experience:8721:description",
        "label": "拍摄经历描述",
        "targetId": "8721",
        "projectName": "《长安风云》",
        "roleName": "侍女",
        "shootDate": "2025-07",
        "currentValue": "..."
      }
    ]
  },
  "history": [
    {
      "role": "user",
      "content": "把语气改得更职业一些"
    },
    {
      "role": "assistant",
      "content": "已为你优化自我介绍"
    }
  ]
}
```

约束：

- `instruction` 必填
- `history` 只保留最近 20 轮
- `fieldKey` 不能使用数组下标，例如 `workExperiences[0].description`
- `profileVersion` 本轮先预留，可为空；当前实现已透传但尚未做强制 stale patch 校验

### 4.2 `PUT /api/actor/profile`

演员档案保存 DTO 预留：

```json
{
  "name": "张三",
  "intro": "...",
  "workExperiences": [
    {
      "id": 8721,
      "projectName": "《长安风云》",
      "description": "..."
    }
  ],
  "aiResumeApplyMeta": {
    "draftId": "airp_draft_01",
    "requestId": "airp_req_01",
    "appliedPatchIds": ["patch_intro_01", "patch_exp_01"],
    "profileVersion": "profile_v20260402_01"
  }
}
```

说明：

- `aiResumeApplyMeta` 只在本次保存确实应用了 AI patch 时上传
- 未应用任何 patch 时，不传该字段
- 后端需以 `aiResumeApplyMeta` 把本次保存与 AI 草稿关联，形成正式历史

## 5. 响应协议

### 5.1 `POST /api/ai/polish-resume`

返回体：

```json
{
  "requestId": "airp_req_01",
  "conversationId": "airp_conv_01",
  "draftId": "airp_draft_01",
  "reply": "我已经按更职业的演员简历口径优化了你的介绍。",
  "patches": [
    {
      "patchId": "patch_intro_01",
      "fieldType": "intro",
      "fieldKey": "intro",
      "label": "自我介绍",
      "beforeValue": "...",
      "afterValue": "...",
      "reason": "强化专业度和信息密度",
      "status": "pending"
    }
  ],
  "quota": {
    "userId": 10001,
    "quotaType": "resume_polish",
    "totalQuota": 20,
    "usedCount": 3,
    "periodType": "monthly",
    "periodStart": "2026-04-01"
  },
  "warnings": []
}
```

约束：

- `patches` 只返回当前轮草稿
- `status` 首轮固定为 `pending`
- `quota` 返回扣减后的服务端权威结果

## 6. 历史与回滚协议

### 6.1 `GET /api/ai/resume-polish/history`

只返回“已通过 `PUT /api/actor/profile` 保存成功”的记录，不返回纯草稿。

单条记录结构：

```json
{
  "historyId": "airp_hist_01",
  "draftId": "airp_draft_01",
  "requestId": "airp_req_01",
  "conversationId": "airp_conv_01",
  "instruction": "把自我介绍改得更专业一些",
  "reply": "我已经按更职业的演员简历口径优化了你的介绍。",
  "status": "applied",
  "patches": [
    {
      "patchId": "patch_intro_01",
      "fieldType": "intro",
      "fieldKey": "intro",
      "label": "自我介绍",
      "beforeValue": "...",
      "afterValue": "...",
      "reason": "强化专业度和信息密度",
      "status": "applied"
    }
  ],
  "beforeSnapshot": [
    { "fieldKey": "intro", "value": "旧文案" }
  ],
  "afterSnapshot": [
    { "fieldKey": "intro", "value": "新文案" }
  ],
  "createdAt": "2026-04-02T10:00:00",
  "appliedAt": "2026-04-02T10:03:00",
  "rolledBackAt": null
}
```

### 6.2 `POST /api/ai/resume-polish/history/{historyId}/rollback`

请求体：

```json
{
  "profileVersion": "profile_v20260402_02"
}
```

返回体：

```json
{
  "historyId": "airp_hist_01",
  "rollbackId": "airp_rb_01",
  "restoredSnapshots": [
    { "fieldKey": "intro", "value": "旧文案" }
  ],
  "profileVersion": "profile_v20260402_03",
  "rolledBackAt": "2026-04-02T10:10:00"
}
```

约束：

- rollback 只能作用于 `status=applied` 的历史记录
- rollback 成功后，原记录状态更新为 `rolled_back`
- rollback 后仍然通过演员档案权威写库链路更新下游展示

## 7. 错误码冻结

本项目现有错误结构是 `R.code + R.message`，因此 AI 简历错误码冻结为数值口径：

| code | 语义 | 前端动作 |
|------|------|----------|
| `7101` | 未登录或登录态失效 | 拉起登录并中断 AI 面板 |
| `7102` | 未完成实名认证，不能使用 AI 简历 | 展示认证前置并跳转认证 |
| `7103` | 当前等级暂无 AI 润色额度 / 配额已用尽 | 展示配额提示与升级引导 |
| `7104` | AI 简历上下文不合法 | 提示补全档案或刷新页面 |
| `7105` | 命中敏感内容，未生成 patch | 展示拒绝原因，不扣减或自动回补额度 |
| `7106` | 模型超时 | 支持重试，不视为成功 |
| `7107` | 模型响应不可解析 | 展示通用失败提示并记录日志 |
| `7108` | 档案版本已过期，patch 不能直接应用 | 刷新档案后重新生成 patch |
| `7109` | AI 历史不存在或当前用户无权访问 | 刷新历史列表 |
| `7110` | AI 历史回滚冲突 | 刷新档案后重试回滚 |

说明：

- 现有 `500 + message` 的临时写法，不足以支撑前端分支逻辑
- `ai-resume` 后续新增异常必须优先复用以上编码区间，不再只给模糊文案

## 8. 本轮明确不做

- 不新增单独的 `/api/ai/resume-polish/context` 端点；上下文直接随 `POST /api/ai/polish-resume` 传输
- 不允许 `/api/ai/polish-resume` 直接写演员档案
- 不允许 AI 修改图片、视频、枚举型标签和结构化事实字段
- 不允许历史记录基于数组下标定位字段
