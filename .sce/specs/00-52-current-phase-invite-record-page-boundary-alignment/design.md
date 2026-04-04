# 00-52 设计说明

## 1. 设计原则

- 以现代码和现产品边界为准，不以旧执行记录倒推现状
- 不删历史能力事实，但把它们移出当前阶段主验收面
- 让 `00-28`、`05-12`、状态卡和索引四处口径一致
- 当前阶段分享产物口径要同时约束“接口返回”“偏好保存”“前端类型解析”，不能只修一层

## 2. 当前阶段页面边界

| 页面 / 模块 | 当前阶段职责 | 不再作为当前阶段职责 |
|-------------|--------------|----------------------|
| `pages/login/index` | 承接 `inviteCode / scene`，把邀请关系带入注册 | 承担 invite 展示页 |
| `src/pkg-card/actor-card/index.vue` | 小程序卡片 / 海报分享入口、邀请记录入口 | 页面内展示 raw invite code |
| `src/pkg-card/membership/index.vue` | 能力摘要、邀请统计、邀请记录入口 | 页面内展示 raw invite code、invite 分享页 |
| `src/pkg-card/invite/index.vue` | 邀请记录、状态、数量摘要 | 邀请码复制、邀请链接复制、海报生成、`open-type="share"` 分享唯一入口 |
| `kaipai-admin/src/views/referral/*` | 后台治理、风险、规则、资格发放 | 前台分享产品语义 |

## 3. 文档对齐策略

### 3.1 `00-28`

- 路线图改写为“invite 当前阶段记录页边界与历史兼容治理收口”
- invite 状态卡改写当前已确认事实、阻塞项和下一步动作
- overall assessment 改写 invite 当前阶段主缺口，不再继续围绕 `inviteLink / qrCodeUrl` 页面态描述
- invite 切片补充 `00-52` 上位 spec，并明确分享入口和记录页分工

### 3.2 `05-12`

- 不抹掉历史收口事实
- 但在顶部明确标记：当前阶段以 `00-52` 为准
- 防止后续继续按“invite 页必须承担海报/复制/分享”错误验收

## 4. Runtime 口径收口

### 4.1 后端响应

- `/api/card/personalization` 的 `artifacts` 当前阶段只返回 `miniProgramCard`、`poster`
- `publicCardPage` 仍允许作为公开名片页独立路径 helper 存在，但不再作为当前阶段 artifact 项下发
- `inviteCard` 不再作为当前阶段分享产物参与 personalization 返回

### 4.2 偏好保存

- `preferredArtifact` 保存前统一归一化到 `miniProgramCard / poster`
- 历史数据库里残留的 `publicCardPage / inviteCard` 在读取时自动回落到 `miniProgramCard`
- 这样可以避免“前端已过滤，保存一次又把旧值写回库里”的假收口

### 4.3 前端口径

- `src/types/personalization.ts` 的当前阶段 `ShareArtifactType` 只保留 `miniProgramCard / poster`
- `src/utils/share-artifact.ts` 继续保留公开名片路径 helper，但不再把 `publicCardPage / inviteCard` 当作当前阶段 artifact 类型参与分支
- `src/utils/personalization.ts` 继续作为真接口模式下的归一化落点，保证后端历史值不会重新扩散到页面层

## 5. 历史兼容处理

- `inviteCard`、`publicCardPage`、后端 artifact path、历史样本目录仍可保留
- 这些内容在当前阶段只算“历史兼容或旧证据”，不算当前产品承诺
- 非当前阶段主线之外的历史样本和旧证据不在本轮批量改写，避免污染历史执行记录

## 6. 影响文件

- `.sce/specs/00-28-architecture-driven-delivery-governance/phase-01-roadmap.md`
- `.sce/specs/00-28-architecture-driven-delivery-governance/tasks.md`
- `.sce/specs/00-28-architecture-driven-delivery-governance/slices/invite-referral-capability-slice.md`
- `.sce/specs/00-28-architecture-driven-delivery-governance/status/invite-status.md`
- `.sce/specs/00-28-architecture-driven-delivery-governance/status/overall-architecture-assessment.md`
- `.sce/specs/05-12-share-invite-code-consolidation/requirements.md`
- `.sce/specs/05-12-share-invite-code-consolidation/design.md`
- `.sce/specs/05-12-share-invite-code-consolidation/tasks.md`
- `.sce/specs/05-12-share-invite-code-consolidation/execution.md`
- `.sce/specs/README.md`
- `.sce/specs/spec-code-mapping.md`
- `kaipaile-server/src/main/java/com/kaipai/module/server/card/service/impl/ActorPersonalizationServiceImpl.java`
- `kaipaile-server/src/main/java/com/kaipai/module/server/card/service/impl/ActorCardConfigServiceImpl.java`
- `kaipaile-server/src/main/java/com/kaipai/module/server/card/support/CurrentPhaseShareArtifactSupport.java`
- `kaipai-frontend/src/types/personalization.ts`
- `kaipai-frontend/src/utils/share-artifact.ts`
- `kaipai-frontend/src/utils/personalization.ts`
