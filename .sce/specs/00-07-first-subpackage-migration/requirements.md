# 00-07 第一批真实分包迁移（First Subpackage Migration）

> 状态：进行中 | 优先级：高 | 依赖：00-05, 00-06, 05-05

## 1. 目标

执行第一批真实微信小程序分包迁移，优先将非 tab、入口明确、与名片 / 会员 / 工具能力相关的页面迁出主包，直接降低主包体积并为后续继续增长留出空间。

## 2. 本轮范围

- `actor-card`
- `membership`
- `webview`
- `video-player`

## 3. 需求

### 3.1 分包迁移

- **R1** 上述四个页面必须迁移到真实 `subPackages`，不得只停留在候选清单。
- **R2** 分包根路径必须独立清晰，不得继续沿用统一 `pages/*` 根路径做模糊划分。
- **R3** 页面源码路径、`pages.json` 注册路径、页面跳转路径和分享路径必须同步更新。

### 3.2 行为稳定

- **R4** 页面迁移后，现有入口语义不得变化。
- **R5** `actor-card` 分享进入链路必须继续可用，`onShareAppMessage` / `onShareTimeline` 产物路径必须与新页面路径一致。
- **R6** `webview` 和 `video-player` 的返回行为不得被路径迁移破坏。

### 3.3 主包治理

- **R7** 本轮目标是降低主包体积，不要求总包体积显著下降。
- **R8** 必须通过 `audit:mp-package` 验证分包确实生成，并记录主包体积变化。

## 4. 验收标准

- [ ] 已新增 `subPackages` 配置
- [ ] 四个页面已完成真实迁移
- [ ] 页面跳转与分享路径已全部更新
- [ ] `npm run type-check` 通过
- [ ] `npm run build:mp-weixin` 通过
- [ ] `npm run audit:mp-package` 输出主包 / 分包结果
