# SCE 操作手册

> AI 工具：先读此文件。本项目使用 Spec 驱动开发。

## 工作流

1. **查 Spec** → `.sce/specs/` 目录下查找对应 Spec
2. **无 Spec** → 先创建 `requirements.md` + `design.md`
3. **有 Spec** → 读 requirements.md + design.md + SHARED_CONVENTIONS.md
4. **实现** → 遵循 design.md 技术方案
5. **验证** → 对照 requirements.md 验收标准
6. **更新** → 如实现偏离设计，同步更新 Spec

## Spec 三件套结构

```
XX-YY-功能名称/
├── requirements.md   WHAT — 用户故事、功能需求、验收标准
├── design.md         HOW  — 路由、依赖、状态、模板、逻辑、样式
└── tasks.md          STEPS — 执行步骤（可选）
```

### requirements.md

```markdown
# 功能名称
## 1. 概述
## 2. 用户故事
## 3. 功能需求
### 3.1 需求标题
**描述**: ...
**验收标准**: WHEN [条件] THEN [结果]
## 4. 非功能需求（仅页面特有项，通用项见 SHARED_CONVENTIONS.md）
## 5. 约束条件（仅页面特有项，通用项见 SHARED_CONVENTIONS.md）
```

### design.md

```markdown
# 功能名称 - 技术设计
## 1. 路由配置
## 2. 依赖清单
## 3. 页面状态定义
## 4. 模板结构
## 5. 交互逻辑
## 6. 生命周期
## 7. 页面跳转关系
## 8. 关键样式（可选）
```

## 双向追溯

- **正向**（需求→设计）：design.md 中标注 `_Requirements: 3.1, 3.2_`
- **反向**（任务→需求）：tasks.md 中标注 `**Validates: Requirements 3.1**`

## 目录结构

```
.sce/
├── README.md                  ← 本文件
├── specs/
│   ├── README.md              Spec 索引 + 组件复用矩阵
│   ├── SHARED_CONVENTIONS.md  全局技术约定
│   ├── spec-code-mapping.md   Spec ↔ 源文件映射
│   └── {spec-name}/           各 Spec（requirements.md + design.md）
├── steering/
│   ├── CORE_PRINCIPLES.md     长期开发原则
│   ├── ENVIRONMENT.md         项目环境配置
│   ├── CURRENT_CONTEXT.md     当前阶段上下文
│   └── RULES_GUIDE.md         Steering 规则索引
├── config/                    SCE 框架配置
└── knowledge/                 问题和经验库
```

## 执行原则

- 一次只执行一个任务
- 执行前读取 requirements.md + design.md + SHARED_CONVENTIONS.md
- 执行后更新任务状态，停止并等待用户审核
- 不要跳过 Spec 直接实现功能

**SCE Version**: 3.6.55
