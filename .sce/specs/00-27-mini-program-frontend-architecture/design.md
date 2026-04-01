# 小程序前端架构总览 - 技术设计

_Requirements: 00-27 全部_

## 1. 设计目标

00-27 解决的不是某一个页面，而是当前小程序前端的整体系统骨架和信息架构。

本 Spec 主要回答六类问题：

1. `kaipai-frontend` 在整个项目中的系统位置是什么
2. 当前小程序有哪些页面分组、页面类型和主线入口
3. 页面、组件、Store、API、类型、utils 分别负责什么
4. 当前名片主线如何在前端中落位
5. 新页面、新模块进入前该如何做放置与抽象决策
6. 后续前端重构时应优先更新哪些文档和边界

## 2. 总体形态

```text
kaipai-frontend
  -> 主包 pages/**
  -> 演员增强分包 pkg-card/**
  -> 工具分包 pkg-tools/**
  -> src/components/Kp*.vue
  -> src/api/*.ts
  -> src/stores/*.ts
  -> src/types/*.ts
  -> src/utils/*.ts
  -> src/styles/*
```

### 2.1 系统定位

- 小程序前端工程：`kaipai-frontend`
- 平台后台前端工程：`kaipai-admin`
- 后端服务工程：`kaipaile-server`

明确结论：

- 小程序前端和后台前端是两个不同的前端系统
- 小程序前端只服务演员端和分享链路
- 后台审核、配置、运营、订单和退款不回流到小程序端

### 2.2 当前前端主线

```text
演员基础链路
  -> 首页 / 角色详情 / 投递 / 我的 / 档案

演员增强主线
  -> 名片预览
  -> 会员能力中心
  -> 实名认证
  -> 邀请裂变
  -> 命理个性化

分享链路
  -> 小程序分享卡片
  -> 海报
  -> 公开名片页
  -> 邀请卡片
```

## 3. 页面与路由信息架构

### 3.1 当前页面分组

| 分组 | 路径前缀 | 定位 | 当前页面 |
|------|----------|------|----------|
| 主包 | `pages/` | 启动即达页、tab 页、基础链路页 | login, role-select, home, role-detail, apply-confirm, my-applies, apply-detail, actor-profile/edit, mine, project/create, project/role-create, apply-manage, actor-profile/detail, company-profile/edit |
| 演员增强分包 | `pkg-card/` | 持续增长的名片增强主线 | actor-card, membership, verify, invite, fortune |
| 工具分包 | `pkg-tools/` | 低频工具能力 | webview, video-player |

### 3.2 当前页面信息架构

#### 主包 `pages/`

按职责分为：

- 认证与角色入口：
  - `pages/login/index`
  - `pages/role-select/index`
- 基础演员链路：
  - `pages/home/index`
  - `pages/role-detail/index`
  - `pages/apply-confirm/index`
  - `pages/my-applies/index`
  - `pages/apply-detail/index`
- 档案与个人中心：
  - `pages/actor-profile/edit`
  - `pages/mine/index`
  - `pages/actor-profile/detail`
- 历史保留的剧组页：
  - `pages/project/create`
  - `pages/project/role-create`
  - `pages/apply-manage/index`
  - `pages/company-profile/edit`

说明：

- 剧组页当前保留在代码中，但产品主线已迁往平台后台
- 小程序主包仍需保留这些页面的历史兼容结构，直到明确下线

#### 演员增强分包 `pkg-card/`

当前页面：

- `pkg-card/actor-card/index`
- `pkg-card/membership/index`
- `pkg-card/verify/index`
- `pkg-card/invite/index`
- `pkg-card/fortune/index`

职责：

- 承接当前演员增强主线
- 承接持续增长的分享、会员、个性化和邀请能力
- 与主包基础链路解耦，降低主包膨胀风险

#### 工具分包 `pkg-tools/`

当前页面：

- `pkg-tools/webview/index`
- `pkg-tools/video-player/index`

职责：

- 承接工具型、低频、可独立加载能力
- 与名片增强主线解耦

