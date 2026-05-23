# 00-158 设计

## 分层方案

### 小程序前端

新增 `kaipai-frontend/src/config/brand.ts`，集中保存小程序运行态品牌文案：

- `miniProgramName`
- `miniProgramShortName`
- `brandRomanName`
- `brandName`
- `shareCardTitle`
- `shareCardArtifactLabel`
- `miniCardBrandLine`
- `posterBrandName`

页面、工具函数和分享产物标签只引用该配置，不再在页面里定义 `POSTER_BRAND_NAME` 这类局部品牌常量。

登录页 hero、首页 micro copy 与海报 eyebrow 等短品牌露出统一读取 `brandRomanName`。当前按用户输入的 `kaupaile` 采用大写展示 `KAUPAILE`，与原 `JU MING PIAN` 的视觉字母样式保持一致。

### 后台管理端

新增 `kaipai-admin/src/constants/brand.ts`，集中保存后台壳层品牌文案：

- `platformName`
- `shortName`
- `miniProgramName`
- `adminTitle`
- `adminMark`
- `adminRomanName`
- `domain`

登录页、侧边栏、系统设置优先从该配置读取。`index.html`、`.env.*` 属于构建外壳配置，保留为静态配置，但内容应与品牌配置一致。

### 后端

新增 `BrandCopySupport`，保存后端返回给前端的品牌/分享产物文案。当前重点替换 `ActorPersonalizationServiceImpl` 中的分享产物标签。

### 构建产物

小程序 `dist/build/mp-weixin` 由 `npm run build:mp-weixin` 生成，`postbuild:mp-weixin` 会同步到 `dist/dev/mp-weixin`。本规格不依赖手写修改构建产物作为最终事实源。

## 微信平台边界

微信分享确认弹窗底部显示的小程序官方名称由微信公众平台账号资料决定，不由本地代码决定。代码侧只能保证：

- AppID 正确；
- 分享标题正确；
- 本地开发者工具项目名正确；
- 小程序内用户可见文案正确。

正式的小程序名称 `开拍了演员卡` 和简称 `开拍了` 仍需在微信公众平台提交并通过审核。

## 本轮调查命中

运行态源代码命中点：

- `kaipai-frontend/src/pkg-card/actor-card/index.vue`
- `kaipai-frontend/src/pages/login/index.vue`
- `kaipai-frontend/src/pages/home/index.vue`
- `kaipai-frontend/src/utils/actor-card.ts`
- `kaipai-frontend/src/utils/share-artifact.ts`
- `kaipai-frontend/src/utils/personalization-copy.ts`
- `kaipai-frontend/src/utils/verify.ts`
- `kaipai-frontend/src/pkg-card/capability/index.vue`
- `kaipai-frontend/src/pkg-card/verify/index.vue`
- `kaipai-frontend/src/pages/actor-profile/edit.vue`
- `kaipai-frontend/src/pkg-tools/webview/index.vue`
- `kaipai-admin/src/components/layout/AdminSidebar.vue`
- `kaipai-admin/src/views/auth/LoginView.vue`
- `kaipai-admin/src/views/system/SettingsView.vue`
- `kaipaile-server/src/main/java/com/kaipai/module/server/card/service/impl/ActorPersonalizationServiceImpl.java`

配置/外壳命中点：

- `kaipai-frontend/src/manifest.json`
- `kaipai-frontend/project.private.config.json`
- `kaipai-frontend/dist/build/mp-weixin/project.config.json`
- `kaipai-frontend/dist/dev/mp-weixin/project.config.json`
- `kaipai-admin/index.html`
- `kaipai-admin/.env.development`
- `kaipai-admin/.env.production`
- `kaipai-admin/.env.test`
