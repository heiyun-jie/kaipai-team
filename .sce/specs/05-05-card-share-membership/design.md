# 名片分享与等级体系 v2 - 技术设计

_Requirements: 05-05 v2 全部_

## 1. 路由与页面归属

名片相关页面全部在 `pkg-card` 分包：

```json
{
  "subPackages": [
    {
      "root": "pkg-card",
      "pages": [
        { "path": "actor-card/index", "style": { "navigationStyle": "custom", "backgroundColor": "#121214" } },
        { "path": "membership/index", "style": { "navigationStyle": "custom", "backgroundColor": "#121214" } }
      ]
    }
  ]
}
```

主包保留：

```json
{ "path": "pages/actor-profile/detail", "style": { "navigationStyle": "custom", "backgroundColor": "#121214" } }
```

## 2. 模块分工

| 模块 | 职责 |
|------|------|
| `pkg-card/actor-card/index.vue` | 名片主页面：场景切换、配色定制、海报生成、分享入口 |
| `pkg-card/membership/index.vue` | 等级中心：等级进度、邀请任务、能力清单、配额展示 |
| `pages/actor-profile/detail.vue` | 公开详情页：分享落地、名片回跳 |
| `types/level.ts` | 等级枚举、等级信息、场景模板、定制配置类型定义 |
| `types/membership.ts` | **废弃**，由 `level.ts` 替代 |
| `utils/actor-card.ts` | 名片摘要、场景文案生成、分享态维护、主题计算 |
| `utils/level.ts` | 等级计算、能力矩阵、模板可用性判断、AI 配额判断 |
| `utils/membership.ts` | **废弃**，由 `level.ts` 替代 |
| `api/level.ts` | 等级信息、模板配置、定制配置、AI 配额接口 |
| `stores/user.ts` | 用户等级态、认证状态、邀请数 |

## 3. 等级体系

### 3.1 等级计算规则

```ts
function calculateLevel(inviteCount: number, isCertified: boolean, profileCompletion: number): UserLevel {
  if (!isCertified || profileCompletion < 70) return UserLevel.Lv0
  if (inviteCount >= 8) return UserLevel.Lv5
  if (inviteCount >= 5) return UserLevel.Lv4
  if (inviteCount >= 3) return UserLevel.Lv3
  if (inviteCount >= 1) return UserLevel.Lv2
  return UserLevel.Lv1
}
```

### 3.2 能力矩阵

```ts
interface LevelCapability {
  maxScenes: number           // 可用场景数
  canCustomColor: boolean     // 配色微调
  canCustomLayout: boolean    // 布局选择
  aiQuotaPerMonth: number     // AI 月配额
  canUseLuckyColor: boolean   // 命理配色
  paidSkinFreePreview: boolean // 付费皮肤免费体验
}

const LEVEL_CAPABILITIES: Record<UserLevel, LevelCapability> = {
  [UserLevel.Lv0]: { maxScenes: 0, canCustomColor: false, canCustomLayout: false, aiQuotaPerMonth: 0, canUseLuckyColor: false, paidSkinFreePreview: false },
  [UserLevel.Lv1]: { maxScenes: 2, canCustomColor: false, canCustomLayout: false, aiQuotaPerMonth: 1, canUseLuckyColor: false, paidSkinFreePreview: false },
  [UserLevel.Lv2]: { maxScenes: 3, canCustomColor: false, canCustomLayout: false, aiQuotaPerMonth: 1, canUseLuckyColor: false, paidSkinFreePreview: false },
  [UserLevel.Lv3]: { maxScenes: 3, canCustomColor: true,  canCustomLayout: false, aiQuotaPerMonth: 3, canUseLuckyColor: false, paidSkinFreePreview: false },
  [UserLevel.Lv4]: { maxScenes: 5, canCustomColor: true,  canCustomLayout: true,  aiQuotaPerMonth: 4, canUseLuckyColor: false, paidSkinFreePreview: false },
  [UserLevel.Lv5]: { maxScenes: 5, canCustomColor: true,  canCustomLayout: true,  aiQuotaPerMonth: 5, canUseLuckyColor: true,  paidSkinFreePreview: true  },
}
```

### 3.3 Store 变更

