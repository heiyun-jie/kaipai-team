# 演员档案个人照片无限制上传 Tasks

## Phase 1: Spec

- [x] 新增 `05-19`，明确取消档案照片池数量上限。
- [x] 明确分享卡片代表图最多 3 张的版式限制保留。

## Phase 2: Red

- [x] 新增静态验收脚本。
- [x] 运行脚本并确认当前仍有 3/9 限制时失败。

## Phase 3: Implementation

- [x] 修改 `PhotoCategorySection.vue`，移除 `/9`、`/3` 文案和添加入口隐藏条件。
- [x] 修改 `edit.vue`，移除分类 3 张上传门禁和总数 `/9` 展示。
- [x] 修改 `profile-enhance.ts`，归一化和合并时不再截断照片池。
- [x] 修改 `ai-profile-card/index.vue`，分析图同步档案不再截断照片分类。
- [x] 修改 `card-list/index.vue`，作品上传不再受档案照片池 9 张上限限制。
- [x] 修改 `portfolio/index.vue`，作品集展示实际数量。

## Phase 4: Verification

- [x] 静态验收脚本通过。
- [x] 前端类型检查通过。
- [x] 微信小程序构建通过并同步到 `dist/dev/mp-weixin`。
- [x] 产物检查确认 `PhotoCategorySection` 生成结果不再含 `已上传 {{...}}/9`、`{{...}}/3` 或 `length < 3` 添加门禁。
- [x] 截图验证个人照片模块仍可展示添加入口。
