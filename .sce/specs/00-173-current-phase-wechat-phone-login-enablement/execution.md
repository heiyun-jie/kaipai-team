# 00-173 执行记录

## 1. 问题契约

用户反馈：微信后台已经配置成功，现在需要更新后端和微信小程序，实现微信一键登录。

已核对当前事实：

1. 小程序 AppID 为 `wx4dcc4e1066fd0fb9`。
2. 前端 `.env / .env.local / .env.example` 中 `VITE_ENABLE_WECHAT_AUTH=false`，导致登录页微信按钮不挂载 `getPhoneNumber`。
3. 登录页已有 `getPhoneNumber` 回调和 `/api/auth/wechat-login` 调用，但缺少空 code 前置校验。
4. 后端已有 `/api/auth/wechat-login` 与微信 `getuserphonenumber` 调用骨架。
5. 后端微信首次自动注册当前写入 `userType=0`，会被前端移动端身份校验拦截。

## 2. 本轮边界

本轮处理：

1. 开启小程序微信登录入口构建开关。
2. 前端补齐微信手机号授权 code 校验。
3. 后端修复微信首次注册默认身份为演员。
4. 验证前端构建、包体和后端测试。

本轮不处理：

1. 不提交微信 appSecret。
2. 不改手机号验证码登录 / 注册。
3. 不新增数据库字段。
4. 不做微信登录后角色选择页。

## 3. 实施记录

已完成：

1. 新增 `00-173-current-phase-wechat-phone-login-enablement`，明确微信后台能力已开通后的前后端启用边界。
2. 更新 `.sce/specs/README.md` 与 `.sce/specs/spec-code-mapping.md`，登记 `00-173`。
3. 修改 `kaipai-frontend/src/utils/runtime.ts`：
   - 微信登录入口默认启用。
   - 只有显式配置 `VITE_ENABLE_WECHAT_AUTH=false` 时关闭。
   - 规避 `.env / .env.local / .env.example` 被仓库 `.gitignore` 忽略后，发布构建继续默认禁用的问题。
4. 修改 `kaipai-frontend/src/pages/login/index.vue`：
   - 在 `getPhoneNumber:ok` 后校验 `event.detail.code`。
   - 若微信未返回手机号授权 code，则展示 `微信未返回手机号授权 code`，不请求后端。
   - 后端请求继续携带 `inviteCode` 与 `deviceFingerprint`。
5. 修改 `kaipaile-server/src/main/java/com/kaipai/module/server/auth/service/impl/AuthServiceImpl.java`：
   - 微信首次自动注册默认 `userType=1` 演员。
   - 已注册手机号仍保持既有身份，只刷新登录时间。
6. 修改 `kaipaile-server/src/main/java/com/kaipai/module/server/wechat/service/WechatMiniProgramService.java` 与实现：
   - 新增 `getPhoneNumber(code)`，集中承接微信 `wxa/business/getuserphonenumber`。
   - `AuthServiceImpl` 不再直接拼接微信手机号接口，只消费微信服务返回的手机号。
7. 修改 `WechatLoginReqDTO` 注释，明确 code 来源为微信 `getPhoneNumber` 返回的手机号授权 code。
8. 新增 `AuthServiceImplTest`，覆盖微信首次登录自动注册为演员身份。
9. 补齐 `LoginRespDTO.phone` 与 `buildLoginResp` 的手机号返回，避免微信登录没有前端输入手机号时写入空用户态。

未改：

1. 未提交微信 appSecret。
2. 未改手机号验证码登录 / 注册主链。
3. 未新增数据库字段。
4. 未改小程序 AppID，继续使用 `wx4dcc4e1066fd0fb9`。

## 4. 验证记录

已实际执行：

```powershell
cd kaipai-frontend
npm run type-check
npm run build:mp-weixin
npm run audit:mp-package
```

```powershell
cd kaipaile-server
mvn test
```

结果：

1. `npm run type-check` 通过。
2. `npm run build:mp-weixin` 通过，并由 `postbuild:mp-weixin` 同步到 `dist/dev/mp-weixin`。
3. `npm run audit:mp-package` 通过：
   - main：`533.43 KB / 2.00 MB`
   - pkg-card：`201.87 KB / 2.00 MB`
   - pkg-tools：`28.31 KB / 2.00 MB`
