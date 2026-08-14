# 恢复 1.0 分享落地页并接入首页模板区跳转 - 技术设计

_Requirements: ALL_

## 1. 恢复清单（来源：git `27d3bef^`，即 00-209 删除前）

| 文件 | 说明 |
|------|------|
| `src/pkg-card/ai-profile-card-detail/index.vue` | 分享落地页本体（2510 行，含样式） |
| `src/pkg-card/ai-profile-card-detail/layout-presets.ts` | 海报布局预设（314 行） |
| `src/api/ai-profile-card.ts` | AI 分享图 artifact/task 接口 |
| `src/api/history.ts` | 浏览历史记录接口 |
| `src/api/share-card-favorite.ts` | 收藏接口 |
| `src/api/personalization.ts` | 个性化数据接口（`/api/card/personalization`） |
| `src/composables/use-share-card-favorite.ts` | 收藏逻辑 composable |
| `src/utils/ai-profile-card-image.ts` | 分享图 URL 构造 |
| `src/utils/share-card-latest.ts` | 分享卡最新快照聚合 |
| `src/utils/personalization.ts` | 个性化解析（依赖 `api/personalization` + `utils/share-artifact`） |
| `src/utils/share-artifact.ts` | 分享 artifact 类型归一化 |
| `src/components/KpBottomActionBar.vue` | 底部操作栏组件 |
| `src/types/ai-profile-card.ts` | AI 分享卡类型 |
| `src/types/share-card-favorite.ts` | 收藏类型 |

存活未动：`api/contact`、`api/actor-card`、`utils/share-card-mvp`、`utils/navigation`、`KpButton`、`KpFloatingBackButton`、`types/level`、`types/personalization`、`types/contact`。

## 2. 路由注册

`src/pages.json` `pkg-card` 分包追加（照 00-209 前原配置）：

```json
{ "path": "ai-profile-card-detail/index", "style": { "navigationStyle": "custom", "backgroundColor": "#F5F3EE" } }
```

## 3. 首页跳转（Requirements 3.2）

`src/pages/home/index.vue`：

- 模板卡片 `@click`：`goCreateWithStyle(activeStyle)` → `goShareCard`
- `goShareCard`：`requireLogin()` → `listMyShareCards()`（新建 `src/api/card.ts`，`GET /api/card/my-cards`）→ 取 `cards[0].cardId` → `uni.navigateTo('/pkg-card/ai-profile-card-detail/index?shareCardId={id}&shared=1')`
- 无卡：toast「还没有已创建的分享卡」；接口失败：toast「分享卡加载失败，请重试」
- `goCreateWithStyle` 删除（无其他引用）；hero 区 `goCreate` 保留（AI 创建入口仍是创建）

## 4. 后端接口与鉴权（零改动）

| 接口 | 鉴权 | 用途 |
|------|------|------|
| `GET /api/card/my-cards` | 需登录 | 首页取我的分享卡 |
| `GET /api/card/personalization` | **白名单 permitAll** | 分享页核心数据（`SecurityConfig` 已含） |
| `GET /api/card/config` | **白名单 permitAll** | 分享卡配置 |
| `GET /api/ai/profile-card/share-cards/{id}/artifact` | **白名单 permitAll** | 分享图 artifact |
| `GET /api/ai/profile-card/artifacts/*` | **白名单 permitAll** | artifact 明细 |
| 收藏 / 联系方式 / 历史 | 需登录（仅交互项，观看者可跳过） | 收藏 / 联系 / 记录 |

## 5. 风险与边界

- 分享页为 1.0 体系（`share_card` 数据），与 v2 演员卡（`actor_card`）无交集；首页模板区展示的是 v2 背景图库，点击后跳 1.0 分享页——语义由 Spec 固化（用户裁决：优先复现分享者视角）
- 不恢复 `onShareAppMessage` 分享出口（另行立项）
- 00-215（v2 观看者页）规划不受影响，后续可按需实现
