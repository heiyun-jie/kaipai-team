# 00-199 当前阶段小程序职业资料夹与 DeepSeek 智能导入 - 技术设计

## 1. 设计结论

本轮采用“保留现有核心实体、拆出作品与素材事实源、DeepSeek 只生成候选”的渐进式架构：

```text
pages/mine/index
  -> 职业资料夹入口
     -> pages/actor-profile/edit        核心 / 职业资料
     -> pkg-profile/works/index         不限量作品库
     -> pkg-profile/assets/index        照片 / 视频 / PDF

微信收藏纯文字
  -> pkg-profile/import-review/index
  -> POST /api/ai/profile-import/extract
  -> DeepSeekProfileTextExtractor
  -> CandidateValidator / ConflictResolver
  -> 用户确认
  -> POST /api/actor/profile-import/apply
  -> ActorProfile + ActorExperience 单事务写入

公开档案 / 创建分享 / 分享卡 / AI 分享图
  -> ProfilePresentationResolver
  -> ActorProfile + ActorExperience + ActorMediaAsset + 关系表
```

核心判断：

1. `actor_experience` 已是独立表且后端不限数量；前端 10 条门禁退场即可，不再新建第二套作品主表。
2. 照片、视频、PDF 和经历剧照缺少统一实体，必须新增素材表与明确关系表。
3. 当前 profile PUT 会无条件覆盖标量，并在空 `workExperiences` 时删除全部经历；新页面不能继续依赖该合同保存作品。
4. 当前 AI 润色使用规则适配器且只修改简介 / 经历描述；DeepSeek 导入必须是独立 provider、配置、接口和候选合同。
5. `actor_card_config` 已保存经历 ID 与照片 URL；保留 `experience_id` 可以显著降低作品迁移风险，照片 URL 则需要迁为素材引用。

_Requirements: R1-R151_

## 2. 当前事实与风险

### 2.1 个人档案

当前 `actor_profile` 同时保存：

- 核心标量：昵称、性别、生日、年龄、身高、体重、城市、头像、简介
- 单视频 URL
- 照片 JSON
- 技能 / 风格逗号串
- `extended_field` 中的照片分类、语言、体型、发型、PDF 元数据与 PDF 图片页

`ActorProfileServiceImpl.saveProfile(...)` 当前为全量覆盖语义：

- `name ~ videoUrl` 无条件覆盖
- `workExperiences=[]` 会删除全部 `actor_experience`
- 首次建档携带旧 AI apply meta 会被拒绝

因此本轮必须把档案文字保存、作品保存和 AI 导入应用拆开，不能只调整前端模板。

### 2.2 作品

现有 `actor_experience` 已有：

```text
experience_id / user_id / actor_profile_id
drama_name / role_name / drama_type
shoot_year / shoot_month / platform / role_desc
sort_no / extended_field
```

当前 10 条上限仅存在于 `WorkExperienceSection.vue`。本轮保留物理表名与 `experience_id`，在 Java / API 层引入 `ActorWork` 语义，并为旧 `workExperiences` 提供短期只读投影。

### 2.3 分享配置

当前：

- `actor_card_config.highlighted_experience_ids` 保存作品 ID JSON
- `actor_card_config.highlighted_photo_urls` 保存照片 URL JSON
- `user_share_card.actor_profile_id` 关联档案

作品 ID 可直接迁到新关系表；照片 URL 必须先解析为素材，再建立分享素材关系。

### 2.4 AI 配置

后台已有生图 provider 的：

- 公开配置 JSON
- AES-GCM 密文
- 脱敏回显
- 测试状态
- 操作审计

本轮复用密钥服务、权限与审计模式，但不复用 `ai_image_provider_config` 表，避免文字识别与生图 provider 生命周期耦合。

_Requirements: R32, R44, R64, R99-R109_

## 3. 前端页面与分包

### 3.1 主包保留页

| 路由 | 新职责 |
|---|---|
| `pages/mine/index` | 职业资料夹：账号头部、三个资产入口、创建分享、联系申请、设置 |
| `pages/actor-profile/edit` | 当前头像引用、核心资料、职业资料、自我介绍、智能导入入口 |

不迁移这两个既有路由，避免破坏 tab 与历史跳转。

### 3.2 `pages/actor-profile/edit` UI 与交互合同

档案编辑页采用微信原生分组列表的信息结构。设计参考 WeUI 的 `cell / cell-group / button / actionsheet`、TDesign Miniprogram 的行级表单与底部选择面板、Ant Design Mobile 的原子化移动端表单，但不复制微信绿色品牌色。页面目标是降低首屏密度和重复输入成本，不改变现有档案、草稿、AI 复核与统一保存业务合同。

#### 3.2.1 导航与首屏

```text
白色自定义导航栏
  KpFloatingBackButton       复用项目统一的深色半透明“‹ 返回”胶囊
  个人档案                   居中标题

浅灰页面背景 #F5F5F5
  白色 cell-group
    从复制内容智能填写       标准单元格入口

  白色 cell-group / 核心资料
    头像                     当前头像 + 进入素材库选择
    公开名称                 当前值 / 占位
    性别                     当前值 / 待完善
    年龄、身高               紧凑行级编辑
    当前城市                 当前值 / 待完善

  白色 cell-group
    职业资料                 真实摘要 + 展开入口
    自我介绍                 内容摘要 + 展开入口

固定底部操作区
  保存资料
```

