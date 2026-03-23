# 共享组件库 - 技术设计

## 1. 架构概览

组件库采用 **原子化分层架构**，分为三层：

- **基础层（Atoms）**: KpButton, KpTag, KpStatusTag, KpInput, KpTextarea, KpEmpty
- **容器层（Molecules）**: KpCard, KpFormItem, KpPageLayout, KpNavBar, KpTabBar, KpFilterBar, KpConfirmDialog
- **业务层（Organisms）**: KpRoleCard, KpProjectCard, KpApplyCard, KpActorBrief, KpImageUploader, KpVideoUploader

所有组件基于 Vue 3.4 Composition API（`<script setup lang="ts">`），样式使用 SCSS 引用全局 Design Tokens。毛玻璃效果通过 `backdrop-filter: blur()` 实现，低端机型降级为纯色 + 透明度。

Design Tokens 引用约定：
```scss
// 颜色
$kp-color-primary: #FF6B35;       // Spotlight Orange
$kp-color-dark-primary: #121214;  // 深色头部背景
$kp-color-bg: #F8F9FA;            // 浅色内容背景
$kp-color-card: #FFFFFF;       // 卡片背景
$kp-color-text-primary: #1A1A1A;  // 主文字色
$kp-color-text-secondary: #666666;// 次要文字色
$kp-color-text-dark-primary: #FFFFFF;  // 反色文字

// 毛玻璃
$kp-color-glass: rgba(255, 255, 255, 0.72);
$kp-glass-blur: 20px;
$kp-glass-border: rgba(255, 255, 255, 0.35);

// 圆角
$kp-radius-tag: 999rpx;
$kp-radius-input: 16rpx;
$kp-radius-lg: 40rpx;
$kp-radius-full: 999rpx;

// 阴影
$kp-shadow-card: 0 8rpx 32rpx rgba(0, 0, 0, 0.06);
$kp-shadow-float: 0 12rpx 44rpx rgba(0, 0, 0, 0.12);
```

## 2. 文件结构

```
kaipai-frontend/src/components/
├── KpPageLayout/
│   ├── KpPageLayout.vue
│   ├── types.ts
│   └── index.ts
├── KpNavBar/
│   ├── KpNavBar.vue
│   ├── types.ts
│   └── index.ts
├── KpCard/
│   ├── KpCard.vue
│   ├── types.ts
│   └── index.ts
├── KpButton/
│   ├── KpButton.vue
│   ├── types.ts
│   └── index.ts
├── KpTag/
│   ├── KpTag.vue
│   ├── types.ts
│   └── index.ts
├── KpInput/
│   ├── KpInput.vue
│   ├── types.ts
│   └── index.ts
├── KpTextarea/
│   ├── KpTextarea.vue
│   ├── types.ts
│   └── index.ts
├── KpFormItem/
│   ├── KpFormItem.vue
│   ├── types.ts
│   └── index.ts
├── KpImageUploader/
│   ├── KpImageUploader.vue
│   ├── types.ts
│   └── index.ts
├── KpVideoUploader/
│   ├── KpVideoUploader.vue
│   ├── types.ts
│   └── index.ts
├── KpRoleCard/
│   ├── KpRoleCard.vue
│   ├── types.ts
│   └── index.ts
├── KpProjectCard/
│   ├── KpProjectCard.vue
│   ├── types.ts
│   └── index.ts
├── KpApplyCard/
│   ├── KpApplyCard.vue
│   ├── types.ts
│   └── index.ts
├── KpActorBrief/
│   ├── KpActorBrief.vue
│   ├── types.ts
│   └── index.ts
├── KpEmpty/
│   ├── KpEmpty.vue
│   ├── types.ts
│   └── index.ts
├── KpFilterBar/
│   ├── KpFilterBar.vue
│   ├── types.ts
│   └── index.ts
├── KpTabBar/
│   ├── KpTabBar.vue
│   ├── types.ts
│   └── index.ts
├── KpStatusTag/
│   ├── KpStatusTag.vue
│   ├── types.ts
│   └── index.ts
├── KpConfirmDialog/
│   ├── KpConfirmDialog.vue
│   ├── types.ts
│   └── index.ts
└── index.ts                    // 统一导出所有组件
```

## 3. 组件详细设计

### 3.1 KpPageLayout

_Requirements: 3.1_

**Template 结构**:
```vue
<template>
  <view class="kp-page-layout">
    <!-- 状态栏占位 -->
    <view class="kp-page-layout__status-bar" :style="{ height: statusBarHeight + 'px' }" />
    <!-- 深色头部 -->
    <view
      v-if="showHeader"
      class="kp-page-layout__header"
      :style="{ height: headerHeight + 'rpx', background: headerBg }"
    >
      <slot name="header" />
    </view>
    <!-- 浅色内容区 -->
    <scroll-view
      v-if="scrollable"
      class="kp-page-layout__content"
      scroll-y
      :style="{ background: contentBg }"
      @scroll="onScroll"
      @scrolltolower="emit('scrolltolower')"
    >
      <slot />
      <view v-if="safeAreaBottom" class="kp-page-layout__safe-bottom" />
    </scroll-view>
    <view v-else class="kp-page-layout__content" :style="{ background: contentBg }">
      <slot />
    </view>
  </view>
</template>
```

**关键样式**:
```scss
.kp-page-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;

  &__header {
    position: relative;
    background: $kp-color-dark-primary;
    overflow: hidden;
  }

  &__content {
    flex: 1;
    background: $kp-color-bg;
    border-radius: $kp-radius-lg $kp-radius-lg 0 0;
    margin-top: -#{$kp-radius-lg};  // 与头部重叠形成圆角过渡
    position: relative;
    z-index: 1;
  }

  &__safe-bottom {
    height: constant(safe-area-inset-bottom);
    height: env(safe-area-inset-bottom);
  }
}
```

