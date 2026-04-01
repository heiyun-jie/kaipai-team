# 05-08 命理个性化（Fortune Personalization）

> 状态：待实现 | 优先级：P1 | 依赖：05-05 v2（等级体系与名片定制）
> 本 Spec 为独立功能模块，产出数据供名片定制消费

## 1. 功能概述

为演员提供基于生日的命理画像系统，包含：

1. **幸运色 / 幸运数字**：每月更新，可一键应用为名片主色
2. **十二生肖**：由出生年自动推算，展示生肖性格特质与本月运势
3. **十二星座**：由出生日期自动推算，展示星座特质与本月运势
4. **紫微斗数命盘**：由出生日期+时辰推算命宫主星，展示命盘特质

以上数据均通过外部 AI 大模型生成，后端缓存，前端展示并与名片定制系统联动。

## 2. 产品边界

### 2.1 本轮范围

- 命理画像展示页面（生肖 + 星座 + 紫微主星 + 幸运色/数字）
- 外部 AI 大模型对接（后端调用，Prompt 模板化）
- 幸运色一键应用到名片配色
- 月度自动更新机制

### 2.2 不在本轮范围

- 用户自建命盘、手动输入出生时辰（初期由生日推算，时辰可选填）
- 社交互动（命理匹配、合盘）
- 付费算命 / 深度解读

## 3. 需求清单

### 3.1 基础数据推算

- **R1** 生肖由 `birthday` 年份自动推算（已有 `ActorProfile.birthday` 字段）
- **R2** 星座由 `birthday` 月日自动推算
- **R3** 紫微斗数需出生时辰，初期提供"不确定"选项，后端以默认时辰（午时）推算
- **R4** 用户可在个人资料中补填出生时辰（`birthHour`），补填后重新推算

### 3.2 AI 大模型推算

- **R5** 后端对接外部 AI 大模型（通义千问 / 智谱 / DeepSeek）
- **R6** Prompt 模板后端维护，前端不接��大模型细节
- **R7** 每月为每位用户生成一次命理报告，结果缓存在数据库
- **R8** 命理报告内容：

| 项目 | 内容 |
|------|------|
| 幸运色 | hex 色值 + 颜色名称 + 一句话解读 |
| 幸运数字 | 1-99 + 一句话解读 |
| 生肖运势 | 本月关键词 + 3 句话运势解读 |
| 星座运势 | 本月关键词 + 3 句话运势解读 |
| 紫微主星 | 主星名称 + 性格特质 + 本月建议 |

- **R9** AI 返回 JSON 格式，后端校验结构后存储

### 3.3 展示与交互

- **R10** 命理画像页在 `pkg-card` 分包：`pkg-card/fortune/index`
- **R11** 页面结构：

```
┌───────────────────────────┐
│ [返回]    我的命理          │
│                           │
│  本月幸运                  │
│  ┌──────┬──────┐          │
│  │🎨 幸运色 │ 🔢 幸运数字│   │
│  │ 落日橘   │   7       │   │
│  │ #FF6B35  │          │   │
│  └──────┴──────┘          │
│  [应用幸运色到我的名片]     │
│                           │
│  🐉 生肖：龙               │
│  本月关键词：突破            │
│  "本月适合大胆尝试新角色…"   │
│                           │
│  ♌ 星座：狮子座             │
│  本月关键词：表现力          │
│  "镜头前的自信是你的武器…"   │
│                           │
│  ⭐ 紫微主星：七杀星         │
│  性格特质：果断、有魄力      │
│  本月建议："适合挑战反派…"   │
│                           │
│  数据每月初自动更新          │
└───────────────────────────┘
```

- **R12** "应用幸运色到我的名片"点击后调用 05-05 的 `POST /api/card/config` 更新 `primaryColor`
- **R13** 命理功能 Lv5 完整可用，Lv1-Lv4 可查看生肖/星座基础信息，幸运色应用到名片需 Lv5

### 3.4 入口

- **R14** "我的"页新增"我的命理"入口
- **R15** 名片定制面板中，配色区域显示"试试本月幸运色？"引导（Lv5）

## 4. 数据模型

### 4.1 后端表结构

```sql
-- 命理报告（按月缓存）
CREATE TABLE fortune_report (
  id             BIGINT PRIMARY KEY AUTO_INCREMENT,
  user_id        BIGINT NOT NULL,
  month          VARCHAR(7) NOT NULL,        -- '2026-04'
  zodiac_animal  VARCHAR(8) NOT NULL,         -- 'dragon'
  zodiac_fortune JSON,                        -- { keyword, readings[] }
  constellation  VARCHAR(16) NOT NULL,        -- 'leo'
  constellation_fortune JSON,                 -- { keyword, readings[] }
  ziwei_star     VARCHAR(16),                 -- 'seven_kills'
  ziwei_profile  JSON,                        -- { trait, monthlyAdvice }
  lucky_color    VARCHAR(7) NOT NULL,         -- '#FF6B35'
  lucky_color_name VARCHAR(16) NOT NULL,      -- '落日橘'
  lucky_color_interpretation VARCHAR(128),
  lucky_number   INT NOT NULL,
  lucky_number_interpretation VARCHAR(128),
  birth_hour     VARCHAR(4),                  -- 出生时辰 key，可为 null
  created_at     DATETIME DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uk_user_month (user_id, month)
);

-- 演员表新增字段
ALTER TABLE actor_profile ADD COLUMN birth_hour VARCHAR(4) DEFAULT NULL COMMENT '出生时辰(子丑寅卯...)';
```