返回按钮必须复用 `KpFloatingBackButton` 的微信胶囊对齐、尺寸和命中区，删除页面私有的单字符 `‹`。导航栏不增加 Hero、渐变背景或第二个大标题。“从复制内容智能填写”保持工具入口层级，不使用营销大卡。首屏不得重新放入照片、视频、作品、PDF、完成度或提升建议。

#### 3.2.2 展开编辑与标签操作

- 职业资料点击后在当前页面原位置展开，编辑体重、籍贯、院校、专业、语言 / 方言、职业特长、人物类型 / 戏路和职业能力。
- 自我介绍点击后在当前页面原位置展开文本编辑；允许职业资料和自我介绍同时保持展开，不采用“只能一个分组展开”的状态机。
- 语言 / 方言、职业特长、人物类型 / 戏路等标签字段打开底部多选面板；面板顶部使用 `12-16px` 圆角和轻微上投影，选择结果只写入当前页面草稿。
- 头像、核心资料、职业资料、自我介绍和标签共用一份页面草稿，最后只由底部“保存资料”提交；不新增编辑路由，不把照片、视频、作品或 PDF 重新放回档案页。

#### 3.2.3 页面状态与反馈

- 首次无档案：直接进入空表单，使用 `profileVersion=0`，不展示“演员档案不存在”错误弹窗。
- 加载中：显示列表骨架或“正在读取档案”，保存按钮不可用。
- AI 识别完成：显示待确认数量；候选、性别推断和冲突项必须先复核，不能静默写入正式值。
- 保存中：底部按钮锁定并显示“保存中…”。保存成功后只显示短 Toast“资料已保存”，停留当前页。
- 真实网络 / 服务异常：使用页内错误与“重新加载”；仅用户主动保存失败使用 Toast。
- 未保存返回：调用原生操作表，提供“保存资料并返回 / 放弃修改 / 继续编辑”。

#### 3.2.4 视觉 Token

| Token | 值 |
|---|---|
| 页面底色 | `#F5F5F5` |
| 分组背景 | `#FFFFFF` |
| 主文字 | `#191919` |
| 主按钮 | `#242424` |
| 分割线 | `#EDEDED` |
| 页面分组 | 无圆角、无阴影、无渐变 |
| 按钮 | `6-8px` 圆角 |
| 底部选择层 | 顶部 `12-16px` 圆角、轻微上投影 |
| 布局 | 分组间距约 `12px`，行高 `48-56px`，左右边距约 `16px` |
| 字级 | 页面标题 `16-17px`，行标题 `15-16px`，说明 `12-13px` |

表单区不使用大号衬线标题；页面不使用渐变、装饰性阴影或卡片堆叠。

_Requirements: R21-R31h, R124, R129, R133-R136, R148-R150_

### 3.3 新增 `pkg-profile` 分包

| 路由 | 职责 |
|---|---|
| `pkg-profile/import-review/index` | 原文预览、识别进度、候选分组、冲突与应用 |
| `pkg-profile/works/index` | 搜索、筛选、代表作、导入、删除保护 |
| `pkg-profile/work-edit/index` | 单条作品编辑、局部 AI 润色、关联素材 |
| `pkg-profile/assets/index` | 照片 / 视频 / PDF 上传、分类、引用与删除保护 |

`pages.json` 新增 subPackage root：

```json
{
  "root": "pkg-profile",
  "pages": [
    { "path": "import-review/index", "style": { "navigationStyle": "custom" } },
    { "path": "works/index", "style": { "navigationStyle": "custom" } },
    { "path": "work-edit/index", "style": { "navigationStyle": "custom" } },
    { "path": "assets/index", "style": { "navigationStyle": "custom" } }
  ]
}
```

现有工具分包新增：

| 路由 | 职责 |
|---|---|
| `pkg-tools/settings/index` | 消息通知、偏好设置、用户协议、隐私政策、关于和退出登录的统一设置目录 |

`pages/history/index` 从单一浏览历史改为 `浏览记录 / 收藏` 分段视图；现有 `pkg-card/favorites/index` 在迁移期只承担兼容跳转，正式入口和数据展示归并到“记录”。

### 3.3 状态与类型层

新增 / 调整：

```text
src/types/profile.ts               核心 / 职业档案
src/types/actor-work.ts            作品、代表作、筛选
src/types/actor-asset.ts           素材、引用、处理状态
src/types/profile-import.ts        候选、证据、冲突、应用
src/api/profile-import.ts          capability / extract / apply
src/api/actor-work.ts              作品 CRUD / 代表作
src/api/actor-asset.ts             素材查询 / 关系操作
src/stores/profile-import.ts       当次结构化候选内存草稿
```

`profile-import` store 不保存原文到持久化 storage；页面栈内允许保留候选与用户选择，应用或退出后清空。

_Requirements: R1-R31, R124-R137_

## 4. 个人中心设计

### 4.1 登录态

```text
账号头部
  头像 / 公开名称
  当前城市 · 演员账号 · 用户 ID
我的资料
  个人档案  核心状态 / 职业资料数量
  作品库    作品总数 / 代表作数量
  素材库    照片 / 视频 / 当前 PDF
常用功能
  创建分享
  联系申请  待处理 badge
  设置
```

当前城市缺失时省略该段，不显示 `--`。账号摘要的用户 ID 来自真实 session，不根据手机号或档案字段拼造。

不再请求旧页面为伪数据卡而并发调用的卡片、浏览历史与能力推算数据。页面只请求职业资料夹摘要接口，或由三个领域接口的轻量 summary 合并输出。

后端聚合接口：

```http
GET /api/actor/career-hub/summary
```

返回：

