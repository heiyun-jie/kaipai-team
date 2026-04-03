# 00-28 项目结构快速定位图

## 1. 文档定位

- 归属 Spec：`00-28 architecture-driven-delivery-governance`
- 文档用途：把当前工作区内的根仓、独立子仓、Spec 文档体系、发布脚本与运行时资料收口到同一张“导航图”里
- 适用场景：
  - 新任务启动前，先判断应该进哪个仓库
  - 排查接口 400/500、mock 未退场、权限菜单、发布脚本时，快速定位到对应目录
  - 避免把根仓 `.git`、`kaipai-admin/.git`、`kaipai-frontend/.git`、`kaipaile-server/.git` 混成一个仓库操作
- 更新时间：`2026-04-03`

## 2. 工作区总览

```text
D:\XM\kaipai-team
├─ .sce/                Spec / runbook / status / scripts / 治理入口
├─ docs/                当前主线产品文档与本地运维资料
├─ kaipai-frontend/     小程序前端独立仓库（uni-app + Vue 3）
├─ kaipai-admin/        平台管理后台独立仓库（Vite + Vue 3 + Element Plus）
├─ kaipaile-server/     后端独立仓库（Spring Boot 3 + MyBatis-Plus）
├─ src/                 根仓历史测试目录，非当前业务主代码入口
├─ tmp/                 临时文件目录
└─ *.log                本地调试日志
```

## 3. 仓库边界

| 位置 | 角色 | Git 边界 | 说明 |
|------|------|----------|------|
| 根目录 `D:\XM\kaipai-team` | 治理与总控仓 | 独立 `.git` | 主要存放 `.sce`、`docs`、跨仓记录，不承载三端主业务代码 |
| `kaipai-frontend/` | 小程序前端 | 独立 `.git` | uni-app 主线代码、页面、组件、API、mock 与构建脚本 |
| `kaipai-admin/` | 平台管理后台 | 独立 `.git` | 后台运营/治理页面、权限菜单、接口封装与前端发布产物 |
| `kaipaile-server/` | Java 后端 | 独立 `.git` | 认证、邀请、实名认证、会员、招募、AI 等真实接口与数据库迁移 |

## 4. 根仓怎么用

### 4.1 `.sce/` 是统一治理入口

| 路径 | 作用 | 快速说明 |
|------|------|----------|
| `.sce/README.md` | SCE 总操作手册 | 先读工作流、Spec 结构和执行原则 |
| `.sce/specs/README.md` | 全量 Spec 索引 | 按功能编号找 requirements / design / tasks |
| `.sce/specs/spec-code-mapping.md` | Spec ↔ 源文件映射 | 从 Spec 反查代码，或从代码回追 Spec |
| `.sce/specs/00-27-mini-program-frontend-architecture/` | 小程序整体架构 | 小程序页面层、共享层、分包、状态/API 总纲 |
| `.sce/specs/00-28-architecture-driven-delivery-governance/` | 整体推进治理 | 当前项目按能力切片推进的上位 Spec |
| `.sce/specs/00-28-architecture-driven-delivery-governance/status/` | 当前真实状态 | 每条主线的联调判断、闭环缺口、评估结论 |
| `.sce/specs/00-29-backend-admin-release-governance/` | 发布治理 Spec | 规定后端/后台发布必须遵循的标准流程 |
| `.sce/runbooks/backend-admin-release/` | 运维发布手册 | 标准发布流程、证据模板、发布脚本、历史记录 |
| `.sce/runbooks/backend-admin-release/wechat-config-gate-runbook.md` | 微信门禁单页入口 | invite / login-auth 的本地输入、总控、发布后复检必须先看这里 |
| `.sce/config/local-secrets/wechat-miniapp.env` | 本地微信 secret 输入位 | gitignored，本地合法 `appId/appSecret` 只允许从这里或同等受控来源进入总控 |
| `.sce/reports/` | 阶段性专项报告 | 包体、重构、治理审计等专项记录 |
| `.sce/steering/` | 长期规则 | 当前阶段上下文、环境、原则与规则索引 |

### 4.2 `docs/` 放业务说明与本地运维资料

| 路径 | 作用 |
|------|------|
| `docs/product-design.md` | 当前主线综合产品说明 |
| `docs/dev-playbook.md` | 开发经验、视觉基线、常见坑 |
| `docs/ops-infrastructure.md` | 本地运维资料与基础设施说明，含敏感信息，不可推远端 |
| `docs/archive/` | 已归档的旧版产品文档 |

### 4.3 根目录其它内容

| 路径 | 作用 |
|------|------|
| `src/test/` | 根仓历史测试目录，当前不是三端主链路入口 |
| `tmp/` | 临时中间文件 |
| `tmp-dev-mp-weixin.log` 与同类日志 | 本地调试日志，排障后可按需清理 |