**使用示例**:
```vue
<KpPageLayout :header-height="360" @scrolltolower="loadMore">
  <template #header>
    <KpNavBar title="首页" :show-back="false" />
    <view class="search-area">...</view>
  </template>
  <view class="content-list">
    <KpRoleCard v-for="role in roles" :key="role.id" :role="role" />
  </view>
</KpPageLayout>
```

### 3.2 KpNavBar

_Requirements: 3.2_

**Template 结构**:
```vue
<template>
  <view
    class="kp-navbar"
    :class="{ 'kp-navbar--fixed': fixed, 'kp-navbar--glass': showGlass }"
    :style="{ paddingTop: statusBarHeight + 'px' }"
  >
    <view class="kp-navbar__content" :style="{ height: navBarHeight + 'px' }">
      <!-- 左侧 -->
      <view class="kp-navbar__left" @click="onBack">
        <slot name="left">
          <u-icon v-if="showBack" name="arrow-left" :color="backIconColor" size="20" />
        </slot>
      </view>
      <!-- 标题 -->
      <view class="kp-navbar__center">
        <slot name="center">
          <text class="kp-navbar__title" :style="{ color: titleColor }">{{ title }}</text>
        </slot>
      </view>
      <!-- 右侧（不超过胶囊区域） -->
      <view class="kp-navbar__right" :style="{ marginRight: capsuleRight + 'px' }">
        <slot name="right" />
      </view>
    </view>
  </view>
</template>
```

**关键样式**:
```scss
.kp-navbar {
  width: 100%;
  z-index: 100;

  &--fixed {
    position: fixed;
    top: 0;
    left: 0;
  }

  &--glass {
    background: $kp-color-glass;
    backdrop-filter: blur($kp-glass-blur);
    -webkit-backdrop-filter: blur($kp-glass-blur);
    border-bottom: 1rpx solid $kp-glass-border;
  }

  &__content {
    display: flex;
    align-items: center;
    padding: 0 24rpx;
  }

  &__center {
    flex: 1;
    text-align: center;
  }

  &__title {
    font-size: 34rpx;
    font-weight: 600;
  }
}
```

**使用示例**:
```vue
<KpNavBar title="角色详情" glass-on-scroll @back="navigateBack">
  <template #right>
    <u-icon name="share" color="#fff" size="20" />
  </template>
</KpNavBar>
```

### 3.3 KpCard

_Requirements: 3.3_

**Template 结构**:
```vue
<template>
  <view
    class="kp-card"
    :class="[`kp-card--${mode}`, { 'kp-card--glass': glass, 'kp-card--shadow': shadow }]"
    :style="{ borderRadius: radius + 'rpx', padding, background: bgColor }"
    @click="emit('click')"
  >
    <view v-if="$slots.header" class="kp-card__header">
      <slot name="header" />
    </view>
    <view class="kp-card__body">
      <slot />
    </view>
    <view v-if="$slots.footer" class="kp-card__footer">
      <slot name="footer" />
    </view>
  </view>
</template>
```

**关键样式**:
```scss
.kp-card {
  overflow: hidden;
  transition: transform 0.2s ease;

  &--light {
    background: $kp-color-card;
    color: $kp-color-text-primary;
  }

  &--dark {
    background: rgba($kp-color-dark-primary, 0.85);
    color: $kp-color-text-dark-primary;
  }

  &--glass {
    background: $kp-color-glass;
    backdrop-filter: blur($kp-glass-blur);
    border: 1rpx solid $kp-glass-border;
  }

  &--shadow {
    box-shadow: $kp-shadow-card;
  }

  &__header {
    padding-bottom: 16rpx;
    border-bottom: 1rpx solid rgba(0, 0, 0, 0.06);
  }

  &__footer {
    padding-top: 16rpx;
    border-top: 1rpx solid rgba(0, 0, 0, 0.06);
  }
}
```

**使用示例**:
```vue
<KpCard mode="light" :radius="24" shadow>
  <template #header>
    <text class="card-title">项目信息</text>
  </template>
  <view class="card-content">...</view>
</KpCard>
```

### 3.4 KpButton

_Requirements: 3.4_

**Template 结构**:
```vue
<template>
  <button
    class="kp-button"
    :class="[
      `kp-button--${variant}`,
      `kp-button--${size}`,
      { 'kp-button--block': block, 'kp-button--disabled': disabled, 'kp-button--loading': loading }
    ]"
    :style="{ borderRadius: radius + 'rpx' }"
    :disabled="disabled || loading"
    :open-type="openType || undefined"
    @click="onClick"
    @getphonenumber="emit('getphonenumber', $event)"
    @getuserinfo="emit('getuserinfo', $event)"
  >
    <u-loading-icon v-if="loading" size="16" :color="loadingColor" class="kp-button__loading" />
    <slot name="icon">
      <u-icon v-if="icon && !loading" :name="icon" size="16" class="kp-button__icon" />
    </slot>
    <text class="kp-button__text"><slot /></text>
  </button>
</template>
```

**关键样式**:
```scss
.kp-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8rpx;
  font-weight: 500;
  transition: opacity 0.2s;
  // 清除微信按钮默认样式
  &::after { display: none; }

  &--primary {
    background: $kp-color-primary;
    color: $kp-color-text-dark-primary;
  }

  &--secondary {
    background: transparent;
    color: $kp-color-primary;
    border: 2rpx solid $kp-color-primary;
  }

  &--danger {
    background: #E53935;
    color: $kp-color-text-dark-primary;
  }

  &--glass {
    background: $kp-color-glass;
    backdrop-filter: blur($kp-glass-blur);
    color: $kp-color-text-dark-primary;
    border: 1rpx solid $kp-glass-border;
  }

  &--disabled {
    opacity: 0.4;
    pointer-events: none;
  }

  &--small  { height: 56rpx;  padding: 0 24rpx; font-size: 24rpx; }
  &--medium { height: 80rpx;  padding: 0 40rpx; font-size: 28rpx; }
  &--large  { height: 96rpx;  padding: 0 48rpx; font-size: 32rpx; }
  &--block  { width: 100%; }
}
```

