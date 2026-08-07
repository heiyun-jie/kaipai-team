# 00-196 当前阶段小程序手机号快捷登录入口恢复 - 执行记录

## 1. 触发原因

用户要求开始执行修复。修复目标来自 `00-195`：恢复 `pages/login/index` 的合规版「手机号快捷登录」入口，修正 `00-187` 把去品牌化误扩大为删除入口的问题。

## 2. 执行记录

### 2.1 红灯门禁

先修正 `00-187` 的专项验收脚本，把原先错误的“禁止 `getPhoneNumber` / 手机号快捷登录”改为“要求合规手机号快捷登录入口存在”。

在恢复代码前运行：

```powershell
node .sce\specs\00-187-current-phase-miniapp-review-login-gate-fix\scripts\verify-miniapp-review-login-gate.mjs
```

结果按预期失败，失败点指向：

- `pages/login/index` 缺少「手机号快捷登录」。
- `pages/login/index` 缺少 `getPhoneNumber` 绑定。
- `src/api/auth.ts` 缺少快捷登录 helper。
- `dist/build` / `dist/dev` 登录页产物缺少合规快捷登录入口。

### 2.2 实现内容

`kaipai-frontend/src/api/auth.ts`

- 新增 `loginByPhoneQuickAuth(code, inviteCode?)`。
- 对授权 code 做 trim 和空值保护。
- 继续调用既有后端 `/api/auth/wechat-login` 合同。
- 缺 code 错误文案使用「手机号授权结果缺少 code」，不使用「微信授权」类品牌化文案。

`kaipai-frontend/src/utils/runtime.ts`

- 新增 `canUsePhoneQuickAuth()`。
- 新增 `getPhoneQuickAuthBlocker()`。
- 继续承接运行时配置和 `VITE_ENABLE_WECHAT_AUTH=false` 开关。
- 用户可见不可用文案使用「手机号快捷登录入口未启用，请使用手机号验证码登录 / 注册。」。

`kaipai-frontend/src/pages/login/index.vue`

- 在短信「登录 / 注册」按钮下方恢复 `button.login-page__phone-quick`。
- 按钮文案为「手机号快捷登录」或登录中态。
- 已勾选协议、能力可用且非 loading 时才设置 `open-type="getPhoneNumber"`。
- 绑定 `@getphonenumber="handlePhoneQuickLogin"`。
- 未勾选协议点击时只弹协议确认，确认后勾选协议，不直接触发授权。
- 授权拒绝、缺 code、能力不可用、后端失败都给出自有能力口径 toast。
- 登录成功后复用既有顺序：`setUserData()` -> `navigateAfterLogin()` -> `syncActorRuntimeStateAfterNavigation()`。
- 不恢复 `wechat-login.png`、`login-page__wechat-icon` 或「微信登录 / 微信一键登录 / 微信授权」可见文案。

`00-187` 文档与脚本

- `requirements.md` 修正为“保留合规手机号快捷登录入口，禁止官方混淆元素”。
- `design.md` 依赖从旧 `loginByWechat / canUseWechatAuth` 口径改为 `loginByPhoneQuickAuth / canUsePhoneQuickAuth`。
- `execution.md` 保留 `0679e09` 删除入口的历史事实，但标记为已由 `00-195 / 00-196` 纠偏。
- `scripts/verify-miniapp-review-login-gate.mjs` 现在要求源码和构建产物都存在合规快捷登录入口。

### 2.3 验证结果

| 验证项 | 命令 | 结果 |
|---|---|---|
| 前端类型检查 | `cd kaipai-frontend && npm run type-check` | 通过 |
| 小程序构建 | `cd kaipai-frontend && npm run build:mp-weixin` | 通过；仅 Sass legacy JS API 警告；`postbuild:mp-weixin` 已同步到 `dist/dev/mp-weixin` |
| 包体审计 | `cd kaipai-frontend && npm run audit:mp-package` | 通过；main `524.65 KB`，`pkg-card 211.01 KB`，`pkg-tools 28.23 KB`，均低于 `2 MB` |
| 00-187 登录门禁 | `node .sce\specs\00-187-current-phase-miniapp-review-login-gate-fix\scripts\verify-miniapp-review-login-gate.mjs` | 通过；源码、`dist/build`、`dist/dev` 均通过 |
| 00-188 复审合规 | `node .sce\specs\00-188-current-phase-miniapp-review-compliance-audit-fix\scripts\verify-miniapp-review-compliance-audit.mjs` | 通过；源码、`dist/build`、`dist/dev` 均通过 |
| 产物核验 | `rg -n "手机号快捷登录|getPhoneNumber|bindgetphonenumber|login-page__phone-quick|wechat-login|login-page__wechat-icon" ...` | `dist/build` 与 `dist/dev` 登录页 WXML/WXSS/JS 均包含快捷登录入口；未命中官方 logo 风险项 |
| 空白检查 | `git diff --check` / `git -C kaipai-frontend diff --check` | 仅 LF/CRLF 提示，无 whitespace error |

### 2.4 产物结论

- `dist/build/mp-weixin/pages/login/index.wxml` 存在 `button.login-page__phone-quick` 与 `bindgetphonenumber`。
- `dist/dev/mp-weixin/pages/login/index.wxml` 存在 `button.login-page__phone-quick` 与 `bindgetphonenumber`。
- `dist/build/mp-weixin/pages/login/index.js` 存在「手机号快捷登录」与 `getPhoneNumber`。
- `dist/dev/mp-weixin/pages/login/index.js` 存在「手机号快捷登录」与 `getPhoneNumber`。
- 登录页构建产物未恢复 `wechat-login.png` 或 `login-page__wechat-icon`。

### 2.5 当前结论

`pages/login/index` 已恢复合规版「手机号快捷登录」入口。当前登录页同时保留短信验证码登录和手机号快捷登录；快捷登录由用户主动点击触发，未勾协议时不会直接拉起授权；可见文案没有恢复「微信登录 / 微信一键登录 / 微信授权」。
