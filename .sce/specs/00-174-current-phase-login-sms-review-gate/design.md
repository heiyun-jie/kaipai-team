# 00-174 当前阶段登录页验证码审核门禁 - 技术设计

## 1. 设计结论

`pages/login/index` 当前阶段采用模板级审核门禁：

```text
remove SMS form from template
  -> no phone field in generated WXML
  -> no sms code field in generated WXML
  -> no sms login/register submit in generated WXML
  -> keep WeChat getPhoneNumber as the only login CTA
```

该门禁只影响页面可见层，不删除短信登录脚本逻辑，也不改变后端接口。后续验证码审核通过后，需要按独立 Spec 恢复模板入口。

隐藏短信表单后，登录页还需要同步收口视觉高度，避免下半屏只剩背景留白；因此登录 sheet 继续承接剩余 viewport，协议区下方只允许放置非交互的影像 / 胶片视觉元素，不能用审核前不可用入口填充页面。

_Requirements: 3.1, 3.2, 3.3, 3.4_

## 2. 路由配置

- 路由不变：`pages/login/index`
- `src/pages.json` 不需要调整。

_Requirements: 3.1_

## 3. 依赖清单

继续复用现有依赖：

- `@/api/auth`
  - `loginByWechat`
  - `loginByPhone`
  - `registerByPhone`
  - `sendSmsCode`
- `@/utils/runtime`
  - `canUseWechatAuth`
  - `getWechatAuthBlocker`
- `@/stores/user`
- `@/utils/navigation`

本轮不新增 API、不新增 Store。

_Requirements: 3.2, 3.3_

## 4. 页面状态定义

保留现有短信登录状态：

- `phone`
- `smsCode`
- `smsLoading`
- `countdown`
- `authMode`
- `registerRole`

这些状态继续服务于后续审核通过后的恢复，但当前模板不消费这些状态，因此不会生成短信表单 WXML。

_Requirements: 3.1, 3.4_

## 5. 模板结构

登录页结构调整为：

```text
hero
sheet
  sheet head
  WeChat one-click login primary CTA
  agreement
  non-interactive film visual fill
```

手机号输入、验证码输入、获取验证码、短信登录 / 注册提交节点从当前模板中移除，确保审核前产物不携带短信登录可见入口。

`non-interactive film visual fill` 只承担视觉承接，不绑定点击、不展示说明文案、不触发任何登录能力。

微信按钮继续满足：

```vue
:open-type="canUseWechatLogin && agreed && !loginLoading ? 'getPhoneNumber' : ''"
@getphonenumber="handleWechatLogin"
```

_Requirements: 3.1, 3.2, 3.3_

## 6. 布局策略

- `.login-page` 使用纵向 flex 容器，确保页面内容覆盖完整 viewport。
- `.login-page__hero` 固定承接品牌视觉。
- `.login-page__sheet` 使用 `flex: 1 1 auto` 和最小高度承接底部空间。
- 协议区下方使用 `margin-top: auto` 的胶片视觉块填满剩余空间，避免短信表单隐藏后下半屏出现纯空白。
- 胶片视觉块不包含任何用户可见功能文案，不引入新的登录方式或审核前能力入口。

_Requirements: 3.3_

## 7. 交互逻辑

- 未勾选协议时点击微信登录：
  - 调用现有 `confirmAgreementBeforeLogin()`
  - 不直接触发微信手机号授权
- 已勾选协议且微信配置可用时点击微信登录：
  - 触发微信 `getPhoneNumber`
  - 回调 `handleWechatLogin`
  - 复用 `loginByWechat`
- 短信登录相关函数保留，但没有可见控件可触发。

_Requirements: 3.2, 3.4_

## 8. 生命周期

不改变：

- `onLoad` 中的邀请码读取
- 已登录 session 恢复
- `onUnload` 中的倒计时 / shake timer 清理

_Requirements: 3.4_

## 9. 验证设计

必须执行：

1. `cd kaipai-frontend && npm run type-check`
2. `cd kaipai-frontend && npm run build:mp-weixin`
3. `cd kaipai-frontend && npm run audit:mp-package`

构建产物核验：

- `dist/dev/mp-weixin/pages/login/index.wxml`
- `dist/build/mp-weixin/pages/login/index.wxml`

核验点：

- 可见 WXML 不包含 `手机号`
- 可见 WXML 不包含 `验证码`
- 可见 WXML 不包含 `获取验证码`
- 可见 WXML 不包含 `登录 / 注册`
- 微信按钮仍保留 `getPhoneNumber` 绑定逻辑
- 登录页 WXML 包含非交互 `login-page__film` 视觉承接节点
- 微信开发者工具 preview 通过，并用 390x844 移动视口截图确认登录卡片下方不再出现大面积空白

_Requirements: 3.1, 3.2, 3.3_
