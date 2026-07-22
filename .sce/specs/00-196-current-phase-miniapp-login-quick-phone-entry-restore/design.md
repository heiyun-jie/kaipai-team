# 00-196 当前阶段小程序手机号快捷登录入口恢复 - 技术设计

## 1. 设计结论

恢复合规版快捷登录，不恢复旧官方风格图标：

```text
pages/login/index
  -> 短信验证码登录保留
  -> 在短信主按钮下方恢复 button.login-page__phone-quick
  -> 按钮文案固定为“手机号快捷登录”或登录中态
  -> 不渲染 image / wechat-login.png / 微信官方 logo
  -> 未勾协议只弹协议确认，确认后勾选协议，不直接授权
  -> 已勾协议且运行时配置可用时 open-type=getPhoneNumber
  -> getPhoneNumber 成功后调用 api/auth 的 phone quick helper
  -> 成功后复用短信登录的非阻断导航顺序

api/auth
  -> 恢复手机号快捷登录 helper
  -> 内部调用 /api/auth/wechat-login
  -> 缺 code 错误文案使用“手机号授权结果缺少 code”

utils/runtime
  -> 恢复自有命名的 phone quick capability helper
  -> 配置不可用文案不出现“微信登录 / 微信授权”

00-187 verify script
  -> 要求合规入口存在
  -> 禁止 logo 和微信品牌化可见文案
```

_Requirements: 3.1, 3.2, 3.3, 3.4_

## 2. 页面视觉合同

- 页面路由：`pages/login/index`
- 可见块：登录 sheet 内，`登录 / 注册` 按钮和协议勾选之间。
- 预期变化：新增一个与现有主按钮同尺寸的深色胶囊按钮，文案为「手机号快捷登录」。
- 保持不变：顶部返回按钮继续与胶囊同行；短信手机号输入、验证码输入、获取验证码、登录 / 注册按钮保持现有布局；协议区域继续在按钮组下方。

## 3. 代码结构

### `src/pages/login/index.vue`

新增状态和计算：

- `canUsePhoneQuickLogin = computed(() => canUsePhoneQuickAuth())`
- `phoneQuickLoginTip = computed(() => getPhoneQuickAuthBlocker() || '手机号快捷登录暂不可用，请使用验证码登录')`
- `phoneQuickActionText = computed(() => loginLoading.value ? '登录中...' : '手机号快捷登录')`

新增模板：

```vue
<button
  class="login-page__phone-quick"
  :class="{ 'login-page__phone-quick--disabled': !canUsePhoneQuickLogin || !agreed || loginLoading }"
  :open-type="canUsePhoneQuickLogin && agreed && !loginLoading ? 'getPhoneNumber' : ''"
  @click="handlePhoneQuickButtonClick"
  @getphonenumber="handlePhoneQuickLogin"
>
  <text class="login-page__phone-quick-text">{{ phoneQuickActionText }}</text>
</button>
```

不使用 `<image>`，不引用 `wechat-login.png`。

新增交互：

```text
handlePhoneQuickButtonClick
  -> loading: return
  -> capability 不可用: toast phoneQuickLoginTip
  -> 未勾协议: confirmAgreementBeforeLogin()
  -> 已勾协议: 交给 getPhoneNumber 原生回调

handlePhoneQuickLogin
  -> capability 不可用: toast
  -> loading: return
  -> 未勾协议: confirmAgreementBeforeLogin()
  -> errMsg != getPhoneNumber:ok: toast 需要授权手机号才能登录
  -> code 为空: toast 手机号授权结果缺少 code
  -> loginByPhoneQuickAuth(code, inviteCode)
  -> setUserData
  -> navigateAfterLogin
  -> syncActorRuntimeStateAfterNavigation
```

### `src/api/auth.ts`

新增：

```ts
export function loginByPhoneQuickAuth(code: string, inviteCode?: string): Promise<LoginResult>
```

内部调用 `/api/auth/wechat-login`，继续传 `deviceFingerprint`。

### `src/utils/runtime.ts`

新增：

```ts
export function canUsePhoneQuickAuth(): boolean
export function getPhoneQuickAuthBlocker(): string | null
```

仍复用 `getRuntimeConfigBlocker()`，并保留 `VITE_ENABLE_WECHAT_AUTH=false` 作为关闭开关，但用户可见文案使用「手机号快捷登录入口未启用，请使用手机号验证码登录 / 注册。」。

## 4. 验收脚本设计

更新 `00-187/scripts/verify-miniapp-review-login-gate.mjs`：

- 保留官方图标删除检查。
- 保留微信品牌化中文文案检查。
- 将“禁止快捷入口”替换为“必须存在合规快捷入口”。
- 新增 API helper 缺 code 文案检查。
- 新增 source/dist 登录 WXML 的 `getPhoneNumber` 和「手机号快捷登录」检查。

红灯：

```powershell
node .sce\specs\00-187-current-phase-miniapp-review-login-gate-fix\scripts\verify-miniapp-review-login-gate.mjs
```

当前代码应失败，因为缺少 `getPhoneNumber` /「手机号快捷登录」。

## 5. 验证命令

1. `node .sce\specs\00-187-current-phase-miniapp-review-login-gate-fix\scripts\verify-miniapp-review-login-gate.mjs`
2. `cd kaipai-frontend && npm run type-check`
3. `cd kaipai-frontend && npm run build:mp-weixin`
4. `cd kaipai-frontend && npm run audit:mp-package`
5. `node .sce\specs\00-187-current-phase-miniapp-review-login-gate-fix\scripts\verify-miniapp-review-login-gate.mjs`
6. `node .sce\specs\00-188-current-phase-miniapp-review-compliance-audit-fix\scripts\verify-miniapp-review-compliance-audit.mjs`

## 6. 产物核验

构建后核对：

- `kaipai-frontend/dist/build/mp-weixin/pages/login/index.wxml`
- `kaipai-frontend/dist/dev/mp-weixin/pages/login/index.wxml`
- `kaipai-frontend/dist/build/mp-weixin/pages/login/index.wxss`
- `kaipai-frontend/dist/dev/mp-weixin/pages/login/index.wxss`

核验点：

- WXML 包含 `getPhoneNumber`。
- WXML 包含「手机号快捷登录」。
- WXML/WXSS 不包含 `wechat-login.png` 或 `login-page__wechat-icon`。
- WXSS 包含 `login-page__phone-quick`。
