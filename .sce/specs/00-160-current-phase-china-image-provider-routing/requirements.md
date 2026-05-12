# 00-160 国内国区生图大模型多 Provider 接入需求

## 开头先回答三个问题

1. 这次解决什么：把 AI 演员资料卡生图从单一 `kplyyk` / `openai` 形态扩展为后台可动态配置的国内国区生图 provider 池，运营/管理员可在管理后台启用厂商、录入密钥、切换当前调用的大模型。
2. 为什么现在做：当前项目已经有后端 `AiProfileImageProvider` 抽象和真实生图任务链路，但缺少国内合规云厂商直连接入、统一配置、灰度、失败回退和供应商验收标准。
3. 不做什么：不让小程序端直连任何生图 API；不把数据库、发布主逻辑沉淀到前端 `src/api/*.ts`；不使用第三方中转站、个人代理站或非官方 API。

## 目标

- 管理后台可直接维护生图 provider 配置，包含启用状态、当前主 provider、模型参数、密钥/API Key，并支持无需重启的动态切换。
- 后端运行时根据后台配置选择当前生图 provider，默认继续允许 `kplyyk`，新增国内官方 provider。
- 首批 provider 目标：
  - `volc-seedream`：火山引擎 / 火山方舟 / 豆包 Seedream 系列。
  - `aliyun-qwen-image` 或 `aliyun-wanxiang`：阿里云百炼千问图像 / 通义万相。
  - `tencent-hunyuan`：腾讯混元生图。
  - `baidu-qianfan`：百度千帆图像生成，作为备选。
- 当前 AI 资料卡合同保持不变：图像模型只生成视觉背景或参考图变体，最终演员姓名、资料、联系方式、二维码、按钮仍由小程序/确定性渲染器负责。
- 生成图片必须持久化到项目自有存储，不能把厂商临时 URL 作为用户最终可见资产。
- 每次生成任务必须可追溯 provider、model、region、requestId/taskId、生成时间、输入来源图、输出图、失败原因和内容安全结果。

## 范围

- 后端：`kaipaile-server/src/main/java/com/kaipai/module/server/ai/**`。
- 配置与密钥管理：后端数据库配置表、密钥加密服务、少量兜底环境变量。
- 后台管理端：`kaipai-admin` 新增 AI 生图 provider 配置页面。
- 文档：`.sce/specs/00-160-current-phase-china-image-provider-routing/`。

## 功能需求

### Provider 选择

- P0 支持管理后台动态选择当前主 provider：
  - `volc-seedream|aliyun-qwen-image|aliyun-wanxiang|tencent-hunyuan|baidu-qianfan|kplyyk|http|openai`
- P0 支持后台保存并立即生效的固定 provider 策略：
  - `fixed`：固定使用一个后台激活的 provider。
- P1 支持更复杂的后台策略：
  - `fixed`：固定使用一个 provider。
  - `style`：按 `templateSceneCode` / `styleCode` 映射 provider。
  - `fallback`：主 provider 失败后按白名单回退。
- provider fallback 只允许在明确可接受的错误上触发，例如超时、限流、临时服务不可用；内容安全拒绝、参考图无授权、输入违规不能回退继续生成。

### Provider 配置

- 每家 provider 独立配置 `enabled`、`endpoint/baseUrl`、`region`、`model`、`version`、`size`、`quality`、`count`、`timeout`、`poll`、`watermark`、`promptRewrite`、`auth`。
- 管理后台允许录入 API Key / SecretId / SecretKey 等密钥，密钥必须加密落库。
- 管理后台允许对具备密钥查看权限的管理员回显密钥明文；默认详情页仍显示脱敏值、配置状态、更新时间和更新人。
- 密钥明文回显必须通过独立的“查看密钥”动作触发，要求二次确认，并写入操作审计。
- 密钥不得写入 Git 仓库、日志、操作记录明细、异常栈、前端 localStorage/sessionStorage；密钥明文只允许出现在受控回显接口响应、当前页面内存状态和调用厂商 API 的内存过程。
- 后端必须通过环境变量提供密钥加密主密钥，例如 `AI_PROVIDER_CONFIG_MASTER_KEY`；如果主密钥缺失，后台密钥保存和 provider 调用必须禁用并报错。
- 后台保存配置时校验当前 provider 必填项；缺失密钥、region、model 或 endpoint 时不允许激活该 provider。
- 配置变更必须有权限控制、操作日志、版本号和回滚能力。

