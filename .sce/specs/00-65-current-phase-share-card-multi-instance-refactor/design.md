# 00-65 设计说明

## 1. 设计原则

- 模板是资格，不是卡片实例
- 卡片实例必须有自己独立主键、独立配置、独立分享路径
- 所有读取链继续 `shareCardId-first`
- 不为兼容旧“一风格一张卡”语义而牺牲新增语义正确性

## 2. 当前问题拆解

### 2.1 现状

当前后端 `createCard(...)` 逻辑：

```text
sceneKey
  -> 校验模板可用
  -> 校验邀请解锁
  -> ensureOwnedCard(userId, sceneKey, ...)
  -> 若同风格已有卡，则直接复用
```

所以“新增分享卡片”本质不是 create，而是 ensure。

### 2.2 结构性问题

这种设计把两件事混在了一起：

1. 该用户是否有资格创建某风格卡
2. 该用户是否已经拥有某张该风格卡

在当前产品意图下，这两件事必须拆开。

## 3. 目标模型

### 3.1 模板资格层

用于回答：

- 用户是否已解锁某模板
- 用户还能否创建该模板卡片
- 模板本身当前是否启用

该层不再直接映射为 `UserShareCard` 唯一实例。

### 3.2 卡片实例层

`UserShareCard` 表示真实卡片实例，至少包含：

- `shareCardId`
- `userId`
- `templateId`
- `sceneKey`
- `defaultCard`
- `shareStatus`
- `latestConfigId`
- 时间字段

允许：

- 同一用户
- 同一 `templateId / sceneKey`
- 多条 active card 实例并存

## 4. 创建流程重构

### 4.1 新流程

```text
用户点击新增分享卡片
  -> 选择模板
  -> 校验该模板是否启用
  -> 校验该用户是否已解锁该模板
  -> 直接 insert 新 UserShareCard
  -> 为该实例绑定默认配置 / latestConfig
  -> 返回新 shareCardId
  -> 跳转该实例编辑页
```

### 4.2 删除旧流程假设

必须删除以下旧假设：

- 同用户同风格只允许一张卡
- `findOwnedCard(userId, sceneKey)` 可作为新增前置主查询
- `ensureOwnedCard(...)` 可继续承担 create 语义

## 5. 前端设计影响

### 5.1 列表页

当前 `card-list/index` 需要从“风格卡列表”推进为“卡片实例列表”：

- 同一模板可出现多张卡
- 每张卡要有实例级标识信息
- 列表操作作用于实例，不作用于风格

### 5.2 新增入口

新增分享卡片流程：

- 先选模板
- 再执行实例创建
- 再跳转该实例编辑页

### 5.3 编辑与公开页

编辑页、公开页、历史记录、联系方式授权：

- 均不需要退回 `sceneKey`
- 继续以 `shareCardId` 作为实例主键

## 6. 后台设计影响

后台分享卡治理要补两层视角：

1. 模板资格视角
   - 哪些模板已解锁
   - 模板解锁策略
2. 卡片实例视角
   - 同一模板下用户实际创建了多少张卡
   - 哪一张是默认卡
   - 每张卡当前配置 / 状态 / 最近分享使用情况

## 7. 迁移与兼容策略

### 7.1 旧数据

旧模型下每风格只有一张卡，因此旧数据天然可兼容为“已有第一张实例”。

### 7.2 迁移原则

- 旧卡不删
- 旧默认普通卡继续保留
- 从新版本开始，新建动作直接创建新实例

### 7.3 不建议继续保留的兼容方式

- 不建议继续让 `createCard()` 在后台偷偷复用旧卡
- 不建议前端通过“如果已有同风格卡就直接跳编辑”伪装为新增

## 8. 非目标

以下问题不在本 Spec 中处理：

- 编辑页里旧会员 / 命理 / audience selector 的 UI 清理
- 代表照片 / 高亮经历 / 配色编辑器细节
- 预览公开名片按钮

这些应由编辑页边界 Spec 单独处理。

## 9. 影响文件

- `kaipaile-server/src/main/java/com/kaipai/module/server/card/service/impl/UserShareCardServiceImpl.java`
- `kaipaile-server/src/main/java/com/kaipai/module/server/card/service/UserShareCardService.java`
- `kaipaile-server/src/main/java/com/kaipai/module/controller/card/CardController.java`
- `kaipaile-server/src/main/java/com/kaipai/module/model/card/entity/UserShareCard.java`
- `kaipai-frontend/src/pkg-card/card-list/index.vue`
- `kaipai-frontend/src/pages/home/index.vue`
- `kaipai-frontend/src/utils/share-card-mvp.ts`
- 后台分享卡治理页与相关 DTO

## 10. 验证思路

### 10.1 创建验证

- 同一用户在同一模板下连续新增两次
- 应得到两个不同 `shareCardId`

### 10.2 列表验证

- 卡片列表应出现两张同模板实例
- 编辑任一实例不得影响另一实例

### 10.3 后台验证

- 后台能看到同模板多实例
- 默认卡标识仍准确
