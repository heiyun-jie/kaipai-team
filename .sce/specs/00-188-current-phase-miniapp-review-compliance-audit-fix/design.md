# 00-188 当前阶段小程序复审合规专项整改 - 技术设计

## 1. 设计结论

本轮按“源码 + 构建产物 + 静态门禁”三层收口：

```text
pages.json / app.json
  -> 默认启动页改为 pages/home/index

pkg-tools/video-player
  -> 移除 autoplay
  -> 自动播放标签改为手动播放语义

pkg-tools/webview
  -> 删除外部 url web-view 模式
  -> 只保留本地协议 / 隐私 / 设置说明页

分享 / 风格 / 等级文案
  -> 微信 / WECHAT / 朋友圈包装文案改成中性分享表达
  -> 再邀请 X 人解锁 / 升级改成中性能力状态

static assets / manifest
  -> 删除 wechat-login.png
  -> urlCheck=true

verify-miniapp-review-compliance-audit.mjs
  -> 同时扫描 src、dist/build、dist/dev
```

_Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7_

## 2. 路由配置

- `kaipai-frontend/src/pages.json` 中 `pages/home/index` 调整为第一项。
- `pages/login/index` 保留在主包页面列表中，仍由 `goLogin()`、邀请码入口和账号功能门禁显式打开。
- 不新增页面。
- `pkg-tools/webview/index` 保留路由，但只承载本地说明内容，不再作为任意外链容器。

_Requirements: 3.2, 3.5_

## 3. 依赖清单

继续复用：

- `@/stores/user`
- `@/utils/navigation`
- `@/utils/share-card-mvp`
- `@/utils/level`
- `@/utils/share-artifact`
- `@/config/brand`

删除：

- `kaipai-frontend/src/static/icons/wechat-login.png`

不新增 npm 依赖。

_Requirements: 3.3, 3.7_

## 4. 页面状态定义

### `pkg-tools/video-player/index`

保留：

- `url`
- `type`
- `isGuideVideo`
- `playUrl`
- `hasVideo`

调整：

- 视频组件只保留 `controls`、`show-center-play-btn`、`show-fullscreen-btn`、`enable-play-gesture`。
- 右侧状态从 `LIVE PLAY` 调整为 `MANUAL PLAY`。
- 标签从「自动播放」调整为「点击播放」。

_Requirements: 3.1_

### `pkg-tools/webview/index`

移除：

- `externalUrl`
- `safeDecode(options.url)` 对 `web-view` 的承接。
- 模板中的 `<web-view v-if="externalUrl" ...>`。

保留：

- `type`
- `title`
- `preferences`
- 本地用户协议 / 隐私政策 / 关于 / 通知 / 偏好设置内容。

`onLoad` 只读取 `type` 和 `title`。传入 `url` 参数时不进入外链模式。

_Requirements: 3.5_

## 5. 文案调整策略

### 官方品牌混淆降风险

替换规则：

| 当前文案 | 新文案 |
| --- | --- |
| `WECHAT CHAT PREVIEW` | `SESSION CARD PREVIEW` |
| `WECHAT MINIPROGRAM` | `MINI PROGRAM CARD` |
| `微信对话展开` | `会话卡片展开` |
| `直接调起微信分享面板` | `打开系统分享面板` |
| `分享到朋友圈` | `发送海报` |
| `保存后转发朋友圈` | `保存后发送海报` |

内部接口名如 `/api/auth/wechat-login`、环境变量 `VITE_ENABLE_WECHAT_AUTH` 不属于用户可见文案，不纳入本轮改名。

_Requirements: 3.3_

### 邀请解锁诱导降风险

替换规则：

| 当前文案 | 新文案 |
| --- | --- |
| `再邀请 X 人解锁` | `成长条件未满足` |
| `再邀请 X 人后可继续` | `完成成长条件后可继续` |
| `再邀请 X 人升到下一等级` | `成长条件未满足` |
| `邀请人数将用于等级升级` | `成长记录将用于等级更新` |

后端字段 `inviteCount`、邀请记录页 API 和现有等级计算保持不变；本轮只减少复审包前台诱导表达。

_Requirements: 3.4_

## 6. 构建配置

- `kaipai-frontend/src/manifest.json`：`mp-weixin.setting.urlCheck` 改为 `true`。
- `npm run build:mp-weixin` 生成后，`project.config.json` 应同步为 `urlCheck=true`。

_Requirements: 3.6_

## 7. 验证设计

新增脚本：

```text
.sce/specs/00-188-current-phase-miniapp-review-compliance-audit-fix/scripts/verify-miniapp-review-compliance-audit.mjs
```

脚本检查：

1. `src/pages.json` 与 `dist/*/app.json` 首项为 `pages/home/index`。
2. `src/manifest.json` 与 `dist/*/project.config.json` 的 `urlCheck=true`。
3. 源码与构建产物不存在视频 `autoplay`。
4. 源码与构建产物不存在 `wechat-login.png` 文件或引用。
5. 指定可见层文件不包含 `WECHAT`、`微信对话`、`微信分享面板`、`朋友圈`。
6. 指定可见层文件不包含 `再邀请.*解锁`、`再邀请.*升到`、`邀请.*解锁`。
7. `pkg-tools/webview` 源码与构建产物不再包含 `web-view` 和 `options.url` 外链模式。

必须执行：

1. `node .sce/specs/00-188-current-phase-miniapp-review-compliance-audit-fix/scripts/verify-miniapp-review-compliance-audit.mjs`（整改前红灯）
2. `cd kaipai-frontend && npm run type-check`
3. `cd kaipai-frontend && npm run build:mp-weixin`
4. `cd kaipai-frontend && npm run audit:mp-package`
5. `node .sce/specs/00-187-current-phase-miniapp-review-login-gate-fix/scripts/verify-miniapp-review-login-gate.mjs`
6. `node .sce/specs/00-188-current-phase-miniapp-review-compliance-audit-fix/scripts/verify-miniapp-review-compliance-audit.mjs`

_Requirements: 3.7_
