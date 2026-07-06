# 00-189 当前阶段小程序全量 E2E 截图与文档整理审计 - 任务拆解

## T1 建立 Spec 与启动基线

- [x] 新增 `00-189` requirements / design / tasks / execution。
- [x] 执行 `npm run build:mp-weixin`，确保 `dist/dev/mp-weixin` 是最新镜像。
- [x] 使用 launch skill 脚本打开 `dist/dev/mp-weixin`。
- [x] 保存 DevTools 启动结果到 `output/miniapp-e2e/00-189/<run-id>/launch-result.json`。

## T2 页面与流程清单生成

- [x] 从 `dist/dev/mp-weixin/app.json` 生成主包与分包页面清单。
- [x] 为需要参数的页面补最小参数策略。
- [x] 为需要登录的页面补演员 / 剧组测试 session 注入策略。
- [x] 输出业务流程矩阵。

## T3 全页面截图 E2E

- [x] 编写 `miniprogram-automator` 截图脚本。
- [x] 启用 automator 端口 `19425`。
- [x] 对每个页面执行 `reLaunch` / `switchTab`、等待、读取 `page.data()`、截图。
- [x] 写入 `full-page-screenshot-manifest.json`。
- [x] 记录失败页面和失败原因；最终验收 run 中 `failedCount=0`。

## T4 业务流程 E2E 复核

- [x] 游客首页浏览与账号入口登录门禁流程。
- [x] 登录页按钮响应流程。
- [x] 演员首页与创建分享页流程。
- [x] AI 分享图与实名 / 分析图门禁流程。
- [x] 作品集、分享预览、公开详情与历史记录流程。
- [x] 我的页、协议设置与操作指南视频流程。
- [x] 旧剧组 / 投递保留页面运行态截图与当前主线关系记录。

## T5 旧文档整理

- [x] 扫描 docs 与 `.sce/specs` 中小程序相关文档。
- [x] 输出 `doc-audit-matrix.md`。
- [x] 标记保留、更新、归档、后续验证项。
- [x] 不直接改写历史执行记录，只整理当前引用口径。

## T6 回填与验收

- [x] 回填 `execution.md`。
- [x] 更新 `.sce/specs/README.md`。
- [x] 更新 `.sce/specs/spec-code-mapping.md`。
- [x] 汇总截图覆盖率、流程覆盖率、失败项和环境阻断项。
