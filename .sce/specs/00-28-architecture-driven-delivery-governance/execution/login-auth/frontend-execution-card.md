# 登录鉴权与前台会话闭环前端执行卡

## 1. 执行卡名称

登录鉴权与前台会话闭环 - 小程序前端执行卡

## 2. 归属切片

- `../../slices/login-auth-capability-slice.md`

## 3. 负责范围

- 登录页手机号验证码登录 / 注册交互
- 微信手机号授权入口、显隐和错误提示
- `stores/user` 会话恢复与登录后状态同步
- `inviteCode / scene` 承接与注册透传
- 运行时 mock 开关与微信能力显式 gating

## 4. 不负责范围

- 短信验证码存储和校验
- 微信手机号换取接口实现
- 后台账号登录和后台权限体系
- 真实短信商用接入

## 5. 关键输入

- 上位 Spec：
  - `00-27 mini-program-frontend-architecture`
  - `01-01 page-login`
  - `05-10 invite-referral`
  - `00-28 architecture-driven-delivery-governance`
- 关键文件：
  - `kaipai-frontend/src/pages/login/index.vue`
  - `kaipai-frontend/src/api/auth.ts`
  - `kaipai-frontend/src/stores/user.ts`
  - `kaipai-frontend/src/utils/runtime.ts`
  - `kaipai-frontend/src/utils/request.ts`
  - `kaipai-frontend/src/utils/invite.ts`

## 6. 目标交付物

- 手机号登录 / 注册与微信一键登录都能挂到真实接口
- 登录成功后先建立会话，再同步 `verify / invite / level`
- 登录页可稳定承接 `inviteCode / scene`
- 微信按钮显隐和失败提示受显式运行时开关控制
- 真实环境不再允许因为前端兜底而回退到 `mock-code`

## 7. 关键任务

1. 收口前端登录数据源
   - `api/auth.ts` 统一承接短信、注册、微信登录
   - `stores/user.ts` 统一承接 token、user session 和登录后同步
2. 回接登录页
   - `pages/login/index.vue` 接收 `inviteCode / scene`
   - 登录和注册模式下的文案、按钮态、错误态清楚
   - 微信登录缺少授权 code 时必须显式报错
3. 收口运行时开关
   - `utils/runtime.ts` 用显式开关控制微信登录可见性
   - 不再把真实环境错误吞成 mock 成功
4. 收口登录后时序
   - 登录成功后再跑 `syncActorRuntimeState`
   - 匿名态不提前请求受保护数据
5. 补齐前端验证说明
   - 手机号登录
   - 手机号注册 + 邀请码
   - 微信老用户登录
   - 微信新用户自动注册

## 8. 依赖项

- 后端 `auth / user` 契约先稳定
- `inviteCode` 消费规则必须由后端统一定义
- 真实环境是否展示微信按钮，依赖 `VITE_ENABLE_WECHAT_AUTH` 与后端微信配置同步确认

## 9. 验证方式

- 登录页携带 `inviteCode / scene` 进入时能正确提示并透传
- 手机号登录 / 注册成功后可建立会话并进入正确路由
- 微信授权返回缺少 code 时前端显式报错，不继续伪造成功
- 会话恢复后再同步 `verify / invite / level`，不提前请求受保护接口
- `npm run type-check` 通过

## 10. 完成定义

- 前端登录入口都接回真实链路
- 登录后会话和受保护数据同步时序稳定
- 邀请码透传口径统一
- 微信按钮显隐、失败提示和 mock 开关口径一致
- 前端可明确给出“已接真”还是“仍受配置阻塞”的判断

## 11. 风险与备注

- 若登录页继续保留真实环境 `mock-code` 回退，会把微信权限或运行时问题伪装成接口可用
- 若 `bootstrapSession` 与登录后同步分离失控，首屏 protected data 很容易再次回到“先请求、后建会话”
- 若邀请态在登录页和 `stores/user` 之间各写一套透传逻辑，后面会再次分裂
