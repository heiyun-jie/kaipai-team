# AI Resume Collaboration Validation Sample 20260403-164135-continue-ai-collaboration-closure

- Generated At: `2026-04-03T16:41:35`
- Base URL: `http://101.43.57.62/api`
- Sample Label: `continue-ai-collaboration-closure`

## Key IDs

- Admin User ID: `2`
- Assignee Admin ID: `2`
- Assign/Acknowledge Failure ID: `airp_fail_a52d6d76ff134c539043773e7d5e5e57`
- Assign/Acknowledge Request ID: `airp_req_e83687dbcf1540c184925b7659261659`
- Assign/Remind Failure ID: `airp_fail_687385902b0f4ff89f4fee7d3a8eb1f1`
- Assign/Remind Request ID: `airp_req_b94816fdc92e4d26823dff47f0cd4dc1`

## Checks

- `PASS` admin-login: adminUserId=2, account=admin
- `PASS` admin-session-visible: sessionAdminUserId=2
- `PASS` actor-certified: userId=10000, isCertified=True
- `PASS` collaboration-catalog-ready: assigneeCount=2, escalationRoleCount=1
- `PASS` self-assignee-resolved: assigneeAdminId=2, account=admin
- `PASS` assign-ack-failure-created: failureId=airp_fail_a52d6d76ff134c539043773e7d5e5e57, requestId=airp_req_e83687dbcf1540c184925b7659261659
- `PASS` assign-action-updates-collaboration-fields: assignedAdminId=2, collaborationStatus=pending_ack, claimDeadlineAt=2026-04-03T12:41:35
- `PASS` assign-action-handling-note-visible: assignNoteFound=True
- `PASS` pending-ack-filter-visible: marker=20260403-164135-continue-ai-collaboration-closure-assign-ack
- `PASS` acknowledge-action-updates-collaboration-fields: ackBy=2, collaborationStatus=acknowledged
- `PASS` acknowledge-action-handling-note-visible: acknowledgeNoteFound=True
- `PASS` acknowledged-filter-visible: marker=20260403-164135-continue-ai-collaboration-closure-assign-ack
- `PASS` assign-remind-failure-created: failureId=airp_fail_687385902b0f4ff89f4fee7d3a8eb1f1, requestId=airp_req_b94816fdc92e4d26823dff47f0cd4dc1
- `PASS` assign-remind-chain-pending-ack: collaborationStatus=pending_ack
- `PASS` remind-action-updates-reminder-fields: reminderCount=1, lastRemindedByAdminId=2, collaborationStatus=pending_ack
- `PASS` remind-action-handling-note-visible: remindNoteFound=True
- `PASS` remind-pending-ack-filter-visible: marker=20260403-164135-continue-ai-collaboration-closure-assign-remind
- `PASS` assign-operation-log-visible: requestId=20260403-164135-continue-ai-collaboration-closure-assign-ack, list=1
- `PASS` acknowledge-operation-log-visible: requestId=20260403-164135-continue-ai-collaboration-closure-acknowledge, list=1
- `PASS` remind-operation-log-visible: requestId=20260403-164135-continue-ai-collaboration-closure-remind, list=1

## Artifacts

- `results.json`
