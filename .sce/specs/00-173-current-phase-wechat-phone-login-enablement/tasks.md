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

## Phase 5: 2026-07-31 配置故障复发治理（>= 3 次）

- [x] 标记同一“微信登录未配置小程序 appId/appSecret”问题已至少复发 3 次。
- [x] 复现并确认当前小程序开发产物请求本地 `8010`，而本地 Java 进程由裸命令启动、未加载合法 secret 文件。
- [x] 新增主 / 子启动器，成组校验配置并通过隔离子启动链环境向 Java 传播，命令行不携带 appSecret。
- [x] 将 dev 打包完成提示收口到统一启动脚本，不再继续引导裸 Java 启动。
- [x] 启动脚本拒绝 placeholder、无效 / 漂移 appId、缺失项目配置和误停非目标端口进程。
- [x] 增加 workspace / port 命名互斥、port 级 PID / 日志隔离、一次性 launch PID、失败清理与独占端口绑定门禁。
- [x] 使用轻量 Swagger 配置端点执行无重定向 HTTP 就绪检查，并在响应前后绑定新 Java PID。
- [x] 新增无 Pester 依赖的 PowerShell 回归套件，覆盖 owner 拒绝、同端口互斥、不同端口 PID 隔离、超时清理和凭据环境传播。
- [x] 修正 `.sce/config/wechat-miniapp.env.example` 中已漂移的示例 appId。
- [x] 补充后端缺配置错误合同测试。
- [ ] 基于最终脚本连续重启本地 `8010` 后端，并确认正式 PID、HTTP 就绪和无效 code 错误分支。
- [ ] 执行最终后端测试、SCE 审计、差异检查与 appSecret 精确泄漏扫描，并如实回填结果。
