# 执行记录（2026-10-22）

## 审查结论与约束
- 用户明确批准必要依赖处理及测试体验版替换；公众平台当前线上1.0.0（2026-07-06）不动，当前体验包3.0.0.20260902.174419（2026-09-02）确实早于00-262修复。
- 管理端本地vue 3.5.31→3.5.44、axios 1.19.0→1.20.0、source-map-js 1.2.1→1.2.2，production audit high/critical/total均0，typecheck+vite build通过。未部署管理端，未改后端与数据库。
- 小程序lock完全不变，避免破坏uni内部固定Vue3.4.21合同。真实新告警入口：SSR renderer由uni-cli/H5与Vue依赖引入；baseline-browser-mapping由browserslist构建目标计算引入；braces由chokidar/micromatch文件模式引入；source-map-js由SFC/CSS/Sass源码映射工具引入。小程序入口不执行SSR，不提供通用源码映射或glob解析API。
- 检查旧Candidate最终微信产物：无renderToString/ssrRenderAttrs/SourceMapConsumer、browser-mapping与braces模块标记，无map/Node包清单/工具链marker。运行i18n/core-base均9.14.5，旧9.1.9仅工具链使用。不是凭“包名不在文件名中”判定不可达。
- 对当前66项name|advisory URL身份建立显式review policy，绑定本次frontend lock SHA。涵盖已接受的编译器/CSS/source-map、文件glob、图像/ZIP本地转换、Node下载/WebSocket、dev-server工具类别；不接受H5/SSR或对外dev-server使用。构建只处理仓库受控源码/素材，不输入外部ZIP、任意sourceMappingURL或网络glob。没有声称原始npm audit计数归零。
- 既有风险期限09-30已过，旧实现没有执行到期检查。本次基于重新审查续至11-05，并真正执行当前时间检查；准入时再次检查，不能先构建再无限期使用旧证据。锁变化、未知URL（即使包名已知）、critical、产物marker均拒绝。新增审查只登记可达性结论，不降低high/critical或未知门禁。

## TDD与验证
- 新增过期、4个SSR/工具marker、已知包的新advisory：首次6个断言失败；实现后通过。
- 新增准入拒绝已过期的FROZEN/GO manifest，先红（未抛错）再绿。
- 独立评审发现npm audit可解析错误JSON被旧代码默认为0告警、.wxs未纳入扫描。新增3种错误JSON与WXS marker先4断言失败，再修复；审计错误/缺失结构/异常退出直接失败，不能将网络失败视为干净报告。最终builder16项、准入13项、generator6项通过。
- 补lock变化/critical拒绝，build脚本12项通过；生成器6项通过；图片17/17与原反馈14/14、前端typecheck通过。
- 后续Candidate、双根重建、固定dev、准入与上传云端结果记录在对应records目录，未获这些证据前不标T4/T5完成。

## 独立评审收口与最终候选准备
- reviewer review_00262 最终无阻断：错误审计JSON、WXS与真实test/release双环境扫描均复核通过；真实advisory与policy 66/66精确匹配，无missing/stale，lock一致。
- 本轮重新执行builder16/16、准入13/13、generator6/6通过。真实build_frontend已接入classify_miniprogram_artifacts，test包独有marker也会拒绝。
- 20261022-150243-v3-draft在最后双环境扫描改动前启动，仅保留诊断，不用于最终上传；源码及治理说明固定后另建最终Candidate，重新构建与双根复现。

## 最终Candidate、准入与体验版交付
- 最终Candidate `20261022-150736-v3-draft` 从固定源码生成；四类产物隔离构建成功，并在第二绝对目录独立重建，backend/admin/mini-test/mini-release 的size/SHA或tree SHA全部一致，`reproducibility.json passed=true`。两个环境依赖分类均PASSED；管理端production audit为0。
- test产物330文件、2,063,041 B，tree SHA `69e2b2167d2afa8a8909e5bc93b24ca09490c62e0e0f5e7689dbd1d34c784cc6`。MCP正常quit并等待退出后备份原固定dev，再复制此test产物；未写workspace dist/build。物化前后、MCP运行后、上传后均核对fixed dev树一致。
- 内部MCP真实打开home/首图/素材选择，无setData或mock注入；首页返回2草稿/3模板，首图正常，素材选择默认全部照片、10张照片均显示。未点下一步/确认，不做卡片/素材写入。对应脱敏页面数据、runtime-readiness与截图已落盘。
- 测试API唯一，test marker3文件、production/local0；package/single-runtime/steering通过。测试API curl只读HTTP200。后端JAR及迁移与10-20已部署服务完全一致，仅复用既有部署与当天只读证据，不重复部署或迁移。
- `verify-test-miniapp-acceptance.py --candidate-id 20261022-150736-v3-draft` 上传前及上传后均 `READY_FOR_MANUAL_ACCEPTANCE / exit0`。生产helper/凭据两门仍DRAFT/NO-GO，测试准入按既有边界处理，未伪造生产GO。root manifest在新增运行截图后不再全量CURRENT，差异最初仅3张新增证据，已单独留档；backend/admin/frontend三个运行输入均CURRENT。后续本Spec/索引回填只改治理记录，不改冻结运行源码。
- CLI上传 `3.0.0.20261022.151525` 成功（exit0）。微信上传口径total2,871,215 B，main1,954,138 B（离2MB余143,014 B）；4分包均低于2MB，不能将静态audit1,409,252 B主包与微信处理后口径混为一谈。
- 公众平台回读开发版本 `3.0.0.20261022.151525`、提交时间2026-10-22 15:16:27并带“体验版”标记；本次上传自动继承该开发者原体验版指定，无需重复设体验版。旧9月版本已被替换，不是只上传未设体验版。`00-263/cloud-trial-proof.json` 与 `trial-version-updated-full.jpg` 记录此事实。
- 线上仍1.0.0（07-06），审核区无待审版本；没有提交审核、正式发布、后台部署或生产更改。用户手机实测仍待完成，T6保持未勾选。

重跑准入：`python .sce/runbooks/backend-admin-release/scripts/verify-test-miniapp-acceptance.py --candidate-id 20261022-150736-v3-draft`。
