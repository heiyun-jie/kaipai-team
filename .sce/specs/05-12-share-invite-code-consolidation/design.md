# 05-12 分享链路邀请码收口 - 技术设计

_Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6_

## 1. 影响范围

| 域 | 页面 / 模块 | 现状 | 本轮目标 |
|------|------|------|------|
| 小程序分享页 | `src/pkg-card/actor-card/index.vue` | 自带邀请码概览卡和复制邀请码动作 | 移除 raw invite code 展示，保留去邀请页 / 分享产物入口 |
| 小程序等级中心 | `src/pkg-card/membership/index.vue` | 仍复用邀请码概览卡；已部分改成邀请页入口 | 进一步收口为“入口 / 统计”视图，不展示 raw invite code |
| 小程序邀请页 | `src/pkg-card/invite/index.vue` | 已承担邀请码 / 链接 / 海报 / 记录闭环 | 保留为前台唯一邀请码操作页 |
| 共享组件 | `src/components/KpInviteSummaryCard.vue` | 默认把邀请码当作主视觉输出 | 改成可区分分享态 / 邀请治理态 |
| 共享工具 | `src/utils/invite.ts` / `src/utils/share-artifact.ts` | 已负责邀请路径和分享产物路径解析 | 继续作为单一来源，禁止页面散落拼接 |
| 后台治理 | `kaipai-admin/src/views/referral/*.vue` | 运营按邀请码审核 / 查询 / 处理 | 保持不动，仅在 Spec 中明确边界 |

## 2. 路由与页面边界

### 2.1 前台边界

- `pkg-card/actor-card/index`
  - 负责场景名片预览、分享产物切换、公开页 / 海报 / 邀请卡片的统一分享入口。
  - 不再负责展示 raw invite code。
- `pkg-card/membership/index`
  - 负责能力说明、等级 / 会员状态、邀请统计入口。
  - 不再负责展示 raw invite code。
- `pkg-card/invite/index`
  - 唯一负责邀请码、邀请链接、海报、分享给好友、邀请记录。

### 2.2 后台边界

- `kaipai-admin/src/views/referral/RiskView.vue`
- `kaipai-admin/src/views/referral/EligibilityView.vue`
- `kaipai-admin/src/views/referral/PoliciesView.vue`
- `kaipai-admin/src/types/referral.ts`

这些页面和类型继续保留邀请码字段，因为它们属于治理域，不属于前台分享展示域。

## 3. 组件口径重构

### 3.1 `KpInviteSummaryCard` 的现状问题

当前组件默认展示：

- 邀请码文案
- raw invite code
- secondary action（通常是复制邀请码）
- primary action（通常是刷新 / 去邀请）

这导致 `actor-card`、`membership` 只要复用该组件，就会被动把邀请码暴露到非邀请专页。

### 3.2 重构方向

两种可接受实现，最终以更少重复逻辑为准：

1. 在 `KpInviteSummaryCard` 中新增显式 props：
   - `showInviteCode?: boolean`
   - `showSecondaryAction?: boolean`
   - 默认值按“前台分享态”更安全地关闭
2. 将组件拆成：
   - `KpInviteStatsCard`：只展示统计 / 状态 / 入口
   - `KpInviteSummaryCard`：保留给 `pkg-card/invite/index`

### 3.3 页面使用约束

- `actor-card` 只能使用“无邀请码展示”的版本。
- `membership` 只能使用“无邀请码展示”的版本。
- `invite/index` 才能使用“展示邀请码 + 复制 + 邀请动作”的版本。

## 4. 页面改造方案

### 4.1 `pkg-card/actor-card/index`

_Requirements: 3.1, 3.2, 3.4_

当前问题：

- 自己的名片页里存在 `KpInviteSummaryCard`
- 同时有 `copyInviteCode()` 与 `handleInviteAction()`
- 与 `selectedArtifact === 'inviteCard'` 的统一分享模型重复

