# 邀请裂变与邀请资格闭环联调执行卡

## 1. 执行卡名称

邀请裂变与邀请资格闭环 - 联调与回归执行卡

## 2. 归属切片

- `../../slices/invite-referral-capability-slice.md`

## 3. 负责范围

- 串联小程序前端、后端、后台三端的联调顺序
- 定义邀请闭环端到端验证矩阵
- 收口接口命名断层、缺陷清单和回归项
- 明确“局部完成”和“闭环完成”的验收边界

## 4. 不负责范围

- 单独补做后端演员端接口
- 单独补做小程序页面
- 单独补做后台页面
- 任何超出邀请闭环的扩展需求

## 5. 关键输入

- 上位切片：
  - `../../slices/invite-referral-capability-slice.md`
- 执行卡：
  - `frontend-execution-card.md`
  - `backend-execution-card.md`
  - `admin-execution-card.md`
- 关键链路文件：
  - `kaipai-frontend/src/pages/login/index.vue`
  - `kaipai-frontend/src/pkg-card/invite/index.vue`
  - `kaipai-frontend/src/pkg-card/membership/index.vue`
  - `kaipai-admin/src/views/referral/RiskView.vue`
  - `kaipaile-server/src/main/java/com/kaipai/module/controller/referral/ReferralController.java`
  - `kaipaile-server/src/main/java/com/kaipai/module/controller/admin/referral/AdminReferralController.java`

## 6. 目标交付物

- 一条可重复执行的“邀请 -> 注册 -> 生效 / 风险复核 -> 资格发放 -> 前台可见”联调路径
- 一份问题清单模板：前端 / 后端 / 后台分别归因
- 一份回归清单：接口命名、邀请状态、资格动作、分享产物、权限、日志
- 一次明确的“邀请裂变与邀请资格闭环完成度”验收结论

## 7. 关键任务

1. 先收口接口契约
   - 当前前端走 `/api/invite/*`，服务端演员端挂在 `/referral`
   - 联调前必须先决定统一命名或兼容策略，不能边做边猜
2. 建立端到端主场景矩阵
   - 已认证用户生成邀请码和小程序码
   - 新用户带 `inviteCode` 注册
   - 后台可见邀请记录
   - 满足门槛后邀请记录生效、邀请人数增长
   - 资格发放后前端消费同一口径
3. 建立风险治理场景矩阵
   - 同设备命中
   - 同小时高频命中
   - 风险待复核
   - 后台通过 / 作废 / 复核完成
4. 建立前台回归矩阵
   - `login`
   - `invite`
   - `membership`
   - `actor-card`
   - 邀请卡片 / 海报 / 公开页分享产物
5. 收口归因与验收
   - 接口不存在或命名不一致归后端契约
   - 页面展示不一致归前端消费
   - 权限、菜单、治理动作缺失归后台
   - 给出闭环完成或局部完成的明确结论

## 8. 依赖项

- 演员端邀请码、统计、记录、小程序码接口必须先可用
- 后台至少要具备风险复核和资格管理能力，记录页最好同步具备
- 需要一组可复现的邀请测试数据，包括正常邀请、待生效邀请、风险邀请、资格已发放用户

## 9. 验证方式

- 场景 1：已认证邀请人发起分享
  - 小程序可复制邀请码、邀请链接、生成海报
  - 登录页可收到 `inviteCode`
- 场景 2：新用户注册绑定邀请关系
  - 注册成功后后台出现 `referral_record`
  - 邀请页和后台记录一致
- 场景 3：邀请记录生效
  - 达到资料门槛后记录从待生效转已生效
  - 邀请人数与等级能力同步更新
- 场景 4：命中风险
  - 后台风险页可见记录
  - 复核结果正确影响邀请有效性
- 场景 5：资格发放与前台消费
  - 后台发放 / 撤销 / 延期后，小程序邀请页、等级中心、名片页口径一致

## 10. 完成定义

- 三端联调路径可重复执行
- 接口命名和字段口径完成收口
- 主场景、风险场景、资格场景全部走通
- 缺陷能够明确归因到前端 / 后端 / 后台
- 可以给出“邀请裂变与邀请资格闭环已完成”或“仍是局部完成”的明确结论

## 11. 风险与备注

- 若不先解决 `/invite` 与 `/referral` 的契约断层，联调会持续停留在接口打不通阶段
- 若只跑邀请页展示，不验证注册绑定、风险复核和资格发放，就不算闭环
- 若没有统一测试数据，待生效、风险待复核、资格已生效三类状态很容易漏测
