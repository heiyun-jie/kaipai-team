# 新建角色页 - 技术设计

## 1. 路由配置

_Requirements: 3.1_

**pages.json 注册**:
```json
{
  "path": "pages/project/role-create",
  "style": {
    "navigationStyle": "custom",
    "navigationBarTitleText": "发布角色"
  }
}
```

**权限守卫**: `onLoad` 中检查 `useUserStore().isCrew`，非剧组用户 `reLaunch` 到首页。同时校验 `options.projectId` 是否存在，缺失则 toast 提示并 `navigateBack`。

## 2. 依赖清单

| 依赖 | 来源 | 用途 |
|------|------|------|
| `KpPageLayout` | 00-02-shared-components §3.1 | 深色头部 + 浅色内容区骨架 |
| `KpNavBar` | 00-02-shared-components §3.2 | 导航栏，标题"发布角色" |
| `KpFormItem` | 00-02-shared-components §3.8 | 表单项容器 |
| `KpInput` | 00-02-shared-components §3.6 | 角色名称、报酬输入 |
| `KpTextarea` | 00-02-shared-components §3.7 | 角色描述输入 |
| `KpTag` | 00-02-shared-components §3.5 | 性别标签单选 |
| `KpButton` | 00-02-shared-components §3.4 | 底部发布按钮 |
| `useUserStore` | 00-03-shared-utils-api §3.7 | 用户角色判断 |
| `createRole` | 00-03-shared-utils-api §3.12 | 创建角色 API |
| `requiredRule` | 00-03-shared-utils-api §3.6 | 表单校验规则 |

## 3. 页面状态

_Requirements: 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8_

```typescript
interface FormState {
  roleName: string;     // 角色名称，必填
  gender: string;       // 性别要求，必填，默认"不限"
  minAge: number | null;// 最小年龄，选填
  maxAge: number | null;// 最大年龄，选填
  fee: string;          // 报酬，必填
  requirement: string;  // 角色描述，选填，max 500
  deadline: string;     // 截止时间，选填，YYYY-MM-DD
}

interface PageState {
  projectId: string;
  form: FormState;
  errors: Partial<Record<keyof FormState, string>>;
  submitting: boolean;
}
```

**初始值**:
```typescript
const projectId = ref('');
const form = reactive<FormState>({
  roleName: '',
  gender: '不限',
  minAge: null,
  maxAge: null,
  fee: '',
  requirement: '',
  deadline: '',
});
const errors = reactive<Partial<Record<keyof FormState, string>>>({});
const submitting = ref(false);

const genderOptions = ['不限', '男', '女'] as const;
const today = formatDate(new Date(), 'YYYY-MM-DD');
```

## 4. 模板结构

_Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8_

```vue
<template>
  <KpPageLayout :header-height="200" :scrollable="true">
    <!-- 深色头部 -->
    <template #header>
      <KpNavBar title="发布角色" />
    </template>

    <!-- 白色内容区：表单 -->
    <view class="role-create">
      <view class="role-create__form">
        <!-- 3.2 角色名称 -->
        <KpFormItem label="角色名称" required :error="errors.roleName">
          <KpInput
            v-model="form.roleName"
            placeholder="请输入角色名称"
            @blur="validateField('roleName')"
          />
        </KpFormItem>

        <!-- 3.3 性别要求 -->
        <KpFormItem label="性别要求" required :error="errors.gender">
          <view class="role-create__gender-tags">
            <KpTag
              v-for="opt in genderOptions"
              :key="opt"
              :text="opt"
              :selected="form.gender === opt"
              round
              @click="selectGender(opt)"
            />
          </view>
        </KpFormItem>

        <!-- 3.4 年龄范围 -->
        <KpFormItem label="年龄范围">
          <view class="role-create__age-range">
            <picker
              mode="selector"
              :range="ageRange"
              :value="form.minAge ? form.minAge - 1 : 0"
              @change="onMinAgeChange"
            >
              <view class="role-create__picker">
                {{ form.minAge || '最小年龄' }}
              </view>
            </picker>
            <text class="role-create__separator">—</text>
            <picker
              mode="selector"
              :range="ageRange"
              :value="form.maxAge ? form.maxAge - 1 : 0"
              @change="onMaxAgeChange"
            >
              <view class="role-create__picker">
                {{ form.maxAge || '最大年龄' }}
              </view>
            </picker>
          </view>
        </KpFormItem>

        <!-- 3.5 报酬 -->
        <KpFormItem label="报酬" required :error="errors.fee">
          <KpInput
            v-model="form.fee"
            placeholder="如：500元/天 或 面议"
            @blur="validateField('fee')"
          />
        </KpFormItem>

        <!-- 3.6 角色描述 -->
        <KpFormItem label="角色描述">
          <KpTextarea
            v-model="form.requirement"
            placeholder="请输入角色要求描述（选填）"
            :maxlength="500"
            show-count
            auto-height
          />
        </KpFormItem>

        <!-- 3.7 截止时间 -->
        <KpFormItem label="截止时间">
          <picker mode="date" :start="today" :value="form.deadline" @change="onDeadlineChange">
            <view class="role-create__picker">
              {{ form.deadline || '请选择截止日期（选填）' }}
            </view>
          </picker>
        </KpFormItem>
      </view>
    </view>

    <!-- 固定底部按钮 -->
    <view class="role-create__footer">
      <KpButton
        variant="primary"
        size="large"
        block
        :loading="submitting"
        :disabled="submitting"
        @click="handleSubmit"
      >
        发布角色
      </KpButton>
    </view>
  </KpPageLayout>
</template>
```