4. 构建产物确认：
   - `dist/dev/mp-weixin/utils/runtime.js` 中微信开关编译为可用分支：`"false"===String("true")` 为 false，不再固定禁用。
   - `dist/dev/mp-weixin/pages/login/index.js` 包含 `getPhoneNumber` 与 `微信未返回手机号授权 code`。
   - `dist/dev/mp-weixin/api/auth.js` 继续请求 `/api/auth/wechat-login`。
5. `mvn test` 通过：
   - Tests run: `34`
   - Failures: `0`
   - Errors: `0`
   - Skipped: `0`
6. 新增 `AuthServiceImplTest` 已覆盖微信首次注册：
   - mock 微信手机号授权 code -> `13800138000`
   - 自动注册 `userType=1`
   - 自动注册 `registerSource=3`
   - 登录响应返回 `phone=13800138000`
   - 返回 token 与 `userType=1`

上线必要条件：

1. 服务器必须配置：
   - `WECHAT_MINIAPP_APP_ID=wx4dcc4e1066fd0fb9`
   - `WECHAT_MINIAPP_APP_SECRET=<微信后台生成的 secret>`
2. 配置后需要重启后端。
3. 小程序需要使用本轮构建产物上传体验版 / 审核 / 发布。

## 5. 2026-07-31 配置故障复发治理（>= 3 次）

### 5.1 复发标记

用户明确反馈同类 `{message: "微信登录未配置小程序 appId/appSecret"}` 问题已至少出现 3 次。本问题已存在于本 Spec 的 `3.3 后端微信手机号换取` 验收合同中，因此不新建平行 Spec；在 `00-173` 内追加复发标记、本地启动门禁和验收记录。

### 5.2 根因证据

1. `kaipai-frontend/.env.local` 与当前 `dist/dev/mp-weixin` 把 API 指向 `http://127.0.0.1:8010`，不是公网 API。
2. 本地 `8010` Java 进程由裸命令 `java -jar target/kaipai-backend-1.0.0-SNAPSHOT.jar --spring.profiles.active=dev` 启动。
3. 当前 Process / User / Machine 环境均未向该进程提供 `WECHAT_MINIAPP_APP_ID / WECHAT_MINIAPP_APP_SECRET`。
4. gitignored `.sce/config/local-secrets/wechat-miniapp.env` 已存在，成组值通过仓库合法输入门禁，且 appId 与 `kaipai-frontend/project.config.json` 一致。
5. 裸 Java 启动不会自动读取 dotenv 文件，因此 `application.yml` 中两个 Spring placeholder 最终为空，`WechatMiniProgramService.isConfigured()` 返回 false。
6. 使用无效 code 的本地探测稳定返回“微信登录未配置小程序 appId/appSecret”；同一探测请求公网 `https://api.kplyyk.com` 已进入“微信手机号换取失败：invalid code”分支，证明当前生产运行进程已加载微信配置。

根因结论：**合法本地 secret 已存在，但本地后端启动链没有传播配置；不是配置键命名漂移，也不是微信接口或登录注册业务失败。**

### 5.3 持久修复

1. 新增 `kaipaile-server/scripts/start-local-backend.ps1`：
   - 默认读取 `.sce/config/local-secrets/wechat-miniapp.env`。
   - 校验 appId 格式、appSecret 非空/非 placeholder、前后端 appId 一致。
   - 通过隔离子启动器环境向 Java 传播真实值，不修改主启动器自身的进程环境，也不把 appSecret 放入命令行、控制台或日志。
   - `-ValidateOnly` 提供无敏感值预检。
   - `-Restart` 只允许替换同时匹配规范化完整 jar 路径与精确 `--server.port` 的 Java 进程。
   - 同一 workspace / port 由命名互斥锁串行化，不同 port 使用独立 PID / 日志目录。
   - 新 Java 先通过一次性 launch PID 建立身份，只有严格 HTTP 就绪后才原子发布正式 PID；任何失败均清理新 Java 与临时 / 正式 PID。
   - 旧 listener 退出后执行独占端口绑定探针，避免 Windows 动态出站端口抢占启动空档。
   - HTTP 就绪门禁固定使用轻量 `/api/v3/api-docs/swagger-config`，禁止重定向，校验 `200 + application/json + url/configUrl`，并在响应前后核对 listener owner PID 与进程启动时间。
