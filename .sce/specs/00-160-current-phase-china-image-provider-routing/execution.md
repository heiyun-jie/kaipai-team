# 00-160 执行调查与配合清单

## 调查日期

- 当前日期：2026-05-12
- 调查对象：国内国区官方云厂商生图 API，用于 AI 演员资料卡图生图/背景生成。

## 当前项目接入基础

- 后端已有 `AiProfileImageProvider` 抽象。
- 后端已有 `AiProfileImageProviderRegistry`，按 `providerCode()` 选择实现。
- 后端已有 `HttpAiProfileImageProvider`，可作为临时中转网关验证新 provider。
- 现有配置入口：`kaipai.ai.profile-card.provider-code`。
- 现有生成模式：`image_to_image`。
- 现有结果持久化：`AiGeneratedImageStorage.uploadFromUrl(...)` / `upload(...)`。

结论：不需要改小程序端即可开始接入国内 provider。当前需求已明确为管理后台页面动态切换，并在后台直接录入密钥/API Key 供后端调用；因此优先级从“环境变量切换”调整为“后台配置中心 + 密钥加密落库 + provider 直连”。

## Provider 调查表

| Provider | 推荐用途 | 接入优先级 | 图生图/参考图 | 鉴权 | 结果 URL | 关键风险 |
|---|---|---:|---|---|---|---|
| 火山 Seedream | 首选 POC，演员来源图 + 风格提示词 | 首批 | 官方文档支持 `reference_images` 1 张或多张 | 后台录入 API Key / Base URL，最终以控制台为准 | `url` 24 小时或 `b64_json` | endpoint/产品线需账号侧确认；水印默认开启 |
| 阿里百炼 Qwen Image | 首选 POC，负向提示词和主体一致性 | 首批 | Qwen 编辑支持 1-3 张输入图；Wan 文档说明最多 9 张参考 | 后台录入 DashScope API Key | OSS 临时 URL | Qwen/Wan 调用形态不同，建议拆 provider |
| 腾讯混元生图 | 腾讯云生态备选/对照 | 第二批或首批对照 | `ContentImage` 可作为参考图 | 后台录入 Tencent Cloud SecretId/SecretKey，云 API 3.0 签名 | 查询结果 URL 1 小时 | 异步任务、默认 1 并发、TokenHub 迁移提示 |
| 百度千帆 | 成本/兼容备选 | 备选 | 文档写可根据文本或图片生成，但公开字段需二次确认 | 后台录入 API Key Bearer | URL 24 小时 | 图生图字段未完全确认前不能做主 provider |

## 官方资料摘录

### 火山 Seedream

官方文档确认：

- 文生图：仅输入 `prompt`。
- 图生图：输入 `reference_images` 一张或多张 + `prompt`。
- 返回 `url` 或 `b64_json`。
- `url` 链接生成后 24 小时内失效。
- 支持 `doubao-seedream-4.0` version `250828`、`doubao-seedream-4.5` version `251128`。
- `watermark` 默认 `true`。

来源：`https://www.volcengine.com/docs/6492/2221472`

需要你提供：

- 火山账号主体。
- Seedream 服务是否已开通。
- API Key。
- Base URL / endpoint。
- 模型名和版本号。
- 免费额度或预算限制。
- 是否允许 provider 水印。

### 阿里云百炼

官方文档确认：

- 图片生成与编辑页推荐 `wan2.7-image-pro`，支持文生图和编辑，文生图最高 4096x4096，编辑最高 2048x2048。
- `qwen-image-2.0-pro` 支持文生图和编辑，支持负向提示词，最多 6 张图片变体。
- Qwen 图像编辑可输入 1-3 张图片和一条文本编辑指令。
- 北京地域 multimodal generation URL 示例为 `https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation`。
- 返回图片 URL，需要下载持久化。

来源：

- `https://help.aliyun.com/zh/model-studio/image-model`
- `https://help.aliyun.com/zh/model-studio/text-to-image`
- `https://help.aliyun.com/zh/model-studio/qwen-image-edit-guide`

需要你提供：

- 阿里云账号主体。
- 百炼是否已开通。
- 中国内地还是国际地域；建议中国内地北京。
- `DASHSCOPE_API_KEY`。
- 选择 `qwen-image-2.0-pro`、`wan2.7-image-pro` 或其他模型。
- 免费额度用完是否停止。
- 水印策略。

### 腾讯混元

官方文档确认：

- 产品支持文本或图片输入相关的图像生成与处理能力。
- `SubmitHunyuanImageJob` 域名 `hunyuan.tencentcloudapi.com`。
- 仅支持 `ap-guangzhou`。
- 支持 `Prompt`、`NegativePrompt`、`Resolution`、`Num`、`ContentImage`、`LogoAdd`。
- 查询接口返回 `JobStatusCode` 和 `ResultImage`；结果 URL 有效期 1 小时。
- 免费额度：首次开通后混元生图、图像风格化等多项接口各 50 次，资源包有效期 1 年。
- 计费页提示混元能力会逐步迁移 TokenHub，新购/开通路径需确认。

来源：

- `https://cloud.tencent.com/document/product/1668/86244`
- `https://cloud.tencent.com/document/product/1668/90897`
- `https://cloud.tencent.com/document/product/1729/105925`
- `https://cloud.tencent.com/document/api/1729/105969`
- `https://cloud.tencent.com/document/api/1729/105970`

需要你提供：

