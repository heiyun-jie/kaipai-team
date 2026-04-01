# 演员明信片 - 技术设计

> 注：本设计为早期方案，当前主线已由 `05-05-card-share-membership` 接管。

_Requirements: 05-01 全部_

## 1. 路由配置

```json
// pages.json 新增
{
  "path": "pages/actor-card/index",
  "style": {
    "navigationStyle": "custom",
    "navigationBarTitleText": "演员名片",
    "backgroundColor": "#121214"
  }
}
```

URL 参数：`?actorId=xxx`（查看他人名片时传入，查看自己名片时可省略）

```json
// pages/actor-profile/detail 修改
{
  "path": "pages/actor-profile/detail",
  "style": {
    "navigationStyle": "custom",
    "navigationBarTitleText": "演员详情",
    "backgroundColor": "#121214"
  }
}
```

detail 页去除 `ensureUserSessionReady(UserRole.Crew)` 限制，改为公开可访问。

## 2. 依赖清单

| 类别 | 依赖项 | 来源 Spec |
|------|--------|-----------|
| 布局 | KpPageLayout | 00-02 |
| 导航 | KpNavBar | 00-02 |
| 按钮 | KpButton | 00-02 |
| 卡片 | KpCard | 00-02 |
| 标签 | KpTag | 00-02 |
| 等级标签 | KpLevelTag | 05-03 |
| 积分徽章 | KpCreditBadge | 05-03 |
| API | getActorProfile, getActorDetail | 00-03 (api/actor) |
| API | getMyCreditScore | 05-03 (api/credit) |
| Store | useUserStore | 00-03 (stores/user) |
| 样式 | Design Tokens ($kp-*) | 00-01 |

## 3. 页面结构

### 3.1 明信片页 `actor-card/index`（B 类页面）

```
┌─────────────────────────────────┐
│  [返回]        演员名片          │  ← 导航层
├─────────────────────────────────┤
│                                 │
│         [头像 160rpx]           │
│          张三                   │
│    ┌────┐ ┌────┐ ┌─────┐       │
│    │ 男  │ │横店 │ │古装  │       │  ← 标签
│    └────┘ └────┘ └─────┘       │
│                                 │
│  ┌─────────┐ ┌────────────┐    │
│  │ LV.3    │ │ 积分 28 🥉  │    │  ← 等级+积分
│  │ 活跃演员 │ │             │    │
│  └─────────┘ └────────────┘    │
│                                 │
│  [照片1] [照片2] [照片3]        │  ← 代表照片
│                                 │
│  "我是张三，来自横店..."        │  ← 自我介绍摘要
│                                 │
│  ┌─────────────────────────┐   │
│  │     [小程序码]           │   │
│  │  扫码查看完整档案         │   │
│  └─────────────────────────┘   │
│                                 │
│  [分享给好友]  [生成海报]       │  ← 底部操作
└─────────────────────────────────┘
```

### 3.2 落地页 `actor-profile/detail`（A 类深色 Hero 页）

```
┌─────────────────────────────────┐
│  [返回]                         │  ← 悬浮返回
│                                 │
│         [头像 120rpx]           │
│          张三                   │
│    LV.3 活跃演员  |  积分 28 🥉  │
│    ┌────┐ ┌────┐ ┌─────┐       │
│    │ 男  │ │横店 │ │古装  │       │
│    └────┘ └────┘ └─────┘       │
├── 白色内容区（圆角上移）─────────┤
│  ┌ 自我介绍 ──────────────────┐ │
│  │ 完整自我介绍文本...          │ │
│  └────────────────────────────┘ │
│  ┌ 作品经历 ──────────────────┐ │
│  │ 项目名 / 角色 / 时间 / 剧照  │ │
│  └────────────────────────────┘ │
│  ┌ 照片墙 ────────────────────┐ │
│  │ 形象照 | 生活照 | 剧照       │ │
│  └────────────────────────────┘ │
│  ┌ 视频简历 ──────────────────┐ │
│  │ [播放视频]                   │ │
│  └────────────────────────────┘ │
└─────────────────────────────────┘
```

## 4. 页面状态

```typescript
// actor-card/index
const actorId = ref<number>(0)
const actor = ref<ActorProfile | null>(null)
const creditScore = ref<CreditScore | null>(null)
const posterGenerating = ref(false)

// 是否查看自己的名片
const isSelf = computed(() => !actorId.value || actorId.value === userStore.userId)
```

## 5. 分享能力实现

### 5.1 转发好友

```typescript
onShareAppMessage(() => ({
  title: `${actor.value?.name} - 演员名片`,
  path: `/pages/actor-profile/detail?actorId=${actor.value?.userId}`,
  imageUrl: actor.value?.avatar
}))
```

### 5.2 分享朋友圈

```typescript
onShareTimeline(() => ({
  title: `${actor.value?.name} - 演员名片`,
  query: `actorId=${actor.value?.userId}`
}))
```

### 5.3 Canvas 海报生成

```typescript
async function generatePoster(): Promise<void> {
  posterGenerating.value = true
  // 1. 下载头像和照片到临时路径（解决跨域）
  // 2. 创建 Canvas 2D 上下文
  // 3. 绘制背景、头像、文字、照片、小程序码
  // 4. canvasToTempFilePath → saveImageToPhotosAlbum
  posterGenerating.value = false
}
```

**mock 阶段**：小程序码使用占位图，真实小程序码需后端调用 `wxacode.getUnlimited` 接口生成。

## 6. 落地页改造要点

- 删除 `ensureUserSessionReady(UserRole.Crew)` 限制
- 新增 `onShareAppMessage` 和 `onShareTimeline`
- 引入 KpLevelTag 和 KpCreditBadge
- 从 79 行骨架扩展为完整详情页（照片墙、作品经历、视频、信用信息）
- 未登录用户可浏览，联系按钮引导登录

## 7. 入口改造

### mine/index.vue — actorMenus 新增

```typescript
{
  key: 'share',
  label: '分享我的名片',
  desc: '生成专属名片分享给好友',
  path: '/pages/actor-card/index',
}
```

### actor-profile/edit.vue — 底部操作栏新增

"预览名片"次要按钮，跳转 `/pages/actor-card/index`
