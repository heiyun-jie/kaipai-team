# 00-195 当前阶段小程序手机号快捷登录入口回归定位 - 任务

- [x] T1 读取 `.sce/README.md`、`.sce/steering/CURRENT_CONTEXT.md`、`.sce/specs/README.md` 和 `SHARED_CONVENTIONS.md`。
- [x] T2 核对当前 `kaipai-frontend/src/pages/login/index.vue`，确认页面只有短信验证码登录，不存在「手机号快捷登录」入口。
- [x] T3 查询 `kaipai-frontend` git 历史，定位「手机号快捷登录」入口存在、文案调整和删除入口的提交。
- [x] T4 查看 `84c2778`、`0679e09`、`54d8a31` diff，确认当前问题不是样式隐藏，而是完整快捷登录链路被删除。
- [x] T5 核对 `00-187` requirements / design / tasks / execution / verify script，记录文档内部冲突。
- [x] T6 新增本 Spec 的 `requirements.md`、`design.md`、`tasks.md` 和 `execution.md`。
- [x] T7 更新 `.sce/specs/README.md` 和 `.sce/specs/spec-code-mapping.md`。
- [ ] T8 后续另起修复任务：恢复合规版「手机号快捷登录」入口，并修正 00-187 验收脚本。
