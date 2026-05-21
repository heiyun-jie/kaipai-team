# 00-69 执行记录

## 1. 当前状态

- 已重新读取 `User Global Memory`
- 已重新核对当前主架构相关 Spec：`00-27`、`00-62`、`00-68`
- 已完成首轮事实盘点，确认当前代码与新架构存在明显偏差

## 2. 已确认的代码事实

### 2.1 前端

- `pages.json` 当前虽已切到 `home / history / mine` 三 tab，但仍保留大量旧页面：
  - `role-detail`
  - `apply-confirm`
  - `my-applies`
  - `apply-detail`
  - `project/create`
  - `project/role-create`
  - `apply-manage`
  - `company-profile/edit`
  - `role-select`
- `src/pages` 目录下还存在历史 `credit-*` 页面目录
- `pkg-card` 仍保留：
  - `membership`
  - `invite`
  - `fortune`
  - `verify`
  作为独立页面
- `pages/mine/index.vue` 仍残留：
  - 剧组资料
  - 投递反馈记录
  - 旧角色 / 招募相关统计口径

### 2.2 后台

- 当前后台菜单仍是多业务域并列：
  - dashboard
  - verify
  - referral
  - recruit
  - membership
  - payment
  - refund
  - content
  - system
- 与用户最新架构“控制台 / 用户中心”明显不一致
- `kaipai-admin/src/constants/menus.ts` 当前把上述域一比一输出为侧边栏顶级菜单；`kaipai-admin/src/router/index.ts` 也按同样的业务域逐条注册路由，说明后台当前不是“只有视觉文案没改”，而是菜单、路由和页面目录三层都仍按旧多业务域建模
- `kaipai-admin/src/views/` 当前目录仍保留：
  - `dashboard`
  - `verify`
  - `referral`
  - `recruit`
  - `membership`
  - `payment`
  - `refund`
  - `content`
  - `system`
- `kaipai-admin/src/views/dashboard/DashboardView.vue` 当前只是简单包一层 `OverviewView.vue`，但路由只实际引用 `OverviewView.vue`，说明 dashboard 目录里还存在一层未收口的历史包装壳
- `kaipai-admin/src/types/admin.ts` 的 `AdminMenuItem` 目前没有“hidden / phase / migration”字段，`src/components/layout/AdminSidebar.vue` 也会把 `permissionStore.menus` 全量渲染为主导航；这意味着若要满足 `R15` 的“迁移期治理入口不再出现在当前主菜单”，不能只改文案，必须同步调整菜单模型或菜单来源

### 2.3 后端

- 当前 controller 仍保留大量旧域：
  - `recruit`
  - `company`
  - `membership`
  - `referral`
  - `refund`
  - `payment`
  - `verify`
  - `fortune`
  - `order`
- 与当前“分享主链 + 统计主链”架构不一致
- `kaipaile-server/src/main/java/com/kaipai/module/server/` 当前仍保留：
  - `actor`
  - `adminauth`
  - `ai`
  - `auth`
  - `card`
  - `company`
  - `fortune`
  - `invite`
  - `membership`
  - `order`
  - `payment`
  - `recruit`
  - `referral`
  - `refund`
  - `system`
  - `user`
  - `verify`
  - `wechat`
- `kaipaile-server/src/main/java/com/kaipai/module/model/` 当前也仍按旧业务域保留大量 DTO 目录：
  - `actor / auth / card / company / fortune / level / membership / order / payment / recruit / referral / refund / system / user / verify / ai`
- 其中已有若干关键事实能直接证明“当前产品主线”和“旧域残留”并存：
  - `controller/user/UserController.java` 提供 `/user/me` 与 `/user/role`，属于当前登录态与身份主链
  - `controller/card/CardController.java`、`CardViewHistoryController.java`、`CardContactRequestController.java` 已覆盖分享卡、查看历史、联系方式授权
  - `controller/level/LevelController.java` 仍直接依赖 `server.membership.MembershipAccountService` 产出当前分享等级信息，说明 membership 已不是独立产品中心，但仍是主链支撑依赖
  - `controller/referral/ReferralController.java` 仍直接提供 `/invite|/referral` 的 `code / stats / records / qrcode`，说明邀请域虽然退出独立前台入口，仍在给分享成长门禁供数
  - `controller/fortune/FortuneController.java` 的 `apply-lucky-color` 直接按 `shareCardId` 写当前卡片，说明 fortune 也已降为分享个性化支撑域，而不是独立产品主线
  - `controller/invite/InviteRecordController.java` 当前只有空壳 class，无实际 endpoint，属于明显历史残留

