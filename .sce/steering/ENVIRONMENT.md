# 项目环境配置

- **项目**: 开拍了（KaiPai）
- **类型**: 微信小程序演员通告投递平台
- **前端技术栈**: uni-app 3.0 + Vue 3.4 + TypeScript + SCSS + Pinia + Vite 5.2.8
- **后端技术栈**: Spring Boot 3.2.3 + MyBatis-Plus + MySQL 8.0 + Redis
- **本地环境**: Windows 11 / PowerShell / Node.js / npm / Git
- **前端仓库**: `git@github.com:yinuocarl-droid/kaipaile-frontend.git`
- **后端仓库**: `https://github.com/yinuocarl-droid/kaipaile-server.git`
- **数据库**: MySQL 8.0.45 @ `101.43.57.62:3306/kaipai`
- **服务器**: Ubuntu `101.43.57.62:22`，部署目录 `/opt/kaipai`

**核心目录**:
- `.sce/specs/` — 53 个 Spec（当前前端总纲见 `00-27`，推进治理见 `00-28`，当前主线治理见 `05-11`）
- `.sce/steering/` — 长期原则、环境约束、当前上下文
- `kaipai-frontend/src/` — 前端源码（主包 14 页 + 分包 7 页，31 个 Kp 组件）
- `kaipaile-server/` — 后端 Spring Boot 服务
- `kaipai-admin/` — 平台后台 Web 管理端
- `docs/` — 产品设计、开发手册、运维基础设施

**构建与发布**:
- 开发: `cd kaipai-frontend && npm run dev:mp-weixin`
- 构建: `cd kaipai-frontend && npm run build:mp-weixin`
- 类型检查: `cd kaipai-frontend && npm run type-check`
- 治理审计: `cd kaipai-frontend && npm run audit:steering`
- 包体审计: `cd kaipai-frontend && npm run audit:mp-package`
- 产物目录: `kaipai-frontend/dist/build/mp-weixin`
- 目标平台: 微信小程序（主）、H5（辅）

**实现现状基线**:
- 前端当前已注册 18 个页面
- 当前演员增强主线页已注册 `actor-card / membership / verify / invite / fortune`
- 当前主线以 `05-11 命理驱动分享定制主线` 为前端治理基线
- 前端整体架构总纲入口为 `00-27 mini-program-frontend-architecture`
- 全局治理已新增 `00-05 mini-program-package-governance`
- 全局治理已新增 `00-06 bundle-size-first-pass` 和 `00-07 first-subpackage-migration`
- 全局治理已新增 `00-27 mini-program-frontend-architecture`
- 全局治理已新增 `00-28 architecture-driven-delivery-governance`
- 2026-03-31 最近一次 `audit:mp-package` 结果：主包 `517.65 KB`，`pkg-card 86.81 KB`，`pkg-tools 18.80 KB`
- `credit-score / credit-record / credit-rank` 已从当前主线分支移除
- 剧组端页面仍保留在小程序代码中，但业务主线已迁至平台后台

**文档治理**:
- 详细业务规则、页面需求、技术设计写入对应 Spec，不向 steering 堆积细节
- 环境、仓库、部署、数据库变更时，优先同步本文件和 `docs/ops-infrastructure.md`
- 若包体治理基线、审计命令或分包策略变化，优先同步 `00-05` Spec、`CURRENT_CONTEXT.md` 和项目开发手册
