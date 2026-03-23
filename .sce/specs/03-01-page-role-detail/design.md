# 角色详情页 - 技术设计

## 1. 路由配置

```json
// pages.json
{
  "path": "pages/role-detail/index",
  "style": {
    "navigationStyle": "custom",
    "navigationBarTitleText": "角色详情",
    "backgroundColor": "#121214"
  }
}
```

页面参数：通过 URL query 传递 `id`（角色 ID）。
```
/pages/role-detail/index?id=123
```

## 2. 依赖清单

| 类别 | 依赖项 | 来源 Spec |
|------|--------|-----------|
| 布局组件 | KpPageLayout | 00-02-shared-components |
| 导航组件 | KpNavBar | 00-02-shared-components |
| 容器组件 | KpCard | 00-02-shared-components |
| 按钮组件 | KpButton | 00-02-shared-components |
| 标签组件 | KpTag | 00-02-shared-components |
| API | getRole(id) | 00-03-shared-utils-api (api/role.ts) |
| API | getMyApplies(params) | 00-03-shared-utils-api (api/apply.ts) |
| 工具函数 | formatFee, formatGender, formatAge, formatPhone, formatDate | 00-03-shared-utils-api (utils/format.ts) |
| Store | useUserStore | 00-03-shared-utils-api (stores/user.ts) |
| 类型 | Role, Project, Company, Apply | 00-03-shared-utils-api (types/) |
| 样式 | Design Tokens ($kp-*) | 00-01-global-style-system |

## 3. 页面状态

_Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6_

```typescript
// 页面响应式状态
const roleId = ref<number>(0);
const roleDetail = ref<Role | null>(null);
const projectInfo = ref<Project | null>(null);
const companyInfo = ref<Company | null>(null);
const applyStatus = ref<'none' | 'applied' | 'approved'>('none');
const isExpired = ref<boolean>(false);
const loading = ref<boolean>(true);
const submitting = ref<boolean>(false);
```

页面状态枚举：
- `loading`: 数据加载中，显示 loading
- `ready`: 数据加载完成，正常展示
- `error`: 加载失败，显示错误提示 + 重试按钮

## 4. 模板结构

_Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6_

```vue
<template>
  <KpPageLayout :header-height="320">
    <!-- 深色头部 -->
    <template #header>
      <KpNavBar title="角色详情" />
      <view class="role-header">
        <text class="role-header__name">{{ roleDetail?.roleName }}</text>
        <text class="role-header__fee">{{ formatFee(roleDetail?.fee) }}</text>
      </view>
    </template>

    <!-- 白色内容区 -->
    <view class="role-detail-content">
      <!-- 角色要求 -->
      <KpCard shadow :radius="24" padding="32rpx">
        <template #header>
          <text class="section-title">角色要求</text>
        </template>
        <view class="info-row">
          <text class="info-label">性别</text>
          <text class="info-value">{{ formatGender(roleDetail?.gender) || '不限' }}</text>
        </view>
        <view class="info-row">
          <text class="info-label">年龄</text>
          <text class="info-value">{{ formatAge(roleDetail?.minAge, roleDetail?.maxAge) || '不限' }}</text>
        </view>
        <view class="info-row">
          <text class="info-label">要求描述</text>
          <text class="info-value">{{ roleDetail?.requirement || '暂无' }}</text>
        </view>
      </KpCard>

      <!-- 项目信息 -->
      <KpCard shadow :radius="24" padding="32rpx">
        <template #header>
          <text class="section-title">项目信息</text>
        </template>
        <view class="info-row">
          <text class="info-label">项目名称</text>
          <text class="info-value">{{ projectInfo?.title }}</text>
        </view>
        <view class="info-row">
          <text class="info-label">拍摄地点</text>
          <text class="info-value">{{ projectInfo?.location }}</text>
        </view>
        <view class="info-row">
          <text class="info-label">项目描述</text>
          <text class="info-value">{{ projectInfo?.description }}</text>
        </view>
      </KpCard>

      <!-- 剧组信息 -->
      <KpCard shadow :radius="24" padding="32rpx">
        <template #header>
          <text class="section-title">剧组信息</text>
        </template>
        <view class="info-row">
          <text class="info-label">公司名称</text>
          <text class="info-value">{{ companyInfo?.companyName }}</text>
        </view>
        <view class="info-row">
          <text class="info-label">联系人</text>
          <text class="info-value">{{ companyInfo?.contactName }}</text>
        </view>
        <view class="info-row">
          <text class="info-label">联系电话</text>
          <text class="info-value">{{ maskedPhone }}</text>
        </view>
      </KpCard>

      <!-- 截止日期 -->
      <view class="deadline-section">
        <text :class="['deadline-text', { 'deadline-text--expired': isExpired }]">
          截止日期：{{ formatDate(roleDetail?.deadline, 'YYYY-MM-DD') }}
          <text v-if="isExpired" class="deadline-tag">已截止</text>
        </text>
      </view>

      <!-- 底部占位（防止固定按钮遮挡内容） -->
      <view class="bottom-placeholder" />
    </view>

    <!-- 固定底部按钮 -->
    <view class="fixed-bottom">
      <KpButton
        variant="primary"
        size="large"
        block
        :disabled="applyStatus !== 'none' || isExpired"
        @click="handleApply"
      >
        {{ bottomButtonText }}
      </KpButton>
    </view>
  </KpPageLayout>
</template>
```