### 后台管理

- 新增管理后台页面：AI 生图模型配置。
- 页面必须支持：
  - provider 列表、启用/停用、设为当前主模型。
  - 每家 provider 的公开参数编辑：endpoint、region、model、version、size、quality、watermark、timeout、poll。
  - 密钥写入：API Key、SecretId、SecretKey、Bearer Token 等字段按 provider 类型展示。
  - 密钥状态展示：已配置/未配置、脱敏尾号、更新时间、更新人。
  - 密钥明文回显：有权限的管理员二次确认后可查看完整密钥。
  - 测试连接/测试生成：用后台指定测试图和提示词进行一次真实 provider 调用。
  - 操作审计：谁在何时修改了哪个 provider、是否查看密钥、是否切换为主模型、测试是否成功。
- 页面不得：
  - 在默认列表/详情态展示完整密钥。
  - 对无密钥查看权限的账号展示完整密钥或复制密钥按钮。
  - 把密钥保存到浏览器本地持久存储。
  - 在失败弹窗里展示厂商返回的 Authorization、签名串或请求正文。

### 请求合同

- 继续使用现有 `AiProfileImageGenerationRequest` 作为 provider 内部统一入参。
- 对所有 provider 发送的数据必须遵守 `docs/ai-profile-card-agent-contract.md` 的数据边界：
  - 可以发送来源图 URL/图片字节、风格提示词、极少量视觉信号。
  - 不得发送 bearer token、手机号、微信号、二维码、私信/联系申请记录、内部审核备注、后台运营字段。
- 对于只支持 URL 的 provider，来源图必须是厂商可访问的公网 HTTPS 地址。
- 对于只支持 Base64 的 provider，后端负责下载来源图并编码，且设置最大文件大小限制。

### 响应合同

- provider 适配器必须把结果统一转换为 `AiProfileImageGenerationResult.imageUrl(...)` 或 `imageBytes(...)`。
- 所有临时 URL 必须立即通过 `AiGeneratedImageStorage` 持久化。
- 若返回多个图片，P0 只取第一张并记录总数；P1 可支持多候选图评审。
- 生成结果不得等于原始参考图；保留当前“不能直接返回原始参考图”的校验。

### 任务与轮询

- 同步 provider 可直接返回结果。
- 异步 provider 必须封装提交任务、轮询任务、超时、失败原因解析。
- provider-specific requestId/taskId 必须记录到任务上下文或日志，方便供应商排障。
- 轮询间隔和最大次数必须可配置。

### 内容安全与质量门

- 输出图必须通过现有质量门要求：
  - 与参考图不同，不是原图回显。
  - 不包含可读中文/英文/数字业务文字、电话、二维码、logo、水印干扰。
  - 关键安全区域没有被主体或复杂纹理覆盖。
- 厂商返回内容安全拒绝时，任务状态必须为 `failed`，错误原因可读。
- 后续可接入二次图片审核，但 P0 至少记录厂商安全错误码和失败信息。

### 合规标识

- 项目必须在最终详情页/分享图中提供确定性的显式 `AI生成` 标识。
- 存储或任务记录中必须保留隐式追溯信息：provider、model、taskId、contentId、generatedAt。
- 供应商自身水印开关由合规/产品决定，不能默认为了美观全部关闭而没有替代标识。

## 需要用户配合提供

- 管理后台密钥录入方式确认：
  - 是否允许超级管理员在页面录入真实 API Key / SecretKey。
  - 已确认密钥可以回显；需要确认哪些角色可查看完整密钥。
  - 是否需要密钥清空/轮换功能。
  - 谁有权限查看 provider 配置、谁有权限修改密钥、谁有权限设为主模型。
