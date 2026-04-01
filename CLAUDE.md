# CLAUDE.md — 「开拍了」KaiPai

> 本项目使用 **SCE** 驱动开发。功能开发、问题修复、重构均以 Spec 为中心。
> 当前产品主线：演员名片分享 + 命理驱动个性化 + 会员能力分层 + 统一分享产物。

## 导航

| 需要什么 | 位置 |
|---------|------|
| **SCE 操作手册** | `.sce/README.md` |
| **当前阶段** | `.sce/steering/CURRENT_CONTEXT.md` |
| **开发原则** | `.sce/steering/CORE_PRINCIPLES.md` |
| **Spec 索引** | `.sce/specs/README.md` |
| **全局技术约定** | `.sce/specs/SHARED_CONVENTIONS.md` |
| **前端架构总览** | `.sce/specs/00-27-mini-program-frontend-architecture/` |
| **Spec-代码映射** | `.sce/specs/spec-code-mapping.md` |
| **产品设计文档** | `docs/product-design.md` |
| **开发经验手册** | `docs/dev-playbook.md` |
| **运维信息** | `docs/ops-infrastructure.md`（已 gitignore） |

## 工作流

```text
需求 → 查 Spec → 读 requirements + design + SHARED_CONVENTIONS → 实现 → 验证验收标准 → 构建 → 必要时执行包体审计 → 文档同步
```

## 项目结构

```text
kaipai-team/
├── .sce/specs/          52 个 Spec（当前前端总纲见 00-27，当前主线治理见 05-11）
├── .sce/steering/       开发原则 + 环境 + 当前上下文
├── kaipai-frontend/src/
│   ├── pages/           主包 14 页 + 分包 7 页（pkg-card / pkg-tools）
│   ├── components/      31 个 Kp 组件
│   ├── api/             11 个 API 模块
│   ├── stores/          Pinia Store
│   ├── utils/           17 个工具模块
│   ├── types/           12 个类型定义
│   └── styles/          SCSS tokens + mixins
├── kaipai-admin/        平台后台 Web 管理端
├── kaipaile-server/     后端 Spring Boot 3.2.3
└── docs/                产品设计 + 经验手册 + 运维
```

## 当前 Phase 05

| Spec | 功能 | 状态 |
|------|------|------|
| 05-01 actor-card | 早期名片方案 | 历史保留，当前由 05-05 接管 |
| 05-02 actor-profile-enhance | 档案美化与编辑页模块化增强 | 已实现，持续回调 UI |
| 05-03 credit-score | 信用积分 / 排行榜 | 当前阶段搁置，当前分支已移除实现 |
| 05-04 ai-resume-polish | 全档案对话式 AI 润色 | 已建 Spec，待实现 |
| 05-05 card-share-membership | 名片分享主线 + 等级/会员基础能力 | 已接入 05-11 第一轮 |
| 05-06 mainline-residual-cleanup | 主线残余清理 | 已完成首轮 |
| 05-07 mainline-component-refactor | 主线组件重构 | 已完成首轮 |
| 05-08 fortune-personalization | 命理个性化 | 已接入 05-11 第一轮 |
| 05-09 identity-verification | 实名认证 | 已建档并完成前端接入 |
| 05-10 invite-referral | 邀请裂变 | 已接入 05-11 第一轮 |
| 05-11 fortune-driven-share-personalization | 命理驱动分享定制主线 | 当前架构治理基线 |

## 当前规则

- 先建 Spec，再动实现。
- 当前前端整体架构入口为 `00-27 mini-program-frontend-architecture`。
- 当前主线治理基线为 `05-11`，05-05 / 05-08 / 05-10 后续实现必须服从 05-11。
- 当前主线不保留旧信用入口、旧积分页、旧积分组件和旧命名残留。
- 小程序 UI 验收以 `kaipai-frontend/dist/build/mp-weixin` 为准。
- 治理审计命令：`cd kaipai-frontend && npm run audit:steering`
- 包体审计命令：`cd kaipai-frontend && npm run audit:mp-package`
- 微信小程序默认以单包不超过 `2 MB` 为约束，后续分包治理以 `00-05` Spec 为准。
- 后续新增功能模块默认先评估是否独立分包，不能直接默认进入主包。
- AI 大模型统一由后端封装，前端不直接调用。
- 身份证号后端加密存储，前端只展示脱敏值。
