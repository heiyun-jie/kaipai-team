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
- `.sce/specs/` — 20 个 Spec（3 全局基础 + 14 页面 + 3 演员增强）
- `.sce/steering/` — 长期原则、环境约束、当前上下文
- `kaipai-frontend/src/` — 前端源码（16 个页面、19 个 Kp 组件、6 个 API 模块、7 个 utils、7 个 types）
- `kaipai-frontend/docs/` — 页面导览、链路分析、导航规则
- `kaipaile-server/` — 后端 Spring Boot 服务
- `docs/` — 产品设计、开发手册、运维基础设施

**构建与发布**:
- 开发: `cd kaipai-frontend && npm run dev:mp-weixin`
- 构建: `cd kaipai-frontend && npm run build:mp-weixin`
- 类型检查: `cd kaipai-frontend && npm run type-check`
- 产物目录: `kaipai-frontend/dist/build/mp-weixin`
- 目标平台: 微信小程序（主）、H5（辅）

**实现现状基线**:
- 前端当前已注册 16 个页面
- 共享组件当前为 19 个 `Kp*.vue`
- 演员增强 Phase 05 的 `actor-card / credit-score / credit-record / credit-rank` 仍处于 Spec 阶段，尚未注册到 `pages.json`
- 剧组端页面仍保留在小程序代码中，但业务主线已迁至平台后台

**文档治理**:
- 详细业务规则、页面需求、技术设计写入对应 Spec，不向 steering 堆积细节
- 环境、仓库、部署、数据库变更时，优先同步本文件和 `docs/ops-infrastructure.md`
