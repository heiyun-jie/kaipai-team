# 00-160 设计

## 开头先回答三个问题

1. 这次改哪里：扩展后端 AI 资料卡生图 provider、后台管理端动态配置页面、密钥加密落库、日志、测试和运行文档；小程序继续消费既有任务和作品接口。
2. 为什么这样改：当前 `AiProfileImageProvider`、`AiProfileImageProviderRegistry`、`AiProfileCardPromptAgent` 已经具备 provider 抽象，新增后台配置中心后可以不重启服务切换国内 provider。
3. 不改哪里：不把厂商 API 调用放到前端；不改变 AI 资料卡“模型生成背景、确定性渲染文字”的产品合同；不让 mock/source image fallback 变成成功产物。

## 当前架构事实

- `AiProfileCardServiceImpl.generate` 创建任务时通过 `promptAgent.resolveProvider(properties.getProviderCode())` 确定 provider 和 model。
- `AiProfileCardPromptAgent.generate` 负责构造 provider-independent prompt，并调用 `AiProfileImageProvider.generate(...)`。
- `AiProfileImageProviderRegistry` 通过 Spring 注入的 `List<AiProfileImageProvider>` 按 `providerCode()` 匹配。
- 结果通过 `AiGeneratedImageStorage` 持久化，支持 provider 返回 URL 或图片字节。
- 现有 provider 包含 `kplyyk`、`http`、`openai`。

## 总体方案

### P0：后台动态配置

P0 以管理后台页面动态切换为主能力。后端环境变量只保留两类用途：

- 密钥加密主密钥：`AI_PROVIDER_CONFIG_MASTER_KEY`。
- 配置中心不可用时的只读兜底 provider，例如 `AI_PROFILE_CARD_PROVIDER_CODE_FALLBACK=kplyyk`。

管理后台负责维护：

- 当前主 provider。
- 各 provider 是否启用。
- 各 provider 的公开配置。
- 各 provider 的密钥/API Key/SecretId/SecretKey。
- 测试连接和测试生成。
- 操作审计和版本回滚。

### 数据模型

新增 provider 配置表，建议命名为 `ai_image_provider_config`：

```sql
CREATE TABLE ai_image_provider_config (
  config_id BIGINT PRIMARY KEY AUTO_INCREMENT,
  provider_code VARCHAR(64) NOT NULL,
  display_name VARCHAR(128) NOT NULL,
  enabled TINYINT NOT NULL DEFAULT 0,
  active TINYINT NOT NULL DEFAULT 0,
  priority INT NOT NULL DEFAULT 100,
  public_config_json JSON NOT NULL,
  secret_config_ciphertext TEXT NULL,
  secret_mask_json JSON NULL,
  secret_updated_by BIGINT NULL,
  secret_updated_at DATETIME NULL,
  last_test_status VARCHAR(32) NULL,
  last_test_message VARCHAR(512) NULL,
  last_test_at DATETIME NULL,
  version INT NOT NULL DEFAULT 1,
  deleted TINYINT NOT NULL DEFAULT 0,
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
  update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY uk_provider_code_deleted (provider_code, deleted)
);
```

新增配置版本/审计表，建议命名为 `ai_image_provider_config_audit`：

