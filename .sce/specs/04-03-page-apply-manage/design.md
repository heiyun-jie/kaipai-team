# 投递管理页（剧组端） - 技术设计

## 1. 路由配置

_Requirements: 3.1_

```json
// pages.json
{
  "path": "pages/apply-manage/index",
  "style": {
    "navigationStyle": "custom",
    "navigationBarTitleText": "投递管理"
  }
}
```

页面参数通过 `onLoad(options)` 接收：

```typescript
interface PageParams {
  roleId: string;
}
```

## 2. 依赖清单

| 类别 | 依赖项 | 来源 |
|------|--------|------|
| 组件 | KpPageLayout | 00-02-shared-components (3.1) |
| 组件 | KpNavBar | 00-02-shared-components (3.2) |
| 组件 | KpCard | 00-02-shared-components (3.3) |
| 组件 | KpButton | 00-02-shared-components (3.4) |
| 组件 | KpStatusTag | 00-02-shared-components (3.18) |
| 组件 | KpActorBrief | 00-02-shared-components (3.14) |
| 组件 | KpConfirmDialog | 00-02-shared-components (3.19) |
| 组件 | KpEmpty | 00-02-shared-components (3.15) |
| API | getAppliesByRole | 00-03-shared-utils-api (3.13) |
| API | approveApply | 00-03-shared-utils-api (3.13) |
| API | rejectApply | 00-03-shared-utils-api (3.13) |
| API | getRole | 00-03-shared-utils-api (3.12) |
| 类型 | Apply, ApplyStatus | 00-03-shared-utils-api (3.1) |
| 类型 | PageResult | 00-03-shared-utils-api (3.1) |
| 工具 | formatApplyStatus | 00-03-shared-utils-api (3.5) |

## 3. 页面状态

_Requirements: 3.2, 3.3_

```typescript
/** 状态筛选 Tab 定义 */
interface TabItem {
  label: string;
  status: ApplyStatus | null; // null 表示全部
  count: number;
}

/** 投递列表项（含演员摘要） */
interface ApplyListItem extends Apply {
  actorName: string;
  actorAvatar: string;
  actorGender: string;
  actorAge: number;
  actorHeight: number;
  actorIntro: string;
}

/** 页面响应式状态 */
const roleId = ref<number>(0);
const roleName = ref<string>('');
const projectName = ref<string>('');
const activeTab = ref<number>(0);          // 当前 Tab 索引
const applyList = ref<ApplyListItem[]>([]); // 当前列表数��
const loading = ref<boolean>(false);        // 列表加载中
const page = ref<number>(1);
const pageSize = ref<number>(10);
const total = ref<number>(0);
const hasMore = ref<boolean>(true);
const actionLoading = ref<boolean>(false);  // 审核操作加载中

/** 确认对话框状态 */
const showConfirm = ref<boolean>(false);
const confirmAction = ref<'approve' | 'reject'>('approve');
const confirmApplyId = ref<number>(0);

/** Tab 列表 */
const tabs = ref<TabItem[]>([
  { label: '全部', status: null, count: 0 },
  { label: '待审核', status: ApplyStatus.Pending, count: 0 },
  { label: '通过', status: ApplyStatus.Approved, count: 0 },
  { label: '拒绝', status: ApplyStatus.Rejected, count: 0 },
]);

## 4. 模板结构

_Requirements: 3.2, 3.3, 3.4, 3.5, 3.6, 3.7_

```vue
<template>
  <KpPageLayout @scrolltolower="loadMore">
    <!-- 深色头部 -->
    <template #header>
      <KpNavBar title="投递管理" />
      <view class="header-info">
        <text class="header-info__role">{{ roleName }}</text>
        <text class="header-info__project">{{ projectName }}</text>
        <text class="header-info__count">共 {{ total }} 份投递</text>
      </view>
    </template>

    <!-- 浅色内容区 -->
    <!-- Tab 筛选栏 -->
    <view class="tab-bar">
      <view
        v-for="(tab, index) in tabs"
        :key="index"
        class="tab-bar__item"
        :class="{ 'tab-bar__item--active': activeTab === index }"
        @click="switchTab(index)"
      >
        <text>{{ tab.label }}({{ tab.count }})</text>
      </view>
    </view>

    <!-- 投递卡片列表 -->
    <view class="apply-list">
      <KpCard
        v-for="item in applyList"
        :key="item.id"
        mode="light"
        shadow
        :radius="24"
        class="apply-card"
      >
        <!-- 演员摘要 -->
        <KpActorBrief
          :actor="{
            id: String(item.actorId),
            name: item.actorName,
            avatar: item.actorAvatar,
            gender: item.actorGender,
            age: item.actorAge,
            height: item.actorHeight,
            weight: 0,
          }"
          :clickable="false"
        />
        <!-- 介绍片段 -->
        <text v-if="item.actorIntro" class="apply-card__intro">
          {{ item.actorIntro }}
        </text>
        <!-- 备注 -->
        <text v-if="item.remark" class="apply-card__remark">
          备注：{{ item.remark }}
        </text>
        <!-- 操作区 -->
        <template #footer>
          <view v-if="item.status === ApplyStatus.Pending" class="apply-card__actions">
            <KpButton variant="secondary" size="small" @click="goActorProfile(item.actorId)">
              查看档案
            </KpButton>
            <KpButton variant="primary" size="small" :loading="actionLoading" @click="onApprove(item.id)">
              通过
            </KpButton>
            <KpButton variant="secondary" size="small" :loading="actionLoading" @click="onReject(item.id)">
              拒绝
            </KpButton>
          </view>
          <view v-else class="apply-card__status">
            <KpStatusTag :status="getStatusKey(item.status)" />
          </view>
        </template>
      </KpCard>
    </view>

    <!-- 空状态 -->
    <KpEmpty v-if="!loading && applyList.length === 0" type="apply" text="暂无投递记录" />

    <!-- 确认对话框 -->
    <KpConfirmDialog
      v-model="showConfirm"
      :title="confirmAction === 'approve' ? '通过投递' : '拒绝投递'"
      :content="confirmAction === 'approve' ? '确定通过该演员的投递吗？' : '确定拒绝该演员的投递吗？'"
      :confirm-variant="confirmAction === 'approve' ? 'primary' : 'danger'"
      @confirm="handleConfirmAction"
    />
  </KpPageLayout>