## 5. 交互逻辑

_Requirements: 3.4, 3.6_

```typescript
/** 计算底部按钮文案 */
const bottomButtonText = computed(() => {
  if (isExpired.value) return '已截止';
  if (applyStatus.value === 'applied' || applyStatus.value === 'approved') return '已投递';
  return '立即投递';
});

/** 计算脱敏/完整电话 */
const maskedPhone = computed(() => {
  if (!companyInfo.value?.contactPhone) return '';
  if (applyStatus.value === 'approved') return companyInfo.value.contactPhone;
  return formatPhone(companyInfo.value.contactPhone);
});

/** 点击投递按钮 */
function handleApply(): void {
  if (applyStatus.value !== 'none' || isExpired.value) return;
  uni.navigateTo({ url: `/pages/apply-confirm/index?roleId=${roleId.value}` });
}

/** 判断是否已过截止日期 */
function checkExpired(deadline: string): boolean {
  return new Date(deadline).getTime() < Date.now();
}
```

## 6. 生命周期

_Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6_

```typescript
import { onLoad, onShow } from '@dcloudio/uni-app';

onLoad((options) => {
  roleId.value = Number(options?.id || 0);
  if (!roleId.value) {
    uni.showToast({ title: '参数错误', icon: 'none' });
    setTimeout(() => uni.navigateBack(), 1500);
    return;
  }
  fetchData();
});

onShow(() => {
  // 从投递确认页返回时刷新投递状态
  if (roleId.value) {
    checkApplyStatus();
  }
});

async function fetchData(): Promise<void> {
  loading.value = true;
  try {
    // 并行请求角色详情（含项目和公司信息）
    const role = await getRole(roleId.value);
    roleDetail.value = role;
    // 假设 getRole 返回嵌套的 project 和 company
    // 或分别请求 getProject / getCompanyInfo
    isExpired.value = checkExpired(role.deadline);
    await checkApplyStatus();
  } catch (err) {
    uni.showToast({ title: '加载失败', icon: 'none' });
  } finally {
    loading.value = false;
  }
}

async function checkApplyStatus(): Promise<void> {
  try {
    const applies = await getMyApplies({ page: 1, size: 100, roleId: roleId.value });
    const myApply = applies.list.find((a) => a.roleId === roleId.value);
    if (myApply) {
      applyStatus.value = myApply.status === 2 ? 'approved' : 'applied';
    } else {
      applyStatus.value = 'none';
    }
  } catch {
    // 查询失败不影响页面展示
  }
}
```

## 7. 跳转关系

_Requirements: 3.6_

| 触发 | 目标页面 | 参数 | 方式 |
|------|----------|------|------|
| 点击"立即投递" | pages/apply-confirm/index | roleId | uni.navigateTo |
| 点击导航栏返回 | 上一页 | — | uni.navigateBack |
