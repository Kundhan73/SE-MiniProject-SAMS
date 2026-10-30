# Run, deliver and maintain SAMS

## Local demo

Follow the root README. SQLite and terminal email make the demo independent of cloud credentials. Current-date sessions are generated from weekly slots when faculty open the dashboard. P and OD count as attended; an enrollment with no held classes displays “No classes” rather than 0%.

Django reads environment variables directly. The `.env` file is read by Docker Compose; a direct local Python invocation needs environment variables exported in the shell. Never commit `.env`, databases, real student lists, SMTP credentials, certificates or private keys.

## Full Docker stack

Copy `.env.example` to `.env`, change its PostgreSQL password and secret, and run `docker compose up --build -d`. The one-shot migrate service runs database migrations and collects static files before the web and background workers start. Seed only once with `docker compose exec web python manage.py seed_demo`.

Use `docker compose ps`, `docker compose logs --tail=100 web worker beat`, and `/api/health/` for diagnosis. The health endpoint checks the database and, with real background jobs enabled, Redis. An unavailable Redis returns 503.

`docker compose exec web python manage.py shell -c "from notifications.tasks import nightly_scan; nightly_scan.delay()"` runs the nightly low-attendance scan immediately. Notifications are deduplicated per student/section/day. SMTP failures retry with backoff; exhausted failures remain visible through the Admin-only `/api/admin/email-failures/` endpoint. In-app messages survive email failures.

## HTTPS staging

Obtain a valid certificate for the staging domain. Mount `docker/certs/fullchain.pem` and `docker/certs/privkey.pem`; this directory is ignored by Git. Change `server_name` in `docker/nginx-tls.conf` and set:

```text
DJANGO_DEBUG=0
DJANGO_SECRET_KEY=<random value of at least 50 characters>
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,<staging-host>
PUBLIC_URL=https://<staging-host>:8443
CSRF_TRUSTED_ORIGINS=https://<staging-host>:8443
```

Run `docker compose -f docker-compose.yml -f docker-compose.tls.yml up --build -d`. The supplied local staging overlay binds HTTP to 8000 and HTTPS to 8443 on loopback, redirects HTTP to 8443, and permits TLS 1.2/1.3 only. For a real server, bind the desired network interface and standard 80/443 ports, remove `:8443` from the redirect/public URL, configure the firewall and DNS, and obtain a matching certificate. Do not expose the development HTTP configuration.

Django trusts `X-Forwarded-Proto` only behind the configured Nginx proxy; the web service is not published directly in Compose. Verify the actual certificate, redirects, HSTS and rejected TLS versions with `curl` and `testssl.sh` on staging. Configuration presence is not proof of a live TLS check.

## Delivery and rollback

GitHub Actions publishes to GHCR only after successful CI on a push to main. PR code runs without package-write permission. Images have immutable `sha-<commit>` tags for reproducible release selection; `latest` is a convenience alias.

The repository currently supplies continuous delivery, not a remote deployment that has already run. A server/domain was not provided. Pull the reviewed image on the chosen host, run migrations, replace the application container, then check health and the three role workflows. Use the previous SHA-tagged image for application rollback. Review migration compatibility before rolling back; restore a database backup when a schema rollback is required.

Jenkins can run the included Jenkinsfile with Python, Docker and (optionally) `sonar-scanner` on its agent. Set `SONAR_HOST_URL` and a Jenkins secret-text credential named `sams-sonar-token` to enable the SonarQube quality gate. GitHub Actions is usable without that external infrastructure. No successful Jenkins or SonarQube run is claimed without an actual server execution.

## Data protection and maintenance

Back up PostgreSQL daily to an access-controlled location: `docker compose exec -T db sh -c 'pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB"' > sams-backup.sql`. Keep backups out of Git. Rehearse restore into a separate database before relying on backups.

Audit rows have no update/delete API and database triggers reject update/delete even through raw SQL. Database owners retain administrative power; use separate migration/runtime roles and protect backup access in a deployed institution. Retain records for the current academic year and document any archival process. The project does not auto-purge audit data.

Review dependency alerts weekly, rotate real secrets when needed, run migrations during announced maintenance, and re-run tests before releases. Measure semester uptime externally; a passing health endpoint does not establish 99% uptime.

## Proxy security headers

The HTTP and HTTPS proxies emit a CSP restricting scripts and API connections to the same origin. The existing Google Fonts stylesheet/font origins remain explicitly allowed. Attendance bars set numeric widths through the trusted external script rather than inline style attributes, so the policy requires neither unsafe-inline nor unsafe-eval. Nginx-served static files and proxied responses receive nosniff; the proxy hides its version and disables unused camera, microphone and geolocation capabilities.

The CSRF cookie remains readable because the external JavaScript constructs X-CSRFToken from it. This is distinct from the HttpOnly authentication/session cookie. Cross-origin embedding isolation is not enabled merely to silence a scanner finding; assess it against actual integration needs. These headers and a local scan do not establish live public TLS validation.

API documentation uses the pinned drf-spectacular-sidecar package for same-origin Swagger assets, SpectacularSwaggerSplitView for its external initializer, and an external stylesheet. The same strict CSP applies to documentation and application pages; neither a CDN script exception nor inline styles are required. The Swagger validator is disabled to keep schema requests on the same origin.
