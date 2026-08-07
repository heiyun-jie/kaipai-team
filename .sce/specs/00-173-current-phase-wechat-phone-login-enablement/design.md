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

1. `kaipaile-server/src/main/java/com/kaipai/service/auth/impl/AuthServiceImpl.java`
   - 微信首次自动注册默认 `userType=1`。
   - 已注册用户保持既有身份。
   - 登录响应补齐 `phone`，避免微信登录场景前端用户态缺少手机号。
2. `kaipaile-server/src/main/java/com/kaipai/model/auth/dto/WechatLoginReqDTO.java`
   - 明确 code 来源为 `getPhoneNumber` 返回的手机号授权 code。
3. `kaipaile-server/src/main/java/com/kaipai/model/auth/dto/LoginRespDTO.java`
   - 登录 / 注册响应显式包含手机号。
4. `kaipaile-server/scripts/start-local-backend.ps1`
   - 读取并校验 gitignored 微信配置，编排端口 owner 预检、重启、PID 绑定和 HTTP 就绪门禁。
   - 只把微信配置写入隔离子进程环境，不修改启动器自身的进程环境。
5. `kaipaile-server/scripts/start-local-backend-child.ps1`
   - 作为凭据隔离边界，仅从自身进程环境接收微信配置并启动 Java 子进程。
   - appSecret 不进入 PowerShell / Java 命令行；Java 创建后立即清除子启动器自身的微信凭据环境值。
   - 通过一次性文件回传 Java PID，并在 Java 存活期间维持 stdout / stderr 重定向监督。
6. `kaipaile-server/scripts/package-backend.ps1`
   - dev 打包完成后只提示统一启动入口，避免继续引导裸 `java -jar`。
7. `kaipaile-server/src/test/java/com/kaipai/module/server/auth/service/impl/AuthServiceImplTest.java`
   - 固化缺配置时在用户查询前失败的业务合同。
8. `kaipaile-server/scripts/tests/run-start-local-backend-regression.ps1`
   - 使用临时 workspace、合成凭据和 Fake Java 覆盖非目标 owner 拒绝、同端口互斥、不同端口 PID 隔离、超时清理与凭据环境传播。

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

本地开发不把真实值复制到后端源码或命令行。统一启动入口读取：

```text
.sce/config/local-secrets/wechat-miniapp.env
  -> validate pair + placeholder + project appId match
  -> port-scoped named mutex + runtime directory
  -> isolated child-launcher environment
  -> start-local-backend-child.ps1 starts Java, clears its own credential values
  -> one-time launch PID
  -> exact process identity + strict HTTP readiness
  -> atomic port-scoped backend.pid publication
```

启动脚本的 `-ValidateOnly` 模式只输出存在性和合法性结论，不输出 appSecret。

`-Restart` 的进程身份判定必须同时满足：

1. Java 命令行中的 `-jar` 参数等于规范化后的完整后端 jar 路径，不能只按 jar 文件名或子串匹配。
2. Java 命令行中的 `--server.port` 精确等于本次 `-Port`。
3. 端口上的全部 owner 必须先完成身份校验，再进入停止阶段；任一 owner 不满足时不得先停掉其他 owner。

同一 workspace / port 的启动过程由命名互斥锁串行化；不同 port 使用独立的 `port-<Port>/backend.pid` 与唯一日志名。旧进程停止后先执行独占端口绑定探针，避免 Windows 动态出站端口竞争造成新 Tomcat 假启动。

启动后的 HTTP 就绪门禁固定使用 `GET /api/v3/api-docs/swagger-config`，并满足：

1. 发起请求前先确认目标端口 listener owner 为本次新启动 Java PID。
2. 禁止跟随 HTTP 重定向；只接受直接 `200` 与 `application/json`。
3. JSON 必须可解析，`url=/api/v3/api-docs` 且 `configUrl=/api/v3/api-docs/swagger-config`。
4. 成功响应后立即重新查询进程身份与 listener，并再次确认 owner PID 仍等于本次新启动 Java PID，避免旧进程响应或检查时序造成假阳性。
5. 正式 PID 文件只在上述检查完成后原子发布；此前的一次性 launch PID 在成功或失败后均删除。

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
5. `cd kaipaile-server && powershell -File scripts/start-local-backend.ps1 -ValidateOnly`
6. 使用 placeholder、无效 appId、前后端 appId 不一致和缺失 `project.config.json` 输入执行 `-ValidateOnly`，确认启动前拒绝。
7. `cd kaipaile-server && powershell -File scripts/tests/run-start-local-backend-regression.ps1`
8. 本地后端通过统一脚本重启后，确认轻量 HTTP 就绪请求禁止重定向，且成功响应前后 listener owner 均为新 PID。
9. 用无效微信手机号授权 code 探测 `/api/auth/wechat-login`：
   - 预期进入“微信手机号换取失败：invalid code”分支。
   - 禁止仍返回“微信登录未配置小程序 appId/appSecret”。
10. 静态确认构建产物：
   - `dist/dev/mp-weixin/utils/runtime.js` 中微信开关编译为可用分支，不再固定禁用。
   - `pages/login/index` 仍输出 `getPhoneNumber` open-type 逻辑。

## 6. 风险与边界

1. 若线上后端未配置 `WECHAT_MINIAPP_APP_ID / WECHAT_MINIAPP_APP_SECRET`，前端入口可点击但后端会返回配置错误。
2. 微信 `getPhoneNumber` 能力只能在真实微信小程序环境完整验证，H5 无法替代真实授权。
3. 本轮不提交 appSecret，不改服务器部署脚本；发布时需要运维在服务器环境变量中配置 secret 并重启后端。
4. `.env.local` 会使开发构建请求本地 `8010`；因此“公网后端已配置”不能替代本地后端启动门禁验证。
