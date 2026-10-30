# API reference

Base `/api/`. Interactive request definitions: `/api/docs/`; generated OpenAPI: `docs/openapi.yaml`. Browser UI uses Django sessions and CSRF tokens; API clients can use `Authorization: Bearer <access>`. Unsafe requests using cookies need `X-CSRFToken`. Login itself requires a CSRF token obtained from `/login/`, including API login.

Errors use `{"error":{"code":"...","message":"...","details":{}}}`. Validation errors may include structured field details. No stack trace or password is returned in production.

| Method / path | Role | Input / output |
| --- | --- | --- |
| GET health/ | Public | `{status:ok}`; 503 if configured Redis is unavailable |
| POST auth/login/ | Public + CSRF | `{institute_id,password}` → access, refresh, role, name, public user details |
| POST auth/refresh/ | Public | `{refresh}` → access; revoked/idle/disabled sessions rejected |
| POST auth/logout/ | Authenticated | 205; revokes current bearer family and associated browser JWT family; clears browser session |
| POST auth/password-reset/ | Public | `{email}` → generic 202 response |
| POST auth/password-reset/confirm/ | Public | `{token,new_password}`; 410 for invalid/expired/used token |
| GET me/ | Authenticated | id, institute_id, name, role, email, is_active |
| GET sessions/today/ | Faculty | Sessions assigned to current faculty, submitted flag and roster/status/record IDs |
| POST sessions/{id}/attendance/ | Assigned faculty | `{records:[{student_id,status}]}`; complete unique roll list, P/A/OD; 201 or 409 duplicate |
| PATCH records/{id}/ | Assigned faculty/Admin | `{status,reason}` → updated status plus audit |
| GET students/me/attendance/ | Student | Per-course held, attended, percentage or null, below_threshold |
| GET students/me/records/ | Student | Latest 500 own marks: id/date/course/status |
| GET corrections/ | Authenticated | Own requests for student; assigned requests for faculty; all for Admin; latest 500 |
| POST corrections/ | Student | `{record_id,requested_status,reason}`; own marks only; one pending request |
| PATCH corrections/{id}/ | Assigned faculty | `{decision:APPROVE\|REJECT,note?}`; atomic decision, notification and approved edit |
| GET reports/summary/ | Faculty/Admin | Scoped report rows; faculty limited to own sessions/sections |
| GET reports/defaulters/ | Faculty/Admin | Same shape, strictly below configured/explicit threshold |
| GET/POST admin/courses/ | Admin | List or create `{code,title}` |
| GET/POST admin/sections/ | Admin | List or create `{course_id,faculty_id,name}` |
| GET/POST admin/timetable/ | Admin | List or create `{section_id,weekday:0..6,start:HH:MM,end:HH:MM}`; reject clashes |
| POST admin/sections/{id}/enroll/ | Admin | `{csv:"institute_id\nSTU001\n..."}` → enrolled count and per-row errors |
| GET/POST admin/users/ | Admin | Search `?q=ID`; create `{institute_id,email,name,password,role}`; no password in response |
| PATCH admin/users/{id}/ | Admin | `{role?,is_active?}`; guards own admin access and assigned role changes |
| GET/PATCH admin/config/ | Admin | Read/set `{threshold:0..100}` |
| GET audit/ | Admin | `{count,results}`; 100/page, `page`, `record`, `editor`, inclusive `from`/`to`; no write API |
| GET notifications/ | Authenticated | Latest 100 own notifications |
| POST notifications/{id}/read/ | Owner | Mark own notification read |
| GET admin/email-failures/ | Admin | Failed delivery metadata; no SMTP credential disclosure |

Report filters: `course` (code), `section` (name), `student` (institute ID), inclusive `from`/`to` (YYYY-MM-DD), `threshold` (0–100), `export=json|csv|pdf`. `format=` also works for compatibility; the renderer override is disabled. JSON rows contain student_id, srn, name, section_id, section, course, held, attended, percentage and below_threshold.

There is no hard-delete API for submitted sessions, attendance or audit entries. Creating courses/sections and enrollment is sufficient for the initial semester setup. Timetable changes create new slots; existing submitted records retain session/faculty references. New enrollment does not fabricate marks for past submitted classes.