## 3. 当前结论

- 当前仓库不是“缺一个页面”，而是“新架构已部分进入，但旧业务域和旧代码仍大量并存”
- 因此本轮必须先做整体架构重构 Spec，而不能继续零散删页面

## 4. 本轮已落的前端入口收口

- 已先按 `00-69` 的 active 主链要求，收口 `kaipai-frontend/src/pages/mine/index.vue`：
  - 演员侧个人中心从“档案 + 实名 + 已联系 + 我的名片”收口为“个人档案 + 创建分享”
  - 剧组侧旧“剧组资料 / 投递反馈 / 名片能力 / 设置”入口已从当前移动端主链移出
  - 旧 `project / role / apply` 统计口径已从个人中心主展示面移除
- 已同步收口 `kaipai-frontend/src/pages/home/index.vue` 的剧组占位文案：
  - 明确剧组资料、投递反馈与招募管理已退出当前移动端主链
  - 当前首页只服务演员分享卡片 MVP，剧组治理以后台控制台为准
- 已继续收口 `role-select / company-profile` 旧入口：
  - `kaipai-frontend/src/pages/role-select/index.vue` 已改为“历史未完成身份落位账号”的兼容页，不再把自己伪装成当前正式主入口
  - 剧组身份选择后不再跳转 `pages/company-profile/edit`，而是进入当前兼容占位页 `pages/mine/index`
  - `kaipai-frontend/src/pages.json` 已移除 `pages/company-profile/edit` 的 active 路由登记，明确其退出当前移动端主链
- 已继续收口旧招募 / 投递页面的 active 路由：
  - 通过仓内引用核对，`pages/role-detail`、`apply-confirm`、`my-applies`、`apply-detail`、`project/create`、`project/role-create`、`apply-manage` 当前只剩旧页面之间的自引用，不再被首页 / 记录 / 我的 / 登录 / 分享主链调用
  - 因此本轮已把上述 7 个旧页面从 `kaipai-frontend/src/pages.json` 的 active 路由表中移除，先完成“退出当前主链”，文件级删除留待后续批次
- 已继续收口旧分包 / 旧页面残留入口：
  - 通过仓内引用核对，`pages/contacts/index` 已无任何主线页面或 helper 引用，仅剩 `pages.json` 路由登记
  - `pkg-card/membership`、`pkg-card/invite`、`pkg-card/fortune` 当前也只剩旧页面之间的互相跳转，不再被首页 / 记录 / 我的 / 登录 / 档案编辑 / 分享主链直接调用
  - 因此本轮已把 `contacts` 页面与 `membership / invite / fortune` 三个旧分包页从 `kaipai-frontend/src/pages.json` 中移除，明确其退出当前 active 架构；`verify` 仍因 `actor-profile/edit` 的实名认证兼容跳转暂时保留
- 当前前端删除 / 兼容清单已形成：
  - 已退出 active 路由：`company-profile/edit`、`role-detail`、`apply-confirm`、`my-applies`、`apply-detail`、`project/create`、`project/role-create`、`apply-manage`、`contacts`、`pkg-card/membership`、`pkg-card/invite`、`pkg-card/fortune`
  - 兼容保留：`pages/role-select/index`（历史未完成身份落位账号）、`pkg-card/verify/index`（档案编辑中的实名认证兼容入口）
- 已通过 `kaipai-frontend npm run type-check` 与 `npm run build:mp-weixin` 验证本轮改动未引入前端类型错误，且 `pages.json` 路由调整可正常出包

## 5. 本轮已完成后台盘点与收口方案

- 已按 `00-69 T3` 盘点后台菜单、路由与页面域，确认当前后台仍是“旧多业务域并列”：
  - 顶级菜单：`dashboard / verify / referral / recruit / membership / payment / refund / content / system`
  - 路由域：`/dashboard/*`、`/verify/*`、`/referral/*`、`/recruit/*`、`/membership/*`、`/payment/*`、`/refund/*`、`/content/*`、`/system/*`
  - 页面目录：`src/views/dashboard|verify|referral|recruit|membership|payment|refund|content|system`
