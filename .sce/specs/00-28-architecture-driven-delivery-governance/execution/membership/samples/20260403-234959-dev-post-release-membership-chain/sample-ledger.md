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
  - `screenshots/admin-membership-accounts.png`
  - `screenshots/admin-content-templates.png`
  - `screenshots/admin-content-templates-rollback-dialog.png`
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
  - `captures/admin-screenshot-capture.json`
  - `captures/mini-program-screenshot-capture.json`
- DB Query Result:
  - `captures/admin-membership-template-chain-db.txt`

## Conclusion

- Current Status: `局部完成`
- Confirmed:
  - 发布后 membership 主链再次跑通 `member -> none -> member`
  - `after-close.reasonCodes=member_required`
  - 同一样本已并入后台会员账户页、模板页与回滚弹窗三张后台截图
  - 五页小程序页面证据已补齐，并保留 route / query / page-data / screenshot hash
  - 当前正式样本已收口为“后端 API + DB + 后台 UI + 小程序页面”同包证据
- Blockers:
  - `00-49 membership-preview-overlay-fact-source-boundary` 已明确当前 preview overlay 仍是 session-only 预览态，而不是后端事实源
  - 当前正式样本仍固定在 `dev + Nacos` 运行时，尚未扩展到更多环境基线
- Next Action:
  - 继续把 membership 留在 `00-49` 治理门禁下观察；没有跨登录 / 跨设备新证据前，不再新增 overlay 后端化实现项
  - `00-28` 下一实现优先级切到 AI 简历与其余切片，membership 以现有正式样本维持回归基线
