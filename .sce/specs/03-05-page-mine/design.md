# 我的页面 - 技术设计

## 1. 路由配置

```json
// pages.json
{
  "path": "pages/mine/index",
  "style": {
    "navigationStyle": "custom",
    "navigationBarTitleText": "我的",
    "backgroundColor": "#121214"
  }
}
```

```json
// pages.json tabBar 配置
{
  "tabBar": {
    "custom": true,
    "list": [
      { "pagePath": "pages/home/index", "text": "首页" },
      { "pagePath": "pages/mine/index", "text": "我的" }
    ]
  }
}
```

该页面为 Tab 页（Tab 2），无 URL 参数。

## 2. 依赖清单

| 类别 | 依赖项 | 来源 Spec |
|------|--------|-----------|
| 布局组件 | KpPageLayout | 00-02-shared-components |
| 标签组件 | KpTag | 00-02-shared-components |
| 对话框组件 | KpConfirmDialog | 00-02-shared-components |
| TabBar 组件 | KpTabBar | 00-02-shared-components |
| Store | useUserStore (userInfo, isActor, isCrew, logout) | 00-03-shared-utils-api (stores/user.ts) |
| 工具函数 | formatPhone | 00-03-shared-utils-api (utils/format.ts) |
| 样式 | Design Tokens ($kp-*) | 00-01-global-style-system |

## 3. 页面状态

_Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

```typescript
const userStore = useUserStore();
const showLogoutDialog = ref<boolean>(false);

/** 演员菜单配置 */
const actorMenus = [
  { icon: 'file-text', label: '我的投递', path: '/pages/my-applies/index' },
  { icon: 'account', label: '我的档案', path: '/pages/actor-profile/edit' },
  { icon: 'info-circle', label: '关于我们', path: '' },
  { icon: 'log-out', label: '退出登录', path: '', action: 'logout' },
];

/** 剧组菜单配置 */
const crewMenus = [
  { icon: 'list', label: '投递管理', path: '/pages/apply-manage/index' },
  { icon: 'home', label: '剧组资料', path: '/pages/company-profile/edit' },
  { icon: 'info-circle', label: '关于我们', path: '' },
  { icon: 'log-out', label: '退出登录', path: '', action: 'logout' },
];

/** 当前菜单列表 */
const menuList = computed(() => {
  return userStore.isActor ? actorMenus : crewMenus;
});
```

## 4. 模板结构

_Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

```vue
<template>
  <KpPageLayout :header-height="320" :scrollable="false">
    <!-- 深色头部 -->
    <template #header>
      <view class="mine-header" @click="goEditProfile">
        <image
          class="mine-header__avatar"
          :src="userStore.userInfo?.avatar || '/static/default-avatar.png'"
          mode="aspectFill"
        />
        <view class="mine-header__info">
          <view class="mine-header__name-row">
            <text class="mine-header__name">{{ userStore.userInfo?.name || '未设置昵称' }}</text>
            <KpTag
              :text="userStore.isActor ? '演员' : '剧组'"
              :type="userStore.isActor ? 'primary' : 'default'"
              size="small"
            />
          </view>
          <text class="mine-header__phone">{{ formatPhone(userStore.userInfo?.phone || '') }}</text>
        </view>
        <text class="mine-header__edit">编辑资料 →</text>
      </view>
    </template>

    <!-- 白色内容区 -->
    <view class="mine-content">
      <view class="menu-list">
        <view
          v-for="(item, index) in menuList"
          :key="index"
          class="menu-item"
          @click="handleMenuClick(item)"
        >
          <view class="menu-item__left">
            <u-icon :name="item.icon" size="20" color="#333" />
            <text class="menu-item__label">{{ item.label }}</text>
          </view>
          <u-icon name="arrow-right" size="16" color="#ccc" />
        </view>
      </view>
    </view>

    <!-- 毛玻璃 TabBar -->
    <KpTabBar :current="1" :items="tabBarItems" @change="onTabChange" />

    <!-- 退出登录确认对话框 -->
    <KpConfirmDialog
      v-model="showLogoutDialog"
      title="提示"
      content="确定要退出登录吗？"
      confirm-variant="danger"
      @confirm="handleLogout"
    />
  </KpPageLayout>
</template>
```

## 5. 交互逻辑

_Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

```typescript
/** TabBar 配置 */
const tabBarItems = [
  { icon: 'home', activeIcon: 'home-fill', text: '首页', pagePath: 'pages/home/index' },
  { icon: 'account', activeIcon: 'account-fill', text: '我的', pagePath: 'pages/mine/index' },
];

/** 跳转编辑资料页 */
function goEditProfile(): void {
  const path = userStore.isActor
    ? '/pages/actor-profile/edit'
    : '/pages/company-profile/edit';
  uni.navigateTo({ url: path });
}

/** 菜单点击处理 */
function handleMenuClick(item: { path: string; action?: string }): void {
  if (item.action === 'logout') {
    showLogoutDialog.value = true;
    return;
  }
  if (item.path) {
    uni.navigateTo({ url: item.path });
  }
}

/** 确认退出登录 */
function handleLogout(): void {
  userStore.logout();
  uni.reLaunch({ url: '/pages/login/index' });
}

/** TabBar 切换 */
function onTabChange(e: { index: number; pagePath: string }): void {
  uni.switchTab({ url: `/${e.pagePath}` });
}
```

## 6. 生命周期

_Requirements: 3.1_

```typescript
import { onShow } from '@dcloudio/uni-app';

onShow(() => {
  // Tab 页每次显示时刷新用户信息
  userStore.initFromStorage();
});
```

## 7. 跳转关系

_Requirements: 3.1, 3.2, 3.3, 3.4_

| 触发 | 目标页面 | 条件 | 方式 |
|------|----------|------|------|
| 点击头像区域 / "编辑资料 →" | pages/actor-profile/edit | 演员角色 | uni.navigateTo |
| 点击头像区域 / "编辑资料 →" | pages/company-profile/edit | 剧组角色 | uni.navigateTo |
| 点击"我的投递" | pages/my-applies/index | 演员角色 | uni.navigateTo |
| 点击"我的档案" | pages/actor-profile/edit | 演员角色 | uni.navigateTo |
| 点击"投递管理" | pages/apply-manage/index | 剧组角色 | uni.navigateTo |
| 点击"剧组资料" | pages/company-profile/edit | 剧组角色 | uni.navigateTo |
| 确认退出登录 | pages/login/index | — | uni.reLaunch |
| TabBar 切换 | 对应 Tab 页 | — | uni.switchTab |