```json
{
  "profile": { "coreReady": true, "careerFieldCount": 8 },
  "works": { "total": 29, "representativeCount": 6 },
  "assets": { "photoCount": 14, "videoCount": 3, "hasCurrentResume": true },
  "pendingContactRequests": 2
}
```

### 4.2 游客态

游客只消费全局 session，不请求 summary。三个资产入口显示名称，不显示数量；点击账号能力时复用统一登录门禁。设置中的协议 / 隐私 / 关于继续允许游客访问。

### 4.3 记录与设置归并

- `pages/history/index` 使用分段控制切换浏览记录与收藏，两类数据保持各自真实 API，不把收藏伪装为浏览记录。
- 收藏使用 `share_card_favorite` 作为唯一事实源；公开分享详情页显示登录后可用的收藏 / 取消收藏操作，记录页只读取真实收藏关系。
- `pkg-tools/settings/index` 只做设置目录；协议、隐私、关于、通知和偏好继续复用现有本地工具内容。
- 游客可从设置目录进入协议、隐私和关于；通知、偏好中的账号级能力若需要 token，必须在动作发生时登录。
- 退出登录只在已登录态显示。

_Requirements: R1-R20_

## 5. 个人档案模型

### 5.1 `actor_profile` additive 字段

新增：

```text
avatar_asset_id                    BIGINT NULL
current_resume_asset_id            BIGINT NULL
birth_year                         SMALLINT NULL
birth_month                        TINYINT NULL
birth_day                          TINYINT NULL
birth_precision                    VARCHAR(16) NULL   year / month / day
origin_place                       VARCHAR(128) NULL
school_name                        VARCHAR(128) NULL
major_name                         VARCHAR(128) NULL
language_tags_json                 JSON NULL
specialty_tags_json                JSON NULL
role_type_tags_json                JSON NULL
professional_ability_tags_json     JSON NULL
work_library_version               BIGINT NOT NULL DEFAULT 0
```

说明：

- 继续复用现有 `weight`。
- `locationCity` 继续表达当前城市，`origin_place` 单独表达籍贯。
- 现有 `birthday` 在迁移期保留；只有 `birth_precision=day` 时才能生成完整生日。
- `2004.9` 写为 `birth_year=2004 / birth_month=9 / birth_day=NULL / birth_precision=month`。
- `age` 作为兼容展示值可由服务端按出生精度计算，但不得反推虚假日期。
- `avatar_url` 在迁移期保留兼容投影；新写路径以 `avatar_asset_id` 为事实源。
- `current_resume_asset_id` 是“每个档案最多一份当前简历”的唯一事实源；设置时必须校验素材属于本人、类型为 PDF 且状态为 ready。
- 继续使用 BaseEntity 的 `version` 作为档案乐观锁版本；`work_library_version` 在作品增删改、合并、删除和代表作重排时递增。

### 5.2 保存 DTO

档案编辑页只暴露一个组合保存 DTO：

```text
ActorProfileMineUpdateDTO
  expectedProfileVersion
  avatarAssetId
  core
  career
  intro
ActorProfileRespDTO
```

头像选择、核心资料、职业资料和自我介绍先保留在前端同一页面草稿，点击“保存资料”后由一个事务完成。档案保存不再携带作品、照片、视频和 PDF 数组。

旧 `ActorProfileSaveDTO` 只供旧客户端兼容。新事实源启用后，旧接口对 `workExperiences / photos / video / PDF` 无论是字段缺失、空数组、最多 10 条截断数组还是其他非空值都不得再执行替换写入；只允许更新兼容核心标量，或按最低客户端版本门禁返回升级错误。

_Requirements: R21-R31, R78-R85, R100-R109_

## 6. 作品库模型

### 6.1 原地扩展 `actor_experience`

新增字段：

```text
publish_status          VARCHAR(32) NULL
work_type_code          VARCHAR(32) NULL
role_level_code         VARCHAR(32) NULL
sync_sound_status       VARCHAR(16) NULL
collaborators_json      JSON NULL
achievement_text        TEXT NULL
normalized_drama_name   VARCHAR(255) NOT NULL DEFAULT ''
normalized_role_name    VARCHAR(255) NOT NULL DEFAULT ''
dedupe_key              VARCHAR(128) NOT NULL DEFAULT ''
active_dedupe_key       VARCHAR(128) NULL
source_type             VARCHAR(32) NOT NULL DEFAULT 'manual'
```

兼容关系：

- `drama_name` -> 项目名
- `role_name` -> 角色名
- `drama_type` -> 旧类型兼容值
- `role_desc` -> 作品描述
- `platform` -> 播出平台
- `experience_id` 保持不变

`dedupe_key` 由 `normalized_drama_name + normalized_role_name` 生成稳定哈希，用户范围由复合唯一键表达；服务层对空角色名和别名归一化进行稳定处理。`active_dedupe_key` 定义为 `CASE WHEN deleted=0 THEN dedupe_key ELSE NULL END` 的 stored generated column，并建立 `(user_id, active_dedupe_key)` 唯一索引，利用 MySQL 多 NULL 语义防止并发重复且兼容多条历史删除记录。

### 6.2 代表作表

```sql
actor_profile_representative_work (
  relation_id BIGINT PRIMARY KEY,
  actor_profile_id BIGINT NOT NULL,
  experience_id BIGINT NOT NULL,
  sort_no INT NOT NULL,
  ...BaseEntity
)
```

约束：

- `(actor_profile_id, experience_id)` 唯一
- `(actor_profile_id, sort_no)` 唯一
- 服务层最多 6 条
- 必须校验作品属于同一用户 / 档案

