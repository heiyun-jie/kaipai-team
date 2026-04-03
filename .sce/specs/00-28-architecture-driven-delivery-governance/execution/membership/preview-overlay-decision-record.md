# Preview Overlay 决策记录

## 1. 结论

- 决策日期：`2026-04-03`
- 当前决策：`保持 session-only，不升级为后端临时摘要`

## 2. 证据依据

### 2.1 已有正向证据

- `run-preview-overlay-static-audit.py` 已证明 overlay 结构边界没有扩散；当前只命中：
  - `src/utils/personalization.ts`
  - `src/types/personalization.ts`
  - `src/pkg-card/actor-card/index.vue`
  - `src/pages/actor-profile/detail.vue`
  - `src/pkg-card/invite/index.vue`
- `run-admin-template-rollback-mini-program-no-fortune-theme.py` 最新样本已证明：
  - `actor-card / detail / invite` 都能在同一设备会话内恢复到正确模板视觉
  - rollback / restore 的视觉变化已经不再依赖 overlay path patch
- 当前运行时代码事实已进一步收口：
  - `patchPathWithPersonalizationPreviewOverlay` 已退场
  - `readPersonalizationPreviewOverlay` 与四个 overlay query key 已退场
  - overlay query 兼容读取已全部退场
  - `invite` 已只读取 session overlay

### 2.2 当前仍缺失的升级触发证据

- 没有证据表明同一份未保存预览需要跨登录恢复
- 没有证据表明同一份未保存预览需要跨设备恢复
- 没有证据表明 overlay 已扩展到模板、artifact、capability 等后端事实字段
- 没有证据表明当前 session-only 方案已经破坏 rollback、分享落点或运营回查

## 3. 为什么现在不升级后端

当前若直接把 overlay 升级成后端临时摘要，会引入新的创建、读取、失效、清理与权限边界，但现在缺少能证明这组改造必要性的真实样本。

因此当前继续升级，收益不确定，反而会把 membership 从“已可审计的边界问题”重新改回“更大结构变更但证据不足”。

## 4. 当前允许的实现边界

- overlay 只允许覆盖未保存的 `layoutVariant / primaryColor / accentColor / backgroundColor`
- overlay 只允许保留在当前设备 session
- overlay 只允许用于 `actor-card / detail / invite` 的同 actor、同 scene 预览恢复
- 真实分享 path 不允许继续写入 overlay query，页面运行时也不再兼容读取 overlay query

## 5. 重新开启升级讨论的门禁

满足以下任一条，才重新开启“升级为后端临时摘要”的实现：

1. 新样本证明同一份未保存预览必须跨登录恢复
2. 新样本证明同一份未保存预览必须跨设备或跨端恢复
3. overlay 字段扩展到模板、artifact、会员能力或其它后端事实
4. session-only 方案已导致真实分享落点、审核链或运营回查出现错误

## 6. 后续动作

- 短期动作：继续用 `run-preview-overlay-static-audit.py` 约束边界，不再新增 overlay path patch
- 中期动作：继续观察 invite / login-auth / membership 的真实样本，只有出现新的跨端恢复证据时再升级模型
- 文档动作：`membership-status.md`、`overall-architecture-assessment.md`、`phase-01-roadmap.md` 统一引用本记录，不再反复口头讨论
