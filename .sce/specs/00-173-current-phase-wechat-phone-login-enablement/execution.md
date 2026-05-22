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