- 已形成后台收口方案，按 `R11-R15` 分为三类：
  1. **当前 active 主菜单（目标保留）**
     - `控制台 / 渠道分析`：以当前 `/dashboard/index` 为基础，后续承接分享次数、进入次数、渠道来源、回访率、留存/活跃等统计
     - `用户中心`：当前先以 `/content/share-cards`、`/content/contact-requests` 承接分享卡片与联系方式治理；业务用户信息页后续再补，不再把后台账号页混入当前产品用户中心
  2. **迁移期治理入口（需移出主菜单）**
     - `/content/templates`
     - `/content/default-general-card`
     - `/verify/*`
     - `/referral/*`
     - `/system/ai-resume-governance`
     - `/system/admin-users`
     - `/system/roles`
     - `/system/operation-logs`
      这些页面仍可能承担配置、运维、审计或迁移责任，但不应继续作为当前正式业务架构主菜单
  3. **主菜单退场候选**
     - `/recruit/*`
     - `/membership/*`
     - `/payment/*`
     - `/refund/*`
     这些域与当前“分享 + 记录 + 我的 + 渠道分析”主架构不一致，应优先从当前可见主导航退场
- 在完成上述盘点后，已先用独立侧边栏菜单源落第一版收口，而没有直接删除旧路由，避免把仍承担治理责任的页面一并抹掉
- 本轮已直接落第一版后台主菜单收口实现：
  - `kaipai-admin/src/constants/menus.ts` 新增 `adminSidebarMenus`，把当前主线侧边栏收口为两个一级域：`控制台 / 渠道分析`、`用户中心`
  - `kaipai-admin/src/stores/permission.ts` 改为区分 `menus`（全量可见菜单，用于保留治理/迁移入口语义）与 `sidebarMenus`（当前主线侧边栏）
  - `kaipai-admin/src/components/layout/AdminSidebar.vue` 已切到 `sidebarMenus` 渲染，因此旧 `verify / referral / recruit / membership / payment / refund / content / system` 不再继续占据当前侧边栏一级导航
  - 现阶段未移除旧路由，只是把它们从主导航退场，符合 `00-69` 对“迁移期治理入口仍可直达、但不应继续作为正式主菜单”的要求
  - 已通过 `kaipai-admin npm run type-check` 与 `npm run build` 验证该改动可正常通过类型检查与生产构建；当前剩余仅为 Sass legacy API 与 bundle 体积告警，不影响本轮收口结论
- 已按 `00-69 T4` 对后端 controller / service / DTO 域完成首轮分类，结论如下：
  1. **当前 active 主链保留**
     - 控制器 / 接口域：`auth`、`user`、`actor`、`card`、`level`
     - 后台接口域：`admin.auth`、`admin.dashboard`、`admin.content`、`admin.user`
     - 对应服务 / DTO：`server.auth`、`server.user`、`server.actor`、`server.card`、`model.auth`、`model.user`、`model.actor`、`model.card`、`model.level`
  2. **迁移期支撑依赖或治理域**
     - `referral`：当前虽不再是独立前台主入口，但仍为邀请数、邀请码与成长门禁供数
     - `membership`：当前虽不再是独立产品中心，但 `LevelController` 仍依赖其产出等级与能力
     - `verify`：当前仍是档案编辑链里的实名认证兼容入口
     - `fortune`：当前已退为分享个性化/幸运色能力支撑，不再是独立主线
     - `ai`、`wechat`、`system`：仍承担 AI 治理、微信能力、后台角色/日志等治理职责，但不应继续被当成当前产品主架构中心
  3. **删除候选或优先退场域**
     - `company`
     - `recruit`
     - `payment`
     - `refund`
     - `order`
     - `invite` 空壳 controller / service 残留
- 这意味着后端下一步不应继续围绕“多业务域并行扩展”演进，而应先把 `auth / user / actor / card / level + admin.dashboard / admin.content / admin.user` 视为当前主线，其他域按“迁移治理保留”或“删除候选”处理

## 6. 本轮已完成后端盘点与分类方案

- `00-69 T4` 当前已完成首轮事实盘点与分类，现阶段可以稳定回答：
  - 哪些后端域仍是当前分享主链
  - 哪些域只是支撑依赖
  - 哪些域已经属于历史残留或优先退场候选
- 当前仍未直接删后端旧 controller / service / DTO，原因是本轮目标仍是先完成边界划分；真正删除前还需要补调用面核对和迁移顺序

## 7. 本轮已完成分享统计与存活率指标口径固化

- 已核对当前 dashboard 前后端实现，确认现状仍围绕旧治理指标：
  - `kaipai-admin/src/types/dashboard.ts` 当前只有 `verifyPendingCount / referralRiskPendingCount / refundPendingCount / todayPaymentOrderCount`
  - `kaipaile-server/.../AdminDashboardOverviewDTO.java` 也只暴露上述四个计数和 `recentItems`
  - `AdminDashboardServiceImpl.java` 当前 `recentItems` 也只从 `verify / referral / refund / payment` 四条旧业务线取数
