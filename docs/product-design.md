# 「开拍了」当前产品设计文档

> 版本：v1.4 | 更新日期：2026-04-01
> 当前主线：演员名片分享 + 命理驱动个性化 + 会员能力分层 + 统一分享产物
> 历史版本归档：`docs/archive/product-design-v1.2-2026-03-23.md`

## 一、文档定位

本文档只描述当前分支的现行产品模型、当前主线页面和当前验收重点。

以下内容不再作为当前实现依据：

- 信用积分主页、积分记录、排行榜
- `KpCreditBadge`、`KpLevelTag`
- “我的信用分”入口
- basic / pro 二元会员旧方案
- 把命理、邀请、海报视为孤立页面功能的旧方案

如果需要查看历史方案，请进入归档文档或历史 Spec，不要把旧方案与当前主线混写。

## 二、产品定位

「开拍了」当前的小程序端仍然是演员侧工具，但产品主线已经从“信用证明”切换为“名片对外分享”。

当前产品模型围绕以下事实组织：

1. 演员维护档案，并以档案为基础生成可分享名片
2. 分享链路不只包含名片页，还包括小程序分享卡片、海报、公开名片页、邀请卡片
3. 邀请驱动等级体系承担成长节奏
4. 会员体系承担高级定制和商业化能力
5. 命理结果不再是孤立功能，而是个性化输入源，用于驱动主题、文案气质和分享产物风格

平台统一发布通告、演员浏览和投递的链路仍然保留，但它不再是当前迭代的视觉和功能中心。

## 三、当前范围与非范围

### 3.1 当前范围

- 演员档案编辑与档案增强：`pages/actor-profile/edit`
- 名片主预览页：`pkg-card/actor-card/index`
- 公开分享落地页：`pages/actor-profile/detail`
- 名片能力中心：`pkg-card/membership/index`
- 实名认证：`pkg-card/verify/index`
- 邀请裂变：`pkg-card/invite/index`
- 命理个性化说明与应用：`pkg-card/fortune/index`
- “我的”页入口收口：`pages/mine/index`
- AI 润色能力模型
- 小程序分享卡、海报、公开页、邀请卡片

### 3.2 当前不在范围

- 信用积分体系
- 排行榜体系
- 真实会员支付、扣费、订单闭环
- 真实 AI 后端对话接口
- 剧组端小程序功能扩展

## 四、当前用户与角色

### 4.1 小程序用户

- 演员：完善档案、浏览通告、投递、管理名片、完成认证、邀请好友、查看个性化主题

### 4.2 非小程序当前主线角色

- 平台运营：通过管理后台维护审核、模板、会员、邀请规则和数据
- 剧组端：当前仅保留历史兼容代码，不作为小程序主线继续扩展

## 五、当前页面信息架构

### 5.1 主包页面

公共页：

- `pages/login/index`
- `pages/role-select/index`

基础演员链路：

- `pages/home/index`
- `pages/role-detail/index`
- `pages/apply-confirm/index`
- `pages/my-applies/index`
- `pages/apply-detail/index`

档案与个人中心：

- `pages/mine/index`
- `pages/actor-profile/edit`
- `pages/actor-profile/detail`

历史兼容页：

- `pages/project/create`
- `pages/project/role-create`
- `pages/apply-manage/index`
- `pages/company-profile/edit`

### 5.2 分包页面

演员增强主线分包 `pkg-card`：

- `pkg-card/actor-card/index`
- `pkg-card/membership/index`
- `pkg-card/verify/index`
- `pkg-card/invite/index`
- `pkg-card/fortune/index`

工具分包 `pkg-tools`：

- `pkg-tools/webview/index`
- `pkg-tools/video-player/index`

### 5.3 TabBar

当前底部 Tab 只有两个：

- 首页
- 我的

当前主线中不存在排行榜 Tab。

## 六、当前核心链路

### 6.1 名片主链路

```text
登录 / 进入小程序
  → 完善演员档案
  → 完成实名认证
  → 预览个人名片
  → 选择主题与分享产物
  → 生成小程序分享卡 / 海报 / 公开页
  → 好友打开分享内容
  → 进入公开名片页查看完整档案
```

### 6.2 邀请成长链路

```text
演员完成实名认证
  → 生成邀请码
  → 分享邀请卡片 / 邀请海报 / 邀请链接
  → 新用户注册并完善档案
  → 邀请生效
  → 驱动等级成长和能力解锁
```

### 6.3 演员业务辅助链路

