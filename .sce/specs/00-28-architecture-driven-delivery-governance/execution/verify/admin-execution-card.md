# 实名认证闭环后台执行卡

## 1. 执行卡名称

实名认证闭环 - 后台管理端执行卡

## 2. 归属切片

- `../../slices/verify-capability-slice.md`

## 3. 负责范围

- 实名认证待审核 / 历史记录页面
- 实名认证详情抽屉
- 审核通过 / 拒绝动作
- 后台筛选、状态展示、拒绝原因输入和联调回显

## 4. 不负责范围

- 后端加密、状态回写、数据库落库
- 小程序端认证提交页和前台 gating
- 第三方实名校验服务
- 操作日志后端实现细节

## 5. 关键输入

- 上位 Spec：
  - `00-11 platform-admin-console`
  - `00-28 architecture-driven-delivery-governance`
  - `05-09 identity-verification`
- 关键文件：
  - `kaipai-admin/src/views/verify/VerificationBoard.vue`
  - `kaipai-admin/src/views/verify/PendingView.vue`
  - `kaipai-admin/src/views/verify/HistoryView.vue`
  - `kaipai-admin/src/views/verify/VerifyListView.vue`
  - `kaipai-admin/src/api/verify.ts`
  - `kaipai-admin/src/types/verify.ts`

## 6. 目标交付物

- 待审核 / 历史记录可区分处理
- 详情抽屉可查看脱敏证件信息、审核信息和拒绝原因
- 审核通过 / 拒绝操作可用
- 页面筛选条件、状态标签、空态和错误态清楚
- 页面只消费后台聚合接口，不自行拼多个前台接口

## 7. 关键任务

1. 固化列表页与历史页分工
   - 待审核页只聚焦处理动作
   - 历史页聚焦回看
2. 固化详情抽屉信息结构
   - 验证 ID
   - 用户信息
   - 实名信息
   - 提交时间
   - 审核时间
   - 拒绝原因
3. 固化审核动作
   - 通过
   - 拒绝
   - 拒绝原因校验
4. 固化页面状态
   - 加载中
   - 空态
   - 失败态
   - 操作成功后的刷新
5. 对齐权限与接口
   - `page.verify.pending`
   - `page.verify.history`
   - `page.verify.detail`
   - `action.verify.approve`
   - `action.verify.reject`

## 8. 依赖项

- 后端详情、审核接口和状态字段要先稳定
- 拒绝原因字段必须可回显，否则历史记录无法闭环
- 后台权限码必须与服务端 `@PreAuthorize` 一致

## 9. 验证方式

- 待审核列表可筛选并打开详情
- 审核通过后，待审核页记录消失或状态刷新，历史页可见
- 审核拒绝时必须填写原因，并在历史页和详情里可回看
- 无权限账号看不到对应页面或操作按钮
- 匿名访问后台接口返回 `401`，低权限访问高风险动作被拦截

## 10. 完成定义

- 后台审核页可以真实处理申请
- 历史记录和详情信息可回看
- 拒绝原因输入、回显和刷新链路完整
- 按钮权限、页面权限和详情权限口径一致
- 后台不再只是演示页，而是可用治理入口

## 11. 风险与备注

- 若后台列表和历史页边界不清，运营会在同一页承担处理和回看两类职责
- 若拒绝原因没有强校验，前台失败态无法解释
- 若页面为兼容接口不一致而私自拼口径，后续联调成本会持续上升
