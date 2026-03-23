# 剧组资料编辑页 - 技术设计

## 1. 路由配置

_Requirements: 3.1_

```json
// pages.json
{
  "path": "pages/company-profile/edit",
  "style": {
    "navigationStyle": "custom",
    "navigationBarTitleText": "剧组资料"
  }
}
```

## 2. 依赖清单

| 类别 | 依赖项 | 来源 |
|------|--------|------|
| 组件 | KpPageLayout | 00-02-shared-components (3.1) |
| 组件 | KpNavBar | 00-02-shared-components (3.2) |
| 组件 | KpFormItem | 00-02-shared-components (3.8) |
| 组件 | KpInput | 00-02-shared-components (3.6) |
| 组件 | KpTextarea | 00-02-shared-components (3.7) |
| 组件 | KpButton | 00-02-shared-components (3.4) |
| API | getMyCompany | 00-03-shared-utils-api (3.10) |
| API | updateCompanyInfo | 00-03-shared-utils-api (3.10) |
| 类型 | Company | 00-03-shared-utils-api (3.1) |
| 工具 | phoneRule, requiredRule | 00-03-shared-utils-api (3.6) |

## 3. 页面状态

_Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

```typescript
/** 表单数据 */
const formData = reactive<{
  companyName: string;
  contactName: string;
  contactPhone: string;
  remark: string;
}>({
  companyName: '',
  contactName: '',
  contactPhone: '',
  remark: '',
});

/** 表单错误信息 */
const errors = reactive<{
  companyName: string;
  contactName: string;
  contactPhone: string;
}>({
  companyName: '',
  contactName: '',
  contactPhone: '',
});

const saving = ref<boolean>(false);
const loading = ref<boolean>(true);
```

## 4. 模板结构

_Requirements: 3.2, 3.3, 3.4, 3.5, 3.6_

```vue
<template>
  <KpPageLayout :scrollable="true" :safe-area-bottom="false">
    <!-- 深色头部 -->
    <template #header>
      <KpNavBar title="剧组资料" />
    </template>

    <!-- 浅色内容区 - 表单 -->
    <view class="form-container">
      <!-- 公司名称 -->
      <KpFormItem label="公司名称" required :error="errors.companyName">
        <KpInput
          v-model="formData.companyName"
          placeholder="请输入公司/团队名称"
          @blur="validateField('companyName')"
        />
      </KpFormItem>

      <!-- 联系人 -->
      <KpFormItem label="联系人" required :error="errors.contactName">
        <KpInput
          v-model="formData.contactName"
          placeholder="请输入联系人姓名"
          @blur="validateField('contactName')"
        />
      </KpFormItem>

      <!-- 联系电话 -->
      <KpFormItem label="联系电话" required :error="errors.contactPhone">
        <KpInput
          v-model="formData.contactPhone"
          type="number"
          placeholder="请输入联系电话"
          :maxlength="11"
          @blur="validateField('contactPhone')"
        />
      </KpFormItem>

      <!-- 简介 -->
      <KpFormItem label="简介">
        <KpTextarea
          v-model="formData.remark"
          placeholder="请输入公司/团队简介"
          :maxlength="500"
          show-count
          auto-height
          :min-height="200"
        />
      </KpFormItem>
    </view>

    <!-- 固定底部按钮 -->
    <view class="fixed-bottom">
      <KpButton
        variant="primary"
        size="large"
        block
        :loading="saving"
        @click="handleSave"
      >
        保存资料
      </KpButton>
    </view>
  </KpPageLayout>
</template>
```

## 5. 交互逻辑

_Requirements: 3.2, 3.3, 3.4, 3.5, 3.6_

```typescript
import { isPhone } from '@/utils/validate';

/** 单字段校验 */
function validateField(field: keyof typeof errors): boolean {
  switch (field) {
    case 'companyName':
      errors.companyName = formData.companyName.trim() ? '' : '请输入公司名称';
      break;
    case 'contactName':
      errors.contactName = formData.contactName.trim() ? '' : '请输入联系人';
      break;
    case 'contactPhone':
      if (!formData.contactPhone.trim()) {
        errors.contactPhone = '请输入联系电话';
      } else if (!isPhone(formData.contactPhone)) {
        errors.contactPhone = '请输入正确的手机号';
      } else {
        errors.contactPhone = '';
      }
      break;
  }
  return !errors[field];
}

/** 全量校验 */
function validateAll(): boolean {
  const fields: (keyof typeof errors)[] = ['companyName', 'contactName', 'contactPhone'];
  return fields.map(validateField).every(Boolean);
}

/** 保存资料 */
async function handleSave(): Promise<void> {
  if (!validateAll()) return;
  if (saving.value) return;
  saving.value = true;
  try {
    await updateCompanyInfo({
      companyName: formData.companyName.trim(),
      contactName: formData.contactName.trim(),
      contactPhone: formData.contactPhone.trim(),
      remark: formData.remark.trim(),
    });
    uni.showToast({ title: '保存成功', icon: 'success' });
    setTimeout(() => uni.navigateBack(), 1500);
  } catch {
    // 错误由 request 层统一处理
  } finally {
    saving.value = false;
  }
}
```

## 6. 生命周期

_Requirements: 3.1_

```typescript
onLoad(async () => {
  try {
    loading.value = true;
    const company = await getMyCompany();
    formData.companyName = company.companyName || '';
    formData.contactName = company.contactName || '';
    formData.contactPhone = company.contactPhone || '';
    formData.remark = company.remark || '';
  } catch {
    // 首次编辑可能无数据，保持空表单
  } finally {
    loading.value = false;
  }
});
```

**关键样式**:

```scss
.form-container {
  padding: 32rpx 24rpx;
  padding-bottom: 180rpx; // 为固定底部按钮留出空间
}

.fixed-bottom {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 16rpx 24rpx;
  padding-bottom: calc(16rpx + env(safe-area-inset-bottom));
  background: $kp-color-card;
  box-shadow: 0 -4rpx 16rpx rgba(0, 0, 0, 0.06);
  z-index: 50;
}
```

## 7. 跳转关系

_Requirements: 3.1_

| 来源 | 目标 | 触发条件 | 携带参数 |
|------|------|----------|----------|
| 我的页面/设置 | 本页面 | 点击"编辑剧组资料" | — |
| 本页面 | 上一页 | 保存成功 / 点击返回 | — |
