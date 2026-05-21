# AI 分享图跨页连续生图与中文 prompt 契约 - 技术设计

> 状态：已被 `00-171-current-phase-ai-profile-card-single-cover-theme-flow` 取代。本文仅保留历史记录，不再指导当前实现。

## 1. 设计结论

这次要做的，不是改成“更多页”，也不是改成“更强 OCR”。设计结论很明确：

1. 三页仍然固定是 `cover / resume / gallery`。
2. 第二页和第三页必须继承上一页的**尾部视觉带**，而不是整页复用。
3. prompt 必须采用**中文为主**的业务描述。
4. 仍然保留一段**短、硬、稳定**的英文约束尾，作为模型的最后防线。

推荐的 prompt 结构是：

```text
中文业务目标
中文构图说明
中文风格和背景说明
中文跨页连续性说明
短英文约束尾
中文禁用项补充
```

其中最稳定的英文尾保持为：

```text
Plain, unmarked, symbol-free.
```

## 2. 跨页连续性流

### 2.1 页面接续顺序

```text
cover 生成完成
  -> 提取 cover 尾部连续性参考带
  -> 用于 resume 的顶部衔接
  -> resume 生成完成
  -> 提取 resume 尾部连续性参考带
  -> 用于 gallery 的顶部衔接
  -> gallery 生成完成
```

### 2.2 参考带策略

连续性参考带建议采用上一页底部的固定比例裁切，而不是整页：

- 推荐比例：`12% ~ 15%`
- 参考带来源：上一页生成图的底部区域
- 参考带用途：提供纹理、光线、色彩、空间方向的连续信号
- 禁止用途：复制人物主体、复制业务文字、复制前景卡片

如果 provider 支持 image-to-image 或 reference image 输入，则优先把参考带作为输入。
如果 provider 不支持，则保留参考带 metadata 和文字连续性说明，进入降级模式，并在任务/页面状态中记录。

## 3. Prompt Contract

### 3.1 中文为主的基础模板

所有页面的 prompt 都应满足以下顺序：

1. 用中文说明当前页要做什么。
2. 用中文说明构图和页面职责。
3. 用中文说明风格和背景。
4. 用中文说明如何延续上一页结尾。
5. 用短英文尾做硬约束收口。
6. 最后再用中文补充禁用项。

### 3.2 Cover 模板

```text
生成一张 9:16 全幅演员封面背景图，输出 2160x3840。
构图：演员在右侧，左侧留空给后续信息层。
画面底部保留一段安静、低细节、可继续延伸的过渡区，供下一页自然接续。
风格：{style}
背景：{background}
Plain, unmarked, symbol-free.
不要可读文字、水印、Logo、标签、二维码、UI 形状。
```

### 3.3 Resume 模板

```text
生成一张 9:16 全幅履历背景图，输出 2160x3840。
顶部 15% 延续上一页结尾的色彩、光线、材质和空间方向，让它像同一本资料册自然翻页。
无人物主体，页面以资料背景承载为主。
风格：{style}
背景：{background}
Plain, unmarked, symbol-free.
不要人物肖像、可读文字、水印、Logo、标签、二维码、UI 形状。
```

### 3.4 Gallery 模板

```text
生成一张 9:16 全幅影像页背景图，输出 2160x3840。
顶部 15% 延续上一页结尾的色彩、光线、材质和空间方向，让它和履历页保持同一组连续气质。
无人物主体，画面要给照片墙和视频入口留出安静背景。
风格：{style}
背景：{background}
Plain, unmarked, symbol-free.
不要人物肖像、可读文字、水印、Logo、标签、二维码、缩略图框、视频控件或 UI 形状。
```

### 3.5 语言策略

中文作为主提示语言的原因：

1. 后台配置和人工复核更直接。
2. 业务语义更容易对齐国内厂商的真实能力边界。
3. prompt 迭代时更容易看出到底是“构图问题”还是“禁用项问题”。

英文尾保留的原因：

1. 硬约束更短。
2. 对多个 provider 更容易复用。
3. 对避免文字、水印、符号的指令更像统一的最后收口。

## 4. Provider 适配

### 4.1 Tencent 混元

Tencent 这条链路以单个 `Prompt` 字段为主，设计上应尽量做到：

1. prompt 主体中文化。
2. 末尾固定短英文约束尾。
3. 避免把“slot 名称”“内部布局代码”“SQL 风格字段名”直接暴露给模型。
4. 在长度上继续维持可控，不超过当前 provider 上限。

### 4.2 其他 provider

如果后续 provider 支持更完整的 `negative_prompt` 或参考图结构，则保留相同的逻辑契约：

1. 中文主 prompt。
2. 短英文约束尾。
3. 连续性参考带优先于整页参考。
4. 文字/Logo/UI 禁用项保持统一。

### 4.3 降级策略

当 provider 不支持连续性参考带输入时：

1. 仍然必须输出中文主 prompt。
2. 仍然必须保留短英文约束尾。
3. 仍然必须记录本次连续性降级。
4. 仍然必须让 QA 能区分“参考图缺失”与“prompt 失败”。

## 5. 数据与持久化设计

建议为每个页面保存以下逻辑信息：

```text
pageType
pageNo
promptText
promptJson
negativePrompt
promptLocale
continuityMode
continuityBandRatio
continuityReferenceSourcePage
continuityReferenceUrl
providerCode
modelCode
generatedImageUrl
status
failureReason
retryCount
```

其中：

- `promptLocale` 建议记录为 `zh-CN`。
- `continuityMode` 建议记录为 `tail_reference` / `text_only` / `degraded` 等可审计值。
- `continuityReferenceUrl` 建议指向裁切后的尾部参考图，而不是整页原图。

## 6. QA 与验收方式

### 6.1 截图验证

验收时必须覆盖：

1. `cover` 的底部过渡带。
2. `resume` 的顶部接续带。
3. `resume` 的底部过渡带。
4. `gallery` 的顶部接续带。

### 6.2 白盒验证

验收时必须确认：

1. 参考输入来自上一页尾部裁片。
2. prompt 语言主体是中文。
3. 英文尾是固定短句，而不是长段说明。
4. OCR 不参与主要控制路径。

## 7. Open Decisions

1. 连续性参考带是单独落库，还是只放在 `prompt_json` 里。
2. 连续性裁切比例是否固定为 `15%`，还是在配置中允许小幅调整。
3. Tencent 之外的 provider 是否都统一采用同一套中文 prompt 模板。
4. 是否需要把连续性降级态暴露给后台可视化界面。
