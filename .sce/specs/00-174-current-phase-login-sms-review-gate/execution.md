# 00-174 Execution

## 1. 启动记录

- 用户要求：`pages/login/index` 手机验证码需要先隐藏，只使用微信一键登录，等验证码审核过了才能使用。
- 已读取：
  - `.sce/README.md`
  - `.sce/steering/CURRENT_CONTEXT.md`
  - `.sce/specs/README.md`
  - `.sce/specs/SHARED_CONVENTIONS.md`
  - `.sce/specs/00-173-current-phase-wechat-phone-login-enablement/requirements.md`
  - `.sce/specs/00-173-current-phase-wechat-phone-login-enablement/design.md`
  - `kaipai-frontend/src/pages/login/index.vue`

## 2. 实施记录

- 修改 `kaipai-frontend/src/pages/login/index.vue`：
  - 从模板中移除手机号输入框。
  - 从模板中移除验证码输入框与获取验证码动作。
  - 从模板中移除短信登录 / 注册提交按钮。
  - 保留微信一键登录按钮，并提升为当前登录页唯一主 CTA。
  - 登录页说明文案改为 `使用微信一键登录，授权后进入分享平台`，避免审核前页面继续引导验证码登录。
  - 保留 `loginByPhone / registerByPhone / sendSmsCode` 相关脚本逻辑，后续验证码审核通过后可按独立 Spec 恢复模板入口。
- 根据用户反馈“下面是空的”继续优化 `kaipai-frontend/src/pages/login/index.vue`：
  - `.login-page` 改为纵向 flex 页面容器。
  - `.login-page__sheet` 改为承接剩余 viewport 的登录面板。
  - 协议下方新增非交互 `login-page__film` 胶片视觉块，填补隐藏短信表单后的下半屏空白。
  - 将 hero / sheet 宽度显式锁为 `calc(100vw - 68rpx)`，避免移动视口边缘裁切。
  - 将微信一键登录按钮固定为 `width: 100%` + `box-sizing: border-box`，避免不同端 `button` 默认样式导致横向溢出。

## 3. 验证记录

- `cd D:\XM\kaipai-team\kaipai-frontend && npm run type-check`：通过。
- `cd D:\XM\kaipai-team\kaipai-frontend && npm run build:mp-weixin`：通过。
- `cd D:\XM\kaipai-team\kaipai-frontend && npm run audit:mp-package`：通过。
  - main：`519.17 KB / 2.00 MB`
  - pkg-card：`201.87 KB / 2.00 MB`
  - pkg-tools：`28.31 KB / 2.00 MB`
- `cd D:\XM\kaipai-team\kaipai-frontend && npm run build:h5`：通过，用于移动视口视觉截图核验。
- 产物核验：
  - `dist/build/mp-weixin/pages/login/index.wxml`
  - `dist/dev/mp-weixin/pages/login/index.wxml`
- WXML 文本核验结果：
  - `手机号=False`
  - `验证码=False`
  - `获取验证码=False`
  - `登录 / 注册=False`
  - `login-page__film=True`
  - `bindgetphonenumber=True`
  - `open-type=True`
- 390x844 移动视口截图核验：
  - 基于 `dist/build/h5` 启动本地静态服务。
  - 使用 Chrome headless 生成 `D:\XM\kaipai-team\kaipai-frontend\.tmp-login-h5-390x844.png`。
  - 截图确认登录卡片下方已由胶片视觉块承接，不再是用户截图中的大面积空白。
- 微信开发者工具 CLI 验证：
  - `D:\AP\微信web开发者工具\cli.bat cache --clean all --project D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin`：通过。
  - `D:\AP\微信web开发者工具\cli.bat open --project D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin --port 9420`：通过。
  - `D:\AP\微信web开发者工具\cli.bat preview --project D:\XM\kaipai-team\kaipai-frontend\dist\dev\mp-weixin --port 9420 --qr-format terminal`：通过，开发者工具可基于当前产物生成预览码。
  - 最新 preview 输出使用 AppID：`wx4dcc4e1066fd0fb9`。

## 4. 结论

- 当前 `pages/login/index` 已收口为只展示微信一键登录。
- 手机验证码登录入口已从当前构建产物的登录页 WXML 中退出。
- 微信 `getPhoneNumber` 绑定仍保留，继续复用 `00-173` 的微信登录链路。
- 登录页隐藏短信表单后的底部空白已收口，当前由非交互胶片视觉块承接。
- 后续验证码能力审核通过后，应另起 Spec 恢复短信登录模板入口，并重新执行小程序构建与审核态验证。
