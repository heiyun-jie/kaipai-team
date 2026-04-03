# AI Resume Collaboration Validation Sample 20260404-013746-continue-ai-resume-governance-sweep

- Generated At: `2026-04-04T01:37:46`
- Base URL: `http://101.43.57.62/api`
- Sample Label: `continue-ai-resume-governance-sweep`

## Key IDs

- Admin User ID: `2`
- Assignee Admin ID: `2`
- Assign/Acknowledge Failure ID: `airp_fail_f69d04d96c0c4f5c8873df490af16bb9`
- Assign/Acknowledge Request ID: `airp_req_7ce92abdec954bb695007fc5d8edf7c2`
- Assign/Remind Failure ID: `None`
- Assign/Remind Request ID: `None`
- Auto Remind Sweep Failure ID: `None`
- Timeout Escalation Failure ID: `None`

## Checks

- `PASS` admin-login: adminUserId=2, account=admin
- `PASS` admin-session-visible: sessionAdminUserId=2
- `PASS` actor-certified: userId=10000, isCertified=True
- `PASS` collaboration-catalog-ready: assigneeCount=2, escalationRoleCount=1
- `PASS` self-assignee-resolved: assigneeAdminId=2, account=admin
- `PASS` assign-ack-failure-created: failureId=airp_fail_f69d04d96c0c4f5c8873df490af16bb9, requestId=airp_req_7ce92abdec954bb695007fc5d8edf7c2
- `PASS` assign-action-updates-collaboration-fields: assignedAdminId=2, collaborationStatus=pending_ack, claimDeadlineAt=2026-04-03T21:37:48
- `PASS` assign-action-derives-notification-and-sla-fields: notificationStatus=pending_send, receiptStatus=not_sent, autoRemindStage=idle, slaStatus=not_started
- `PASS` assign-action-handling-note-visible: assignNoteFound=True
- `PASS` pending-ack-filter-visible: marker=20260404-013746-continue-ai-resume-governance-sweep-assign-ack
- `PASS` notification-and-sla-filter-visible-before-ack: marker=20260404-013746-continue-ai-resume-governance-sweep-assign-ack

## Artifacts

- `results.json`