</template>
```

## 5. 交互逻辑

_Requirements: 3.3, 3.5, 3.6, 3.7_

```typescript
/** 切换 Tab */
function switchTab(index: number): void {
  activeTab.value = index;
  page.value = 1;
  applyList.value = [];
  hasMore.value = true;
  fetchApplyList();
}

/** 获取投递列表 */
async function fetchApplyList(): Promise<void> {
  if (loading.value || !hasMore.value) return;
  loading.value = true;
  try {
    const status = tabs.value[activeTab.value].status;
    const params: ApplySearchParams = {
      page: page.value,
      size: pageSize.value,
      ...(status !== null ? { status } : {}),
    };
    const result = await getAppliesByRole(roleId.value, params);
    applyList.value = page.value === 1 ? result.list : [...applyList.value, ...result.list];
    total.value = result.total;
    hasMore.value = applyList.value.length < result.total;
    page.value++;
  } finally {
    loading.value = false;
  }
}

/** 加载更多 */
function loadMore(): void {
  if (hasMore.value) fetchApplyList();
}

/** 跳转演员档案 */
function goActorProfile(actorId: number): void {
  uni.navigateTo({ url: `/pages/actor-profile/detail?actorId=${actorId}` });
}

/** 触发通过确认 */
function onApprove(applyId: number): void {
  confirmAction.value = 'approve';
  confirmApplyId.value = applyId;
  showConfirm.value = true;
}

/** 触发拒绝确认 */
function onReject(applyId: number): void {
  confirmAction.value = 'reject';
  confirmApplyId.value = applyId;
  showConfirm.value = true;
}

/** 执行审核操作 */
async function handleConfirmAction(): Promise<void> {
  if (actionLoading.value) return;
  actionLoading.value = true;
  try {
    if (confirmAction.value === 'approve') {
      await approveApply(confirmApplyId.value);
      uni.showToast({ title: '已通过', icon: 'success' });
    } else {
      await rejectApply(confirmApplyId.value);
      uni.showToast({ title: '已拒绝', icon: 'none' });
    }
    // 刷新列表和计数
    page.value = 1;
    applyList.value = [];
    hasMore.value = true;
    await fetchApplyList();
    await updateTabCounts();
  } finally {
    actionLoading.value = false;
    showConfirm.value = false;
  }
}

/** 更新各 Tab 数量 */
async function updateTabCounts(): Promise<void> {
  const allResult = await getAppliesByRole(roleId.value, { page: 1, size: 1 });
  tabs.value[0].count = allResult.total;
  for (let i = 1; i < tabs.value.length; i++) {
    const s = tabs.value[i].status!;
    const r = await getAppliesByRole(roleId.value, { page: 1, size: 1, status: s });
    tabs.value[i].count = r.total;
  }
}

/** 状态数值转 KpStatusTag key */
function getStatusKey(status: ApplyStatus): string {
  const map: Record<number, string> = {
    [ApplyStatus.Pending]: 'pending',
    [ApplyStatus.Approved]: 'accepted',
    [ApplyStatus.Rejected]: 'rejected',
  };
  return map[status] || 'pending';
}
```

## 6. 生命周期

_Requirements: 3.1, 3.2_

```typescript
onLoad(async (options: PageParams) => {
  if (!options?.roleId) {
    uni.showToast({ title: '参数错误', icon: 'none' });
    setTimeout(() => uni.navigateBack(), 1500);
    return;
  }
  roleId.value = Number(options.roleId);

  // 获取角色信息（名称、项目名）
  try {
    const role = await getRole(roleId.value);
    roleName.value = role.roleName;
    // projectName 从 role 关联数据或额外请求获取
    projectName.value = role.projectName || '';
  } catch {
    // 角色信息获取失败不阻塞列表加载
  }

  // 加载投递列表和 Tab 计数
  await fetchApplyList();
  await updateTabCounts();
});
```

## 7. 跳转关系

_Requirements: 3.7_

| 来源 | 目标 | 触发条件 | 携带参数 |
|------|------|----------|----------|
| 角色管理/角色详情 | 本页面 | 点击"查看投递" | `roleId` |
| 本页面 | 演员详情查看页 | 点击"查看档案" | `actorId` |
| 本页面 | 上一页 | 点击导航栏返回 | — |
