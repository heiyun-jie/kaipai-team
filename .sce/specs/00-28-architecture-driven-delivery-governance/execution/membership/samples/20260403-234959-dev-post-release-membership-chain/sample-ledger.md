# Membership Validation Sample Ledger

## Sample

- Environment: `dev`
- Sample Label: `post-release-membership-chain`
- Validate At: `2026-04-03 23:50:12 +0800`

## Runtime

- Backend Entry: `http://101.43.57.62/api`
- Spring Profile: `dev`
- NACOS_ENABLED: `true`
- Mini Program VITE_API_BASE_URL: `http://101.43.57.62`
- Mini Program VITE_USE_MOCK: `false`
- Admin VITE_API_BASE_URL: `/api`

## Scenario

- ActorUserId: `10000`
- MembershipAccountId: `user_id=10000 current active membership_account`
- TemplateId: `1`
- PublishLogId: `26`
- SceneKey: `general`

## Evidence

- Admin Screenshot:
  - 本样本尚未补后台 UI 截图；如需并入同一样本，可补跑 `capture-admin-membership-template-screenshots.py`
- Membership Screenshot:
  - `screenshots/post-release-membership-index.png`
- Actor Card Screenshot:
  - `screenshots/post-release-actor-card-mini-program-card.png`
- Detail Screenshot:
  - `screenshots/post-release-actor-profile-detail.png`
- Invite / Fortune Screenshot:
  - `screenshots/post-release-invite-card.png`
  - `screenshots/post-release-fortune-general.png`
- API Capture:
  - `captures/capture-results.json`
  - `captures/admin-membership-template-chain-results.json`
  - `captures/mini-program-screenshot-capture.json`
- DB Query Result:
  - `captures/admin-membership-template-chain-db.txt`

## Conclusion

- Current Status: `局部完成`
- Confirmed:
  - 发布后 membership 主链再次跑通 `member -> none -> member`
  - `after-close.reasonCodes=member_required`
  - 五页小程序页面证据已补齐，并保留 route / query / page-data / screenshot hash
- Blockers:
  - 当前样本还没有并入后台 UI 截图
  - 当前样本仍未处理 overlay 事实源边界之外的新跨端恢复证据
- Next Action:
  - 如需把这份样本提升为更完整回归包，下一步补后台截图并把结论回写 `membership-status.md`
