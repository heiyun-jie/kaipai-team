# AI 生成分享图分析图必填上传 - 技术设计

## 1. 路由配置

页面路由不变：

```text
pkg-card/ai-profile-card/index
```

不新增页面、不改 `pages.json`。

_Requirements: 3.1, 3.2_

## 2. 相关性分析

本改动与现有链路的关系如下：

| 位置 | 当前能力 | 本轮处理 |
|------|----------|----------|
| `kaipai-frontend/src/pkg-card/ai-profile-card/index.vue` | AI 分享图生成入口，当前只有风格选择和生成按钮 | 新增必填分析图上传 UI，提交时传 `sourceImageUrl` |
| `kaipai-frontend/src/types/ai-profile-card.ts` | `AiProfileCardGeneratePayload` 已有 `sourceImageUrl?: string` | 直接复用，不改类型 |
| `kaipai-frontend/src/api/ai-profile-card.ts` | `generateAiProfileCard(payload)` 原样透传 payload | 直接复用，不改 API |
| `kaipai-frontend/src/utils/media-picker.ts` | `chooseImageFiles(1)` 支持相册 / 拍照 | 复用 |
| `kaipai-frontend/src/utils/upload.ts` | `uploadImage(filePath, 'photo')` 支持图片上传 | 复用 |
| `kaipaile-server/.../AiProfileCardGenerateReqDTO.java` | 已有 `sourceImageUrl` 字段 | 不改后端 DTO |
| `kaipaile-server/.../AiProfileCardServiceImpl.java` | `resolveSourceImage(profile, dto.getSourceImageUrl())` 会校验候选图 | 保持现状；前端上传成功后同步写入个人档案照片池，保证 `sourceImageUrl` 可通过校验 |

设计结论：本轮把前端 UI、上传、档案照片池同步与提交合同补齐，避免继续让用户在无分析图状态下触发生成；不扩展后端。

_Requirements: 3.1, 3.2, 3.3_

## 3. 依赖清单

前端新增 import：

```ts
import { chooseImageFiles } from '@/utils/media-picker';
import { uploadImage } from '@/utils/upload';
import { getOptionalMyActorProfile, updateActorProfile } from '@/api/actor';
```

沿用现有组件：

- `KpBottomActionBar`
- `KpButton`
- `KpFloatingBackButton`
- `KpShareSceneCard`

_Requirements: 3.1, 3.2_

## 4. 页面状态定义

新增状态：

```ts
const analysisImageUploading = ref(false);
const analysisImageUrl = ref('');
const profile = ref<ActorProfile | null>(null);
```

新增派生状态：

```ts
const analysisImageStatus = computed(() => analysisImageUrl.value ? '已上传' : '必填');
```

`actionTip` 改为同时反映风格锁定、页面加载、上传中、未上传和可生成状态。

_Requirements: 3.1, 3.2_

## 5. 模板结构

在风格面板后新增面板：

```text
STEP 02 上传分析图
  - 说明：上传一张用于 AI 分析的演员照片，生成后的 AI 图会作为详情首图
  - 未上传：上传占位按钮
  - 已上传：缩略图 + 已上传标记 + 更换图片 / 移除
```

步骤条从 2 步改成 3 步：

```text
01 风格 -> 02 分析图 -> 03 生成
```

review 区新增：

```text
分析图：已上传 / 未上传
```

_Requirements: 3.1, 3.3_

## 6. 交互逻辑

上传：

1. 点击上传区域或更换按钮。
2. 若当前 `profile` 为空，提示 `请先完善演员档案后再上传分析图`，不进入上传和档案保存。
3. 调用 `chooseImageFiles(1)`。
4. 调用 `uploadImage(filePath, 'photo')`。
5. 上传成功后通过 `updateActorProfile(...)` 把图片写入当前演员档案照片池。
6. 刷新 `profile`，再写入 `analysisImageUrl`。
7. 失败时 toast 上传失败原因。

移除：

1. 用户点击移除。
2. 清空 `analysisImageUrl`。
3. 回到必填未上传状态。

生成：

1. 保留原有重复提交、未选风格、风格锁定校验。
2. 上传中时提示 `分析图上传中，请稍后`。
3. 未上传时提示 `请先上传分析图`。
4. 提交时传入：

```ts
sourceImageUrl: analysisImageUrl.value
```

_Requirements: 3.2, 3.3_

## 7. 生命周期

`onShow` 继续调用 `hydratePage()`。

`hydratePage()` 读取当前演员档案用于上传后的安全合并，但不自动取档案第一张图填入 `analysisImageUrl`，因为用户确认本轮要求是“上传分析图必填”，页面需要用户显式上传。

_Requirements: 3.2_

## 8. 关键样式

新增局部样式命名沿用页面 BEM：

- `ai-profile-card-page__analysis-card`
- `ai-profile-card-page__analysis-empty`
- `ai-profile-card-page__analysis-preview`
- `ai-profile-card-page__analysis-image`
- `ai-profile-card-page__analysis-actions`
- `ai-profile-card-page__analysis-button`

产物验收必须确认这些类出现在：

- `dist/build/mp-weixin/pkg-card/ai-profile-card/index.wxml`
- `dist/build/mp-weixin/pkg-card/ai-profile-card/index.wxss`
- `dist/dev/mp-weixin/pkg-card/ai-profile-card/index.wxml`
- `dist/dev/mp-weixin/pkg-card/ai-profile-card/index.wxss`

_Requirements: 3.1_
