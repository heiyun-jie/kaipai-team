# 项目环境配置

- **项目**: 开拍了（KaiPai）
- **类型**: 微信小程序演员通告投递平台
- **前端技术栈**: uni-app 3.0 + Vue 3.4 + TypeScript + SCSS + Pinia + Vite 5.2.8
- **后端技术栈**: Spring Boot 3.2.3 + MyBatis-Plus + MySQL 8.0 + Redis
- **本地环境**: Windows 11 / PowerShell / Node.js / npm / Git
- **前端仓库**: `git@github.com:yinuocarl-droid/kaipaile-frontend.git`
- **后端仓库**: `https://github.com/yinuocarl-droid/kaipaile-server.git`
- **数据库**: MySQL 8.0 Docker @ `192.168.1.108:3309/kaipai_dev`
- **服务器**: `192.168.1.108:22`（SSH alias `hy-backup`，用户 `zeno-deocker`），部署目录 `/home/zeno-deocker/docker-apps/kaipai`
- **后端运行入口**: 108 服务器 `http://127.0.0.1:8010/api`；本地通过 `127.0.0.1:18080` SSH tunnel 与 `https://localhost:18443` HTTPS proxy 访问
- **当前数据库状态**: 2026-05-05 已从本机 Docker `kaipai-mysql-local` 全量迁移到 108 `kaipai_dev`；当前 59 张表，`user` 表 7 条记录，登录闭环已通过

**核心目录**:
- `.sce/specs/` — 全量 Spec 索引（前端总纲见 `00-27`，推进治理见 `00-28`，当前后台主线见 `00-140 / 00-141 / 00-142`）
- `.sce/steering/` — 长期原则、环境约束、当前上下文
- `kaipai-frontend/` — 小程序前端工程（构建、包体治理、DevTools 运行态核验）
- `kaipaile-server/` — 后端 Spring Boot 服务
- `kaipai-admin/` — 平台后台 Web 管理端
- `docs/` — 产品设计、开发手册、运维基础设施

**构建与发布**:
- 开发: `cd kaipai-frontend && npm run dev:mp-weixin`
- 构建: `cd kaipai-frontend && npm run build:mp-weixin`
- 类型检查: `cd kaipai-frontend && npm run type-check`
- 治理审计: `cd kaipai-frontend && npm run audit:steering`
- 包体审计: `cd kaipai-frontend && npm run audit:mp-package`
- 本地后端联调: `powershell -ExecutionPolicy Bypass -File .sce\tools\start-kplyyk-local-https-proxy.ps1`
- DevTools 固定工程目录: `kaipai-frontend/dist/dev/mp-weixin`
- 内部构建源目录: `kaipai-frontend/dist/build/mp-weixin`
- 目标平台: 微信小程序（主）、H5（辅）

**实现现状基线**:
- 前端当前页面数量以 `kaipai-frontend/src/pages.json` 为准，旧统计不得作为验收依据
- 当前演员增强主线页为 `actor-card / card-list / style-detail / membership / verify / invite` 等当前分享链路页面；`fortune` 已转为退场对象
- 当前项目主线已切到后台 `00-140 / 00-141 / 00-142`
- 当前后台正式导航为 7 页：`仪表盘 / 数据分析 / 用户管理 / 分享内容 / 风格模板 / 运营动作 / 系统设置`
- 小程序前台历史主线仍可追溯到 `05-11 命理驱动分享定制主线`，但不再代表当前项目主线；旧 `fortune` / 命理 / 幸运色域由 `00-149` 物理退场
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
