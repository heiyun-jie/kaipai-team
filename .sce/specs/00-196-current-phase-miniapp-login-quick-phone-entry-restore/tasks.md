# 00-196 当前阶段小程序手机号快捷登录入口恢复 - 任务

- [x] T1 读取 `00-195` 定位结论、`00-187` 当前验收脚本、登录页源码和全局约定。
- [x] T2 新增本 Spec 的 `requirements.md`、`design.md`、`tasks.md`。
- [x] T3 修改 `00-187` 验收脚本，建立“缺少手机号快捷登录入口”红灯。
- [x] T4 运行红灯验收，确认当前代码失败且失败原因指向缺失快捷入口。
- [x] T5 恢复 `api/auth.ts` 手机号快捷登录 helper，缺 code 文案去微信品牌化。
- [x] T6 恢复 `utils/runtime.ts` 自有命名快捷登录开关和去品牌化不可用文案。
- [x] T7 恢复 `pages/login/index` 合规版「手机号快捷登录」按钮和交互逻辑，不恢复 logo。
- [x] T8 更新 `00-187` requirements / execution，记录 00-196 已修复入口。
- [x] T9 更新 `.sce/specs/README.md`、`.sce/specs/spec-code-mapping.md` 和当前上下文。
- [x] T10 执行 `type-check`、`build:mp-weixin`、`audit:mp-package`、`00-187` 和 `00-188` 验收脚本。
- [x] T11 核对 `dist/build` 与 `dist/dev` 登录页 WXML/WXSS，确认入口进入构建产物。
- [x] T12 回填 `execution.md`。
