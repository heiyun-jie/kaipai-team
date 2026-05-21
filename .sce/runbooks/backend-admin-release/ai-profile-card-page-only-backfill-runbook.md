# AI Profile Card Page-Only Backfill Runbook

> Scope: `00-171-current-phase-ai-profile-card-single-cover-theme-flow` Phase 5
> Status: execution pending target-environment inventory

## 1. Goal

Inventory legacy AI profile-card tasks where `actor_ai_profile_card_task.generated_image_url` is empty while a historical successful `cover` row exists in `actor_ai_profile_card_page`.

Do not execute a data update until a target environment has been inventoried and the candidate rows have been reviewed.

## 2. Read-Only Inventory

Before running against a target environment, establish the approved release/admin session for that environment. Do not paste protected row data into chat.

Run from repo root:

```powershell
python .sce/runbooks/backend-admin-release/scripts/read-ai-profile-card-page-only-inventory.py --operator <operator> --mysql-database <target_database> --mysql-container <target_mysql_container>
```

The script defaults are development-environment conveniences. A development database result cannot close the Phase 5 target-environment inventory item and cannot approve frontend fallback removal.

For a dry evidence scaffold only, without connecting to the target environment:

```powershell
python .sce/runbooks/backend-admin-release/scripts/read-ai-profile-card-page-only-inventory.py --template-only
```

Template-only records intentionally omit `remote-helper-command.txt`, `raw-mysql-output.txt`, `result-count.txt`, and `sample.tsv`; they cannot be used as execution evidence.

The execution writes a diagnostics directory:

```text
.sce/runbooks/backend-admin-release/records/diagnostics/<timestamp>-ai-profile-card-page-only-inventory/
```

Required evidence files:

- `query-count.sql`
- `query-sample.sql`
- `query-inventory.sql`
- `remote-helper-command.txt`
- `raw-mysql-output.txt`
- `result-count.txt`
- `sample.tsv`
- `summary.json`
- `README.md`

Required reviewed fields:

- environment / host
- execution time
- operator
- `page_only_cover_count`
- sample rows reviewed: `yes / no`
- evidence path
- approval session
- reviewed by
- review conclusion
- fallback removal approved: `yes / no`

The script uses the standard helper with a fixed generated SELECT-only SQL payload. Do not replace it with a hand-written SQL file for this evidence chain.

## 3. Decision Gate

If `page_only_cover_count = 0`:

- Record the evidence.
- Do not create a migration.
- Keep the frontend fallback until release owners explicitly approve its removal.

If `page_only_cover_count > 0`:

- Review sample rows.
- Confirm each cover URL is usable and is not the source image URL.
- Choose one path:
  - SQL forward migration, only if cover URLs are stable managed URLs.
  - Operational re-host script, if cover URLs may be provider temporary URLs.

## 4. Frontend Fallback Removal Gate

Do not remove the frontend legacy `pages` cover fallback until one of these is recorded:

1. Target-environment inventory count is `0`.
2. A reviewed backfill or re-host operation has run, post-run count is `0`, and API samples return task-level `generatedImageUrl`.

The fallback is still temporary compat code, but static repository review is not enough to delete it.

## 5. Completion Criteria

The Phase 5 page-only data item can only be marked complete after one of these is true:

1. Target-environment inventory count is `0`, with recorded evidence.
2. A forward migration or operational script has run, post-run count is `0`, and sample API responses return task-level `generatedImageUrl`.

Do not mark this item complete based only on static repository review.

## 6. Related Spec

- `.sce/specs/00-171-current-phase-ai-profile-card-single-cover-theme-flow/legacy-page-only-backfill.md`
- `.sce/specs/00-171-current-phase-ai-profile-card-single-cover-theme-flow/tasks.md`
