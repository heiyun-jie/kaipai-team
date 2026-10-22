# 演员卡单一首图来源收口 - 技术设计

_Requirements: 2.1-2.3, 3, 4_

## 1. 兼容数据模型

数据库保留三个历史字段与 `source_image` 素材绑定，不做 schema 迁移。统一的有效首图规则为：

```text
expandedImageUrl
-> source_image 绑定预览
-> sourceImageUrl（无显式空绑定时的历史兼容）
-> backgroundImageUrl
-> generatedPreviewUrl
-> 档案 cover/avatar
```

新前端选择模板图库时同时镜像写入 `backgroundImageUrl` 与 `sourceImageUrl`，并清空旧 `source_image` 绑定；选择素材时以绑定为真源，并显式清理旧 `backgroundImageUrl`。`expandedImageUrl` 在来源变化时清空。

## 2. 前端交互

### 2.1 `step-visual`

- 单个白色区段包含当前首图大图预览、素材库/手机操作、风格 Tab 和模板图库。
- `mainVisualSource` 只区分 `library` / `asset`，可见文案统一为“首图”。
- 模板图库点击只更新本地状态；进入下一步时清空素材绑定并保存 URL 镜像。
- 素材选择沿用当前即时绑定接口，绑定成功后清除模板选中态；进入下一步时显式清理旧背景镜像。
- 步骤页不再接收或触发 AI 扩图任务；后端扩图接口、`expandedImageUrl` 字段和解析优先级保留，内部编排由 `00-245` 及后续独立 Spec 管理。

### 2.2 创建 Hub

首页模板预选即时保存 `backgroundImageUrl` 和 `sourceImageUrl`，并清空复制卡可能继承的 `source_image` 绑定，使用户即使跳过步骤页也能得到一致首图。

## 3. 后端解析

- `ActorCardDraftServiceImpl`：步骤 1 支持图片字符串空值显式清理；步骤完成判据在素材绑定为空时认可 `backgroundImageUrl`，无绑定表时认可两个历史 URL。
- `ActorCardGenerateService`：生成门禁与输入认可素材绑定或历史 URL，显式空绑定只允许 `backgroundImageUrl` 作为模板图库来源。
- 私有素材绑定不持久化短时签名 URL；生成成功时用 `structured://actor-card/{id}` 标记结构化正文已生成，列表与公开图片解析器忽略该非 HTTP 标记。
- `ActorCardPublicServiceImpl`：一次计算有效首图，同时写入 `backgroundImageUrl` 和 `previewImageUrl`。
- `ActorCardPublishService`：列表封面增加 `backgroundImageUrl` 历史兜底。
- `ActorCardRenderer`：消费 `previewImageUrl` 优先；两个兼容字段同值时自动去重。

## 4. 验证与回滚

新增 `verify-00242-actor-card-single-main-visual.mjs`，断言单入口文案、互斥来源、保存语义、后端优先级、公开字段同值以及 build/dev 等价。后端补充草稿、生成、公开详情和列表封面的定向测试。

回滚恢复代码文件并重新构建即可；本次没有数据库迁移。新版本可能把模板图库 URL 同时写入两个历史字段，旧版本仍可读取，因此代码回滚后数据行为可恢复。