## 5. 小程序前端 `kaipai-frontend/`

### 5.1 关键目录

| 路径 | 看什么 |
|------|--------|
| `kaipai-frontend/src/pages/` | 主包页面，登录/首页/我的/角色详情/档案编辑等主链路 |
| `kaipai-frontend/src/pkg-card/` | 演员增强分包，名片/会员/实名认证/邀请/命理 |
| `kaipai-frontend/src/pkg-tools/` | 工具分包，`webview` / `video-player` |
| `kaipai-frontend/src/components/` | `Kp*` 共享组件 |
| `kaipai-frontend/src/api/` | 前端请求封装，按业务域拆分 |
| `kaipai-frontend/src/stores/` | Pinia 状态，当前核心是 `user.ts` |
| `kaipai-frontend/src/utils/` | 请求、登录、分享、命理、等级、主题、上传等工具 |
| `kaipai-frontend/src/types/` | DTO / 前端领域类型 |
| `kaipai-frontend/src/mock/` | mock 数据与 mock service，排查“是否还在 mock”先看这里 |
| `kaipai-frontend/src/styles/` | token、mixin、页面壳层与全局样式 |
| `kaipai-frontend/src/pages.json` | 路由与分包配置 |
| `kaipai-frontend/scripts/` | 小程序包体审计与产物同步脚本 |
| `kaipai-frontend/dist/build/mp-weixin/` | 微信开发者工具应打开的真实构建产物 |

### 5.2 常见需求去哪改

| 场景 | 优先目录 |
|------|----------|
| 页面 UI/交互 | `src/pages/` 或 `src/pkg-card/` 对应页面 |
| 视频简历预览页壳层 | `src/pkg-tools/video-player/index.vue`，当前作为演员视频简历的播放器优先预览页 |
| 演员首页主入口与角色/档案分流 | `src/pages/home/index.vue`，当前口径是“演员档案列表首页 + 剧组项目总览首页” |
| 共享组件复用 | `src/components/` |
| 新接口接入 / mock 退场 | `src/api/`、`src/utils/request.ts`、`src/mock/` |
| 登录态 / 用户资料同步 | `src/stores/user.ts`、`src/api/auth.ts`、`src/utils/auth.ts` |
| 分享主题 / 命理 / 会员 gating | `src/api/personalization.ts`、`src/utils/personalization.ts`、`src/utils/theme-resolver.ts` |
| 包体 / 分包 / 构建问题 | `src/pages.json`、`scripts/audit-mp-package.ps1`、`scripts/sync-mp-weixin.ps1` |

## 6. 平台管理后台 `kaipai-admin/`

### 6.1 关键目录

| 路径 | 看什么 |
|------|--------|
| `kaipai-admin/src/views/` | 后台各业务页面，按域拆分：`dashboard`、`verify`、`referral`、`membership`、`recruit`、`system` 等 |
| `kaipai-admin/src/api/` | 后台接口封装 |
| `kaipai-admin/src/router/` | 路由注册、权限守卫、静态路由 |
| `kaipai-admin/src/constants/menus.ts` | 菜单结构与页面挂载入口 |
| `kaipai-admin/src/constants/permission-registry.ts` | 权限矩阵与角色治理基线 |
| `kaipai-admin/src/stores/` | 登录态、权限态、应用态 |
| `kaipai-admin/src/components/` | 页面容器、筛选面板、弹窗、树形权限编辑器等 |
| `kaipai-admin/src/layouts/` | 管理台壳层 |
| `kaipai-admin/src/utils/request.ts` | 后台请求底座 |
| `kaipai-admin/src/styles/` | 后台全局样式与 token |
| `kaipai-admin/public/` | 静态资源 |
| `kaipai-admin/dist/` | 发布产物 |

### 6.2 常见需求去哪改

| 场景 | 优先目录 |
|------|----------|
| 菜单没显示 / 页面路由不对 | `src/constants/menus.ts`、`src/router/index.ts` |
| 权限码缺失 / 角色分配异常 | `src/constants/permission-registry.ts`、`src/stores/permission.ts`、`src/views/system/RolesView.vue` |
| 某个后台页面 400/500 | 先看对应 `src/views/**` 的查询参数构造，再看 `src/api/**` |
| 通用筛选区 / 页头 / 表格壳层 | `src/components/business/`、`src/styles/index.scss` |
| 登录与 token 问题 | `src/api/auth.ts`、`src/stores/auth.ts`、`src/router/guard.ts` |

## 7. 后端 `kaipaile-server/`

### 7.1 关键目录

