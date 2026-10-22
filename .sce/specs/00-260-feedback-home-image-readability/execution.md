# 执行记录

## 2026-10-13 调查与本地修复

### 证据与实现

- 读取七个背景图库 seed COS URL，普通 HTTP Range 请求返回 `206 image/png`；加微信 `https://servicewechat.com/wx4dcc4e1066fd0fb9/0/page-frame.html` 和 `/1/` Referer 同样可读。因此暂不支持“图片已删除、公开 COS 拒读或 Referer 防盗链”归因。
- 没有取得反馈截图账号对应的请求、签名状态或微信平台域名读回。截图完整根因未闭合，不把桌面 HTTP 可读当作真机可读。
- 首页模板缩略图失败回退原图，两者都失败显示“图片暂不可用 / 重新加载”。每个渲染项保存当次 URL 的错误回调，缩略图旧 error 不误伤原图。
- 草稿封面错误显示重试，重拉列表获取既有后端封面签名；保留主视觉来源合同，不另造封面签名 API。
- 页面重入强制获取图库；账号隔离风格缓存，重取后清失败状态。请求序号、账号、token 防止旧风格或旧账号返回覆盖当前列表。
- 图库服务、COS ACL、图片域名平台配置均保持原合同；没有证据支持盲改签名或权限。

### 构建与验证

| 检查 | 结果 |
|------|------|
| 首页行为回归（合并 11 项专项） | 缩略/原图回退、旧 error、COS 派生缩略、重新现签、风格竞态、草稿重试通过 |
| `npm run verify:v3-home` | 17 项通过 |
| `npm run type-check` | 通过 |
| 隔离 uni 构建 + ArtifactOnly 显式目录归一化 | 通过；不作为新的微信项目入口 |
| `npm run build:mp-weixin` | 固定 dev 构建与 scoped 哈希核验通过 |
| 固定 dev home WXML | 有失败态、重新加载、草稿重试与新的 URL 绑定 |
| 包体 / 单入口 / steering 审计 | 通过 |

首页门禁存在一条历史断言漂移：仍要求 `backgroundImageUrl: selectedBgUrl.value`。已按 00-242 更新为素材来源清空、图库来源的 `backgroundImageUrl/sourceImageUrl` 双字段同步合同，没有放宽为不检查。

原始 uni 隔离产物有编译链远程字体与文档 URL，已由现有归一化流程移除。新增 `sync-mp-weixin.ps1 -ArtifactOnly -ArtifactDir` 支持显式隔离目录，禁止与其它模式混用或指向固定 dev；TDesign 和网格门禁增加 CHECK_MP_DIR。默认检查入口仍为固定 dev。

审计原白名单遗漏构建器默认 `https://test-api.kplyyk.com`，导致四个合法 API 字符串误报；已精确增加测试主机，同时按主机边界匹配，拒绝 `api.kplyyk.com.evil.invalid`。未知外链负例仍退出 1。此静态白名单不等于微信平台域名准入。

固定 dev 包体（apparent bytes）：主包 1,409,185；pkg-actor-card 302,420；pkg-card 130,624；pkg-profile 168,943；pkg-tools 42,860，均低于 2,097,152 B。

隔离日志位于 ignored release records 的 `20261013-feedback-local/feedback-frontend-build.log`；固定构建日志为同目录 `feedback-runtime-build.log`。没有把工作区 dist/build 作为日常运行入口。

### 待闭合

截图完整失败请求、真机图片加载和 00-257 域名准入仍待验。本轮完成可回退、可重试与新签名获取能力，不能声称反馈的网络根因已经全部修复。新 Candidate 需要重新冻结后再验证。

## 2026-10-16 登录态 MCP 运行核验

- 用户明确授权后，仅通过微信开发者工具内部 simulator MCP 打开固定 `dist/dev/mp-weixin`；未使用桌面截图、坐标或键鼠自动化。
- 登录态个人页的档案照片、素材库 10 张照片均成功显示；首页 3 张经典模板仍进入“图片暂不可用”，两张草稿封面进入重试态。
- 七个背景源文件检查：六张 720×1280 PNG 各 2,771,360 B，一张 2160×3840 PNG 为 8,705,884 B，均是接近未压缩体积的 RGB PNG。
- 腾讯 COS `imageMogr2/thumbnail/360x/format/jpg/quality/80` 实测将经典模板降到 37,897 B，HTTP 200 / image/jpeg。前端已优先使用派生缩略地址，同 URL 失败后回退原图，专项回归扩至 11/11，固定 dev 重建通过。
- 重建后模拟器仍失败，因此文件体积不是唯一根因；页面无 console error/fail/domain 日志。当前优先假设转为 `kaipai-prod-1412601014.cos.ap-shanghai.myqcloud.com` 未进入该 AppID 的 download 合法域名，或该主机存在微信图片组件特有准入差异。
- 00-257 的只读远端域名脚本尝试读回时，微信 `modify_domain/get` 返回 `40014 invalid access_token`，没有修改远端配置。不得据此声称域名已读回或已修复。
- 运行截图保存于 `.sce/evidence/wechat-devtools/20261016-feedback/`：`mine-authenticated.png`、`profile-edit-authenticated.png`、`assets-authenticated.png`、`assets-actions.png`、`home-authenticated-fixed.png`。

