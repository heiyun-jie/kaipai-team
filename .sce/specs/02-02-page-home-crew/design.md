# 首页剧组视角 - 技术设计

## 1. 页面路由配置

_Requirements: 3.1_

与演员视角共享同一页面文件 `pages/home/index.vue`。路由配置见 02-01-page-home-actor design.md §1。

页面内部通过条件渲染切换视角：

```vue
<!-- pages/home/index.vue -->
<template>
  <HomeActor v-if="userStore.isActor" />
  <HomeCrew v-else-if="userStore.isCrew" />
</template>

<script setup lang="ts">
import { useUserStore } from '@/stores/user'
import HomeActor from './components/HomeActor.vue'
import HomeCrew from './components/HomeCrew.vue'

const userStore = useUserStore()
</script>
```

## 2. 依赖清单

| 类别 | 依赖项 | 来源 Spec |
|------|--------|-----------|
| 组件 | `KpPageLayout` | 00-02-shared-components §3.1 |
| 组件 | `KpProjectCard` | 00-02-shared-components §3.12 |
| 组件 | `KpStatusTag` | 00-02-shared-components §3.18 |
| 组件 | `KpButton` | 00-02-shared-components §3.4 |
| 组件 | `KpTabBar` | 00-02-shared-components §3.17 |
| 组件 | `KpEmpty` | 00-02-shared-components §3.15 |
| API | `getMyProjects` | 00-03-shared-utils-api §3.11 |
| API | `getRolesByProject` | 00-03-shared-utils-api §3.12 |
| Store | `useUserStore` | 00-03-shared-utils-api §3.7 |
| 工具 | `formatDate`, `formatProjectStatus` | 00-03-shared-utils-api §3.5 |
| 类型 | `Project`, `Role`, `PageResult`, `PageParams` | 00-03-shared-utils-api §3.1 |
| 样式 | `$kp-*` Design Tokens, `@mixin kp-*` | 00-01-global-style-system |

## 3. 页面状态定义

_Requirements: 3.2, 3.5_

```typescript
// pages/home/composables/useCrewHome.ts
import { ref, computed } from 'vue'
import { getMyProjects } from '@/api/project'
import { getRolesByProject } from '@/api/role'
import type { Project } from '@/types/project'
import type { Role } from '@/types/role'
import type { PageResult } from '@/types/common'

interface ProjectWithRoles extends Project {
  roles?: Role[]
  rolesLoading?: boolean
  expanded?: boolean
}

export function useCrewHome() {
  // 项目列表
  const projectList = ref<ProjectWithRoles[]>([])
  const page = ref(1)
  const size = ref(10)
  const total = ref(0)
  const loading = ref(false)
  const refreshing = ref(false)

  // 计算属性
  const hasMore = computed(() => projectList.value.length < total.value)
  const isEmpty = computed(() => !loading.value && projectList.value.length === 0)

  return {
    projectList, page, size, total, loading, refreshing,
    hasMore, isEmpty,
  }
}
```

## 4. 模板结构

_Requirements: 3.1, 3.4, 3.5, 3.6, 3.7_

```vue
<!-- pages/home/components/HomeCrew.vue -->
<template>
  <view class="kp-page">
    <!-- 深色头部 -->
    <view class="kp-header crew-header">
      <view class="crew-header__status-bar" :style="{ height: statusBarHeight + 'px' }" />
      <text class="kp-header__title">我的发布</text>
      <text class="kp-header__subtitle">共 {{ total }} 个项目</text>
    </view>

    <!-- 白色内容区 -->
    <view class="kp-content crew-content">
      <!-- 项目卡片列表 -->
      <view v-if="!isEmpty" class="crew-content__list">
        <view
          v-for="project in projectList"
          :key="project.id"
          class="crew-content__item"
        >
          <KpProjectCard
            :project="project"
            @click="onProjectClick(project)"
          />
          <!-- 展开的角色列表 -->
          <view
            v-if="project.expanded"
            class="crew-content__roles"
          >
            <view v-if="project.rolesLoading" class="crew-content__roles-loading">
              <u-loading-icon size="20" />
            </view>
            <view
              v-else-if="project.roles && project.roles.length > 0"
              class="crew-content__role-list"
            >
              <view
                v-for="role in project.roles"
                :key="role.id"
                class="crew-content__role-item"
                @click="onRoleClick(role)"
              >
                <text class="crew-content__role-name">{{ role.roleName }}</text>
                <text class="crew-content__role-fee">{{ formatFee(role.fee) }}</text>
                <u-icon name="arrow-right" size="14" color="#999" />
              </view>
            </view>
            <view v-else class="crew-content__roles-empty">
              <text>暂无角色，去添加</text>
            </view>
          </view>
        </view>

        <!-- 加载更多 -->
        <view v-if="loading" class="crew-content__loading">
          <u-loading-icon size="24" />
        </view>
        <view v-else-if="!hasMore" class="crew-content__no-more">
          <text>没有更多了</text>
        </view>
      </view>

      <!-- 空状态 -->
      <KpEmpty
        v-else
        type="default"
        text="发布你的第一个项目"
        show-action
        action-text="立即发布"
        @action="onCreateProject"
      />
    </view>

    <!-- 固定底部发布按钮 -->
    <view class="crew-fab">
      <KpButton variant="primary" size="large" block @click="onCreateProject">
        ＋ 发布新项目
      </KpButton>
    </view>

    <!-- 毛玻璃 TabBar -->
    <KpTabBar :current="0" :items="tabBarItems" @change="onTabChange" />
  </view>
</template>
```