_Requirements: R32-R43, R105-R108_

### 6.3 分享收藏关系

```sql
share_card_favorite (
  favorite_id BIGINT PRIMARY KEY,
  user_id BIGINT NOT NULL,
  share_card_id BIGINT NOT NULL,
  active_share_card_id BIGINT GENERATED ALWAYS AS
    (CASE WHEN deleted = 0 THEN share_card_id ELSE NULL END) STORED,
  ...BaseEntity
)
```

约束：

- `(user_id, active_share_card_id)` 唯一，收藏和取消收藏均为幂等操作。
- `share_card_id` 必须解析到 active `user_share_card.share_card_id`；持有人不能收藏自己的分享卡。
- 收藏列表复用当前分享卡历史项所需的公开摘要字段，但不借用浏览历史表，也不从前端硬编码构造空数据。
- 本轮不迁移历史收藏，因为现有收藏页从未写入可信业务记录。

_Requirements: R10, R38-R39, R106-R109_

## 7. 素材模型

### 7.1 素材表

```text
actor_media_asset
  asset_id
  user_id
  media_type              photo / video / pdf
  category_code
  storage_provider
  bucket_code
  object_key
  thumbnail_object_key
  original_name
  mime_type
  size_bytes
  duration_ms
  page_count
  process_status           uploading / processing / ready / failed
  failure_code
  failure_message
  source_type              upload / migration
  ...BaseEntity
```

新素材记录本身不表达“公开”。底层对象使用私有 Bucket / 私有 ACL；数据库保存对象定位，不保存永久可公开访问 URL。公开资格只能来自明确关系。

### 7.2 PDF 页表

```text
actor_media_asset_page
  page_id
  asset_id
  page_no
  image_object_key
  process_status
  ...BaseEntity
```

PDF 页不再塞入 profile JSON，继续复用现有 PDFBox 转换和顺序校验。

### 7.3 明确关系表

```text
actor_profile_asset
  actor_profile_id / asset_id / usage_code / sort_no
  usage_code: public_photo / public_video / public_resume

actor_work_asset
  experience_id / asset_id / usage_code / sort_no
  usage_code: still / clip

share_card_work
  share_card_id / experience_id / sort_no

share_card_asset
  share_card_id / asset_id / usage_code / sort_no
  usage_code: cover / gallery / video / resume
```

`share_card_work / share_card_asset.share_card_id` 明确引用 `user_share_card.share_card_id`，不引用 `actor_card_config.config_id`。

头像和当前简历分别使用 `actor_profile.avatar_asset_id / current_resume_asset_id`，避免通用关系表表达两个单值状态。当前简历是否公开由独立 `public_resume` 关系决定，设置“当前”本身不等于公开。

`actor_profile_asset.usage_code=public_resume` 必须引用当前 `current_resume_asset_id`；历史 PDF 若仅供某张分享卡使用，只建立 `share_card_asset` 关系，不伪装成公开档案当前简历。

每张关系表必须有：

- 目标归属校验
- 复合唯一键
- `deleted=0` 查询索引
- 删除引用保护

### 7.4 素材访问 URL

- 所有者预览接口在校验 token 与 asset owner 后返回短时 `accessUrl`。
- 公开档案 / 分享卡 resolver 只有在找到明确公开关系后才签发对应场景的短时 `accessUrl`。
- 签名 URL 过期后由页面按 asset ID 重新请求，不把签名 URL 持久化回数据库。
- 历史公开 URL 在迁移期复制到私有对象键；完成复制和关系核对前不删除旧对象。

_Requirements: R44-R59, R106-R109_

## 8. DeepSeek 配置与 provider

### 8.1 配置表

```text
ai_profile_import_config
  config_id
  provider_code            固定 deepseek
  display_name
  enabled
  endpoint
  model_name
  connect_timeout_ms
  read_timeout_ms
  max_input_chars
  max_output_tokens
  per_user_daily_limit
  secret_config_ciphertext
  secret_mask_json
  last_test_status / message / at
  ...BaseEntity
```

只允许一条未删除 `deepseek` 配置。密钥复用 `AiProviderSecretCryptoService`，但配置服务、DTO、权限和表保持独立。

### 8.2 配置审计

```text
ai_profile_import_config_audit
  audit_id / config_id / action_code
  before_public_config_json / after_public_config_json
  before_secret_mask_json / after_secret_mask_json
  operator_id / operator_name
  result_status / message
  ...BaseEntity
```

动作至少覆盖：`public_config_update / secret_update / enable / disable / test`。

### 8.3 调用审计

```text
ai_profile_import_request_audit
  audit_id / request_id / user_id / config_id / model_name
  status / input_length / candidate_count / work_count / conflict_count
  elapsed_ms / error_code / applied_at
  apply_payload_sha256 / apply_status / apply_result_summary_json
  ...BaseEntity
```

禁止列：原文、完整模型响应、完整证据片段、API Key。

必须建立 `(user_id, request_id)` 唯一键。apply 对该审计行加行锁：相同 payload 哈希的成功重试返回首次结果摘要，不同 payload 复用同一 requestId 返回 `PROFILE_IMPORT_REQUEST_REUSED`。

### 8.4 Provider 接口

```java
public interface ProfileTextExtractor {
    ProfileImportExtraction extract(ProfileImportExtractionRequest request);
}

public final class DeepSeekProfileTextExtractor implements ProfileTextExtractor {
    // HTTP call, structured JSON parsing, one bounded repair retry
}
```

不提供规则型 fallback。DeepSeek 不可用时返回稳定错误码并保留手动编辑路径。