**使用示例**:
```vue
<KpButton variant="primary" size="large" block @click="handleSubmit">
  提交申请
</KpButton>

<KpButton variant="glass" icon="share">分享</KpButton>

<KpButton variant="secondary" :disabled="!isValid">下一步</KpButton>
```

### 3.5 KpTag

_Requirements: 3.5_

**Template 结构**:
```vue
<template>
  <view
    class="kp-tag"
    :class="[
      `kp-tag--${type}`,
      `kp-tag--${size}`,
      { 'kp-tag--selected': selected, 'kp-tag--round': round }
    ]"
    :style="{ background: bgColor, color: textColor }"
    @click="emit('click')"
  >
    <text class="kp-tag__text">{{ text }}</text>
    <u-icon v-if="closable" name="close" size="12" class="kp-tag__close" @click.stop="emit('close')" />
  </view>
</template>
```

**关键样式**:
```scss
.kp-tag {
  display: inline-flex;
  align-items: center;
  gap: 4rpx;

  &--default  { background: rgba(0,0,0,0.05); color: $kp-color-text-secondary; }
  &--primary  { background: rgba($kp-color-primary, 0.1); color: $kp-color-primary; }
  &--success  { background: rgba(#4CAF50, 0.1); color: #4CAF50; }
  &--warning  { background: rgba(#FF9800, 0.1); color: #FF9800; }
  &--danger   { background: rgba(#E53935, 0.1); color: #E53935; }

  &--selected {
    background: $kp-color-primary;
    color: $kp-color-text-dark-primary;
  }

  &--small  { height: 40rpx; padding: 0 16rpx; font-size: 22rpx; }
  &--medium { height: 52rpx; padding: 0 20rpx; font-size: 26rpx; }
  &--round  { border-radius: $kp-radius-full; }
}
```

**使用示例**:
```vue
<KpTag text="演员" type="primary" />
<KpTag text="北京" :selected="isSelected" @click="toggleFilter" />
<KpTag text="技能标签" closable @close="removeTag" />
```

### 3.6 KpInput

_Requirements: 3.6_

**Template 结构**:
```vue
<template>
  <view class="kp-input" :class="{ 'kp-input--error': status === 'error', 'kp-input--disabled': disabled, 'kp-input--focus': isFocused }">
    <view v-if="prefixIcon || $slots.prefix" class="kp-input__prefix">
      <slot name="prefix">
        <u-icon :name="prefixIcon" size="18" color="#999" />
      </slot>
    </view>
    <input
      class="kp-input__inner"
      :type="type"
      :value="modelValue"
      :placeholder="placeholder"
      :disabled="disabled"
      :maxlength="maxlength"
      :password="type === 'password'"
      @input="onInput"
      @focus="onFocus"
      @blur="onBlur"
    />
    <u-icon
      v-if="clearable && modelValue && isFocused"
      name="close-circle-fill"
      size="16"
      color="#ccc"
      class="kp-input__clear"
      @click="onClear"
    />
    <view v-if="suffixIcon || $slots.suffix" class="kp-input__suffix" @click="emit('clickSuffix')">
      <slot name="suffix">
        <u-icon :name="suffixIcon" size="18" color="#999" />
      </slot>
    </view>
  </view>
</template>
```

**关键样式**:
```scss
.kp-input {
  display: flex;
  align-items: center;
  height: 88rpx;
  padding: 0 24rpx;
  background: $kp-color-card;
  border: 2rpx solid #E8E8E8;
  border-radius: $kp-radius-input;
  transition: border-color 0.2s;

  &--focus { border-color: $kp-color-primary; }
  &--error { border-color: #E53935; }
  &--disabled { background: #F5F5F5; opacity: 0.6; }

  &__inner {
    flex: 1;
    font-size: 28rpx;
    color: $kp-color-text-primary;
  }
}
```

**使用示例**:
```vue
<KpInput v-model="phone" type="number" placeholder="请输入手机号" prefix-icon="phone" :maxlength="11" />
```

### 3.7 KpTextarea

_Requirements: 3.7_

**Template 结构**:
```vue
<template>
  <view class="kp-textarea" :class="{ 'kp-textarea--error': status === 'error', 'kp-textarea--disabled': disabled }">
    <textarea
      class="kp-textarea__inner"
      :value="modelValue"
      :placeholder="placeholder"
      :maxlength="maxlength"
      :auto-height="autoHeight"
      :disabled="disabled"
      :style="{ minHeight: minHeight + 'rpx' }"
      @input="onInput"
      @focus="emit('focus', $event)"
      @blur="emit('blur', $event)"
    />
    <view v-if="showCount" class="kp-textarea__count">
      <text :class="{ 'kp-textarea__count--over': modelValue.length >= maxlength }">
        {{ modelValue.length }}
      </text>/{{ maxlength }}
    </view>
  </view>
</template>
```

**关键样式**:
```scss
.kp-textarea {
  position: relative;
  padding: 24rpx;
  background: $kp-color-card;
  border: 2rpx solid #E8E8E8;
  border-radius: $kp-radius-input;

  &--error { border-color: #E53935; }
  &--disabled { background: #F5F5F5; opacity: 0.6; }

  &__inner {
    width: 100%;
    font-size: 28rpx;
    color: $kp-color-text-primary;
    line-height: 1.6;
  }

  &__count {
    text-align: right;
    font-size: 24rpx;
    color: $kp-color-text-secondary;
    margin-top: 8rpx;

    &--over { color: #E53935; }
  }
}
```

**使用示例**:
```vue
<KpTextarea v-model="bio" placeholder="请输入个人简介" :maxlength="300" show-count auto-height />
```

### 3.8 KpFormItem

_Requirements: 3.8_

