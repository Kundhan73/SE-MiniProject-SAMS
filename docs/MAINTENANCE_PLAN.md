# SAMS Product Maintenance Plan

**Document Version:** 1.1 (developer review corrections, 30 October 2026)  
**Effective Date:** 29 October 2026  
**Accountable QA Owner:** Anish (`planetai05`), QA Engineer  
**Related Backlog Issue:** [#32](https://github.com/Kundhan73/SE-MiniProject-SAMS/issues/32) (SAM-45)  
**Requirements Traced:** SAMS-NF-002 (Uptime & Availability), SAMS-NF-004 (Academic-Year Data Retention), SAMS-SR-005 (Append-Only Audit Trail)

---

## 1. Overview and Operational Scope

The Student Attendance Management System (SAMS) provides automated attendance marking, self-service student views, correction request workflows, notifications, and immutable audit logging. This Maintenance Plan defines procedures for backups, disaster recovery, software updates, operational monitoring, and team responsibilities to maintain system integrity and availability throughout the academic semester.

### Operational Targets
- **Target Availability:** >= 99% during working hours (8:00 AM – 6:00 PM, Monday through Saturday), excluding announced maintenance windows (SRS SAMS-NF-002).
- **Data Retention:** Retain all attendance, enrollment, and audit records for at least the full academic year without automatic purging (SRS SAMS-NF-004).
- **Audit Immutability:** Audit records are strictly append-only; database triggers and application code reject UPDATE and DELETE actions on audit logs (SRS SAMS-SR-005).

---

## 2. Backup Strategy

### 2.1 Backup Methodology and Tooling
- **Primary Database Engine:** PostgreSQL 16 (in Docker or hosted staging/production).
- **Tool:** PostgreSQL custom-format logical archive via `pg_dump -Fc` (built-in archive compression). The commands below are procedures to rehearse; no automated backup job is installed by this document.
- **Backup Command:**
  ```bash
  # Run from the deployment checkout. Set an existing protected host directory.
  set -eu
  backup_dir="${SAMS_BACKUP_DIR:?Set SAMS_BACKUP_DIR outside the repository}"
  backup_name="sams_backup_$(date -u +%Y%m%d_%H%M%S).dump"
  umask 077
  docker compose exec -T db sh -c 'pg_dump -U "$POSTGRES_USER" --format=c "$POSTGRES_DB"' > "$backup_dir/$backup_name.partial"
  test -s "$backup_dir/$backup_name.partial"
  mv "$backup_dir/$backup_name.partial" "$backup_dir/$backup_name"
  (cd "$backup_dir" && shasum -a 256 "$backup_name" > "$backup_name.sha256")
  ```
- **Scope:** Complete database schema, user accounts, timetables, course sections, attendance records, correction history, and append-only audit tables (`audit_auditlog`).

### 2.2 Schedule and Automation
- **Required frequency:** Daily at 02:00 AM IST via an operator-configured scheduler. Installation, timezone, successful execution logs, failed-backup alerts and encryption/offsite transfer must be verified on the selected host. This repository does not yet provide that scheduled service.
- **Pre-Migration Backups:** A mandatory ad-hoc backup must be created immediately prior to executing any Django database migration (`python manage.py migrate`).

### 2.3 Storage and Encryption
- **Location:** Backups are stored in an isolated, access-controlled directory outside the application directory. Under no circumstances are backup files committed to Git.
- **Encryption requirement:** Configure encrypted storage and authenticated offsite transfer before institutional use. The command above creates an unencrypted logical archive; it does not implement encryption or offsite copying.
- **Retention Schedule:**
  - Daily backups: Retained for 14 days.
  - Weekly snapshots (Sunday 02:00 IST): Retained for 8 weeks.
  - Monthly snapshots (1st of month): Retained for 12 months (1 full academic year) per SAMS-NF-004.

### 2.4 Integrity Verification
- **Required restore rehearsal:** Schedule an isolated restore test every Sunday at 04:00 AM IST after the operator implements it. No automated restore job is installed or verified by this PR. Record the archive checksum, matching source-release SHA and source snapshot counts, then verify:
  1. Successful database restoration without errors.
  2. Table row counts match counts captured at the backup snapshot (a later live database may legitimately differ).
  3. Append-only triggers are active on `audit_auditlog`.
  4. Migration status is cleanly reported by `python manage.py showmigrations`.

---

## 3. Disaster Recovery and Business Continuity

### 3.1 Objectives
- **Recovery Time Objective (RTO):** <= 2 hours for core attendance marking and viewing services.
- **Recovery Point Objective (RPO):** <= 24 hours (maximum data loss bounded by daily backup interval; intra-day classes can be re-entered from physical class rosters if catastrophic hardware failure occurs).

### 3.2 Step-by-Step Restoration Procedure
1. **Isolate and Stop Application:**
   ```bash
   docker compose stop nginx web worker beat
   ```
2. **Verify Backup File Integrity:**
   ```bash
   backup_dir="${SAMS_BACKUP_DIR:?Set the protected host backup directory}"
   backup_name="sams_backup_<timestamp>.dump"  # Select a known-good archive.
   (cd "$backup_dir" && shasum -a 256 -c "$backup_name.sha256")
   ```
3. **Restore Database:**
   ```bash
   # Destructive: rehearse on an isolated database first.
   # The archive stays on the host; credentials expand inside the db container.
   docker compose up -d db redis
   docker compose exec -T db sh -c 'pg_restore --exit-on-error --clean --if-exists --no-owner -U "$POSTGRES_USER" -d "$POSTGRES_DB"' < "$backup_dir/$backup_name"
   ```
4. **Validate the matching release schema:**
   ```bash
   docker compose run --rm --no-deps web python manage.py migrate --check
   ```
5. **Restart Services & Smoke Test:**
   ```bash
   docker compose up -d web worker beat nginx
   curl --fail http://localhost:8000/api/health/
   ```

A failed restore or schema check must stop recovery. Use the image/source release matching the backup; do not automatically run forward migrations before deciding schema compatibility. Record a full restore rehearsal before relying on the stated RTO/RPO.

### 3.3 Rehearsals
- Disaster recovery procedures must be rehearsed once per semester in a staging environment to validate runbooks and verify team readiness.

---

## 4. Updates, Patch Management, and Rollbacks

### 4.1 Dependency and Vulnerability Auditing
- **Automated Audits:** `pip-audit` runs on every GitHub Actions PR and push to `main`.
- **Review Cadence:** Weekly review of newly disclosed CVEs affecting Django, psycopg, ReportLab, Celery, or Redis.
- **Patch Policy:**
  - Critical/High CVEs: Patched within 48 hours.
  - Routine dependency updates: Bundled into scheduled sprint releases.

### 4.2 Maintenance Windows
- All routine updates and schema migrations must occur during announced maintenance windows: **Sundays 00:00 – 06:00 IST** or non-instructional holidays.
- Advance notice (minimum 24 hours) must be posted to faculty and administrative users.
- Announced maintenance windows are explicitly excluded when calculating semester uptime for SAMS-NF-002.

### 4.3 Container-Based Deployment and Rollback
- Application images are built deterministically and tagged with Git commit SHAs: `ghcr.io/kundhan73/se-miniproject-sams:sha-<commit>`.
- **Application rollback with downtime:** The base Compose file builds locally and does not read `IMAGE_TAG`. Select a reviewed published image with an explicit override for every application service, including the migration job:
  ```bash
  export SAMS_IMAGE="ghcr.io/kundhan73/se-miniproject-sams:sha-<previous-commit>"
  cat > /tmp/sams-image-override.yml <<'YAML'
  services:
    migrate:
      image: ${SAMS_IMAGE:?Set SAMS_IMAGE to a reviewed SHA tag}
    web:
      image: ${SAMS_IMAGE:?Set SAMS_IMAGE to a reviewed SHA tag}
    worker:
      image: ${SAMS_IMAGE:?Set SAMS_IMAGE to a reviewed SHA tag}
    beat:
      image: ${SAMS_IMAGE:?Set SAMS_IMAGE to a reviewed SHA tag}
  YAML
  docker compose -f docker-compose.yml -f /tmp/sams-image-override.yml config --images
  docker compose -f docker-compose.yml -f /tmp/sams-image-override.yml pull migrate web worker beat
  docker compose stop nginx web worker beat
  docker compose -f docker-compose.yml -f /tmp/sams-image-override.yml run --rm --no-deps web python manage.py migrate --check
  docker compose -f docker-compose.yml -f /tmp/sams-image-override.yml up -d --no-build --force-recreate migrate web worker beat nginx
  curl --fail http://localhost:8000/api/health/
  ```
- The checks must succeed before continuing. Rehearse the override on staging and record the actual container image IDs, health and all three role flows. Include the TLS overlay in every Compose command when that deployment uses it.
- If migrations are incompatible with the previous release, stop and follow the approved database recovery procedure with a pre-migration backup. Application image rollback alone cannot undo schema/data changes. This runbook does not establish zero downtime or a successful rollback rehearsal.

---

## 5. Monitoring, Alerting, and Availability Tracking

### 5.1 Service Health Checks
- **Endpoint:** `GET /api/health/` (unauthenticated).
- **Probes:**
  - Database connectivity: Executes `SELECT 1` on PostgreSQL.
  - Cache/Broker connectivity: Issues `.ping()` to Redis when Celery is not in eager mode.
- **Responses:**
  - HTTP `200 OK`: `{"status": "ok"}`
  - HTTP `503 Service Unavailable`: `{"status": "unavailable"}` for a caught Redis failure. A database exception is handled by the global API error handler; treat every non-200 response and timeout as an outage rather than assuming the same response body.

### 5.2 Working-Hours Uptime Monitoring (Issue #36 / SAMS-NF-002)
- **Schedule:** 8:00 AM – 6:00 PM IST, Monday through Saturday.
- **Probe Interval:** 60-second synthetic HTTP GET to `/api/health/`.
- **Target SLA:** 99.0% uptime over the semester.
- **Required tracking:** Provision an external monitor and retain working-hours latency/status logs, with monthly summaries. No semester-long availability result or externally configured monitor is established by this plan.

### 5.3 Asynchronous Task and Notification Alerting
- Failed email deliveries are captured in the database with retry counters, timestamps, and exact exception details (`email_error` and `email_attempts`).
- Administrators can monitor failures via `GET /api/admin/email-failures/`.
- Recurring low-attendance scans run nightly via Celery Beat (`nightly_scan` task).

---

## 6. Roles and Maintenance Responsibilities

| Role | Primary Member | Responsibilities |
| --- | --- | --- |
| **Developer** | Kundhan Vudutha (`Kundhan73`) | Implementation of patches, bug fixes, database migrations, Docker configuration, and CI/CD workflow updates. |
| **Tester** | Tarun J (`DarkTJ7`) | Independent execution of test suites after updates, verifying bug fixes (#45, #46), executing staging performance, ZAP, and accessibility tests. |
| **QA Engineer** | Anish (`planetai05`) | Monitoring compliance with SRS/SAD/STP, updating Requirements Traceability Matrix (`TRACEABILITY.md`), validating test and coverage reports, auditing maintenance records, and conducting PR release reviews. |
| **System Administrator (Ops)** | Faculty/IT Operations | Server OS patching, TLS certificate renewals, external DNS/Nginx configuration, offsite backup storage maintenance, and external uptime monitor administration. |

---

## 7. Operational Verification Still Required

- [ ] Install and run the scheduled backup, checksum, encryption, retention and offsite-transfer jobs; attach logs.
- [ ] Rehearse this corrected restore runbook on an isolated Docker database; attach schema/count/trigger checks and measured recovery time.
- [ ] Rehearse the explicit SHA-image override, migration compatibility and post-rollback smoke checks.
- [ ] Configure an external monitor and retain actual uptime/alert evidence; backend health tests alone do not prove monitoring is installed.
- [x] Maintenance window policy defined to preserve SAMS-NF-002 SLA boundaries.
- [x] Operational roles delineated across Developer, Tester, QA, and SysAdmin.