- 加密主密钥：
  - 需要在部署环境提供 `AI_PROVIDER_CONFIG_MASTER_KEY`。
  - 主密钥不能放进管理后台，也不能提交到仓库。
  - 若需要多环境一致解密，测试/生产主密钥要分别安全保管。
- 要接入的首批厂商优先级：火山、阿里、腾讯、百度是否都要 POC，还是先做 1-2 家。
- 每家云账号主体和区域选择：
  - 是否使用公司主体账号。
  - 是否要求中国内地地域。
  - 是否已有实名认证、服务开通、免费资源包或预算。
- 厂商密钥材料，不要发到聊天里，后续通过管理后台录入：
  - 火山：API Key、Base URL/地域、模型名、版本号。
  - 阿里：百炼 API Key、地域、模型 ID。
  - 腾讯：SecretId、SecretKey、Region、服务是否已开通、免费资源包是否到账。
  - 百度：API Key/Bearer 凭证、模型 ID、是否确认图生图参数。
- 预算和限额：
  - 免费额度用完是否停止。
  - 单日/单月最大张数。
  - 是否允许后付费。
  - 并发上限。
- 测试样本：
  - 至少 10 个已授权演员样本，每个样本 1-3 张来源图。
  - 至少 3 个风格：`classic`、`costume`、`urban`。
  - 用户确认这些样本可用于第三方云厂商 AI 生成测试。
- 合规材料：
  - 用户协议/隐私政策是否已经覆盖 AI 生成与肖像授权。
  - 小程序上架材料中是否需要列明模型厂商、模型名称、算法备案信息和标识方案。

## 验收标准

- 管理后台可新增/编辑 provider 配置、录入密钥、启用 provider、设为当前主模型。
- 后台录入密钥后，默认列表/详情接口、日志和操作记录均不出现明文密钥。
- 具备密钥查看权限的管理员触发“查看密钥”后，受控回显接口可返回明文密钥，并记录查看审计。
- 后台切换当前主 provider 后，无需重启服务，下一次 AI 资料卡生成使用新 provider。
- 当前主 provider 为任一已启用国内 provider 时，AI 资料卡生成任务可完成并持久化输出图。
- 小程序端无需修改即可展示新 provider 生成的结果。
- `kplyyk`、`http`、`openai` 既有 provider 不被破坏。
- provider 缺配置、认证失败、限流、内容安全失败、轮询超时都返回可读失败原因。
- 单元测试覆盖 provider registry、后台配置解析、密钥加密/脱敏/受控回显、配置校验、至少 2 家 provider 的响应解析。
- 后台密钥查看、测试连接/测试生成接口成功时记录审计；失败时记录失败分类，不记录密钥。
- 集成 POC 至少覆盖 10 个演员样本 x 3 个风格，输出对比表包含成功率、耗时、单张成本、人工质量分、失败原因。
- 生成图页面/分享图有 `AI生成` 显式标识或已记录产品/合规确认的替代方案。

## 官方资料来源

- 火山 Seedream 图片生成编辑：`https://www.volcengine.com/docs/6492/2221472`
- 阿里云百炼图片生成与编辑：`https://help.aliyun.com/zh/model-studio/image-model`
- 阿里云百炼文本生成图像：`https://help.aliyun.com/zh/model-studio/text-to-image`
- 阿里云百炼千问图像编辑：`https://help.aliyun.com/zh/model-studio/qwen-image-edit-guide`
- 腾讯混元生图产品概述：`https://cloud.tencent.com/document/product/1668/86244`
- 腾讯混元生图任务 API：`https://cloud.tencent.com/document/api/1729/105969`
- 腾讯混元生图查询 API：`https://cloud.tencent.com/document/api/1729/105970`
- 百度千帆通用图像生成 API：`https://cloud.baidu.com/doc/qianfan-api/s/8m7u6un8a`
- 生成式人工智能服务管理暂行办法：`https://www.cac.gov.cn/2023-07/13/c_1690898327029107.htm`
- 人工智能生成合成内容标识办法：`https://www.cac.gov.cn/2025-03/14/c_1743654684782215.htm`