- 腾讯云账号主体。
- SecretId / SecretKey。
- 是否已开通混元生图或 TokenHub 对应服务。
- 免费资源包是否到账。
- 是否允许开启后付费。
- 是否接受默认 1 并发，或需要购买并发包。
- `LogoAdd` 水印策略。

### 百度千帆

官方文档确认：

- 通用图像生成 API：`POST https://qianfan.baidubce.com/v2/images/generations`。
- API 可根据用户输入的文本或图片生成图片。
- 请求字段包括 `model`、`prompt`、`negative_prompt`、`n`、`size`、`steps`、`seed`、`guidance`、`prompt_extend`、`watermark`。
- 返回 `data[*].url`，链接有效期 24 小时。
- `watermark=true` 会在右下角添加 `AI生成` 可见水印，默认 `false`。

来源：

- `https://cloud.baidu.com/doc/qianfan-api/s/8m7u6un8a`
- `https://cloud.baidu.com/doc/qianfan/s/cmmk7fprv`
- `https://cloud.baidu.com/doc/qianfan/s/Smh4stmxs`

需要你提供：

- 百度智能云账号主体。
- 千帆 API Key / Bearer 凭证。
- 模型 ID，例如 `qwen-image` 或账号内可用模型。
- 控制台确认图生图参数字段和模型支持范围。
- 是否有活动券或付费预算。

## 合规要求

官方监管文件确认：

- 向中国境内公众提供生成文本、图片、音频、视频等内容的生成式 AI 服务，适用《生成式人工智能服务管理暂行办法》。
- API 方式提供生成式 AI 服务也被定义为生成式 AI 服务提供方式。
- 生成式 AI 服务涉及个人信息时，应履行个人信息保护义务；不得侵害肖像权、隐私权、个人信息权益。
- 图片等生成内容应按深度合成要求标识。
- 2025 年《人工智能生成合成内容标识办法》要求生成合成内容标识包含显式标识和隐式标识；图片应在适当位置添加显著提示标识，文件元数据中应添加隐式标识。

来源：

- `https://www.cac.gov.cn/2023-07/13/c_1690898327029107.htm`
- `https://www.cac.gov.cn/2025-03/14/c_1743654684782215.htm`

项目落地要求：

- 用户必须授权上传演员照片用于 AI 生成。
- 不给模型发送手机号、微信、二维码、私信、审核备注。
- 输出图和页面必须有 `AI生成` 显式标识或经产品/合规确认的等效方案。
- 后端记录 provider/model/taskId/contentId 作为隐式追溯。
- 上架材料准备 provider、模型、备案/合规说明。

## 用户配合表

请按下面格式补给我。真实密钥不要写进聊天或仓库；后续通过管理后台页面录入。后台允许有权限的管理员回显完整密钥，但必须二次确认并写审计。

```text
首批 POC provider：
- [ ] 火山 Seedream
- [ ] 阿里百炼 Qwen/Wan
- [ ] 腾讯混元
- [ ] 百度千帆

配置入口：
- [x] 必须做后台管理页面动态切换
- [x] 后台页面直接录入 API Key / SecretId / SecretKey
- [x] 允许后台回显完整密钥
- [ ] 回显密钥是否需要二次确认
- [ ] 是否需要复制密钥按钮
- [ ] 需要密钥清空/轮换功能
- [ ] 需要后台测试连接/测试生成按钮

权限：
- 哪些后台角色可以查看 provider 配置：
- 哪些后台角色可以回显完整密钥：
- 哪些后台角色可以修改公开参数：
- 哪些后台角色可以修改密钥：
- 哪些后台角色可以设为主模型：

密钥加密：
- `AI_PROVIDER_CONFIG_MASTER_KEY` 是否可在测试环境配置：是/否
- `AI_PROVIDER_CONFIG_MASTER_KEY` 是否可在生产环境配置：是/否
- 是否需要密钥轮换流程：是/否

预算：
- 免费额度用完即停：是/否
- 是否允许后付费：是/否
- POC 最大生成张数：
- 单日最大生成张数：

火山：
- 账号主体：
- 服务已开通：是/否
- API Key：后续后台页面录入
- endpoint/baseUrl：
- model：
- version：
- watermark：

阿里：
- 账号主体：
- 百炼已开通：是/否
- API Key：后续后台页面录入
- region/baseUrl：
- model：
- size：
- watermark：

腾讯：
- 账号主体：
- 混元/TokenHub 已开通：是/否
- SecretId：后续后台页面录入
- SecretKey：后续后台页面录入
- region：
- 免费资源包到账：是/否
- LogoAdd：

百度：
- 账号主体：
- 千帆已开通：是/否
- API Key：后续后台页面录入
- model：
- 图生图字段已确认：是/否

样本：
- 授权演员样本数量：
- 每个样本来源图数量：
- 是否允许传给上述云厂商做 AI 生成测试：是/否
```

## 推荐执行顺序

1. 先实现后台 provider 配置表、审计表、密钥加密服务和管理 API。
2. 再实现 `kaipai-admin` AI 生图模型配置页面，支持录入密钥、启用、设为主模型、测试。
3. 先接一家具备明确图生图接口的 provider，建议 `aliyun-qwen-image` 或你已经拿到密钥的腾讯/火山。
4. 再接第二家 provider 做对照。
5. 通过后台页面录入真实密钥，跑 10 个演员 x 3 风格样本。
6. 汇总质量和成本后决定生产主 provider。
7. 最后再做按风格路由和 fallback 策略。
