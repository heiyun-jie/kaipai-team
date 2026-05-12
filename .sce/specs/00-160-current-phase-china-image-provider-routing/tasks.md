# 00-160 任务清单

## 开头先回答三个问题

1. 先做什么：先把后台动态配置、密钥加密落库、provider 调查和用户配合清单固化，再做最小 provider 直连接入。
2. 怎么判断做完：管理后台能录入密钥、启用 provider、设为当前主模型；后端无需重启即可调用至少 2 家国内官方 provider，并用真实样本生成、持久化、展示 AI 资料卡图片。
3. 哪些风险要盯：账号密钥、免费额度、厂商临时 URL、内容安全拒绝、图片水印/AI 标识、图生图身份保持质量。

## 1. 用户确认

- [ ] 确认 POC 首批 provider：建议 `volc-seedream` + `aliyun-qwen-image`，腾讯作为对照，百度作为备选。
- [x] 确认“后台配置”为管理后台页面动态切换，并允许在后台页面录入密钥。
- [x] 确认密钥体验：允许后台回显完整密钥。
- [ ] 确认具备密钥查看权限的后台角色。
- [ ] 确认具备密钥修改权限的后台角色。
- [ ] 提供测试云账号；真实密钥后续通过管理后台录入，不写入仓库和聊天。
- [ ] 提供部署环境加密主密钥 `AI_PROVIDER_CONFIG_MASTER_KEY`。
- [ ] 确认是否启用免费额度用完即停、是否允许后付费。
- [ ] 提供 10 个已授权演员样本和 3 个目标风格。
- [ ] 确认 AI 生成显式标识样式和位置。

## 2. 规格与运行文档

- [x] 新建 `requirements.md`。
- [x] 新建 `design.md`。
- [x] 新建 `tasks.md`。
- [x] 新建 `execution.md`。
- [ ] 用户补齐 provider 账号材料后，更新 execution 中的接入决策表。

## 3. 后端配置与密钥管理

- [ ] 新增 `ai_image_provider_config` 数据库迁移。
- [ ] 新增 `ai_image_provider_config_audit` 数据库迁移。
- [ ] 实现 provider 配置实体、Mapper、Service。
- [ ] 实现 `AiProviderSecretCryptoService`，使用 `AI_PROVIDER_CONFIG_MASTER_KEY` 加密/解密密钥。
- [ ] 实现密钥脱敏、普通 DTO 不回显、专用 reveal 接口受控回显明文。
- [ ] 实现 active provider 运行时缓存和配置变更刷新。
- [ ] 生成链路改为从后台 active provider 解析 providerCode/modelCode。
- [ ] 保留 `kplyyk` / 环境变量作为运维兜底回滚。

## 4. 后台管理 API 与页面

- [ ] 后端新增 `/admin/ai/image-providers` 管理接口。
- [ ] 后端新增 provider 公开配置保存接口。
- [ ] 后端新增 provider 密钥保存/清空接口。
- [ ] 后端新增 provider 密钥回显接口，要求独立权限、二次确认和审计。
- [ ] 后端新增 provider 启用/停用/设为主模型接口。
- [ ] 后端新增 provider 测试连接/测试生成接口。
- [ ] 后端为所有配置和密钥操作写操作审计。
- [ ] 数据库迁移补后台权限动作。
- [ ] `kaipai-admin` 新增 AI 生图模型配置页面。
- [ ] 页面支持 provider 列表、配置编辑、密钥写入、密钥回显、测试、设为主模型、停用。
- [ ] 页面保存成功后清空密钥输入框，不持久化到浏览器本地存储。
- [ ] 页面回显密钥只保存在内存状态，关闭弹窗/切换 provider 后清空。

## 5. Provider 实现

- [ ] 实现 `VolcSeedreamProfileImageProvider`。
- [ ] 实现 `AliyunQwenImageProfileImageProvider`。
- [ ] 实现 `TencentHunyuanProfileImageProvider`。
- [ ] 百度先做文档确认；确认图生图字段后再实现 `BaiduQianfanProfileImageProvider`。
- [ ] 每个 provider 统一解析 image URL / base64，并转换为 `AiProfileImageGenerationResult`。
- [ ] 每个 provider 避免日志输出 token、Base64 正文和个人敏感字段。

## 6. 任务追踪与错误分类

- [ ] 在任务或日志中记录 provider requestId/jobId。
- [ ] 增加统一失败分类。
- [ ] 内容安全拒绝不触发 fallback。
- [ ] 临时 URL 持久化失败时任务失败并记录原因。

## 7. 标识与合规

- [ ] 确认详情页/分享图最终 `AI生成` 显式标识落点。
- [ ] 任务记录保留隐式追溯字段。
- [ ] 用户协议/隐私政策补充 AI 生成、肖像授权、第三方云处理说明。
- [ ] 小程序上架材料准备 provider、model、备案/合规资料清单。

## 8. 测试

- [ ] 单元测试覆盖 registry、后台动态配置和兜底 properties。
- [ ] 单元测试覆盖后台配置读取、active provider 选择、密钥加密/解密/脱敏/受控回显。
- [ ] 单元测试覆盖普通接口不回显明文，reveal 接口仅授权账号可回显明文。
- [ ] 单元测试覆盖密钥查看审计不包含密钥值。
- [ ] 单元测试覆盖配置变更后缓存刷新。
- [ ] 单元测试覆盖 provider 成功响应解析。
- [ ] 单元测试覆盖 provider 错误响应解析。
- [ ] 使用 mock HTTP 验证异步轮询超时和失败路径。
- [ ] 真实 POC：10 个演员 x 3 风格 x 2 个 provider。
- [ ] 输出 POC 结果表：成功率、平均耗时、单张成本、质量分、失败原因、是否乱写文字、是否遮挡安全区。

## 9. 发布与回滚

- [ ] 先在测试环境通过后台配置页开启单 provider。
- [ ] 低量灰度真实账号，不开启 fallback。
- [ ] 通过后在生产后台配置并设为主 provider。
- [ ] 保留后台一键切回 `kplyyk`。
- [ ] 保留运维兜底环境变量 `AI_PROFILE_CARD_PROVIDER_CODE_FALLBACK=kplyyk`。
- [ ] 发布后监控失败率、耗时、成本和内容安全拒绝率。
