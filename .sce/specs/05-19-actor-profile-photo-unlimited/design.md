# 演员档案个人照片无限制上传 - 技术设计

## 1. 路由配置

不新增路由，涉及页面：

```text
pages/actor-profile/edit
pkg-card/portfolio/index
pkg-card/card-list/index
pkg-card/ai-profile-card/index
```

_Requirements: 3.1, 3.2, 3.3_

## 2. 设计结论

本轮取消“档案照片池”数量上限，保留单次选择图片数量受小程序能力约束。

```text
档案照片池：
  portrait[]   不限制
  lifestyle[]  不限制
  production[] 不限制
  photos = 三类完整合并，不限制

分享卡片代表图：
  highlightedPhotos 继续最多 3 张
```

_Requirements: 3.1, 3.2, 3.4_

## 3. 依赖清单

| 文件 | 本轮职责 |
|------|----------|
| `src/pages/actor-profile/components/PhotoCategorySection.vue` | 取消 `/9`、`/3` 文案和添加入口隐藏条件 |
| `src/pages/actor-profile/edit.vue` | 取消分类 3 张上传门禁，保存完整照片数组 |
| `src/pages/actor-profile/profile-enhance.ts` | 归一化和合并时不再截断照片池 |
| `src/pkg-card/ai-profile-card/index.vue` | 分析图同步档案时不再因每类 3 张而覆盖/截断 |
| `src/pkg-card/card-list/index.vue` | 上传作品写入档案照片池时不再受 9 张上限限制 |
| `src/pkg-card/portfolio/index.vue` | 作品集展示实际数量，不再显示 `/9`、`/3` |

_Requirements: 3.1, 3.2, 3.3_

## 4. 页面状态定义

`ActorPhotoCategories` 类型不变：

```ts
interface ActorPhotoCategories {
  portrait: string[]
  lifestyle: string[]
  production: string[]
}
```

不新增 `max` 配置，不新增后端字段。

_Requirements: 3.2_

## 5. 模板结构

### 5.1 编辑页个人照片

旧展示：

```text
个人照片 已上传 9/9
形象照 3/3
```

新展示：

```text
个人照片 已上传 9 张
形象照 3 张
```

每个分类的添加入口始终跟随照片列表显示：

```vue
<view class="photo-category__add" @click="emit('choose-photo', item.key)">
```

不再使用：

```vue
v-if="categories[item.key].length < 3"
```

_Requirements: 3.1_

### 5.2 作品集照片分组

作品集只展示实际数量：

```text
作品照片 已上传 N 张
形象照 N 张
```

_Requirements: 3.3_

## 6. 交互逻辑

### 6.1 编辑页分类上传

旧逻辑：

```ts
if (form.photoCategories[category].length >= 3) return
chooseImageFiles(3 - form.photoCategories[category].length)
for (...) {
  if (form.photoCategories[category].length >= 3) break
}
```

新逻辑：

```ts
if (photoUploading.value) return
const filePaths = await chooseImageFiles(9)
for (const filePath of filePaths) {
  form.photoCategories[category].push(uploadedUrl)
}
syncPhotosFromCategories()
```

说明：`chooseImageFiles(9)` 是单次选择上限，不是档案总量上限。用户可重复点击继续添加。

_Requirements: 3.1, 3.2_

### 6.2 扁平照片兼容

当后端只返回旧 `photos` 扁平数组时，继续保留旧映射前两组的语义，并保证不丢图：

```ts
portrait: photos.slice(0, 3)
lifestyle: photos.slice(3, 6)
production: photos.slice(6)
```

_Requirements: 3.2_

### 6.3 AI 分析图同步

分析图上传后同步进档案照片池时，固定追加到 `portrait` 前面：

```ts
nextCategories.portrait = [normalizedUrl, ...nextCategories.portrait]
```

不再 `.slice(0, 3)`。

_Requirements: 3.3_

### 6.4 卡片创建页上传作品

卡片创建页上传作品时，取消 `remaining = 9 - total` 和 `最多上传 9 张作品照片` 门禁。

上传成功的作品图追加到 `production`，不截断；单张分享卡的 `selectedWorkPhotos` 仍受 `MAX_SELECTED_WORK_PHOTOS = 3` 约束。

_Requirements: 3.3, 3.4_

## 7. 验证设计

新增静态验收脚本：

```text
.sce/specs/05-19-actor-profile-photo-unlimited/verify-photo-unlimited.mjs
```

覆盖：

1. 编辑页不再有分类 3 张上传门禁。
2. `PhotoCategorySection` 不再显示 `/9`、`/3`，且添加入口不再按 `< 3` 隐藏。
3. `profile-enhance.ts` 不再截断 `photoCategories` 或总照片。
4. AI 分析图同步档案不再 `.slice(0, 3)`。
5. 卡片创建页上传作品不再有总数 9 张门禁。
6. 作品集展示不再显示 `/9`、`/3`。
7. `MAX_SELECTED_WORK_PHOTOS = 3` 保留。

验证命令：

```powershell
node .sce\specs\05-19-actor-profile-photo-unlimited\verify-photo-unlimited.mjs .
cd kaipai-frontend
npm run type-check
npm run build:mp-weixin
```