```sql
CREATE TABLE ai_image_provider_config_audit (
  audit_id BIGINT PRIMARY KEY AUTO_INCREMENT,
  config_id BIGINT NOT NULL,
  provider_code VARCHAR(64) NOT NULL,
  action VARCHAR(64) NOT NULL,
  before_public_config_json JSON NULL,
  after_public_config_json JSON NULL,
  before_secret_mask_json JSON NULL,
  after_secret_mask_json JSON NULL,
  operator_id BIGINT NOT NULL,
  operator_ip VARCHAR(64) NULL,
  result VARCHAR(32) NOT NULL,
  message VARCHAR(512) NULL,
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

说明：

- `public_config_json` 存 endpoint、region、model、size、watermark、timeout、poll 等非密钥参数。
- `secret_config_ciphertext` 存加密后的 JSON，例如 `{"apiKey":"...","secretId":"...","secretKey":"..."}`。
- `secret_mask_json` 存脱敏值，例如 `{"apiKey":"****abcd","secretKey":"****wxyz"}`。
- `active=1` 同一时间只能有一个；通过事务或唯一约束保证。
- 不在审计表保存密钥明文或密文，只保存脱敏变化和密钥查看动作。

### 密钥加密

后端新增 `AiProviderSecretCryptoService`：

- 加密算法：AES-256-GCM。
- 主密钥来源：`AI_PROVIDER_CONFIG_MASTER_KEY`，生产环境必须配置。
- 每次加密生成随机 IV。
- 密文结构包含 `version`、`alg`、`iv`、`ciphertext`、`tag`。
- 解密只发生在 provider 调用前。
- 除“查看密钥”接口的专用响应 DTO 外，日志、异常、普通 DTO、审计记录都不得包含明文密钥。

密钥更新规则：

- 后台提交空值表示不修改原密钥。
- 后台提交新值表示覆盖对应密钥字段。
- 后台提供“清空密钥”操作，必须二次确认。
- 后台页面默认只展示 `secret_mask_json` 和更新时间；具备权限的管理员可通过“查看密钥”动作回显完整密钥。
- “查看密钥”必须二次确认，记录操作人、时间、IP、providerCode 和字段名，不记录密钥值。

### 后端运行时解析

新增 `AiImageProviderConfigService`：

- `resolveActiveConfig()`：返回当前启用且 active 的 provider 配置。
- `resolveConfig(providerCode)`：返回指定 provider 配置。
- `decryptSecret(config)`：只在调用 provider 前解密。
- `refreshCache()`：配置变更后刷新本地缓存。

调整生成链路：

- `AiProfileCardServiceImpl.generate` 不再只读 `properties.getProviderCode()`，改为通过 `AiImageProviderRoutingService.resolve(...)` 获取当前 active provider descriptor。
- `AiProfileCardPromptAgent.generate` 传入 providerCode 后，provider 内部读取对应运行时配置。
- `AiProfileImageProvider.modelCode()` 对动态 provider 返回当前配置里的 model；若配置缺失则抛出可读错误。
- `kplyyk` / `http` / `openai` 可保留原配置模式，也可迁移成后台 provider 记录。

### 后台 API

新增管理接口，路径建议：

- `GET /admin/ai/image-providers`
- `GET /admin/ai/image-providers/{providerCode}`
- `PUT /admin/ai/image-providers/{providerCode}/public-config`
- `PUT /admin/ai/image-providers/{providerCode}/secret`
- `POST /admin/ai/image-providers/{providerCode}/enable`
- `POST /admin/ai/image-providers/{providerCode}/disable`
- `POST /admin/ai/image-providers/{providerCode}/activate`
- `POST /admin/ai/image-providers/{providerCode}/clear-secret`
- `POST /admin/ai/image-providers/{providerCode}/reveal-secret`
- `POST /admin/ai/image-providers/{providerCode}/test`

权限建议：

- `action.system.ai-image-provider.view`
- `action.system.ai-image-provider.update`
- `action.system.ai-image-provider.secret.update`
- `action.system.ai-image-provider.secret.view`
- `action.system.ai-image-provider.activate`
- `action.system.ai-image-provider.test`

### 后台页面

新增页面建议挂在后台 `系统设置` 或 `AI 治理` 下：

- 左侧 provider 列表：厂商、启用状态、当前主模型、最近测试状态。
- 右侧配置面板：
  - 基础配置：endpoint、region、model、version、size、quality、watermark、timeout、poll。
  - 密钥配置：按 provider 展示 API Key / SecretId / SecretKey / Bearer Token。
  - 密钥状态：已配置/未配置、脱敏尾号、更新时间。
  - 密钥回显：具备 `secret.view` 权限的管理员可二次确认后查看完整密钥。
  - 操作：保存配置、保存密钥、查看密钥、测试连接、设为当前主模型、停用、清空密钥。
- 所有危险操作二次确认。
- 密钥输入框必须使用 password 类型；保存成功后立即清空输入框。
- 回显出来的密钥只保存在当前页面内存状态，页面刷新、切换 provider、关闭弹窗后立即清除。
- 复制密钥按钮只在已回显且具备 `secret.view` 权限时展示，复制动作也要写审计。

## Provider 适配器

### `VolcSeedreamProfileImageProvider`

用途：首选图生图 POC，适合演员来源图 + 风格提示词。

官方能力摘要：

- Seedream 文档说明支持仅 `prompt` 文生图，也支持 `reference_images` 一张或多张参考图 + `prompt` 图生图。
- 返回格式支持 `url` 和 `b64_json`；`url` 链接生成后 24 小时内失效。
- 支持 `doubao-seedream-4.0` version `250828`、`doubao-seedream-4.5` version `251128`。
- `watermark` 默认值为 `true`。

映射：

- `request.promptText()` -> `prompts` / `prompt`。
- `request.sourceImageUrl()` -> `reference_images[0]`。
- `request.negativePrompt()` -> 追加到 prompt 或 provider 支持字段。
- `config.size` -> `size`。
- `config.responseFormat` -> `response_format`。
- 返回 `list[str]` URL 或 base64 -> `AiProfileImageGenerationResult`。

风险：

- 需要确认使用 LAS 算子还是方舟在线 API 的最终 endpoint 和鉴权形态。
- 水印策略要和项目自己的 `AI生成` 标识统一。

### `AliyunQwenImageProfileImageProvider`

用途：图像编辑 / 图生图 POC，特别适合保留主体和使用负向提示词。

官方能力摘要：

- 百炼图片模型页推荐 `wan2.7-image-pro` 作为图像生成与编辑能力较完整模型。
- `qwen-image-2.0-pro` 支持生成和编辑，适合需要负向提示词、最多 6 张输出变体。
- 千问图像编辑文档说明 `messages` 中可输入 1-3 张图片和一条文本指令，返回结果 URL。
- 北京地域 API URL 示例为 `https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation`。

映射：

- `request.sourceImageUrl()` -> `input.messages[0].content[0].image`。
- `request.promptText()` -> `input.messages[0].content[n].text`。
- `request.negativePrompt()` -> `parameters.negative_prompt`。
- `config.size` -> `parameters.size`，格式 `1024*1536`。
- `config.watermark` -> `parameters.watermark`。
- 返回 `output.choices[0].message.content[*].image` -> 第一张 URL。

风险：

- 阿里返回 OSS 临时 URL，必须立即下载并持久化。
- 如果使用 `wan2.7-image-pro`，同步/异步调用方式和图像输入上限与 Qwen 不完全一样，需拆成独立 provider 或策略分支。

### `TencentHunyuanProfileImageProvider`

用途：腾讯体系备选，适合中文场景和东方审美，但异步任务和云 API 签名复杂度更高。

官方能力摘要：

- 腾讯混元生图产品提供文本或图片输入相关的图像生成与处理能力。
- `SubmitHunyuanImageJob` 请求域名为 `hunyuan.tencentcloudapi.com`，接口仅支持 `ap-guangzhou`。
- 输入包含 `Prompt`、`NegativePrompt`、`Resolution`、`Num`、`ContentImage`、`LogoAdd` 等。
- 查询接口 `QueryHunyuanImageJob` 返回 `JobStatusCode` 和 `ResultImage`，结果 URL 有效期 1 小时。
- 混元生图默认 1 个并发任务。

映射：

- 后端下载 `sourceImageUrl` -> Base64 -> `ContentImage`。
- `request.promptText()` -> `Prompt`。
- `request.negativePrompt()` -> `NegativePrompt`。
- `config.resolution` -> `Resolution`，9:16 优先 `720:1280`。
- `LogoAdd` 默认跟随合规策略。
- 提交得到 `JobId` 后轮询 `QueryHunyuanImageJob`，`JobStatusCode=5` 成功，`ResultImage[0]` 转 `AiProfileImageGenerationResult.imageUrl`。

风险：

- 腾讯云 API 3.0 签名建议用 Tencent Cloud Java SDK，手写签名风险高。
- 图生图参考图分辨率限制比项目目标 2160x3840 更紧，可能影响最终大图质量。
- 计费文档提示混元大模型功能逐步迁移 TokenHub，接入前需要确认新购/开通路径。

### `BaiduQianfanProfileImageProvider`

用途：成本或 OpenAI-compatible 形态备选。首版可先支持文生图或 confirmed image input；图生图参数需账号侧二次确认。

官方能力摘要：

- 千帆通用图像生成 API 为 `POST https://qianfan.baidubce.com/v2/images/generations`。
- 文档说明可根据用户输入的文本或图片生成图片。
- 请求字段包含 `model`、`prompt`、`negative_prompt`、`n`、`size`、`steps`、`seed`、`guidance`、`prompt_extend`、`watermark`。
- 返回 `data[*].url`，图片链接有效期 24 小时。

