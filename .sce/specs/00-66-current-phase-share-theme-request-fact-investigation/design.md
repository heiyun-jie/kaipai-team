# 00-66 设计说明

## 1. 设计原则

- 先拿事实，再改实现
- 用请求链证明问题位置，不用截图直觉代替证据
- 先分层定责，再讨论修法

## 2. 调查对象

### 2.1 前端页面

- `D:\XM\kaipai-team\kaipai-frontend\src\pkg-card\actor-card\index.vue`
- `D:\XM\kaipai-team\kaipai-frontend\src\pages\actor-profile\detail.vue`

### 2.2 前端类型与组装

- `D:\XM\kaipai-team\kaipai-frontend\src\api\level.ts`
- `D:\XM\kaipai-team\kaipai-frontend\src\utils\personalization.ts`
- `D:\XM\kaipai-team\kaipai-frontend\src\utils\theme-resolver.ts`

### 2.3 后端接口与聚合

- `D:\XM\kaipai-team\kaipaile-server\src\main\java\com\kaipai\module\server\card\service\impl\ActorCardConfigServiceImpl.java`
- `D:\XM\kaipai-team\kaipaile-server\src\main\java\com\kaipai\module\server\card\service\impl\ActorPersonalizationServiceImpl.java`

## 3. 调查步骤

### 3.1 保存链调查

目标：

```text
pkg-card/actor-card/index
  -> saveCurrentConfig()
  -> /api/card/config request payload
  -> /api/card/config response payload
```

必须确认：

- 当前编辑页提交的三色值是否等于用户选择值
- `highlightedPhotos / highlightedExperiences` 是否按用户选择真实提交
- 回包是否保持一致，还是被服务端重写

### 3.2 聚合链调查

目标：

```text
pages/actor-profile/detail
  -> /api/card/personalization
  -> profile.customConfig
  -> profile.sharePreferences
  -> theme.*
```

必须确认：

- 聚合层是否按 `/api/card/config` 最新保存值返回
- `theme.primary / accent / background` 是否与 `customConfig` 一致
- 是否存在二次覆盖，例如 fortune / template fallback / 旧 preference

### 3.3 页面消费链调查

目标：

```text
detail.vue
  -> themeTokens
  -> pageStyle/headerStyle
  -> summary/displayPhotos/displayExperiences
```

必须确认：

- 页面最终使用的是 `theme.*` 还是 `customConfig.*`
- `displayPhotos` 是否来自 `highlightedPhotos`
- `displayExperiences` 是否来自 `highlightedExperiences`
- 是否有固定色 / 固定结构把主题变化弱化

## 4. 结论输出格式

建议执行记录按三段给出：

1. 保存链事实
2. 聚合链事实
3. 页面消费链事实

最后给出唯一结论：

- 保存链错误
- 聚合链错误
- 页面消费链错误
- 或多点同时错误

## 5. 停止条件

在以下条件达成前，不再继续新改业务逻辑：

- 已拿到一次完整的 `/api/card/config` 保存样本
- 已拿到对应 `shareCardId` 的 `/api/card/personalization` 样本
- 已明确 `detail.vue` 最终消费点

## 6. 当前约束

- 当前所有后续实现必须先以本 Spec 的调查结论为准
- 若调查结论与先前已做修改冲突，应先记录冲突，再决定保留、回退或重做
