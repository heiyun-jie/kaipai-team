# 00-69 设计说明

## 1. 设计目标

把当前工程从“新分享主线 + 旧演员招募 / 会员 / 邀请 / 后台多业务域并存”的混合态，收口成“分享 + 记录 + 我的 + 渠道分析”的单一当前架构。

## 2. 设计原则

- 先定义 active 架构，再处理旧代码删除
- 先收口可见入口，再收口目录与接口
- 旧代码只有两种去向：删除，或降级为迁移期治理工具
- 数据统计是正式架构能力，不是页面附属脚本

## 3. 目标架构

### 3.1 前端

#### 3.1.1 active 页面

主包 / 分包收口后，前端当前阶段只保留：

- 登录 / 注册页
- 首页
- 记录页
- 个人中心页
- 档案编辑页
- 创建 / 编辑分享页
- 分享详情页

#### 3.1.2 首页职责

首页当前只负责：

- 展示 3 个示例风格：
  - 都市
  - 古风
  - 经典
- 展示 1 个操作视频
- 进入分享创建 / 编辑
- 触发卡片 / 海报分享

首页不再承担：

- 旧演员列表
- 旧角色列表
- 旧剧组 / 招募链路入口

#### 3.1.3 记录页职责

记录页只负责：

- 展示我打开过的卡片 / 海报
- 允许再次进入该分享页面

#### 3.1.4 个人中心职责

个人中心只负责：

- 档案资料
- 创建分享
- 退出登录

### 3.2 后台

#### 3.2.1 active 菜单

后台当前阶段只保留两个一级域：

1. 控制台 / 渠道分析
2. 用户中心

#### 3.2.2 控制台内容

围绕分享和回流统计组织：

- 分享次数
- 分享进入次数
- 卡片 / 海报渠道来源
- 回访率
- 留存 / 活跃指标

#### 3.2.3 用户中心内容

围绕人和分享卡片组织：

- 用户信息
- 用户已创建分享卡片
- 用户分享摘要

### 3.3 后端

#### 3.3.1 active 主链

后端当前阶段只围绕以下域收口：

- auth
- actor profile
- share card
- view history
- analytics / control
- admin user center

#### 3.3.2 统计主链

新增统一统计域，服务于：

- 分享统计
- 进入统计
- 回访统计
- 留存统计
- 风格偏好统计
- 内容转化统计

## 4. 旧代码收口策略

### 4.1 前端

#### 4.1.1 直接删除候选

优先纳入删除候选：

- 招募 / 投递相关旧页面
- `credit-*` 历史页面
- 剧组资料编辑页
- 旧角色选择页

#### 4.1.2 兼容收口候选

优先纳入“合并后删除”候选：

- `pkg-card/membership`
- `pkg-card/invite`
- `pkg-card/fortune`
- `pkg-card/verify`

这些页面要么并入“我的”，要么并入新的分享编辑或分析链路，最终不再作为独立 active 产品页存在。

### 4.2 后台

旧后台多业务域菜单全部纳入重构名单：

- verify
- referral
- recruit
- membership
- payment
- refund
- system
- content 多页拆散结构

重构目标不是继续并列保留，而是：

- 当前有价值的统计 / 用户 / 分享治理能力迁入新的控制台与用户中心
- 与当前架构无关的页面退场或降级

### 4.3 后端

旧控制器 / 服务域分类为三类：

1. 当前 active 保留
2. 迁移期治理保留
3. 删除候选

## 5. 执行顺序

### 阶段 1：入口收口

- 前端 tab / pages / router helper 收口
- 后台菜单 / router 收口

### 阶段 2：页面与模块合并

- 把独立功能页合并到当前 active 页面
- 删除旧入口

### 阶段 3：后端接口域收口

- 收口分享主链与分析主链
- 清理旧 controller / DTO / service

### 阶段 4：旧代码删除

- 删除已无 active 引用和兼容责任的旧页面、旧菜单、旧接口域

## 6. 风险控制

- 删除前必须先确认无 active 路由、无页面引用、无脚本依赖
- 后台旧菜单即使先下线，也要明确是否还承担治理责任
- 后端旧接口删除前必须先确认前端与后台调用面已全部切换

## 7. 影响文件（首轮）

### 前端

- `D:\XM\kaipai-team\kaipai-frontend\src\pages.json`
- `D:\XM\kaipai-team\kaipai-frontend\src\pages\home\index.vue`
- `D:\XM\kaipai-team\kaipai-frontend\src\pages\history\index.vue`
- `D:\XM\kaipai-team\kaipai-frontend\src\pages\mine\index.vue`
- `D:\XM\kaipai-team\kaipai-frontend\src\pkg-card\card-list\index.vue`
- `D:\XM\kaipai-team\kaipai-frontend\src\pkg-card\membership\index.vue`
- `D:\XM\kaipai-team\kaipai-frontend\src\pkg-card\invite\index.vue`
- `D:\XM\kaipai-team\kaipai-frontend\src\pkg-card\fortune\index.vue`

### 后台

- `D:\XM\kaipai-team\kaipai-admin\src\constants\menus.ts`
- `D:\XM\kaipai-team\kaipai-admin\src\router\index.ts`
- `D:\XM\kaipai-team\kaipai-admin\src\views\dashboard\*`
- `D:\XM\kaipai-team\kaipai-admin\src\views\content\ShareCardsView.vue`
- 用户与分享治理相关页面

### 后端

- `D:\XM\kaipai-team\kaipaile-server\src\main\java\com\kaipai\module\controller\actor`
- `D:\XM\kaipai-team\kaipaile-server\src\main\java\com\kaipai\module\controller\card`
- `D:\XM\kaipai-team\kaipaile-server\src\main\java\com\kaipai\module\controller\auth`
- 旧 `recruit / referral / membership / fortune / payment / refund / verify / company / order` 域

## 8. 本轮不直接实现

- 本 Spec 只先完成架构收口和删除边界设计
- 真正删代码时必须再按本 Spec 分阶段执行