## 2026-10-16 根因闭合与第二轮修复

- 用户提供公众平台「服务器域名」截图，确认 `downloadFile` 合法域名已有 `https://kaipai-prod-1412601014.cos.ap-shanghai.myqcloud.com`；证据保存为 `downloadfile-domain-config-user.png`。因此撤销“缺少 prod COS 白名单”的优先假设。
- COS 原图和缩略图响应均含 `Content-Disposition: attachment`、`x-cos-force-download: true`。前端改为 `uni.downloadFile` 成功后使用临时路径渲染，保留缩略图 → 原图回退、账号/请求序号隔离和重试。
- 首次 downloadFile 运行日志暴露真实 URL 尾部污染：合法 `.png` 后追加未编码引号、反斜杠、HTML 与外站跳转片段。该异常字符串直接造成公开模板 404；私有测试桶对象在未被受管存储识别/签名时返回 403。没有请求污染片段内的外站地址。
- 前端 `extractSafeRemoteImageUrl` 只提取首个合法 HTTPS 图片 URL；日志只记录 host/status，不输出可能含签名的完整 URL。后端 `AiGeneratedImageStorage` 在统一读取边界截断 URL 中未编码的引号、尖括号、反斜杠和空白，使受管私有 COS 对象恢复识别并签发短时 URL；数据库原值不在本轮直接修改。
- 固定 dev 登录态复验：三张经典模板全部显示；两张草稿中一张公开可读封面恢复，另一张私有测试桶封面仍由旧测试后端返回 403，需部署本次后端兼容修复后再验。截图：`home-final-fixed.png`。
- 前端 `verify:feedback-october` 扩为 12/12，覆盖污染后缀；`type-check` 与 `verify:v3-home` 17 项通过；`npm run build:mp-weixin` 返回 `RUNTIME_BUILD=PASS`；steering 与包体审计通过，主包 1,415,558 B。后端 `AiGeneratedImageStorageTest,ActorCardPublishServiceTest,ActorCardMainVisualResolverTest` 共 22 项通过。
- 发版兼容：接口字段、数据库结构和 ACL 均不变；后端清洗/签名是兼容增量，必须先于或同批前端部署。当前未部署、未上传、未发布。

## 2026-10-22 测试后端部署事实纠偏与登录态复验

- 用户本轮明确授权部署测试环境后端；核对发现 Candidate `20261020-173705-v3-draft` 已于 10 月 20 日成功部署测试环境。原记录：`.sce/runbooks/backend-admin-release/records/20261020-173705-v3-draft/00-247/tat-deploy-result.json`（TAT `inv-ua56s80m86`，SUCCESS / exit 0）。因此本轮不重复迁移或重建，不改生产、ACL 或数据库原始 URL，不上传或发布小程序。
- 冻结快照重新执行 `mvn -Dtest=AiGeneratedImageStorageTest,ActorCardPublishServiceTest,ActorCardMainVisualResolverTest,ActorProfileWriteServiceImplTest,ActorProfileControllerContractTest -Dproject.build.outputTimestamp=2000-01-01T00:00:00Z clean package`：38 项测试，0 failures / errors，BUILD SUCCESS。JAR SHA256 为 `2c54fa5c0caea22224c35762b7ffa7e22eb9f248bf66acd706b871c07afd3580`，与冻结 Candidate、远端测试磁盘 JAR 和 10 月 20 日容器 JAR 证据一致。此为专项测试，不宣称完整后端套件通过。
- 本轮只读 SSH 标准 helper 诊断：测试容器 running，`startedAt=2026-10-20T09:41:39.339751999Z`、`restartCount=0`，与部署记录吻合；生产容器仍 Up 3 months。本轮未执行任何服务变更命令。
- TAT API 本地 TLS 握手两种连接方式均失败，未发起远端部署；切换 SSH 标准 helper 的只读诊断完成状态核验。helper 不暴露 fresh 容器 JAR 哈希，不能把本轮磁盘哈希冒充为本轮容器内哈希；容器哈希来自 10 月 20 日部署记录。
- 仅使用固定 `kaipai-frontend/dist/dev/mp-weixin` 和内部 simulator MCP 打开 `pages/home/index`，保留用户现有登录态。page data 中 cardId 3、4 的封面均已下载为 `http://tmp/*.png`，三张经典模板均为 `http://tmp/*.jpeg`，错误状态均 false；截图目视确认此前失败的私有草稿封面与公开草稿封面均显示。console error 读取为空；未读取 token、全局存储或完整签名 URL。
- 新证据：`.sce/evidence/wechat-devtools/20261022-feedback/home-backend-verified.png`、`home-image-runtime.json`；服务诊断：上述 Candidate `00-260/runtime-reverification-20261022.json`。
- 结论：测试后端修复已生效，模拟器私有草稿验收通过。用户真机验收仍待完成；不把模拟器结果当作真机/正式发布 GO。