映射：

- `request.promptText()` -> `prompt`。
- `request.negativePrompt()` -> `negative_prompt`，仅在模型支持时发送。
- `config.size` -> `size`，优先 `1152x2048` 或 `768x1024`。
- `config.watermark` -> `watermark`。
- 返回 `data[0].url` -> `AiProfileImageGenerationResult.imageUrl`。

风险：

- 当前公开页中的 image input 字段需要进一步确认，不确认前不把百度作为第一批图生图主 provider。
- 如果只能稳定文生图，不能满足“保留演员身份”的核心验收。

## 统一错误模型

新增内部错误分类，不改变对外 DTO 结构：

- `CONFIG_MISSING`
- `AUTH_FAILED`
- `RATE_LIMITED`
- `CONTENT_REJECTED`
- `PROVIDER_TIMEOUT`
- `PROVIDER_FAILED`
- `RESULT_EMPTY`
- `RESULT_SAME_AS_SOURCE`
- `RESULT_PERSIST_FAILED`

任务失败时 `failureReason` 写用户可读中文摘要，日志中保留 provider 原始错误码和 requestId。

## 日志与审计

每个生成任务至少记录：

- local taskId。
- providerCode。
- modelCode。
- providerRegion。
- providerRequestId / providerJobId。
- sourceImageUrl hash 或内部对象 key。
- generatedImageUrl。
- startedAt / completedAt / elapsedMs。
- failureCategory / failureReason。
- `aiGenerated=true`。

