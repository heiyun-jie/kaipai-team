# 实名认证闭环联调执行卡

## 1. 执行卡名称

实名认证闭环 - 联调与回归执行卡

## 2. 归属切片

- `../../slices/verify-capability-slice.md`

## 3. 负责范围

- 串联前端、后端、后台三端的联调顺序
- 定义端到端验证矩阵
- 收口阻塞项、缺陷清单和回归项
- 明确“局部完成”和“闭环完成”的验收边界

## 4. 不负责范围

- 单独补做后端功能
- 单独补做前端页面
- 单独补做后台组件
- 任何脱离联调目标的功能扩展

## 5. 关键输入

- 上位切片：
  - `../../slices/verify-capability-slice.md`
- 执行卡：
  - `frontend-execution-card.md`
  - `backend-execution-card.md`
  - `admin-execution-card.md`
- 关键链路文件：
  - `kaipai-frontend/src/pkg-card/verify/index.vue`
  - `kaipai-admin/src/views/verify/VerificationBoard.vue`
  - `kaipaile-server/src/main/java/com/kaipai/module/controller/verify/VerifyController.java`
  - `kaipaile-server/src/main/java/com/kaipai/module/controller/admin/verify/AdminVerifyController.java`

## 6. 目标交付物

- 一条可重复执行的实名认证端到端联调路径
- 一份问题清单模板：前端 / 后端 / 后台分别归因
- 一份回归清单：通过、拒绝、重提、权限、日志、gating
- 一次明确的“闭环完成”验收结论

## 7. 关键任务

1. 固化联调顺序
   - 后端接口稳定
   - 后台审核动作可用
   - 小程序提交流程可用
   - 最后做三端联调
2. 建立端到端场景矩阵
   - 首次提交成功
   - 审核通过
   - 审核拒绝
   - 拒绝后重提
   - 重复提交阻断
   - 无权限访问拦截
3. 建立回归矩阵
   - `mine`
   - `membership`
   - `actor-card`
   - 后台历史记录
   - 操作日志
4. 收口缺陷
   - 状态不同步
   - 拒绝原因丢失
   - 页面 gating 不一致
   - 权限和按钮显示不一致

## 8. 依赖项

- 后端接口和状态机先稳定
- 后台审核动作和前端状态消费都必须具备
- 至少准备一组可复现的实名测试数据
- 若要补页面级真实证据，默认走 `run-verify-mini-program-page-evidence.py` 与 `run-verify-admin-page-evidence.py`，不得回退到手工零散截图

## 9. 验证方式

- 场景 1：未认证用户提交实名申请
  - 小程序显示审核中
  - 后台待审核列表出现记录
- 场景 2：后台审核通过
  - 小程序状态刷新为已认证
  - `mine / membership / actor-card` 放行一致
- 场景 3：后台审核拒绝
  - 小程序可见拒绝原因
  - 用户可重提
  - 历史页可回看
- 场景 4：权限与日志
  - 无权限账号不能审核
  - 审核动作进入 `admin_operation_log`

## 10. 完成定义

- 三端联调路径可重复执行
- 关键场景矩阵全部走通
- 回归页口径一致
- 缺陷能明确归因到前端 / 后端 / 后台
- 可以给出“实名认证闭环已完成”或“仍是局部完成”的明确结论

## 11. 风险与备注

- 若联调过早开始，容易把未稳定接口问题错误归因到前端
- 若没有统一测试数据，审核通过 / 拒绝 / 重提链路容易验证不完整
- 若只验证实名认证页本身，不验证 `mine / membership / actor-card`，就不算闭环
- `2026-04-04` 已补齐页面级证据脚本入口：
  - `run-verify-mini-program-page-evidence.py`
  - `run-verify-admin-page-evidence.py`
  当前最新页面样本为：
  - `samples/20260404-021512-continue-verify-mini-page-evidence/summary.md`
  - `samples/20260404-021512-continue-verify-admin-page-evidence/summary.md`
