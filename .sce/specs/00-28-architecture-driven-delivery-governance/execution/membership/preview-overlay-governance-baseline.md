# Preview Overlay 治理基线

## 1. 目的

本基线用于收口 membership 当前最大的剩余结构风险：

`/card/personalization` 已成为模板 / 能力 / artifact 的主事实源，但“未保存 preview overlay”仍是前端显式编辑态。

本文件不否认 overlay 当前存在，而是明确：

- 当前为什么允许它暂留前端
- 它的边界是什么
- 哪些行为必须禁止
- 什么时候必须迁入后端临时摘要或 session 级状态

## 2. 当前判定

- 当前判定：`允许保留，但只能作为当前设备 session 级预览态`
- 当前结论：preview overlay 不是后端事实，不得参与会员、模板、artifact gating 的主判定；它当前只允许覆盖“当前设备、当前会话、尚未保存的布局 / 配色预览”

## 3. 当前代码事实

### 3.1 已经收口的部分

- `kaipai-frontend/src/utils/personalization.ts` 已统一承接：
  - `readPersonalizationPreviewOverlay`
  - `diffPersonalizationPreviewOverlay`
  - `applyPersonalizationPreviewOverlay`
  - `patchPathWithPersonalizationPreviewOverlay`
  - `readPersonalizationPreviewOverlaySession`
  - `writePersonalizationPreviewOverlaySession`
- `kaipai-frontend/src/pkg-card/actor-card/index.vue` 当前只在：
  - 当前设备 session 写入
  - `onShow` 重载恢复
  - 未保存布局 / 配色预览恢复
  这三类场景使用 overlay
- `kaipai-frontend/src/pages/actor-profile/detail.vue`、`src/pkg-card/invite/index.vue` 已开始优先读取同一份 session overlay，避免继续在公开详情页 / 邀请页再发明另一套 query key
- `kaipai-frontend/src/pkg-card/actor-card/index.vue` 的真实分享 path 已不再携带 overlay query；当前 query overlay 只保留为兼容旧路径和调试读取入口

### 3.2 尚未收口的部分

- overlay 仍不是后端事实，只是当前设备 session 恢复态
- 旧 query overlay 兼容读取仍在，尚未完全退场
- overlay 当前只定义了本地 session 生命周期，尚不支持跨登录、跨设备、跨端恢复

## 4. 当前允许的边界

以下行为当前允许：

1. overlay 只覆盖 `layoutVariant / primaryColor / accentColor / backgroundColor`
2. overlay 只来源于“当前用户尚未保存的编辑态”
3. overlay 只允许作用于：
   - actor-card 当前页预览
   - detail 页主题预览恢复
   - invite 页主题预览恢复
   - 当前设备 session 下的同 actor / scene 页面跳转恢复
4. overlay 一旦保存配置成功，就必须立即失效并回到 `/card/personalization` 主事实源
5. overlay 当前只允许保留在本地 session，默认 30 分钟过期，不允许当成长期状态缓存

## 5. 当前明确禁止的行为

以下行为当前禁止：

1. 禁止用 overlay 推导会员能力、等级能力、artifact 锁定状态
2. 禁止把 overlay 写成后端持久配置的替代事实源
3. 禁止在 `membership / actor-card / detail / invite / fortune` 各页自行维护新的 overlay query key
4. 禁止让 overlay 覆盖后台已发布模板、已回滚模板或后端下发 artifact path 的主事实
5. 禁止在未区分“已保存配置”和“临时预览”的情况下，把 overlay 参与真实环境联调结论

## 6. 当前治理规则

### 6.1 单一入口规则

- 读取 overlay 只能走 `utils/personalization.ts`
- 新页面不得直接读写 `previewLayout / previewPrimary / previewAccent / previewBackground`

### 6.2 单一语义规则

- overlay 语义固定为：`unsaved preview only`
- 不能把它扩展成：
  - membership 临时态
  - invite 资格态
  - theme 发布态
  - artifact 能力态

### 6.3 单一失效规则

以下任一事件发生后，应回到后端事实源：

- 保存当前场景配置成功
- 重新拉取 `/card/personalization`
- 退出当前编辑链路并重新进入真实分享链
- 当前设备 session 超过 30 分钟未刷新

## 7. 为什么当前不立即迁入后端

当前不立即迁入后端 / session 的原因不是“前端方案更优”，而是：

1. 现有风险已从“页面里散写 overlay”收敛到统一 helper
2. 当前更紧急的阻塞仍是 invite / membership / login-auth 的真实环境闭环证据
3. 若在没有真实环境样本前强推后端临时摘要，容易把结构改大但仍拿不到闭环证据

因此当前策略是：

- 先固定边界
- 再跑真实环境样本
- 最后按证据决定是否升级为后端/session 模型

## 8. 何时必须迁入后端或 session

满足以下任一条，即应把 overlay 从“当前设备 session 显式态”升级为“后端临时摘要 / 更强 session 状态”：

1. 真实环境联调证明 actor-card / detail / invite 无法稳定共享同一份未保存预览
2. 分享链路需要跨页面、跨登录、跨端恢复同一份未保存预览
3. overlay 字段不再只是布局 / 配色，而扩展到模板、artifact、capability 等高阶事实
4. 当前 query patch 已开始影响真实分享落点、审核链或运营回查

## 9. 下一步实现基线

下一轮若继续动 overlay，只允许做以下两类事：

1. 收口类：
   - 继续减少页面内 query patch 分支
   - 保证 actor-card / detail / invite 对同一份 session overlay 的解释一致
2. 升级类：
   - 明确引入后端临时摘要或 session 存储
   - 同时定义创建、读取、失效、回退规则

不允许再做的事：

- 在局部页面里继续补一层新的临时 patch 逻辑
- 让 overlay 默默参与真实模板 / 会员 / 分享主判定

## 10. 对状态卡的影响

从本基线开始，membership 状态卡里关于 overlay 的表述统一为：

- “preview overlay 当前是被允许的前端显式编辑态”
- “它不是后端事实源”
- “当前主路径已从 query patch 收口为当前设备 session 恢复”
- “是否进一步迁入后端，取决于真实环境样本证据，而不是口头偏好”
