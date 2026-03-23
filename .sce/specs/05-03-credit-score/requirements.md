# 05-03 信用积分与演员等级（Credit & Level）

> 状态：预留 | 优先级：中 | 依赖：00-03, 05-02

## 1. 功能概述

单轨积分制：从 **0 分起步**，通过完善档案、完成拍摄、获得好评、保持活跃来累积积分，满分 100。

积分直接决定演员等级和信用徽章。一个数据源，两种展示形态。

## 2. 积分模型（0→100）

### 2.1 积分来源

#### A. 档案建设（满分 30）

| 行为 | 积分 | 说明 |
|------|------|------|
| 上传头像 | +3 | 一次性 |
| 完善基本信息（姓名+性别+年龄+身高+城市全填） | +5 | 一次性 |
| 上传照片（≥3 张且覆盖 ≥2 个分类） | +5 | 一次性 |
| 上传视频简历 | +5 | 一次性 |
| 填写自我介绍（≥50 字） | +4 | 一次性 |
| 添加作品经历（≥1 条） | +5 | 一次性 |
| 完善形象标签（体型+发型+语言至少各选 1） | +3 | 一次性 |

#### B. 拍摄经验（满分 30）

| 里程碑 | 积分 | 说明 |
|--------|------|------|
| 首次完成拍摄 | +10 | 里程碑 |
| 累计完成 5 次 | +5 | 里程碑 |
| 累计完成 15 次 | +5 | 里程碑 |
| 累计完成 30 次 | +5 | 里程碑 |
| 参与 ≥3 种不同类型项目 | +5 | 里程碑 |

#### C. 口碑评价（满分 25）

| 成就 | 积分 | 说明 |
|------|------|------|
| 首次获得好评 | +5 | 里程碑 |
| 好评率 ≥ 80% | +5 | 动态（降到 80% 以下则扣回） |
| 好评率 ≥ 90% | +5 | 动态（降到 90% 以下则扣回） |
| 连续 5 次无爽约 | +5 | 里程碑 |
| 连续 10 次无爽约 | +5 | 里程碑 |

#### D. 活跃贡献（满分 15）

| 行为 | 积分 | 说明 |
|------|------|------|
| 首次投递 | +3 | 里程碑 |
| 累计投递 10 次 | +3 | 里程碑 |
| 近 30 天有登录 | +3 | 动态（30 天无登录则扣回） |
| 近 30 天有投递 | +3 | 动态（30 天无投递则扣回） |
| 分享过名片 | +3 | 一次性 |

**合计满分**：30 + 30 + 25 + 15 = **100 分**

### 2.2 扣分规则

从已有积分中扣除，最低扣至 0 分：

| 行为 | 扣分 |
|------|------|
| 爽约未到场 | -10 |
| 迟到 | -5 |
| 获得差评 | -5 |
| 频繁取消已确认投递（30 天内 ≥3 次） | -3 |

### 2.3 积分性质说明

- **一次性积分**：达成后永久保留
- **里程碑积分**：达成后永久保留
- **动态积分**：条件不满足时自动扣回（如好评率掉到 80% 以下，扣回 5 分）
- 扣分后积分不低于 0

## 3. 演员等级（积分区间映射）

| 积分区间 | 等级 | 名称 | 标签 | 徽章 |
|---------|------|------|------|------|
| 0-9 | LV.1 | 新秀演员 | NEWCOMER | — |
| 10-24 | LV.2 | 潜力演员 | POTENTIAL | — |
| 25-44 | LV.3 | 活跃演员 | ACTIVE | 🥉 |
| 45-59 | LV.4 | 认证演员 | CERTIFIED | 🥈 |
| 60-74 | LV.5 | 专业演员 | PRO ACTOR | 🥈 |
| 75-89 | LV.6 | 明星演员 | STAR ACTOR | 🥇 |
| 90-100 | LV.7 | 王牌演员 | ACE ACTOR | 💎 |

等级随积分实时变化，升降即时生效。

## 4. 前期 mock 策略

mock 阶段只有**档案建设（A）和部分活跃贡献（D）**可产生积分：

| 场景 | 可得积分 | 等级 |
|------|---------|------|
| 刚注册，什么都没填 | 0 | LV.1 新秀 |
| 填了基本信息+头像 | 8 | LV.1 新秀 |
| 基本信息+头像+照片+介绍 | 17 | LV.2 潜力 |
| 完整档案（A 满分 30）+ 有投递+有登录 | 36 | LV.3 活跃 |

mock 上限 LV.3，需要真实拍摄数据才能达到 LV.4+。

## 5. 需求清单

### 5.1 积分计算

