# 00-189 当前阶段小程序全量 E2E 截图与文档整理审计 - 技术设计

## 1. 设计结论

本轮按四层产出闭环：

```text
DevTools 启动
  -> 固定打开 dist/dev/mp-weixin
  -> 记录 CLI 登录态、工程路径、模拟器 ready 状态

页面截图 E2E
  -> 从 dist/dev/mp-weixin/app.json 自动生成页面目标
  -> 用 miniprogram-automator 注入 / 清空 session
  -> 每页截图 + page.data 快照 + manifest

业务流程 E2E
  -> 在页面截图基础上补关键路径
  -> 游客浏览 / 登录门禁 / 创建分享 / AI 分享图 / 公开详情 / 我的设置等流程生成矩阵

旧文档整理
  -> 扫描 docs 与 .sce/specs
  -> 输出保留 / 需更新 / 历史归档 / 后续修复矩阵
```

_Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

## 2. 运行目录与工具

- 微信开发者工具工程目录：`kaipai-frontend/dist/dev/mp-weixin`
- DevTools 启动脚本：`C:\Users\33340\.codex\skills\launch-wechat-miniprogram\scripts\launch-wechat-miniprogram.ps1`
- Automator 依赖：`.sce/tools/mp-automator/node_modules/miniprogram-automator`
- 输出目录：`output/miniapp-e2e/00-189/<run-id>/`

输出结构：

```text
output/miniapp-e2e/00-189/<run-id>/
├── screenshots/
├── captures/
│   ├── page-data-*.json
│   ├── full-page-screenshot-manifest.json
│   └── miniapp-e2e-progress.log
├── flow-matrix.md
├── doc-audit-matrix.md
└── launch-result.json
```

_Requirements: 3.1, 3.2, 3.5_

## 3. 页面截图目标生成

脚本从 `kaipai-frontend/dist/dev/mp-weixin/app.json` 读取：

- `pages[]` 主包页面。
- `subPackages[].root + pages[]` 分包页面。

默认截图策略：

- `pages/home/index`、`pages/login/index`、`pkg-tools/webview/index?type=...`、`pkg-tools/video-player/index?type=guide` 可游客态截图。
- 账号页、演员档案、创建分享、AI 分享图、作品集、实名、邀请、能力中心、收藏等使用演员测试 session。
- 历史剧组页、投递页、项目创建页如当前主线已迁出但页面仍存在，则记录为“保留代码运行态截图”，不把业务闭环失败直接等同当前主线阻断。

参数页默认参数：

- `pages/actor-profile/detail?shared=1&shareCardId=<shareCardId>`。
- `pkg-card/actor-card/index?shareCardId=<shareCardId>&artifact=miniProgramCard`。
- `pkg-card/actor-card/index?shareCardId=<shareCardId>&artifact=poster`。
- `pkg-card/style-detail/index?scene=urban`。
- `pkg-tools/webview/index?type=privacy`，并补 `user/about/notice/preferences/default` 作为同页多状态。
- `pkg-tools/video-player/index?type=guide`。

若无法从后端或本地 session 推导 `shareCardId`，该类页面仍进入目标，但 manifest 中记录 `missing-parameter`。

_Requirements: 3.2_

## 4. 业务流程矩阵设计

流程矩阵字段：

| 字段 | 说明 |
| --- | --- |
| flowId | 稳定 ID |
| name | 流程名 |
| entry | 入口页面 |
| precondition | 游客 / 演员 / 剧组 / 需数据 |
| steps | 关键步骤 |
| expected | 预期结果 |
| evidence | 截图或 manifest 证据 |
| status | passed / failed / blocked / static-only |
| issue | 问题摘要 |

本轮最低覆盖流程：

1. 游客打开首页并浏览。
2. 游客点击账号功能后进入登录页。
3. 登录页手机号快捷登录按钮有明确响应。
4. 演员进入首页并查看分享主线入口。
5. 演员进入创建分享页，完成风格 / 作品 / 预览三段页面检查。
6. 演员进入 AI 分享图页，检查实名与分析图门禁。
7. 演员进入已创建分享 / 作品集。
8. 分享卡预览：小程序卡片与海报。
9. 公开详情页。
10. 历史记录页。
11. 我的页与退出登录入口。
12. 协议、隐私、关于、通知、偏好设置本地内容页。
13. 操作指南视频页手动播放状态。
14. 旧剧组 / 投递相关保留页面运行态截图。

_Requirements: 3.3_

## 5. 旧文档整理矩阵设计

旧文档矩阵字段：

| 字段 | 说明 |
| --- | --- |
| docPath | 文档路径 |
| topic | 主题 |
| currentStatus | current / historical / stale / unknown |
| finding | 与当前运行态的关系 |
| action | keep / update / archive / split-spec / verify-later |
| ownerSpec | 对应 Spec |

扫描范围：

- `docs/*.md`
- `.sce/specs/README.md`
- `.sce/specs/spec-code-mapping.md`
- `.sce/specs/00-27-mini-program-frontend-architecture/`
- `.sce/specs/00-28-architecture-driven-delivery-governance/`
- `.sce/specs/05-*`
- `.sce/specs/00-14x / 00-17x / 00-18x` 中小程序相关 Spec

不直接重写历史执行记录；历史执行记录只标注为历史证据。

_Requirements: 3.4_

## 6. 验证设计

必须执行：

1. `cd kaipai-frontend && npm run build:mp-weixin`
2. `powershell -ExecutionPolicy Bypass -File C:\Users\33340\.codex\skills\launch-wechat-miniprogram\scripts\launch-wechat-miniprogram.ps1 -ProjectPath D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin`
3. 启用 automator：`微信开发者工具 cli auto --project ... --auto-port <port> --trust-project`
4. 运行全页面截图脚本。
5. 运行流程矩阵脚本或生成流程矩阵。
6. 生成旧文档整理矩阵。
7. 回填 `execution.md`、README、mapping。

成功标准：

- 至少生成所有页面目标的 manifest 记录。
- 可截图页面必须有 screenshot 文件和 SHA256。
- 失败页面必须有错误原因。
- 流程矩阵不得空白。
- 文档矩阵不得空白。

_Requirements: 3.5_