_Requirements: R60-R73, R88-R99, R131-R137_

## 9. 提取合同

### 9.1 请求

```http
POST /api/ai/profile-import/extract
```

```json
{
  "rawText": "演员王火火...",
  "scene": "full_profile",
  "contextVersion": {
    "profileVersion": 3,
    "workLibraryVersion": 12
  }
}
```

`scene` 只允许：

- `full_profile`：提取档案与作品，apply 前要求补齐核心必填。
- `works_only`：只应用作品；不要求头像、性别或当前城市。若用户尚无 `actor_profile` 行，事务内创建不可公开的最小档案壳；`coreReady` 继续由字段完整性动态计算，不新增并行真值字段。

`contextVersion` 必填。首次无档案时使用 `profileVersion=0 / workLibraryVersion=0`。

服务端流程：

1. 登录校验，不做实名门禁。
2. capability 与用户限额校验。
3. 输入长度和空文本校验。
4. 读取当前档案与作品摘要，用于冲突 / 重复匹配。
5. 构造字段白名单和 JSON schema prompt。
6. 调用 DeepSeek。
7. 解析 JSON；失败时一次 repair retry。
8. 服务端范围、枚举、证据、数字与重复项校验。
9. 写脱敏请求审计。
10. 原文与完整响应离开请求作用域后释放。

### 9.2 响应

```json
{
  "requestId": "profile_import_req_20260723_0001",
  "summary": {
    "profileCandidateCount": 12,
    "workCandidateCount": 29,
    "conflictCount": 4,
    "ignoredMediaPlaceholderCount": 18
  },
  "profileCandidates": [
    {
      "candidateId": "profile_gender_001",
      "fieldKey": "gender",
      "candidateValue": "female",
      "confidence": 0.86,
      "sourceText": "女主 / 女二 / 女反一",
      "sourceType": "inferred_from_roles",
      "warning": "根据多条作品角色推断，请确认",
      "selected": false,
      "requiresExplicitConfirmation": true,
      "confirmed": false,
      "conflict": null
    }
  ],
  "workCandidates": [
    {
      "candidateId": "work_001",
      "matchStatus": "field_conflict",
      "matchedExperienceId": 1024,
      "selectedAction": "skip",
      "fields": {
        "projectName": {
          "candidateValue": "绝不回头，白爷宠她成瘾",
          "confidence": 0.99,
          "sourceText": "《绝不回头，白爷宠她成瘾》女二 程雪(同期声)",
          "sourceType": "explicit"
        }
      },
      "conflicts": [
        {
          "fieldKey": "achievementText",
          "existingValue": "爱奇艺飙升榜No1",
          "candidateValue": "爱奇艺飙升榜No1 虐恋榜No2",
          "sourceText": "爱奇艺飙升榜No1 虐恋榜No2"
        }
      ]
    }
  ],
  "unmappedSegments": [],
  "warnings": []
}
```

### 9.3 性别推断

允许条件：

- 至少两条独立、同方向角色证据；或一条明确的自我身份描述加角色证据
- 不存在反向强证据
- 返回 `sourceType=inferred_from_roles`
- 返回 `requiresExplicitConfirmation=true / selected=false / confirmed=false`
- 前端始终展示独立确认动作；后端 apply 拒绝未确认的推断候选

禁止：

- 姓名推断
- 头像风格推断
- 院校 / 专业推断
- 写入实名字段

### 9.4 部分生日

DeepSeek 返回：

```json
{
  "birthYear": 2004,
  "birthMonth": 9,
  "birthDay": null,
  "birthPrecision": "month"
}
```

后端按当前日期生成 `age` 候选，但保留推导警告；不写 `2004-09-01`。

_Requirements: R60-R87, R138-R145_

## 10. 冲突、重复与应用

### 10.1 前端默认选择

| 场景 | 默认行为 |
|---|---|
| 当前字段为空、证据明确 | 选中 |
| 当前字段与候选相同 | 无需修改 |
| 当前字段与候选冲突 | 不选中，展示对比 |
| 低置信或证据不足 | 不选中 |
| 多条一致女性角色证据 | 默认不选中；执行独立确认后才可选中 |
| 籍贯存在、当前城市为空 | 只填籍贯，城市继续缺失 |

### 10.2 作品去重

标准化步骤：

- Unicode / 空白归一化
- 去除书名号、尾部标点和非语义装饰符
- 项目名保留原文用于展示，另生成 normalized 值
- 角色名同样归一化
- 同用户范围生成 `dedupe_key`

匹配结果：

```text
exact_match      跳过
field_conflict   默认跳过，用户确认逐字段最终值后改为 merge
new              默认新增
ambiguous        默认跳过
```

### 10.3 原子应用

```http
POST /api/actor/profile-import/apply
```

请求携带：

- `requestId`
- `scene: full_profile / works_only`
- `contextVersion: profileVersion + workLibraryVersion`
- 用户最终确认的档案候选：`candidateId / fieldKey / finalValue / confirmed`
- 作品操作：`candidateId / selectedAction / matchedExperienceId / finalFields / confirmedConflictFields`
- `full_profile` 场景的当前头像素材 ID

服务端：