- 因此当前后台“工作台”还不是分享分析中台，而是旧审核/支付/退款待办面板；这与 `00-69` 的“控制台 / 渠道分析”目标不一致
- 已据此固化当前阶段正式指标口径，后续 dashboard/analytics 应至少围绕以下指标重建：
  1. **分享行为指标**
     - 用户分享次数
     - 卡片分享次数
     - 海报分享次数
  2. **进入与渠道指标**
     - 通过分享进入次数
     - 卡片来源进入次数
     - 海报来源进入次数
     - 渠道来源分布
  3. **内容偏好指标**
     - `都市 / 古风 / 经典` 三类示例风格的点击次数
     - 不同风格的分享次数与进入次数
  4. **回访与转化指标**
     - 二次回访次数
     - “打开别人分享 -> 创建自己的分享”转化次数
  5. **存活率指标**
     - 次日留存
     - 7 日留存
     - 活跃用户数
- 口径约束也已明确：
  - 指标必须围绕“分享主链 + 小程序存活率”组织，不再继续把 verify/referral/refund/payment 待办数当成 dashboard 主指标
  - 风格维度必须按当前产品文案输出 `都市 / 古风 / 经典`，不能直接把旧技术场景码裸露成 dashboard 主文案
  - 指标应沉到统一 analytics 事实源，而不是继续散落在前端页面内联统计
- 本轮已将 `kaipai-admin/src/views/dashboard/OverviewView.vue` 的页面语义同步收口到该口径：
  - hero、scope、统计卡与模块说明已改成“渠道分析控制台 + 迁移治理快照”
  - 原 `verify / referral / refund / payment` 四类旧指标被明确降级为“迁移治理快照”，不再伪装成正式控制台主指标
  - 新增“目标分享分析指标”占位卡，显式提示分享次数、进入次数、渠道来源、回访/转化、留存/活跃仍待统一 analytics 事实源接入
  - 最近事项表也已改写为“迁移治理最近事项”，避免继续把旧治理业务线当成当前产品控制台主叙事
- 已通过 `kaipai-admin npm run type-check` 与 `npm run build` 验证 `OverviewView` 本轮收口未引入类型或构建错误；当前剩余仅为 Sass legacy API 与 bundle 体积告警，不影响本轮结论
- 本轮又继续把控制台数据结构往真实分享主链推进一刀：
  - `AdminDashboardOverviewDTO` / `DashboardOverview` 已新增分享主链可直接统计的字段：
    - `activeShareCardCount`
    - `activeShareOwnerCount`
    - `shareViewCount`
    - `uniqueViewerCount`
    - `approvedContactRequestCount`
    - `pendingContactRequestCount`
    - `convertedViewerCount`
    - `classic / urban / costume` 三类风格进入次数
  - `AdminDashboardServiceImpl` 已开始从 `user_share_card`、`share_card_view_history`、`share_card_contact_request` 三张真实分享链表取数，而不再只认旧 `verify / referral / refund / payment`
  - `OverviewView.vue` 的“目标分享分析指标”里已有一批口径开始显示真实数据：
    - 当前活跃分享卡
    - 分享进入记录
    - 查看后成卡
    - 已同意联系方式
    - 风格进入偏好
  - 这说明当前控制台虽然还不是完整 analytics 中台，但已经从“纯目标占位”推进到“旧迁移治理快照 + 新分享链真实信号并存”的过渡状态
- 已继续通过 `kaipai-admin npm run type-check`、`npm run build` 与 `kaipaile-server mvn -q -DskipTests compile` 验证本轮前后台联动改动可通过构建

## 8. 索引、映射与 00-28 治理回填状态

- 已确认 `00-69` 的索引与治理回填已落到仓内统一入口：
  - `.sce/specs/README.md` 已登记 `00-69 current-phase-share-analytics-architecture-refactor`
  - `.sce/specs/spec-code-mapping.md` 已登记 `00-69` 的 `requirements / design / tasks / execution`
  - `.sce/specs/00-28-architecture-driven-delivery-governance/tasks.md` 已有 `T13-AS` 回填
  - `.sce/specs/00-28-architecture-driven-delivery-governance/status/overall-architecture-assessment.md` 已将 `00-69` 提升为当前代码层上位重构线
- 因此 `00-69 T6` 当前可以判定为已满足，不再缺“Spec 已建但未挂入治理总览”的问题

## 9. 下一步

- 后续按本 Spec 分阶段推进：
  1. 先收入口与 active 菜单
  2. 再合并旧页面职责
  3. 再清理旧后端域
  4. 最后删除无 active 引用的旧代码
