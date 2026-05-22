# 00-173 任务

## Phase 1: Spec

- [x] 新增 `00-173`，承接微信后台已开通后的真实一键登录启用。
- [x] 明确前端入口、后端配置、微信手机号换取和首次注册身份合同。
- [x] 明确不提交 appSecret、不改变短信登录主链。

## Phase 2: Frontend

- [x] 将小程序微信登录入口改为默认启用，显式 `VITE_ENABLE_WECHAT_AUTH=false` 时才关闭。
- [x] 登录页校验 `getPhoneNumber` 返回 code 后再请求后端。
- [x] 构建产物确认微信登录入口不再被固定 blocker 禁用。

## Phase 3: Backend

- [x] 微信首次自动注册默认创建演员身份。
- [x] 补充微信登录 code 来源说明。
- [x] 编译 / 测试通过。

## Phase 4: Verification

- [x] 前端类型检查通过。
- [x] 微信小程序构建通过。
- [x] 小程序包体审计通过。
- [x] 后端测试通过。
- [x] 执行记录回填。

## Acceptance

- [x] 微信登录入口可在小程序构建中启用 `getPhoneNumber`。
- [x] 空 code 不会请求后端。
- [x] 微信首次注册用户不会再返回 `userType=0`。
- [x] 不提交微信 appSecret。
