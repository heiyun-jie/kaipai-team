# 身份选择页 - 技术设计

## 1. 页面路由配置 (pages.json snippet)

_Requirements: 3.1_

```json
{
  "pages": [
    {
      "path": "pages/role-select/index",
      "style": {
        "navigationStyle": "custom",
        "navigationBarTitleText": "",
        "backgroundColor": "#121214",
        "disableScroll": true,
        "app-plus": {
          "titleNView": false
        }
      }
    }
  ]
}
```

## 2. 依赖清单

### 组件依赖 (from 00-02-shared-components)

| 组件 | 用途 |
|------|------|
| KpCard | 身份选择卡片（glass 模式，280rpx 高度，选中态橙色边框 + 光晕） |
| KpButton | 底部确认按钮（primary, block, large） |
| KpConfirmDialog | 二次确认对话框（"选择后不可更改"提示） |

### API 依赖 (from 00-03-shared-utils-api)

| 函数 | 来源文件 | 用途 |
|------|----------|------|
| `updateUserRole(role)` | `api/auth.ts` | 设置用户身份（1=演员, 2=剧组） |
| `setUserInfo(user)` | `utils/auth.ts` | 更新本地持久化的用户信息 |

### Store 依赖

| Store | 来源文件 | 用途 |
|-------|----------|------|
| `useUserStore` | `stores/user.ts` | 更新用户角色信息、获取当前用户数据 |

## 3. 页面状态定义 (TypeScript ref/reactive)

_Requirements: 3.2, 3.3, 3.4, 3.5_

```typescript
import { ref, computed } from 'vue';
import type { UserInfo } from '@/types/user';

/** 角色类型：1=演员, 2=剧组 */
type RoleType = 1 | 2;

// 选中的角色
const selectedRole = ref<RoleType | null>(null);

// 确认对话框显示状态
const showConfirmDialog = ref<boolean>(false);

// 提交加载状态
const submitLoading = ref<boolean>(false);

// 状态栏高度
const statusBarHeight = ref<number>(0);

// 计算属性
const hasSelection = computed<boolean>(() => selectedRole.value !== null);

const confirmDialogContent = computed<string>(() => {
  const roleName = selectedRole.value === 1 ? '演员' : '剧组';
  return `确定选择【${roleName}】身份？选择后不可更改`;
});

// 卡片配置
const roleCards = [
  {
    role: 1 as RoleType,
    icon: '/static/icon-actor.png',
    title: '我是演员',
    desc: '寻找适合自己的角色，展示才华',
  },
  {
    role: 2 as RoleType,
    icon: '/static/icon-crew.png',
    title: '我是剧组',
    desc: '发布角色需求，寻找合适的演员',
  },
];
```

## 4. 模板结构 (pseudo-template with component composition)

_Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

```vue
<template>
  <view class="role-select" :style="{ background: '#121214' }">
    <!-- 状态栏占位 -->
    <view class="role-select__status-bar" :style="{ height: statusBarHeight + 'px' }" />

    <!-- 标题区域 -->
    <view class="role-select__header">
      <text class="role-select__title">选择你的身份</text>
      <text class="role-select__subtitle">请选择一个身份开始使用</text>
    </view>

    <!-- 身份卡片区域 -->
    <view class="role-select__cards">
      <view
        v-for="card in roleCards"
        :key="card.role"
        class="role-select__card-wrap"
      >
        <KpCard
          mode="dark"
          glass
          :radius="24"
          padding="40rpx"
          :shadow="false"
          :class="{
            'role-select__card--selected': selectedRole === card.role
          }"
          @click="selectRole(card.role)"
        >
          <view class="role-select__card-content">
            <image
              :src="card.icon"
              mode="aspectFit"
              class="role-select__card-icon"
              :class="{ 'role-select__card-icon--active': selectedRole === card.role }"
            />
            <view class="role-select__card-info">
              <text class="role-select__card-title">{{ card.title }}</text>
              <text class="role-select__card-desc">{{ card.desc }}</text>
            </view>
          </view>
        </KpCard>
      </view>
    </view>

    <!-- 底部确认按钮 -->
    <view
      v-if="hasSelection"
      class="role-select__footer"
    >
      <KpButton
        variant="primary"
        size="large"
        block
        :loading="submitLoading"
        @click="handleConfirmClick"
      >
        确认选择
      </KpButton>
    </view>

    <!-- 二次确认对话框 -->
    <KpConfirmDialog
      v-model="showConfirmDialog"
      title="身份确认"
      :content="confirmDialogContent"
      confirm-text="确认"
      cancel-text="取消"
      @confirm="handleConfirmRole"
      @cancel="showConfirmDialog = false"
    />
  </view>
</template>
```

## 5. 交互逻辑 (event handler functions with signatures)