**Template 结构**:
```vue
<template>
  <view class="kp-form-item" :class="[`kp-form-item--${direction}`]">
    <view class="kp-form-item__label" :style="{ width: direction === 'horizontal' ? labelWidth + 'rpx' : 'auto' }">
      <slot name="label">
        <text v-if="required" class="kp-form-item__required">*</text>
        <text class="kp-form-item__label-text">{{ label }}</text>
      </slot>
      <slot name="extra" />
    </view>
    <view class="kp-form-item__control">
      <slot />
    </view>
    <view v-if="error" class="kp-form-item__error">
      <text>{{ error }}</text>
    </view>
  </view>
</template>
```

**关键样式**:
```scss
.kp-form-item {
  margin-bottom: 32rpx;

  &--horizontal {
    display: flex;
    align-items: center;
    .kp-form-item__label { flex-shrink: 0; }
    .kp-form-item__control { flex: 1; }
  }

  &--vertical {
    .kp-form-item__label { margin-bottom: 12rpx; }
  }

  &__label-text {
    font-size: 28rpx;
    color: $kp-color-text-primary;
    font-weight: 500;
  }

  &__required {
    color: #E53935;
    margin-right: 4rpx;
  }

  &__error {
    font-size: 24rpx;
    color: #E53935;
    margin-top: 8rpx;
  }
}
```

**使用示例**:
```vue
<KpFormItem label="手机号" required :error="phoneError">
  <KpInput v-model="phone" type="number" placeholder="请输入手机号" />
</KpFormItem>
```

### 3.9 KpImageUploader

_Requirements: 3.9_

**Template 结构**:
```vue
<template>
  <view class="kp-image-uploader" :class="{ 'kp-image-uploader--single': single }">
    <!-- 已上传图片列表 -->
    <view v-for="(url, index) in modelValue" :key="index" class="kp-image-uploader__item">
      <image :src="url" mode="aspectFill" class="kp-image-uploader__image" @click="onPreview(index)" />
      <view v-if="deletable && !disabled" class="kp-image-uploader__delete" @click.stop="onDelete(index)">
        <u-icon name="close" size="12" color="#fff" />
      </view>
    </view>
    <!-- 上传按钮 -->
    <view
      v-if="modelValue.length < maxCount && !disabled"
      class="kp-image-uploader__trigger"
      @click="chooseImage"
    >
      <slot name="trigger">
        <view class="kp-image-uploader__add">
          <u-icon name="plus" size="24" color="#ccc" />
          <text class="kp-image-uploader__text">{{ uploadText }}</text>
        </view>
      </slot>
    </view>
  </view>
</template>
```

**关键样式**:
```scss
.kp-image-uploader {
  display: flex;
  flex-wrap: wrap;
  gap: 16rpx;

  &__item, &__trigger {
    width: 200rpx;
    height: 200rpx;
    border-radius: $kp-radius-input;
    overflow: hidden;
    position: relative;
  }

  &--single &__item,
  &--single &__trigger {
    width: 160rpx;
    height: 160rpx;
    border-radius: 50%;  // 头像圆形
  }

  &__image {
    width: 100%;
    height: 100%;
  }

  &__delete {
    position: absolute;
    top: 4rpx;
    right: 4rpx;
    width: 36rpx;
    height: 36rpx;
    background: rgba(0, 0, 0, 0.5);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  &__add {
    width: 100%;
    height: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    background: #F5F5F7;
    border: 2rpx dashed #D9D9D9;
    border-radius: $kp-radius-input;
  }

  &__text {
    font-size: 22rpx;
    color: $kp-color-text-secondary;
    margin-top: 8rpx;
  }
}
```

**使用示例**:
```vue
<!-- 头像上传 -->
<KpImageUploader v-model="avatarList" single :max-count="1" upload-text="上传头像" />

<!-- 照片墙 -->
<KpImageUploader v-model="photoList" :max-count="9" upload-text="添加照片" />
```

### 3.10 KpVideoUploader

_Requirements: 3.10_

**Template 结构**:
```vue
<template>
  <view class="kp-video-uploader">
    <!-- 已上传视频 -->
    <view v-if="modelValue" class="kp-video-uploader__preview">
      <video :src="modelValue" class="kp-video-uploader__video" :controls="true" object-fit="cover" />
      <view v-if="!disabled" class="kp-video-uploader__delete" @click="onDelete">
        <u-icon name="close" size="12" color="#fff" />
      </view>
    </view>
    <!-- 上传中 -->
    <view v-else-if="uploading" class="kp-video-uploader__uploading">
      <view class="kp-video-uploader__progress-bar">
        <view class="kp-video-uploader__progress-fill" :style="{ width: percent + '%' }" />
      </view>
      <text class="kp-video-uploader__percent">{{ percent }}%</text>
    </view>
    <!-- 上传按钮 -->
    <view v-else-if="!disabled" class="kp-video-uploader__trigger" @click="chooseVideo">
      <u-icon name="play-circle" size="32" color="#ccc" />
      <text class="kp-video-uploader__text">{{ uploadText }}</text>
    </view>
  </view>
</template>
```

**关键样式**:
```scss
.kp-video-uploader {
  &__preview, &__uploading, &__trigger {
    width: 100%;
    height: 360rpx;
    border-radius: $kp-radius-lg;
    overflow: hidden;
    position: relative;
  }

  &__video {
    width: 100%;
    height: 100%;
  }

  &__trigger {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    background: #F5F5F7;
    border: 2rpx dashed #D9D9D9;
  }

  &__progress-bar {
    width: 60%;
    height: 8rpx;
    background: rgba(0, 0, 0, 0.1);
    border-radius: 4rpx;
    overflow: hidden;
  }

  &__progress-fill {
    height: 100%;
    background: $kp-color-primary;
    transition: width 0.3s;
  }

  &__delete {
    position: absolute;
    top: 16rpx;
    right: 16rpx;
    width: 48rpx;
    height: 48rpx;
    background: rgba(0, 0, 0, 0.5);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
  }
}
```

