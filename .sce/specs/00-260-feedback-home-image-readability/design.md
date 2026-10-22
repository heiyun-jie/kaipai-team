# 技术设计

## 1. 调查
- 读取图库 seed URL 的HTTP状态、图库服务响应与列表封面签名实现。
- 核查 t-image、原生 image 及已有 image 错误回调，不以图片占位文本代替网络证据。
- 拒绝暴露凭据、读取全局微信存储或抢占桌面。

## 2. 实现边界
- 七张 seed 图片在普通与微信 Referer HTTP Range 请求下均返回 206 image/png；目前没有证据表明其需要额外签名。图库服务保持原读取合同，不盲改签名或 COS ACL。
- 2026-10-16 用户提供的公众平台截图确认 `downloadFile` 合法域名已包含 `kaipai-prod-1412601014.cos.ap-shanghai.myqcloud.com`，排除缺少该主机白名单的假设。COS 原图及图片处理响应带 `Content-Disposition: attachment` / `x-cos-force-download: true`，首页先通过 `downloadFile` 得到临时文件，再交给图片组件渲染。
- MCP console 进一步捕获真实请求：接口中的 `.png` 后被追加未编码引号、反斜杠、HTML 和外站跳转片段，模板变为 404，私有草稿对象变为 403。前端只提取首个合法 HTTPS 图片 URL；后端 `AiGeneratedImageStorage` 在 URL 读取边界截断非法后缀，使受管私有 COS 恢复对象识别并签发短时 URL。不得请求、跟随或记录污染片段中的外站地址。
- 经典 PNG 单张 2,771,360 B，古风 PNG 8,705,884 B；COS 图片处理生成约 38 KB JPEG。文件体积不是根因，但派生缩略图继续作为性能优化保留。
- 草稿列表沿用已有受管主视觉响应期签名。前端清洗后公开可读草稿已恢复；私有 `kaipai-test-*` 对象必须依赖本次后端清洗后再签名，未部署旧后端仍会返回 403，不能由前端绕过 ACL。
- 前端维护每张模板缩略/原图失败状态与重试，页面重入重新请求图库以更新签名。
- 渲染项持有当次 URL 的错误回调；旧缩略图重复 error 不能把刚回退的原图标为失败。
- 若草稿封面已签名，不重复造并行读取协议；验证失败回退是否也需要签名。

_Requirements: 2_

## 3. 验证
前端回退、污染后缀清洗、downloadFile 临时文件、缓存与竞态行为测试；后端受管 COS 污染值签名测试；home 门禁、type-check、构建及固定 dev 登录态截图。2026-10-22 已复验测试后端部署后的私有草稿封面，详见 execution.md；真实手机仍待用户验收。

隔离核验支持 `CHECK_MP_DIR` 显式产物目录和 `sync-mp-weixin.ps1 -ArtifactOnly -ArtifactDir`，默认测试入口仍是固定 dev。显式归一化不得指向固定运行入口，也不得清缓存或镜像 dev。

静态包体外链白名单补入既有测试接口 `test-api.kplyyk.com`（与正式 `api.kplyyk.com` 和主站一样采用精确主机名）；未知域名继续阻断。这只消除正常测试产物误报，不代表微信平台已准入任何图片域名。