**关键样式**:
```scss
.role-create {
  padding: 32rpx;

  &__form {
    background: $kp-color-card;
    border-radius: $kp-radius-lg;
    padding: 32rpx;
  }

  &__gender-tags {
    display: flex;
    gap: 16rpx;
  }

  &__age-range {
    display: flex;
    align-items: center;
    gap: 16rpx;
  }

  &__picker {
    height: 88rpx;
    display: flex;
    align-items: center;
    padding: 0 24rpx;
    background: $kp-color-card;
    border: 2rpx solid #E8E8E8;
    border-radius: $kp-radius-input;
    font-size: 28rpx;
    color: $kp-color-text-primary;
    flex: 1;

    &:empty,
    &--placeholder {
      color: $kp-color-text-secondary;
    }
  }

  &__separator {
    color: $kp-color-text-secondary;
    font-size: 28rpx;
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

### 5.1 性别标签单选

_Requirements: 3.3_

```typescript
function selectGender(gender: string): void {
  form.gender = gender;
  clearError('gender');
}
```

### 5.2 年龄范围选择

_Requirements: 3.4_

```typescript
const ageRange = Array.from({ length: 120 }, (_, i) => i + 1);

function onMinAgeChange(e: { detail: { value: number } }): void {
  const val = ageRange[e.detail.value];
  form.minAge = val;
  if (form.maxAge !== null && val > form.maxAge) {
    form.maxAge = val;
  }
}

function onMaxAgeChange(e: { detail: { value: number } }): void {
  const val = ageRange[e.detail.value];
  form.maxAge = val;
  if (form.minAge !== null && val < form.minAge) {
    form.minAge = val;
  }
}
```

### 5.3 截止时间选择

_Requirements: 3.7_

```typescript
function onDeadlineChange(e: { detail: { value: string } }): void {
  form.deadline = e.detail.value;
}
```

### 5.4 表单校验

_Requirements: 3.8_

```typescript
function validateField(field: keyof FormState): boolean {
  if (field === 'roleName' && !form.roleName.trim()) {
    errors.roleName = '请输入角色名称';
    return false;
  }
  if (field === 'gender' && !form.gender) {
    errors.gender = '请选择性别要求';
    return false;
  }
  if (field === 'fee' && !form.fee.trim()) {
    errors.fee = '请输入报酬';
    return false;
  }
  errors[field] = '';
  return true;
}

function validateAll(): boolean {
  const nameOk = validateField('roleName');
  const genderOk = validateField('gender');
  const feeOk = validateField('fee');
  return nameOk && genderOk && feeOk;
}

function clearError(field: keyof FormState): void {
  errors[field] = '';
}
```

### 5.5 提交发布

_Requirements: 3.8_

```typescript
async function handleSubmit(): Promise<void> {
  if (!validateAll()) return;
  if (submitting.value) return;

  submitting.value = true;
  try {
    await createRole({
      projectId: Number(projectId.value),
      roleName: form.roleName.trim(),
      gender: form.gender,
      minAge: form.minAge ?? 0,
      maxAge: form.maxAge ?? 0,
      fee: form.fee.trim(),
      requirement: form.requirement.trim(),
      deadline: form.deadline,
    });
    uni.showToast({ title: '角色发布成功', icon: 'none', duration: 2000 });
    setTimeout(() => {
      uni.navigateBack();
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
onLoad((options) => {
  const userStore = useUserStore();
  if (!userStore.isCrew) {
    uni.reLaunch({ url: '/pages/home/index' });
    return;
  }
  if (!options?.projectId) {
    uni.showToast({ title: '缺少项目信息', icon: 'none' });
    setTimeout(() => uni.navigateBack(), 1000);
    return;
  }
  projectId.value = options.projectId;
});
```

## 7. 跳转关系

| 触发 | 目标页面 | 方式 | 条件 |
|------|---------|------|------|
| 点击返回按钮 | 上一页 | `navigateBack` | — |
| 发布成功 | 上一页 | `navigateBack` | API 返回成功 |
| 缺少 projectId | 上一页 | `navigateBack` | 参数校验失败 |