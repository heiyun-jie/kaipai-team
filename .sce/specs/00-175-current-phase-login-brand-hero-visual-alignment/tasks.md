# 00-175 任务

## Phase 1: Spec

- [x] 新增登录页品牌 hero 视觉协调 Spec。
- [x] 明确本轮只处理视觉协调，不改变登录能力。

## Phase 2: Frontend

- [x] 登录页顶部改用 `KpCapsuleSpacer` 预留微信胶囊导航高度。
- [x] 优化 hero 卡片渐变、品牌锁定位置、字号和间距。
- [x] 将登录页可见文本字距归零，避免顶部品牌和登录按钮松散。
- [x] 保持短信验证码入口隐藏和微信一键登录绑定不变。

## Phase 2.1: Vertical Placement

- [x] 新增仅用于整体定位的 `stage` 容器包住 hero 与登录 sheet。
- [x] 将 hero + sheet 整组移动到屏幕居中偏上位置。
- [x] 保持小屏高度不足时可纵向滚动。

## Phase 3: Verification

- [x] 前端类型检查通过。
- [x] 微信小程序构建通过。
- [x] 小程序包体审计通过。
- [x] H5 构建通过。
- [x] H5 390x844 视口 DOM 核验通过。
- [x] 小程序产物文本 / 绑定核验通过。
- [x] 微信开发者工具 preview 通过。

## Acceptance

- [x] 登录页 hero 展示 `KAIPAILE / 开拍了`。
- [x] 顶部品牌区域不再与微信胶囊按钮挤在一起。
- [x] hero 与登录 sheet 整体位于屏幕居中偏上区域。
- [x] `开拍了` 不再显示成过度分散的三个字。
- [x] 不出现 `KAUPAILE`、`JU MING PIAN`、`剧 名 片`。
- [x] 微信一键登录仍是当前唯一可见主操作。