## 5. 交互逻辑

_Requirements: 3.2, 3.3, 3.5, 3.6_

```typescript
// pages/home/composables/useCrewHome.ts（续）

/** 加载项目列表 */
async function loadProjects(append = false): Promise<void> {
  if (loading.value) return
  loading.value = true
  try {
    const result: PageResult<Project> = await getMyProjects({
      page: page.value,
      size: size.value,
    })
    const items: ProjectWithRoles[] = result.list.map((p) => ({
      ...p,
      roles: undefined,
      rolesLoading: false,
      expanded: false,
    }))
    if (append) {
      projectList.value.push(...items)
    } else {
      projectList.value = items
    }
    total.value = result.total
  } catch (err) {
    uni.showToast({ title: '加载失败，请重试', icon: 'none' })
  } finally {
    loading.value = false
  }
}

/** 点击项目卡片 — 展开/收起角色列表 */
async function onProjectClick(project: ProjectWithRoles): Promise<void> {
  if (project.expanded) {
    project.expanded = false
    return
  }
  project.expanded = true
  // 首次展开时加载角色列表
  if (!project.roles) {
    project.rolesLoading = true
    try {
      const result = await getRolesByProject(project.id)
      project.roles = result.list
    } catch {
      uni.showToast({ title: '加载角色失败', icon: 'none' })
    } finally {
      project.rolesLoading = false
    }
  }
}

/** 点击角色项 — 跳转申请管理 */
function onRoleClick(role: Role): void {
  uni.navigateTo({
    url: `/pages/apply-manage/index?roleId=${role.id}`,
  })
}

/** 发布新项目 */
function onCreateProject(): void {
  uni.navigateTo({ url: '/pages/project/create' })
}

/** 上拉加载更多 */
function onLoadMore(): void {
  if (!hasMore.value || loading.value) return
  page.value++
  loadProjects(true)
}

/** 下拉刷新 */
async function onRefresh(): Promise<void> {
  refreshing.value = true
  page.value = 1
  await loadProjects()
  refreshing.value = false
  uni.stopPullDownRefresh()
}
```

## 6. 生命周期

_Requirements: 3.1, 3.2, 3.3_

```typescript
import { onShow, onPullDownRefresh, onReachBottom } from '@dcloudio/uni-app'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

// 页面显示时加载数据（包括从项目创建页返回后刷新）
onShow(() => {
  if (userStore.isCrew) {
    page.value = 1
    loadProjects()
  }
})

// 下拉刷新
onPullDownRefresh(() => {
  onRefresh()
})

// 触底加载更多
onReachBottom(() => {
  onLoadMore()
})
```

## 7. 页面跳转关系

```
pages/home/index (剧组视角)
├── → /pages/project/create                     [点击"发布新项目"按钮]
├── → /pages/apply-manage/index?roleId={id}    [点击展开的角色项]
└── → /pages/mine/index                         [TabBar 切换]
```

**关键样式**:

```scss
// pages/home/components/HomeCrew.scss
.crew-header {
  padding-bottom: $kp-spacing-lg;
}

.crew-content {
  // 为底部固定按钮留出空间
  padding-bottom: calc(120rpx + env(safe-area-inset-bottom));

  &__list {
    @include kp-flex-column;
    gap: $kp-spacing-gap;
  }

  &__roles {
    margin-top: -#{$kp-spacing-xs};
    margin-left: $kp-spacing-card;
    margin-right: $kp-spacing-card;
    padding: $kp-spacing-sm $kp-spacing-card;
    background: $kp-color-bg;
    border-radius: 0 0 $kp-radius-card $kp-radius-card;
    @include kp-transition(max-height);
  }

  &__role-item {
    @include kp-flex-between;
    padding: $kp-spacing-sm 0;
    border-bottom: 1rpx solid $kp-color-divider;

    &:last-child {
      border-bottom: none;
    }
  }

  &__role-name {
    flex: 1;
    font-size: $kp-font-size-body;
    color: $kp-color-text-primary;
  }

  &__role-fee {
    font-size: $kp-font-size-body;
    color: $kp-color-primary;
    font-weight: $kp-font-weight-medium;
    margin-right: $kp-spacing-xs;
  }

  &__roles-loading,
  &__roles-empty {
    @include kp-flex-center;
    padding: $kp-spacing-lg 0;
    color: $kp-color-text-tertiary;
    font-size: $kp-font-size-caption;
  }

  &__loading,
  &__no-more {
    @include kp-flex-center;
    padding: $kp-spacing-lg 0;
    color: $kp-color-text-tertiary;
    font-size: $kp-font-size-caption;
  }
}

.crew-fab {
  position: fixed;
  bottom: calc(100rpx + env(safe-area-inset-bottom));
  left: $kp-spacing-page;
  right: $kp-spacing-page;
  z-index: 50;
}
```
