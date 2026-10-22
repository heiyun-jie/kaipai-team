# 演员卡技能特长语义与展示收口 - 技术设计

_Requirements: 3.1-3.5, 4-7_

## 1. 数据合同

在 `ActorCardPublicRespDTO.ProfileVO` 与前端 `ActorCardPublicVO` / `ActorCardRenderModel` 增加可选：

```ts
skillGroups?: {
  specialty: string[];
  professionalAbility: string[];
  roleType: string[];
};
```

后端 `buildProfile` 按以下顺序组装每组：快照对应字段（兼容 `specialtyTags` / `specialties`、`professionalAbilityTags` / `professionalAbilities`、`roleTypeTags` / `roleTypes`）→ `ActorProfile` 持久字段 → 空数组。历史扁平 `skills` / `skillTypes` 继续保留在 `skills`，仅作为未分组技能的展示兜底。

`skills` 的兼容值不再混入 `works[].workType`；既有旧快照中无法分组的值不擅自推断类别。

## 2. 共享渲染器派生模型

`ActorCardRenderer.vue` 内部派生：

```ts
const normalize = (values: unknown[]) => ... // trim、过滤空值、首次出现去重
const groupedSkills = {
  specialty: normalize(model.profile.skillGroups?.specialty ?? []),
  professionalAbility: normalize(model.profile.skillGroups?.professionalAbility ?? []),
  roleType: normalize(model.profile.skillGroups?.roleType ?? []),
};
const legacySkills = normalize(model.profile.skills ?? []);
const trueSkillItems = normalize([
  ...groupedSkills.professionalAbility,
  ...groupedSkills.specialty,
  ...legacySkills,
]);
```

当结构化字段存在时，`trueSkillItems` 只补充未分组旧值；不从 `works` 派生任何技能。角色方向单独使用 `groupedSkills.roleType`。

## 3. Hero 展示

- 保留 `.actor-card-renderer__hero-card--skills` 的 `420rpx / 579rpx / 255rpx / 184rpx`。
- `trueSkillItems.slice(0, 4)` 作为无溢出时的标签内容。
- 若 `trueSkillItems.length > 4`，展示前三个真实技能并在第四个稳定位置显示 `+N`，`N` 为剩余真实技能数。
- 使用现有 chip token 和固定换行，禁止动态增高 Hero 卡片。

## 4. 正文展示

正文技能区改为分组：

1. “职业能力”显示 `professionalAbility` 标签。
2. “职业特长”显示 `specialty` 标签。
3. “其他技能”仅在存在 `legacySkills` 且未被结构化值覆盖时显示。
4. “角色方向”显示 `roleType` 标签，不计入技能数量。

不再调用 `describeSkill`，不再渲染自动拼接描述。技能数量为职业能力 + 职业特长 + 未分组技能的去重数量。

## 5. 作品与摘要

- `workMeta` 继续读取 `work.workType`，只在拍摄经历中展示。
- 基础信息中的技能摘要改为 `trueSkillItems.slice(0, 3)`。
- 统计卡中的技能数量改为 `trueSkillItems.length`。

## 6. 测试与产物

- 后端：扩展 `ActorCardPublicServiceImplTest`，覆盖分组来源、快照优先、空数组和作品类型隔离。
- 前端：新增 `verify-00251-actor-card-skill-semantics.mjs`，断言数据分组、无 `describeSkill` 固定文案、Hero 限制、作品类型边界和 build/dev 三侧 scoped hash。
- 运行 `npm run type-check`、演员卡既有专项门禁、新门禁和 `npm run build:mp-weixin`。
- 构建后检查 `src`、`dist/build/mp-weixin`、`dist/dev/mp-weixin` 的 WXML/WXSS/JS 与 API 类型，禁止只更新单侧产物。
- 只读 MCP 使用固定 `dist/dev/mp-weixin`，不得控制桌面、置顶或抢焦点微信开发者工具。

## 7. 回滚

- 后端回滚只移除新增 `skillGroups` 组装和响应字段，保留旧 `skills`。
- 前端回滚恢复兼容 `skills` 标签渲染，不恢复 `works.workType` 混入或固定虚构说明。
- 不执行数据库回滚，不触碰正式容器和正式数据库。