```text
首页浏览通告
  → 角色详情
  → 投递确认
  → 我的投递查看状态
```

## 七、当前名片分享主线

### 7.1 名片页 `pkg-card/actor-card/index`

当前名片页承接以下能力：

- 本人预览态与分享访客态切换
- 当前主题摘要与主题预览
- 分享产物切换
- 会员能力 gating
- 分享路径统一装配
- 公开详情页回跳

### 7.2 分享产物

当前统一治理的分享产物包括：

- 小程序分享卡片
- 海报
- 公开名片页
- 邀请卡片

### 7.3 分享参数

统一分享参数不再只围绕模板切换，而要覆盖：

```text
actorId / scene / shared / artifact / themeId / tone
```

分享进入后，页面必须根据参数和后端配置恢复当前展示场景，但最终主题以服务端配置与 resolver 输出为准。

### 7.4 公开详情页 `pages/actor-profile/detail`

公开详情页当前用于承接分享访问，展示：

- 自我介绍
- 拍摄经历
- 照片墙
- 视频简历
- 分享主题相关视觉
- 回跳名片入口

## 八、等级、会员与个性化

### 8.1 等级体系

当前等级体系承担成长节奏，包括：

- 解锁能力节奏
- 邀请人数驱动成长
- AI 配额增长

### 8.2 会员体系

当前会员体系承担高级定制能力，包括：

- 命理驱动主题
- 定制分享卡片
- 定制海报
- 定制邀请卡片

### 8.3 命理个性化

命理结果当前不是独立终点功能，而是用于驱动：

- 主题风格
- 视觉气质
- 分享卡片文案气质
- 海报与邀请链路风格

`pkg-card/fortune/index` 当前负责解释命理结果如何进入名片主线，而不是单独维护另一套产品闭环。

## 九、当前能力页面

### 9.1 名片能力中心 `pkg-card/membership/index`

当前页面用于：

- 解释等级能力与会员能力的区别
- 展示当前可见分享产物
- 展示实名认证、邀请成长、AI 配额等关联能力
- 统一承接邀请动作与能力说明

### 9.2 实名认证 `pkg-card/verify/index`

当前页面用于：

- 提交实名认证
- 展示审核状态
- 作为邀请和成长链路的前置条件

### 9.3 邀请裂变 `pkg-card/invite/index`

当前页面用于：

- 展示邀请摘要
- 展示邀请记录
- 预览邀请主题与邀请产物
- 统一邀请链路与名片主题

## 十、AI 能力边界

### 10.1 当前已接入

当前主线已接入 AI 能力模型，但仍以“前端结构和配额展示”为主，主要用于：

- 名片相关文案气质说明
- 个性化主模型中的 AI 能力挂点
- 会员能力中心中的配额展示

### 10.2 后续待接

`05-04 ai-resume-polish` 负责“全档案对话式 AI 润色”，当前仅有 Spec，尚未进入完整实现。

真实 AI 调用仍需由后端统一封装，前端不直接调用模型。

## 十一、当前验收重点

当前验收重点不再是信用体系，而是：

1. 名片页是否正确进入统一主题和分享产物体系
2. 命理结果是否正确作为个性化输入源进入主线
3. 基础版和会员版能力是否正确区分
4. 邀请链路是否正确并入统一分享主题
5. “我的”页是否只保留当前主线相关入口
6. 公开详情页是否能承接分享访问并恢复当前主题
7. 前端页面放置、分包、共享组件是否继续符合 `00-27` 和 `05-11`

## 十二、当前文档依据

当前以以下文档为准：

- `.sce/specs/00-27-mini-program-frontend-architecture/*`
- `.sce/specs/05-11-fortune-driven-share-personalization/*`
- `.sce/specs/05-05-card-share-membership/*`
- `.sce/specs/05-08-fortune-personalization/*`
- `.sce/specs/05-09-identity-verification/*`
- `.sce/specs/05-10-invite-referral/*`
- `.sce/specs/05-04-ai-resume-polish/requirements.md`
- `.sce/steering/CURRENT_CONTEXT.md`
- `.sce/specs/spec-code-mapping.md`

## 十三、历史归档说明

以下内容已转为历史参考：

- 旧版综合产品设计文档：
  `docs/archive/product-design-v1.2-2026-03-23.md`
- `05-03 credit-score` 历史方案：
  `.sce/specs/05-03-credit-score/*`
- `05-01 actor-card` 早期名片方案：
  `.sce/specs/05-01-actor-card/*`

历史资料允许保留，但不得作为当前分支实现依据。