1. 锁定 `(request_id, user_id)` 审计行，计算 canonical payload SHA-256。
2. 校验 `contextVersion`；提取后若档案或作品库已变化，返回版本冲突并要求刷新对比。
3. 重新校验枚举、数值、素材归属、作品归属、合并目标与所有推断字段的显式确认。
4. `full_profile` 校验核心必填；`works_only` 只校验作品并允许创建未完成档案壳。
5. 在一个事务中创建 / 更新 profile、执行 create / merge / skip、更新版本与 apply audit。
6. 利用作品 active 去重唯一键处理并发；唯一冲突转为精确重复 / 合并结果，不重试插入第二条。
7. 相同 requestId + 相同 payload 的成功重试返回首次 `applyResult`；不同 payload 复用同一 requestId 明确拒绝。
8. 首次建档允许使用本 apply，不复用旧 AI resume apply meta。
9. 成功后记录 `applied_at`，不保存原始文本、完整候选或证据片段。

`full_profile` 中若头像、性别或当前城市仍缺失，apply 返回字段级错误；候选继续保留在前端页面栈内，用户可补齐后重试。`works_only` 不执行这组门槛。

_Requirements: R74-R87, R100-R103_

## 11. 业务 API

### 11.1 Career Hub

```http
GET /api/actor/career-hub/summary
```

### 11.2 Profile

```http
GET /api/actor/profile/mine
PUT /api/actor/profile/mine
```

`PUT /api/actor/profile/mine` 一次提交头像、核心、职业资料和自我介绍，并用 `expectedProfileVersion` 做乐观锁。

尚无 `actor_profile` 行时，读取接口返回 HTTP 200 和空草稿，版本固定为 `profileVersion=0 / workLibraryVersion=0`；首次 `PUT` 仅接受 `expectedProfileVersion=0` 并在同一事务中创建档案。前端不得通过吞掉“演员档案不存在”错误模拟空态。

旧 `PUT /api/actor/profile` 在兼容期保留，但新事实源启用后永远不得再写作品和素材域：集合字段缺失或为空时只视为 no-op；出现任何非空旧集合时返回 `PROFILE_LEGACY_COLLECTION_WRITE_RETIRED` 并提示升级，不静默丢弃用户意图。对无法安全兼容的旧客户端执行最低版本门禁。

### 11.3 Works

```http
GET    /api/actor/works
POST   /api/actor/works
GET    /api/actor/works/{id}
PUT    /api/actor/works/{id}
DELETE /api/actor/works/{id}
PUT    /api/actor/works/representatives
PUT    /api/actor/works/{id}/assets
```

### 11.4 Assets

现有上传接口继续负责对象存储；素材服务负责元数据、处理状态和引用：

```http
GET    /api/actor/assets
POST   /api/actor/assets
GET    /api/actor/assets/{id}
PUT    /api/actor/assets/{id}
DELETE /api/actor/assets/{id}
PUT    /api/actor/assets/current-resume
POST   /api/actor/assets/{id}/access-url
```

公开页面不直接调用所有者 access-url；由公开档案 / 分享 resolver 按明确引用签发场景化短时 URL。

### 11.5 DeepSeek capability

```http
GET  /api/ai/profile-import/capability
POST /api/ai/profile-import/extract
```

### 11.6 Admin

```http
GET  /api/admin/ai/profile-import/config
PUT  /api/admin/ai/profile-import/config
PUT  /api/admin/ai/profile-import/secret
POST /api/admin/ai/profile-import/test
PUT  /api/admin/ai/profile-import/enabled
GET  /api/admin/ai/profile-import/audits
```

_Requirements: R88-R109_

### 11.7 Favorites

```http
GET    /api/card/favorites
PUT    /api/card/{shareCardId}/favorite
DELETE /api/card/{shareCardId}/favorite
```

收藏列表只返回 active、当前用户有权重新打开的分享卡摘要；收藏操作要求登录，取消收藏对不存在的 active 关系返回幂等成功。

_Requirements: R10, R14-R20_

## 12. 后台页面

新增系统设置子入口：

```text
/system/ai-profile-import
```

页面职责：

- provider / model / endpoint
- 超时、长度、token 与用户限额
- API Key 脱敏保存
- 启用 / 停用
- 测试连接
- 最近测试结果
- 配置审计

该路由作为系统设置下的隐藏子页，不增加正式一级导航。权限固定为：

```text
system:ai-profile-import:view
system:ai-profile-import:update
system:ai-profile-import:secret
system:ai-profile-import:test
system:ai-profile-import:audit
```

_Requirements: R88-R99_

## 13. 数据迁移

### 13.1 Phase A：Inspect

输出脱敏基线：

- profile 总数
- 非空头像、照片 JSON、视频、PDF 数
- PDF 页总数
- actor_experience 总数
- 经历照片总数
- share card highlighted experience / photo 引用数
- extended JSON 解析失败 ID 清单

王火火测试账户单独输出可恢复快照，但不得把原始微信收藏文本写入迁移样本。

### 13.2 Phase B：Additive DDL

- actor_profile 新列
- actor_experience 新列
- representative / asset / asset page / relation tables
- DeepSeek config / config audit / request audit tables
- 迁移映射与异常表

不删除旧列。

### 13.3 Phase C：Backfill

1. 头像 URL -> photo asset -> `avatar_asset_id`
2. `photo_urls / photoCategories` -> photo assets -> profile public relations
3. `video_url` -> video asset -> profile public relation
4. PDF metadata / page URLs -> PDF asset / pages -> current resume relation
5. actor_experience extended photos -> photo assets -> work relations
6. actor_experience 补 normalized / dedupe / source 字段
7. highlighted experience IDs -> `share_card_work`
8. highlighted photo URLs -> `share_card_asset`

历史公开素材复制到私有对象键并建立 public / share 关系；新上传素材默认不建立关系。迁移映射保存 legacy URL / object locator 到新 asset ID，但正式读取不再把 legacy URL 当权限边界。

