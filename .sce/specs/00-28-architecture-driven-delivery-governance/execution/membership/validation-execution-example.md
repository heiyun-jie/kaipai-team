# 会员与模板联调执行示例

## 1. 只创建样本目录

```powershell
powershell -ExecutionPolicy Bypass -File `
  "D:\XM\kaipai-team\.sce\specs\00-28-architecture-driven-delivery-governance\execution\membership\new-membership-validation-sample.ps1" `
  -EnvironmentName "dev" `
  -SampleLabel "template-publish"
```

输出目录下会预建：

- `captures/`
- `screenshots/`
- `sample-ledger.md`

## 2. 一次性准备 membership 联调样本

```powershell
powershell -ExecutionPolicy Bypass -File `
  "D:\XM\kaipai-team\.sce\specs\00-28-architecture-driven-delivery-governance\execution\membership\run-membership-validation.ps1" `
  -EnvironmentName "dev" `
  -SampleLabel "member-open-template-publish"
```

脚本会自动：

- 创建样本目录
- 扫描 `kaipai-frontend/.env`、`.env.example`
- 扫描 `kaipai-admin/.env.development`
- 扫描 `kaipaile-server/src/main/resources/application.yml`
- 生成：
  - `captures/capture-results.json`
  - `runtime-summary.md`
  - `sample-ledger.md`
  - `validation-report.md`

## 3. 人工补证顺序

1. 打开 `runtime-summary.md`，确认当前环境是否具备真实联调前置
2. 补后台截图：
   - 会员账户页
   - 模板发布 / 回滚页
3. 补接口响应：
   - `level.info`
   - `card.personalization`
   - `card.scene-templates`
4. 补小程序截图：
   - membership
   - actor-card
   - detail
   - invite
   - fortune
5. 补数据库证据：
   - `membership_account`
   - `card_scene_template`
   - `template_publish_log`
6. 最后把结论回填到 `status/membership-status.md`

## 3.1 等级 gating 样本

当 `fortune` 或分享主题只剩 `level_required` 阻塞时，可继续在同一份 spec 下补高等级验证样本：

```powershell
python `
  "D:\XM\kaipai-team\.sce\specs\00-28-architecture-driven-delivery-governance\execution\membership\run-membership-level-unlock.py" `
  "D:\XM\kaipai-team\.sce\specs\00-28-architecture-driven-delivery-governance\execution\membership\samples\<sample-root>"
```

脚本会自动：

- 回读当前 `user / invite_code / referral_record`
- 只补足到 `Lv5` 还缺的有效邀请样本，不重复多写
- 复测 `user.me / invite.stats / level.info / card.config / card.personalization`
- 保存 `enableFortuneTheme=true`
- 生成：
  - `captures/membership-level-unlock-results.json`
  - `captures/membership-level-unlock-db.txt`
  - `membership-level-unlock-summary.md`

## 3.2 首保存回归样本

当同一份样本曾记录过 `/card/config` 首次保存失败，可继续在同一份 spec 下补运行时修复验证：

```powershell
python `
  "D:\XM\kaipai-team\.sce\specs\00-28-architecture-driven-delivery-governance\execution\membership\verify-card-config-first-save.py" `
  "D:\XM\kaipai-team\.sce\specs\00-28-architecture-driven-delivery-governance\execution\membership\samples\<sample-root>"
```

脚本会自动：

- 删除目标用户当前场景下的 `actor_card_config / actor_share_preference`
- 重新走 `sendCode / login / GET card.config / GET card.personalization / POST card.config`
- 回读 `actor_card_config.template_id` 与 `actor_share_preference.enable_fortune_theme`
- 生成：
  - `captures/card-config-first-save-success-results.json`
  - `captures/card-config-first-save-db.txt`
  - `card-config-first-save-success-summary.md`

## 3.3 模板回滚到前台样本

当模板发布已经跑通，需要确认“后台回滚 -> 前台恢复 -> 再发布恢复”时，可继续在同一份 spec 下补 rollback 样本：

