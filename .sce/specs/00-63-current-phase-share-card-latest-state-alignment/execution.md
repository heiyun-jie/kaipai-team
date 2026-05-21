# 00-63 执行记录

## 1. 调查结论

- 当前问题已确认不能再简单归因为“后端没保存”
- `pages/actor-profile/edit -> PUT /api/actor/profile -> ActorProfileServiceImpl.saveProfile(...)` 链路本身存在
- `pkg-card/actor-card/index -> POST /api/card/config -> ActorCardConfigServiceImpl.saveActorConfig(...)` 链路本身存在，且会回绑 `user_share_card.latest_config_id`
- 真正的结构性问题是：
  - `pages/actor-profile/detail` 与 `pkg-card/actor-card/index` 各自维护一套 latest-state 读取逻辑
  - 公开页此前没有完整消费 shareCard 最新配置
  - 编辑后回到分享页是否重新读取后端最新态，仍依赖页面各自分散实现

## 2. 本轮落地

- 新增 `00-63` Spec，正式把“分享页最新态对齐”提升为独立治理入口
- 设计上把前端主读取链收口为共享 latest snapshot loader
- 约束公开页继续显式区分：
  - 通用资料来自 `ActorProfile`
  - 卡片展示配置来自 `UserShareCard / personalization.customConfig`
- 新增 `kaipai-frontend/src/utils/share-card-latest.ts`，统一执行：
  - `shareCardId -> /api/card/personalization`
  - `personalization.profile.actorId -> /api/actor/{actorId}`
  - `buildCardConfigFromPersonalization(...)`
- `kaipai-frontend/src/pages/actor-profile/detail.vue` 已改为直接消费共享 latest snapshot，不再自己维护一套 personalization/detail 拼装链
- `kaipai-frontend/src/pkg-card/actor-card/index.vue` 已改为：
  - 首次进入走共享 latest snapshot
  - `onShow` 回前台后走共享 latest snapshot
  - 保存分享配置成功后再次走共享 latest snapshot

## 3. 验证

- 已执行 `kaipai-frontend npm run type-check`，通过
- 已执行 `kaipai-frontend npm run build:mp-weixin`，通过
- 已复核源码与构建产物：
  - `src/pages/actor-profile/detail.vue` 与 `src/pkg-card/actor-card/index.vue` 都已引用 `src/utils/share-card-latest.ts`
  - `dist/build/mp-weixin/utils/share-card-latest.js` 与 `dist/dev/mp-weixin/utils/share-card-latest.js` 已生成
  - `dist/build/mp-weixin/pages/actor-profile/detail.js` 与 `dist/dev/mp-weixin/pages/actor-profile/detail.js` 已切到共享 latest snapshot 读取链
  - `dist/build/mp-weixin/pkg-card/actor-card/index.js` 与 `dist/dev/mp-weixin/pkg-card/actor-card/index.js` 已切到共享 latest snapshot 读取链

## 4. Spec 回填

- 已完成：
  - `.sce/specs/README.md`
  - `.sce/specs/spec-code-mapping.md`
  - `00-28/tasks.md`
  - `00-28/status/overall-architecture-assessment.md`
  - `00-28/status/share-card-mvp-status.md`
