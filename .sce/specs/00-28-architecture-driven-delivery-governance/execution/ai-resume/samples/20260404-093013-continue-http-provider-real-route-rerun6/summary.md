# AI Resume Notification Foundation Sample 20260404-093013-continue-http-provider-real-route-rerun6

- Generated At: `2026-04-04T09:30:13`
- Base URL: `http://101.43.57.62/api`
- Sample Label: `continue-http-provider-real-route-rerun6`
- Provider Code: `http`

## Checks

- `PASS` admin-login: adminUserId=2
- `PASS` actor-profile-ready: userId=10000
- `PASS` self-assignee-resolved: assignedAdminId=2
- `PASS` dispatch-send-success: status=sent, source=admin_dispatch, provider=http, deliveryId=12, providerMessageId=mock-http-20260404093016-0010
- `PASS` dispatch-pending-receipt-visible: receiptStatus=pending_receipt
- `PASS` provider-callback-delivered: receiptStatus=delivered, receiptSource=provider_callback, provider=http
- `PASS` provider-callback-receipt-failed: receiptStatus=receipt_failed, receiptSource=provider_callback, provider=http, reason=provider_delivery_rejected
- `PASS` manual-send-failed-backfill: status=send_failed, source=manual_admin_record, reason=sample manual send failed
- `PASS` manual-send-failed-persists-delivery-summary: deliveryId=14
- `PASS` pending-receipt-sample-visible: sendStatus=sent, receiptStatus=pending_receipt, receiptAt=None

## Artifacts

- `results.json`
