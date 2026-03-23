# 首页演员视角 - 技术设计

## 1. 页面路由配置

_Requirements: 3.1_

```jsonc
// pages.json 片段
{
  "pages": [
    {
      "path": "pages/home/index",
      "style": {
        "navigationStyle": "custom",
        "enablePullDownRefresh": true,
        "backgroundTextStyle": "light",
        "backgroundColor": "#121214"
      }
    }
  ],
  "tabBar": {
    "custom": true,
    "list": [
      { "pagePath": "pages/home/index", "text": "首页" },
      { "pagePath": "pages/mine/index", "text": "我的" }
    ]
  }
}
```

角色视角切换逻辑：`pages/home/index` 为统一入口，内部通过 `useUserStore().isActor` 条件渲染演员视角或剧组视角组件。

## 2. 依赖清单

| 类别 | 依赖项 | 来源 Spec |
|------|--------|-----------|
| 组件 | `KpPageLayout` | 00-02-shared-components §3.1 |
| 组件 | `KpRoleCard` | 00-02-shared-components §3.11 |
| 组件 | `KpFilterBar` | 00-02-shared-components §3.16 |
| 组件 | `KpTabBar` | 00-02-shared-components §3.17 |
| 组件 | `KpEmpty` | 00-02-shared-components §3.15 |
| API | `searchRoles` | 00-03-shared-utils-api §3.12 |
| Store | `useUserStore` | 00-03-shared-utils-api §3.7 |
| 工具 | `formatFee`, `formatAge` | 00-03-shared-utils-api §3.5 |
| 类型 | `Role`, `RoleSearchParams`, `PageResult` | 00-03-shared-utils-api §3.1 |
| 样式 | `$kp-*` Design Tokens, `@mixin kp-*` | 00-01-global-style-system |

## 3. 页面状态定义

_Requirements: 3.2, 3.4, 3.5_

```typescript
// pages/home/composables/useActorHome.ts
import { ref, reactive, computed } from 'vue'
import { searchRoles } from '@/api/role'
import type { Role, RoleSearchParams } from '@/types/role'
import type { PageResult } from '@/types/common'

interface FilterState {
  gender: string       // '' | 'male' | 'female'
  age: string          // '' | '18-25' | '25-35' | '35+'
  city: string         // '' | 城市名
  fee: string          // '' | 'negotiable' | '0-300' | '300-800' | '800+'
}

export function useActorHome() {
  // 列表数据
  const roleList = ref<Role[]>([])
  const page = ref(1)
  const size = ref(10)
  const total = ref(0)
  const loading = ref(false)
  const refreshing = ref(false)

  // 搜索
  const keyword = ref('')
  const searchTimer = ref<ReturnType<typeof setTimeout> | null>(null)

  // 筛选
  const filters = reactive<FilterState>({
    gender: '',
    age: '',
    city: '',
    fee: '',
  })

  // 计算属性
  const hasMore = computed(() => roleList.value.length < total.value)
  const isEmpty = computed(() => !loading.value && roleList.value.length === 0)
  const isFiltering = computed(() =>
    !!(keyword.value || filters.gender || filters.age || filters.city || filters.fee)
  )

  return {
    roleList, page, size, total, loading, refreshing,
    keyword, searchTimer, filters,
    hasMore, isEmpty, isFiltering,
  }
}
```

## 4. 模板结构

_Requirements: 3.1, 3.4, 3.5, 3.6, 3.7_

```vue
<template>
  <view class="kp-page">
    <!-- 深色头部：搜索 + 筛选 -->
    <view class="kp-header home-header">
      <view class="home-header__status-bar" :style="{ height: statusBarHeight + 'px' }" />
      <!-- 搜索栏 -->
      <view class="home-header__search">
        <view class="home-header__search-input">
          <u-icon name="search" color="rgba(255,255,255,0.5)" size="16" />
          <input
            v-model="keyword"
            class="home-header__input"
            placeholder="搜索角色、项目..."
            placeholder-class="home-header__placeholder"
            confirm-type="search"
            @input="onSearchInput"
          />
        </view>
      </view>
      <!-- 筛选标签行 -->
      <KpFilterBar
        v-model="filterValues"
        :filters="filterConfig"
        :sticky="false"
        @change="onFilterChange"
      />
    </view>

    <!-- 白色内容区（圆角重叠） -->
    <view class="kp-content home-content">
      <!-- 角色卡片列表 -->
      <view v-if="!isEmpty" class="home-content__list">
        <KpRoleCard
          v-for="role in roleList"
          :key="role.id"
          :role="role"
          @click="onRoleCardClick"
        />
        <!-- 加载更多 -->
        <view v-if="loading" class="home-content__loading">
          <u-loading-icon size="24" />
        </view>
        <view v-else-if="!hasMore" class="home-content__no-more">
          <text>没有更多了</text>
        </view>
      </view>

      <!-- 空状态 -->
      <KpEmpty
        v-else
        :type="isFiltering ? 'search' : 'default'"
        :text="isFiltering ? '未找到相关角色' : '暂无通告'"
      />
    </view>

    <!-- 毛玻璃 TabBar -->
    <KpTabBar :current="0" :items="tabBarItems" @change="onTabChange" />
  </view>
</template>
```

