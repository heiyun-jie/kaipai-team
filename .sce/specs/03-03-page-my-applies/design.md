# 我的投递页 - 技术设计

## 1. 路由配置

_Requirements: 3.1_

```json
// pages.json
{
  "path": "pages/my-applies/index",
  "style": {
    "navigationStyle": "custom",
    "navigationBarTitleText": "我的投递",
    "backgroundColor": "#121214"
  }
}
```

## 2. 依赖清单

| 类别 | 依赖项 | 来源 |
|------|--------|------|
| 组件 | KpPageLayout | 00-02-shared-components (3.1) |
| 组件 | KpNavBar | 00-02-shared-components (3.2) |
| 组件 | KpApplyCard | 00-02-shared-components (3.13) |
| 组件 | KpStatusTag | 00-02-shared-components (3.18) |
| 组件 | KpEmpty | 00-02-shared-components (3.15) |
| 组件 | KpTabBar | 00-02-shared-components |
| API | getMyApplies(params) | 00-03-shared-utils-api (3.13) api/apply.ts |
| 工具 | formatApplyStatus, formatFee, formatDate | 00-03-shared-utils-api (3.5) utils/format.ts |
| 类型 | Apply, ApplySearchParams, ApplyStatus, PageResult | 00-03-shared-utils-api (3.1) |
| 样式 | Design Tokens ($kp-*) | 00-01-global-style-system |

## 3. 页面状态

_Requirements: 3.2, 3.3_

```typescript
/** Tab 筛选项 */
type TabKey = 'all' | 'pending' | 'approved' | 'rejected';

interface TabItem {
  key: TabKey;
  label: string;
  status?: number; // 对应 API 的 status 参数，all 时不传
}

const tabs: TabItem[] = [
  { key: 'all', label: '全部' },
  { key: 'pending', label: '待审核', status: 1 },
  { key: 'approved', label: '已通过', status: 2 },
  { key: 'rejected', label: '已拒绝', status: 3 },
];

/** 页面响应式状态 */
const activeTab = ref<TabKey>('all');
const list = ref<Apply[]>([]);
const page = ref<number>(1);
const size = ref<number>(10);
const hasMore = ref<boolean>(true);
const loading = ref<boolean>(false);
const refreshing = ref<boolean>(false);
```

## 4. 模板结构

_Requirements: 3.4, 3.5, 3.6_

```vue
<template>
  <KpPageLayout :header-height="200">
    <!-- 深色头部 -->
    <template #header>
      <KpNavBar title="我的投递" />
    </template>

    <!-- 浅色内容区 -->
    <view class="my-applies">
      <!-- Tab 筛选栏 -->
      <view class="my-applies__tabs">
        <view
          v-for="tab in tabs"
          :key="tab.key"
          :class="['tab-item', { 'tab-item--active': activeTab === tab.key }]"
          :aria-selected="activeTab === tab.key"
          role="tab"
          @click="switchTab(tab.key)"
        >
          <text>{{ tab.label }}</text>
        </view>
      </view>

      <!-- 投递列表 -->
      <scroll-view
        v-if="list.length > 0"
        scroll-y
        class="my-applies__list"
        :refresher-enabled="true"
        :refresher-triggered="refreshing"
        @refresherrefresh="onRefresh"
        @scrolltolower="onLoadMore"
      >
        <KpApplyCard
          v-for="item in list"
          :key="item.id"
          :apply="item"
          view-mode="actor"
          :aria-label="`${item.roleName} ${formatApplyStatus(item.status)}`"
          @click="goRoleDetail(item.roleId)"
        >
          <!-- 已通过：显示联系方式 -->
          <template v-if="item.status === 2" #footer>
            <view class="contact-info">
              <text class="contact-info__name">联系人：{{ item.contactName }}</text>
              <text
                class="contact-info__phone"
                @click.stop="callPhone(item.contactPhone)"
              >
                {{ item.contactPhone }}
              </text>
            </view>
          </template>
        </KpApplyCard>

        <!-- 底部加载提示 -->
        <view class="load-tip">
          <text v-if="loading">加载中...</text>
          <text v-else-if="!hasMore">没有更多了</text>
        </view>
      </scroll-view>

      <!-- 空状态 -->
      <KpEmpty
        v-else-if="!loading"
        :type="activeTab === 'all' ? 'apply' : undefined"
        :text="activeTab === 'all' ? '暂无投递记录' : '暂无该状态的投递'"
      >
        <KpButton
          v-if="activeTab === 'all'"
          variant="text"
          @click="goHome"
        >
          去看看有什么角色 →
        </KpButton>
      </KpEmpty>
    </view>
  </KpPageLayout>
</template>
```

