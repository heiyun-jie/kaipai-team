# 登录页协议勾选框视觉对齐 - 执行记录

## 结果

- 路由：`pages/login/index`
- 可见控件：底部《用户协议》《隐私政策》前的协议勾选框
- 未选中：单个浅蓝圆环；截图 SHA256 `676DECE56744539D797A949A8424CA9180081DFD136D858F5CA3F3058B23A0A6`
- 选中：蓝底白勾；截图 SHA256 `EA5E4FE762507A516868B35C813AABD0838CC3B3C251D7309C6ACBA710874496`
- 源码 SHA256：`419A624295224F932C5FAF1688B261CB76081FB8E86226DE83AEBC0F57EB28B7`

## 实现

- `.login-page__checkbox` 不再绘制 `width/height/border/border-radius/background`。
- `t-checkbox` 使用 `:icon="agreementCheckboxIcons"`，数组为本地官方 SVG `[checked, unchecked]`。
- `check-circle-filled-brand.svg` SHA256：`F0F53CA4EADD830C4C94C62FD485AE6BF8A0C05A8A0D69F771D94E5CD99EA416`
- `circle-agreement.svg` SHA256：`146ABEC2EFCAD37BC709E86F36EDA28B249905430B645C00B90F34C5BB3552C3`

## 自动验证

- `npm run type-check`：exit `0`。
- `npm run verify:login-agreement-checkbox`：`Passed 34 checks.`，exit `0`。
- `npm run verify:tdesign-migration`：`Passed 1331 checks.`，exit `0`。
- `npm run verify:v3-ui-legacy-colors`：全部命中与白名单一致，exit `0`。
- `npm run verify:nav-title`：通过 `101` 项，失败 `0` 项，exit `0`。
- `node .sce/specs/00-187-current-phase-miniapp-review-login-gate-fix/scripts/verify-miniapp-review-login-gate.mjs`：全部通过，exit `0`。
- `powershell -ExecutionPolicy Bypass -File .sce/tools/audit-steering.ps1`：`steering audit passed`，exit `0`。
- `npm run audit:mp-package`：包体部分通过，主包 `1.33 MB`、总产物 `1.95 MB`、所有包低于 `2 MB`；总命令 exit `1`，因为当前固定测试构建包含 `test-api.kplyyk.com`，而旧外链正则只允许正式 `api.kplyyk.com`，并同时命中 vendor 中的 `https://` 文本。本轮未放宽正式发布外链门禁。

## 产物与运行态

- build/dev scope：`data-v-2e6f43f9`。
- JS SHA256：`B3AB30D11205DF89FFDBD916E607231682B3AC2810D78CEF469E9CB99F32326F`。
- WXML SHA256：`10B28409E6F8B3622A070BF599FA7A2CBBFF6E7EC8B4F97F1C1BAC7A3F695D10`。
- WXSS SHA256：`5E7352DD659E219D4C07737A962911D0BDE6CC2D64B7806184E83D4105E8E5B7`。
- 微信内部接口确认未选中 `aria-checked=false` 使用 `circle-agreement.svg`；触发 `change {checked:true}` 后 `aria-checked=true` 并使用 `check-circle-filled-brand.svg`。
- 控制台 `grep -i error` 为空。核验未使用桌面截图、坐标、键鼠自动化、置顶、退出或重启微信开发者工具。

## 候选边界

本次只更新本地测试小程序产物，没有修改后端、数据库、远端测试服务或正式环境。旧候选 `20260826-1625-v3-draft` 的小程序字节已失效；正式人工签收前必须重新冻结候选。
