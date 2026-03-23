# 登录页 - 技术设计

## 1. 页面路由配置 (pages.json snippet)

_Requirements: 3.1_

```json
{
  "pages": [
    {
      "path": "pages/login/index",
      "style": {
        "navigationStyle": "custom",
        "navigationBarTitleText": "",
        "backgroundColor": "#121214",
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
| KpButton | 登录按钮（primary, block, large）、微信登录按钮（glass 变体, openType="getPhoneNumber"） |
| KpInput | 手机号输入框、验证码输入框（半透明深色样式覆写） |
| KpConfirmDialog | 未勾选协议时的提示弹窗（可选，也可用 toast） |

### API 依赖 (from 00-03-shared-utils-api)

| 函数 | 来源文件 | 用途 |
|------|----------|------|
| `sendSmsCode(phone)` | `api/auth.ts` | 发送短信验证码 |
| `loginByPhone(phone, code)` | `api/auth.ts` | 手机号 + 验证码登录 |
| `loginByWechat(code)` | `api/auth.ts` | 微信一键登录 |
| `isPhone(value)` | `utils/validate.ts` | 手机号格式校验 |
| `setToken(token)` | `utils/auth.ts` | 持久化 Token |
| `setUserInfo(user)` | `utils/auth.ts` | 持久化用户信息 |

### Store 依赖

| Store | 来源文件 | 用途 |
|-------|----------|------|
| `useUserStore` | `stores/user.ts` | 管理登录态、用户信息、角色判断 |

## 3. 页面状态定义 (TypeScript ref/reactive)

_Requirements: 3.2, 3.3, 3.4, 3.5, 3.6_

```typescript
import { ref, computed } from 'vue';

// 表单数据
const phone = ref<string>('');
const smsCode = ref<string>('');
const agreed = ref<boolean>(false);

// 倒计时
const countdown = ref<number>(0);
let countdownTimer: ReturnType<typeof setInterval> | null = null;

// 加载状态
const loginLoading = ref<boolean>(false);
const smsLoading = ref<boolean>(false);

// 计算属性
const isPhoneValid = computed<boolean>(() => isPhone(phone.value));
const canSendSms = computed<boolean>(() => isPhoneValid.value && countdown.value === 0 && !smsLoading.value);
const canLogin = computed<boolean>(() =>
  isPhoneValid.value && smsCode.value.length === 6 && agreed.value && !loginLoading.value
);
const smsButtonText = computed<string>(() =>
  countdown.value > 0 ? `${countdown.value}s 后重新获取` : '获取验证码'
);
```

## 4. 模板结构 (pseudo-template with component composition)

_Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6_

```vue
<template>
  <view class="login-page" :style="{ background: '#121214' }">
    <!-- 状态栏占位 -->
    <view class="login-page__status-bar" :style="{ height: statusBarHeight + 'px' }" />

    <!-- Logo 区域 — 居中置顶 30% -->
    <view class="login-page__logo">
      <image src="/static/logo.png" mode="aspectFit" class="login-page__logo-img" />
      <text class="login-page__app-name">开拍了</text>
    </view>

    <!-- 表单区域 -->
    <view class="login-page__form">
      <!-- 手机号输入 -->
      <view class="login-page__input-wrap">
        <KpInput
          v-model="phone"
          type="number"
          placeholder="请输入手机号"
          prefix-icon="phone"
          :maxlength="11"
          class="login-page__input--dark"
        />
      </view>

      <!-- 验证码输入 + 获取按钮 -->
      <view class="login-page__input-wrap login-page__sms-row">
        <KpInput
          v-model="smsCode"
          type="number"
          placeholder="请输入验证码"
          prefix-icon="shield"
          :maxlength="6"
          class="login-page__input--dark"
        >
          <template #suffix>
            <text
              class="login-page__sms-btn"
              :class="{ 'login-page__sms-btn--disabled': !canSendSms }"
              @click="handleSendSms"
            >
              {{ smsButtonText }}
            </text>
          </template>
        </KpInput>
      </view>

      <!-- 登录按钮 — Spotlight Orange -->
      <KpButton
        variant="primary"
        size="large"
        block
        :disabled="!canLogin"
        :loading="loginLoading"
        @click="handleLogin"
      >
        登录
      </KpButton>

      <!-- 分割线 -->
      <view class="login-page__divider">
        <view class="login-page__divider-line" />
        <text class="login-page__divider-text">其他登录方式</text>
        <view class="login-page__divider-line" />
      </view>

      <!-- 微信一键登录 — Glass 样式 -->
      <KpButton
        variant="glass"
        size="large"
        block
        icon="weixin"
        :disabled="!agreed"
        open-type="getPhoneNumber"
        @getphonenumber="handleWechatLogin"
      >
        微信一键登录
      </KpButton>
    </view>

    <!-- 用户协议 -->
    <view class="login-page__agreement">
      <view
        class="login-page__checkbox"
        :class="{ 'login-page__checkbox--checked': agreed }"
        @click="agreed = !agreed"
      >
        <u-icon v-if="agreed" name="checkmark" size="12" color="#FF6B35" />
      </view>
      <text class="login-page__agreement-text">
        我已阅读并同意
        <text class="login-page__link" @click.stop="openAgreement('user')">《用户协议》</text>
        和
        <text class="login-page__link" @click.stop="openAgreement('privacy')">《隐私政策》</text>
      </text>
    </view>
  </view>
</template>
```

## 5. 交互逻辑 (event handler functions with signatures)

_Requirements: 3.3, 3.4, 3.5, 3.6, 3.7_

```typescript
import { sendSmsCode, loginByPhone, loginByWechat } from '@/api/auth';
import { isPhone } from '@/utils/validate';
import { useUserStore } from '@/stores/user';

