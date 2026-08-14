# v2.0 演员卡分享与观看者页面 - 技术设计

_Requirements: 3.1, 3.2, 3.3, 3.4_

## 1. 路由配置

### 新增页面

| 路由 | 说明 | 分包 |
|------|------|------|
| `pkg-actor-card/view/index` | 观看者落地页（分享目标页） | `pkg-actor-card` |

### 修改页面

| 路由 | 修改内容 |
|------|----------|
| `pages/card-list/index` | 已发布 Tab 增加分享按钮 + `onShareAppMessage` |

`pages.json` 需同步变更：
- `subpackages[pkg-actor-card].pages` 新增 `view/index`
- `pages/card-list/index.json` 增加 `"enableShareAppMessage": true`

---

## 2. 目录结构

```
src/
├── pkg-actor-card/
│   ├── view/
│   │   ├── index.vue                  观看者落地页
│   │   └── components/
│   │       ├── ProfileCard.vue        个人资料卡片
│   │       ├── WorksSection.vue       参演作品区
│   │       ├── PhotosSection.vue      生活照片区
│   │       ├── VideoSection.vue       视频简历区
│   │       └── AttachmentSection.vue  附件简历区
│   └── components/
│       └── (复用现有组件)
├── pages/card-list/
│   └── index.vue                      名片夹（增加分享功能）
└── api/
    └── actor-card.ts                  新增 getPublicCard 方法
```

---

## 3. 前端 API 合同

### 3.1 新增接口

```typescript
// src/api/actor-card.ts

/**
 * 获取已发布演员卡公开信息（无需鉴权）
 */
export function getPublicCard(cardId: string | number) {
  return request<ActorCardPublicVO>({
    url: `/api/actor-card/public/${cardId}`,
    method: 'GET'
  })
}

interface ActorCardPublicVO {
  id: number
  style: 'classic' | 'urban' | 'ancient' | 'fresh'
  previewImageUrl: string
  profile: {
    name: string
    height?: string
    city?: string
    school?: string
    contact?: string
    introduction?: string
  }
  works: Array<{
    id: number
    title: string
    role: string
    workType: string
    stills: string[]
  }>
  photos: string[]
  video?: {
    assetId: number
    coverUrl: string
    duration: number
  }
  attachment?: {
    assetId: number
    filename: string
  }
  settings: {
    showContact: boolean
    showVideo: boolean
    showAttachment: boolean
    moduleOrder: string[]
  }
}
```

---

## 4. 后端 API 实现

### 4.1 Controller

```java
// ActorCardController.java

@GetMapping("/public/{cardId}")
public ResponseEntity<ActorCardPublicRespDTO> getPublicCard(@PathVariable Long cardId) {
    ActorCardPublicRespDTO resp = actorCardPublishService.getPublicView(cardId);
    return ResponseEntity.ok(resp);
}
```

**注意**：需在 `SecurityConfig.WHITE_LIST` 添加 `/api/actor-card/public/**`

---

### 4.2 Service

```java
// ActorCardPublishService.java

public ActorCardPublicRespDTO getPublicView(Long cardId) {
    ActorCard card = actorCardMapper.selectById(cardId);
    
    if (card == null) {
        throw new BizException(ErrorCode.RESOURCE_NOT_FOUND, "演员卡不存在");
    }
    
    if (!"published".equals(card.getStatus())) {
        throw new BizException(ErrorCode.FORBIDDEN, "该演员卡尚未发布");
    }
    
    ActorCardPublicRespDTO resp = new ActorCardPublicRespDTO();
    resp.setId(card.getId());
    resp.setStyle(card.getStyle());
    
    // 主视觉图片（签名 URL）
    resp.setPreviewImageUrl(
        actorMediaAssetService.generatePresignedUrl(card.getGeneratedPreviewUrl())
    );
    
    // 个人资料
    resp.setProfile(parseProfileSnapshot(card.getProfileSnapshotJson()));
    
    // 参演作品
    List<ActorCardWork> works = actorCardWorkMapper.selectList(
        new LambdaQueryWrapper<ActorCardWork>()
            .eq(ActorCardWork::getCardId, cardId)
            .orderByAsc(ActorCardWork::getSortOrder)
    );
    resp.setWorks(works.stream()
        .map(this::toPublicWorkVO)
        .collect(Collectors.toList()));
    
    // 生活照片
    resp.setPhotos(parsePhotosJson(card.getPhotosJson()));
    
    // 解析 settings
    ActorCardSettings settings = parseSettings(card.getSettingsJson());
    resp.setSettings(settings);
    
    // 按 settings 控制视频/附件返回
    if (settings.isShowVideo() && card.getVideoAssetId() != null) {
        resp.setVideo(buildVideoVO(card.getVideoAssetId()));
    }
    
    if (settings.isShowAttachment() && card.getAttachmentAssetId() != null) {
        resp.setAttachment(buildAttachmentVO(card.getAttachmentAssetId()));
    }
    
    // 按 settings 控制联系方式
    if (!settings.isShowContact()) {
        resp.getProfile().setContact(null);
    }
    
    return resp;
}

private ActorCardPublicWorkVO toPublicWorkVO(ActorCardWork work) {
    ActorCardPublicWorkVO vo = new ActorCardPublicWorkVO();
    vo.setId(work.getId());
    vo.setTitle(work.getWorkTitle());
    vo.setRole(work.getRoleName());
    vo.setWorkType(work.getWorkType());
    
    // 剧照签名 URL
    List<String> stills = parseStillsJson(work.getStillsJson());
    vo.setStills(stills.stream()
        .map(url -> actorMediaAssetService.generatePresignedUrl(url))
        .collect(Collectors.toList()));
    
    return vo;
}
```