## 5. 交互逻辑

_Requirements: 3.2, 3.3, 3.4, 3.5, 3.6_

```typescript
// pages/home/composables/useActorHome.ts（续）

/** 构建搜索参数 */
function buildSearchParams(): RoleSearchParams {
  const params: RoleSearchParams = {
    page: page.value,
    size: size.value,
  }
  if (keyword.value) params.keyword = keyword.value
  if (filters.gender) params.gender = filters.gender
  if (filters.age) {
    const [min, max] = parseAgeRange(filters.age)
    params.minAge = min
    params.maxAge = max
  }
  if (filters.city) params.city = filters.city
  // fee 筛选映射为后端参数（具体字段视后端接口而定）
  return params
}

/** 加载角色列表 */
async function loadRoles(append = false): Promise<void> {
  if (loading.value) return
  loading.value = true
  try {
    const result: PageResult<Role> = await searchRoles(buildSearchParams())
    if (append) {
      roleList.value.push(...result.list)
    } else {
      roleList.value = result.list
    }
    total.value = result.total
  } catch (err) {
    uni.showToast({ title: '加载失败，请重试', icon: 'none' })
  } finally {
    loading.value = false
  }
}

/** 搜索防抖（300ms） */
function onSearchInput(): void {
  if (searchTimer.value) clearTimeout(searchTimer.value)
  searchTimer.value = setTimeout(() => {
    page.value = 1
    loadRoles()
  }, 300)
}

/** 筛选变化 */
function onFilterChange({ key, value }: { key: string; value: any }): void {
  ;(filters as any)[key] = value
  page.value = 1
  loadRoles()
}

/** 上拉加载更多 */
function onLoadMore(): void {
  if (!hasMore.value || loading.value) return
  page.value++
  loadRoles(true)
}

/** 下拉刷新 */
async function onRefresh(): Promise<void> {
  refreshing.value = true
  page.value = 1
  await loadRoles()
  refreshing.value = false
  uni.stopPullDownRefresh()
}

/** 点击角色卡片 */
function onRoleCardClick({ roleId }: { roleId: string }): void {
  uni.navigateTo({ url: `/pages/role-detail/index?id=${roleId}` })
}
```

## 6. 生命周期

_Requirements: 3.1, 3.2, 3.3_

```typescript
import { onShow, onPullDownRefresh, onReachBottom } from '@dcloudio/uni-app'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

// 页面显示时加载数据
onShow(() => {
  if (userStore.isActor) {
    // 首次进入或从其他页面返回时刷新列表
    page.value = 1
    loadRoles()
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
pages/home/index (演员视角)
├── → /pages/role-detail/index?id={roleId}    [点击角色卡片]
└── → /pages/mine/index                        [TabBar 切换]
```

**筛选配置常量**:

```typescript
const filterConfig = [
  {
    key: 'gender',
    label: '性别',
    type: 'single' as const,
    options: [
      { label: '不限', value: '' },
      { label: '男', value: 'male' },
      { label: '女', value: 'female' },
    ],
  },
  {
    key: 'age',
    label: '年龄',
    type: 'single' as const,
    options: [
      { label: '不限', value: '' },
      { label: '18-25', value: '18-25' },
      { label: '25-35', value: '25-35' },
      { label: '35+', value: '35+' },
    ],
  },
  {
    key: 'city',
    label: '地区',
    type: 'single' as const,
    options: [], // 动态加载城市列表
  },
  {
    key: 'fee',
    label: '报酬',
    type: 'single' as const,
    options: [
      { label: '不限', value: '' },
      { label: '面议', value: 'negotiable' },
      { label: '300以下', value: '0-300' },
      { label: '300-800', value: '300-800' },
      { label: '800+', value: '800+' },
    ],
  },
]

const tabBarItems = [
  {
    icon: '/static/tab/home.png',
    activeIcon: '/static/tab/home-active.png',
    text: '首页',
    pagePath: 'pages/home/index',
  },
  {
    icon: '/static/tab/mine.png',
    activeIcon: '/static/tab/mine-active.png',
    text: '我的',
    pagePath: 'pages/mine/index',
  },
]
```

**关键样式**:

```scss
// pages/home/index.scss
.home-header {
  padding-bottom: $kp-spacing-xl;

  &__search {
    padding: 0 $kp-spacing-page;
    margin-bottom: $kp-spacing-sm;
  }

  &__search-input {
    @include kp-flex-center;
    gap: $kp-spacing-xs;
    height: 72rpx;
    padding: 0 $kp-spacing-card;
    background: rgba(255, 255, 255, 0.1);
    border-radius: $kp-radius-full;
    border: 1rpx solid rgba(255, 255, 255, 0.15);
  }

  &__input {
    flex: 1;
    font-size: $kp-font-size-body;
    color: $kp-color-text-dark-primary;
  }

  &__placeholder {
    color: rgba(255, 255, 255, 0.4);
  }
}

.home-content {
  &__list {
    @include kp-flex-column;
    gap: $kp-spacing-gap;
  }

  &__loading,
  &__no-more {
    @include kp-flex-center;
    padding: $kp-spacing-lg 0;
    color: $kp-color-text-tertiary;
    font-size: $kp-font-size-caption;
  }
}
```
