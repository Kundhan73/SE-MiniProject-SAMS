# Jenkins and SonarQube validation

The [Jenkins and SonarQube validation workflow](../.github/workflows/jenkins-validation.yml) executes the repository Jenkinsfile on every pull request, main push and manual dispatch. Its Actions result and `jenkins-sonarqube-evidence` artifact are the execution record; configuration alone is not a passing run.

The isolated hosted fixture runs Jenkins 2.580.2 with Java 21, SonarQube and SonarScanner images pinned by digest. Jenkins performs environment setup, lint/migration checks, the complete backend suite and coverage gates, dependency audit, Sonar analysis with a waited quality gate, and a Docker build. The explicit Sonar gate requires overall coverage of at least 80%, including on a first analysis; pytest/report generation separately require at least 80% statement and 70% branch coverage. Coverage paths are repository-relative and retain distinct application modules with the same filename.

The artifact contains the actual Jenkins result, console/controller logs, JUnit/coverage and generated reports, Sonar quality-gate condition values/issues, exact source commit and tool metadata. A successful Jenkins build with a missing or unmeasured coverage condition fails the outer check. Setup failures remain visible in Actions and must not be relabeled as application passes.

Jenkins and Sonar bind only to loopback on the disposable runner. Credentials are generated for each execution, masked and discarded; Jenkins credential storage is excluded from artifacts. The fixture uses Sonar's evaluation database and is not a persistent production service. Plugin dependencies resolve during setup; container and Jenkins versions are pinned.

For a permanent institutional installation, provide a Python 3.12 agent with Docker and SonarScanner, set `SONAR_HOST_URL`, and create secret-text credential `sams-sonar-token`. Configure the project quality gate and PR/webhook integration on that server. Never install the disposable initialization fixture on a shared controller. Retain real server evidence separately from this ephemeral validation.
