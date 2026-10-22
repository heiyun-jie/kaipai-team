# 00-251 执行记录

## 实施范围

- 后端公开演员卡响应增加可选 `profile.skillGroups`，旧 `profile.skills` 保留。
- 共享 `ActorCardRenderer` 以职业能力 / 职业特长生成技能区，角色方向独立展示，作品类型只留在拍摄经历。
- 移除前端拼接的固定技能说明。

## 已执行命令

| 阶段 | 命令 | 结果 |
|------|------|------|
| 基线 | `mvn -Dtest=ActorCardMainVisualResolverTest test` | `6/6`，exit `0` |
| 修改后端 | `mvn -Dtest=ActorCardPublicServiceImplTest test` | `11/11`，exit `0` |
| 前端类型 | `npm run type-check` | exit `0` |
| 源码门禁 | `$env:CHECK_MP_TARGET='build'; npm run verify:actor-card-skill-semantics` | PASS，exit `0` |
| 构建 | `npm run build:mp-weixin` | uni build exit `0`；postbuild 镜像被运行中的微信工具保护拦截 |
| 构建产物归一化 | `powershell -ExecutionPolicy Bypass -File scripts/sync-mp-weixin.ps1 -ArtifactOnly` | `dist/build` scoped hash consistent，exit `0` |
| 包体 | `npm run audit:mp-package` | 包体均低于 `2 MB`；既有 4 处本地 API URL 审计失败，exit `1` |

## 产物状态

- `dist/build/mp-weixin/pkg-actor-card/components/ActorCardRenderer.*` 已包含 00-251 修改。
- `dist/dev/mp-weixin` 未被脚本镜像；微信开发者工具仍在运行，默认同步被项目保护拦截。
- 未打开新 DevTools 窗口，未结束、置顶或抢占用户当前工具。
- 正式后端、正式数据库、正式 Nginx 和正式小程序未触碰。

## 待恢复的验收前置

在微信开发者工具完全退出后，重新执行 `npm run build:mp-weixin`，确认 `dist/dev` 与 `dist/build` 的 Renderer 三件套等价，再运行默认的 `npm run verify:actor-card-skill-semantics` 和既有演员卡门禁，随后才可进行 MCP 截图验收和新 Candidate 冻结。

## MCP 只读复测

- 固定工程：`D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin`
- 页面：`pkg-actor-card/generate/index?cardId=1&preview=1`
- `runtime_info(currentPage)`：成功，当前页面路径与查询参数匹配。
- `get_simulator_console(grep -i error)`：空结果，exit `0`。
- 截图：[00-251-skill-generate-dev.png](D:/XM/kaipai-team/.sce/evidence/wechat-devtools/00-251-skill-generate-dev.png)
- 观察：Hero 仍展示“影视表演 / 短剧 / 情感戏 / 现代戏”，统计仍为 `12+`，证明运行态仍加载旧 `dist/dev` Renderer；不能作为新实现验收证据。
