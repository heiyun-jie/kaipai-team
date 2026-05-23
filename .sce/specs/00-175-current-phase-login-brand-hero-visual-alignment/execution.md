# 00-175 Execution

## 1. 启动记录

- 用户反馈：`pages/login/index` 顶部太丑、不协调。
- 用户截图中可见问题：
  - 微信胶囊按钮与 hero 卡片顶部视觉距离不足。
  - 顶部暗色大块过重。
  - `KAIPAILE` 和 `开拍了` 字距过大。
  - hero 与下方登录 sheet 衔接生硬。
- 二次反馈：希望 hero 与登录 sheet 整体在屏幕中“居中偏上”，而不是贴近顶部后下方留出过大空白。

## 2. 实施记录

- 修改 `kaipai-frontend/src/pages/login/index.vue`：
  - 顶部从手写 status bar spacer 改为 `KpCapsuleSpacer`，按微信胶囊导航高度预留空间。
  - 移除不再使用的 `statusBarHeight` 状态和 `login-page__status-bar` 样式。
  - hero 卡片改为左下品牌锁定，避免品牌文字悬在大暗色块中间。
  - hero 从 `flex: 1` 改为内容自身高度，避免顶部暗色块被撑满首屏。
  - hero 背景改为暖灰暗色过渡，弱化硬暗色块。
  - `KAIPAILE`、`开拍了`、副标题、登录按钮等当前登录页可见文字的 `letter-spacing` 归零。
  - `开拍了` 字号从 `94rpx` 降为 `76rpx`，降低压迫感。
  - sheet 负 margin 和圆角微调，让登录卡片与 hero 衔接更柔和。
  - 未修改微信登录处理函数、短信登录隐藏门禁、后端接口或 Store。
- 二次修改 `kaipai-frontend/src/pages/login/index.vue`：
  - 新增 `login-page__stage` 结构容器，仅包住 hero 与登录 sheet。
  - `stage` 使用 `flex: 1 0 auto` 占据胶囊安全区之后的剩余空间。
  - `stage` 使用 `padding: 10vh 0 0` 将整组内容移动到屏幕居中偏上位置。
  - 未新增装饰节点，未修改登录接口、Store、微信授权处理或短信隐藏门禁。

## 3. 验证记录

- `npm run type-check`
  - 通过。
- `npm run build:h5`
  - 通过。
- H5 390x844 视口 DOM / 截图核验
  - URL: `http://127.0.0.1:4179/?v=stage2#/pages/login/index`
  - `innerWidth=390`
  - `scrollWidth=390`
  - `scrollHeight=844`
  - `kicker=KAIPAILE`
  - `title=开拍了`
  - `hasWrongRoman=false`
  - `hasOldRoman=false`
  - `hasOldTitle=false`
  - `hasPhoneText=false`
  - `hasSmsText=false`
  - `horizontalOverflow=false`
  - `heroWithinViewport=true`
  - `sheetWithinViewport=true`
  - `titleInsideHero=true`
  - `buttonWithinSheet=true`
  - `titleStyle.fontSize=39.52px`，对应 `76rpx`。
  - `stageStyle.paddingTop=84.4px`
  - `group.top=132.546875`
  - `group.bottom=570.625`
  - `group.centerRatio=0.41657101599526064`
  - `groupCenteredUpper=true`
  - `sheetBottomInFirstScreen=true`
- H5 390x667 较矮视口 DOM 核验
  - `innerWidth=390`
  - `innerHeight=667`
  - `scrollWidth=390`
  - `scrollHeight=667`
  - `horizontalOverflow=false`
  - `group.top=114.84375`
  - `group.bottom=552.921875`
  - `group.centerRatio=0.5005739317841079`
  - `sheetBottomInFirstScreen=true`
  - `buttonVisibleInFirstScreen=true`
  - `agreementVisibleInFirstScreen=true`
- `npm run build:mp-weixin`
  - 通过。
  - `postbuild:mp-weixin` 已同步到 `dist/dev/mp-weixin`。
- `npm run audit:mp-package`
  - 通过。
  - `main`: `518.01 KB / 2.00 MB`
  - `pkg-card`: `201.91 KB / 2.00 MB`
  - `pkg-tools`: `28.31 KB / 2.00 MB`
- 小程序产物文本 / 绑定核验
  - 核验文件：
    - `dist/build/mp-weixin/pages/login/index.wxml`
    - `dist/dev/mp-weixin/pages/login/index.wxml`
  - `HasStage=true`
  - `HasPhoneText=false`
  - `HasSmsText=false`
  - `HasSendCode=false`
  - `HasSmsSubmit=false`
  - `HasWrongRoman=false`
  - `HasOldRoman=false`
  - `HasOldTitle=false`
  - `HasBindGetPhoneNumber=true`
  - `HasOpenTypeBinding=true`
  - `HasWechatText=true`
  - `开拍了` 来自 `MINI_PROGRAM_BRAND` 运行时绑定，已在 `dist/build/mp-weixin/config/brand.js` 中核验。
- 小程序产物样式核验
  - 核验文件：
    - `dist/build/mp-weixin/pages/login/index.wxss`
    - `dist/dev/mp-weixin/pages/login/index.wxss`
  - `HasStageSelector=true`
  - `HasStagePadding10vh=true`
  - `HasHeroFlexGrow=false`
  - `HasHeroMinHeight468=true`
  - `HasTitleFont76=true`
  - `HasSheetMargin54=true`
- 微信开发者工具 preview
  - 命令：`D:\AP\微信web开发者工具\cli.bat preview --project D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin --port 9420 --qr-format terminal`
  - 通过。
  - 使用 AppID：`wx4dcc4e1066fd0fb9`
  - Preview 包大小：`TOTAL 1.1 MB`、`main 775.8 KB`、`/pkg-card/ 310.5 KB`、`/pkg-tools/ 36.8 KB`。

## 4. 结论

- 登录页顶部 hero 已完成视觉收紧：胶囊安全区由 `KpCapsuleSpacer` 接管，品牌锁定左下对齐，字距归零，暗色块不再撑满首屏。
- hero 与登录 sheet 已作为一组移动到屏幕居中偏上位置，390x844 视口中整体中心位于屏幕高度约 `41.7%`。
- 微信一键登录仍是当前唯一可见主操作，`getPhoneNumber` 绑定保持不变。
- 短信验证码入口未恢复，产物中未出现手机号验证码可见文本。
