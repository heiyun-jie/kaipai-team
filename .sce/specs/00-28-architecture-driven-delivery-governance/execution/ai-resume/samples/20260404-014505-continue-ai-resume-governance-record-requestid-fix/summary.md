# AI Resume Collaboration Validation Sample 20260404-014505-continue-ai-resume-governance-record-requestid-fix

- Generated At: `2026-04-04T01:45:05`
- Base URL: `http://101.43.57.62/api`
- Sample Label: `continue-ai-resume-governance-record-requestid-fix`

## Key IDs

- Admin User ID: `2`
- Assignee Admin ID: `2`
- Assign/Acknowledge Failure ID: `airp_fail_e22328175497462e8b4c90406c18a263`
- Assign/Acknowledge Request ID: `airp_req_e3536dee61a94dce8cf807ab0846b473`
- Assign/Remind Failure ID: `airp_fail_0021c3124c9b45e185225d55994cbb67`
- Assign/Remind Request ID: `airp_req_8c661ed2b7f947719766911646da89c1`
- Auto Remind Sweep Failure ID: `airp_fail_09551938cfea468696e4ed59bb0e617d`
- Timeout Escalation Failure ID: `airp_fail_22300b9e96b64ad8ba410745e48a69c4`

## Checks

- `PASS` admin-login: adminUserId=2, account=admin
- `PASS` admin-session-visible: sessionAdminUserId=2
- `PASS` actor-certified: userId=10000, isCertified=True
- `PASS` collaboration-catalog-ready: assigneeCount=2, escalationRoleCount=1
- `PASS` self-assignee-resolved: assigneeAdminId=2, account=admin
- `PASS` assign-ack-failure-created: failureId=airp_fail_e22328175497462e8b4c90406c18a263, requestId=airp_req_e3536dee61a94dce8cf807ab0846b473
- `PASS` assign-action-updates-collaboration-fields: assignedAdminId=2, collaborationStatus=pending_ack, claimDeadlineAt=2026-04-03T21:45:06
- `PASS` assign-action-derives-notification-and-sla-fields: notificationStatus=pending_send, receiptStatus=not_sent, autoRemindStage=idle, slaStatus=not_started
- `PASS` assign-action-handling-note-visible: assignNoteFound=True
- `PASS` pending-ack-filter-visible: marker=20260404-014505-continue-ai-resume-governance-record-requestid-fix-assign-ack
- `PASS` notification-and-sla-filter-visible-before-ack: marker=20260404-014505-continue-ai-resume-governance-record-requestid-fix-assign-ack
- `PASS` record-notification-action-updates-fields: notificationStatus=sent, notificationSentAt=2026-04-03T17:45:06, receiptStatus=pending_receipt, autoRemindStage=watching
- `PASS` record-notification-filter-visible: marker=20260404-014505-continue-ai-resume-governance-record-requestid-fix-assign-ack
- `PASS` record-receipt-action-updates-fields: receiptStatus=delivered, receiptAt=2026-04-03T17:45:06, notificationStatus=sent
- `PASS` delivered-filter-visible-before-ack: marker=20260404-014505-continue-ai-resume-governance-record-requestid-fix-assign-ack
- `PASS` acknowledge-action-updates-collaboration-fields: ackBy=2, collaborationStatus=acknowledged
- `PASS` acknowledge-action-derives-receipt-and-complete-states: receiptStatus=received, receiptAt=2026-04-03T17:45:07, autoRemindStage=completed, slaStatus=within_sla
- `PASS` acknowledge-action-handling-note-visible: acknowledgeNoteFound=True
- `PASS` acknowledged-filter-visible: marker=20260404-014505-continue-ai-resume-governance-record-requestid-fix-assign-ack
- `PASS` receipt-filter-visible-after-ack: marker=20260404-014505-continue-ai-resume-governance-record-requestid-fix-assign-ack
- `PASS` assign-remind-failure-created: failureId=airp_fail_0021c3124c9b45e185225d55994cbb67, requestId=airp_req_8c661ed2b7f947719766911646da89c1
- `PASS` assign-remind-chain-pending-ack: collaborationStatus=pending_ack
- `PASS` remind-action-updates-reminder-fields: reminderCount=1, lastRemindedByAdminId=2, collaborationStatus=pending_ack
- `PASS` remind-action-derives-resent-notification-state: notificationStatus=resent, receiptStatus=pending_receipt, autoRemindStage=manual_intervened, slaStatus=active
- `PASS` remind-action-handling-note-visible: remindNoteFound=True
- `PASS` remind-pending-ack-filter-visible: marker=20260404-014505-continue-ai-resume-governance-record-requestid-fix-assign-remind
- `PASS` resent-filter-visible-after-remind: marker=20260404-014505-continue-ai-resume-governance-record-requestid-fix-assign-remind
- `PASS` skip-auto-remind-action-updates-stage: autoRemindStage=skipped, autoRemindSkippedAt=2026-04-03T17:45:07
- `PASS` skip-auto-remind-filter-visible: marker=20260404-014505-continue-ai-resume-governance-record-requestid-fix-assign-remind
- `PASS` manual-takeover-failure-created: failureId=airp_fail_ebefee04f4f941cb88d0b0cb6d2dec21, requestId=airp_req_74fe1ba3df9846b783af74bc33d87a2c
- `PASS` manual-takeover-action-updates-stage: autoRemindStage=manual_takeover, manualTakeoverAt=2026-04-03T17:45:08, ackBy=2
- `PASS` manual-takeover-filter-visible: marker=20260404-014505-continue-ai-resume-governance-record-requestid-fix-manual-takeover
- `PASS` auto-remind-sweep-failure-created: failureId=airp_fail_09551938cfea468696e4ed59bb0e617d, requestId=airp_req_2a054e872e9049deb800f956514030bc
- `PASS` governance-sweep-preview-detects-auto-remind: dueCount=1, actionType=auto_remind, actionStatus=ready
- `PASS` governance-sweep-executes-auto-remind: executedCount=1, actionStatus=executed, reminderCount=1, notificationStatus=resent
- `PASS` timeout-escalation-failure-created: failureId=airp_fail_22300b9e96b64ad8ba410745e48a69c4, requestId=airp_req_7786b680d60949b8851d2dc412938508
- `PASS` governance-sweep-preview-detects-timeout-escalation: timeoutEscalationCount=1, actionType=timeout_escalation, actionStatus=ready
- `PASS` governance-sweep-executes-timeout-escalation: executedCount=1, actionStatus=executed, handlingStatus=escalated, escalationRoleCode=ADMIN
- `FAIL` assign-operation-log-visible: requestId=20260404-014505-continue-ai-resume-governance-record-requestid-fix-assign-ack, list=0
- `FAIL` record-notification-operation-log-visible: requestId=20260404-014505-continue-ai-resume-governance-record-requestid-fix-record-notification, list=0
- `FAIL` record-receipt-operation-log-visible: requestId=20260404-014505-continue-ai-resume-governance-record-requestid-fix-record-receipt, list=0
- `FAIL` acknowledge-operation-log-visible: requestId=20260404-014505-continue-ai-resume-governance-record-requestid-fix-acknowledge, list=0
- `FAIL` remind-operation-log-visible: requestId=20260404-014505-continue-ai-resume-governance-record-requestid-fix-remind, list=0
- `FAIL` skip-auto-remind-operation-log-visible: requestId=20260404-014505-continue-ai-resume-governance-record-requestid-fix-skip-auto-remind, list=0
- `FAIL` manual-takeover-operation-log-visible: requestId=20260404-014505-continue-ai-resume-governance-record-requestid-fix-manual-takeover, list=0
- `FAIL` auto-remind-operation-log-visible: requestId=20260404-014505-continue-ai-resume-governance-record-requestid-fix-auto-remind-execute, list=0
- `FAIL` timeout-escalation-operation-log-visible: requestId=20260404-014505-continue-ai-resume-governance-record-requestid-fix-timeout-escalation-execute, list=0

## Artifacts

- `results.json`
