# 第一批真实分包迁移 - 技术设计

_Requirements: 00-07 全部_

## 1. 分包策略

本轮使用两个独立分包：

- `pkg-card`
- `pkg-tools`

原因：

- `actor-card` 与 `membership` 语义相近，均属于名片 / 会员相关页面
- `webview` 与 `video-player` 均为工具型页面，适合归到工具分包
- 根路径清晰，后续可继续扩展

## 2. 页面迁移映射

### 2.1 名片分包

- `pages/actor-card/index` → `pkg-card/actor-card/index`
- `pages/membership/index` → `pkg-card/membership/index`

### 2.2 工具分包

- `pages/webview/index` → `pkg-tools/webview/index`
- `pages/video-player/index` → `pkg-tools/video-player/index`

## 3. 影响面

需要同步修改：

- `src/pages.json`
- 页面内 `navigateTo` / `reLaunch` / `switchTab` 相关引用
- `src/utils/actor-card.ts` 中分享路径

## 4. 风险控制

- 不迁移 `home / mine / login / role-select` 等主入口页
- 不在本轮同时处理第二批业务页分包
- 迁移完成后以构建产物和 `audit:mp-package` 为准验证主包变化
