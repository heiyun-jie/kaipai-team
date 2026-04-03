# AI Resume Collaboration Validation Sample 20260404-015141-continue-ai-resume-governance-requestid-expand

- Generated At: `2026-04-04T01:51:41`
- Base URL: `http://101.43.57.62/api`
- Sample Label: `continue-ai-resume-governance-requestid-expand`

## Key IDs

- Admin User ID: `2`
- Assignee Admin ID: `2`
- Assign/Acknowledge Failure ID: `airp_fail_7ea1458c354a48c09e265148e6aabd03`
- Assign/Acknowledge Request ID: `airp_req_f3f96ddec81f4d4fafafa2014fea999c`
- Assign/Remind Failure ID: `airp_fail_5be811b6907d4522bbd1eede5cf95e93`
- Assign/Remind Request ID: `airp_req_bcd8a4fda5b54e14a2a9c84c9f8a33d0`
- Auto Remind Sweep Failure ID: `airp_fail_4fc0e5c4e74a4bc1ad5df00c375efab1`
- Timeout Escalation Failure ID: `airp_fail_e3786a2b8ef7448a91bb2dc3ed6e2e6b`

## Checks

- `PASS` admin-login: adminUserId=2, account=admin
- `PASS` admin-session-visible: sessionAdminUserId=2
- `PASS` actor-certified: userId=10000, isCertified=True
- `PASS` collaboration-catalog-ready: assigneeCount=2, escalationRoleCount=1
- `PASS` self-assignee-resolved: assigneeAdminId=2, account=admin
- `PASS` assign-ack-failure-created: failureId=airp_fail_7ea1458c354a48c09e265148e6aabd03, requestId=airp_req_f3f96ddec81f4d4fafafa2014fea999c
- `PASS` assign-action-updates-collaboration-fields: assignedAdminId=2, collaborationStatus=pending_ack, claimDeadlineAt=2026-04-03T21:51:43
- `PASS` assign-action-derives-notification-and-sla-fields: notificationStatus=pending_send, receiptStatus=not_sent, autoRemindStage=idle, slaStatus=not_started
- `PASS` assign-action-handling-note-visible: assignNoteFound=True
- `PASS` pending-ack-filter-visible: marker=20260404-015141-continue-ai-resume-governance-requestid-expand-assign-ack
- `PASS` notification-and-sla-filter-visible-before-ack: marker=20260404-015141-continue-ai-resume-governance-requestid-expand-assign-ack
- `PASS` record-notification-action-updates-fields: notificationStatus=sent, notificationSentAt=2026-04-03T17:51:43, receiptStatus=pending_receipt, autoRemindStage=watching
- `PASS` record-notification-filter-visible: marker=20260404-015141-continue-ai-resume-governance-requestid-expand-assign-ack
- `PASS` record-receipt-action-updates-fields: receiptStatus=delivered, receiptAt=2026-04-03T17:51:44, notificationStatus=sent
- `PASS` delivered-filter-visible-before-ack: marker=20260404-015141-continue-ai-resume-governance-requestid-expand-assign-ack
- `PASS` acknowledge-action-updates-collaboration-fields: ackBy=2, collaborationStatus=acknowledged
- `PASS` acknowledge-action-derives-receipt-and-complete-states: receiptStatus=received, receiptAt=2026-04-03T17:51:44, autoRemindStage=completed, slaStatus=within_sla
- `PASS` acknowledge-action-handling-note-visible: acknowledgeNoteFound=True
- `PASS` acknowledged-filter-visible: marker=20260404-015141-continue-ai-resume-governance-requestid-expand-assign-ack
- `PASS` receipt-filter-visible-after-ack: marker=20260404-015141-continue-ai-resume-governance-requestid-expand-assign-ack
- `PASS` assign-remind-failure-created: failureId=airp_fail_5be811b6907d4522bbd1eede5cf95e93, requestId=airp_req_bcd8a4fda5b54e14a2a9c84c9f8a33d0
- `PASS` assign-remind-chain-pending-ack: collaborationStatus=pending_ack
- `PASS` remind-action-updates-reminder-fields: reminderCount=1, lastRemindedByAdminId=2, collaborationStatus=pending_ack
- `PASS` remind-action-derives-resent-notification-state: notificationStatus=resent, receiptStatus=pending_receipt, autoRemindStage=manual_intervened, slaStatus=active
- `PASS` remind-action-handling-note-visible: remindNoteFound=True
- `PASS` remind-pending-ack-filter-visible: marker=20260404-015141-continue-ai-resume-governance-requestid-expand-assign-remind
- `PASS` resent-filter-visible-after-remind: marker=20260404-015141-continue-ai-resume-governance-requestid-expand-assign-remind
- `PASS` skip-auto-remind-action-updates-stage: autoRemindStage=skipped, autoRemindSkippedAt=2026-04-03T17:51:45
- `PASS` skip-auto-remind-filter-visible: marker=20260404-015141-continue-ai-resume-governance-requestid-expand-assign-remind
- `PASS` manual-takeover-failure-created: failureId=airp_fail_89e4aa9ad9bf41b5900377cf4ab9a353, requestId=airp_req_f4ab27a1f5064ecbac23a4190e44ff8b
- `PASS` manual-takeover-action-updates-stage: autoRemindStage=manual_takeover, manualTakeoverAt=2026-04-03T17:51:46, ackBy=2
- `PASS` manual-takeover-filter-visible: marker=20260404-015141-continue-ai-resume-governance-requestid-expand-manual-takeover
- `PASS` auto-remind-sweep-failure-created: failureId=airp_fail_4fc0e5c4e74a4bc1ad5df00c375efab1, requestId=airp_req_ad24ccfb7b664bab80dd1c48bffc8454
- `PASS` governance-sweep-preview-detects-auto-remind: dueCount=1, actionType=auto_remind, actionStatus=ready
- `PASS` governance-sweep-executes-auto-remind: executedCount=1, actionStatus=executed, reminderCount=1, notificationStatus=resent
- `PASS` timeout-escalation-failure-created: failureId=airp_fail_e3786a2b8ef7448a91bb2dc3ed6e2e6b, requestId=airp_req_8ebe61f927d54a168f8860bfea9b914e
- `PASS` governance-sweep-preview-detects-timeout-escalation: timeoutEscalationCount=1, actionType=timeout_escalation, actionStatus=ready
- `PASS` governance-sweep-executes-timeout-escalation: executedCount=1, actionStatus=executed, handlingStatus=escalated, escalationRoleCode=ADMIN
- `PASS` assign-operation-log-visible: requestId=20260404-015141-continue-ai-resume-governance-requestid-expand-assign-ack, list=1
- `PASS` record-notification-operation-log-visible: requestId=20260404-015141-continue-ai-resume-governance-requestid-expand-record-notification, list=1
- `PASS` record-receipt-operation-log-visible: requestId=20260404-015141-continue-ai-resume-governance-requestid-expand-record-receipt, list=1
- `PASS` acknowledge-operation-log-visible: requestId=20260404-015141-continue-ai-resume-governance-requestid-expand-acknowledge, list=1
- `PASS` remind-operation-log-visible: requestId=20260404-015141-continue-ai-resume-governance-requestid-expand-remind, list=1
- `PASS` skip-auto-remind-operation-log-visible: requestId=20260404-015141-continue-ai-resume-governance-requestid-expand-skip-auto-remind, list=1
- `PASS` manual-takeover-operation-log-visible: requestId=20260404-015141-continue-ai-resume-governance-requestid-expand-manual-takeover, list=1
- `PASS` auto-remind-operation-log-visible: requestId=20260404-015141-continue-ai-resume-governance-requestid-expand-auto-remind-execute, list=1
- `PASS` timeout-escalation-operation-log-visible: requestId=20260404-015141-continue-ai-resume-governance-requestid-expand-timeout-escalation-execute, list=1

## Artifacts

- `results.json`
