# 演员详情查看页（剧组端） - 技术设计

## 1. 路由配置

_Requirements: 3.1_

```json
// pages.json
{
  "path": "pages/actor-profile/detail",
  "style": {
    "navigationStyle": "custom",
    "navigationBarTitleText": "演员档案"
  }
}
```

页面参数通过 `onLoad(options)` 接收：

```typescript
interface PageParams {
  actorId: string;
}
```

## 2. 依赖清单

| 类别 | 依赖项 | 来源 |
|------|--------|------|
| 组件 | KpPageLayout | 00-02-shared-components (3.1) |
| 组件 | KpNavBar | 00-02-shared-components (3.2) |
| 组件 | KpTag | 00-02-shared-components (3.5) |
| API | getActorDetail | 00-03-shared-utils-api (3.9) |
| 类型 | ActorProfile | 00-03-shared-utils-api (3.1) |
| 工具 | formatGender | 00-03-shared-utils-api (3.5) |

## 3. 页面状态

_Requirements: 3.2_

```typescript
const actorId = ref<number>(0);
const actor = ref<ActorProfile | null>(null);
const loading = ref<boolean>(true);

/** 头部信息组合文字 */
const metaText = computed<string>(() => {
  if (!actor.value) return '';
  const { gender, age, height } = actor.value;
  return `${formatGender(gender)} · ${age}岁 · ${height}cm`;
});
```

## 4. 模板结构

_Requirements: 3.2, 3.3, 3.4, 3.5, 3.6_

```vue
<template>
  <KpPageLayout>
    <!-- 深色头部 -->
    <template #header>
      <KpNavBar title="演员档案" />
      <view v-if="actor" class="header-profile">
        <image
          class="header-profile__avatar"
          :src="actor.avatar || '/static/default-avatar.png'"
          mode="aspectFill"
        />
        <text class="header-profile__name">{{ actor.name }}</text>
        <text class="header-profile__meta">{{ metaText }}</text>
        <text class="header-profile__city">{{ actor.city }}</text>
      </view>
    </template>

    <!-- 浅色内容区 -->
    <!-- 擅长类型 -->
    <view v-if="actor?.skillTypes?.length" class="section">
      <text class="section__title">擅长类型</text>
      <view class="section__tags">
        <KpTag
          v-for="tag in actor.skillTypes"
          :key="tag"
          :text="tag"
          type="primary"
          size="medium"
        />
      </view>
    </view>

    <!-- 自我介绍 -->
    <view v-if="actor?.intro" class="section">
      <text class="section__title">自我介绍</text>
      <text class="section__text">{{ actor.intro }}</text>
    </view>

    <!-- 个人照片 -->
    <view v-if="actor?.photos?.length" class="section">
      <text class="section__title">个人照片</text>
      <view class="photo-grid">
        <image
          v-for="(photo, index) in actor.photos"
          :key="index"
          :src="photo"
          mode="aspectFill"
          class="photo-grid__item"
          @click="previewPhoto(index)"
        />
      </view>
    </view>

    <!-- 视频简历 -->
    <view v-if="actor?.videoUrl" class="section">
      <text class="section__title">视频简历</text>
      <view class="video-wrap">
        <video
          :src="actor.videoUrl"
          class="video-player"
          object-fit="cover"
          :controls="true"
          :show-fullscreen-btn="true"
          :enable-progress-gesture="true"
        />
      </view>
    </view>
  </KpPageLayout>
</template>
```

## 5. 交互逻辑

_Requirements: 3.5, 3.6_

```typescript
/** 照片全屏预览 */
function previewPhoto(index: number): void {
  if (!actor.value?.photos?.length) return;
  uni.previewImage({
    urls: actor.value.photos,
    current: index,
  });
}
```

## 6. 生命周期

_Requirements: 3.1, 3.2_

```typescript
onLoad(async (options: PageParams) => {
  if (!options?.actorId) {
    uni.showToast({ title: '参数错误', icon: 'none' });
    setTimeout(() => uni.navigateBack(), 1500);
    return;
  }
  actorId.value = Number(options.actorId);

  try {
    loading.value = true;
    actor.value = await getActorDetail(actorId.value);
  } catch {
    uni.showToast({ title: '获取演员资料失败', icon: 'none' });
  } finally {
    loading.value = false;
  }
});
```

**关键样式**:

```scss
.header-profile {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 32rpx 0 48rpx;

  &__avatar {
    width: 160rpx;
    height: 160rpx;
    border-radius: 50%;
    border: 4rpx solid rgba(255, 255, 255, 0.3);
    margin-bottom: 20rpx;
  }

  &__name {
    font-size: 36rpx;
    font-weight: 600;
    color: $kp-color-text-dark-primary;
  }

  &__meta {
    font-size: 26rpx;
    color: rgba(255, 255, 255, 0.7);
    margin-top: 8rpx;
  }

  &__city {
    font-size: 24rpx;
    color: rgba(255, 255, 255, 0.5);
    margin-top: 4rpx;
  }
}

.section {
  padding: 32rpx 24rpx;
  border-bottom: 1rpx solid rgba(0, 0, 0, 0.06);

  &__title {
    font-size: 30rpx;
    font-weight: 600;
    color: $kp-color-text-primary;
    margin-bottom: 20rpx;
  }

  &__tags {
    display: flex;
    flex-wrap: wrap;
    gap: 12rpx;
  }

  &__text {
    font-size: 28rpx;
    color: $kp-color-text-secondary;
    line-height: 1.6;
  }
}

.photo-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12rpx;

  &__item {
    width: 100%;
    aspect-ratio: 1;
    border-radius: $kp-radius-input;
    object-fit: cover;
  }
}

.video-wrap {
  width: 100%;
  aspect-ratio: 16 / 9;
  border-radius: $kp-radius-lg;
  overflow: hidden;
}

.video-player {
  width: 100%;
  height: 100%;
}
```

## 7. 跳转关系

_Requirements: 3.1_

| 来源 | 目标 | 触发条件 | 携带参数 |
|------|------|----------|----------|
| 投递管理页 | 本页面 | 点击"查看档案" | `actorId` |
| 本页面 | 上一页 | 点击导航栏返回 | — |
