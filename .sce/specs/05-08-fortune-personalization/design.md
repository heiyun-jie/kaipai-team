# 命理个性化 - 技术设计

_Requirements: 05-08 全部_

## 1. 路由

```json
{
  "root": "pkg-card",
  "pages": [
    { "path": "fortune/index", "style": { "navigationStyle": "custom", "backgroundColor": "#121214" } }
  ]
}
```

## 2. 模块分工

| 模块 | 职责 |
|------|------|
| `pkg-card/fortune/index.vue` | 命理画像展示页 |
| `types/fortune.ts` | 命理类型定义���FortuneReport、ZodiacAnimal、Constellation、ZiweiStar） |
| `utils/fortune.ts` | 生肖/星座本地推算工具、幸运色应用逻辑 |
| `api/fortune.ts` | 命理报告接口、幸运色应��接口 |

## 3. 本地推算工具

生肖和星座由前端本地推算（不需要调 AI），用于即时展示基础信息：

```ts
// utils/fortune.ts
function getZodiacAnimal(birthday: string): ZodiacAnimal {
  const year = new Date(birthday).getFullYear()
  const animals: ZodiacAnimal[] = ['monkey','rooster','dog','pig','rat','ox','tiger','rabbit','dragon','snake','horse','goat']
  return animals[year % 12]
}

function getConstellation(birthday: string): Constellation {
  const d = new Date(birthday)
  const month = d.getMonth() + 1
  const day = d.getDate()
  // 标准星座日期表查表
  // ...
}
```

AI 大模型只负责生成运势解读、紫微主星、幸运色/数字。

## 4. 页面组件结构

```
fortune/index.vue
├── FortuneHeader        — 渐变头部 + 标题
├── LuckyPanel           — 幸运色 + 幸运数字 + 应用按钮
├── ZodiacSection        — 生肖卡片 + 运势
├── ConstellationSection — 星座卡片 + 运势
├── ZiweiSection         — 紫微主星 + 特质 + 建议
└── FooterNote           — "数据每月初自动更新"
```

所有 Section 为页面内局部组件（不抽为全局 Kp 组件），避免增加共享组件数量。

## 5. 与名片系统联动

### 5.1 幸运色应用流程

```
用户点击"应用幸运色到我的名片"
  → 检查等级 ≥ Lv5
  → POST /api/fortune/apply-lucky-color { sceneKey: 当前名片场景 }
  → 后端更新 actor_card_config.primary_color = fortune_report.lucky_color
  → 前端刷新名片预览
```

### 5.2 名片定制面板引导

在 `pkg-card/actor-card/index.vue` 的配色定制区域：
- Lv5 用户显示浮标："✨ 试试本月幸运色？" → 点击跳转命理页
- 非 Lv5 用户不显示

## 6. 错误处理

| 场景 | 处理 |
|------|------|
| AI 大模型超时/失败 | 使用规则兜底：生肖星座由本地推算，运势用预设文案池随机，幸运色从 12 色预设中取 |
| 用户无生日 | 引导去编辑档案补填生日 |
| 当月报告已存在 | 直接返回缓存，不重复调用 |

## 7. 任务清单

- [ ] T1 新建 `types/fortune.ts`、`utils/fortune.ts`、`api/fortune.ts`
- [ ] T2 实现 `pkg-card/fortune/index.vue` 命理画像页
- [ ] T3 后端新建 `fortune_report` 表和对应接口
- [ ] T4 后端对接 AI 大模型（Prompt 模板 + 结果校验 + 缓存）
- [ ] T5 实现幸运色应用到名片的联动
- [ ] T6 名片定制面板添加幸运色引导入口
- [ ] T7 "我的"页添加命理入口
- [ ] T8 构建验证：分包体积检查
