# CLAUDE.md — 「开拍了」KaiPai

> 本项目使用 **SCE** 驱动开发。功能开发、问题修复、重构均以 Spec 为中心。
> 业务模型：美团外卖模式 — 平台统一发布通告，小程序端纯演员端。

## 导航

| 需要什么 | 位置 |
|---------|------|
| **SCE 操作手册** | `.sce/README.md` |
| **当前阶段** | `.sce/steering/CURRENT_CONTEXT.md` |
| **开发原则** | `.sce/steering/CORE_PRINCIPLES.md` |
| **Spec 索引** | `.sce/specs/README.md` |
| **全局技术约定** | `.sce/specs/SHARED_CONVENTIONS.md` |
| **Spec-代码映射** | `.sce/specs/spec-code-mapping.md` |
| **产品设计文档** | `docs/product-design.md` |
| **开发经验手册** | `docs/dev-playbook.md` |
| **运维信息** | `docs/ops-infrastructure.md`（已 gitignore） |

## 工作流

```
需求 → 查 Spec → 读 requirements + design + SHARED_CONVENTIONS → 实现 → 验证验收标准 → 构建
```

## 项目结构

```
kaipai-team/
├── .sce/specs/          20 个 Spec（3 全局 + 14 页面 + 3 演员增强）
├── .sce/steering/       开发原则 + 环境 + 当前上下文
├── kaipai-frontend/src/
│   ├── pages/           16+ 页面（V1.1 新增 actor-card、credit-score 等）
│   ├── components/      19+ Kp 组件（V1.1 新增 KpCreditBadge、KpLevelTag）
│   ├── api/             6+ API 模块（V1.1 新增 credit）
│   ├── stores/          Pinia Store
│   ├── utils/           7+ 工具模块（V1.1 新增 credit 计算）
│   ├── types/           7+ 类型定义（V1.1 新增 credit）
│   └── styles/          SCSS tokens + mixins
├── kaipaile-server/     后端 Spring Boot 3.2.3
└── docs/                产品设计 + 经验手册 + 运维
```

## V1.1 新增功能（Phase 05）

| Spec | 功能 | 状态 |
|------|------|------|
| 05-01 actor-card | 演员分享明信片 + 公开落地页 | 待实现 |
| 05-02 actor-profile-enhance | 档案美化（edit.vue 拆分 + 作品经历 + 形象标签 + 照片分类） | 待实现 |
| 05-03 credit-score | 信用积分（0→100 叠加）与演员等级（LV.1-7） | 预留 |
