# 投递确认页 - 技术设计

## 1. 路由配置

```json
// pages.json
{
  "path": "pages/apply-confirm/index",
  "style": {
    "navigationStyle": "custom",
    "navigationBarTitleText": "确认投递",
    "backgroundColor": "#121214"
  }
}
```

页面参数：通过 URL query 传递 `roleId`。
```
/pages/apply-confirm/index?roleId=123
```

## 2. 依赖清单

| 类别 | 依赖项 | 来源 Spec |
|------|--------|-----------|
| 布局组件 | KpPageLayout | 00-02-shared-components |
| 导航组件 | KpNavBar | 00-02-shared-components |
| 容器组件 | KpCard | 00-02-shared-components |
| 按钮组件 | KpButton | 00-02-shared-components |
| 业务组件 | KpActorBrief | 00-02-shared-components |
| 输入组件 | KpTextarea | 00-02-shared-components |
| API | submitApply(roleId, remark) | 00-03-shared-utils-api (api/apply.ts) |
| API | getRole(id) | 00-03-shared-utils-api (api/role.ts) |
| API | getActorProfile(userId) | 00-03-shared-utils-api (api/actor.ts) |
| Store | useUserStore | 00-03-shared-utils-api (stores/user.ts) |
| 类型 | Role, ActorProfile | 00-03-shared-utils-api (types/) |
| 样式 | Design Tokens ($kp-*) | 00-01-global-style-system |

## 3. 页面状态

_Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

```typescript
const roleId = ref<number>(0);
const roleDetail = ref<Role | null>(null);
const actorProfile = ref<ActorProfile | null>(null);
const remark = ref<string>('');
const loading = ref<boolean>(true);
const submitting = ref<boolean>(false);
```

页面状态枚举：
- `loading`: 数据加载中
- `ready`: 数据加载完成，可提交
- `submitting`: 投递提交中
- `profileIncomplete`: 档案不完整，需跳转编辑

## 4. 模板结构

_Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

```vue
<template>
  <KpPageLayout :header-height="200">
    <!-- 深色头部 -->
    <template #header>
      <KpNavBar title="确认投递" />
    </template>

    <!-- 白色内容区 -->
    <view class="apply-confirm-content">
      <!-- 角色摘要卡片 -->
      <KpCard shadow :radius="24" padding="32rpx">
        <template #header>
          <text class="section-title">角色信息</text>
        </template>
        <view class="role-summary">
          <view class="role-summary__row">
            <text class="role-summary__label">角色名称</text>
            <text class="role-summary__value">{{ roleDetail?.roleName }}</text>
          </view>
          <view class="role-summary__row">
            <text class="role-summary__label">所属项目</text>
            <text class="role-summary__value">{{ roleDetail?.projectName }}</text>
          </view>
          <view class="role-summary__row">
            <text class="role-summary__label">剧组公司</text>
            <text class="role-summary__value">{{ roleDetail?.companyName }}</text>
          </view>
        </view>
      </KpCard>

      <!-- 演员档案预览 -->
      <KpCard shadow :radius="24" padding="32rpx">
        <template #header>
          <view class="profile-header">
            <text class="section-title">我的档案</text>
            <text class="profile-edit-link" @click="goEditProfile">查看/编辑档案 →</text>
          </view>
        </template>
        <KpActorBrief
          v-if="actorProfile"
          :actor="actorProfile"
          :clickable="false"
        />
      </KpCard>

      <!-- 备注输入 -->
      <KpCard shadow :radius="24" padding="32rpx">
        <template #header>
          <text class="section-title">备注（选填）</text>
        </template>
        <KpTextarea
          v-model="remark"
          placeholder="可以补充说明你的优势或特殊情况"
          :maxlength="200"
          show-count
          auto-height
          :min-height="160"
        />
      </KpCard>

      <!-- 底部占位 -->
      <view class="bottom-placeholder" />
    </view>

    <!-- 固定底部按钮 -->
    <view class="fixed-bottom">
      <KpButton
        variant="primary"
        size="large"
        block
        :loading="submitting"
        :disabled="submitting"
        @click="handleSubmit"
      >
        确认投递
      </KpButton>
    </view>
  </KpPageLayout>
</template>
```

## 5. 交互逻辑

_Requirements: 3.3, 3.5_

```typescript
const userStore = useUserStore();

/** 检查档案完整性 */
function isProfileComplete(profile: ActorProfile | null): boolean {
  if (!profile) return false;
  return !!(profile.name && profile.gender && profile.age && profile.height);
}

/** 跳转编辑档案 */
function goEditProfile(): void {
  uni.navigateTo({ url: '/pages/actor-profile/edit' });
}

/** 提交投递 */
async function handleSubmit(): Promise<void> {
  // 档案完整性校验
  if (!isProfileComplete(actorProfile.value)) {
    uni.showToast({ title: '请先完善个人档案', icon: 'none' });
    setTimeout(() => {
      uni.navigateTo({ url: '/pages/actor-profile/edit' });
    }, 1500);
    return;
  }

  if (submitting.value) return;
  submitting.value = true;

  try {
    await submitApply(roleId.value, remark.value || undefined);
    uni.showToast({ title: '投递成功', icon: 'success' });
    setTimeout(() => {
      uni.navigateBack();
    }, 1500);
  } catch (err) {
    // 错误提示由 request 层统一处理
  } finally {
    submitting.value = false;
  }
}
```

## 6. 生命周期

_Requirements: 3.2, 3.3_

```typescript
import { onLoad } from '@dcloudio/uni-app';

onLoad((options) => {
  roleId.value = Number(options?.roleId || 0);
  if (!roleId.value) {
    uni.showToast({ title: '参数错误', icon: 'none' });
    setTimeout(() => uni.navigateBack(), 1500);
    return;
  }
  fetchData();
});

async function fetchData(): Promise<void> {
  loading.value = true;
  try {
    // 并行请求角色信息和演员档案
    const [role, profile] = await Promise.all([
      getRole(roleId.value),
      getActorProfile(userStore.userId!),
    ]);
    roleDetail.value = role;
    actorProfile.value = profile;

    // 档案不完整时提醒
    if (!isProfileComplete(profile)) {
      uni.showToast({ title: '请先完善个人档案', icon: 'none' });
    }
  } catch (err) {
    uni.showToast({ title: '加载失败', icon: 'none' });
  } finally {
    loading.value = false;
  }
}
```

## 7. 跳转关系

_Requirements: 3.3, 3.5_

| 触发 | 目标页面 | 参数 | 方式 |
|------|----------|------|------|
| 点击"查看/编辑档案 →" | pages/actor-profile/edit | — | uni.navigateTo |
| 档案不完整时自动跳转 | pages/actor-profile/edit | — | uni.navigateTo |
| 投递成功后 | 上一页（角色详情页） | — | uni.navigateBack |
| 点击导航栏返回 | 上一页（角色详情页） | — | uni.navigateBack |
