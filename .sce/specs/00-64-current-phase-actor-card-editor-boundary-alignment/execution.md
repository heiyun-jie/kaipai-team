# 00-64 执行记录

## 1. 调查结论

- `pkg-card/actor-card/index` 当前仍残留旧会员能力矩阵、命理主题、幸运色入口与受众视角 selector
- 页面虽然已经朝“单卡编辑页”迁移，但用户能看到的仍是一张混合页
- 后端已具备 `highlightedPhotos / highlightedExperiences / 配色 / 布局` 等配置字段，但前端编辑页能力未补齐
- 页面缺少“预览公开名片”这一最小闭环动作

## 2. 本轮建档结论

- 新增 `00-64`，专门约束分享卡编辑页当前阶段边界
- 当前编辑页应从“旧分享能力中心”收口为“单卡配置编辑器”
- 多实例模型问题不在本 Spec 中处理，避免边界串线
- 已执行第一轮实现：
  - 移除 `pkg-card/actor-card/index` 中旧会员能力矩阵、命理入口、受众视角 selector 与 AI 润色控制区
  - 新增代表照片选择器与高亮经历选择器
  - 去除当前编辑链上的旧会员 gating，使布局 / 配色 / 高亮保存直接面向当前卡片配置
  - 新增“预览公开名片”按钮，直接跳转真实公开页 `pages/actor-profile/detail?shared=1&shareCardId=...`
  - 调整 `KpColorPalettePicker` 默认文案，改为“保存后同步到公开名片”的当前阶段口径

## 3. 验证

- 已执行 `D:\XM\kaipai-team\kaipai-frontend` 下：
  - `npm run type-check`
  - `npm run build:mp-weixin`
- 已确认生成产物包含：
  - `card-page__candidate-photos`
  - `card-page__candidate-experiences`
  - `预览公开名片`
  - `编辑当前卡片`
  - `当前卡片配置`
  - `调整主色、强调色与背景色，保存后会同步到公开名片。`

## 4. 待你侧页面验证

- 页面是否已移除会员 / 命理 / 受众视角噪音
- 代表照片 / 高亮经历是否符合你的实际使用预期
- 预览按钮跳入公开页后，是否符合你想要的“真实公开页”验证方式
- 配色和布局保存后，公开页是否按你的目标同步生效

## 5. 本轮输出

- `requirements.md`
- `design.md`
- `tasks.md`
- `execution.md`