_Requirements: 3.3, 3.4, 3.5, 3.6_

```typescript
import { updateUserRole } from '@/api/auth';
import { setUserInfo } from '@/utils/auth';
import { useUserStore } from '@/stores/user';
import type { UserInfo } from '@/types/user';

const userStore = useUserStore();

/**
 * 选择角色卡片
 * Requirements: 3.3
 */
function selectRole(role: RoleType): void {
  selectedRole.value = role;
}

/**
 * 点击确认按钮 — 打开二次确认对话框
 * Requirements: 3.4, 3.5
 */
function handleConfirmClick(): void {
  if (!hasSelection.value || submitLoading.value) return;
  showConfirmDialog.value = true;
}

/**
 * 二次确认后提交身份选择
 * Requirements: 3.5, 3.6
 */
async function handleConfirmRole(): Promise<void> {
  if (!selectedRole.value || submitLoading.value) return;

  showConfirmDialog.value = false;
  submitLoading.value = true;

  try {
    // 调用 API 设置身份
    await updateUserRole(selectedRole.value);

    // 更新本地用户信息
    const currentUser = userStore.userInfo;
    if (currentUser) {
      const updatedUser: UserInfo = { ...currentUser, role: selectedRole.value };
      userStore.updateProfile({ role: selectedRole.value });
      setUserInfo(updatedUser);
    }

    // 跳转到对应资料编辑页
    navigateToProfileEdit(selectedRole.value);
  } catch (err: any) {
    uni.showToast({ title: err.message || '设置身份失败', icon: 'none' });
  } finally {
    submitLoading.value = false;
  }
}

/**
 * 跳转到对应的资料编辑页
 * Requirements: 3.6
 */
function navigateToProfileEdit(role: RoleType): void {
  const url = role === 1
    ? '/pages/actor-profile/edit'
    : '/pages/company-profile/edit';
  uni.redirectTo({ url });
}
```

## 6. 生命周期

_Requirements: 3.1_

```typescript
import { onLoad } from '@dcloudio/uni-app';

onLoad(() => {
  // 获取状态栏高度用于适配
  const systemInfo = uni.getSystemInfoSync();
  statusBarHeight.value = systemInfo.statusBarHeight || 0;
});
```

## 7. 页面跳转关系

_Requirements: 3.1, 3.6_

```
登录页 (pages/login/index)
  └── [role=空] ──redirectTo──→ 身份选择页 (pages/role-select/index)
                                  ├── [确认演员] ──redirectTo──→ 演员资料编辑页 (pages/actor-profile/edit)
                                  └── [确认剧组] ──redirectTo──→ 剧组资料编辑页 (pages/company-profile/edit)
```

## 8. 关键样式说明

_Requirements: 3.2, 3.3, 3.4_

```scss
.role-select {
  min-height: 100vh;
  background: $kp-color-dark-primary;
  @include kp-flex-column;
  padding: 0 $kp-spacing-page;

  // 标题区域
  &__header {
    margin-top: 120rpx;
    margin-bottom: $kp-spacing-xl;
    text-align: center;
  }

  &__title {
    @include kp-text-h1;
    color: $kp-color-text-dark-primary;
    display: block;
  }

  &__subtitle {
    @include kp-text-body;
    color: $kp-color-text-dark-secondary;
    margin-top: $kp-spacing-xs;
    display: block;
  }

  // 卡片区域
  &__cards {
    @include kp-flex-column;
    gap: $kp-spacing-page; // 32rpx
  }

  &__card-wrap {
    // 选中态样式覆写 KpCard
    .role-select__card--selected {
      border: 2rpx solid $kp-color-primary !important;
      box-shadow: 0 0 40rpx rgba($kp-color-primary, 0.3);
      @include kp-transition(border-color);
    }
  }

  // 卡片内容布局
  &__card-content {
    @include kp-flex-center;
    height: 200rpx; // 280rpx 卡片高度 - 80rpx padding
    gap: $kp-spacing-gap;
  }

  &__card-icon {
    width: 120rpx;
    height: 120rpx;
    opacity: 0.7;
    @include kp-transition(opacity);

    &--active {
      opacity: 1;
    }
  }

  &__card-title {
    @include kp-text-h2;
    color: $kp-color-text-dark-primary;
    display: block;
  }

  &__card-desc {
    @include kp-text-caption;
    color: $kp-color-text-dark-secondary;
    margin-top: $kp-spacing-xs;
    display: block;
  }

  // 底部确认按钮 — 滑入动画
  &__footer {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    padding: $kp-spacing-gap $kp-spacing-page;
    @include kp-safe-area-bottom($kp-spacing-gap);
    animation: slideUp $kp-duration-normal $kp-easing-default;
  }
}

@keyframes slideUp {
  from {
    transform: translateY(100%);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}
```
