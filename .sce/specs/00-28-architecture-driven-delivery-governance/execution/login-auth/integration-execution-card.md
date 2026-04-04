# 登录鉴权与前台会话闭环联调执行卡

## 1. 执行卡名称

登录鉴权与前台会话闭环 - 联调与回归执行卡

## 2. 归属切片

- `../../slices/login-auth-capability-slice.md`

## 3. 负责范围

- 串联前端、后端、运行配置三端的联调顺序
- 定义端到端验证矩阵
- 收口阻塞项、缺陷清单和回归项
- 明确“局部完成”和“闭环完成”的验收边界

## 4. 不负责范围

- 单独补做后端功能
- 单独补做前端页面
- 单独补做环境变更
- 任何脱离登录闭环目标的功能扩展

## 5. 关键输入

- 上位切片：
  - `../../slices/login-auth-capability-slice.md`
- 执行卡：
  - `frontend-execution-card.md`
  - `backend-execution-card.md`
  - `admin-execution-card.md`
- 关键链路文件：
  - `kaipai-frontend/src/pages/login/index.vue`
  - `kaipai-frontend/src/stores/user.ts`
  - `kaipaile-server/src/main/java/com/kaipai/module/controller/auth/AuthController.java`
  - `kaipaile-server/src/main/java/com/kaipai/module/controller/user/UserController.java`

## 6. 目标交付物

- 一条可重复执行的登录端到端联调路径
- 一份问题清单模板：前端 / 后端 / 配置分别归因
- 一份回归清单：手机号登录、注册、邀请透传、会话恢复、页面级证据，以及未来批次的微信 / 正式短信入口
- 一次明确的“当前阶段闭环完成”或“仍是局部完成”的验收结论

## 7. 关键任务

1. 固化联调顺序
   - 先确认运行时配置
   - 再验证后端接口
   - 再验证前端按钮与流程
   - 最后做端到端回归
2. 建立端到端场景矩阵
   - 手机号发送验证码
   - 手机号登录
   - 手机号注册 + `inviteCode`
   - 会话恢复 + 受保护数据同步
   - 当前阶段页面级证据
   - 微信老用户登录 / 微信新用户自动注册 + `inviteCode`（未来批次）
   - 正式短信商用能力（未来批次）
3. 建立回归矩阵
   - `login`
   - `mine`
   - `membership`
   - `invite`
   - `role-select`
     当前真实样本先记为“未知身份用户专属页，待微信或独立 unknown-role 样本时再补”
4. 收口缺陷
   - 按钮显隐错误
   - 配置缺失时仍假装可用
   - 登录后状态不同步
   - 邀请码透传丢失

## 8. 依赖项

- 前端显式开关与后端微信配置必须同时确认
- 微信配置确认必须沿用 `.sce/runbooks/backend-admin-release/wechat-config-gate-runbook.md`，不能因为本地 secret 文件存在就跳过门禁
- 至少准备一组老用户和一组未注册手机号
- 若要验证微信自动注册透传，必须准备可追踪的邀请码样本
- 若要验证正式短信商用能力，必须另行建立未来批次样本，不与当前阶段手机号主链混写

## 9. 验证方式

- 场景 1：手机号验证码登录 / 注册
  - 可返回 token
  - 登录页完成路由分发
- 场景 2：当前阶段页面级证据
  - `run-login-auth-mini-program-page-evidence.py` 可稳定产出 `login(带inviteCode) -> mine -> membership -> invite`
  - 未登录页采证前必须先清理 DevTools 残留 `kp_token / kp_user`
- 场景 3：微信老用户登录（未来批次）
  - 页面展示按钮
  - 授权后登录成功
- 场景 4：微信新用户自动注册（未来批次）
  - 自动创建账号
  - `inviteCode` 透传不丢
- 场景 5：会话恢复
  - 页面刷新或重进后可恢复登录态
  - 再同步 `verify / invite / level`
- 场景 6：配置阻塞
  - 缺开关或缺 `appId / appSecret` 时，页面只展示降级提示
  - 后端报错与状态卡结论一致
- 场景 7：正式短信能力（未来批次）
  - 不再只看开发态 `sendCode`
  - 必须补真实短信通道、送达/失败口径与独立样本

## 10. 完成定义

- 端到端联调路径可重复执行
- 关键场景矩阵全部走通
- 运行时阻塞与功能缺陷可明确归因
- 可以给出“登录鉴权当前阶段闭环已完成”或“仍是局部完成”的明确结论

## 11. 风险与备注

- 若不先核对运行时开关，联调很容易把配置问题错误归因到前端或后端
- 若只测手机号登录，不测注册链与邀请码透传，就不能宣告当前阶段闭环
- 若只测登录成功，不测 `verify / invite / level` 的登录后同步，仍然只是半条链
- 若登录页页面证据没有先清理前台会话，`inviteCode` 落点会被旧 token 重定向到首页，不能当成有效登录页样本
- 若未来要宣告全量闭环，则还必须另行补微信真实样本与正式短信能力，不能拿当前阶段样本直接替代
