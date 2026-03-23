# 新建项目页 - 技术设计

## 1. 路由配置

_Requirements: 3.1_

**pages.json 注册**:
```json
{
  "path": "pages/project/create",
  "style": {
    "navigationStyle": "custom",
    "navigationBarTitleText": "发布项目"
  }
}
```

**权限守卫**: `onLoad` 中检查 `useUserStore().isCrew`，非剧组用户 `reLaunch` 到首页。

## 2. 依赖清单

| 依赖 | 来源 | 用途 |
|------|------|------|
| `KpPageLayout` | 00-02-shared-components §3.1 | 深色头部 + 浅色内容区骨架 |
| `KpNavBar` | 00-02-shared-components §3.2 | 导航栏，标题"发布项目" |
| `KpFormItem` | 00-02-shared-components §3.8 | 表单项容器 |
| `KpInput` | 00-02-shared-components §3.6 | 项目名称输入 |
| `KpTextarea` | 00-02-shared-components §3.7 | 项目简介输入 |
| `KpButton` | 00-02-shared-components §3.4 | 底部发布按钮 |
| `useUserStore` | 00-03-shared-utils-api §3.7 | 用户角色判断 |
| `createProject` | 00-03-shared-utils-api §3.11 | 创建项目 API |
| `requiredRule` | 00-03-shared-utils-api §3.6 | 表单校验规则 |

## 3. 页面状态

_Requirements: 3.2, 3.3, 3.4, 3.5_

```typescript
interface FormState {
  title: string;        // 项目名称，必填，max 50
  location: string;     // 拍摄地点，必填
  description: string;  // 项目简介，选填，max 500
}

interface PageState {
  form: FormState;
  errors: Partial<Record<keyof FormState, string>>;
  submitting: boolean;
}
```

**初始值**:
```typescript
const form = reactive<FormState>({
  title: '',
  location: '',
  description: '',
});
const errors = reactive<Partial<Record<keyof FormState, string>>>({});
const submitting = ref(false);
```

## 4. 模板结构

_Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

```vue
<template>
  <KpPageLayout :header-height="200" :scrollable="true">
    <!-- 深色头部 -->
    <template #header>
      <KpNavBar title="发布项目" />
    </template>

    <!-- 白色内容区：表单 -->
    <view class="project-create">
      <view class="project-create__form">
        <!-- 3.2 项目名称 -->
        <KpFormItem label="项目名称" required :error="errors.title">
          <KpInput
            v-model="form.title"
            placeholder="请输入项目名称"
            :maxlength="50"
            @blur="validateField('title')"
          />
        </KpFormItem>

        <!-- 3.3 拍摄地点 -->
        <KpFormItem label="拍摄地点" required :error="errors.location">
          <KpInput
            v-model="form.location"
            placeholder="请选择拍摄城市"
            :disabled="true"
            suffix-icon="arrow-right"
            @click-suffix="openCityPicker"
            @click="openCityPicker"
          />
        </KpFormItem>

        <!-- 3.4 项目简介 -->
        <KpFormItem label="项目简介">
          <KpTextarea
            v-model="form.description"
            placeholder="请输入项目简介（选填）"
            :maxlength="500"
            show-count
            auto-height
          />
        </KpFormItem>
      </view>
    </view>

    <!-- 固定底部按钮 -->
    <view class="project-create__footer">
      <KpButton
        variant="primary"
        size="large"
        block
        :loading="submitting"
        :disabled="submitting"
        @click="handleSubmit"
      >
        发布项目
      </KpButton>
    </view>
  </KpPageLayout>
</template>
```

**关键样式**:
```scss
.project-create {
  padding: 32rpx;

  &__form {
    background: $kp-color-card;
    border-radius: $kp-radius-lg;
    padding: 32rpx;
  }

  &__footer {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    padding: 24rpx 32rpx;
    padding-bottom: calc(24rpx + env(safe-area-inset-bottom));
    background: $kp-color-card;
    box-shadow: 0 -4rpx 16rpx rgba(0, 0, 0, 0.06);
  }
}
```

## 5. 交互逻辑

### 5.1 城市选择器

_Requirements: 3.3_

```typescript
function openCityPicker(): void {
  // 使用 uni-app 内置城市选择或自定义 picker
  uni.chooseLocation({
    success: (res) => {
      form.location = res.name || res.address;
      clearError('location');
    },
  });
}
```

> 备选方案：若 `uni.chooseLocation` 不满足需求，可使用 `picker mode="region"` 实现省市区三级联动，取城市名。

### 5.2 表单校验

_Requirements: 3.5_

```typescript
function validateField(field: keyof FormState): boolean {
  if (field === 'title' && !form.title.trim()) {
    errors.title = '请输入项目名称';
    return false;
  }
  if (field === 'location' && !form.location.trim()) {
    errors.location = '请选择拍摄地点';
    return false;
  }
  errors[field] = '';
  return true;
}

function validateAll(): boolean {
  const titleOk = validateField('title');
  const locationOk = validateField('location');
  return titleOk && locationOk;
}

function clearError(field: keyof FormState): void {
  errors[field] = '';
}
```

### 5.3 提交发布

_Requirements: 3.5_

```typescript
async function handleSubmit(): Promise<void> {
  if (!validateAll()) return;
  if (submitting.value) return;

  submitting.value = true;
  try {
    await createProject({
      title: form.title.trim(),
      location: form.location.trim(),
      description: form.description.trim(),
    });
    uni.showToast({ title: '发布成功，去添加角色吧', icon: 'none', duration: 2000 });
    setTimeout(() => {
      uni.switchTab({ url: '/pages/home/index' });
    }, 500);
  } catch {
    // 错误已由 request 封装统一处理
  } finally {
    submitting.value = false;
  }
}
```

## 6. 生命周期

_Requirements: 3.1_

```typescript
onLoad(() => {
  const userStore = useUserStore();
  if (!userStore.isCrew) {
    uni.reLaunch({ url: '/pages/home/index' });
    return;
  }
});
```

## 7. 跳转关系

| 触发 | 目标页面 | 方式 | 条件 |
|------|---------|------|------|
| 点击返回按钮 | 上一页 | `navigateBack` | — |
| 发布成功 | 剧组首页 `pages/home/index` | `switchTab` | API 返回成功 |
