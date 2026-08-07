# 00-205 设计 - 首页已创建作品瀑布流

## 1. 范围与继承

本轮只计划修改 `kaipai-frontend/src/pages/home/index.vue`，并新增本 Spec 文档和静态门禁。首页仍是 Tab 根页；不新增页面、分包、Store、API、后端实体或路由。

`00-201` 的 `home-page__hero`、`home-page__creation-stage`、两个透明创建入口、`goAiProfileCard()`、`goCardList()`、`goMine()` 与 `480rpx` 阴阳鱼视觉完全保留。唯一结构增量是放在 `home-page__creation-stage` 结束标签之后的作品瀑布流。

_Requirements: 3.1, 3.4_

## 2. 首页本地只读适配器

在 `home/index.vue` 内定义窄的展示类型，不把 portfolio 页的完整管理模型搬回首页：

```ts
type HomePortfolioItem =
  | {
      kind: 'ai';
      key: string;
      shareCardId: number;
      taskId: string; // canonical ID, only for artifact/task deduplication
      detailTaskId: string; // artifactId first for the existing detail loader
      previewUrl: string;
      sceneCode: CardScene;
      sceneDisplay: ReturnType<typeof resolveMvpSceneDisplay>;
    }
  | {
      kind: 'manual';
      key: string;
      shareCardId: number;
      sceneCode: CardScene;
      previewUrl: string;
      sceneDisplay: ReturnType<typeof resolveMvpSceneDisplay>;
    };
```

页面本地读取函数采用以下责任划分：

| 函数 | 输入 / 数据源 | 输出 / 行为 |
|------|---------------|-------------|
| `loadHomePortfolioItems` | 已通过身份边界后的读取 | 组合 AI 项和手动项；每个数据源失败返回空集合，不抛出可见错误 |
| `buildHomeAiPortfolioItems` | artifacts + tasks | 官方产物优先，合格 task fallback，按 `taskId` 去重 |
| `buildHomeManualPortfolioItems` | `MyShareCardItem[]` | 每张卡映射一次；逐卡读取 config，失败时保留无预览项目 |
| `firstHighlightedPhoto` | `highlightedPhotos` | 返回按原顺序的第一个 `photo.trim()` 非空 URL，否则空字符串 |
| `openHomePortfolioItem` | `HomePortfolioItem` | 根据 `kind` 进入现有详情页 |

`loadHomePortfolioItems` 只消费既有 API：

```ts
try {
  const [shareCards, artifacts, tasks] = await Promise.all([
    getMyShareCards().catch(() => ({ cards: [], templates: [] })),
    listAiProfileCardArtifacts().catch(() => []),
    listAiProfileCardTasks().catch(() => []),
  ]);
  const cards = shareCards.cards || [];

  return [
    ...buildHomeAiPortfolioItems(artifacts, tasks, cards),
    ...(await buildHomeManualPortfolioItems(cards)),
  ];
} catch {
  return [];
}
```

手动卡不得通过 `filter` 删除。每张卡都读取 `getActorCardConfig({ shareCardId })`；配置读取失败只令 `previewUrl` 为空，模板回退继续可渲染。

_Requirements: 3.2, 3.3_

## 3. AI 过滤与去重

AI 适配复用 portfolio 页当前的真实性判断：排除 `mock` provider、没有生成图、无有效分享卡 ID，以及源图与生成图去掉 query 后相同的记录。任务额外要求 `status === 'success'`。

```ts
const officialItems = artifacts.filter(isUsableAiArtifact).map(buildHomeAiItem);
const representedTaskIds = new Set(officialItems.map((item) => item.taskId).filter(Boolean));
const shareCardIdByScene = cards.reduce<Record<string, number>>((result, card) => {
  if (card.templateSceneCode && !result[card.templateSceneCode]) result[card.templateSceneCode] = card.cardId;
  return result;
}, {});

for (const task of tasks) {
  if (!isUsableAiTask(task) || representedTaskIds.has(task.taskId)) continue;
  const shareCardId = Number(task.shareCardId || shareCardIdByScene[task.templateSceneCode] || 0);
  const fallback = shareCardId > 0 ? buildHomeAiItemFromTask(task, shareCardId) : null;
  if (!fallback) continue;
  officialItems.push(fallback);
  representedTaskIds.add(task.taskId);
}
```

官方 artifact 的 canonical `taskId` 是唯一去重事实；不得以 `shareCardId` 去重，因为手动卡必须完整保留，且同一分享卡可以同时承载手动卡和 AI 图。官方 item 同时记录 `detailTaskId = artifact.artifactId || artifact.taskId`，任务兜底记录 `detailTaskId = task.taskId`，以保持既有 AI 详情页“先按 artifact 读取、再回落 task”的加载语义。任务的详情目标先使用 `task.shareCardId`；旧任务缺失该字段时，按当前 `cards` 中第一个同 `templateSceneCode` 的卡片补出有效 ID，与既有 portfolio 页兼容逻辑一致。仍无法解析正整数 ID 的任务不展示。AI 图片 URL 必须经过 `buildAiProfileCardDisplayImageUrl()`。

