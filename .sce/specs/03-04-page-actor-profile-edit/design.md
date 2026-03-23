# 编辑演员资料页 - 技术设计

## 1. 路由配置

_Requirements: 3.1_

```json
// pages.json
{
  "path": "pages/actor-profile/edit",
  "style": {
    "navigationStyle": "custom",
    "navigationBarTitleText": "编辑资料",
    "backgroundColor": "#121214"
  }
}
```

## 2. 依赖清单

| 类别 | 依赖项 | 来源 |
|------|--------|------|
| 组件 | KpPageLayout | 00-02-shared-components (3.1) |
| 组件 | KpNavBar | 00-02-shared-components (3.2) |
| 组件 | KpFormItem | 00-02-shared-components (3.8) |
| 组件 | KpInput | 00-02-shared-components (3.6) |
| 组件 | KpTextarea | 00-02-shared-components (3.7) |
| 组件 | KpButton | 00-02-shared-components (3.4) |
| 组件 | KpTag | 00-02-shared-components |
| 组件 | KpImageUploader | 00-02-shared-components |
| 组件 | KpVideoUploader | 00-02-shared-components |
| API | getActorProfile() | 00-03-shared-utils-api api/actor.ts |
| API | updateActorProfile(data) | 00-03-shared-utils-api api/actor.ts |
| 上传 | uploadImage() | 00-03-shared-utils-api utils/upload.ts |
| 上传 | uploadVideo() | 00-03-shared-utils-api utils/upload.ts |
| 工具 | requiredRule | 00-03-shared-utils-api (3.6) |
| 类型 | ActorProfile | 00-03-shared-utils-api (3.1) |
| 样式 | Design Tokens ($kp-*) | 00-01-global-style-system |

## 3. 页面状态

_Requirements: 3.2-3.8_

```typescript
/** 擅长类型预定义列表 */
const SKILL_TYPES = ['古装', '现代', '反派', '喜剧', '文艺', '动作', '恐怖', '其他'] as const;

/** 表单数据 */
const formData = reactive<{
  avatar: string;
  name: string;
  gender: number;       // 1=男, 2=女
  age: number | null;
  height: number | null;
  city: string;
  skillTypes: string[];
  introduction: string;
  photos: string[];     // 照片墙 URL 列表，max 9
  videoUrl: string;
  videoThumb: string;
}>({
  avatar: '',
  name: '',
  gender: 0,
  age: null,
  height: null,
  city: '',
  skillTypes: [],
  introduction: '',
  photos: [],
  videoUrl: '',
  videoThumb: '',
});

/** 表单错误信息 */
const errors = reactive<{
  avatar: string;
  name: string;
  gender: string;
  age: string;
  height: string;
  city: string;
}>({
  avatar: '',
  name: '',
  gender: '',
  age: '',
  height: '',
  city: '',
});

const saving = ref<boolean>(false);
const loading = ref<boolean>(true);
const videoUploading = ref<boolean>(false);
const videoProgress = ref<number>(0);
```

## 4. 模板结构

_Requirements: 3.2-3.9_

