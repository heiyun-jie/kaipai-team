# 00-68 设计说明

## 1. 设计目标

把当前线上两个问题一次性收口：

1. 分享链以 `shareCardId` 为入口时，不再因为独立 `actor_profile` 缺失而中途断裂
2. 分享海报的能力规则、后端返回、前端按钮和用户文案全部统一

## 2. 设计原则

- 分享链以卡片实例为主，不以页面各自补跳接口为主
- 后端先修事实源，再让前端收口消费
- 能力口径先由后端统一，再让前端按结果展示
- 治理动作显式化，不继续依赖运行时偶然回填

## 3. 分享链整改策略

### 3.1 现状问题

当前 `share-card-latest` 主链仍是：

```text
shareCardId
  -> /api/card/personalization
  -> actorId
  -> /api/actor/{actorId}
```

这意味着：

- 只要第二跳缺 `actor_profile`
- 整个公开页和编辑页就会一起炸

### 3.2 本轮目标结构

建议把分享公开链收口为：

```text
shareCardId
  -> /api/card/personalization
      -> profile
      -> customConfig
      -> theme
      -> actorSnapshot(minimal)
```

即：

- 公开分享链所需的最小演员资料直接由个性化聚合接口一并返回
- 前端分享页不再以 `/api/actor/{id}` 作为分享主链硬依赖

### 3.3 fallback 原则

若历史用户尚未补齐独立 `actor_profile`：

- 分享链仍应能基于 `user`、`shareCard`、已保存配置等信息返回最小 `actorSnapshot`
- 后台治理页或修复动作再负责后续数据补齐

不允许：

- 运行时直接 `500`
- 前端静默兜底假数据

## 4. 分享海报能力整改策略

### 4.1 当前阶段产品口径

本轮按用户最新要求固定为：

```text
只要用户可使用当前分享卡主链，就可使用“分享海报”
```

因此本轮设计要求：

- `canUseCustomPoster = true`
- `poster artifact.locked = false`
- `lockReason = null`

### 4.2 前端展示规则

所有分享海报入口统一遵循：

- 能力开放：正常显示并可点击
- 能力关闭：不显示或禁用态显式说明

不得继续使用：

- 按钮先显示
- 点击后才 toast “会员海报能力”

### 4.3 影响入口

- `pages/home/index.vue`
- `pkg-card/card-list/index.vue`
- `pkg-card/actor-card/index.vue`
- 与 capability 说明、会员页、分享产物说明相关的共享文案 helper

## 5. 治理与证据

### 5.1 后台治理

需要具备至少一种可复用治理方式：

- 列出“分享卡存在但公开 actor snapshot 缺失风险”的记录
- 支持补偿或修复

### 5.2 证据要求

整改完成后需要补：

1. 有问题 shareCard 的修复前后接口样本
2. 前端三处按钮展示样本
3. 后端 capability / artifact 返回样本
4. 公开页 / 编辑页读取分享链不再二跳失败的样本

## 6. 影响文件

- `D:\XM\kaipai-team\kaipaile-server\src\main\java\com\kaipai\module\server\card\service\impl\ActorPersonalizationServiceImpl.java`
- `D:\XM\kaipai-team\kaipaile-server\src\main\java\com\kaipai\module\server\actor\service\impl\ActorProfileServiceImpl.java`
- `D:\XM\kaipai-team\kaipai-frontend\src\utils\share-card-latest.ts`
- `D:\XM\kaipai-team\kaipai-frontend\src\pages\actor-profile\detail.vue`
- `D:\XM\kaipai-team\kaipai-frontend\src\pkg-card\actor-card\index.vue`
- `D:\XM\kaipai-team\kaipai-frontend\src\pkg-card\card-list\index.vue`
- `D:\XM\kaipai-team\kaipai-frontend\src\pages\home\index.vue`
- `D:\XM\kaipai-team\kaipai-frontend\src\utils\share-artifact.ts`
- `D:\XM\kaipai-team\.sce\specs\00-28-architecture-driven-delivery-governance\status\share-card-mvp-status.md`
- `D:\XM\kaipai-team\.sce\specs\00-28-architecture-driven-delivery-governance\status\overall-architecture-assessment.md`

## 7. 本轮不扩大设计

- 不在本轮引入新的分享产物
- 不把整个档案服务重写成全新模型
- 不做会员体系整体重算