- **R1** 积分从 0 开始，根据行为规则叠加
- **R2** 一次性/里程碑积分达成后永久保留
- **R3** 动态积分条件不满足时自动扣回
- **R4** 扣分后最低为 0，不出现负分
- **R5** 等级随积分实时变化

### 5.2 信用主页 `pages/credit-score/index`

- **R6** 顶部大字展示当前积分 + 等级名称 + 徽章
- **R7** 环形进度条展示当前积分占满分比例
- **R8** 四大类积分明细卡片（档案/经验/口碑/活跃），每类展示已得分/满分
- **R9** 每类点开可查看具体得分项和未完成项
- **R10** 升级提示："再完善视频简历可获得 5 分，升至 LV.3"

### 5.3 积分记录 `pages/credit-record/index`

- **R11** 按时间倒序展示每次积分变化
- **R12** 每条记录：时间、类型（获得/扣除/扣回）、分值、原因、变化后总分
- **R13** 按类型筛选（全部/获得/扣除）

### 5.4 积分排行榜 `pages/credit-rank/index`

- **R14** 全平台 / 按城市排名
- **R15** 列表项：排名、头像、姓名、积分、等级、徽章
- **R16** 高亮当前用户位置

### 5.5 入口

- **R17** 「我的」页面菜单新增"我的信用分"
- **R18** 演员明信片展示等级标签 + 积分徽章

## 6. 组件设计

### KpCreditBadge — 积分徽章

- **R19** 展示积分数值 + 等级对应徽章图标
- **R20** size: small（列表/名片） / medium（详情页） / large（信用主页）
- **R21** 积分为 0 时显示灰色占位

### KpLevelTag — 等级标签

- **R22** 展示 "LV.X 名称"（如 "LV.5 专业演员"）
- **R23** 不同等级不同颜色主题（LV.1-2 灰、LV.3 铜、LV.4-5 银、LV.6 金、LV.7 钻石色）
- **R24** size: small / medium

## 7. 数据结构

```typescript
// 积分总览
interface CreditScore {
  totalScore: number          // 当前总积分 0-100
  level: number               // 等级 1-7
  levelTitle: string          // "新秀演员"..."王牌演员"
  levelTag: string            // "NEWCOMER"..."ACE ACTOR"
  breakdown: CreditBreakdown  // 四类明细
  nextLevelHint?: string      // 升级提示
  nextLevelScore?: number     // 下一等级最低分
}

// 四类明细
interface CreditBreakdown {
  profile: CategoryScore      // 档案建设 0-30
  experience: CategoryScore   // 拍摄经验 0-30
  reputation: CategoryScore   // 口碑评价 0-25
  activity: CategoryScore     // 活跃贡献 0-15
}

interface CategoryScore {
  earned: number              // 已得分
  max: number                 // 满分
  items: ScoreItem[]          // 具体得分项
}

interface ScoreItem {
  label: string               // "上传头像"
  score: number               // 该项分值
  achieved: boolean           // 是否已达成
  type: 'once' | 'milestone' | 'dynamic'
}

// 积分记录
interface CreditRecord {
  id: number
  type: 'earn' | 'deduct' | 'revoke'  // 获得/扣除/动态扣回
  amount: number
  reason: string
  category: 'profile' | 'experience' | 'reputation' | 'activity'
  totalAfter: number          // 变化后总分
  createdAt: string
}

// 排行榜
interface CreditRankItem {
  rank: number
  userId: number
  name: string
  avatar: string
  totalScore: number
  level: number
  levelTitle: string
  isCurrentUser: boolean
}
```

## 8. API 设计

```typescript
// api/credit.ts
getMyCreditScore(): Promise<CreditScore>
getCreditRecords(params: {
  type?: 'earn' | 'deduct' | 'revoke'
  page: number
  size: number
}): Promise<PageResult<CreditRecord>>
getCreditRank(params: {
  scope?: 'all' | 'city'
  page: number
  size: number
}): Promise<PageResult<CreditRankItem>>
```

## 9. 依赖

- `00-01 global-style-system` — Design Tokens
- `00-02 shared-components` — KpPageLayout, KpNavBar, KpCard, KpEmpty
- `00-03 shared-utils-api` — request 封装、types
- `05-02 actor-profile-enhance` — 档案完整度数据源

## 10. 验收标准

- [ ] 积分从 0 开始，档案建设行为正确加分
- [ ] mock 阶段积分和等级与档案完整度对应（LV.1-3）
- [ ] 信用主页正确展示积分、等级、四类明细、升级提示
- [ ] 积分记录列表可筛选、分页
- [ ] 排行榜支持全平台/城市切换，高亮当前用户
- [ ] KpCreditBadge 和 KpLevelTag 在各展示位置正确渲染
- [ ] 扣分后积分不低于 0
- [ ] 动态积分条件不满足时正确扣回