```vue
<template>
  <KpPageLayout :scrollable="true" :safe-area-bottom="false">
    <!-- 深色头部 -->
    <template #header>
      <KpNavBar title="编辑资料" />
    </template>

    <!-- 浅色内容区 -->
    <view class="actor-edit">
      <!-- 3.2 头像上传 -->
      <view class="actor-edit__avatar">
        <KpImageUploader
          mode="avatar"
          :value="formData.avatar"
          @change="onAvatarChange"
        />
        <text v-if="errors.avatar" class="error-text">{{ errors.avatar }}</text>
      </view>

      <!-- 3.3 基本信息 -->
      <view class="actor-edit__section">
        <KpFormItem label="姓名" required :error="errors.name">
          <KpInput
            v-model="formData.name"
            placeholder="请输入姓名"
            :maxlength="20"
            @blur="validateField('name')"
          />
        </KpFormItem>

        <KpFormItem label="性别" required :error="errors.gender">
          <KpInput
            :model-value="formData.gender === 1 ? '男' : formData.gender === 2 ? '女' : ''"
            placeholder="请选择性别"
            :disabled="true"
            suffix-icon="arrow-right"
            @click="openGenderPicker"
          />
        </KpFormItem>

        <KpFormItem label="年龄" required :error="errors.age">
          <KpInput
            v-model="formData.age"
            type="number"
            placeholder="请输入年龄"
            @blur="validateField('age')"
          />
        </KpFormItem>

        <KpFormItem label="身高(cm)" required :error="errors.height">
          <KpInput
            v-model="formData.height"
            type="number"
            placeholder="请输入身高"
            @blur="validateField('height')"
          />
        </KpFormItem>
      </view>

      <!-- 3.4 城市选择 -->
      <view class="actor-edit__section">
        <KpFormItem label="所在城市" required :error="errors.city">
          <KpInput
            :model-value="formData.city"
            placeholder="请选择所在城市"
            :disabled="true"
            suffix-icon="arrow-right"
            @click="openCityPicker"
          />
        </KpFormItem>
      </view>

      <!-- 3.5 擅长类型 -->
      <view class="actor-edit__section">
        <text class="section-label">擅长类型</text>
        <view class="skill-tags">
          <KpTag
            v-for="type in SKILL_TYPES"
            :key="type"
            :text="type"
            :selected="formData.skillTypes.includes(type)"
            @click="toggleSkillType(type)"
          />
        </view>
      </view>

      <!-- 3.6 自我介绍 -->
      <view class="actor-edit__section">
        <KpFormItem label="自我介绍">
          <KpTextarea
            v-model="formData.introduction"
            placeholder="介绍一下自己的表演经历和特长"
            :maxlength="500"
            show-count
            auto-height
            :min-height="200"
          />
        </KpFormItem>
      </view>

      <!-- 3.7 照片墙 -->
      <view class="actor-edit__section">
        <text class="section-label">照片墙（最多9张）</text>
        <KpImageUploader
          mode="grid"
          :value="formData.photos"
          :max-count="9"
          @add="onPhotosAdd"
          @delete="onPhotoDelete"
          @preview="onPhotoPreview"
        />
      </view>

      <!-- 3.8 视频简历 -->
      <view class="actor-edit__section">
        <text class="section-label">视频简历</text>
        <KpVideoUploader
          :value="formData.videoUrl"
          :thumb="formData.videoThumb"
          :uploading="videoUploading"
          :progress="videoProgress"
          @choose="onVideoChoose"
          @delete="onVideoDelete"
          @play="onVideoPlay"
        />
      </view>

      <!-- 底部占位 -->
      <view class="bottom-placeholder" />
    </view>

    <!-- 固定底部按钮 -->
    <view class="fixed-bottom">
      <KpButton
        variant="primary"
        size="large"
        block
        :loading="saving"
        :disabled="saving"
        @click="handleSave"
      >
        保存资料
      </KpButton>
    </view>
  </KpPageLayout>
</template>
```

**关键样式**:
```scss
.actor-edit {
  padding: 0 32rpx 180rpx;

  &__avatar {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 40rpx 0;
  }

  &__section {
    background: $kp-color-card;
    border-radius: $kp-radius-lg;
    padding: 32rpx;
    margin-bottom: 24rpx;
  }
}

.section-label {
  font-size: $kp-font-size-body;
  font-weight: 600;
  color: $kp-color-text-primary;
  margin-bottom: 24rpx;
  display: block;
}

.skill-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 16rpx;
}

.error-text {
  font-size: $kp-font-size-mini;
  color: $kp-color-danger;
  margin-top: 8rpx;
}

.fixed-bottom {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 16rpx 32rpx;
  padding-bottom: calc(16rpx + env(safe-area-inset-bottom));
  background: $kp-color-card;
  box-shadow: 0 -4rpx 16rpx rgba(0, 0, 0, 0.06);
  z-index: 50;
}
```

## 5. 交互逻辑

### 5.1 头像上传

_Requirements: 3.2_

```typescript
async function onAvatarChange(tempFilePath: string): Promise<void> {
  try {
    const url = await uploadImage(tempFilePath);
    formData.avatar = url;
    errors.avatar = '';
  } catch {
    uni.showToast({ title: '头像上传失败', icon: 'none' });
  }
}
```

### 5.2 性别选择 & 城市选择

_Requirements: 3.3, 3.4_

```typescript
function openGenderPicker(): void {
  uni.showActionSheet({
    itemList: ['男', '女'],
    success: (res) => {
      formData.gender = res.tapIndex + 1; // 1=男, 2=女
      errors.gender = '';
    },
  });
}

function openCityPicker(): void {
  uni.chooseLocation({
    success: (res) => {
      formData.city = res.name || res.address;
      errors.city = '';
    },
  });
}
```

### 5.3 擅长类型 toggle

_Requirements: 3.5_

```typescript
function toggleSkillType(type: string): void {
  const idx = formData.skillTypes.indexOf(type);
  if (idx > -1) {
    formData.skillTypes.splice(idx, 1);
  } else {
    formData.skillTypes.push(type);
  }
}
```

### 5.4 照片墙操作

_Requirements: 3.7_

```typescript
async function onPhotosAdd(tempFiles: string[]): Promise<void> {
  for (const file of tempFiles) {
    if (formData.photos.length >= 9) break;
    try {
      const url = await uploadImage(file);
      formData.photos.push(url);
    } catch {
      uni.showToast({ title: '照片上传失败', icon: 'none' });
    }
  }
}

function onPhotoDelete(index: number): void {
  uni.showModal({
    title: '提示',
    content: '确定删除该照片？',
    success: (res) => {
      if (res.confirm) formData.photos.splice(index, 1);
    },
  });
}

function onPhotoPreview(index: number): void {
  uni.previewImage({
    urls: formData.photos,
    current: formData.photos[index],
  });
}
```