**使用示例**:
```vue
<KpVideoUploader v-model="videoUrl" :max-duration="60" :max-size="50" @success="onVideoUploaded" />
```

### 3.11 KpRoleCard

_Requirements: 3.11_

**Template 结构**:
```vue
<template>
  <KpCard mode="light" shadow :radius="24" @click="emit('click', { roleId: role.id })">
    <view class="kp-role-card">
      <image v-if="role.coverImage" :src="role.coverImage" mode="aspectFill" class="kp-role-card__cover" />
      <view class="kp-role-card__info">
        <view class="kp-role-card__header">
          <text class="kp-role-card__name">{{ role.name }}</text>
          <KpStatusTag v-if="showStatus" :status="role.status" size="small" />
        </view>
        <text v-if="showProject" class="kp-role-card__project">{{ role.projectName }}</text>
        <view class="kp-role-card__tags">
          <KpTag :text="role.gender" size="small" />
          <KpTag :text="role.ageRange" size="small" />
          <KpTag v-for="tag in role.tags" :key="tag" :text="tag" size="small" type="primary" />
        </view>
        <view class="kp-role-card__footer">
          <text class="kp-role-card__salary">{{ role.salary }}</text>
          <text class="kp-role-card__time">{{ role.publishTime }}</text>
        </view>
      </view>
    </view>
    <template v-if="$slots.footer" #footer><slot name="footer" /></template>
  </KpCard>
</template>
```

**关键样式**:
```scss
.kp-role-card {
  display: flex;
  gap: 20rpx;

  &__cover {
    width: 160rpx;
    height: 160rpx;
    border-radius: $kp-radius-input;
    flex-shrink: 0;
  }

  &__info { flex: 1; }

  &__name {
    font-size: 32rpx;
    font-weight: 600;
    color: $kp-color-text-primary;
  }

  &__project {
    font-size: 24rpx;
    color: $kp-color-text-secondary;
    margin-top: 4rpx;
  }

  &__tags {
    display: flex;
    flex-wrap: wrap;
    gap: 8rpx;
    margin-top: 12rpx;
  }

  &__salary {
    font-size: 30rpx;
    font-weight: 600;
    color: $kp-color-primary;
  }

  &__footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 12rpx;
  }

  &__time {
    font-size: 22rpx;
    color: $kp-color-text-secondary;
  }
}
```

**使用示例**:
```vue
<KpRoleCard v-for="role in roleList" :key="role.id" :role="role" @click="goRoleDetail" />
```

### 3.12 KpProjectCard

_Requirements: 3.12_

**Template 结构**:
```vue
<template>
  <KpCard mode="light" shadow :radius="24" @click="emit('click', { projectId: project.id })">
    <view class="kp-project-card">
      <image v-if="project.coverImage" :src="project.coverImage" mode="aspectFill" class="kp-project-card__cover" />
      <view class="kp-project-card__info">
        <text class="kp-project-card__name">{{ project.name }}</text>
        <view class="kp-project-card__meta">
          <text>{{ project.type }}</text>
          <text class="kp-project-card__divider">|</text>
          <text>{{ project.location }}</text>
        </view>
        <text class="kp-project-card__date">拍摄时间：{{ project.shootingDate }}</text>
        <text v-if="showRoleCount" class="kp-project-card__role-count">
          招募 {{ project.roleCount }} 个角色
        </text>
      </view>
    </view>
    <template v-if="$slots.footer" #footer><slot name="footer" /></template>
  </KpCard>
</template>
```

**关键样式**:
```scss
.kp-project-card {
  display: flex;
  gap: 20rpx;

  &__cover {
    width: 200rpx;
    height: 150rpx;
    border-radius: $kp-radius-input;
    flex-shrink: 0;
  }

  &__name {
    font-size: 32rpx;
    font-weight: 600;
    color: $kp-color-text-primary;
  }

  &__meta {
    display: flex;
    align-items: center;
    gap: 12rpx;
    margin-top: 8rpx;
    font-size: 24rpx;
    color: $kp-color-text-secondary;
  }

  &__date {
    font-size: 24rpx;
    color: $kp-color-text-secondary;
    margin-top: 8rpx;
  }

  &__role-count {
    font-size: 24rpx;
    color: $kp-color-primary;
    font-weight: 500;
    margin-top: 8rpx;
  }
}
```

**使用示例**:
```vue
<KpProjectCard v-for="p in projectList" :key="p.id" :project="p" @click="goProjectDetail" />
```

### 3.13 KpApplyCard

_Requirements: 3.13_

**Template 结构**:
```vue
<template>
  <KpCard mode="light" shadow :radius="24" @click="emit('click', { applyId: apply.id })">
    <view class="kp-apply-card">
      <image v-if="viewMode === 'crew' && apply.actorAvatar" :src="apply.actorAvatar" mode="aspectFill" class="kp-apply-card__avatar" />
      <view class="kp-apply-card__info">
        <view class="kp-apply-card__header">
          <text v-if="viewMode === 'crew'" class="kp-apply-card__actor-name">{{ apply.actorName }}</text>
          <text class="kp-apply-card__role">{{ apply.roleName }}</text>
          <KpStatusTag :status="apply.status" size="small" />
        </view>
        <text class="kp-apply-card__project">{{ apply.projectName }}</text>
        <text class="kp-apply-card__time">{{ apply.applyTime }}</text>
      </view>
    </view>
    <template v-if="viewMode === 'crew' && apply.status === 'pending'" #footer>
      <slot name="action">
        <view class="kp-apply-card__actions">
          <KpButton variant="secondary" size="small" @click.stop="emit('action', { applyId: apply.id, action: 'reject' })">拒绝</KpButton>
          <KpButton variant="primary" size="small" @click.stop="emit('action', { applyId: apply.id, action: 'accept' })">通过</KpButton>
        </view>
      </slot>
    </template>
  </KpCard>
</template>
```

