# 00-63 设计说明

## 1. 设计原则

- 不再继续靠“这个页面补一下、那个页面补一下”修分享最新态
- 让 `ActorProfile` 与 `UserShareCard` 的展示职责显式分层
- 让公开页和编辑页至少共享同一条最新态读取入口
- 失败时显式暴露错误，不再静默回退到错误用户或旧摘要

## 2. 调查结论

### 2.1 已确认不是主因的部分

- `pages/actor-profile/edit` 的保存请求 `PUT /api/actor/profile` 已直接落到后端 `ActorProfileServiceImpl.saveProfile(...)`
- `pkg-card/actor-card/index` 的保存请求 `POST /api/card/config` 已直接落到后端 `ActorCardConfigServiceImpl.saveActorConfig(...)`
- 后端保存分享卡配置时已经会把 `latest_config_id` 重新绑定回 `user_share_card`

因此当前问题不能继续简单归因为“保存没进库”。

### 2.2 已确认的主因

1. **前端读取链路重复实现**
   - `pages/actor-profile/detail`
   - `pkg-card/actor-card/index`
   都各自写了一套“拉 personalization -> 拉 actor detail -> 派生 summary/theme”的逻辑。
   这种重复实现导致一个页面修了，另一个页面很容易继续漏字段或漏刷新。

2. **公开页曾长期没有完整消费最新 shareCard 配置**
   公开页此前主要围绕通用 `ActorProfile` 摘要展示，虽然底层工具已支持 `highlightedPhotos / highlightedExperiences / tagOrder`，但页面本身没有完整消费，导致“卡片保存成功但公开页没变化”。

3. **编辑后刷新语义依赖页面各自 onShow / hydrate，自然容易分叉**
   当前“编辑完回到上一页”后是否刷新最新态，主要由每个页面自己决定。只要某一页少拉一个接口、少回填一个字段，用户就会感觉“保存了但没更新”。

## 3. 设计策略

### 3.1 建立共享最新态加载入口

新增前端共享 helper，统一完成以下动作：

```text
shareCardId
  -> /api/card/personalization
  -> 解析 actorId
  -> /api/actor/{actorId}
  -> buildCardConfigFromPersonalization(profile)
  -> 返回 detail / actor-card 共用的 latest snapshot
```

共享入口输出字段：

- `shareCardId`
- `actorId`
- `actor`
- `personalization`
- `cardConfig`
- `sceneKey`
- `theme`

这样 `detail` 与 `actor-card` 不再各写一套最新态读取流程。

### 3.2 页面职责

#### `pages/actor-profile/detail`

- 作为**公开分享页**
- 只消费共享 latest snapshot，再派生：
  - `displayTags`
  - `displayExperiences`
  - `displayPhotos`
  - `detailLayoutClass`
- 通用资料来自 `actor`
- 展示配置来自 `cardConfig`

#### `pkg-card/actor-card/index`

- 作为**单卡编辑 / 预览页**
- 加载时与 `detail` 共用同一 latest snapshot
- `onShow` 回前台后再次走同一 latest snapshot，确保从档案编辑页返回时能看到最新资料
- 保存分享卡配置后，再次走同一 latest snapshot，避免页面只更新局部响应

### 3.3 刷新策略

#### 3.3.1 档案编辑返回

```text
pages/actor-profile/edit 保存成功
  -> 返回上一页
  -> 上一页 onShow
  -> 重新走 latest snapshot loader
```

#### 3.3.2 分享卡配置保存

```text
pkg-card/actor-card 保存成功
  -> 再次拉 latest snapshot
  -> 更新当前页展示
  -> 后续公开页再次进入也走 latest snapshot
```

#### 3.3.3 分享出去再次打开

```text
分享路径仅携带 shareCardId
  -> 页面打开时重新拉 latest snapshot
  -> 不缓存旧档案内容和旧卡片配置
```

## 4. 错误处理边界

- 若缺少 `shareCardId`：直接提示“缺少分享卡主键”
- 若 `personalization` 无法解析出 `actorId`：直接提示“分享卡片缺少持卡人”
- 若 latest snapshot 任一主链失败：页面应显式提示加载失败，而不是静默绑定到当前登录用户自己的档案

## 5. 影响文件

- `.sce/specs/README.md`
- `.sce/specs/spec-code-mapping.md`
- `.sce/specs/00-28-architecture-driven-delivery-governance/tasks.md`
- `.sce/specs/00-28-architecture-driven-delivery-governance/status/overall-architecture-assessment.md`
- `.sce/specs/00-28-architecture-driven-delivery-governance/status/share-card-mvp-status.md`
- `kaipai-frontend/src/utils/share-card-latest.ts`（新增）
- `kaipai-frontend/src/pages/actor-profile/detail.vue`
- `kaipai-frontend/src/pkg-card/actor-card/index.vue`

## 6. 本轮不扩大设计

- 不新增后端分享快照表
- 不在本轮引入版本化发布态
- 不把公开页和编辑页完全合并成同一个页面
- 不恢复 `actorId + sceneKey` 作为主读取键
