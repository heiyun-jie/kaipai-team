# 00-173 当前阶段微信手机号一键登录启用 - 技术设计

## 1. 设计结论

本轮把微信手机号一键登录打通为真实能力：

```text
login page getPhoneNumber
  -> event.detail.code
  -> POST /api/auth/wechat-login
  -> WeChat getuserphonenumber
  -> user login or default actor registration
  -> token + UserInfo
```

前端只接收微信授权 code，不接触 appSecret。后端只通过环境变量读取小程序 appId/appSecret。

## 2. 影响范围

### 2.1 小程序前端

1. `kaipai-frontend/src/utils/runtime.ts`
   - 微信登录入口默认启用；只有显式配置 `VITE_ENABLE_WECHAT_AUTH=false` 时关闭。
2. `kaipai-frontend/src/pages/login/index.vue`
   - 校验 `event.detail.code`，避免空 code 请求后端。

### 2.2 后端

1. `kaipaile-server/src/main/java/com/kaipai/module/server/auth/service/impl/AuthServiceImpl.java`
   - 微信首次自动注册默认 `userType=1`。
   - 已注册用户保持既有身份。
   - 登录响应补齐 `phone`，避免微信登录场景前端用户态缺少手机号。
2. `kaipaile-server/src/main/java/com/kaipai/module/model/auth/dto/WechatLoginReqDTO.java`
   - 明确 code 来源为 `getPhoneNumber` 返回的手机号授权 code。
3. `kaipaile-server/src/main/java/com/kaipai/module/model/auth/dto/LoginRespDTO.java`
   - 登录 / 注册响应显式包含手机号。

### 2.3 文档治理

1. `.sce/specs/README.md`
2. `.sce/specs/spec-code-mapping.md`
3. `.sce/specs/00-173-current-phase-wechat-phone-login-enablement/*`

## 3. 前端设计

### 3.1 入口门禁

继续沿用 `canUseWechatAuth()`：

```ts
VITE_API_BASE_URL 存在
AND VITE_ENABLE_WECHAT_AUTH !== 'false'
```

构建产物中微信按钮满足：

```text
open-type="{{t}}"
t = "getPhoneNumber" only when canUseWechatLogin && agreed && !loginLoading
```

### 3.2 授权回调

`handleWechatLogin` 增加 code 校验：

```ts
const wechatPhoneCode = event.detail?.code?.trim();
if (!wechatPhoneCode) {
  showToast('微信未返回手机号授权 code');
  return;
}
await loginByWechat(wechatPhoneCode, inviteCode);
```

该校验避免在微信能力、基础库或调试环境异常时，把空 code 传到后端。

## 4. 后端设计

### 4.1 配置

继续使用现有配置：

```yaml
wechat:
  miniapp:
    app-id: ${WECHAT_MINIAPP_APP_ID:}
    app-secret: ${WECHAT_MINIAPP_APP_SECRET:}
```

线上部署必须配置：

```text
WECHAT_MINIAPP_APP_ID=wx4dcc4e1066fd0fb9
WECHAT_MINIAPP_APP_SECRET=<微信后台生成的 secret>
```

### 4.2 微信手机号换取

继续复用现有 `WechatMiniProgramService.getAccessToken()` 与：

```text
https://api.weixin.qq.com/wxa/business/getuserphonenumber
```

后端错误直接返回业务错误，便于前端 toast 与排障。

### 4.3 首次注册身份

当前前端只允许 `UserRole.Actor=1` 或 `UserRole.Crew=2` 进入移动端。微信首次注册若写 `userType=0`，前端会立即执行不可用提示。

本轮将微信自动注册默认身份设为：

```java
private static final int USER_TYPE_ACTOR = 1;
```

这样首次微信登录可以直接进入演员主流程。后续如果需要微信登录时选择剧组身份，应另起 Spec 做登录后的角色选择页，而不是继续返回 `Unknown` 身份。

## 5. 测试设计

1. `cd kaipai-frontend && npm run type-check`
2. `cd kaipai-frontend && npm run build:mp-weixin`
3. `cd kaipai-frontend && npm run audit:mp-package`
4. `cd kaipaile-server && mvn test`
5. 静态确认构建产物：
   - `dist/dev/mp-weixin/utils/runtime.js` 中微信开关编译为可用分支，不再固定禁用。
   - `pages/login/index` 仍输出 `getPhoneNumber` open-type 逻辑。

## 6. 风险与边界

1. 若线上后端未配置 `WECHAT_MINIAPP_APP_ID / WECHAT_MINIAPP_APP_SECRET`，前端入口可点击但后端会返回配置错误。
2. 微信 `getPhoneNumber` 能力只能在真实微信小程序环境完整验证，H5 无法替代真实授权。
3. 本轮不提交 appSecret，不改服务器部署脚本；发布时需要运维在服务器环境变量中配置 secret 并重启后端。