---

### 4.3 DTO

```java
// ActorCardPublicRespDTO.java

@Data
public class ActorCardPublicRespDTO {
    private Long id;
    private String style;
    private String previewImageUrl;
    private ProfileVO profile;
    private List<WorkVO> works;
    private List<String> photos;
    private VideoVO video;
    private AttachmentVO attachment;
    private SettingsVO settings;
    
    @Data
    public static class ProfileVO {
        private String name;
        private String height;
        private String city;
        private String school;
        private String contact;
        private String introduction;
    }
    
    @Data
    public static class WorkVO {
        private Long id;
        private String title;
        private String role;
        private String workType;
        private List<String> stills;
    }
    
    @Data
    public static class VideoVO {
        private Long assetId;
        private String coverUrl;
        private Integer duration;
    }
    
    @Data
    public static class AttachmentVO {
        private Long assetId;
        private String filename;
    }
    
    @Data
    public static class SettingsVO {
        private Boolean showContact;
        private Boolean showVideo;
        private Boolean showAttachment;
        private List<String> moduleOrder;
    }
}
```

---

## 5. 前端页面实现

### 5.1 名片夹分享功能

```vue
<!-- pages/card-list/index.vue -->

<template>
  <view class="card-list">
    <!-- 已发布 Tab -->
    <view v-if="currentTab === 'published'" class="card-list__published">
      <view v-for="card in publishedCards" :key="card.id" class="card-item">
        <image :src="card.coverUrl" class="card-item__cover" />
        <view class="card-item__info">
          <text class="card-item__title">{{ card.title }}</text>
          <text class="card-item__time">{{ card.publishTime }}</text>
        </view>
        <view class="card-item__actions">
          <button class="card-item__btn" @click="previewCard(card.id)">预览</button>
          <button 
            class="card-item__btn card-item__btn--primary" 
            open-type="share"
            :data-card-id="card.id"
            @click="prepareShare(card)"
          >
            分享
          </button>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const currentShareCard = ref<any>(null)

function prepareShare(card: any) {
  currentShareCard.value = card
}

// 微信分享配置
onShareAppMessage((options: any) => {
  const card = currentShareCard.value
  if (!card) return {}
  
  return {
    title: `${card.ownerName} 的演员卡`,
    path: `/pkg-actor-card/view/index?cardId=${card.id}`,
    imageUrl: card.coverUrl
  }
})
</script>
```

---

### 5.2 观看者落地页

