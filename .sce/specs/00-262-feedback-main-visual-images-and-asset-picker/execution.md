# 00-262 执行记录

## 2026-10-22：固定 dev 修复与内部核验

- 用户批准局部修复，不改生产、不发布正式版；后续确认三张手机截图来自体验版，并明确授权上传新的测试体验包、替换体验版。上传/设体验版结果单独在 Candidate 记录登记，不能把授权当作完成。
- 根因一：首页 00-260 清洗与临时图片链路没有覆盖首图页；首图页直接渲染污染 URL。根因二：首图入口限定四类且默认 portrait，已有生活照等被默认筛掉。
- 用户首页截图与当前固定 dev 文案不同，存在版本差异线索；体验版不会自动跟随本地构建，仍待新包与真机验收，不宣称旧包是唯一原因。
- 实现：分包内自包含 image-preview 工具、严格 HTTPS 图片 URL 提取、模板缩略/原图候选、重试与卸载/修订号隔离；稳定 URL/assetId 与 displayUrl 分离。首图素材选择默认全部照片和完整七分类，其他用途不变，“全部”上传仍使用 portrait。
- 运行试验纠偏：强制私有素材也走 downloadFile 时首图失败/等待，而素材库和原生 image 正常。因此保留私有素材现签原生渲染，仅模板/历史 URL 下载临时文件；未取得下载失败的确切网络原因，不臆测域名/签名故障。
- 截图复核又发现“图库缩略正常、点击模板大图失败”：大图只下载原图。补齐原图优先、图库候选回退和解码失败回退，实际点击模板后大图恢复；始终保存原稳定身份，不保存缩略临时文件。

## 验证

- TDD：初始真实页面脚本6条失败、2条通过；后续卸载/安全诊断/私有预览补充先红后绿；最后模板大图下载与解码回退2条先失败，再修复。最终 `npm run verify:main-visual-images` **17/17**。
- `npm run type-check` 通过。
- `verify:feedback-october` 14/14；`verify:v3-home` 17；`verify:v3-asset-wizard` 68；`verify:actor-card-single-main-visual` 21；`verify:actor-card-step-ui` 13。
- 最终 `npm run build:mp-weixin` 返回 RUNTIME_BUILD=PASS；构建前正常 quit，等待工具进程退出，不绕过门禁。日志 `tmp/00-262-runtime-build.log`。既有 Sass/Browserslist/empty-chunk 警告不代表失败。
- `audit:mp-package` / `verify:single-runtime-entry` / `audit:steering` 全通过。main 1,410,108 B；pkg-actor-card 311,014 B；pkg-profile 169,291 B；pkg-card 130,624 B；pkg-tools 42,860 B，均低于单包2MB。
- 独立只读评审无阻断项，复跑专项17/17与type-check通过。

## 运行证据

目录 `.sce/evidence/wechat-devtools/20261022-feedback/`，固定 `dist/dev/mp-weixin`，仅内部 simulator，不使用桌面截图/坐标/键鼠/置顶：

- `step-visual-fixed-final.png`：私有素材首图正常。
- `step-visual-template-fixed-final.png`：三张模板正常。
- `step-visual-template-selected-final.png`：实际点击模板，大首图正常；未点击下一步保存。
- `source-picker-all-fixed-final.png`：首图选择默认全部照片，10张均显示；未点击确认，无素材/卡片写入。
- `home-images-fixed-final.png`：最新运行态首页模板与草稿封面正常。
- `00-262-runtime-redacted.json`：页面数据只保存脱敏版本，不含签名URL/token。

中间 `step-visual-template-selected.png`、`step-visual-fixed.png` 为失败试验，不能用作最终通过证据。

## 发版与剩余验收

- API/后端/数据库/COS ACL均未变；测试后端已是10-20 Candidate，无需重复部署。
- 用户已授权测试体验版更新；需新冻结 Candidate，只有 mini-program-test 可上传；不上传 release 产物，不修改线上正式版。上传与设体验版是两个独立结果，均需证据。
- 手机三处图片与选择/保存/重进待验，T6保持未完成。自动门禁与模拟器不替代真机或生产GO。

## 体验版更新准备：门禁未通过，尚未上传

- 用户明确授权后生成 Candidate `20261022-143750-v3-draft`，隔离 commit+显式overlay构建四类产物通过，test/release API目标扫描均通过。未部署任何新后端/后台，也未上传小程序。
- 测试小程序330文件、2,063,041 B，tree SHA256 `69e2b2167d2afa8a8909e5bc93b24ca09490c62e0e0f5e7689dbd1d34c784cc6`；后端JAR与已运行测试JAR一致 `2c54fa5c0caea22224c35762b7ffa7e22eb9f248bf66acd706b871c07afd3580`。
- Candidate隔离源码再次通过专项17/17与type-check。本轮相关路径diff --check通过；全仓另有既存CORE_PRINCIPLES.md尾部空行，不改他人内容。
- 新发版审计 `DEPENDENCY_AUDIT_REVIEW_PENDING`：admin high=5/critical=0；mini-program high=49/critical=0，尚未复核的advisory包为 @vue/server-renderer、baseline-browser-mapping、braces、source-map-js。不能把无工具链marker等同于所有新增告警都已复核，也不能覆盖gate为PASSED。
- 准入脚本返回 `INVALID_CANDIDATE / exit 2`，明确原因 `candidate manifest contains blockers that affect test acceptance`。Candidate仍为DRAFT/NO-GO，**未完成冻结、未上传、未设体验版**；没有绕过门禁。等待用户裁决是否另建依赖修复Spec继续；生产GO仍未授权。
- 原始脱敏审计及准入输出：`records/20261022-143750-v3-draft/00-262/{frontend-audit-full,admin-audit-full,acceptance-gate}.json`。构建日志 `tmp/00-262-candidate-build.log`。后续依赖/源码变化必须新Candidate，不能继续使用本DRAFT宣称准入。
- Chrome已打开公众平台登录页并保留；该登录独立于微信开发者工具登录。尚未进入版本管理或修改云端体验版。

## 00-263后续交付已完成（覆盖上述待授权/未上传状态）
- 用户已授权依赖审计处理与体验版更新。00-263通过独立评审、双根四产物一致性、固定dev同源与测试准入，Candidate `20261022-150736-v3-draft` 已上传为 `3.0.0.20261022.151525`；公众平台新版本带体验版标记，旧9月体验版已被替换。
- 当前截图：trial-candidate-home.png、trial-candidate-step-visual.png、trial-candidate-source-picker.png、trial-version-updated-full.jpg。首页、首图、默认全部照片10张均正常。
- 正式版仍1.0.0，未提交审核/发布、未部署后台/后端、未改生产；真机图片与选择保存回读仍待用户验收。详见00-263 execution与对应records。
