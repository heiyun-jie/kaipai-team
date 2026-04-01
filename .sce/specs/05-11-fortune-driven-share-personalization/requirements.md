# 05-11 命理驱动的分享定制主线（Fortune-driven Share Personalization）

> 状态：架构治理中 | 优先级：最高 | 依赖：05-05 v2、05-08、05-09、05-10
> 关系说明：本 Spec 不替代实名认证、邀请裂变、等级计算等既有能力，但会重新定义它们在“名片分享主线”中的职责边界。

## 1. 功能概述

产品主线从“场景名片 + 等级能力”继续升级为“命理驱动的千人千面分享链路”。

核心变化：

1. 命理不再是孤立页面，而是全链路个性化的数据源
2. 会员不再只控制某个页面入口，而是控制分享产物能力深度
3. 名片分享不再只看 `actor-card` 页面，而是统一治理小程序分享卡片、海报、公开名片页、邀请卡片
4. 分享进入后的名片页、海报和卡片视觉必须保持同一套用户主题

## 2. 当前架构缺口

### 2.1 当前已具备

- 已有 `scene` 场景名片
- 已有实名认证 / 邀请裂变 / 等级体系基础能力
- 已有命理报告页和幸运色应用入口
- 已有小程序名片页、等级中心页、邀请页

### 2.2 当前不足

- 命理仍以独立页面存在，没有成为全链路主题源
- 会员能力仍偏页面级，不是产物级控制
- 小程序分享卡片、海报、公开名片页、邀请卡片没有统一的主题决策链
- `pkg-card/membership/index`、`pkg-card/fortune/index` 的职责边界未重新收敛
- 当前分享链路无法支撑“千人千面”的统一定制

## 3. 产品边界

### 3.1 本轮范围

- 建立命理驱动的个性化主模型
- 建立统一的主题解析和分享产物解析模型
- 重定义会员能力边界
- 重构名片主页面、等级中心、命理页、邀请页的职责分工
- 明确公开分享进入链路的定制化要求

### 3.2 不在本轮范围

- 真实会员支付 / 订单 / 续费链路
- 命理 AI 模型实现细节
- 海报设计后台 CMS
- 剧组端业务扩展

## 4. 需求清单

### 4.1 个性化主模型

- **R1** 前端必须引入统一的 `PersonalizationProfile`，聚合用户等级、会员态、命理结果、模板能力、分享偏好
- **R2** `PersonalizationProfile` 必须成为名片页、海报、分享卡片、邀请卡片的共同输入源
- **R3** 命理数据至少覆盖：幸运色、命理标签、视觉倾向、推荐文案语气
- **R4** 任何个性化展示都不得在页面内部各自拼接零散规则，必须经过统一解析层

### 4.2 命理角色重定义

- **R5** `pkg-card/fortune/index` 不再作为孤立业务终点页
- **R6** 命理页调整为“个性化说明 / 配置 / 预览”页面，职责是解释命理结果并允许用户应用到名片体系
- **R7** 命理结果必须可被名片页、海报、分享卡片、邀请卡片消费
- **R8** 命理能力对非会员默认只展示基础解释；深度个性化应用由会员能力控制

### 4.3 会员能力重定义

- **R9** 会员体系必须独立于邀请等级存在
- **R10** 等级体系继续承担成长和解锁节奏，会员体系承担高级定制和商业化能力
- **R11** 非会员只能使用基础名片页面和基础名片分享
- **R12** 会员用户才可使用深度定制能力，包括但不限于命理驱动主题、定制海报、定制小程序分享卡片、定制邀请卡片
- **R13** 会员能力控制必须精确到分享产物维度，而不是“能不能进入某个页面”

### 4.4 分享产物治理

- **R14** 必须显式定义分享产物类型：
  - `miniProgramCard`
  - `poster`
  - `publicCardPage`
  - `inviteCard`