const userStore = useUserStore();

/**
 * 发送短信验证码
 * Requirements: 3.3
 */
async function handleSendSms(): Promise<void> {
  if (!canSendSms.value) return;
  if (!isPhone(phone.value)) {
    uni.showToast({ title: '请输入正确的手机号', icon: 'none' });
    return;
  }
  smsLoading.value = true;
  try {
    await sendSmsCode(phone.value);
    uni.showToast({ title: '验证码已发送', icon: 'success' });
    startCountdown();
  } catch (err: any) {
    uni.showToast({ title: err.message || '发送失败', icon: 'none' });
  } finally {
    smsLoading.value = false;
  }
}

/**
 * 启动 60s 倒计时
 * Requirements: 3.3
 */
function startCountdown(): void {
  countdown.value = 60;
  countdownTimer = setInterval(() => {
    countdown.value--;
    if (countdown.value <= 0) {
      clearInterval(countdownTimer!);
      countdownTimer = null;
    }
  }, 1000);
}

/**
 * 手机号 + 验证码登录
 * Requirements: 3.4, 3.7
 */
async function handleLogin(): Promise<void> {
  if (!canLogin.value) return;
  if (!agreed.value) {
    uni.showToast({ title: '请先同意用户协议和隐私政策', icon: 'none' });
    return;
  }
  loginLoading.value = true;
  try {
    const { token, user } = await loginByPhone(phone.value, smsCode.value);
    userStore.setUserData(user, token);
    navigateAfterLogin(user);
  } catch (err: any) {
    uni.showToast({ title: err.message || '登录失败', icon: 'none' });
  } finally {
    loginLoading.value = false;
  }
}

/**
 * 微信一键登录回调
 * Requirements: 3.5
 */
async function handleWechatLogin(e: any): Promise<void> {
  if (!agreed.value) {
    uni.showToast({ title: '请先同意用户协议和隐私政策', icon: 'none' });
    return;
  }
  if (e.detail.errMsg !== 'getPhoneNumber:ok') {
    uni.showToast({ title: '需要授权手机号才能登录', icon: 'none' });
    return;
  }
  loginLoading.value = true;
  try {
    const { token, user } = await loginByWechat(e.detail.code);
    userStore.setUserData(user, token);
    navigateAfterLogin(user);
  } catch (err: any) {
    uni.showToast({ title: err.message || '微信登录失败', icon: 'none' });
  } finally {
    loginLoading.value = false;
  }
}

/**
 * 登录后路由分发
 * Requirements: 3.7
 */
function navigateAfterLogin(user: UserInfo): void {
  if (user.role === 1) {
    uni.reLaunch({ url: '/pages/home/index' });
  } else if (user.role === 2) {
    uni.reLaunch({ url: '/pages/home/index' });
  } else {
    uni.redirectTo({ url: '/pages/role-select/index' });
  }
}

/**
 * 打开协议页面
 * Requirements: 3.6
 */
function openAgreement(type: 'user' | 'privacy'): void {
  const url = type === 'user'
    ? '/pages/webview/index?url=USER_AGREEMENT_URL'
    : '/pages/webview/index?url=PRIVACY_POLICY_URL';
  uni.navigateTo({ url });
}
```

## 6. 生命周期

_Requirements: 3.1_

```typescript
import { onLoad, onUnload } from '@dcloudio/uni-app';

onLoad(() => {
  // 获取状态栏高度用于适配
  const systemInfo = uni.getSystemInfoSync();
  statusBarHeight.value = systemInfo.statusBarHeight || 0;
});

onUnload(() => {
  // 清理倒计时定时器，防止内存泄漏
  if (countdownTimer) {
    clearInterval(countdownTimer);
    countdownTimer = null;
  }
});
```

## 7. 页面跳转关系

_Requirements: 3.7_

```
登录页 (pages/login/index)
  ├── [登录成功 + role=1] ──reLaunch──→ 首页 (pages/home/index)
  ├── [登录成功 + role=2] ──reLaunch──→ 首页 (pages/home/index)
  ├── [登录成功 + role=空] ──redirectTo──→ 身份选择页 (pages/role-select/index)
  ├── [点击用户协议] ──navigateTo──→ WebView 页面
  └── [点击隐私政策] ──navigateTo──→ WebView 页面
```

## 8. 关键样式说明

_Requirements: 3.1, 3.2_

```scss
// 登录页特殊样式 — 全深色沉浸式
.login-page {
  min-height: 100vh;
  background: $kp-color-dark-primary; // #121214
  @include kp-flex-column;
  padding: 0 $kp-spacing-page;

  // 半透明输入框覆写
  &__input--dark {
    :deep(.kp-input) {
      background: rgba(255, 255, 255, 0.08);
      border-color: rgba(255, 255, 255, 0.12);
      color: $kp-color-text-dark-primary;

      &--focus {
        border-color: rgba($kp-color-primary, 0.6);
      }
    }
  }

  // Logo 居中 — 距顶部 30%
  &__logo {
    @include kp-flex-center;
    flex-direction: column;
    margin-top: 30vh;
    margin-bottom: $kp-spacing-xl;
  }

  // 验证码按钮
  &__sms-btn {
    @include kp-text-caption;
    color: $kp-color-primary;
    white-space: nowrap;

    &--disabled {
      color: $kp-color-text-dark-secondary;
    }
  }

  // 协议区域
  &__agreement {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    @include kp-flex-center;
    @include kp-safe-area-bottom($kp-spacing-lg);
    padding: $kp-spacing-gap $kp-spacing-page;
  }

  &__link {
    color: $kp-color-primary;
  }
}
```
