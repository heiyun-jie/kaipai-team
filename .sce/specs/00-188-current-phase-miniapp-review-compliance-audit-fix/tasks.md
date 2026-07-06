# 00-188 当前阶段小程序复审合规专项整改 - 任务拆解

> 执行原则：一次一个任务，先红灯脚本，再最小整改，最后构建与产物核验。

## T1 建立 Spec 与红灯脚本

- [x] 新增 `00-188` requirements / design / tasks。
- [x] 新增 `verify-miniapp-review-compliance-audit.mjs` 静态验收脚本。
- [x] 在当前未整改代码上运行脚本，确认红灯失败。

## T2 多媒体、入口和外链模式整改

- [x] 移除 `pkg-tools/video-player/index.vue` 的 `autoplay`。
- [x] 将视频页“自动播放”相关文案改为手动播放语义。
- [x] 将 `pages/home/index` 调整为 `pages.json` 第一项。
- [x] 移除 `pkg-tools/webview/index.vue` 任意 `url` 外链 `web-view` 模式。
- [x] 将 `src/manifest.json` 的 `mp-weixin.setting.urlCheck` 改为 `true`。

## T3 品牌混淆和诱导邀请文案整改

- [x] 删除未使用的 `src/static/icons/wechat-login.png`。
- [x] 替换分享卡 / 海报 / 创建页中的 `WECHAT`、`微信`、`朋友圈` 包装文案。
- [x] 替换风格、AI 分享图和等级进度中的「再邀请 X 人解锁 / 升级」文案。
- [x] 保留后端邀请 / 等级事实模型，不改 API 合同。

## T4 构建、产物核对与脚本验收

- [x] `kaipai-frontend npm run type-check` 通过。
- [x] `kaipai-frontend npm run build:mp-weixin` 通过并同步 `dist/dev/mp-weixin`。
- [x] `kaipai-frontend npm run audit:mp-package` 通过。
- [x] `00-187` 登录门禁脚本继续通过。
- [x] `00-188` 复审合规脚本通过。
- [x] 核对 `dist/build/mp-weixin` 与 `dist/dev/mp-weixin` 中首页入口、`autoplay`、`wechat-login.png`、`web-view`、高风险文案和 `urlCheck`。

## T5 执行记录回填

- [x] 新增 `execution.md` 记录红灯、修改、构建与验收结果。
- [x] 更新 `.sce/specs/README.md`。
- [x] 更新 `.sce/specs/spec-code-mapping.md`。
