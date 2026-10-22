# 名片夹日期语义与操作区布局收口 - 执行记录

## 2026-09-02

- 已完成问题调查：裸 `9/2` 来源为前端对 `lastUpdate` 执行无标签月/日格式化；后端和 DTO 已提供 `publishedAt`。
- 已确认实现边界：前端单页布局与日期语义，不修改后端、数据库、路由和 DTO。
- 已完成源码调整：已发布卡按 `publishedAt || lastUpdate` 显示“发布于”，草稿按 `lastUpdate` 显示“更新于”；当前年省略年份，跨年补年份，无效日期不渲染。
- 卡片已重排为 `card-main + card-actions + delete-error`。移除 Tab 内重复状态标签，封面固定 `112rpx x 112rpx`；已发布操作三等分，草稿操作两等分，操作高度 `64rpx`，删除错误回到正常文档流。
- 新增 `scripts/verify-00253-card-list-layout.mjs` 和 `verify:card-list-layout`，源码基线预期失败 7 项，修改源码通过 8 项，构建后源码/产物合计 15 项通过。
- `npm run type-check`、`npm run verify:v3-card-list`（13 项）、`npm run verify:single-runtime-entry` 均通过。
- 通过项目级 MCP 只关闭并退出固定 dev 工程后，`npm run build:mp-weixin` 成功直接写入唯一 `dist/dev/mp-weixin`，构建基址为 `https://test-api.kplyyk.com`。运行产物中本地 API 0 处、测试 API 3 个文件、正式 API 0 处。
- MCP 产物检查确认 `pages/card-list/index` 三件套完整且 scoped hash 状态一致；JS/WXML/WXSS SHA-256 分别为 `71BEAFDFE8B5088583845AAB9A92A7CF541754B46D19C5A53DB07A2CA15AEAEB`、`081FA70F02CD7EF069A9AF9AA675FC4B960A5F83ACB92748C359A5B56352081E`、`9F9D9EEAC91B5C194164EA91C6EDC1BC9A662920AFD51F6A96212310474CCD86`。
- MCP 内部模拟器截图显示“发布于9月2日”和横向三操作；操作栏 `344 x 33px`、信息区 `364 x 82px`，控制台 `grep -i error` 为空。截图：`.sce/evidence/wechat-devtools/00-253-card-list-layout-20260902.png`，SHA-256 `B91E6A1BBD41A81F11F5FA355AC94B40066E3EC97C6D2B7074EFC5568B044545`。
- `npm run audit:mp-package` 的所有包均低于 2 MB，但全局外链门禁仍因其只允许 `api.kplyyk.com`、不识别测试域名 `test-api.kplyyk.com` 而报告 4 处既有失败；本次没有扩大范围修改该门禁。
- 事务证据和回滚副本测试见 `evidence/VERIFICATION.txt`。业务源码与 `MODIFIED_FILE.vue` 保持修改态，回滚仅作用于 `ROLLBACK_TEST_COPY.vue`。
- 本次源码和运行产物变化已使旧 Candidate 验收失效，下一步必须重新冻结 Candidate；正式发布继续为 `NOT_AUTHORIZED`，未执行生产操作。
