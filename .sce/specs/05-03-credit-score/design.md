# 信用积分与演员等级 - 技术设计

_Requirements: 05-03 全部_

## 1. 路由配置

```json
// pages.json 新增
[
  {
    "path": "pages/credit-score/index",
    "style": {
      "navigationStyle": "custom",
      "navigationBarTitleText": "信用积分",
      "backgroundColor": "#121214"
    }
  },
  {
    "path": "pages/credit-record/index",
    "style": {
      "navigationStyle": "custom",
      "navigationBarTitleText": "积分记录",
      "backgroundColor": "#121214"
    }
  },
  {
    "path": "pages/credit-rank/index",
    "style": {
      "navigationStyle": "custom",
      "navigationBarTitleText": "积分排行榜",
      "backgroundColor": "#121214"
    }
  }
]
```

```json
// tabBar 新增
{
  "tabBar": {
    "list": [
      { "pagePath": "pages/home/index", "text": "首页" },
      { "pagePath": "pages/credit-rank/index", "text": "排行榜" },
      { "pagePath": "pages/mine/index", "text": "我的" }
    ]
  }
}
```

## 2. 依赖清单

| 类别 | 依赖项 | 来源 Spec |
|------|--------|-----------|
| 布局 | KpPageLayout | 00-02 |
| 导航 | KpNavBar | 00-02 |
| 卡片 | KpCard | 00-02 |
| 空态 | KpEmpty | 00-02 |
| API | getMyCreditScore, getCreditRecords, getCreditRank | 05-03 (api/credit) |
| Store | useUserStore | 00-03 |
| 样式 | Design Tokens ($kp-*) | 00-01 |

## 3. 积分计算逻辑（前端 mock）

mock 阶段积分在前端根据 ActorProfile 数据计算：

```typescript
// utils/credit.ts
function calculateCreditScore(profile: ActorProfile): CreditScore {
  const breakdown: CreditBreakdown = {
    profile: calcProfileScore(profile),     // 0-30
    experience: calcExperienceScore([]),     // mock: 0
    reputation: calcReputationScore([]),     // mock: 0
    activity: calcActivityScore(profile),    // 0-15（部分）
  }
  const totalScore = breakdown.profile.earned
    + breakdown.experience.earned
    + breakdown.reputation.earned
    + breakdown.activity.earned
  return {
    totalScore,
    level: scoreToLevel(totalScore),
    levelTitle: LEVEL_TITLES[scoreToLevel(totalScore)],
    levelTag: LEVEL_TAGS[scoreToLevel(totalScore)],
    breakdown,
    nextLevelHint: getNextLevelHint(totalScore),
    nextLevelScore: getNextLevelThreshold(totalScore),
  }
}

function scoreToLevel(score: number): number {
  if (score >= 90) return 7
  if (score >= 75) return 6
  if (score >= 60) return 5
  if (score >= 45) return 4
  if (score >= 25) return 3
  if (score >= 10) return 2
  return 1
}

const LEVEL_TITLES: Record<number, string> = {
  1: '新秀演员', 2: '潜力演员', 3: '活跃演员',
  4: '认证演员', 5: '专业演员', 6: '明星演员', 7: '王牌演员',
}
const LEVEL_TAGS: Record<number, string> = {
  1: 'NEWCOMER', 2: 'POTENTIAL', 3: 'ACTIVE',
  4: 'CERTIFIED', 5: 'PRO ACTOR', 6: 'STAR ACTOR', 7: 'ACE ACTOR',
}
```

## 4. 页面结构

### 4.1 信用主页 `credit-score/index`（A 类深色 Hero 页）

