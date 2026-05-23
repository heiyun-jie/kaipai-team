# 00-175 当前阶段登录页品牌 Hero 视觉协调 - 技术设计

## 1. 设计结论

登录页顶部采用“胶囊导航高度预留 + 左对齐品牌锁定 + 柔和暗色封面”的方案：

```text
KpCapsuleSpacer
stage
  hero
    hero-card
      KAIPAILE
      开拍了
      剧组版 / 分享平台
  sheet
    WeChat one-click login
    agreement
```

不新增胶片块、占位卡片或非业务视觉节点。视觉改善只通过现有 hero / sheet 的样式调整完成。

_Requirements: 3.1, 3.2, 3.3, 3.4_

## 2. 顶部安全区

登录页用 `KpCapsuleSpacer` 替代手写 status bar spacer。该组件基于 `getFloatingBackNavStyles()` 读取微信胶囊按钮底部位置，保证 hero 从胶囊导航区域之后开始。

这样可以避免微信开发者工具和真机中右上角胶囊按钮压到 hero 卡片边缘。

_Requirements: 3.1_

## 3. 整体垂直位置

hero 与 sheet 需要作为一个整体移动，而不是分别增加零散 margin。页面在 `KpCapsuleSpacer` 之后增加 `login-page__stage` 布局容器：

- `stage` 占据胶囊安全区之后的剩余首屏空间。
- `stage` 使用顶部视口比例 padding，将整组内容下移到屏幕居中偏上位置。
- `stage` 不承载视觉装饰，仅用于整体定位。
- root 保持 `min-height` 与纵向布局，屏幕高度不足时允许纵向滚动。

_Requirements: 3.4_

## 4. Hero 样式

- hero 卡片继续作为品牌封面，不承载任何登录操作。
- 品牌锁定改为左下视觉重心，和下方登录卡片的左对齐正文形成连贯关系。
- hero 不再用 `flex: 1` 撑满首屏，避免顶部变成大面积暗色空块。
- `KAIPAILE`、`开拍了`、副标题的 `letter-spacing` 全部归零，避免品牌文字松散。
- `开拍了` 字号降低，保持标题气质但避免压迫。
- 背景渐变从硬暗色块改为暖灰过渡，让 hero 与下方浅色登录 sheet 更自然衔接。

_Requirements: 3.2_

## 5. 登录能力边界

本轮不触碰：

- `loginByWechat`
- `handleWechatLogin`
- `open-type="getPhoneNumber"`
- 短信登录隐藏门禁
- 登录成功后的用户态写入和跳转

_Requirements: 3.3_

## 6. 验证设计

必须执行：

1. `npm run type-check`
2. `npm run build:mp-weixin`
3. `npm run audit:mp-package`
4. `npm run build:h5`

产物核验：

- `dist/build/mp-weixin/pages/login/index.wxml`
- `dist/dev/mp-weixin/pages/login/index.wxml`

核验点：

- 不包含 `手机号`
- 不包含 `验证码`
- 不包含 `获取验证码`
- 不包含 `登录 / 注册`
- 不包含 `KAUPAILE`
- 不包含 `JU MING PIAN`
- 不包含 `剧 名 片`
- 保留 `bindgetphonenumber`
- 保留 `open-type`

H5 390x844 视口核验：

- `kicker=KAIPAILE`
- `title=开拍了`
- `scrollWidth=innerWidth`
- hero title 未横向溢出
- stage 顶部留白使整体位于居中偏上区域
- sheet bottom 位于首屏内

微信开发者工具：

- `preview` 通过。