```ts
// stores/user.ts 新增
const userLevel = computed(() => calculateLevel(
  userInfo.value?.inviteCount ?? 0,
  userInfo.value?.isCertified ?? false,
  userInfo.value?.profileCompletion ?? 0
))
const levelCapability = computed(() => LEVEL_CAPABILITIES[userLevel.value])
```

移除旧字段：`membershipPlan`、`isMember`、`membershipLabel`

## 4. 场景名片

### 4.1 场景模板配置

模板由后端接口下发 `GET /api/card/scene-templates`，前端不硬编码：

```ts
// 接口返回结构
interface SceneTemplateResponse {
  scenes: SceneTemplate[]
}

interface SceneTemplate {
  sceneKey: CardScene
  name: string
  description: string
  coverImage: string              // 预览封面图 URL
  themeColors: {
    primary: string
    accent: string
    background: string
    text: string
    heroText: string
  }
  layoutVariant: 'compact' | 'spacious' | 'magazine'
  contentFocus: string[]          // 突出板块 key
  heroEyebrow: string            // 顶部标语
  tier: 'free' | 'paid'
  requiredLevel: UserLevel
}
```

### 4.2 场景与内容侧重映射

| 场景 | 突出经历 dramaType | 突出照片类型 | 突出标签 |
|------|-------------------|-------------|---------|
| costume | 古装剧(3,TV)、电影(2) | production 剧照 | 身段、武戏、骑马 |
| urban | 都市剧(3,TV)、短剧(1) | lifestyle 生活照 | 台词、情感表达 |
| commercial | 广告(4)、短视频(1) | portrait 形象照 | 镜头感、亲和力 |
| artistic | 电影(2)、独立片 | production 剧照 | 表演深度、即兴 |
| general | 全部 | 全部 | 全部 |

前端根据场景 key 过滤 `actorExperiences` 和 `photoUrls` 中的内容，优先展示匹配项。

### 4.3 场景切换交互

```
本人态名片页:
┌─────────────────────────────┐
│ [返回]              [分享]   │  ← 导航层
│                             │
│  场景: [古装] [都市] [商业]   │  ← 场景选择器（横向滚动 tag）
│                             │
│  ┌─ 名片内容区 ─────────┐   │  ← 根据场景变化
│  │ Hero + 头像 + 标签    │   │
│  │ 场景相关经历          │   │
│  │ 场景相关照片          │   │
│  └──────────────────────┘   │
│                             │
│  [配色定制] [AI润色] [海报]   │  ← 操作栏（按等级灰度）
└─────────────────────────────┘
```

## 5. 配色定制

### 5.1 定制配置存储

后端新增 `actor_card_config` 表：

```sql
CREATE TABLE actor_card_config (
  id          BIGINT PRIMARY KEY AUTO_INCREMENT,
  actor_id    BIGINT NOT NULL,
  scene_key   VARCHAR(32) NOT NULL DEFAULT 'general',
  layout_variant VARCHAR(16) DEFAULT 'compact',
  primary_color  VARCHAR(7),   -- '#FF6B35'
  accent_color   VARCHAR(7),
  bg_color       VARCHAR(7),
  highlighted_experiences JSON, -- [expId, ...]
  highlighted_photos     JSON, -- [url, ...]
  tag_order              JSON, -- [tag, ...]
  created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at  DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY uk_actor_scene (actor_id, scene_key)
);
```

每个演员每个场景一条配置。

### 5.2 接口

```
GET  /api/card/config?actorId={id}&scene={key}    → ActorCardConfig
POST /api/card/config                              → 保存定制配置
GET  /api/card/scene-templates                     → SceneTemplate[]
```

### 5.3 配色选择器

不做完整低代码编辑器。用色盘选择器组件：

- 提供 12 个预设色 + 自定义 hex 输入
- 实时预览：改色后名片区域即时刷新
- 仅修改 `primaryColor`、`accentColor`、`backgroundColor` 三个值

### 5.4 主题计算

```ts
function resolveCardTheme(scene: SceneTemplate, customConfig?: ActorCardConfig): CardTheme {
  const base = scene.themeColors
  return {
    primary: customConfig?.primaryColor || base.primary,
    accent: customConfig?.accentColor || base.accent,
    background: customConfig?.backgroundColor || base.background,
    text: base.text,
    heroText: base.heroText,
  }
}
```