| 路径 | 看什么 |
|------|--------|
| `kaipaile-server/src/main/java/com/kaipai/module/controller/` | Controller 层，区分 actor/admin 等入口 |
| `kaipaile-server/src/main/java/com/kaipai/module/server/` | Service 业务实现主区 |
| `kaipaile-server/src/main/java/com/kaipai/module/model/` | DTO / Query / VO / Entity 等领域模型 |
| `kaipaile-server/src/main/java/com/kaipai/common/` | 安全、配置、统一返回、异常、过滤器与公共能力 |
| `kaipaile-server/src/main/resources/application.yml` | 通用 Spring Boot 配置 |
| `kaipaile-server/src/main/resources/application-dev.yml` | dev 环境配置 |
| `kaipaile-server/src/main/resources/bootstrap.yml` | Nacos / bootstrap 入口 |
| `kaipaile-server/src/main/resources/db/migration/` | 数据库 schema migration |
| `kaipaile-server/pom.xml` | Maven、Spring Boot、Java 版本与依赖 |

### 7.2 常见需求去哪改

| 场景 | 优先目录 |
|------|----------|
| 某接口返回 400/500 | 对应 `controller` 的参数定义 + `server` 的实现 |
| 后台招募 / 邀请 / AI / 实名治理接口 | `module/controller/admin/` 与对应 `server` |
| 小程序演员端接口 | `module/controller/app/` 与对应 `server` |
| DTO 字段错位 / 分页查询问题 | `module/model/`、查询对象、VO 与分页装配逻辑 |
| 数据库缺字段 / 上线后 schema 漂移 | `src/main/resources/db/migration/` |
| 登录、鉴权、统一返回 | `common/auth/`、`common/filter/`、`common/result/`、`common/handler/` |

## 8. 发布与运维资料在哪

| 路径 | 作用 |
|------|------|
| `.sce/specs/00-29-backend-admin-release-governance/` | 标准发布治理 Spec |
| `.sce/runbooks/backend-admin-release/backend-admin-standard-release.md` | 发布流程主文档 |
| `.sce/runbooks/backend-admin-release/wechat-config-gate-runbook.md` | invite / login-auth 微信配置门禁单页入口 |
| `.sce/runbooks/backend-admin-release/backend-admin-release-evidence-template.md` | 发布证据模板 |
| `.sce/runbooks/backend-admin-release/scripts/` | 后端/后台标准发布脚本与只读诊断脚本 |
| `.sce/runbooks/backend-admin-release/records/` | 每次发布记录 |
| `.sce/config/local-secrets/wechat-miniapp.env` | 本地 gitignored 微信 secret 输入位 |
| `docs/ops-infrastructure.md` | 服务器、数据库、Docker Compose、本地凭据说明 |

## 9. 快速定位清单

| 要找什么 | 先去哪里 |
|----------|----------|
| 整体推进状态 | `.sce/specs/00-28-architecture-driven-delivery-governance/status/` |
| 整体架构评估 | `.sce/specs/00-28-architecture-driven-delivery-governance/status/overall-architecture-assessment.md` |
| 某条能力切片的 requirements / design / tasks | `.sce/specs/{spec-id}/` |
| Spec 对应到哪些代码文件 | `.sce/specs/spec-code-mapping.md` |
| 小程序页面与分包结构 | `kaipai-frontend/src/pages/`、`kaipai-frontend/src/pkg-card/`、`kaipai-frontend/src/pages.json` |
| 后台菜单、权限、页面入口 | `kaipai-admin/src/constants/menus.ts`、`kaipai-admin/src/constants/permission-registry.ts`、`kaipai-admin/src/views/` |
| 后端接口与 Service | `kaipaile-server/src/main/java/com/kaipai/module/controller/`、`kaipaile-server/src/main/java/com/kaipai/module/server/` |
| 数据库变更历史 | `kaipaile-server/src/main/resources/db/migration/` |
| 标准发布脚本 | `.sce/runbooks/backend-admin-release/scripts/` |
| invite / login-auth 微信门禁 | `.sce/runbooks/backend-admin-release/wechat-config-gate-runbook.md`、`.sce/config/local-secrets/wechat-miniapp.env` |
| 本地运维环境资料 | `docs/ops-infrastructure.md` |

## 10. 当前约束

1. 根仓主要用于治理与文档，不要把 `kaipai-frontend`、`kaipai-admin`、`kaipaile-server` 当成根仓普通子目录直接做混合提交。
2. 新调查、新实现、新发布要优先回到对应 Spec / status / runbook，而不是只在聊天记录里保留结论。
3. 后端和管理端发布必须以 `00-29` 与 `.sce/runbooks/backend-admin-release/` 为准，不再使用临时手工命令替代正式流程。
4. invite / login-auth 若涉及微信真实链路，必须先通过 `wechat-config-gate-runbook.md` 的合法 secret 门禁；`.sce/config/local-secrets/wechat-miniapp.env` 存在不等于已就绪。
5. 排查“小程序还是 mock”时，必须同时检查 `src/api/`、`src/mock/`、运行时环境变量和真实构建产物 `dist/build/mp-weixin/`，不能只看页面代码。
