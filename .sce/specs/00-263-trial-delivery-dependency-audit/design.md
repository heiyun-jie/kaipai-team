# 技术设计

_Requirements: 1-5_

- 先保存00-262阻断审计，核对真实lock、包入口与候选JS。管理端更新axios/vue到已修复的兼容版本，并刷新必要传递依赖；typecheck/build/npm audit三重验证。
- 小程序新增告警对应SSR renderer、browser mapping、braces、source-map-js均追溯依赖入口与编译输出；优先最小升级，不能为消告警破坏uni-app内部Vue版本。确为构建专用才在00-231已有分类中登记审查，增加对应代码特征扫描。
- build-release-candidate-artifacts.py保留未知包fail-closed、critical零、i18n版本下限、禁止map/package/node_modules/工具marker；补真实当前时间对riskExpiry的检查，续期必须附本次审查证据。不得仅以包名消失/构建成功判定不可达。
- tests/test_build_release_candidate_artifacts.py先补过期拒绝、未知拒绝、SSR/工具代码marker拒绝，再实现。记录接受期限2026-11-05，仅受控本地源码构建，无外露dev server、无不可信素材输入；到期重新审查。
- tasks顺序：依赖诊断→最小修复→本地验证→评审→新候选双根重建→固定dev物化/运行证明→准入→CLI上传测试包→公众平台设体验版。所有操作保留日志与SHA。
- 微信唯一工程固定dist/dev/mp-weixin；写入前正常quit并等退出，备份原运行树。上传前逐文件核验冻结test产物，严禁上传release产物。