```
┌─────────────────────────────────┐
│  [返回]        信用积分          │
│                                 │
│            28                   │  ← 大字积分
│        LV.3 活跃演员  🥉         │
│    ┌──────────────────────┐     │
│    │ ████████░░░░░  28/100│     │  ← 环形进度条
│    └──────────────────────┘     │
│   升至 LV.4 还需 17 分          │
├── 白色内容区 ───────────────────┤
│                                 │
│  ┌ 档案建设 ─────── 22/30 ──┐  │
│  │ ✅ 头像 +3                 │  │
│  │ ✅ 基本信息 +5             │  │
│  │ ✅ 照片 +5                 │  │
│  │ ✅ 自我介绍 +4             │  │
│  │ ✅ 作品经历 +5             │  │
│  │ ☐ 视频简历 +5 ← 去完善     │  │
│  │ ☐ 形象标签 +3 ← 去完善     │  │
│  └────────────────────────┘   │
│  ┌ 拍摄经验 ─────── 0/30 ───┐  │
│  │ ☐ 首次完成拍摄 +10        │  │
│  │ ...                       │  │
│  └────────────────────────┘   │
│  ┌ 口碑评价 ─────── 0/25 ───┐  │
│  └────────────────────────┘   │
│  ┌ 活跃贡献 ─────── 6/15 ───┐  │
│  └────────────────────────┘   │
│                                 │
│  [查看积分记录]  [查看排行榜]    │
└─────────────────────────────────┘
```

### 4.2 积分记录 `credit-record/index`（B 类普通顶部页）

```
┌─────────────────────────────────┐
│  [返回]        积分记录          │
├─────────────────────────────────┤
│  [全部] [获得] [扣除]            │  ← 筛选 Tab
│                                 │
│  ┌────────────────────────────┐ │
│  │ +5  完善基本信息             │ │
│  │ 档案建设 · 总分 8    03-23  │ │
│  └────────────────────────────┘ │
│  ┌────────────────────────────┐ │
│  │ +3  上传头像                 │ │
│  │ 档案建设 · 总分 3    03-23  │ │
│  └────────────────────────────┘ │
│  ...（分页加载）                 │
└─────────────────────────────────┘
```

### 4.3 排行榜 `credit-rank/index`（底部 Tab 独立页）

```
┌─────────────────────────────────┐
│              排行榜              │
│        演员信用榜单              │
├─────────────────────────────────┤
│  [全平台] [本城市]               │  ← 切换 Tab
│                                 │
│  🥇 1  [头像] 李四  LV.5  72分  │
│  🥈 2  [头像] 王五  LV.4  58分  │
│  🥉 3  [头像] 赵六  LV.3  42分  │
│     4  [头像] 张三  LV.3  28分 ←│  ← 高亮自己
│     5  ...                      │
│  ...（分页加载）                 │
└─────────────────────────────────┘
```

## 5. 组件设计

### 5.1 KpCreditBadge

```typescript
defineProps<{
  score: number       // 积分数值
  level: number       // 等级 1-7
  size?: 'small' | 'medium' | 'large'  // 默认 medium
}>()
```

渲染：`积分数值 + 徽章图标`。根据 level 选择图标（LV.1-2 无图标，LV.3 🥉，LV.4-5 🥈，LV.6 🥇，LV.7 💎）。

### 5.2 KpLevelTag

```typescript
defineProps<{
  level: number       // 等级 1-7
  title: string       // 等级名称
  size?: 'small' | 'medium'  // 默认 medium
}>()
```

渲染：`LV.X 名称`。颜色主题：
- LV.1-2: `$kp-color-text-secondary`（灰）
- LV.3: `#CD7F32`（铜色）
- LV.4-5: `#C0C0C0`（银色）
- LV.6: `#FFD700`（金色）
- LV.7: `#B9F2FF`（钻石色）

## 6. 入口改造

### mine/index.vue — actorMenus 新增

```typescript
{
  key: 'credit',
  label: '我的信用分',
  desc: '查看积分明细与成长情况',
  path: '/pages/credit-score/index',
}
```

### mine/index.vue — 头部 stats 改造

```typescript
// 旧
{ label: '被查看', value: viewedCount.value }

// 新
{ label: '积分', value: creditScore.value?.totalScore ?? 0 }
```

等级标签替换硬编码 `LV.4`：
```typescript
// 旧
const levelText = computed(() => userStore.isActor ? 'LV.4' : ...)

// 新
const levelText = computed(() => userStore.isActor
  ? `LV.${creditScore.value?.level ?? 1}`
  : ...)
```
