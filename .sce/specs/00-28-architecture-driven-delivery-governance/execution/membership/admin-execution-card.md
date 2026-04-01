# 会员能力与模板配置闭环后台执行卡

## 1. 执行卡名称

会员能力与模板配置闭环 - 后台管理端执行卡

## 2. 归属切片

- `../../slices/membership-template-capability-slice.md`

## 3. 负责范围

- 会员产品页、会员账户页、会员权益说明页
- 场景模板页、主题 token 配置页、分享产物配置页、发布日志页
- 路由、菜单、权限点、操作弹窗和状态回显
- 运营视角的产品维护、账户开关、模板发布、回滚和版本回看

## 4. 不负责范围

- 会员账户、模板配置、发布日志的后端落库规则
- 小程序名片页、等级中心、命理页的前端展示
- 真正支付 / 退款资金链路
- 页面自行推断会员能力和模板能力的临时兼容逻辑

## 5. 关键输入

- 上位 Spec：
  - `00-11 platform-admin-console`
  - `05-05 card-share-membership`
  - `00-28 architecture-driven-delivery-governance`
- 关键文件：
  - `kaipai-admin/src/views/membership/ProductsView.vue`
  - `kaipai-admin/src/views/membership/AccountsView.vue`
  - `kaipai-admin/src/views/content/TemplatesView.vue`
  - `kaipai-admin/src/api/membership.ts`
  - `kaipai-admin/src/api/content.ts`
  - `kaipai-admin/src/types/membership.ts`
  - `kaipai-admin/src/types/content.ts`
  - `kaipai-admin/src/router/index.ts`
  - `kaipai-admin/src/constants/menus.ts`
  - `kaipai-admin/src/constants/permission.ts`
  - `kaipai-admin/src/constants/permission-registry.ts`

## 6. 目标交付物

- 现有会员产品页、会员账户页、模板页稳定可用
- 补齐会员权益页、主题 token 页、分享产物页、发布日志页，形成完整后台治理入口
- 路由、菜单、权限点和页面动作与后端真实能力对齐
- 页面只消费后台聚合接口，不自行拼装前台数据
- 运营能真实完成“配产品、开会员、配模板、发版本、调主题、调产物”的日常动作

## 7. 关键任务

1. 固化现有会员产品页
   - `ProductsView.vue` 继续承担产品列表与新建动作
   - 补齐编辑、启用、停用、排序、详情回看入口
2. 固化现有会员账户页
   - `AccountsView.vue` 继续承担列表、手工开通、延期、关闭
   - 补齐详情与变更日志查看入口
3. 固化现有模板页
   - `TemplatesView.vue` 承担模板列表、基础编辑、发布、回滚
   - 补齐启用、停用、排序、详情查看和版本说明
4. 补齐缺失治理页
   - 会员权益页
   - 主题 token 配置页
   - 分享产物配置页
   - 发布日志页
5. 对齐后台入口与权限
   - 当前路由和菜单只覆盖 `membership/products`、`membership/accounts`、`content/templates`
   - 需要把权益、主题、产物、发布日志这些后端已具备的能力真正暴露出来

## 8. 依赖项

- 后端要先稳定产品 / 账户 / 权益 / 模板 / 主题 / 产物 / 发布日志接口与 DTO
- 权限码必须与服务端 `@PreAuthorize` 一一对应
- 若页面需要展示能力矩阵、产物预设、发布版本，后端应提供可消费结构而不是让后台自行推断 JSON

## 9. 验证方式

- 会员产品可新建、编辑、启停用、排序并刷新可见
- 会员账户可开通、延期、关闭并查看详情或日志
- 模板可创建、编辑、发布、回滚并查看版本记录
- 主题 token 与分享产物配置修改后可回显且可追溯
- 无权限账号看不到对应页面或动作按钮，接口访问被正确拦截

## 10. 完成定义

- 后台不再只有产品 / 账户 / 模板三块局部能力，而是形成完整会员与模板治理入口
- 页面动作、权限、详情与列表口径一致
- 后台消费的是统一后端契约，而不是页面自己推导会员或模板能力
- 可以支撑会员与模板闭环的联调和日常运营
- 不再出现“后端有接口但后台没有入口”的长期悬空能力

## 11. 风险与备注

- 当前后台页面比前台成熟，但 `api/membership.ts` 与 `api/content.ts` 仍只覆盖部分能力，和服务端控制器能力并不完全对齐
- 当前路由和菜单没有暴露权益、主题 token、分享产物、发布日志等页面，即便后端有能力也会长期沉没
- 若后台继续直接编辑 JSON 但没有结构化校验，模板和权益配置很容易演化成难以治理的配置黑盒