`share_card_favorite` 是本轮新增关系表，不回填虚构历史收藏。

### 13.4 Phase D：Read Switch

按顺序切换：

1. 新职业资料夹与编辑页
2. 作品库 / 素材库
3. 创建分享
4. 公开页 / 作品集
5. 卡片预览 / 海报预览
6. AI 分享图 prompt / PDF 内容流
7. 完成度 / 实名 / 等级消费者

### 13.5 Phase E：Write Stop 与退场

- 禁止新接口写旧数组 / JSON
- 旧 DTO 只读投影短期保留
- 最低客户端版本或兼容适配生效后停止旧 profile PUT 写旧域
- 独立 Spec 审计旧列、旧组件、旧脚本和旧 API 删除

_Requirements: R110-R123_

## 14. 错误码与恢复

稳定错误码采用现有 `R<T>.code` 数值合同，统一落在 `46001-46017` 区间；前端请求层必须把数值 code 保留到 `ApiError`，资料导入页面只映射该数值，不通过中文 message 判断状态。

| 数值 code | 语义名 |
|---:|---|
| 46001 | `PROFILE_IMPORT_DISABLED` |
| 46002 | `PROFILE_IMPORT_UNAVAILABLE` |
| 46003 | `PROFILE_IMPORT_INPUT_EMPTY` |
| 46004 | `PROFILE_IMPORT_INPUT_TOO_LONG` |
| 46005 | `PROFILE_IMPORT_RATE_LIMITED` |
| 46006 | `PROFILE_IMPORT_MODEL_TIMEOUT` |
| 46007 | `PROFILE_IMPORT_RESPONSE_INVALID` |
| 46008 | `PROFILE_IMPORT_APPLY_CONFLICT` |
| 46009 | `PROFILE_IMPORT_REQUEST_REUSED` |
| 46010 | `PROFILE_IMPORT_CONTEXT_VERSION_CONFLICT` |
| 46011 | `PROFILE_IMPORT_CONFIRMATION_REQUIRED` |
| 46012 | `PROFILE_ASSET_NOT_FOUND` |
| 46013 | `PROFILE_ASSET_NOT_READY` |
| 46014 | `PROFILE_ASSET_IN_USE` |
| 46015 | `PROFILE_WORK_DUPLICATE` |
| 46016 | `PROFILE_WORK_IN_USE` |
| 46017 | `PROFILE_LEGACY_COLLECTION_WRITE_RETIRED` |

语义名仅用于后端枚举、前端集中映射和审计；HTTP 响应维持现有数值 `code + message` 结构。

恢复规则：

- extract 失败：保留原文与用户编辑
- partial success：展示已识别项，不包装为整体失败
- apply 字段错误：定位字段，保留候选
- apply 版本冲突：刷新当前值后重新显示对比
- requestId 已被不同 payload 使用：拒绝写入并要求重新识别
- 素材上传失败：保留失败记录和重试
- 删除引用冲突：展示引用方并引导解除 / 替换

_Requirements: R55, R69, R73, R76-R87, R129-R137_

## 15. 安全与隐私

- DeepSeek API Key 只在后端解密使用。
- HTTP client 日志禁止输出 Authorization 和 body。
- 原始文本、完整响应、证据片段只存在请求内存与前端当次页面内存。
- 错误治理只存脱敏统计，不存用户原文。
- 即使业务确认常规输入不含身份证号、口令或精确地址，后端仍按字段白名单拒绝写入未知敏感字段。
- 公开接口只返回存在明确公开关系的素材。
- 新素材对象使用私有存储；所有者和公开访问分别由鉴权 / 引用校验后签发短时 URL。
- 用户只能引用自己拥有且 ready 的素材 / 作品。
- 管理员测试连接不得复用用户样本或写业务表。

_Requirements: R51-R59, R66-R70, R88-R99, R131-R137_

## 16. 测试设计

### 16.1 后端 TDD

- profile 局部保存不删除作品 / 素材
- 旧 profile PUT 对字段缺失、空数组、10 条截断数组和非空旧数组都不再替换作品 / 素材
- 组合档案保存原子性与 profile 乐观锁
- actor_experience 不限量与去重
- active 去重唯一键的并发创建与逻辑删除重建
- 代表作最多 6 条
- 收藏 add / remove 幂等、不能收藏自己、失效分享卡过滤和记录页真实列表
- 素材归属、ready 状态与删除引用保护
- PDF 多版本 + 单 current
- DeepSeek capability / 配置 / 密钥 / 测试审计
- JSON 解析、repair retry、超时、限流
- 部分生日与年龄推算
- 籍贯 / 当前城市隔离
- 角色证据性别推断
- extract 不写业务数据
- apply 事务与幂等
- contextVersion 冲突、requestId payload 哈希冲突和成功重试结果复用
- 原文不落库、不入日志
- 私有对象、所有者签名 URL、公开引用签名 URL 与过期重签
- 迁移重复执行、异常隔离和回滚

### 16.2 前端 TDD / 静态门禁

- mine 不再包含 analytics / QR / header edit
- 游客不请求账号数据
- 三个资产入口与常用功能层级
- 档案页不再包含作品 / 照片 / 视频 / PDF 上传器
- 头像只从素材库选择
- 剪贴板必须用户主动触发
- 候选分组、冲突默认不覆盖、推断证据展示
- 推断性别默认未选中，未执行独立确认不能提交
- 29 条作品分组渲染不破版
- 未保存离开提醒
- 删除引用保护反馈
- 记录页浏览 / 收藏分段与统一设置页
- 公开分享页收藏 / 取消收藏的登录门禁与刷新反馈

