# 05-11 命理驱动的分享定制主线 - 技术设计

_Requirements: 05-11 全部_

## 1. 设计目标

05-11 的目标不是增加一个新页面，而是把当前零散的名片、命理、邀请、会员逻辑收敛为统一的个性化分享架构。

本轮设计要解决三件事：

1. 建立个性化主模型，避免页面内散落规则
2. 建立统一主题解析链，支撑千人千面
3. 建立产物级能力控制，区分基础用户和会员用户

## 2. 模块分层

| 层级 | 模块 | 职责 |
|------|------|------|
| 数据聚合层 | `api/level.ts` `api/fortune.ts` `api/invite.ts` `api/verify.ts` `api/personalization.ts` | 获取等级、会员态、命理结果、模板配置、分享配置 |
| 领域模型层 | `types/level.ts` `types/fortune.ts` `types/invite.ts` `types/personalization.ts` | 定义个性化主模型、能力矩阵、分享产物模型 |
| 解析层 | `utils/personalization.ts` `utils/theme-resolver.ts` `utils/share-artifact.ts` | 聚合 profile、解析主题、解析分享产物 |
| 页面层 | `pkg-card/actor-card/index.vue` `pkg-card/membership/index.vue` `pkg-card/fortune/index.vue` `pkg-card/invite/index.vue` `pages/actor-profile/detail.vue` | 消费统一解析结果，不直接拼装底层规则 |
| 共享 UI 层 | `src/components/Kp*.vue` | 承载跨页面复用视觉片段 |

## 3. 核心类型设计

### 3.1 个性化主模型

```ts
type MembershipTier = 'none' | 'member' | 'vip'
type PersonalizationTone = 'gentle' | 'sharp' | 'bright' | 'calm'

interface PersonalizationProfile {
  actorId: number
  levelInfo: UserLevelInfo
  membershipTier: MembershipTier
  sceneKey: CardScene
  templateId?: string
  fortuneProfile: {
    luckyColor?: string
    keywords: string[]
    tone?: PersonalizationTone
    visualTags: string[]
  }
  customConfig?: ActorCardConfig
  sharePreferences: {
    preferredArtifact: ShareArtifactType
    enableFortuneTheme: boolean
    preferredTone?: 'natural' | 'professional' | 'commercial'
  }
}
```

### 3.2 分享产物模型

```ts
type ShareArtifactType = 'miniProgramCard' | 'poster' | 'publicCardPage' | 'inviteCard'

interface ShareArtifact {
  type: ShareArtifactType
  title: string
  subtitle?: string
  coverImage?: string
  path?: string
  theme: ThemeTokenSet
  capability: CapabilityGateResult
}
```

### 3.3 能力控制模型

```ts
interface CapabilityGateResult {
  canUseBasicCard: boolean
  canUsePersonalizedTheme: boolean
  canUseCustomMiniProgramCard: boolean
  canUseCustomPoster: boolean
  canUseCustomInviteCard: boolean
  canApplyFortuneTheme: boolean
  reasonCodes: string[]
}
```

## 4. 解析器设计

### 4.1 `utils/personalization.ts`

职责：

- 聚合等级、会员态、命理、模板配置、自定义配置
- 输出统一 `PersonalizationProfile`
- 为页面层屏蔽接口组合细节

建议导出：

```ts
async function resolvePersonalizationProfile(actorId: number, sceneKey: CardScene): Promise<PersonalizationProfile>
function mergeSharePreferences(profile: PersonalizationProfile, overrides?: Partial<PersonalizationProfile['sharePreferences']>): PersonalizationProfile
```

### 4.2 `utils/theme-resolver.ts`

职责：

- 基于 `PersonalizationProfile` 和模板配置输出 `ThemeTokenSet`
- 统一页面态、海报态、分享卡片态的主题

建议导出：

```ts
function resolveThemeTokens(profile: PersonalizationProfile, template: SceneTemplate): ThemeTokenSet
function resolveFortuneThemeSeed(profile: PersonalizationProfile): Partial<ThemeTokenSet>
```

规则：

1. 先取后端模板基础 token
2. 再叠加用户自定义配置
3. 若会员能力允许，再叠加命理主题种子
4. 最终输出给页面和分享产物共用

### 4.3 `utils/share-artifact.ts`

职责：

- 明确每一种分享产物的构造逻辑
- 避免页面里各自生成海报标题、分享摘要、封面配置

建议导出：

```ts
function resolveCapabilityGate(profile: PersonalizationProfile): CapabilityGateResult
function resolveShareArtifact(type: ShareArtifactType, profile: PersonalizationProfile, theme: ThemeTokenSet): ShareArtifact
function buildActorCardSharePath(profile: PersonalizationProfile): string
```

## 5. 页面职责调整

### 5.1 `pkg-card/actor-card/index.vue`

调整后职责：