_Requirements: 3.3_

## 4. 会话、清空与静默失败

`hydratePage()` 继续负责 `bootstrapSession()` 与演员运行态同步。它增加页面局部 `portfolioRequestVersion` 和 `portfolioItems`：

```ts
let portfolioRequestVersion = 0;
const portfolioItems = ref<HomePortfolioItem[]>([]);

async function hydratePage(): Promise<void> {
  const requestVersion = ++portfolioRequestVersion;
  portfolioItems.value = [];

  const user = await userStore.bootstrapSession();
  if (requestVersion !== portfolioRequestVersion || !user || user.role === 2) return;

  await userStore.syncActorRuntimeState();
  const nextItems = await loadHomePortfolioItems();
  if (requestVersion === portfolioRequestVersion) portfolioItems.value = nextItems;
}
```

实际实现须保留当前 session 同步的错误处理语义，但作品读取函数自行吞掉其读取错误并返回空数组，不对作品区增加 Toast。请求版本防止旧 actor 请求在 logout、切换剧组或刷新后回写；新轮开始、游客 / 剧组分支和当前轮失败都保持空数组。

个人 API 调用仅存在于 `loadHomePortfolioItems` 及其私有 helper 中，且该适配器只能在上述 `!user || user.role === 2` 返回之后调用。游客 / 剧组不能通过预加载、模板渲染或隐藏分支触发个人作品请求。

_Requirements: 3.2, 4_

## 5. 模板、瀑布流与路由

模板紧跟 `home-page__creation-stage`，由 `portfolioItems.length` 唯一决定是否渲染。它不含标题、数量、空态、加载态、说明文字或操作按钮：

```vue
<view v-if="portfolioItems.length" class="home-page__portfolio-waterfall">
  <view v-for="(column, columnIndex) in portfolioColumns" :key="columnIndex" class="home-page__portfolio-column">
    <view v-for="item in column" :key="item.key" class="home-page__portfolio-item" @click="openHomePortfolioItem(item)">
      <image v-if="item.previewUrl" class="home-page__portfolio-image" :src="item.previewUrl" mode="widthFix" />
      <KpShareSceneCover
        v-else
        :scene="item.sceneCode"
        :eyebrow="item.sceneDisplay.eyebrow"
        :title="item.sceneDisplay.title"
        variant="compact"
      />
    </view>
  </view>
</view>
```

`portfolioColumns` 由 `portfolioItems` 的 index parity 分配到固定 `[left, right]` 两列。CSS 使用外层 flex、两条 `flex: 1; min-width: 0` 的纵向列和固定 gap；卡片宽度固定为列宽，图片 `widthFix` 自然撑高，因此不会形成普通等高网格。

```ts
function openHomePortfolioItem(item: HomePortfolioItem): void {
  if (item.kind === 'ai') {
    uni.navigateTo({ url: buildAiHomePortfolioDetailPath(item.shareCardId, item.detailTaskId) });
    return;
  }
  uni.navigateTo({ url: buildShareCardDetailPath({ shareCardId: item.shareCardId }) });
}
```

`buildAiHomePortfolioDetailPath` 仅构造既有 `/pkg-card/ai-profile-card-detail/index?shareCardId=...&taskId=...`，手动项必须复用 `buildShareCardDetailPath`。没有新路由或详情页改动。

_Requirements: 3.1, 3.4_

## 6. 验证设计

1. 先运行 `node .sce/specs/00-205-current-phase-miniapp-home-portfolio-waterfall/scripts/verify-miniapp-home-portfolio-waterfall.mjs`，在本轮实现前应红灯：00-201 保护项通过，作品区、身份边界、适配、过滤、回退、路由与样式项失败。
2. 首页实现后重跑该门禁，确认模板位置、无噪声状态、双列、真实 API、游客 / 剧组无请求边界、stale 清空、AI 去重、manual fallback 和两条详情路由均通过。
3. 运行 `cd kaipai-frontend && npm run type-check`、`npm run build:mp-weixin`，并复跑 `00-187`、`00-192` 与 `00-201` 相关门禁；核对 `src / dist/build / dist/dev` 的首页产物。
4. 按项目约定运行 `npm run audit:steering` 与 `npm run audit:mp-package`。若无关既有问题阻断，记录证据，不扩改其它页面或后端。

静态门禁检查语义性源代码合同，不使用整文件快照；它故意不把构建产物当作实现前的前置条件。

_Requirements: 3.1-3.4, 4_
