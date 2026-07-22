# 00-195 当前阶段小程序手机号快捷登录入口回归定位 - 执行记录

## 1. 用户反馈

用户指出：上一版小程序登录页 `pages/login/index` 中有「手机号快捷登录」，当前页面只有手机号验证码登录，之前把“验证码登录存在”当成“手机号快捷登录存在”的定位不准确。

本轮只做定位和文档回填，不改小程序运行时代码。

## 2. 当前页面事实

当前 `kaipai-frontend/src/pages/login/index.vue` 可见登录元素为：

- `使用手机号验证码登录，未注册手机号将自动创建演员账号`
- `请输入手机号`
- `请输入验证码`
- `获取验证码`
- `登录 / 注册`

当前 `pages/login/index` 源码不包含：

- `getPhoneNumber`
- `handleWechatLogin`
- `loginByWechat`
- `手机号快捷登录`

结论：当前页面有“短信验证码登录”，但没有“手机号快捷登录”。这两者不能混同。

## 3. git 历史定位

### 3.1 入口开启

提交：

```text
427274e feat: enable wechat phone login entry
AuthorDate: 2026-05-22 21:08:38 +0800
```

该提交补强了 `getPhoneNumber` 授权 code 校验，并继续调用 `loginByWechat(...)`。

### 3.2 引入官方风格图标风险

提交：

```text
0a67730 fix: update wechat login icon
AuthorDate: 2026-06-30 10:44:10 +0800
```

该提交把登录按钮中的自绘点替换为：

```vue
<image class="login-page__wechat-icon" src="/static/icons/wechat-login.png" mode="aspectFit" />
```

同时新增 `src/static/icons/wechat-login.png`。

判断：这一步引入了审核反馈第 1 条中的官方 logo / 官方元素混淆风险。

### 3.3 文案改为「手机号快捷登录」

提交：

```text
84c2778 fix: update quick phone login copy
AuthorDate: 2026-06-30 21:17:59 +0800
```

该提交仅把按钮文案从：

```ts
微信一键登录
```

改为：

```ts
手机号快捷登录
```

判断：该提交证明上一版相关代码中确实存在「手机号快捷登录」按钮。但它没有删除 `/static/icons/wechat-login.png`，因此仍可能触发“官方 logo / 官方元素混淆”审核风险。

### 3.4 完整删除快捷登录入口

提交：

```text
0679e09 fix: remove quick phone auth login entry
AuthorDate: 2026-07-02 14:53:52 +0800
Author: mashaorui <609616309@qq.com>
```

该提交删除范围：

```text
M src/api/auth.ts
M src/pages/login/index.vue
D src/static/icons/wechat-login.png
M src/utils/runtime.ts
```

具体删除对象包括：

- 登录页模板中的 `button.login-page__wechat`。
- `open-type="getPhoneNumber"`。
- `@getphonenumber="handleWechatLogin"`。
- `/static/icons/wechat-login.png` image 节点。
- `canUseWechatLogin` / `wechatLoginTip` / `wechatActionText`。
- `handleWechatLogin()`。
- `handleWechatButtonClick()`.
- `loginByWechat()` 前端 API helper。
- `canUseWechatAuth()` / `getWechatAuthBlocker()` runtime helper。
- `src/static/icons/wechat-login.png` 文件。

判断：这是当前「手机号快捷登录」消失的直接来源。该入口不是被 CSS 隐藏，而是被物理删除。

### 3.5 后续登录流程调整没有恢复入口

提交：

```text
54d8a31 fix: align miniapp review login flow
AuthorDate: 2026-07-06 17:33:49 +0800
```

该提交在 `0679e09` 删除入口后的基础上继续修改：

- 新增登录页返回按钮。
- 登录成功后先导航，再非阻断同步演员运行态。
- 附属运行态同步传入 `redirectOnUnauthorized: false`。

判断：该提交修复了登录流程和返回按钮问题，但没有恢复「手机号快捷登录」。

## 4. 00-187 文档冲突

`00-187` 当前内部存在互相冲突的记录。

### 4.1 正确方向：去品牌化但保留入口

`.sce/specs/00-187-current-phase-miniapp-review-login-gate-fix/design.md`：

