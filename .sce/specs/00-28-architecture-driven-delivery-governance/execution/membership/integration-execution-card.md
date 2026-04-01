# 会员能力与模板配置闭环联调执行卡

## 1. 执行卡名称

会员能力与模板配置闭环 - 联调与回归执行卡

## 2. 归属切片

- `../../slices/membership-template-capability-slice.md`

## 3. 负责范围

- 串联后台治理、后端输出、小程序恢复三端的联调顺序
- 定义会员与模板闭环的端到端验证矩阵
- 收口演员端接口缺口、本地 resolver 依赖和后台入口缺口
- 明确“局部完成”和“闭环完成”的验收边界

## 4. 不负责范围

- 单独补做小程序页面
- 单独补做会员或模板后端接口
- 单独补做后台缺失页面
- 任何脱离闭环验收的功能扩展

## 5. 关键输入

- 上位切片：
  - `../../slices/membership-template-capability-slice.md`
- 执行卡：
  - `frontend-execution-card.md`
  - `backend-execution-card.md`
  - `admin-execution-card.md`
- 关键链路文件：
  - `kaipai-frontend/src/pkg-card/membership/index.vue`
  - `kaipai-frontend/src/pkg-card/actor-card/index.vue`
  - `kaipai-frontend/src/pages/actor-profile/detail.vue`
  - `kaipai-admin/src/views/membership/ProductsView.vue`
  - `kaipai-admin/src/views/content/TemplatesView.vue`
  - `kaipaile-server/src/main/java/com/kaipai/module/controller/membership/MembershipController.java`
  - `kaipaile-server/src/main/java/com/kaipai/module/controller/card/CardController.java`
  - `kaipaile-server/src/main/java/com/kaipai/module/controller/admin/membership/AdminMembershipController.java`
  - `kaipaile-server/src/main/java/com/kaipai/module/controller/admin/content/AdminContentController.java`

## 6. 目标交付物

- 一条可重复执行的“后台配置 -> 后端下发 -> 前台恢复”联调路径
- 一份问题清单模板：前端 / 后端 / 后台分别归因
- 一份回归清单：会员状态、模板版本、主题 token、分享产物、权限、日志
- 一次明确的“会员能力与模板配置闭环完成度”验收结论

## 7. 关键任务

1. 先收口演员端接口
   - 当前后台治理接口相对完整，但 `MembershipController`、`CardController` 为空
   - 联调前必须先补齐小程序侧真实查询接口，否则前端只能继续吃本地 resolver
2. 建立会员场景矩阵
   - 未开通会员
   - 手工开通会员
   - 延期会员
   - 关闭会员
   - AI 配额与分享产物能力同步变化
3. 建立模板场景矩阵
   - 新建模板
   - 编辑模板
   - 发布模板
   - 回滚模板
   - 更新主题 token
   - 更新分享产物预设
4. 建立前台回归矩阵
   - `membership`
   - `actor-card`
   - `actor-profile/detail`
   - `fortune`
   - `invite`
5. 收口归因与验收
   - 前台仍依赖本地完整规则库归前端 / 后端契约问题
   - 后台有接口无入口归后台治理问题
   - 演员端接口缺失归后端问题
   - 给出闭环完成或局部完成的明确结论

## 8. 依赖项

- 后台产品 / 账户 / 模板能力先稳定
- 演员端会员与模板接口必须先可用
- 准备至少一组基础用户、一组会员用户、一组模板已发布用户和一组模板回滚数据

## 9. 验证方式

- 场景 1：后台开通会员
  - 小程序会员状态同步变化
  - 名片页、命理页、邀请页可见产物能力同步变化
- 场景 2：后台关闭或延期会员
  - 等级中心与名片页能力结果同步变化
  - 日志可追溯
- 场景 3：后台发布模板 / 更新主题 / 更新产物
  - 名片页和公开详情页恢复最新配置
  - 邀请页、命理页与名片页主题结果一致
- 场景 4：后台回滚模板
  - 前台恢复到指定版本表现
  - 发布日志和操作日志可回看
- 场景 5：权限与入口
  - 无权限账号看不到对应页面或动作
  - 后台页面入口与服务端权限码一致

## 10. 完成定义

- 三端联调路径可重复执行
- 会员状态、模板状态、主题 token、分享产物 gating 口径一致
- 前端不再依赖本地完整规则库作为唯一真相
- 缺陷能够明确归因到前端 / 后端 / 后台
- 可以给出“会员能力与模板配置闭环已完成”或“仍是局部完成”的明确结论

## 11. 风险与备注

- 若不先补演员端接口，后台配置再完整也只能停留在“后台自证完成”，无法带动前台恢复
- 若只验证会员页，不验证名片页、公开详情页、命理页、邀请页，就不算模板与能力闭环
- 若没有回滚测试数据，模板版本治理很容易只做到“能发布”而没有“能回退”