2. 新增 `kaipaile-server/scripts/start-local-backend-child.ps1`，作为凭据隔离边界：仅从子进程环境读取微信配置、启动 Java、清除自身凭据环境值、通过一次性文件回传 PID，并在 Java 存活期间维持日志重定向监督；命令行不携带 appSecret。
3. 新增 `kaipaile-server/scripts/tests/run-start-local-backend-regression.ps1` 与 Fake Java / worker fixtures，使用临时 workspace 和合成凭据覆盖 owner 拒绝、同端口互斥、不同端口 PID 隔离、超时清理和凭据环境传播。
4. 更新 `kaipaile-server/scripts/package-backend.ps1`，dev 打包成功后直接提示统一启动命令，不再只给出容易漏掉微信配置的通用运行提醒。
5. 修正 `.sce/config/wechat-miniapp.env.example` 的示例 appId，使其与当前小程序 `project.config.json` 一致。
6. `AuthServiceImplTest` 新增缺配置错误合同，确认失败发生在用户查询 / 注册前。

### 5.4 启动器加固状态与待最终复验

第一次执行新脚本时，验证发现 PowerShell 5.1 将单个端口监听结果解包为标量，导致 `.Count` 门禁未进入；新进程因端口冲突退出，而旧进程的健康响应又可能造成假阳性。该次没有核销。

后续已围绕数组化、PID 绑定、凭据隔离、完整路径 / 端口身份判定和 HTTP 就绪语义继续加固。由于启动器仍在收口，本节此前记录的连续重启、HTTP `200`、PID 一致和无效 code 探测只作为阶段性观察，**不作为当前最终实现的通过证据**。

最终核销前必须基于最终文件重新执行并记录：

1. Windows PowerShell 5.1 对主启动器与 `start-local-backend-child.ps1` 的语法解析。
2. 合法配置、placeholder、无效 appId 和前后端 appId 不一致四类预检。
3. `-Restart` 对“规范化完整 jar 路径 + 精确 `--server.port`”的正向匹配，以及非目标 owner 的拒绝；全部 owner 必须先校验、后停止。
4. 连续两次 `-Restart`，每次均确认 `port-<Port>/backend.pid` 与目标端口 listener owner PID 一致。
5. 对无需鉴权、无业务写入的轻量 HTTP 就绪端点发起禁止重定向的请求；直接成功响应后重新查询 listener owner，并确认仍为本次新 PID。
6. 使用无效微信手机号授权 code 请求本地 `/api/auth/wechat-login`，确认进入微信接口错误分支且不再返回缺配置错误。
7. 对最终变更文件、最新 stdout / stderr 日志执行真实 appSecret 精确值泄漏扫描，但不输出 secret 值。
8. 重新执行后端测试、根仓 / 后端仓差异检查及 SCE 审计，并如实记录任何剩余红项。

### 5.5 历史观察与当前核销状态

加固前 / 加固过程曾观察到：

1. PowerShell 5.1 语法解析。
2. 使用当前 gitignored secret 执行 `-ValidateOnly`，结果为 appId 匹配、appSecret 合法。
3. 使用仓库示例 placeholder secret 执行 `-ValidateOnly`，启动脚本按预期拒绝。
4. `mvn -q -Dtest=AuthServiceImplTest test` 通过。
5. 本地 `8010` 健康检查与 owner PID 绑定检查通过。
6. 本地无效 code 微信配置探测通过，不再返回缺配置错误。
7. 后端全量 `mvn -q test` 通过：`43` tests，`0` failures，`0` errors，`0` skipped。
8. 根仓与后端仓 `git diff --check` 通过，仅有既有的 LF/CRLF 提示。
9. 真实 appSecret 未出现在本轮变更文件或最新运行日志中；本地 secret 文件仍由 `.gitignore` 排除。

上述结果对应当时文件与当时运行进程。主 / 子启动器完成本轮安全加固后，必须按 `5.4` 全量复验；复验记录回填前，启动器运行态门禁保持**待核销**，不得继续表述为最终 GREEN。

`cd kaipai-frontend && npm run audit:steering` 已执行但未通过，唯一报告为 `.sce/steering/CORE_PRINCIPLES.md` 的历史编号重复 / 不连续。该文件本轮无 worktree diff，因此按现有改动保护规则不在微信登录修复中改写；该结果不影响本轮后端测试与原始故障回归结论，但全局 steering audit 不能标记为 GREEN。