**关键样式**:
```scss
.my-applies {
  &__tabs {
    display: flex;
    padding: 24rpx 32rpx;
    gap: 24rpx;
    background: $kp-color-bg;
    position: sticky;
    top: 0;
    z-index: 10;
  }

  &__list {
    padding: 0 32rpx 32rpx;
    height: calc(100vh - 200rpx - 88rpx);
  }
}

.tab-item {
  padding: 12rpx 28rpx;
  border-radius: $kp-radius-full;
  font-size: $kp-font-size-caption;
  color: $kp-color-text-secondary;
  background: $kp-color-card;

  &--active {
    color: #fff;
    background: $kp-color-primary;
  }
}

.contact-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 16rpx;
  border-top: 1rpx solid $kp-color-border;

  &__phone {
    color: $kp-color-primary;
    text-decoration: underline;
  }
}

.load-tip {
  text-align: center;
  padding: 24rpx 0;
  font-size: $kp-font-size-mini;
  color: $kp-color-text-tertiary;
}
```

## 5. 交互逻辑

```typescript
/** 切换 Tab */
function switchTab(key: TabKey): void {
  if (activeTab.value === key) return;
  activeTab.value = key;
  page.value = 1;
  list.value = [];
  hasMore.value = true;
  fetchList();
}

/** 加载列表 */
async function fetchList(): Promise<void> {
  if (loading.value) return;
  loading.value = true;
  try {
    const currentTab = tabs.find((t) => t.key === activeTab.value);
    const params: ApplySearchParams = {
      page: page.value,
      size: size.value,
    };
    if (currentTab?.status !== undefined) {
      params.status = currentTab.status;
    }
    const res = await getMyApplies(params);
    if (page.value === 1) {
      list.value = res.list;
    } else {
      list.value.push(...res.list);
    }
    hasMore.value = list.value.length < res.total;
  } catch {
    uni.showToast({ title: '加载失败，请重试', icon: 'none' });
  } finally {
    loading.value = false;
  }
}

/** 上拉加载更多 */
function onLoadMore(): void {
  if (!hasMore.value || loading.value) return;
  page.value++;
  fetchList();
}

/** 下拉刷新 */
async function onRefresh(): Promise<void> {
  refreshing.value = true;
  page.value = 1;
  list.value = [];
  hasMore.value = true;
  await fetchList();
  refreshing.value = false;
}

/** 跳转角色详情 */
function goRoleDetail(roleId: number): void {
  uni.navigateTo({ url: `/pages/role-detail/index?id=${roleId}` });
}

/** 拨打电话 */
function callPhone(phone: string): void {
  uni.makePhoneCall({ phoneNumber: phone });
}

/** 跳转首页 */
function goHome(): void {
  uni.switchTab({ url: '/pages/home/index' });
}
```

## 6. 生命周期

_Requirements: 3.1, 3.2_

```typescript
import { onLoad, onShow } from '@dcloudio/uni-app';

onLoad(() => {
  fetchList();
});

onShow(() => {
  // 从其他页面返回时刷新列表（如投递状态可能已变更）
  if (list.value.length > 0) {
    page.value = 1;
    list.value = [];
    hasMore.value = true;
    fetchList();
  }
});
```

## 7. 跳转关系

_Requirements: 3.4, 3.6_

| 触发 | 目标页面 | 参数 | 方式 |
|------|----------|------|------|
| 点击投递卡片 | pages/role-detail/index | id={roleId} | uni.navigateTo |
| 点击联系电话 | 系统拨号 | phoneNumber | uni.makePhoneCall |
| 空状态引导按钮 | pages/home/index | — | uni.switchTab |
| 点击导航栏返回 | 上一页 | — | uni.navigateBack |
