# 00-195 当前阶段小程序手机号快捷登录入口回归定位 - 技术设计

## 1. 调查目标

本轮不改代码，只沉淀一次可追溯定位：

```text
当前页面现象
  -> pages/login/index 只剩短信验证码登录
  -> 没有“手机号快捷登录”

历史定位
  -> 84c2778 仍有“手机号快捷登录”
  -> 0679e09 删除完整快捷登录入口
  -> 54d8a31 继续基于删除后的页面补登录流程，没有恢复入口

文档定位
  -> 00-187 design/tasks 保留入口并去品牌化
  -> 00-187 requirements/execution/script 错误固化删除入口
```

_Requirements: 3.1, 3.2, 3.3, 3.4_

## 2. 调查对象

### 代码对象

- `kaipai-frontend/src/pages/login/index.vue`
- `kaipai-frontend/src/api/auth.ts`
- `kaipai-frontend/src/utils/runtime.ts`
- `kaipai-frontend/src/static/icons/wechat-login.png`

### SCE 对象

- `.sce/specs/00-173-current-phase-wechat-phone-login-enablement/`
- `.sce/specs/00-187-current-phase-miniapp-review-login-gate-fix/`
- `.sce/specs/00-188-current-phase-miniapp-review-compliance-audit-fix/`
- `.sce/specs/00-190-current-phase-miniapp-login-back-and-mine-review-supplement/`
- `.sce/specs/spec-code-mapping.md`

## 3. 调查命令

使用 `kaipai-frontend` 子仓库历史定位入口：

```powershell
git -C kaipai-frontend log --oneline --decorate --all -- src/pages/login/index.vue
git -C kaipai-frontend log --oneline --decorate --all -S "手机号快捷登录" -- src/pages/login/index.vue
git -C kaipai-frontend log --oneline --decorate --all -S "getPhoneNumber" -- src/pages/login/index.vue
git -C kaipai-frontend log --oneline --decorate --all -S "loginByWechat" -- src/pages/login/index.vue src/api/auth.ts src/utils/runtime.ts
```

使用 diff 还原改动内容：

```powershell
git -C kaipai-frontend show --unified=80 84c2778 -- src/pages/login/index.vue
git -C kaipai-frontend show --unified=80 0679e09 -- src/pages/login/index.vue
git -C kaipai-frontend show --unified=80 0679e09 -- src/api/auth.ts src/utils/runtime.ts
git -C kaipai-frontend show --unified=80 54d8a31 -- src/pages/login/index.vue
```

使用 `rg` 核对当前运行态源码：

```powershell
rg -n "getPhoneNumber|loginByWechat|手机号快捷登录|handleWechatLogin|wechat-login" kaipai-frontend/src/pages/login/index.vue kaipai-frontend/src/api/auth.ts kaipai-frontend/src/utils/runtime.ts
```

## 4. 判定规则

### 当前页面状态

当前 `pages/login/index` 只有以下短信验证码登录元素：

- `请输入手机号`
- `请输入验证码`
- `获取验证码`
- `登录 / 注册`

当前页面不包含：

- `getPhoneNumber`
- `handleWechatLogin`
- `loginByWechat`
- `手机号快捷登录`

### 回归来源

如果某提交同时删除以下对象，则判定为删除完整快捷登录链路，而不是隐藏入口：

- 登录页模板中的 `button`。
- `open-type="getPhoneNumber"`。
- `@getphonenumber="handleWechatLogin"`。
- `handleWechatLogin()`。
- `handleWechatButtonClick()`。
- `loginByWechat()` API helper。
- `canUseWechatAuth()` / `getWechatAuthBlocker()` runtime helper。

### 文档冲突

`00-187/design.md` 和 `00-187/tasks.md` 仍保留正确意图：

- 去除手机号快捷登录按钮中的微信官方 logo。
- 可见文案统一为「手机号快捷登录」。
- 授权失败、缺 code、配置不可用、后端失败文案去「微信登录」品牌化。

`00-187/requirements.md`、`execution.md` 和 `verify-miniapp-review-login-gate.mjs` 错误扩大为：

- 不展示 `getPhoneNumber`。
- 不存在手机号快速验证入口。
- 脚本把 `getPhoneNumber|手机号快捷登录|phone-quick` 作为失败项。

## 5. 输出物

- `requirements.md`：调查需求和验收标准。
- `design.md`：调查对象、命令、判定规则。
- `tasks.md`：本轮定位与文档更新任务。
- `execution.md`：实际命令结果、提交时间线、根因结论和后续修复边界。
- `.sce/specs/README.md`：新增 `00-195` 索引。
- `.sce/specs/spec-code-mapping.md`：新增 `00-195` 文档追溯。

## 6. 后续修复建议

本轮不恢复入口。后续修复应至少包含：

1. 修正 `00-187` 中“删除入口”的错误要求和验收脚本。
2. 恢复 `getPhoneNumber` 按钮，按钮文案为「手机号快捷登录」。
3. 不恢复 `/static/icons/wechat-login.png`。
4. 不出现「微信登录」「微信一键登录」「微信授权」等用户可见品牌化文案。
5. 登录成功路径继续沿用 `54d8a31` 后的非阻断运行态同步逻辑。
6. 重新执行 `type-check`、`build:mp-weixin`、包体审计和复审合规脚本。

_Requirements: 3.4_