**关键样式**:
```scss
.kp-apply-card {
  display: flex;
  gap: 20rpx;

  &__avatar {
    width: 88rpx;
    height: 88rpx;
    border-radius: 50%;
    flex-shrink: 0;
  }

  &__header {
    display: flex;
    align-items: center;
    gap: 12rpx;
  }

  &__actor-name {
    font-size: 30rpx;
    font-weight: 600;
    color: $kp-color-text-primary;
  }

  &__role {
    font-size: 28rpx;
    color: $kp-color-text-primary;
  }

  &__project, &__time {
    font-size: 24rpx;
    color: $kp-color-text-secondary;
    margin-top: 4rpx;
  }

  &__actions {
    display: flex;
    justify-content: flex-end;
    gap: 16rpx;
  }
}
```

**使用示例**:
```vue
<!-- 演员端 -->
<KpApplyCard v-for="a in myApplies" :key="a.id" :apply="a" view-mode="actor" />
<!-- 剧组端 -->
<KpApplyCard v-for="a in applies" :key="a.id" :apply="a" view-mode="crew" @action="handleAction" />
```

### 3.14 KpActorBrief

_Requirements: 3.14_

**Template 结构**:
```vue
<template>
  <view class="kp-actor-brief" :class="[`kp-actor-brief--${size}`]" @click="clickable && emit('click', { actorId: actor.id })">
    <image :src="actor.avatar" mode="aspectFill" class="kp-actor-brief__avatar" />
    <view class="kp-actor-brief__info">
      <text class="kp-actor-brief__name">{{ actor.name }}</text>
      <view class="kp-actor-brief__meta">
        <text>{{ actor.gender }}</text>
        <text class="kp-actor-brief__dot">·</text>
        <text>{{ actor.age }}岁</text>
        <text class="kp-actor-brief__dot">·</text>
        <text>{{ actor.height }}cm</text>
        <text class="kp-actor-brief__dot">·</text>
        <text>{{ actor.weight }}kg</text>
      </view>
      <view v-if="showTags && actor.tags?.length" class="kp-actor-brief__tags">
        <KpTag v-for="tag in actor.tags" :key="tag" :text="tag" size="small" />
      </view>
    </view>
    <view class="kp-actor-brief__extra">
      <slot name="extra" />
    </view>
  </view>
</template>
```

**关键样式**:
```scss
.kp-actor-brief {
  display: flex;
  align-items: center;
  gap: 20rpx;

  &__avatar {
    border-radius: 50%;
    flex-shrink: 0;
  }

  &--medium &__avatar { width: 96rpx; height: 96rpx; }
  &--small &__avatar  { width: 72rpx; height: 72rpx; }

  &__info { flex: 1; }

  &__name {
    font-size: 30rpx;
    font-weight: 600;
    color: $kp-color-text-primary;
  }

  &__meta {
    display: flex;
    align-items: center;
    gap: 4rpx;
    font-size: 24rpx;
    color: $kp-color-text-secondary;
    margin-top: 4rpx;
  }

  &__dot { margin: 0 4rpx; }

  &__tags {
    display: flex;
    flex-wrap: wrap;
    gap: 8rpx;
    margin-top: 8rpx;
  }
}
```

**使用示例**:
```vue
<KpActorBrief :actor="actorInfo" show-tags @click="goActorDetail">
  <template #extra>
    <KpButton variant="primary" size="small">查看</KpButton>
  </template>
</KpActorBrief>
```

### 3.15 KpEmpty

_Requirements: 3.15_

**Template 结构**:
```vue
<template>
  <view class="kp-empty">
    <slot name="image">
      <image :src="imageUrl" mode="aspectFit" class="kp-empty__image" />
    </slot>
    <slot>
      <text class="kp-empty__text">{{ text }}</text>
    </slot>
    <slot name="action">
      <KpButton v-if="showAction" variant="secondary" size="small" @click="emit('action')">
        {{ actionText }}
      </KpButton>
    </slot>
  </view>
</template>
```

**关键样式**:
```scss
.kp-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 120rpx 48rpx;

  &__image {
    width: 320rpx;
    height: 240rpx;
    margin-bottom: 32rpx;
  }

  &__text {
    font-size: 28rpx;
    color: $kp-color-text-secondary;
    margin-bottom: 32rpx;
    text-align: center;
  }
}
```

**使用示例**:
```vue
<KpEmpty v-if="list.length === 0" type="search" text="暂无匹配的角色" show-action action-text="清除筛选" @action="resetFilters" />
```

### 3.16 KpFilterBar

_Requirements: 3.16_

**Template 结构**:
```vue
<template>
  <view class="kp-filter-bar" :class="{ 'kp-filter-bar--sticky': sticky }" :style="{ top: sticky ? stickyTop + 'rpx' : 'auto' }">
    <scroll-view scroll-x class="kp-filter-bar__scroll">
      <view
        v-for="filter in filters"
        :key="filter.key"
        class="kp-filter-bar__item"
        :class="{ 'kp-filter-bar__item--active': isActive(filter.key) }"
        @click="togglePanel(filter.key)"
      >
        <text class="kp-filter-bar__label">{{ filter.label }}</text>
        <u-icon name="arrow-down" size="12" :color="isActive(filter.key) ? '#FF6B35' : '#999'" />
      </view>
      <slot name="extra" />
    </scroll-view>
    <!-- 下拉面板 -->
    <view v-if="activePanel" class="kp-filter-bar__panel">
      <view class="kp-filter-bar__options">
        <KpTag
          v-for="opt in activeFilter.options"
          :key="opt.value"
          :text="opt.label"
          :selected="isSelected(activePanel, opt.value)"
          @click="onSelect(activePanel, opt.value)"
        />
      </view>
      <view class="kp-filter-bar__panel-footer">
        <KpButton variant="secondary" size="small" @click="onReset">重置</KpButton>
        <KpButton variant="primary" size="small" @click="onConfirm">确定</KpButton>
      </view>
    </view>
    <!-- 遮罩 -->
    <view v-if="activePanel" class="kp-filter-bar__mask" @click="closePanel" />
  </view>
</template>
```