### 3.3 页面类型设计

页面顶部与骨架继续服从 `SHARED_CONVENTIONS.md`，分为三类：

| 类型 | 特征 | 典型页面 | 架构要求 |
|------|------|----------|----------|
| A. 深色 Hero 页 | 深色头图 + 白卡叠层 + 悬浮返回 | role-detail, apply-confirm, actor-card, membership | 使用共享 Hero / 返回按钮壳层 |
| B. 普通顶部页 | 自定义顶部 + 表单/列表内容区 | actor-profile/edit, verify, invite, fortune | 复用普通顶部策略 |
| C. Tab 根页 | 启动即达或 tab 容器页 | home, mine, login | 不引入多余页面级返回壳层 |

### 3.4 页面放置决策矩阵

| 问题 | 是 | 否 |
|------|----|----|
| 是否为 tab 页或启动即达页 | 留在 `pages/` | 继续判断 |
| 是否为演员增强主线的一部分 | 进入 `pkg-card/` | 继续判断 |
| 是否为工具型独立页面 | 进入 `pkg-tools/` | 继续判断 |
| 是否具备独立入口且会持续增长 | 优先进入分包 | 谨慎评估是否留主包 |

## 4. 前端模块分层设计

### 4.1 推荐分层

| 层级 | 路径 | 职责 |
|------|------|------|
| 页面层 | `pages/**`, `pkg-card/**`, `pkg-tools/**` | 视图组装、生命周期、路由跳转、页面级交互 |
| 共享 UI 层 | `src/components/Kp*.vue` | 复用视觉壳层和交互组件 |
| 状态层 | `src/stores/*.ts` | 承接跨页面共享状态 |
| API 层 | `src/api/*.ts` | 承接后端接口调用 |
| 类型层 | `src/types/*.ts` | 承接共享领域类型 |
| 解析/工具层 | `src/utils/*.ts` | 承接跨页面业务解析、格式化、校验 |
| 样式层 | `src/styles/*` | 承接 token、mixin、页面骨架 |

### 4.2 分层职责说明

#### 页面层

只负责：

- 页面模板结构
- 页面生命周期
- 页面内交互编排
- 调用 API / Store / utils

不负责：

- 复制共享 UI 壳层
- 重复拼装复杂读模型
- 重复定义共享类型

#### 共享 UI 层

优先承接：

- 按钮
- 卡片壳层
- 顶部返回壳层
- 固定底部操作栏
- 主题预览卡
- 能力矩阵卡
- 邀请摘要卡
- 等级进度卡

#### 状态层

当前以用户 Store 为主中心，继续承接：

- 登录态
- 用户角色态
- 实名状态
- 等级与邀请统计
- 会员态

#### API 层

按业务域拆分，而不是按页面零散扩散。当前核心业务域包括：

- `auth`
- `actor`
- `level`
- `invite`
- `verify`
- `fortune`
- `personalization`

#### 类型层

当前类型层继续承接：

- 用户与档案
- 邀请与等级
- 认证
- 命理
- 个性化与分享产物

#### 解析/工具层

当前主线重点在以下解析器：

- `personalization`
- `theme-resolver`
- `share-artifact`

## 5. 数据流与状态流

### 5.1 基础页面数据流

```text
页面
  -> 调用 api
  -> 调用 store 同步共享状态
  -> 渲染页面与 Kp 组件
```

适用于：

- 登录
- 首页基础数据
- 我的页基础数据
- 基础资料编辑页

### 5.2 当前名片主线数据流

```text
页面进入
  -> user store 同步角色 / 实名 / 等级 / 会员 / 邀请信息
  -> api 拉取业务数据
  -> utils/personalization 聚合个性化输入
  -> utils/theme-resolver 解析主题 token
  -> utils/share-artifact 解析分享产物
  -> 页面消费统一结果
  -> Kp 组件负责视觉承载
```

### 5.3 状态流原则