## 6. 分享参数

### 6.1 URL 结构

```
/pkg-card/actor-card/index?actorId=<id>&scene=<costume|urban|commercial|artistic|general>&tone=<natural|professional|commercial>&shared=1
```

### 6.2 访客端渲染流程

```
1. 解析 URL 参数
2. GET /api/card/config?actorId=X&scene=Y  → 获取该演员该场景的定制配置
3. GET /api/card/scene-templates            → 获取场景模板基础配置（可缓存）
4. GET /api/actor/profile?id=X              → 获取演员档案
5. resolveCardTheme(template, config)       → 合并出最终主题
6. 渲染名片
```

访客不需要登录，接口需支持无 token 公开访问。

## 7. AI 简历润色

### 7.1 配额接口

```
GET  /api/ai/quota?type=resume_polish    → AiUsageQuota
POST /api/ai/polish-resume               → 润色结果（扣减配额）
```

### 7.2 前端交互

- 点击 AI 润色 → 检查配额 → 有余量则调用 → 展示结果 → 用户确认应用
- 配额不足 → 弹窗提示"本月次数已用完，邀请好友可提升等级获取更多次数"

### 7.3 当前阶段

当前允许前端 mock 润色结果（本地规则生成）。后端真实接口对接大模型后，前端只替换 API 调用，不改 UI 逻辑。

## 8. 等级中心页（原会员页）

### 8.1 页面结构

```
┌─────────────────────────────┐
│ [返回]    我的等级            │
│                             │
│  ┌─ 等级卡 ────────────┐    │
│  │ Lv3  ★★★☆☆          │    │
│  │ 已邀请 3 人           │    │
│  │ 再邀请 2 人升 Lv4     │    │
│  │ [═════���══░░░] 3/5    │    │
│  └─────────────────────┘    │
│                             │
│  已解锁能力                  │
│  ✓ 基础场景模板              │
│  ✓ 配色微调                  │
│  ✓ AI润色 3次/月             │
│                             │
│  下一级解锁                  │
│  ○ 布局选择                  │
│  ○ 全部场景模板              │
│                             │
│  [邀请好友]  [我的邀请记录]    │
└─────────────────────────────┘
```

### 8.2 替代原会员页

原 `pkg-card/membership/index.vue` 重写为等级中心，不再展示 basic/pro 对比。

## 9. 清理策略

### 9.1 废弃文件

- `types/membership.ts` → 由 `types/level.ts` 替代
- `utils/membership.ts` → 由 `utils/level.ts` 替代

### 9.2 废弃概念

- `MembershipPlan` 枚举（basic/pro）
- `CardTemplateKey`（starter/signature/cinematic）→ 由 `CardScene` + 后端模板配置替代
- `isMember` / `membershipLabel` 计算属性
- `getAvailableCardTemplates()` → 由 `getAvailableScenes()` 替代
- `resolveCardTemplate()` → 由 `resolveCardScene()` 替代

### 9.3 保留概念

- `audience`（crew/brand/friend）分享受众维度保留，与 `scene` 正交
- `tone`（natural/professional/commercial）文案风格保留
- `polishActorCardCopy()` 保留但需适配场景参数
- `setActorShareState()` 保留但参数从 `template` 改为 `scene`

## 10. 后端接口清单

| 接口 | 方法 | 说明 | 鉴权 |
|------|------|------|------|
| `/api/level/info` | GET | 当前用户等级、邀请数、配额 | 需登录 |
| `/api/card/scene-templates` | GET | 全部场景模板配置 | 公开 |
| `/api/card/config` | GET | 某演员某场景的定制配置 | 公开 |
| `/api/card/config` | POST | 保存定制配置 | 需登录 |
| `/api/ai/quota` | GET | AI 使用配额 | 需登录 |
| `/api/ai/polish-resume` | POST | AI 润色（扣配额） | 需登录 |

## 11. 包体控制

- 场景模板配置走接口下发，不打包前端资源
- 模板预览图走 CDN（腾讯 COS），不放本地
- 色盘选择器为轻量组件（预估 < 5 KB）
- 整个定制模块在 `pkg-card` 分包，不影响主包体积