**关键样式**:
```scss
.kp-filter-bar {
  background: $kp-color-card;
  z-index: 50;

  &--sticky {
    position: sticky;
  }

  &__scroll {
    white-space: nowrap;
    padding: 16rpx 24rpx;
  }

  &__item {
    display: inline-flex;
    align-items: center;
    gap: 4rpx;
    padding: 12rpx 20rpx;
    margin-right: 16rpx;
    border-radius: $kp-radius-full;
    background: #F5F5F7;
    font-size: 26rpx;
    color: $kp-color-text-primary;

    &--active {
      background: rgba($kp-color-primary, 0.1);
      color: $kp-color-primary;
    }
  }

  &__panel {
    position: absolute;
    left: 0;
    right: 0;
    background: $kp-color-card;
    padding: 24rpx;
    box-shadow: $kp-shadow-float;
    z-index: 51;
  }

  &__options {
    display: flex;
    flex-wrap: wrap;
    gap: 16rpx;
  }

  &__panel-footer {
    display: flex;
    justify-content: flex-end;
    gap: 16rpx;
    margin-top: 24rpx;
    padding-top: 24rpx;
    border-top: 1rpx solid rgba(0, 0, 0, 0.06);
  }

  &__mask {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.3);
    z-index: 49;
  }
}
```

**使用示例**:
```vue
<KpFilterBar
  v-model="filterValues"
  :filters="[
    { key: 'gender', label: '性别', type: 'single', options: [{ label: '男', value: 'male' }, { label: '女', value: 'female' }] },
    { key: 'age', label: '年龄', type: 'range', options: [{ label: '18-25', value: '18-25' }, { label: '26-35', value: '26-35' }] },
  ]"
  sticky
  @change="onFilterChange"
/>
```

### 3.17 KpTabBar

_Requirements: 3.17_

**Template 结构**:
```vue
<template>
  <view class="kp-tabbar" :class="{ 'kp-tabbar--glass': glass }">
    <view
      v-for="(item, index) in items"
      :key="index"
      class="kp-tabbar__item"
      :class="{ 'kp-tabbar__item--active': current === index }"
      @click="onChange(index, item.pagePath)"
    >
      <view class="kp-tabbar__icon-wrap">
        <image :src="current === index ? item.activeIcon : item.icon" mode="aspectFit" class="kp-tabbar__icon" />
        <view v-if="item.badge" class="kp-tabbar__badge">{{ item.badge > 99 ? '99+' : item.badge }}</view>
      </view>
      <text
        class="kp-tabbar__text"
        :style="{ color: current === index ? activeColor : inactiveColor }"
      >{{ item.text }}</text>
    </view>
    <view class="kp-tabbar__safe-bottom" />
  </view>
</template>
```

**关键样式**:
```scss
.kp-tabbar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  z-index: 100;
  background: $kp-color-card;

  &--glass {
    background: $kp-color-glass;
    backdrop-filter: blur($kp-glass-blur);
    -webkit-backdrop-filter: blur($kp-glass-blur);
    border-top: 1rpx solid $kp-glass-border;
  }

  &__item {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 8rpx 0 4rpx;
  }

  &__icon-wrap {
    position: relative;
  }

  &__icon {
    width: 48rpx;
    height: 48rpx;
  }

  &__badge {
    position: absolute;
    top: -8rpx;
    right: -16rpx;
    min-width: 32rpx;
    height: 32rpx;
    padding: 0 8rpx;
    background: #E53935;
    color: #fff;
    font-size: 20rpx;
    border-radius: $kp-radius-full;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  &__text {
    font-size: 22rpx;
    margin-top: 4rpx;
  }

  &__safe-bottom {
    width: 100%;
    height: constant(safe-area-inset-bottom);
    height: env(safe-area-inset-bottom);
  }
}
```

**使用示例**:
```vue
<KpTabBar
  :current="tabIndex"
  :items="[
    { icon: '/static/tab/home.png', activeIcon: '/static/tab/home-active.png', text: '首页', pagePath: '/pages/home/index' },
    { icon: '/static/tab/mine.png', activeIcon: '/static/tab/mine-active.png', text: '我的', pagePath: '/pages/mine/index' },
  ]"
  @change="switchTab"
/>
```

### 3.18 KpStatusTag

_Requirements: 3.18_

**Template 结构**:
```vue
<template>
  <view class="kp-status-tag" :class="[`kp-status-tag--${status}`, `kp-status-tag--${size}`]">
    <view v-if="dot" class="kp-status-tag__dot" />
    <text class="kp-status-tag__text">{{ statusText }}</text>
  </view>
</template>
```

**关键逻辑**:
```typescript
const STATUS_MAP: Record<string, { text: string; color: string }> = {
  recruiting: { text: '招募中', color: '#4CAF50' },
  paused:     { text: '已暂停', color: '#FF9800' },
  closed:     { text: '已关闭', color: '#999999' },
  pending:    { text: '待审核', color: '#FF6B35' },
  accepted:   { text: '已通过', color: '#4CAF50' },
  rejected:   { text: '已拒绝', color: '#E53935' },
  cancelled:  { text: '已取消', color: '#999999' },
}
```

**关键样式**:
```scss
.kp-status-tag {
  display: inline-flex;
  align-items: center;
  gap: 8rpx;
  border-radius: $kp-radius-full;

  &--small  { padding: 4rpx 16rpx; font-size: 22rpx; }
  &--medium { padding: 6rpx 20rpx; font-size: 24rpx; }

  &--recruiting { background: rgba(#4CAF50, 0.1); color: #4CAF50; }
  &--paused     { background: rgba(#FF9800, 0.1); color: #FF9800; }
  &--closed     { background: rgba(#999, 0.1);    color: #999; }
  &--pending    { background: rgba(#FF6B35, 0.1); color: #FF6B35; }
  &--accepted   { background: rgba(#4CAF50, 0.1); color: #4CAF50; }
  &--rejected   { background: rgba(#E53935, 0.1); color: #E53935; }
  &--cancelled  { background: rgba(#999, 0.1);    color: #999; }

  &__dot {
    width: 12rpx;
    height: 12rpx;
    border-radius: 50%;
    background: currentColor;
  }
}
```