- 短期一次性页面状态：留在页面内
- 跨页面共享且可复用状态：进入 Store
- 组合型读模型：进入 utils 聚合
- 接口源数据：留在 API 层和类型层

## 6. 共享组件与样式架构

### 6.1 共享组件原则

共享组件抽取判断：

1. 是否跨页面复用
2. 是否会继续扩散
3. 是否属于统一视觉壳层
4. 是否会影响小程序 UI 一致性

若答案大于等于 2 个“是”，优先抽为 `Kp` 组件。

### 6.2 当前样式体系

当前样式体系由三层构成：

1. Token：`_tokens.scss`
2. Mixin：`_mixins.scss`
3. 壳层：`_page-layout.scss`

当前关键共享壳层包括：

- Hero 锚点
- 悬浮返回按钮
- 固定底部操作栏
- 页面内容区骨架

### 6.3 当前 UI 约束

- 页面优先复用共享壳层
- 间距节奏优先复用 token
- 顶部安全区与胶囊对齐按共享规范处理
- 不允许页面为了局部效果脱离公共规则重写一套顶部或底栏体系

## 7. 当前业务主线映射

### 7.1 名片分享主线

主页面：

- `pkg-card/actor-card/index`
- `pages/actor-profile/detail`

职责：

- 名片预览
- 分享主题展示
- 分享路径装配
- 公开页落地恢复

### 7.2 会员能力中心

主页面：

- `pkg-card/membership/index`

职责：

- 解释等级能力与会员能力边界
- 展示当前已解锁能力
- 承接会员与邀请能力说明

### 7.3 实名认证

主页面：

- `pkg-card/verify/index`

职责：

- 前端认证提交
- 认证状态展示
- 与邀请、等级前置条件联动

### 7.4 邀请裂变

主页面：

- `pkg-card/invite/index`

职责：

- 邀请摘要
- 邀请记录入口
- 邀请分享产物视角

### 7.5 命理个性化

主页面：

- `pkg-card/fortune/index`

职责：

- 命理结果说明
- 作为个性化输入源解释页
- 关联名片与分享产物，不再作为孤立功能页

## 8. 分包与包体治理设计

### 8.1 当前约束

- 主包不超过 2 MB
- 新增功能默认先评估分包
- `pkg-card` 与 `pkg-tools` 各自保持清晰职责

### 8.2 当前开发默认顺序

新增功能时优先判断：

1. 是否属于主包必经链路
2. 是否属于演员增强主线
3. 是否属于工具型页面
4. 是否会带来体积持续增长

### 8.3 当前风险控制

禁止：

- 直接把所有新功能放回主包
- 在 `pkg-card` 中混放无关工具页
- 为了快速实现复制大段页面内 UI 代码

## 9. 文档与治理关系

### 9.1 与基础 Spec 的关系

| Spec | 作用 |
|------|------|
| 00-01 | 样式系统 |
| 00-02 | 共享组件体系 |
| 00-03 | API / types / utils / stores 基础分层 |
| 00-05 | 包体与分包治理 |
| 00-08 | 样式治理 |
| 00-09 | 样式壳层抽离 |

### 9.2 与业务 Spec 的关系

| Spec | 作用 |
|------|------|
| 05-05 | 名片分享与等级/会员基础能力 |
| 05-08 | 命理个性化 |
| 05-09 | 实名认证 |
| 05-10 | 邀请裂变 |
| 05-11 | 当前主线架构治理基线 |

### 9.3 更新优先级

若发生以下变化，必须优先更新 00-27：

- 页面重新分组
- 分包策略变化
- 新增新的全局共享层
- 主线整体定位变化
- 当前前端系统边界变化

## 10. 验证方式

本 Spec 为架构文档，主要通过一致性验证验收：

1. 当前仓库页面分组与 00-27 描述一致
2. 新增页面时能用 00-27 判断放置位置
3. 当前主线与 05-11 的关系清晰
4. 当前前端总纲与 `.sce/specs/README.md`、`CURRENT_CONTEXT.md` 能互相追溯