- **R15** 所有分享产物都必须从同一主题解析结果派生
- **R16** 小程序分享卡片标题、封面、摘要文案必须支持按用户个性化输出
- **R17** 海报必须支持按用户主题生成，且与公开名片页视觉一致
- **R18** 邀请页和邀请海报必须进入同一分享产物体系，不允许独立维护另一套视觉逻辑
- **R19** 分享进入后的公开名片页必须恢复该用户的个性化主题，而不是退回默认模板

### 4.5 主题治理

- **R20** 前端必须建立统一 `ThemeResolver`
- **R21** `ThemeResolver` 至少输出：颜色、字体层级、按钮样式、背景纹理、装饰元素、文案语气标签
- **R22** 主题结果必须同时支持页面 UI 和分享产物 UI 复用
- **R23** 主题配置来源必须支持后端模板下发，前端不得硬编码完整模板库
- **R24** 命理仅作为主题决策输入之一，不能直接散落在页面样式逻辑中

### 4.6 页面职责重构

- **R25** `pkg-card/actor-card/index` 必须成为个性化名片主战场，负责预览、分享和产物生成入口
- **R26** `pkg-card/membership/index` 必须收敛为“能力中心”，负责解释会员与等级分别解锁了什么
- **R27** `pkg-card/fortune/index` 必须收敛为“命理解释与应用中心”，不承担孤立业务闭环
- **R28** `pkg-card/invite/index` 必须改为个性化邀请载体，消费同一主题和能力控制结果
- **R29** `pages/actor-profile/detail` 必须继续承担公开分享落地页职责，但展示风格受个性化主题控制

### 4.7 复用与包体约束

- **R30** 所有跨页面复用的 UI 片段必须抽为 `Kp` 前缀共享组件，禁止在页面中复制相同 UI 结构
- **R31** 色盘选择器、等级进度条、邀请摘要卡片、分享产物选择器等复用片段必须登记到 `00-02`
- **R32** 所有新增页面和重构页面默认继续放在 `pkg-card` 分包
- **R33** 开发时必须持续控制单包体积，小程序单包不得超过 2 MB

### 4.8 安全与接口边界

- **R34** 身份证号必须后端加密存储，前端只展示脱敏值
- **R35** 模板、主题配置、会员能力、命理结果优先通过后端接口下发
- **R36** AI 相关能力统一走后端封装，前端不直连大模型

## 5. 核心数据模型

```ts
type ShareArtifactType = 'miniProgramCard' | 'poster' | 'publicCardPage' | 'inviteCard'

interface PersonalizationProfile {
  actorId: number
  level: UserLevel
  membershipTier: 'none' | 'member' | 'vip'
  fortune: {
    luckyColor?: string
    keywords: string[]
    tone?: 'gentle' | 'sharp' | 'bright' | 'calm'
  }
  sceneKey: CardScene
  templateId?: string
  sharePreferences: {
    preferredArtifact: ShareArtifactType
    enableFortuneTheme: boolean
  }
}

interface ThemeTokenSet {
  themeId: string
  primary: string
  accent: string
  background: string
  surface: string
  textPrimary: string
  textSecondary: string
  buttonStyle: 'solid' | 'glass' | 'outline'
  mood: 'classic' | 'cinematic' | 'modern' | 'airy'
  posterPreset: string
  cardPreset: string
}

interface CapabilityGateResult {
  canUseBasicCard: boolean
  canUsePersonalizedTheme: boolean
  canUseCustomMiniProgramCard: boolean
  canUseCustomPoster: boolean
  canUseCustomInviteCard: boolean
  canApplyFortuneTheme: boolean
}
```

## 6. 验收标准

- [ ] 已形成统一的 `PersonalizationProfile` / `ThemeResolver` / `ShareArtifactResolver` 设计基线
- [ ] 明确区分等级能力与会员能力
- [ ] 非会员只保留基础名片页和基础名片分享
- [ ] 命理页不再被定义为孤立终点页
- [ ] 分享进入名片页、海报、小程序分享卡片、邀请卡片均纳入统一产物模型
- [ ] 公开名片页支持恢复用户个性化主题
- [ ] 复用 UI 组件纳入 `00-02` 约束，禁止新增跨页面重复块
- [ ] 包体和接口边界约束在 Spec 中明确
