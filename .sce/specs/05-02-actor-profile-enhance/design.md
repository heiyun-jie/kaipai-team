# 档案美化 - 技术设计

_Requirements: 05-02 全部_

## 1. edit.vue 拆分方案

现有 `actor-profile/edit.vue` 为 1604 行。新增功能后预计超过 2000 行，按 CORE_PRINCIPLES 第 11 条必须拆分。

### 拆分目录结构

```
src/pages/actor-profile/
├── edit.vue                          # 主框架：页面骨架 + 顶部卡片 + 底部操作栏 + 表单状态管理
├── components/
│   ├── BasicInfoSection.vue          # 基本信息板块（姓名/性别/年龄/身高/城市）
│   ├── SkillTagSection.vue           # 擅长类型 + 自我介绍
│   ├── AppearanceTagSection.vue      # 形象标签板块（体型/发型/语言）—— 新增
│   ├── PhotoCategorySection.vue      # 分类照片板块（形象照/生活照/剧照）—— 改造
│   ├── WorkExperienceSection.vue     # 作品经历板块 —— 新增
│   ├── VideoResumeSection.vue        # 视频简历板块
│   └── ProfileCompletionBar.vue      # 档案完整度 + 提升建议 —— 增强
```

### 拆分原则

- edit.vue 作为主框架，负责：页面骨架、顶部概览卡片、底部操作栏、表单数据 provide/inject、保存逻辑
- 各 Section 组件通过 `defineProps` + `defineEmits` 与主框架通信
- 表单数据用 `provide('actorForm', form)` 向下传递，减少 props 层级
- 先拆分再加新功能，禁止在 1604 行基础上打补丁

### 拆分顺序

```
第一步：从 edit.vue 中提取现有板块为独立 Section 组件（纯重构，不加新功能）
第二步：新增 AppearanceTagSection、WorkExperienceSection、PhotoCategorySection（改造）
第三步：增强 ProfileCompletionBar（新权重 + 提升建议）
```

## 2. 路由配置

无变化，沿用现有 `pages/actor-profile/edit` 路由。

## 3. 依赖清单

| 类别 | 依赖项 | 来源 Spec |
|------|--------|-----------|
| 布局 | KpPageLayout | 00-02 |
| 导航 | KpNavBar | 00-02 |
| 表单 | KpFormItem, KpInput, KpTextarea | 00-02 |
| 按钮 | KpButton | 00-02 |
| 标签 | KpTag | 00-02 |
| 图片上传 | KpImageUploader | 00-02 |
| 等级标签 | KpLevelTag | 05-03 |
| API | getActorProfile, updateActorProfile | 00-03 (api/actor) |
| API | getMyCreditScore | 05-03 (api/credit) |
| 工具 | uploadFile | 00-03 (utils/upload) |
| Store | useUserStore | 00-03 |
| 样式 | Design Tokens ($kp-*) | 00-01 |

## 4. 数据结构

### photos → photoCategories 迁移

**方案**：`photoCategories` 替代 `photos`。

```typescript
// 旧结构
interface ActorProfile {
  photos: string[]  // 混合数组
}

// 新结构
interface ActorProfile {
  photos: string[]  // 保留，值为 photoCategories 三区合并（向后兼容）
  photoCategories: {
    portrait: string[]    // 形象照，最多 3 张
    lifestyle: string[]   // 生活照，最多 3 张
    production: string[]  // 剧照，最多 3 张
  }
}
```

- 编辑页使用 `photoCategories` 操作
- `photos` 为计算属性：`[...portrait, ...lifestyle, ...production]`
- mock 数据直接使用 `photoCategories` 结构
- 展示侧（明信片、详情页）从 `photoCategories` 读取分类展示

### 档案完整度权重全表

| 项目 | 权重 | 条件 |
|------|------|------|
| 头像 | 10% | avatar 非空 |
| 基本信息 | 15% | 姓名+性别+年龄+身高+城市全填 |
| 照片 | 15% | photoCategories 总计 ≥3 张且覆盖 ≥2 区 |
| 视频简历 | 15% | videoUrl 非空 |
| 自我介绍 | 10% | intro ≥50 字 |
| 擅长类型 | 5% | skillTypes ≥1 项 |
| 作品经历 | 15% | workExperiences ≥1 条 |
| 形象标签 | 10% | bodyType+hairStyle+languages 至少各 1 |
| 照片分类完整 | 5% | 三区各至少 1 张 |
| **合计** | **100%** | |

## 5. 新增板块设计

### 5.1 AppearanceTagSection 形象标签

```
┌ 形象标签 APPEARANCE ────────────┐
│  已选 3 项标签                   │
│                                 │
│  体型：[偏瘦] [标准✓] [偏壮]     │
│  发型：[短发✓] [中长] [长发] [光头]│
│  语言：[普通话✓] [粤语] [四川话]  │
│        [东北话] [英语] [其他]     │
└─────────────────────────────────┘
```

### 5.2 WorkExperienceSection 作品经历

```
┌ 拍摄经历 WORK EXPERIENCE ──────┐
│  已添加 2 条经历                 │
│                                 │
│  ┌────────────────────────────┐ │
│  │ 《xx短剧》 - 路人甲          │ │
│  │ 2026-02  [剧照1] [剧照2]    │ │
│  │ 简要描述...         [删除]   │ │
│  └────────────────────────────┘ │
│  ┌────────────────────────────┐ │
│  │ 《yy广告》 - 群演            │ │
│  │ 2026-01                     │ │
│  └────────────────────────────┘ │
│                                 │
│  [+ 添加经历]                    │
└─────────────────────────────────┘
```

添加/编辑经历使用弹出式表单（半屏弹窗），字段：项目名称*、角色名称、拍摄时间（年月选择器）、剧照（最多4张）、简要描述。

### 5.3 PhotoCategorySection 分类照片

```
┌ 个人照片 PHOTO GALLERY ────────┐
│  已上传 5/9                     │
│                                 │
│  形象照（1/3）                   │
│  [照片] [+添加]                  │
│                                 │
│  生活照（2/3）                   │
│  [照片] [照片] [+添加]           │
│                                 │
│  剧照（2/3）                     │
│  [照片] [照片] [+添加]           │
└─────────────────────────────────┘
```

### 5.4 ProfileCompletionBar 增强

```
┌──────────────────────────────────┐
│  档案完整度 65%                    │
│  ████████████░░░░░░░              │
│                                   │
│  💡 提升建议：                     │
│  · 上传视频简历可提升 15%          │
│  · 添加作品经历可提升 15%          │
│  · 完善形象标签可提升 10%          │
└──────────────────────────────────┘
```

### 5.5 自我介绍引导

在 SkillTagSection 的自我介绍输入框上方新增"使用模板"按钮：

```typescript
function applyIntroTemplate(): void {
  const tpl = `我是${form.name || '[姓名]'}，来自${form.city || '[城市]'}，身高${form.height || '[XX]'}cm，擅长${form.skillTypes?.[0] || '[类型]'}表演。`
  form.intro = tpl
}
```

## 6. 等级标签替换

edit.vue 顶部概览卡片中：

```typescript
// 旧（硬编码）
profileCompletion >= 80 ? 'PRO ACTOR' : 'ACTOR'

// 新（动态计算）
<KpLevelTag :level="computedLevel" size="small" />
```

`computedLevel` 根据 mock 策略由档案完整度映射：积分 = 档案建设得分（0-30），映射到 LV.1-3。
