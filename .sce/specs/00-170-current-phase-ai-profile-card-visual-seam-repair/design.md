# AI 资料册视觉接缝与封面遮罩修复 Design

> 状态：已被 `00-171-current-phase-ai-profile-card-single-cover-theme-flow` 取代。本文仅保留历史记录，不再指导当前实现。

## 1. 设计结论

本轮不再只依赖“让模型理解上一页底部 15%”。

设计采用双层策略：

1. **生成层继续优化**：后端 prompt 更明确要求上一页底部和下一页顶部形成可接续过渡带。
2. **渲染层确定性兜底**：前端在非 cover 页顶部直接渲染上一页底部参考带，并用轻量渐变与当前页背景融合。

这样可以把“模型生成质量”与“页面接缝确定性”分开。模型生成得好时，接缝自然；模型生成得一般时，用户至少能看到上一页底部被真实沿用。

## 2. 当前问题定位

### 2.1 左上白块来源

`kaipai-frontend/src/pkg-card/ai-profile-card-detail/index.vue` 当前存在：

```vue
<view
  v-if="page.pageType === 'cover' && page.displayImageUrl"
  class="ai-share-detail-page__cover-identity-shield"
/>
```

对应样式是固定浅色背景和大面积阴影。这是封面左上角白色遮盖的直接来源。

### 2.2 右下白块来源

同一文件存在：

```vue
<view
  v-if="page.pageType === 'cover' && page.displayImageUrl"
  class="ai-share-detail-page__cover-watermark-shield"
/>
```

该样式在右下角覆盖 42% 宽、128rpx 高的白色渐变。这是封面右下角空白遮挡的直接来源。

### 2.3 接续不稳定来源

后端当前已经保存 `continuityReferenceUrl`，但页面只把每页 `generatedImageUrl` 当作背景渲染。即使后端把上一页底部 15% 传给模型，页面仍无法保证下一页顶部一定等于上一页底部。

因此必须在页面层显式使用 `continuityReferenceUrl`。

## 3. 前端设计

### 3.1 移除封面固定遮罩

处理原则：

1. 删除或禁用 `cover-identity-shield` 的实际渲染。
2. 删除或禁用 `cover-watermark-shield` 的实际渲染。
3. 保留 `poster-tone` 作为整体可读性基础。
4. 如文字可读性不足，仅给标题文字增加轻量 `text-shadow`，不再用大面积白色块。

### 3.2 新增连续性顶部参考带

为非 cover 页增加一个视觉层：

```vue
<image
  v-if="shouldRenderContinuityBand(page)"
  class="ai-share-detail-page__continuity-band"
  :src="page.continuityReferenceUrl"
  mode="scaleToFill"
/>
<view
  v-if="shouldRenderContinuityBand(page)"
  class="ai-share-detail-page__continuity-band-fade"
/>
```

建议层级：

```text
poster bg image: z-index 0
continuity band: z-index 1
continuity fade: z-index 1
poster tone: z-index 2
business modules: z-index 3
```

如果当前样式已经把 `poster-tone` 设为 `z-index: 1`，可相应调整背景层与业务层，确保连续性参考带在背景上方、业务信息下方。

### 3.3 参考带尺寸

参考带高度优先使用后端字段：

```text
height = continuityBandRatio * 100%
```

默认值：

```text
0.15
```

限制范围：

```text
min 0.08
max 0.22
```

避免异常数据导致覆盖过多页面。

### 3.4 过渡融合

在参考带底部增加轻量透明渐变：

```scss
background: linear-gradient(
  180deg,
  rgba(...) 0%,
  rgba(...) 70%,
  transparent 100%
);
```

具体颜色不能写死为白色，应尽量只做 alpha fade；如果必须使用颜色，应从当前页面主题变量取值，避免再形成白块。

## 4. 后端设计

### 4.1 Prompt 强化

`cover`：

```text
底部约 15% 必须是可延展的纯背景过渡带，不要人物身体、衣料主体、文字、Logo、二维码、卡片或任何前景组件。
```

`resume / gallery`：

```text
顶部约 15% 必须贴近参考图1的主要形状、色彩、光线、纹理和空间方向，像直接从上一页底部继续向下生成；不要替换成普通墙面或全新背景。
```

仍保留短英文尾：

```text
Plain, unmarked, symbol-free.
```

### 4.2 数据返回

后端 DTO 当前已有连续性字段时，前端直接消费；如果字段名缺失，需要补齐到页面返回结构中：

```text
continuityReferenceUrl
continuityReferenceSourcePageType
continuityReferenceSourcePageNo
continuityBandRatio
continuityBandRect
continuityFailureReason
```

### 4.3 真实任务缺页处理

真实任务如果只返回一张背景图，需要优先定位是：

1. 后端只生成/返回了 cover。
2. `resume/gallery` 页面记录存在但 `generatedImageUrl` 为空。
3. 前端映射丢失。
4. 旧任务未按新 schema 补齐。

本 spec 不要求自动修复所有历史任务，但测试报告必须把缺页原因说清楚。

## 5. 测试设计

### 5.1 单元与类型验证

后端：

```text
mvn -q -DskipTests compile
mvn -q "-Dtest=AiProfileCardPromptAgentTest,TencentHunyuanProfileImageProviderTest,AiProfileCardServiceImplTest" test
```

前端：

```text
npm run type-check
```

### 5.2 视觉验证

必须输出：

1. 封面首屏截图。
2. `cover` 底部 15% 与 `resume` 顶部 15% 对比图。
3. `resume` 底部 15% 与 `gallery` 顶部 15% 对比图。
4. H5 或小程序页面截图，至少覆盖三页。

### 5.3 结果文件

建议输出到：

```text
output/diagnostics/ai-profile-card-visual-seam-repair/
```

该目录不提交，只作为本地验证证据。

## 6. Agent 分工

### 6.1 Frontend Agent

负责：

1. `kaipai-frontend/src/pkg-card/ai-profile-card-detail/index.vue`
2. 连续性参考带渲染。
3. 封面两个白色遮罩移除或禁用。
4. 前端类型检查和页面截图脚本配合。

### 6.2 Backend Agent

负责：

1. `kaipaile-server/src/main/java/com/kaipai/module/server/ai/profilecard/AiProfileCardPromptAgent.java`
2. 必要时调整 DTO 或服务返回字段。
3. 后端单测补充。

### 6.3 Verification Agent

负责：

1. 审查实现是否符合本 spec。
2. 跑流程截图测试。
3. 输出问题清单和截图路径。

## 7. 风险与取舍

1. 前端直接贴参考带会让下一页顶部与上一页底部一致，但 15% 下沿仍可能与当前页生成图存在轻微断层，所以需要 fade。
2. prompt 强化可以提高模型连续性，但不能作为唯一保障。
3. 右下水印遮挡移除后，如果 provider 再次输出水印，应回到 provider 配置或重试策略处理，而不是恢复默认白块。
4. 历史任务可能缺少连续性字段，前端必须容错。
