# 00-63 当前阶段分享页最新态对齐（Current Phase Share Card Latest State Alignment）

> 状态：进行中 | 优先级：最高 | 依赖：00-28 architecture-driven-delivery-governance，00-62 current-phase-minimal-share-card-mvp-alignment，05-05 card-share-membership，05-11 fortune-driven-share-personalization
> 记录目的：把“编辑档案 / 编辑分享卡后，公开分享页与分享出去的页面没有稳定读取最新后端状态”的问题从零散补丁升级为独立 Spec，明确事实源、读取链路、刷新策略和代码收口方式，避免同类遗漏反复出现。

## 1. 背景

当前分享主线已经进入 `shareCardId-first` 阶段，但“编辑完成后分享页是否立即显示最新内容”仍多次出现遗漏，问题不再是单点 UI 没改，而是：

- `pages/actor-profile/edit`、`pkg-card/actor-card/index`、`pages/actor-profile/detail` 对“最新态”的理解并未完全统一
- 同一张分享卡的读取逻辑分散在多个页面里，各自手写“个性化 -> 档案 -> 派生展示字段”拼装
- 之前虽然已经修过公开页的部分配置消费问题，但新一轮排查仍暴露出“档案编辑页 / 卡片编辑页 / 公开页”之间容易再次漏接字段或漏刷新的风险

因此需要先把“最新态对齐”独立建成 Spec，再基于它做调查、收口和回归。

## 2. 范围

### 2.1 本轮必须处理

- 固化 `档案编辑 -> 分享页` 的最新态对齐规则
- 固化 `分享卡编辑 -> 公开分享页` 的最新态对齐规则
- 固化 `分享出去后再次打开` 仍应读取最新后端状态的规则
- 收口前端分享页的读取实现，避免多个页面继续各写一套加载逻辑
- 回填 `00-28`、Spec 索引、映射与状态文档

### 2.2 本轮不处理

- 重新设计整个分享产品流程
- 新增新的分享产物类型
- 把所有分享页面一次性重做成全新 UI
- 后端扩展新的“快照版本”或“发布版本”模型

## 3. 需求

### 3.1 最新态事实源

- **R1** `ActorProfile` 必须继续作为通用演员资料的唯一事实源，公开分享页不得再使用页面内缓存或旧预览态替代后端最新档案。
- **R2** `UserShareCard + /api/card/personalization` 必须作为分享卡展示配置的唯一事实源，公开分享页不得继续依赖旧的本地拼装结果展示高亮照片、高亮经历、标签顺序、布局等信息。
- **R3** 公开分享页必须显式区分：
  - 通用资料来自 `ActorProfile`
  - 卡片展示配置来自 `PersonalizationProfile.customConfig`
  不得把两者继续混成“某页自己推出来的摘要”。

### 3.2 编辑后刷新语义

- **R4** 当用户在 `pages/actor-profile/edit` 保存成功后，再次回到分享相关页面时，页面必须重新读取后端最新资料，而不是继续使用进入编辑页前的内存快照。
- **R5** 当用户在 `pkg-card/actor-card/index` 保存分享卡配置成功后，公开分享页必须重新读取后端最新卡片配置，而不是继续展示保存前的派生摘要。
- **R6** 已经分享出去的路径再次打开时，也必须读取后端当前最新状态；分享链接本身不能固化旧档案内容或旧卡片配置。

### 3.3 前端读取链路收口

- **R7** `pages/actor-profile/detail` 与 `pkg-card/actor-card/index` 不得继续各自维护一套“先拉 personalization，再拉 actor detail，再手动拼展示态”的平行实现；必须至少把最新态读取主链收口到共享入口。
- **R8** 共享入口必须返回同一张卡片的最小最新态载荷，至少包含：
  - `shareCardId`
  - `actorId`
  - `ActorProfile`
  - `PersonalizationResolvedResult`
  - `ActorCardConfig`
  - 公开页需要的当前 `scene/theme`
- **R9** 任何分享页若无法获取 `shareCardId` 或无法解析出持卡人，必须显式报错，不得静默回退到错误用户或旧页面状态。

### 3.4 公开页渲染边界

- **R10** `pages/actor-profile/detail` 必须真正消费最新 `shareCard` 配置来渲染代表照片、经历、标签、布局和主题。
- **R11** `pages/actor-profile/detail` 必须继续直接消费最新 `ActorProfile` 来渲染头像、姓名、介绍、城市、年龄、身高、视频与通用档案信息。
- **R12** 若某个档案字段当前不在公开页展示范围内，必须在 Spec 中明确“未展示”，而不是让页面因为遗漏映射而表现得像“没有更新”。

### 3.5 治理回填

- **R13** 本问题必须有独立 Spec、执行记录、索引与映射回填，不能再只停留在聊天解释或零散 commit。
- **R14** `00-28` 与 `share-card-mvp-status` 必须把当前主风险更新为“分享页最新态事实源对齐”，并记录本轮收口方式。

## 4. 验收标准

- [ ] 已新增独立 `00-63` Spec，并登记到索引和映射
- [ ] 已明确区分“档案事实源”和“分享卡配置事实源”
- [ ] 已明确“编辑后回到分享页必须重新拉后端最新态”
- [ ] `pages/actor-profile/detail` 与 `pkg-card/actor-card/index` 的最新态读取主链已收口到共享入口
- [ ] 公开分享页已明确消费最新 `ActorProfile + PersonalizationProfile.customConfig`
- [ ] 已完成最小编译验证与治理文档回填
