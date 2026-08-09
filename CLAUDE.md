# CLAUDE.md — 「开拍了」KaiPai

> 本项目使用 **SCE** 驱动开发。功能开发、问题修复、重构均以 Spec 为中心。
> 当前项目主线：后台 reference-driven 架构收口 + 模板可视化配置深化 + 历史路由与旧代码退场治理。

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
├── .sce/specs/          全量 Spec 索引（当前后台主线见 00-140 / 00-141 / 00-142）
├── .sce/steering/       开发原则 + 环境 + 当前上下文
├── kaipai-frontend/     小程序前端（历史主线、包体治理、运行态核验）
├── kaipai-admin/        平台后台 Web 管理端
├── kaipaile-server/     后端 Spring Boot 3.2.3
└── docs/                产品设计 + 经验手册 + 运维
```

## 当前后台主线

| Spec | 功能 | 状态 |
|------|------|------|
| 00-140 | 后台壳层 / 架构 / 模板配置对齐 | 已完成，建立 7 页正式导航与模板配置第一批可视化基线 |
| 00-141 | 后台机构管理页面本体退场 | 已完成，`/users/orgs` 与页面专用残留已退出运行态 |
| 00-142 | 后台风格模板可视化配置深化 | 已完成，模板编辑已深化到页面结构 / 模块显隐 / 行动区配置 |
| 00-110 | 后台旧路由 / 旧代码 / fallback 退场审计 | 持续作为删除门禁与历史能力核销基线 |
| 00-74 | 后台 reference UI / 架构重构 | 历史主线，作为当前后台运行态收口的上游基线保留 |

## 当前规则

- 先建 Spec，再动实现。
- 默认全程在 `V3.0` 上开发（2026-08-09 用户裁决，取代此前的 `main`），禁止自作主张切换分支或新建特性分支；本仓库与各子仓库（`kaipaile-server` / `kaipai-frontend` / `kaipai-admin`）一致适用；仅当用户明确要求时才新建/切换分支，且新建前先确认意图。
- 默认先读 `.sce/README.md`、`.sce/steering/CURRENT_CONTEXT.md`、`.sce/specs/README.md`。
- 当前后台主线以 `00-142 / 00-141 / 00-140` 为准；涉及删除门禁、旧路由、旧 fallback 时回看 `00-110`。
- 当前后台正式导航为 7 页：`仪表盘 / 数据分析 / 用户管理 / 分享内容 / 风格模板 / 运营动作 / 系统设置`。
- 小程序前端仍由 `00-27`、`00-28`、`00-05` 等 Spec 治理，但不再代表当前项目主线。
- 微信开发者工具固定打开 `kaipai-frontend/dist/dev/mp-weixin`。
- 微信开发者工具安装在 `D:\AP\微信web开发者工具`，CLI 为 `D:\AP\微信web开发者工具\cli.bat`（中文路径在 PowerShell 用 `& '...\cli.bat' <命令>` 调用，cmd 下易失败）；常用：`islogin` 查登录、`open --project 'D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin'` 启动小程序。需工具内「设置→安全→服务端口」已开启 CLI。
- `kaipai-frontend/dist/build/mp-weixin` 只作为内部构建源目录与产物核对基线。
- 改动前端 `src` 后必须重新打包产物才生效，不能只改源码就宣称完成或交付验证：执行 `cd kaipai-frontend && npm run build:mp-weixin`，其 postbuild 会自动把 `dist/build` 同步到 `dist/dev`，开发者工具加载的 `dist/dev` 即为最新。打包后用 `grep` 核对改动关键字已进入对应产物文件，避免 dev/build 漂移导致用户看到旧页面。
- 治理审计命令：`cd kaipai-frontend && npm run audit:steering`
- 包体审计命令：`cd kaipai-frontend && npm run audit:mp-package`
- 微信小程序默认以单包不超过 `2 MB` 为约束，后续分包治理以 `00-05` Spec 为准。
- 后续新增功能模块默认先评估是否独立分包，不能直接默认进入主包。
- 后台模板配置、路由治理、隐藏能力退场与正式导航对齐，默认优先落到对应 `00-1xx` Spec，而不是只改代码不回填治理文档。
- AI 大模型统一由后端封装，前端不直接调用。
- 身份证号后端加密存储，前端只展示脱敏值。