```vue
<!-- pkg-actor-card/view/index.vue -->

<template>
  <view class="actor-card-view">
    <KpPageNav :title="cardData?.profile.name || '演员卡'" />
    
    <!-- 加载中 -->
    <view v-if="loading" class="actor-card-view__loading">
      <view class="actor-card-view__skeleton" />
    </view>
    
    <!-- 错误态 -->
    <view v-else-if="error" class="actor-card-view__error">
      <text class="actor-card-view__error-icon">!</text>
      <text class="actor-card-view__error-text">{{ errorMessage }}</text>
      <button class="actor-card-view__retry-btn" @click="loadCard">重试</button>
    </view>
    
    <!-- 内容区 -->
    <scroll-view v-else-if="cardData" scroll-y class="actor-card-view__content">
      <!-- 主视觉 -->
      <image 
        :src="cardData.previewImageUrl" 
        mode="widthFix" 
        class="actor-card-view__hero"
      />
      
      <!-- 个人资料 -->
      <ProfileCard :profile="cardData.profile" />
      
      <!-- 动态模块（按 settings.moduleOrder 排序） -->
      <template v-for="module in orderedModules" :key="module">
        <WorksSection 
          v-if="module === 'works' && cardData.works?.length" 
          :works="cardData.works" 
        />
        <PhotosSection 
          v-if="module === 'photos' && cardData.photos?.length" 
          :photos="cardData.photos" 
        />
        <VideoSection 
          v-if="module === 'video' && cardData.video" 
          :video="cardData.video" 
        />
        <AttachmentSection 
          v-if="module === 'attachment' && cardData.attachment" 
          :attachment="cardData.attachment" 
        />
      </template>
    </scroll-view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { getPublicCard } from '@/api/actor-card'
import KpPageNav from '@/components/KpPageNav.vue'
import ProfileCard from './components/ProfileCard.vue'
import WorksSection from './components/WorksSection.vue'
import PhotosSection from './components/PhotosSection.vue'
import VideoSection from './components/VideoSection.vue'
import AttachmentSection from './components/AttachmentSection.vue'

const loading = ref(true)
const error = ref(false)
const errorMessage = ref('')
const cardData = ref<any>(null)

const orderedModules = computed(() => {
  return cardData.value?.settings?.moduleOrder || ['works', 'photos', 'video', 'attachment']
})

async function loadCard() {
  const pages = getCurrentPages()
  const currentPage = pages[pages.length - 1]
  const options = currentPage.options as any
  const cardId = options.cardId
  
  if (!cardId) {
    error.value = true
    errorMessage.value = '缺少演员卡 ID'
    loading.value = false
    return
  }
  
  loading.value = true
  error.value = false
  
  try {
    cardData.value = await getPublicCard(cardId)
  } catch (e: any) {
    error.value = true
    if (e.code === 403) {
      errorMessage.value = '该演员卡尚未发布'
    } else if (e.code === 404) {
      errorMessage.value = '演员卡不存在或已删除'
    } else {
      errorMessage.value = e.message || '加载失败，请重试'
    }
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadCard()
})
</script>

<style lang="scss" scoped>
.actor-card-view {
  min-height: 100vh;
  background: #f5f5f5;
  
  &__hero {
    width: 100%;
    display: block;
  }
  
  &__content {
    height: calc(100vh - var(--nav-height));
  }
  
  &__loading,
  &__error {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 200rpx 60rpx;
  }
  
  &__error-icon {
    font-size: 80rpx;
    color: #ff6b6b;
    margin-bottom: 32rpx;
  }
  
  &__error-text {
    font-size: 28rpx;
    color: #666;
    margin-bottom: 48rpx;
  }
  
  &__retry-btn {
    padding: 16rpx 60rpx;
    background: #1677ff;
    color: #fff;
    border-radius: 8rpx;
  }
}
</style>
```

---

### 5.3 子组件示例

#### ProfileCard.vue

```vue
<template>
  <view class="profile-card">
    <text class="profile-card__name">{{ profile.name }}</text>
    <view class="profile-card__meta">
      <text v-if="profile.height">身高 {{ profile.height }}</text>
      <text v-if="profile.city">{{ profile.city }}</text>
    </view>
    <text v-if="profile.contact" class="profile-card__contact">
      联系方式：{{ profile.contact }}
    </text>
    <text v-if="profile.introduction" class="profile-card__intro">
      {{ profile.introduction }}
    </text>
  </view>
</template>

<script setup lang="ts">
defineProps<{
  profile: {
    name: string
    height?: string
    city?: string
    contact?: string
    introduction?: string
  }
}>()
</script>
```

#### AttachmentSection.vue

```vue
<template>
  <view class="attachment-section">
    <text class="attachment-section__title">附件简历</text>
    <view class="attachment-section__item" @click="previewAttachment">
      <image src="/static/icons/pdf.png" class="attachment-section__icon" />
      <text class="attachment-section__filename">{{ attachment.filename }}</text>
      <text class="attachment-section__action">查看</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { listActorAssetPages } from '@/api/actor-asset'

const props = defineProps<{
  attachment: {
    assetId: number
    filename: string
  }
}>()

async function previewAttachment() {
  try {
    const pages = await listActorAssetPages(props.attachment.assetId)
    const urls = pages.map((p: any) => p.accessUrl)
    
    uni.previewImage({
      urls,
      current: urls[0]
    })
  } catch (e: any) {
    uni.showToast({
      title: e.message || '加载失败',
      icon: 'none'
    })
  }
}
</script>
```