改造要求：

- 删除 self-only 邀请码概览卡中的 raw invite code 展示与复制动作。
- 如果仍保留邀请引导区，只保留：
  - 去邀请页
  - 切换到 `inviteCard` 产物
  - 说明邀请链路已独立
- `copyInviteCode()` 从该页移除。
- `handleInviteAction()` 统一跳转 `/pkg-card/invite/index`，必要时带上 `artifact=inviteCard`、`actorId`、`scene`、`tone`。

### 4.2 `pkg-card/membership/index`

_Requirements: 3.1, 3.2, 3.3_

当前问题：

- 页面虽然已经把底部 action 收口为去邀请页，但主体概览仍可能展示 raw invite code。

改造要求：

- 页面仅保留邀请统计、等级进度和去邀请页入口。
- raw invite code 不再作为等级中心主视觉信息出现。
- 两个底部动作继续统一导向：
  - `/pkg-card/invite/index?artifact=inviteCard`
  - `/pkg-card/invite/index?artifact=poster`

### 4.3 `pkg-card/invite/index`

_Requirements: 3.2, 3.3, 3.4_

保留职责：

- 展示 raw invite code
- 复制邀请码
- 复制邀请链接
- 保存邀请海报
- `open-type="share"` 分享给好友
- 查看邀请记录

增强要求：

- 明确接收来自 `actor-card` / `membership` 的 `artifact` 入参。
- 页面内部继续使用共享工具恢复分享产物状态，不额外复制一套路径规则。

## 5. 共享路径与状态收口

### 5.1 `utils/invite.ts`

负责：

- 邀请码标准化
- 邀请落点路径 `buildInvitePath`
- 邀请分享 state `setInviteShareState`
- 邀请码从 launch options 恢复

不得由页面重复实现：

- `inviteCode` query 的恢复规则
- 邀请路径 query patch 规则

### 5.2 `utils/share-artifact.ts`

负责：

- `inviteCard` 产物路径统一解析
- 从 share artifact 恢复到 `pkg-card/invite/index`
- `artifact / scene / tone / actorId / themeId / shared` 的标准 query 组合

不得由页面重复实现：

- `selectedArtifact === 'inviteCard'` 时的局部路径拼接变体

## 6. 数据与鉴权约束

_Requirements: 3.2, 3.4_

- 需要邀请详情的页面必须先建立登录会话，再请求 `ensureInviteInfo()`。
- `actor-card` / `membership` 在不展示 raw invite code 后，应尽量避免为了展示邀请码而额外拉取 `ensureInviteInfo()`。
- 仅 `invite/index` 需要承担邀请码详情拉取和复制动作。

## 7. 后台治理保留策略

_Requirements: 3.5_

后台不做产品语义调整，仅做边界声明：

- `inviteCode` 在后台是治理字段，不是分享文案字段。
- 风险审核、资格发放、策略配置、详情侧栏继续保留 `inviteCode`。
- 本轮前台清理不要求后台隐藏 `inviteCode`，也不要求调整数据库模型。

## 8. 验证策略

_Requirements: 3.1, 3.2, 3.6_

### 8.1 小程序页面验证

- `pkg-card/actor-card/index`
  - 不再出现邀请码文案 / 复制邀请码按钮
- `pkg-card/membership/index`
  - 不再出现邀请码文案 / 复制邀请码按钮
- `pkg-card/invite/index`
  - 仍能展示邀请码、复制邀请码、保存海报、分享给好友

### 8.2 后台页面验证

- `referral/RiskView`
- `referral/EligibilityView`
- `referral/PoliciesView`

确认邀请码筛选 / 详情字段未因前台收口而被误删。

### 8.3 文档追溯

- `.sce/specs/README.md` 已新增本 Spec 索引
- `.sce/specs/spec-code-mapping.md` 已新增本 Spec ↔ 影响文件映射
