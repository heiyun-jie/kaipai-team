# Membership Validation Sample Ledger

## Sample

- Environment: `dev`
- Sample Label: `20260402-212713-dev-fortune-theme-lv5-unlock`
- Validate At: `2026-04-02T21:36:26`
- Revalidate At: `2026-04-02T21:59:18`

## Runtime

- Backend Entry: `http://101.43.57.62/api`
- Spring Profile: `dev`
- NACOS_ENABLED: `true`
- Mini Program VITE_API_BASE_URL: `http://101.43.57.62`
- Mini Program VITE_USE_MOCK: `false`
- Admin VITE_API_BASE_URL: `/api`

## Scenario

- ActorUserId: `10000`
- MembershipAccountId: `1`
- TemplateId: `1`
- PublishLogId: `3`
- SceneKey: `general`

## Evidence

- Admin Screenshot: `screenshots/admin-membership-accounts.png`, `screenshots/admin-content-templates.png`, `screenshots/admin-content-templates-rollback-dialog.png`
- Membership Screenshot: `screenshots/membership-index.png`
- Actor Card Screenshot: `screenshots/actor-card-mini-program-card.png`
- Detail Screenshot: `screenshots/actor-profile-detail.png`
- Invite / Fortune Screenshot: `screenshots/invite-card.png`, `screenshots/fortune-general.png`
- Admin Screenshot Capture: `captures/admin-screenshot-capture.json`
- Admin Rollback Chain: `captures/admin-template-rollback-chain-results.json`, `captures/admin-template-rollback-chain-db.txt`, `admin-template-rollback-chain-summary.md`
- Admin Rollback Mini Program Chain: `captures/admin-template-rollback-mini-program-results.json`, `captures/admin-template-rollback-mini-program-db.txt`, `admin-template-rollback-mini-program-summary.md`
- API Capture: `captures/membership-level-unlock-results.json`
- DB Query Result: `captures/membership-level-unlock-db.txt`
- First Save Failure: `captures/card-config-first-save-failure.txt`
- First Save Success: `captures/card-config-first-save-success-results.json`, `captures/card-config-first-save-db.txt`
- Remote Redeploy: `captures/remote-redeploy-plain-docker.json`
- Mini Program Screenshot Capture: `captures/mini-program-screenshot-capture.json`
- Rollback Stage Capture: `captures/mini-program-screenshot-capture-before-rollback.json`, `captures/mini-program-screenshot-capture-after-rollback.json`, `captures/mini-program-screenshot-capture-after-restore.json`

## Conclusion

- Current Status: `局部完成`
- Confirmed:
  - `user_id=10000` 当前有效邀请数已提升到 `8`，`/api/level/info.level=5`，`shareCapability.reasonCodes=[]`
  - `/api/card/personalization?actorId=10000&scene=general&loadFortune=true` 当前返回 `themeId=general-member-fortune / primary=#FF6B35 / enableFortuneTheme=true`
  - `membership / actor-card / detail / invite / fortune` 五页截图已补齐，截图路由与 `themeId=general-member-fortune` 对齐
  - 新补的高等级样本已证明 fortune theme 的 unlock 是可走通的真实运行时链路，而不是页面 mock
  - `2026-04-02 21:57` 已通过 plain `docker` 重建当前 dev 运行时，容器 `/app/app.jar` SHA256 已对齐 `88d23af6cb2934097e2dc0e149537c0e96f18951e6bddc0ad82455a94fdea641`
  - `2026-04-02 21:59` 已再次删除 `actor_card_config / actor_share_preference` 后复测首保存，`POST /api/card/config` 返回 `200/200`，DB 已回读 `template_id=1 / enable_fortune_theme=1`
  - `2026-04-02 22:15` 已按同一份样本跑通模板 rollback -> frontend summary -> restore publish：回滚后 `/api/card/scene-templates` 回到 builtin `通用 / #ff7a45`，恢复发布后又切回 `Smoke Template / #7A3E2B`
  - `2026-04-02 22:16` 已补齐后台会员账户页、模板页和回滚弹窗三张 admin 截图，并生成 `captures/admin-screenshot-capture.json`
  - `2026-04-02 22:30` 已继续补齐 rollback 前后的小程序页面证据：`actor-card` 会从 `Smoke Template` 切到 `通用` 再恢复，但 `detail / invite` 三段截图保持一致，说明当前 `Lv5 + enableFortuneTheme=1` 样本里 fortune 主题层会覆盖公开页与邀请页的模板回滚视觉变化
- Blockers:
  - preview overlay 仍是前端显式编辑态，尚未升级为后端 / session 事实源
- Next Action:
  - 复核 preview overlay 是否还需要升级为后端临时摘要或 session 级状态
  - 如需继续验证公开详情页 / 邀请页的视觉回滚，应改用未启用 fortune theme 的样本，避免 `general-member-fortune` 持续覆盖模板层变化