日志不得写入完整密钥、Authorization、Bearer token、Base64 图片正文。密钥回显接口只记录查看行为，不记录密钥值。

## 标识方案

首版推荐：

- provider 水印按厂商默认或配置执行。
- 小程序详情页和分享图确定性渲染 `AI生成` 标识。
- 存储对象 metadata 或任务表记录 `aiGenerated=true`、provider、model、taskId。

如果产品要求关闭厂商水印，必须先确认项目侧显式标识和隐式追溯信息已经落地。

## 测试策略

- 单元测试：
  - properties binding。
  - registry 解析。
  - 每个 provider 的成功响应解析。
  - 每个 provider 的错误响应解析。
  - URL/base64 结果持久化路径不变。
- 集成测试：
  - 使用真实测试账号跑小样，密钥只通过后台页面录入，不提交到仓库。
  - 10 个演员 x 3 风格 x 目标 provider。
  - 记录耗时、成功率、质量分、单张成本。
- 回归测试：
  - `mvn -q -DskipTests compile`。
  - 现有 `AiProfileCard*Test`。
  - 小程序端无需新增 provider-specific 代码。

## 回滚

- 管理后台把当前主 provider 切回 `kplyyk` 可立即回退旧 provider。
- 如果后台配置表不可用，兜底环境变量 `AI_PROFILE_CARD_PROVIDER_CODE_FALLBACK=kplyyk` 可作为运维恢复路径。
- 新 provider 失败不应影响历史作品展示。
- fallback 策略默认关闭，避免质量不可控时跨 provider 生成不同风格结果。