### 4.2 前端类型

```ts
type ZodiacAnimal = 'rat' | 'ox' | 'tiger' | 'rabbit' | 'dragon' | 'snake' |
                    'horse' | 'goat' | 'monkey' | 'rooster' | 'dog' | 'pig'

type Constellation = 'aries' | 'taurus' | 'gemini' | 'cancer' | 'leo' | 'virgo' |
                     'libra' | 'scorpio' | 'sagittarius' | 'capricorn' | 'aquarius' | 'pisces'

type ZiweiStar = 'emperor' | 'minister' | 'treasury' | 'sun' | 'moon' |
                 'greedy_wolf' | 'giant_gate' | 'power' | 'literature' |
                 'honest' | 'army' | 'seven_kills' | 'broken_army'

interface FortuneReport {
  month: string
  zodiacAnimal: ZodiacAnimal
  zodiacFortune: { keyword: string; readings: string[] }
  constellation: Constellation
  constellationFortune: { keyword: string; readings: string[] }
  ziweiStar: ZiweiStar | null
  ziweiProfile: { trait: string; monthlyAdvice: string } | null
  luckyColor: string
  luckyColorName: string
  luckyColorInterpretation: string
  luckyNumber: number
  luckyNumberInterpretation: string
}
```

## 5. AI 大模型对接

### 5.1 Prompt 模板（后端维护）

```text
你是一位精通中国传统命理和西方星座的大师。
用户信息：生日 {birthday}，出生时辰 {birthHour|未知}，性别 {gender}，职业：演员。
当前月份：{currentMonth}。

请根据以上信息，以 JSON 格式返回以下内容：
{
  "zodiacAnimal": "生肖英文 key",
  "zodiacFortune": { "keyword": "两字关键词", "readings": ["运势1", "运势2", "运势3"] },
  "constellation": "星座英文 key",
  "constellationFortune": { "keyword": "两字关键词", "readings": ["运势1", "运势2", "运势3"] },
  "ziweiStar": "紫微主星英文 key",
  "ziweiProfile": { "trait": "两个性格特质", "monthlyAdvice": "本月建议，与演艺行业相关" },
  "luckyColor": "#hex色值",
  "luckyColorName": "颜色中文名",
  "luckyColorInterpretation": "一句话解读，与演艺事业相关",
  "luckyNumber": 数字,
  "luckyNumberInterpretation": "一句话解读"
}

要求：
- 运势内容与演员职业相关，涉及试镜、拍摄、表演等场景
- 幸运色要适合作为个人名片主色调
- 紫微主星如无时辰则以午时推算
- 每条运势不超过 30 字
```

### 5.2 调用策略

- 每月 1 日凌晨批量为活跃用户生成（定时任务）
- 首次访问命理页时按需生成（如未生成）
- 结果缓存在 `fortune_report` 表，当月内不重复调用
- 大模型接口调用失败时，使用规则引擎兜底（生肖/星座由规则表查，幸运色随机预设）

## 6. 接口清单

| 接口 | 方法 | 说明 | 鉴权 |
|------|------|------|------|
| `/api/fortune/report` | GET | 获取当月命理报告（无则触发生成） | 需登录 |
| `/api/fortune/apply-lucky-color` | POST | 应用幸运色到名片配色 | 需登录，Lv5 |
| `/api/actor/profile` | PATCH | 补填出生时辰 `birthHour` | 需登录 |

## 7. 包体控制

- 命理页在 `pkg-card` 分包下：`pkg-card/fortune/index`
- 生肖/星座图标使用 emoji 或 CDN 图片，不打包 icon 资源
- 无额外重型依赖

## 8. 验收标准

- [ ] 根据生日自动推算生肖和星座
- [ ] 命理报告页展示完整（幸运色/数字 + 生肖 + 星座 + 紫微主星）
- [ ] 幸运色可一键应用到名片（Lv5 限制生效）
- [ ] Lv1-Lv4 可查看基础信息但不能应用幸运色到名片
- [ ] 报告按月缓存，当月不重复调用大模型
- [ ] AI 调用失败时规则兜底正常
- [ ] `npm run build:mp-weixin` 通过，模块在 `pkg-card` 分包内