### 5.5 视频简历操作

_Requirements: 3.8_

```typescript
function onVideoChoose(): void {
  uni.chooseVideo({
    sourceType: ['album', 'camera'],
    maxDuration: 60,
    success: async (res) => {
      if (res.size > 100 * 1024 * 1024) {
        uni.showToast({ title: '视频大小不能超过100MB', icon: 'none' });
        return;
      }
      videoUploading.value = true;
      videoProgress.value = 0;
      try {
        const url = await uploadVideo(res.tempFilePath, (progress) => {
          videoProgress.value = progress;
        });
        formData.videoUrl = url;
        formData.videoThumb = res.thumbTempFilePath || '';
      } catch {
        uni.showToast({ title: '视频上传失���', icon: 'none' });
        formData.videoUrl = '';
        formData.videoThumb = '';
      } finally {
        videoUploading.value = false;
      }
    },
  });
}

function onVideoDelete(): void {
  uni.showModal({
    title: '提示',
    content: '确定删除视频简历？',
    success: (res) => {
      if (res.confirm) {
        formData.videoUrl = '';
        formData.videoThumb = '';
      }
    },
  });
}

function onVideoPlay(): void {
  if (formData.videoUrl) {
    uni.navigateTo({
      url: `/pages/video-player/index?url=${encodeURIComponent(formData.videoUrl)}`,
    });
  }
}
```

### 5.6 表单校验与保存

_Requirements: 3.9_

```typescript
function validateField(field: keyof typeof errors): boolean {
  switch (field) {
    case 'avatar':
      errors.avatar = formData.avatar ? '' : '请上传头像';
      break;
    case 'name':
      errors.name = formData.name.trim() ? '' : '请输入姓名';
      break;
    case 'gender':
      errors.gender = formData.gender ? '' : '请选择性别';
      break;
    case 'age':
      if (!formData.age) errors.age = '请输入年龄';
      else if (formData.age < 1 || formData.age > 99) errors.age = '年龄范围 1-99';
      else errors.age = '';
      break;
    case 'height':
      if (!formData.height) errors.height = '请输入身高';
      else if (formData.height < 50 || formData.height > 250) errors.height = '身高范围 50-250cm';
      else errors.height = '';
      break;
    case 'city':
      errors.city = formData.city ? '' : '请选择所在城市';
      break;
  }
  return !errors[field];
}

function validateAll(): boolean {
  const fields: (keyof typeof errors)[] = ['avatar', 'name', 'gender', 'age', 'height', 'city'];
  return fields.map(validateField).every(Boolean);
}

async function handleSave(): Promise<void> {
  if (!validateAll()) return;
  if (saving.value) return;
  saving.value = true;
  try {
    await updateActorProfile({
      avatar: formData.avatar,
      name: formData.name.trim(),
      gender: formData.gender,
      age: formData.age!,
      height: formData.height!,
      city: formData.city,
      skillTypes: formData.skillTypes,
      introduction: formData.introduction.trim(),
      photos: formData.photos,
      videoUrl: formData.videoUrl,
    });
    uni.showToast({ title: '保存成功', icon: 'success' });
    setTimeout(() => uni.navigateBack(), 1500);
  } catch {
    // 错误由 request 层统一处理
  } finally {
    saving.value = false;
  }
}
```

## 6. 生命周期

_Requirements: 3.1_

```typescript
import { onLoad } from '@dcloudio/uni-app';

onLoad(async () => {
  try {
    loading.value = true;
    const profile = await getActorProfile();
    formData.avatar = profile.avatar || '';
    formData.name = profile.name || '';
    formData.gender = profile.gender || 0;
    formData.age = profile.age || null;
    formData.height = profile.height || null;
    formData.city = profile.city || '';
    formData.skillTypes = profile.skillTypes || [];
    formData.introduction = profile.introduction || '';
    formData.photos = profile.photos || [];
    formData.videoUrl = profile.videoUrl || '';
    formData.videoThumb = profile.videoThumb || '';
  } catch {
    // 首次编辑可能无数据，保持空表单
  } finally {
    loading.value = false;
  }
});
```

## 7. 页面跳转关系

_Requirements: 3.1, 3.9_

| 触发 | 目标页面 | 参数 | 方式 |
|------|----------|------|------|
| 投递确认页"查看/编辑档案" | 本页面 | — | uni.navigateTo |
| 我的页面"编辑资料" | 本页面 | — | uni.navigateTo |
| 保存成功 | 上一页 | — | uni.navigateBack |
| 点击导航栏返回 | 上一页 | — | uni.navigateBack |
| 点击视频播放 | 视频播放页 | url | uni.navigateTo |