- 名片主预览页
- 场景切换、主题预览、分享产物入口
- 预览“基础版”与“会员版”差异
- 不再自行拼接命理和分享逻辑，改为消费 resolver 输出

页面结构建议：

1. 顶部固定返回与分享控制
2. 当前主题摘要区
3. 名片主视觉区
4. 分享产物切换区
5. 能力提示区

### 5.2 `pkg-card/membership/index.vue`

调整后职责：

- 解释等级能力与会员能力的区别
- 展示当前已解锁与未解锁的分享产物能力
- 提供升级入口和能力说明
- 邀请信息卡只保留摘要，不在卡内复制页面底部主操作按钮

不再承担：

- 独立拼装名片主题预览逻辑
- 独立维护另一套邀请卡视觉样式

会员页 UI 节奏要求：

- 顶部 Hero 下方的内容区按统一纵向节奏堆叠，默认卡片间距使用 `$kp-spacing-gap`
- 实名认证卡中的说明文案到“去认证”按钮，使用 `$kp-spacing-page`
- 邀请摘要卡只展示邀请码与状态说明；“复制邀请码 / 查看邀请记录”收敛到页面底部悬浮操作栏
- 页面存在固定底部操作栏时，内容区必须预留安全高度，避免最后一张卡片被遮挡

### 5.3 `pkg-card/fortune/index.vue`

调整后职责：

- 展示命理结果和本期推荐主题
- 提供“应用到我的名片”与“预览分享效果”能力
- 说明当前会员态可用的命理定制深度

不再承担：

- 孤立业务闭环页面
- 与名片体系脱节的独立视觉体系

### 5.4 `pkg-card/invite/index.vue`

调整后职责：

- 展示邀请摘要
- 预览邀请卡片/邀请海报
- 复用与名片主线相同的主题 token

### 5.5 `pages/actor-profile/detail.vue`

调整后职责：

- 作为公开分享落地页
- 通过分享参数恢复用户场景与主题
- 不展示后台管理控件

## 6. 分享链路

### 6.1 统一流程

```text
用户配置/进入名片页
  -> resolvePersonalizationProfile
  -> resolveThemeTokens
  -> resolveCapabilityGate
  -> resolveShareArtifact
  -> 输出：
     1. 小程序分享卡片
     2. 海报
     3. 公开名片页
     4. 邀请卡片
```

### 6.2 分享路径要求

基础名片分享路径仍以 `pkg-card/actor-card/index` 为主，但必须补充足够的恢复参数。

建议参数：

```ts
interface ActorCardShareParams {
  actorId: number
  scene: CardScene
  shared: '1'
  artifact?: ShareArtifactType
  themeId?: string
  tone?: 'natural' | 'professional' | 'commercial'
}
```

规则：

- `themeId` 仅作恢复提示，最终仍以服务端配置 + resolver 为准
- 公开页不得依赖纯前端临时状态恢复最终主题

## 7. 会员与等级能力矩阵

### 7.1 原则

- 等级控制成长节奏、基础场景解锁、AI 次数等成长能力
- 会员控制高级定制、命理主题应用、定制分享产物等商业化能力

### 7.2 能力矩阵示例

| 能力 | 非会员 | 会员 |
|------|--------|------|
| 基础名片页 | 是 | 是 |
| 基础小程序分享卡片 | 是 | 是 |
| 命理驱动主题 | 否 | 是 |
| 定制海报 | 否 | 是 |
| 定制分享卡片 | 否 | 是 |
| 定制邀请卡片 | 否 | 是 |
| 深度主题配置 | 否 | 是 |

说明：

- 具体会员等级、价格、文案后续可扩展，但前端结构先按产物级控制建模

## 8. 共享组件约束

本 Spec 涉及的可复用 UI 片段必须抽为共享组件并回填到 `00-02`：

- `KpColorPalettePicker`
- `KpLevelProgressCard`
- `KpInviteSummaryCard`
- 新增规划：
  - `KpShareArtifactTabs`
  - `KpThemePreviewCard`
  - `KpCapabilityMatrixCard`

规则：

- 页面内不允许复制相同按钮组、邀请摘要、能力说明壳层
- 共享组件优先放 `src/components/`

## 9. 包体与落地约束

- 所有新增页面继续进入 `pkg-card`
- 不引入重型图形编辑器依赖
- 模板素材和分享底图走后端或 CDN
- 每轮实现后必须执行：
  - `npm run build:mp-weixin`
  - `npm run audit:mp-package`

## 10. 对既有 Spec 的约束关系

- 05-05 继续负责名片分享、等级体系、场景名片基础实现，但后续重构必须服从 05-11 的个性化主模型和能力模型
- 05-08 继续负责命理数据来源和解释页，但其产品定位改为“个性化输入源”，不再是孤立终点功能
- 05-10 继续负责邀请关系和数据来源，但邀请卡视觉与分享产物逻辑必须并入 05-11
