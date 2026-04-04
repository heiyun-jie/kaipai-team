# AI Resume Notification Foundation Sample 20260404-073450-continue-ai-notification-random-token

- Generated At: `2026-04-04T07:34:50`
- Base URL: `http://101.43.57.62/api`
- Sample Label: `continue-ai-notification-random-token`

## Checks

- `PASS` admin-login: adminUserId=2
- `PASS` actor-profile-ready: userId=10000
- `PASS` self-assignee-resolved: assignedAdminId=2
- `FAIL` dispatch-send-success: status=send_failed, source=admin_dispatch, deliveryId=1, providerMessageId=None
- `FAIL` dispatch-pending-receipt-visible: receiptStatus=not_sent
- `PASS` provider-callback-delivered: receiptStatus=delivered, receiptSource=provider_callback
- `PASS` provider-callback-receipt-failed: receiptStatus=receipt_failed, receiptSource=provider_callback, reason=provider_delivery_rejected
- `PASS` manual-send-failed-backfill: status=send_failed, source=manual_admin_record, reason=sample manual send failed
- `PASS` manual-send-failed-persists-delivery-summary: deliveryId=3
- `FAIL` pending-receipt-sample-visible: sendStatus=send_failed, receiptStatus=not_sent, receiptAt=None

## Artifacts

- `results.json`