```powershell
python `
  "D:\XM\kaipai-team\.sce\specs\00-28-architecture-driven-delivery-governance\execution\membership\run-admin-template-rollback-chain.py" `
  "D:\XM\kaipai-team\.sce\specs\00-28-architecture-driven-delivery-governance\execution\membership\samples\<sample-root>"
```

脚本会自动：

- 读取当前模板最新 `publishVersion`
- 执行 `POST /admin/content/templates/{id}/rollback`
- 回读 `/card/scene-templates` 与 `/card/personalization`
- 再发布恢复运行时状态
- 生成：
  - `captures/admin-template-rollback-chain-results.json`
  - `captures/admin-template-rollback-chain-db.txt`
  - `admin-template-rollback-chain-summary.md`

## 3.4 回滚前台阶段截图补证

当 rollback 的 API / DB 证据还需要继续映射到真实小程序页面时，可继续在同一份 spec 下补阶段截图样本：

```powershell
python `
  "D:\XM\kaipai-team\.sce\specs\00-28-architecture-driven-delivery-governance\execution\membership\run-admin-template-rollback-mini-program-chain.py" `
  "D:\XM\kaipai-team\.sce\specs\00-28-architecture-driven-delivery-governance\execution\membership\samples\<sample-root>"
```

脚本会自动：

- 读取当前模板最新 `publishVersion`
- 先抓 `before-rollback` 小程序五页截图
- 执行 `POST /admin/content/templates/{id}/rollback`
- 回读 `/card/scene-templates` 与 `/card/personalization`
- 再抓 `after-rollback` 小程序五页截图
- 恢复 publish 后再抓 `after-restore` 小程序五页截图
- 生成：
  - `captures/admin-template-rollback-mini-program-results.json`
  - `captures/admin-template-rollback-mini-program-db.txt`
  - `captures/mini-program-screenshot-capture-before-rollback.json`
  - `captures/mini-program-screenshot-capture-after-rollback.json`
  - `captures/mini-program-screenshot-capture-after-restore.json`
  - `admin-template-rollback-mini-program-summary.md`

## 3.5 后台截图补证

当样本已具备真实后台账号与远端 `/api`，可继续补后台 UI 截图：

```powershell
python `
  "D:\XM\kaipai-team\.sce\specs\00-28-architecture-driven-delivery-governance\execution\membership\capture-admin-membership-template-screenshots.py" `
  "D:\XM\kaipai-team\.sce\specs\00-28-architecture-driven-delivery-governance\execution\membership\samples\<sample-root>"
```

脚本会自动：

- 启动本地 `kaipai-admin` dev server
- 建立 `127.0.0.1:8010 -> http://101.43.57.62` 的本地代理
- 注入真实 admin 登录态并打开后台页面
- 生成：
  - `screenshots/admin-membership-accounts.png`
  - `screenshots/admin-content-templates.png`
  - `screenshots/admin-content-templates-rollback-dialog.png`
  - `captures/admin-screenshot-capture.json`

## 4. 当前脚本边界

- 当前脚本只预填“仓内可直接抽取的运行时事实”
- `run-membership-level-unlock.py` 会直接请求真实后端，并在远端 `kaipai_dev` 补验证样本
- `verify-card-config-first-save.py` 会直接改写远端 `kaipai_dev.actor_card_config / actor_share_preference` 当前样本用户数据，用于回归验证首次保存链路
- `run-admin-template-rollback-chain.py` 会直接对远端模板执行一次 rollback 和一次 restore publish，因此只应用在已有样本模板上
- `run-admin-template-rollback-mini-program-chain.py` 也会直接对远端模板执行一次 rollback 和一次 restore publish，并额外依赖本地 `ws://127.0.0.1:9421` 的 DevTools automator 连接
- 如需排除 `general-member-fortune` 遮罩，可继续执行 `run-admin-template-rollback-mini-program-no-fortune-theme.py`；该脚本会在同一轮样本里强制关闭 fortune theme、跑 rollback / restore，并在结束后恢复原偏好
- `capture-admin-membership-template-screenshots.py` 会临时拉起本地 `kaipai-admin` dev server 与 `127.0.0.1:8010` 代理；脚本退出后会自动清理本地进程
- 仍不会代替人工执行后台发布 / 回滚动作
- 常规小程序截图仍可用 `capture-mini-program-screenshots.js` 跑到同一样本目录；若要补 rollback 前后分阶段页面证据，应优先使用 `run-admin-template-rollback-mini-program-chain.py`

