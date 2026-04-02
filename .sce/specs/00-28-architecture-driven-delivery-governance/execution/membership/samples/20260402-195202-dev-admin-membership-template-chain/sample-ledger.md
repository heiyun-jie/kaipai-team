# Membership Validation Sample Ledger

## Sample

- Environment: `dev`
- Sample Label: `20260402-195202-dev-admin-membership-template-chain`
- Validate At: `2026-04-02T21:09:14`

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

- Admin Screenshot: pending
- Membership Screenshot: `screenshots/membership-index.png`
- Actor Card Screenshot: `screenshots/actor-card-mini-program-card.png`
- Detail Screenshot: `screenshots/actor-profile-detail.png`
- Invite / Fortune Screenshot: `screenshots/invite-card.png`, `screenshots/fortune-general.png`
- API Capture: `captures/admin-membership-template-chain-results.json`
- DB Query Result: `captures/admin-membership-template-chain-db.txt`
- DevTools Blocker Capture: `captures/devtools-auth-blocker.txt`
- Mini Program Screenshot Capture: `captures/mini-program-screenshot-capture.json`

## Conclusion

- Current Status: `局部完成`
- Confirmed:
  - 后台 `close` 会员后，同一用户 `membershipTier` 从 `member -> none`
  - 后台 `open` 会员后，同一用户 `membershipTier` 从 `none -> member`
  - 模板主题发布后，`/api/card/personalization` 主色从 `#2F6B5F -> #7A3E2B`
  - `template_publish_log.publish_log_id=3 / publish_version=SMOKE_V2_ADMIN_20260402_195744`
  - `admin_operation_log.operation_log_id` 已可正常回读，DB 采证无 `log_id` 报错
  - `2026-04-02 21:09` 已通过 automator 建立真实前台会话并补齐 `membership / actor-card / detail / invite / fortune` 五页截图
  - `fortune-general.png` 已证明当前 fortune 主题不是运行时错误，而是业务 gating：页面明确显示 `Lv5 后可应用`
- Blockers:
  - 当前 smoke 用户有效邀请数仍只有 `1`，等级仍为 `Lv2`，`level_required` 仍阻塞 fortune theme 解锁
  - 后台页面截图若要与本样本放在同一证据包内，仍需后补
- Next Action:
  - 为 `user_id=10000` 或新增样本补更高等级条件，再复测 fortune theme gating
  - 如需把后台证据也收口到同一份样本，再补会员账户页与模板页截图