**使用示例**:
```vue
<KpStatusTag status="recruiting" />
<KpStatusTag status="pending" dot size="medium" />
```

### 3.19 KpConfirmDialog

_Requirements: 3.19_

**Template 结构**:
```vue
<template>
  <view v-if="modelValue" class="kp-confirm-dialog">
    <!-- 遮罩 -->
    <view class="kp-confirm-dialog__mask" @click="closeOnClickOverlay && onCancel()" />
    <!-- 对话框 -->
    <view class="kp-confirm-dialog__container">
      <text class="kp-confirm-dialog__title">{{ title }}</text>
      <view class="kp-confirm-dialog__body">
        <slot>
          <text class="kp-confirm-dialog__content">{{ content }}</text>
        </slot>
      </view>
      <slot name="footer">
        <view class="kp-confirm-dialog__footer">
          <KpButton v-if="showCancel" variant="secondary" block @click="onCancel">{{ cancelText }}</KpButton>
          <KpButton :variant="confirmVariant" block @click="onConfirm">{{ confirmText }}</KpButton>
        </view>
      </slot>
    </view>
  </view>
</template>
```

**关键样式**:
```scss
.kp-confirm-dialog {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;

  &__mask {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
  }

  &__container {
    position: relative;
    width: 560rpx;
    background: $kp-color-card;
    border-radius: $kp-radius-lg;
    padding: 48rpx 40rpx 40rpx;
    z-index: 1;
  }

  &__title {
    font-size: 34rpx;
    font-weight: 600;
    color: $kp-color-text-primary;
    text-align: center;
  }

  &__body {
    margin: 24rpx 0 40rpx;
  }

  &__content {
    font-size: 28rpx;
    color: $kp-color-text-secondary;
    text-align: center;
    line-height: 1.6;
  }

  &__footer {
    display: flex;
    gap: 20rpx;
  }
}
```

**使用示例**:
```vue
<KpConfirmDialog
  v-model="showLogout"
  title="退出登录"
  content="确定要退出当前账号吗？"
  confirm-variant="danger"
  @confirm="doLogout"
  @cancel="showLogout = false"
/>
```

## 4. 组件复用矩阵

| 组件 | 登录 | 角色选择 | 首页(演) | 首页(剧) | 角色详情 | 申请确认 | 我的申请 | 演员编辑 | 我的 | 项目创建 | 角色创建 | 申请管理 | 演员详情 | 公司编辑 |
|------|:----:|:-------:|:-------:|:-------:|:-------:|:-------:|:-------:|:-------:|:---:|:-------:|:-------:|:-------:|:-------:|:-------:|
| KpPageLayout | x | x | x | x | x | x | x | x | x | x | x | x | x | x |
| KpNavBar | x | x | x | x | x | x | x | x | — | x | x | x | x | x |
| KpCard | — | — | x | x | x | x | x | x | x | x | x | x | x | x |
| KpButton | x | x | x | x | x | x | x | x | x | x | x | x | x | x |
| KpTag | — | — | x | — | x | x | — | x | — | — | — | — | x | — |
| KpInput | x | — | — | — | — | — | — | x | — | x | x | — | — | x |
| KpTextarea | — | — | — | — | — | — | — | x | — | x | x | — | — | x |
| KpFormItem | x | — | — | — | — | — | — | x | — | x | x | — | — | x |
| KpImageUploader | — | — | — | — | — | — | — | x | — | — | — | — | — | — |
| KpVideoUploader | — | — | — | — | — | — | — | x | — | — | — | — | — | — |
| KpRoleCard | — | — | x | — | x | — | — | — | — | — | — | — | — | — |
| KpProjectCard | — | — | — | x | — | — | — | — | — | — | — | — | — | — |
| KpApplyCard | — | — | — | — | — | — | x | — | — | — | — | x | — | — |
| KpActorBrief | — | — | — | — | — | x | — | — | — | — | — | x | — | — |
| KpEmpty | — | — | x | x | — | — | x | — | — | — | — | x | — | — |
| KpFilterBar | — | — | x | — | — | — | — | — | — | — | — | — | — | — |
| KpTabBar | — | — | x | x | — | — | — | — | x | — | — | — | — | — |
| KpStatusTag | — | — | x | — | x | — | x | — | — | — | — | x | — | — |
| KpConfirmDialog | — | x | — | — | — | x | — | — | x | — | — | x | — | — |

## 5. 测试策略

### 5.1 单元测试

每个组件编写单元测试，覆盖：
- Props 默认值与自定义值渲染
- Events 触发与 payload 正确性
- Slots 内容渲染
- 条件渲染（v-if / v-show 分支）
- 边界情况（空数据、超长文本、极端值）

工具：Vitest + @vue/test-utils

### 5.2 视觉回归测试

- 每个组件在 light / dark 模式下截图对比
- 毛玻璃效果在支持/不支持 backdrop-filter 的环境下分别验证
- 不同屏幕尺寸（375px / 414px / 390px）下的布局验证

### 5.3 集成测试

- KpFormItem + KpInput / KpTextarea 组合的表单校验流程
- KpPageLayout + KpNavBar + KpTabBar 的页面骨架完整性
- KpRoleCard / KpProjectCard / KpApplyCard 在列表中的滚动性能
- KpConfirmDialog 的显示/隐藏/事件回调完整流程

### 5.4 兼容性测试

- 微信开发者工具模拟器
- iOS 真机（iPhone SE / iPhone 15）
- Android 真机（主流中端机型）
- 重点验证：毛玻璃效果降级、安全区域适配、胶囊按钮对齐