---

## 6. 数据库变更

**无需 DDL 变更**。所有字段已在 v2.0 向导中建立：
- `actor_card.status` - 已有
- `actor_card.profile_snapshot_json` - 已有
- `actor_card.photos_json` - 已有
- `actor_card.video_asset_id` - 已有
- `actor_card.attachment_asset_id` - 已有（00-214）
- `actor_card.settings_json` - 已有
- `actor_card_work` 表 - 已有（00-208）

---

## 7. 关键交互流程

### 7.1 分享流程

```
卡主点击"分享" 
  → prepareShare 记录当前卡片
  → 触发 onShareAppMessage
  → 返回分享配置（title / path / imageUrl）
  → 观看者在微信中点击
  → 小程序打开 /pkg-actor-card/view/index?cardId=123
  → 调用 GET /api/actor-card/public/123
  → 渲染完整信息
```

### 7.2 权限校验流程

```
GET /api/actor-card/public/:cardId
  → 查询 actor_card 表
  → 若 status != 'published' → 返回 403
  → 若不存在 → 返回 404
  → 解析 settings_json
  → 按 showContact/showVideo/showAttachment 过滤字段
  → 返回数据
```

### 7.3 附件预览流程（复用 00-214）

```
观看者点击"附件简历"
  → 调用 listActorAssetPages(assetId)
  → 后端返回页图数组 [{pageIndex, accessUrl, width, height}]
  → 提取 accessUrl 数组
  → uni.previewImage({urls: accessUrls})
  → 微信原生图片浏览器展示
```

---

## 8. 错误处理

| 错误码 | HTTP | 场景 | 前端展示 |
|--------|------|------|----------|
| 403 | Forbidden | 草稿卡访问 | "该演员卡尚未发布" |
| 404 | Not Found | 卡片不存在 | "演员卡不存在或已删除" |
| 500 | Internal Error | 服务异常 | "加载失败，请重试" + 重试按钮 |
| 网络超时 | - | 网络异常 | "网络异常，请检查网络后重试" |

---

## 9. 性能优化

### 9.1 图片加载

- 主视觉图片使用 `mode="widthFix"` 自适应
- 剧照/生活照使用 `lazy-load` 懒加载
- 封面图提前调用 `uni.getImageInfo` 预加载（避免分享面板空白）

### 9.2 签名 URL 缓存

- 前端缓存签名 URL（8 分钟）
- 检测到 403 自动重新请求接口刷新

### 9.3 骨架屏

- 加载态显示骨架屏，避免白屏
- 骨架屏包含：顶部占位 + 卡片占位 + 列表占位

---

## 10. 安全性

- 公开接口只返回已发布卡片（`status = 'published'`）
- 草稿卡严格 403 阻断
- 签名 URL 10 分钟过期，防止资源盗链
- 敏感字段（联系方式）按 `settings.showContact` 控制
- 后端不返回用户 ID、创建时间等内部字段

---

## 11. 测试用例

### 11.1 分享功能

- [ ] 已发布卡片显示"分享"按钮
- [ ] 草稿卡不显示"分享"按钮
- [ ] 点击分享触发微信面板
- [ ] 分享卡片标题/封面/路径正确
- [ ] 观看者点击进入观看者页面

### 11.2 观看者页面

- [ ] 已发布卡正常展示
- [ ] 草稿卡返回 403 提示
- [ ] 不存在的卡返回 404 提示
- [ ] `showContact = false` 时不显示联系方式
- [ ] `showVideo = false` 时不显示视频模块
- [ ] `showAttachment = false` 时不显示附件模块
- [ ] `moduleOrder` 控制模块排列顺序
- [ ] 剧照点击可预览大图
- [ ] 生活照点击可预览大图
- [ ] 附件点击可分页预览

### 11.3 边界情况

- [ ] 无参演作品时不显示作品区
- [ ] 无生活照时不显示照片区
- [ ] 所有模块均关闭时只显示主视觉和个人资料
- [ ] 网络异常显示错误提示和重试按钮
- [ ] 签名 URL 过期自动刷新