- 设计结论写明：去除手机号快捷登录按钮中的微信官方 logo image。
- 设计结论写明：可见文案统一为「手机号快捷登录」。
- 交互逻辑仍写有 `click 手机号快捷登录`。
- 授权回调仍写有 `getPhoneNumber -> 调后端 /api/auth/wechat-login`。

`.sce/specs/00-187-current-phase-miniapp-review-login-gate-fix/tasks.md`：

- T2 写明：移除登录页手机号快捷登录按钮中的 `/static/icons/wechat-login.png`。
- T2 写明：登录页用户可见文案统一为「手机号快捷登录」。

### 4.2 错误方向：删除入口

`.sce/specs/00-187-current-phase-miniapp-review-login-gate-fix/requirements.md`：

- 错误写成：复审包采用更保守策略，登录页不暴露 `getPhoneNumber` 手机号快速验证入口。
- 错误验收：页面不展示 `getPhoneNumber` 手机号快速验证按钮。
- 错误验收：不存在手机号快速验证入口。

`.sce/specs/00-187-current-phase-miniapp-review-login-gate-fix/execution.md`：

- 记录本地 rebase 后采用远端更保守方向：不再暴露 `getPhoneNumber`，只保留短信验证码登录。

`.sce/specs/00-187-current-phase-miniapp-review-login-gate-fix/scripts/verify-miniapp-review-login-gate.mjs`：

- 错误检查名：`login page does not expose quick phone authorization entry`。
- 错误规则：`!/getPhoneNumber|手机号快捷登录|phone-quick/.test(loginSource)`。

### 4.3 映射文档与实际代码不一致

`.sce/specs/spec-code-mapping.md` 当前写着：

```text
kaipai-frontend/src/pages/login/index.vue：手机号快捷登录去微信官方 logo / 用户可见品牌文案，并补明确失败反馈
```

但当前代码实际没有「手机号快捷登录」入口。该映射只能代表设计意图或历史目标，不能代表当前运行态。

## 5. 根因结论

根因是 `00-187` 执行时把微信审核反馈中的“去除官方混淆元素，修改提示为手机号快捷登录”误扩大为“删除 `getPhoneNumber` 手机号快捷登录入口”。

正确拆分应为：

- 必须删除：`wechat-login.png` 官方风格图标、用户可见「微信登录 / 微信一键登录 / 微信授权」文案。
- 不应删除：`getPhoneNumber` 手机号快捷登录入口本身。
- 按审核反馈建议，应展示自有能力文案「手机号快捷登录」。

## 6. 当前本轮结论

- 当前页面缺少「手机号快捷登录」是 `0679e09` 造成的。
- 当前页面不是样式隐藏，而是完整前端链路被删除。
- `84c2778` 证明上一版相关代码确实有「手机号快捷登录」文案。
- `00-187` 需要后续纠偏：requirements、execution 和 verify script 中的“删除入口”门禁应改为“保留入口但去官方混淆元素”。
- 本轮未修改 `kaipai-frontend` 源码。

## 7. 后续建议

后续恢复入口时建议另起修复任务，至少包含：

1. 修正 `00-187` 的错误 requirements 和验收脚本。
2. 恢复 `loginByWechat()` 前端 API helper。
3. 恢复 `getPhoneNumber` 按钮，文案为「手机号快捷登录」。
4. 不恢复 `wechat-login.png`，按钮不使用微信官方 logo。
5. 所有用户可见错误文案去掉「微信登录 / 微信一键登录 / 微信授权」。
6. 保留 `54d8a31` 的登录成功后非阻断同步逻辑。
7. 重新执行：
   - `cd kaipai-frontend && npm run type-check`
   - `cd kaipai-frontend && npm run build:mp-weixin`
   - `cd kaipai-frontend && npm run audit:mp-package`
   - `node .sce/specs/00-187-current-phase-miniapp-review-login-gate-fix/scripts/verify-miniapp-review-login-gate.mjs`
   - `node .sce/specs/00-188-current-phase-miniapp-review-compliance-audit-fix/scripts/verify-miniapp-review-compliance-audit.mjs`
