# 当前主线组件化重构 - 技术设计

_Requirements: 05-07 全部_

## 1. 抽取策略

本轮分两阶段推进：

- 第一阶段优先抽取“行为逻辑”
- 第二阶段补充抽取“低风险纯展示组件”

原因：

- 浮动返回导航的重复主要在 JS 计算而非模板
- 媒体选择的重复主要在交互流程而非展示样式
- 先收敛行为，可减少页面脚本膨胀且不容易破坏 UI
- 在行为逻辑稳定后，再收敛重复展示壳层，可进一步缩短页面模板与样式长度
- 第二阶段仅处理结构重复且语义稳定的块，不把差异较大的业务模块强行统一

## 2. 模块设计

### 2.1 浮动返回导航

新增工具：

```ts
src/utils/floating-back-nav.ts
```

输出：

- `navStyle`
- `backButtonStyle`

统一计算口径：

- `statusBarHeight`
- `menuButtonRect.top`
- `menuButtonRect.height`
- `menuButtonRect.bottom`

### 2.2 媒体选择

新增工具：

```ts
src/utils/media-picker.ts
```

提供能力：

- 选择图片来源
- 选择视频来源
- 选择图片文件
- 选择视频文件

页面仍保留：

- 上传行为
- 上传后数据落点
- 成功 / 失败提示

### 2.3 展示组件

候选组件：

```ts
src/components/KpSectionHead.vue
src/components/KpPillSelector.vue
src/components/KpMineMenuItem.vue
```

约束：

- `KpSectionHead` 仅承载标题 / 描述 / 右侧附加区，不内置业务文案
- `KpPillSelector` 仅承载一组可选项、选中态和可选锁定态，不内置会员判断
- `KpMineMenuItem` 仅承载菜单项外壳、图标插槽和右箭头，不吞掉页面路由逻辑

这样可保证：

- 页面仍保留业务数据拼装与点击行为
- 重复样式和结构迁移到共享组件
- 不额外引入图片资源或第三方依赖，避免包体无意义增长

### 2.4 包体控制

当前 `src/pages.json` 仍全部挂在主包，尚未配置 `subPackages`。

因此本轮设计约束为：

- 只新增轻量共享组件和工具，不引入新页面和大资源
- 优先复用现有变量、slot 与 class 组合，避免重复复制样式块
- 后续若会员页、分享页、设置页继续膨胀，应单独起 spec 规划分包迁移

## 3. 接入范围

### 3.1 浮动返回导航

优先替换：

- `pages/actor-card/index.vue`
- `pages/actor-profile/edit.vue`
- `pages/company-profile/edit.vue`
- `pages/role-detail/index.vue`
- `pages/webview/index.vue`

### 3.2 媒体选择

优先替换：

- `pages/actor-profile/edit.vue`
- `pages/company-profile/edit.vue`

### 3.3 展示组件

优先替换：

- `pages/actor-card/index.vue`
- `pages/mine/index.vue`

## 4. 非目标

- 本轮不抽图标绘制本身的纯装饰细节组件
- 本轮不调整海报 canvas 生成逻辑

这些项保留为下一轮候选重构。