## 3.4.1 排除 Fortune Theme 遮罩的 rollback 样本

当 `Lv5 + enableFortuneTheme=1` 样本已经证明 `detail / invite` 会被 fortune 主题覆盖时，可继续补一份 no-fortune 标准样本：

```powershell
python `
  "D:\XM\kaipai-team\.sce\specs\00-28-architecture-driven-delivery-governance\execution\membership\run-admin-template-rollback-mini-program-no-fortune-theme.py"
```

脚本会自动：

- 创建一份新的 `*-dev-template-rollback-no-fortune-theme` 样本目录
- 强制关闭当前用户的 `enableFortuneTheme`
- 调用 `run-admin-template-rollback-mini-program-chain.py` 补齐 `before / after-rollback / after-restore` 三段截图
- 在结束后恢复原 fortune 偏好
- 生成：
  - `captures/no-fortune-theme-chain.stdout.log`
  - `captures/no-fortune-theme-chain.stderr.log`
  - `captures/admin-template-rollback-mini-program-results.json`
  - `admin-template-rollback-mini-program-summary.md`
  - `summary.md`

当前参考样本：`execution/membership/samples/20260403-112652-dev-template-rollback-no-fortune-theme/summary.md`
首轮样本 `20260403-112652-dev-template-rollback-no-fortune-theme` 先证明：

- 三段 `detail / invite` query 已固定为 `themeId=general-member-base`
- `actor-card` SHA：`AB50A24F... -> 19C8615D... -> AB50A24F...`
- `detail / invite` 当时仍保持同哈希

随后已在前端补齐 `detail / invite` 的模板 / artifact 首屏文案消费，并重新构建小程序；最新参考样本：`execution/membership/samples/20260403-121415-dev-template-rollback-no-fortune-theme/summary.md`

- `actor-card` SHA：`AB50A24F... -> 19C8615D... -> AB50A24F...`
- `detail` SHA：`97E4C31E... -> CCC4BB27... -> 97E4C31E...`
- `invite` SHA：`213439AE... -> 4D126C62... -> 213439AE...`
- `detail` 页首屏文案：`Smoke Template公开名片页 -> 通用公开名片页`
- `invite` 页首屏文案：`Smoke Template风格邀请卡 -> 通用风格邀请卡`

因此该样本当前的标准解释已经从“排除 fortune theme 遮罩后仍只在 actor-card 可观测”推进到“排除 fortune theme 遮罩后，actor-card / detail / invite 三页都能体现模板 rollback”

## 3.6 Preview Overlay 静态审计

当 membership 当前主风险已经收口到 preview overlay 边界，需要确认 query/session/helper 没有重新扩散到新页面时，可继续补一份静态审计样本：

```powershell
python `
  "D:\XM\kaipai-team\.sce\specs\00-28-architecture-driven-delivery-governance\execution\membership\run-preview-overlay-static-audit.py"
```

脚本会自动：

- 扫描 `kaipai-frontend/src`
- 校验 `previewLayout / previewPrimary / previewAccent / previewBackground` 只存在于 `src/utils/personalization.ts`
- 校验 `kp:personalization-preview-overlay-session` 只存在于 `src/utils/personalization.ts`
- 校验 `PersonalizationPreviewOverlay` 及相关 helper 是否仍停留在允许的 `actor-card / detail / invite / utils / types` 白名单里
- 生成：
  - `captures/preview-overlay-static-audit.json`
  - `summary.md`

## 5. 适用场景

- 开始真实环境联调前，先做准入检查
- 拿到新一套环境配置后，快速建立新的 membership 验证样本目录
- 把“运行时阻塞”和“模板 / 会员恢复缺陷”拆开记录，避免再次误把配置问题当成功能问题
