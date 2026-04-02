# Membership Validation Report

- Generated At: 2026-04-02T21:27:13
- Environment: dev

## Local Runtime Scan

- Frontend baseURL: http://101.43.57.62
- Frontend mock flag: false
- Admin baseURL: /api
- Server exposes /api context path: True

## Blockers

- [x] No blocker detected from local file scan
- [x] `user_id=10000` 的高等级业务样本已补齐，`/api/level/info.level=5`
- [x] `captures/card-config-first-save-failure.txt` 已记录 `2026-04-02 21:36` 的首保存失败证据
- [x] `2026-04-02 21:57` 已通过 plain `docker` 重建当前 dev 运行时，`captures/remote-redeploy-plain-docker.json` 已保留 `/app/app.jar` SHA256=`88d23af6cb2934097e2dc0e149537c0e96f18951e6bddc0ad82455a94fdea641`
- [x] `2026-04-02 21:59` 已补齐首保存成功证据：`POST /api/card/config` 返回 `200/200`，且 DB 已回读 `template_id=1`
- [x] `2026-04-02 22:15` 已补齐模板 rollback -> frontend summary -> restore publish 链路
- [x] `2026-04-02 22:16` 已补齐 admin 会员账户页、模板页与回滚弹窗截图
- [x] `2026-04-02 22:30` 已补齐 rollback 前后的小程序阶段截图，并确认 `actor-card` 会切到 `通用`，但 `detail / invite` 仍保持 fortune 主题路径

## Manual Evidence To Add

- [x] Membership accounts admin screenshot
- [x] Templates admin screenshot
- [x] level.info / card.personalization capture
- [x] membership / actor-card / detail / invite / fortune screenshots
- [x] DB query result for user / referral_record / actor_card_config / actor_share_preference
- [x] First save failure and post-redeploy success capture for `/api/card/config`
- [x] Template rollback / restore capture for `/api/card/scene-templates` and `/api/card/personalization`
- [x] Template rollback / restore mini-program stage capture for `before / after-rollback / after-restore`

## Output Files

- captures/capture-results.json
- captures/admin-screenshot-capture.json
- captures/admin-template-rollback-chain-results.json
- captures/admin-template-rollback-chain-db.txt
- captures/admin-template-rollback-mini-program-results.json
- captures/admin-template-rollback-mini-program-db.txt
- captures/membership-level-unlock-results.json
- captures/membership-level-unlock-db.txt
- captures/card-config-first-save-failure.txt
- captures/card-config-first-save-success-results.json
- captures/card-config-first-save-db.txt
- captures/remote-redeploy-plain-docker.json
- captures/mini-program-screenshot-capture.json
- captures/mini-program-screenshot-capture-before-rollback.json
- captures/mini-program-screenshot-capture-after-rollback.json
- captures/mini-program-screenshot-capture-after-restore.json
- screenshots/admin-membership-accounts.png
- screenshots/admin-content-templates.png
- screenshots/admin-content-templates-rollback-dialog.png
- membership-level-unlock-summary.md
- admin-template-rollback-chain-summary.md
- admin-template-rollback-mini-program-summary.md
- card-config-first-save-success-summary.md
- runtime-summary.md
- sample-ledger.md
- validation-report.md