### 16.3 固定样本

王火火测试账户使用脱敏、规范化的 golden fixture，验证：

- 公开名称、170cm、45kg、2004.9、院校 / 专业
- 粤语、英语、东北话、普通话
- 人物类型、同期声、台词、威亚等职业能力
- 约 29 条作品及已播 / 待播 / 舞台 / 横屏分类
- 榜单 / 热度 / 播放量原文保持
- 性别推断为 female 候选并要求确认
- 籍贯不覆盖当前城市
- `[图片] / [视频]` 不建素材
- 重复导入幂等

fixture 不保存用户原始剪贴板正文、真实媒体、手机号、Token 或账号凭据。确定性字段与作品验收优先使用 mock extractor / golden response；真实 DeepSeek 仅在后台配置完成后使用运行时注入文本执行受控 smoke。

### 16.4 工程与运行态

```text
后端专项测试
后端 clean package
前端 type-check
前端 build:mp-weixin
前端 audit:steering
前端 audit:mp-package
src / dist/build / dist/dev 核对
微信开发者工具运行态与截图复核
```

_Requirements: R138-R151_

## 17. 条款接管矩阵

| 旧 Spec | 接管范围 | 保留范围 |
|---|---|---|
| `00-73` | mine 的旧 MyScreen 数据卡、二维码、编辑、设置合同 | 其他 6 屏、视觉 token、safe-area、证据门禁 |
| `00-144` | mine UI / IA 评分基线 | 95 分、四层证据、低分继续修改 |
| `00-190` | 游客旧内容区 / 二维码 / 旧设置脚本断言 | 不强登、按动作登录、全局 session |
| `03-04` | 档案页头像上传、照片、视频、作品、全量保存 | 核心必填与手动编辑原则 |
| `05-02` | 10 条经历、照片分类、完整度运营、预览按钮 | 有效职业资料语义 |
| `05-04` | 全局 AI 入口位置 | 显式确认、不捏造、失败不写入、局部润色 |
| `05-13` | PDF 入口、事实源、默认公开 | 校验、转换、有序页、失败闭锁 |
| `05-19` | 档案页照片入口与旧数组事实源 | 不限量照片语义、单卡版式选择上限 |
| `00-27 / 00-05` | 新增 `pkg-profile` | 主包 / 现有分包及 2 MB 治理 |
| `00-69` | 个人中心保留项 | 真实分享 analytics 域 |

额外消费者：`00-63 / 00-64 / 00-161 / 00-171 / 00-172 / 05-05 / 05-15` 必须在实现任务中完成新事实源切换。

`03-05` 的个人中心旧菜单合同一并由本 Spec 接管；`00-191 / 00-192` 的账号头部优先渲染、附属同步失败不降级和全局 session 唯一事实源继续保留。

_Requirements: R1-R151_

## 18. 影响文件（计划）

### 前端

- `kaipai-frontend/src/pages/mine/index.vue`
- `kaipai-frontend/src/pages/history/index.vue`
- `kaipai-frontend/src/pages/actor-profile/edit.vue`
- `kaipai-frontend/src/pages.json`
- `kaipai-frontend/src/pkg-profile/**`
- `kaipai-frontend/src/pkg-tools/settings/index.vue`
- `kaipai-frontend/src/pkg-card/favorites/index.vue`
- `kaipai-frontend/src/pages/actor-profile/detail.vue`
- `kaipai-frontend/src/api/**`
- `kaipai-frontend/src/types/**`
- `kaipai-frontend/src/stores/**`
- `kaipai-frontend/src/pages/actor-profile/detail.vue`
- `kaipai-frontend/src/pkg-card/portfolio/index.vue`
- `kaipai-frontend/src/pkg-card/card-list/index.vue`
- `kaipai-frontend/src/pkg-card/actor-card/index.vue`
- `kaipai-frontend/src/pkg-card/ai-profile-card*/**`

### 后端

- `kaipaile-server/src/main/resources/db/migration/**`
- `kaipaile-server/src/main/java/com/kaipai/model/actor/**`
- `kaipaile-server/src/main/java/com/kaipai/model/ai/**`
- `kaipaile-server/src/main/java/com/kaipai/model/card/**`
- `kaipaile-server/src/main/java/com/kaipai/controller/api/card/**`
- `kaipaile-server/src/main/java/com/kaipai/service/card/**`
- `kaipaile-server/src/main/java/com/kaipai/service/actor/**`
- `kaipaile-server/src/main/java/com/kaipai/service/ai/**`
- `kaipaile-server/src/main/java/com/kaipai/service/card/**`
- `kaipaile-server/src/main/java/com/kaipai/controller/api/**`
- `kaipaile-server/src/main/java/com/kaipai/controller/admin/ai/**`
- `kaipaile-server/src/main/java/com/kaipai/integration/storage/**`
- 对应 mapper 与 tests

### 管理端

- `kaipai-admin/src/views/system/SettingsView.vue`
- `kaipai-admin/src/views/system/AiProfileImportConfigView.vue`（计划新增）
- `kaipai-admin/src/router/index.ts`
- `kaipai-admin/src/api/**`
- `kaipai-admin/src/types/**`

### 治理文档

- 本 Spec 三件套与后续 execution
- `.sce/specs/README.md`
- `.sce/specs/spec-code-mapping.md`
- `.sce/steering/CURRENT_CONTEXT.md`
- `docs/product-design.md`
- `00-05 / 00-27` 及条款接管矩阵中的相关 Spec / 验收脚本

_Requirements: R1-R151_
