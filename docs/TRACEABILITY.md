# Requirements traceability · implemented baseline

“Automated” below means service/API regression evidence exists; it does not imply human acceptance. Original reference case IDs are retained where scenarios match.

| Requirement | Implementation | Automated evidence |
| --- | --- | --- |
| SAMS-F-001 login | accounts/services.py, core/web.py | IT_AUTH_01, UT_AUTH_01/02/05, browser login |
| F-002 role access | core/permissions.py, core/api.py | IT_AUTH_02, ST_SEC_04, anonymous-denial matrix |
| F-003 lockout | accounts/services.py | UT_AUTH_03/04 |
| F-004 reset | accounts/services.py, notifications/tasks.py | UT_PWR_01–05, IT_PWR_01–03 |
| F-005 scheduled roll | courses/services.py, ClassSession | UT_ATT_01/02, roster query-budget test |
| F-006 P/A/OD marking | attendance/services.py | UT_ATT_03/05/06, IT_ATT_01/02, browser marking |
| F-007 duplicate/edit guard | DB constraints, transaction, audit | UT_ATT_04/07, duplicate-student and submitted-roster regressions |
| F-008 private student view | reports/services.py, student API | UT_VIEW_01–04, browser student flow |
| F-009 corrections | attendance/services.py | UT_COR_01–06, IT_COR_01/02, browser approval |
| F-010 per-student report | reports/services.py | UT_REP_03, private-view tests |
| F-011 per-course report | report API course/section filters | UT_REP_03, IT_REP_01/02 |
| F-012 date-range report | inclusive date filters | UT_REP_04, invalid-date tests |
| F-013 defaulters/export | threshold comparison, CSV/PDF | UT_REP_01/05/06, equality, CSV safety, PDF pagination |
| F-014 courses/sections | courses models/admin API | UT_CRS_01, IT_CRS_01–03 |
| F-015 timetable | courses/services.py | UT_CRS_02–04 |
| F-016 faculty/roll linkage | Section, session faculty snapshot | UT_ATT_01/02, other-faculty-denied tests |
| F-017 low-attendance alerts | nightly_scan Celery task | UT_NOT_01/02, no-alert-above-threshold |
| F-018 pending corrections | notifications + decision service | UT_COR_01, UT_NOT_03, notification scoping |
| F-019 user/role admin | user APIs | IT_ADM_03, self-lockout and role-in-use checks |
| F-020 threshold setting | SystemConfig | UT_ADM_02, numeric boundary/NaN tests |
| F-021 audit | AuditLog + triggers + read-only API | UT_ADM_03/04, IT_ADM_01, raw SQL mutation tests |
| NF-001 latency | bounded roster queries, bulk inserts | Query budget regression; full concurrency performance pending on staging |
| NF-002 uptime | health DB/Redis checks | Health success/outage tests; semester uptime pending |
| NF-003 salted hashing/HTTPS | Django hashing, production flags, TLS Nginx | Hash regression; live TLS verification pending |
| NF-004 year retention | persistent PostgreSQL/audit, no purge | Immutability tests; year-long retention review pending |
| NF-005 responsive/accessibility | role templates/custom CSS | 360px Chromium overflow test; full Lighthouse/keyboard/cross-browser audit pending |
| NF-006 2,000 students/100 faculty | --full synthetic seed, same models | Seed command provided; actual target-load report must name deployment and concurrency |
| SR-001 TLS 1.2+ | docker/nginx-tls.conf | Configuration supplied; live test pending |
| SR-002 password protection | Django hash store, restricted API outputs | No-password-response regression, production-hash test |
| SR-003 inactivity/logout | Django idle cookies, LoginSession JWT family | Expired access/idle checks and both logout paths |
| SR-004 server RBAC | role and ownership checks | Cross-role and IDOR rejection tests |
| SR-005 append-only edits | audit service/model/DB triggers | ORM/API/raw SQL immutability and edit/correction history |
