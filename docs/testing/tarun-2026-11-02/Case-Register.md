# Dated test case register — 2 November 2026

These are live HTTP/TLS executions. Browser screenshots, 49 browser checks, six Lighthouse snapshots, and backend reports are retained separately. Tool-assisted execution does not substitute for the accountable tester's personal review.

| Test ID | Issue | Expected | Actual | Result | Commit tested |
| --- | --- | --- | --- | --- | --- |
| AUTH-ROLE-ADMIN | #37 | Authenticated identity has expected role | {"http_status": 200, "role": "ADMIN"} | PASS | b60f42b |
| AUTH-ROLE-FACULTY | #37 | Authenticated identity has expected role | {"http_status": 200, "role": "FACULTY"} | PASS | b60f42b |
| AUTH-ROLE-STUDENT | #37 | Authenticated identity has expected role | {"http_status": 200, "role": "STUDENT"} | PASS | b60f42b |
| AUTH-STUDENT-ADMIN | #37 | Student administrator access rejected | {"http_status": 403, "error_code": "FORBIDDEN"} | PASS | b60f42b |
| AUTH-CSRF-LOGIN | #37 | Login without a CSRF cookie/header is rejected | {"http_status": 403, "error_code": "PERMISSION_DENIED"} | PASS | b60f42b |
| SETUP-COURSE-A | #38 | Create a synthetic course | {"http_status": 201} | PASS | b60f42b |
| SETUP-SECTION-A | #38 | Create a section assigned to faculty | {"http_status": 201} | PASS | b60f42b |
| SETUP-COURSE-B | #38 | Create a synthetic course | {"http_status": 201} | PASS | b60f42b |
| SETUP-SECTION-B | #38 | Create a section assigned to faculty | {"http_status": 201} | PASS | b60f42b |
| SETUP-COURSE-C | #38 | Create a synthetic course | {"http_status": 201} | PASS | b60f42b |
| SETUP-SECTION-C | #38 | Create a section assigned to faculty | {"http_status": 201} | PASS | b60f42b |
| SETUP-DUPLICATE-COURSE | #38 | Duplicate code rejected | {"http_status": 409, "error_code": "CONFLICT"} | PASS | b60f42b |
| SETUP-CSV-PARTIAL | #38 | Two valid rows enrolled; invalid row reported | {"http_status": 200, "enrolled": 2, "errors": [{"row": 3, "reason": "Unknown or inactive student"}]} | PASS | b60f42b |
| SETUP-CSV-HEADER | #38 | Missing institute_id header rejected | {"http_status": 400, "error_code": "INVALID_CSV"} | PASS | b60f42b |
| SETUP-CSV-IDEMPOTENT | #38 | Repeated enrollment creates no duplicates | {"http_status": 200, "enrolled": 0, "errors": []} | PASS | b60f42b |
| SETUP-ENROLL-CONCURRENCY | #38 | Two concurrent imports enroll exactly one row in total | {"http_status": 200, "statuses": [200, 200], "created_total": 1} | PASS | b60f42b |
| SETUP-TIMETABLE | #38 | Create a valid current-day timetable slot | {"http_status": 201} | PASS | b60f42b |
| SETUP-FACULTY-CLASH | #38 | Overlapping faculty slot rejected | {"http_status": 409, "error_code": "TIMETABLE_CLASH"} | PASS | b60f42b |
| SETUP-ADJACENT-SLOT | #38 | Adjacent slot accepted | {"http_status": 201} | PASS | b60f42b |
| SETUP-INVALID-WEEKDAY | #38 | Weekday outside 0..6 rejected | {"http_status": 400, "error_code": "INVALID"} | PASS | b60f42b |
| ATT-COMPLETE-ROSTER | #39 | Partial roster rejected atomically | {"http_status": 400, "error_code": "NOT_IN_ROSTER"} | PASS | b60f42b |
| ATT-PAOD | #39 | Complete P/A/OD roster saved once | {"http_status": 201, "session_id": 163, "saved": 3, "present": 1, "absent": 1, "on_duty": 1} | PASS | b60f42b |
| ATT-DUPLICATE | #39 | Repeated submission rejected | {"http_status": 409, "error_code": "ALREADY_SUBMITTED"} | PASS | b60f42b |
| ATT-CONCURRENT-DUPLICATE | #39 | Concurrent submissions produce one 201 and one 409 | {"http_status": 409, "error_code": "ALREADY_SUBMITTED", "statuses": [201, 409]} | PASS | b60f42b |
| ATT-EDIT-REASON | #39 | Blank edit reason rejected | {"http_status": 400, "error_code": "INVALID"} | PASS | b60f42b |
| ATT-FOREIGN-FACULTY | #39 | Other faculty cannot edit | {"http_status": 403, "error_code": "NOT_SESSION_FACULTY"} | PASS | b60f42b |
| ATT-AUDITED-EDIT | #39 | Authorized reasoned edit accepted | {"http_status": 200} | PASS | b60f42b |
| ATT-AUDIT-HISTORY | #39 | Original mark and reasoned edit appear in audit | {"http_status": 200, "matching_edit_entries": 1, "entries_for_record": 2} | PASS | b60f42b |
| STUDENT-PRIVACY | #40 | Student sees their own records and not the other new record | {"http_status": 200, "own_record_present": true, "foreign_record_present": false} | PASS | b60f42b |
| STUDENT-NO-CLASSES | #40 | Unmarked enrolled course has null percentage | {"http_status": 200, "rows": [{"student_id": 102, "srn": "STU001", "name": "Student 001", "section_id": 26, "section": "C", "course": "QA1102151545C", "held": 0, "attended": 0, "percentage": null, "below_threshold": false}]} | PASS | b60f42b |
| COR-CREATE | #40 | Own correction accepted | {"http_status": 201} | PASS | b60f42b |
| COR-DUPLICATE | #40 | Second pending correction rejected | {"http_status": 409, "error_code": "OPEN_REQUEST_EXISTS"} | PASS | b60f42b |
| COR-FACULTY-ROUTING | #40 | Other faculty cannot decide | {"http_status": 403, "error_code": "NOT_SESSION_FACULTY"} | PASS | b60f42b |
| COR-APPROVE | #40 | Owning faculty approves | {"http_status": 200, "state": "APPROVED"} | PASS | b60f42b |
| COR-REPEAT-DECISION | #40 | Repeated decision rejected | {"http_status": 409, "error_code": "ALREADY_DECIDED"} | PASS | b60f42b |
| COR-REJECT | #40 | Owning faculty rejects correction | {"http_status": 200, "state": "REJECTED"} | PASS | b60f42b |
| REPORT-INCLUSIVE-FILTERS | #41 | Exact student/course/date filters include approved OD as attended | {"http_status": 200, "rows": [{"student_id": 102, "srn": "STU001", "name": "Student 001", "section_id": 24, "section": "A", "course": "QA1102151545A", "held": 1, "attended": 1, "percentage": 100.0, "below_threshold": false}]} | PASS | b60f42b |
| REPORT-THRESHOLD-100 | #41 | Strict below-threshold comparison, equality not flagged | {"http_status": 200, "threshold": 100, "below_threshold": false} | PASS | b60f42b |
| REPORT-THRESHOLD-0 | #41 | Strict below-threshold comparison, equality not flagged | {"http_status": 200, "threshold": 0, "below_threshold": false} | PASS | b60f42b |
| REPORT-THRESHOLD-0.01 | #41 | Strict below-threshold comparison, equality not flagged | {"http_status": 200, "threshold": "0.01", "below_threshold": true} | PASS | b60f42b |
| REPORT-DATE-RANGE | #41 | Inverted date range rejected | {"http_status": 400, "error_code": "INVALID_DATE_RANGE"} | PASS | b60f42b |
| REPORT-CSV | #41 | CSV MIME/header/filtered numeric percentage correct | {"http_status": 200, "content_type": "text/csv", "rows": 1} | PASS | b60f42b |
| REPORT-PDF-NUMERIC | #41 | Valid parsed PDF with correct percentage label | {"http_status": 200, "expected_text_found": true, "bad_no_classes_percent": false} | PASS | b60f42b |
| REPORT-PDF-NO-CLASSES | #41 | Valid parsed PDF with correct percentage label | {"http_status": 200, "expected_text_found": true, "bad_no_classes_percent": false} | PASS | b60f42b |
| REPORT-CSV-FORMULA | #41 | Spreadsheet-formula name is neutralized | {"http_status": 200, "prefix_quoted": true} | PASS | b60f42b |
| ATT-SNAPSHOT-ROSTER | #39 | Post-submission enrollment does not change submitted roster | {"http_status": 200, "roster_size": 3, "late_student_present": false} | PASS | b60f42b |
| ADMIN-SUSPEND | #42 | Admin suspends synthetic account | {"http_status": 200} | PASS | b60f42b |
| ADMIN-REVOKED-SESSION | #42 | Suspension revokes existing token | {"http_status": 401, "error_code": "AUTHENTICATION_FAILED"} | PASS | b60f42b |
| ADMIN-ROLE-IN-USE | #42 | Role change is rejected while student has an enrollment | {"http_status": 409, "error_code": "ROLE_IN_USE"} | PASS | b60f42b |
| ADMIN-ROLE-CHANGE | #42 | Unassigned synthetic account can change role | {"http_status": 200, "role": "FACULTY"} | PASS | b60f42b |
| ADMIN-SELF-LOCKOUT | #42 | Administrator cannot suspend own account | {"http_status": 400, "error_code": "SELF_LOCKOUT"} | PASS | b60f42b |
| ADMIN-THRESHOLD | #42 | Valid threshold persists | {"http_status": 200, "threshold": 80.0} | PASS | b60f42b |
| ADMIN-THRESHOLD-BOUND | #42 | Threshold above 100 rejected | {"http_status": 400, "error_code": "INVALID"} | PASS | b60f42b |
| NOTIFICATION-OWNERSHIP | #42 | Other student cannot mark notification read | {"http_status": 404, "error_code": "NOT_FOUND"} | PASS | b60f42b |
| NOTIFICATION-READ | #42 | Own notification can be marked read | {"http_status": 200, "read": true} | PASS | b60f42b |
| NOTIFICATION-FAILURES-ADMIN | #42 | Admin failure listing available | {"http_status": 200} | PASS | b60f42b |
| NOTIFICATION-FAILURES-STUDENT | #42 | Student failure listing denied | {"http_status": 403, "error_code": "FORBIDDEN"} | PASS | b60f42b |
| AUTH-LOGOUT | #37 | Logout succeeds | {"http_status": 205} | PASS | b60f42b |
| AUTH-LOGOUT-ACCESS | #37 | Logged-out token rejected | {"http_status": 401, "error_code": "AUTHENTICATION_FAILED"} | PASS | b60f42b |
| AUTH-LOGOUT-REFRESH | #37 | Logged-out refresh token rejected | {"http_status": 401, "error_code": "SESSION_EXPIRED"} | PASS | b60f42b |
| SEC-RBAC-GET-/api/admin/config/ | #30 | Student token rejected with HTTP 403 | {"http_status": 403, "error_code": "FORBIDDEN"} | PASS | b60f42b |
| SEC-RBAC-PATCH-/api/admin/config/ | #30 | Student token rejected with HTTP 403 | {"http_status": 403, "error_code": "FORBIDDEN"} | PASS | b60f42b |
| SEC-RBAC-GET-/api/admin/courses/ | #30 | Student token rejected with HTTP 403 | {"http_status": 403, "error_code": "FORBIDDEN"} | PASS | b60f42b |
| SEC-RBAC-POST-/api/admin/courses/ | #30 | Student token rejected with HTTP 403 | {"http_status": 403, "error_code": "FORBIDDEN"} | PASS | b60f42b |
| SEC-RBAC-GET-/api/admin/email-failures/ | #30 | Student token rejected with HTTP 403 | {"http_status": 403, "error_code": "FORBIDDEN"} | PASS | b60f42b |
| SEC-RBAC-GET-/api/admin/sections/ | #30 | Student token rejected with HTTP 403 | {"http_status": 403, "error_code": "FORBIDDEN"} | PASS | b60f42b |
| SEC-RBAC-POST-/api/admin/sections/ | #30 | Student token rejected with HTTP 403 | {"http_status": 403, "error_code": "FORBIDDEN"} | PASS | b60f42b |
| SEC-RBAC-POST-/api/admin/sections/1/enroll/ | #30 | Student token rejected with HTTP 403 | {"http_status": 403, "error_code": "FORBIDDEN"} | PASS | b60f42b |
| SEC-RBAC-GET-/api/admin/timetable/ | #30 | Student token rejected with HTTP 403 | {"http_status": 403, "error_code": "FORBIDDEN"} | PASS | b60f42b |
| SEC-RBAC-POST-/api/admin/timetable/ | #30 | Student token rejected with HTTP 403 | {"http_status": 403, "error_code": "FORBIDDEN"} | PASS | b60f42b |
| SEC-RBAC-GET-/api/admin/users/ | #30 | Student token rejected with HTTP 403 | {"http_status": 403, "error_code": "FORBIDDEN"} | PASS | b60f42b |
| SEC-RBAC-POST-/api/admin/users/ | #30 | Student token rejected with HTTP 403 | {"http_status": 403, "error_code": "FORBIDDEN"} | PASS | b60f42b |
| SEC-RBAC-PATCH-/api/admin/users/1/ | #30 | Student token rejected with HTTP 403 | {"http_status": 403, "error_code": "FORBIDDEN"} | PASS | b60f42b |
| SEC-RBAC-GET-/api/audit/ | #30 | Student token rejected with HTTP 403 | {"http_status": 403, "error_code": "FORBIDDEN"} | PASS | b60f42b |
| SEC-RBAC-PATCH-/api/corrections/1/ | #30 | Student token rejected with HTTP 403 | {"http_status": 403, "error_code": "FORBIDDEN"} | PASS | b60f42b |
| SEC-RBAC-PATCH-/api/records/1/ | #30 | Student token rejected with HTTP 403 | {"http_status": 403, "error_code": "FORBIDDEN"} | PASS | b60f42b |
| SEC-RBAC-GET-/api/reports/summary/ | #30 | Student token rejected with HTTP 403 | {"http_status": 403, "error_code": "FORBIDDEN"} | PASS | b60f42b |
| SEC-RBAC-POST-/api/sessions/1/attendance/ | #30 | Student token rejected with HTTP 403 | {"http_status": 403, "error_code": "FORBIDDEN"} | PASS | b60f42b |
| SEC-RBAC-GET-/api/sessions/today/ | #30 | Student token rejected with HTTP 403 | {"http_status": 403, "error_code": "FORBIDDEN"} | PASS | b60f42b |
| SEC-IDOR-STUDENT-CORRECTION | #30 | Another student record cannot be corrected (403) | {"http_status": 403, "error_code": "NOT_OWN_RECORD"} | PASS | b60f42b |
| SEC-IDOR-FACULTY-SUBMIT | #30 | Another faculty session cannot be marked (403) | {"http_status": 403, "error_code": "NOT_SESSION_FACULTY"} | PASS | b60f42b |
| SEC-IDOR-FACULTY-EDIT | #30 | Another faculty attendance record cannot be edited (403) | {"http_status": 403, "error_code": "NOT_SESSION_FACULTY"} | PASS | b60f42b |
| SEC-INJECTION-LOGIN-1 | #30 | Injection treated as invalid credentials, no server error (401) | {"http_status": 401, "error_code": "INVALID_CREDENTIALS"} | PASS | b60f42b |
| SEC-INJECTION-SEARCH-1 | #30 | Literal escaped search returns no users (200) | {"http_status": 200, "returned_rows": 0} | PASS | b60f42b |
| SEC-INJECTION-LOGIN-2 | #30 | Injection treated as invalid credentials, no server error (401) | {"http_status": 401, "error_code": "INVALID_CREDENTIALS"} | PASS | b60f42b |
| SEC-INJECTION-SEARCH-2 | #30 | Literal escaped search returns no users (200) | {"http_status": 200, "returned_rows": 0} | PASS | b60f42b |
| SEC-MALFORMED-JSON | #30 | Malformed JSON returns validation error (400) | {"http_status": 400, "error_code": "PARSE_ERROR"} | PASS | b60f42b |
| SEC-STORED-XSS-SETUP | #30 | Reason accepted as plain text; browser rendering checked separately (201) | {"http_status": 201} | PASS | b60f42b |
| SEC-IDOR-FACULTY-DECISION | #30 | Another faculty correction cannot be decided (403) | {"http_status": 403, "error_code": "NOT_SESSION_FACULTY"} | PASS | b60f42b |
| SEC-API-CREDENTIAL-LEAK | #30 | User responses contain no password/hash fields | {"http_status": 200, "rows_checked": 2105, "forbidden_fields_present": []} | PASS | b60f42b |
| SEC-LOGOUT | #30 | Logout revokes current session (205) | {"http_status": 205} | PASS | b60f42b |
| SEC-REVOKED-ACCESS | #30 | Access token from logged-out session rejected (401) | {"http_status": 401, "error_code": "AUTHENTICATION_FAILED"} | PASS | b60f42b |
| SEC-REVOKED-REFRESH | #30 | Refresh token from logged-out session rejected (401) | {"http_status": 401, "error_code": "SESSION_EXPIRED"} | PASS | b60f42b |
| AUTH-LOCKOUT-FIVE | #37 | Five incorrect passwords yield 401, then correct login is locked (423) | {"http_status": 423, "failed_attempt_statuses": [401, 401, 401, 401, 401]} | PASS | b60f42b |
| AUTH-RESET-KNOWN | #37 | Locked active user can request reset without revealing account existence | {"http_status": 202} | PASS | b60f42b |
| AUTH-RESET-ENUMERATION | #37 | Unknown and known email reset requests return identical public response | {"http_status": 202, "response_matches_known": true} | PASS | b60f42b |
| AUTH-RESET-MAILPIT | #37 | Worker sends reset link to the controlled synthetic Mailpit recipient | {"http_status": 200, "reset_link_present": true} | PASS | b60f42b |
| AUTH-RESET-WEAK | #37 | Weak replacement password rejected without consuming reset token | {"http_status": 400} | PASS | b60f42b |
| AUTH-RESET-CONSUME | #37 | Valid replacement password consumes token and clears lockout | {"http_status": 200} | PASS | b60f42b |
| AUTH-RESET-REVOKE-ACCESS | #37 | Password reset revokes the earlier access session | {"http_status": 401} | PASS | b60f42b |
| AUTH-RESET-REVOKE-REFRESH | #37 | Password reset revokes earlier refresh session | {"http_status": 401} | PASS | b60f42b |
| AUTH-RESET-REPLAY | #37 | Consumed reset token cannot be reused | {"http_status": 410} | PASS | b60f42b |
| AUTH-RESET-UNKNOWN | #37 | Unknown reset token rejected with same expiry/reuse response | {"http_status": 410} | PASS | b60f42b |
| AUTH-RESET-OLD-PASSWORD | #37 | Previous password cannot sign in after reset | {"http_status": 401} | PASS | b60f42b |
| AUTH-RESET-NEW-PASSWORD | #37 | New password signs in and cleared lockout permits access | {"http_status": 200} | PASS | b60f42b |
| TLS-HTTP-REDIRECT | #30 | 301 to exact HTTPS host, port and path | {"status": 301, "location": "https://localhost:8444/login/?next=/"} | PASS | b60f42b |
| TLS-VERIFIED-CHAIN | #30 | Valid localhost SAN and private-CA certificate verification, HTTP 200 | {"status": 200, "verification": "explicit private CA; verification enabled"} | PASS | b60f42b |
| TLS-HSTS | #30 | HSTS max-age >=31536000 | "max-age=31536000; includeSubDomains; preload, max-age=31536000" | PASS | b60f42b |
| TLS-PROTOCOL-TLSv1_2 | #30 | Accept TLS 1.2/1.3; server rejects TLS 1.0/1.1 | {"negotiated": "TLSv1.2", "cipher": "ECDHE-RSA-AES256-GCM-SHA384"} | PASS | b60f42b |
| TLS-PROTOCOL-TLSv1_3 | #30 | Accept TLS 1.2/1.3; server rejects TLS 1.0/1.1 | {"negotiated": "TLSv1.3", "cipher": "TLS_AES_256_GCM_SHA384"} | PASS | b60f42b |
| TLS-PROTOCOL-TLSv1 | #30 | Accept TLS 1.2/1.3; server rejects TLS 1.0/1.1 | {"ssl_reason": "TLSV1_ALERT_PROTOCOL_VERSION"} | PASS | b60f42b |
| TLS-PROTOCOL-TLSv1_1 | #30 | Accept TLS 1.2/1.3; server rejects TLS 1.0/1.1 | {"ssl_reason": "TLSV1_ALERT_PROTOCOL_VERSION"} | PASS | b60f42b |
| TLS-SESSION-COOKIE | #30 | Secure, HttpOnly and SameSite=Lax session cookie | {"secure": true, "httponly": true, "samesite": "Lax"} | PASS | b60f42b |
| TLS-AUTH-LOGOUT | #30 | Authenticated HTTPS logout succeeds | {"status": 205} | PASS | b60f42b |
