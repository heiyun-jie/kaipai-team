# 00-66 执行记录

## 1. 当前状态

- 已停止继续按截图和代码直觉直接修改映射逻辑
- 本轮先转为请求事实调查

## 2. 已完成的代码事实调查

### 2.1 保存链事实

保存入口位于：

- `D:\XM\kaipai-team\kaipai-frontend\src\pkg-card\actor-card\index.vue:552-583`
- `D:\XM\kaipai-team\kaipai-frontend\src\api\level.ts:22-42`

当前编辑页提交 `/api/card/config` 的字段包含：

- `shareCardId`
- `layoutVariant`
- `primaryColor`
- `accentColor`
- `backgroundColor`
- `highlightedExperiences`
- `highlightedPhotos`
- `tagOrder`
- `preferredArtifact`
- `preferredTone`
- `enableFortuneTheme`

后端保存逻辑位于：

- `D:\XM\kaipai-team\kaipaile-server\src\main\java\com\kaipai\module\server\card\service\impl\ActorCardConfigServiceImpl.java:191-224`

当前服务端对三色字段采取“原值落库”：

- `primaryColor -> actor_card_config.primary_color`
- `accentColor -> actor_card_config.accent_color`
- `backgroundColor -> actor_card_config.background_color`

当前代码事实未发现保存链把三色重新算法转换后再入库；颜色保存语义仍是“前端传什么，后端存什么”。

### 2.2 聚合链事实

公开页最新态加载入口位于：

- `D:\XM\kaipai-team\kaipai-frontend\src\utils\share-card-latest.ts:22-56`

实际链路为：

```text
shareCardId
  -> GET /api/card/personalization
  -> profile.actorId
  -> GET /api/actor/{actorId}
  -> 组装 ShareCardLatestSnapshot
```

`/api/card/personalization` 的后端聚合位于：

- `D:\XM\kaipai-team\kaipaile-server\src\main\java\com\kaipai\module\server\card\service\impl\ActorPersonalizationServiceImpl.java:39-81`

聚合结果同时返回两套与颜色相关的数据：

1. 原始配置：
   - `profile.customConfig.primaryColor`
   - `profile.customConfig.accentColor`
   - `profile.customConfig.backgroundColor`
2. 聚合主题：
   - `theme.primary`
   - `theme.accent`
   - `theme.background`
   - `theme.surface`
   - `theme.surfaceStrong`

主题聚合规则位于：

- `D:\XM\kaipai-team\kaipaile-server\src\main\java\com\kaipai\module\server\card\service\impl\ActorPersonalizationServiceImpl.java:130-166`

已确认当前后端主题语义不是三色独立映射，而是：

- `primaryColor` 驱动 `theme.primary`
- `accentColor` 驱动 `theme.accent`
- `backgroundColor` 驱动 `theme.background`
- `theme.surface = primary + "12"`
- `theme.surfaceStrong = primary + "20"`

即当前主题系统是“primary 主导型主题”，而不是“三色一一对应三区域”。

### 2.3 页面消费链事实

公开页消费点位于：

- `D:\XM\kaipai-team\kaipai-frontend\src\pages\actor-profile\detail.vue:193-213`
- `D:\XM\kaipai-team\kaipai-frontend\src\pages\actor-profile\detail.vue:400-414`
- `D:\XM\kaipai-team\kaipai-frontend\src\pages\actor-profile\detail.vue:475-691`

公开页当前分成两条消费链：

1. 内容配置链：
   - `currentCardConfig` 来自 `profile.customConfig`
   - `displayPhotos` / `displayExperiences` / `primaryTags` 通过 `getActorSummary()` 读取 `highlightedPhotos` / `highlightedExperiences` / `tagOrder`
   - 相关代码：
     - `D:\XM\kaipai-team\kaipai-frontend\src\utils\personalization.ts:46-59`
     - `D:\XM\kaipai-team\kaipai-frontend\src\utils\actor-card.ts:153-177`

2. 颜色主题链：
   - 页面没有直接消费后端返回的 `personalization.theme`
   - 而是再次本地调用 `resolveThemeTokens(...)` 重算主题
   - 且当前还把 `enableFortuneTheme` 强制写成 `false`
   - 相关代码：
     - `D:\XM\kaipai-team\kaipai-frontend\src\pages\actor-profile\detail.vue:400-414`
     - `D:\XM\kaipai-team\kaipai-frontend\src\utils\theme-resolver.ts:47-68`

### 2.4 三色字段与公开页实际视觉区域映射

#### primaryColor

当前不仅影响头部渐变起点，还进一步派生：

- `surface`
- `surfaceStrong`
- `--actor-detail-accent`
- `--actor-detail-accent-soft`

因此它实际控制：

- 头部主渐变起点
- 页面背景中后段色阶
- hero 卡片底色层次
- 内容卡片底色层次
- 部分眉标/强调块

#### accentColor

当前主要只参与：

- 头部渐变终点

没有形成独立的强调体系，未稳定控制按钮、标签、卡片边框等区域。

#### backgroundColor

当前主要只参与：

- 页面最底层背景起点

但因为页面背景是：

```text
backgroundColor -> background 0%
surface -> 42%
surfaceStrong -> 100%
```

后两段又来自 `primaryColor`，因此背景色视觉权重明显弱于主色。

## 3. 当前结论

- 保存链当前从代码上看是直存三色字段，不是根因优先嫌疑。
- 聚合链当前明确把主题实现成“primary 主导型主题”，这与“主色 / 强调色 / 背景色独立区域映射”的用户预期不一致。
- 页面消费链当前没有直接信任后端 `theme`，而是在公开页本地再次重算主题，导致主题事实源存在双轨。
- 当前“颜色映射错”的问题，本质不是单点字段丢失，而是：
  - 颜色语义设计与用户预期不一致；
  - `primaryColor` 权重过强；
  - 公开页主题事实源没有完全收口。

## 4. 下一步修复建议

进入下一步实现前，应新建独立修复 Spec，至少收口以下问题：

1. 明确三色语义：
   - 主色控制哪些固定区域
   - 强调色控制哪些固定区域
   - 背景色控制哪些固定区域
2. 明确公开页只允许一个主题事实源：
   - 直接信任后端 `theme`
   - 或前端统一基于 `customConfig` 生成，但不能双轨并存
3. 调整 `pages/actor-profile/detail` 的主题消费，使编辑页可预期映射到公开页
4. 补一轮真实请求样本，验证 `/api/card/config` 与 `/api/card/personalization` 的返回值和页面渲染一致

## 5. 待补充项

- 仍需补一轮实际运行请求样本，把代码事实与线上返回样本并排固化
- 在补齐请求样本前，不继续扩大 UI 修改面
