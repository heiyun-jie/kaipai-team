# 05-02 档案美化（Actor Profile Enhancement）

> 状态：待实现 | 优先级：高 | 依赖：03-04

## 1. 功能概述

增强现有演员资料编辑页 `actor-profile/edit`，让演员能打造更有吸引力的个人简历，类似"优化简历"。

## 2. 需求清单

### 2.1 作品经历板块（新增）

- **R1** 新增"拍摄经历"编辑板块，位于照片墙之后、视频简历之前
- **R2** 每条经历包含：项目名称（必填）、角色名称、拍摄时间、剧照（最多 4 张）、简要描述
- **R3** 支持添加多条经历，最多 10 条
- **R4** 支持编辑和删除已有经历
- **R5** 经历按时间倒序排列

### 2.2 形象标签扩展

- **R6** 在擅长类型基础上新增形象标签：体型（偏瘦/标准/偏壮）、发型（短发/中长/长发/光头）、语言/方言（普通话/粤语/四川话/东北话/英语等）
- **R7** 形象标签为可选填，不影响档案必填验证
- **R8** 标签展示在擅长类型下方，独立板块

### 2.3 照片分类

- **R9** 照片墙分为三区：形象照、生活照、剧照
- **R10** 每区最多上传 3 张（总共最多 9 张，与现有一致）
- **R11** 上传时引导用户选择照片类别

### 2.4 自我介绍引导

- **R12** 自我介绍输入框提供模板/引导语按钮
- **R13** 模板内容："我是[姓名]，来自[城市]，身高[XX]cm，擅长[类型]表演。曾参与过[作品]的拍摄..."
- **R14** 点击模板自动填充到输入框，用户可自由修改

### 2.5 档案评分优化

- **R15** 完整度计算新增维度：作品经历（+15%）、形象标签（+5%）、照片分类完整（+5%）
- **R16** 给出具体提升建议列表，如"上传视频可提升20%"、"添加作品经历可提升15%"
- **R17** 提升建议显示在档案完整度进度条下方

### 2.6 等级展示优化

- **R18** 编辑页顶部的 `PRO ACTOR` / `ACTOR` 硬编码替换为动态等级标签（KpLevelTag）
- **R19** 等级标签展示 LV.X + 名称，mock 阶段根据档案完整度自动计算

### 2.7 预览名片入口

- **R20** 编辑页底部操作栏新增"预览名片"按钮（次要样式）
- **R21** 点击跳转 `pages/actor-card/index`，预览当前档案的明信片效果

## 3. 数据结构扩展

### ActorProfile 新增字段

```typescript
// 作品经历
interface WorkExperience {
  id?: number
  projectName: string       // 项目名称（必填）
  roleName?: string         // 角色名称
  shootDate?: string        // 拍摄时间
  photos: string[]          // 剧照（最多 4 张）
  description?: string      // 简要描述
}

// ActorProfile 扩展
interface ActorProfile {
  // ...existing fields
  workExperiences: WorkExperience[]   // 作品经历
  bodyType?: string                   // 体型
  hairStyle?: string                  // 发型
  languages: string[]                 // 语言/方言
  photoCategories?: {                 // 照片分类
    portrait: string[]                // 形象照
    lifestyle: string[]               // 生活照
    production: string[]              // 剧照
  }
}
```

## 4. 依赖

- `00-01 global-style-system` — Design Tokens
- `00-02 shared-components` — KpFormItem, KpInput, KpTextarea, KpImageUploader, KpTag, KpButton
- `00-03 shared-utils-api` — api/actor, types/actor, utils/upload
- `05-01 actor-card` — 预览名片跳转
- `05-03 credit-score` — KpLevelTag 等级标签组件

## 5. 验收标准

- [ ] 作品经历板块可正常添加、编辑、删除，数据正确保存
- [ ] 形象标签可选择，正确展示在档案中
- [ ] 照片分类上传功能正常，三区各自独立
- [ ] 自我介绍模板可一键填充
- [ ] 档案完整度正确计算新增维度，提升建议正确展示
- [ ] 编辑页顶部等级标签动态展示（替换硬编码 PRO ACTOR / ACTOR）
- [ ] "预览名片"按钮正确跳转到明信片页
