# Real Jenkins/Sonar execution · 3 November 2026

[GitHub Actions run 41505698588](https://github.com/Kundhan73/SE-MiniProject-SAMS/actions/runs/41505698588) executed the repository Jenkinsfile on an isolated Jenkins controller and SonarQube server. The actual PR test-merge source is recorded in `source-commit.txt`; it combines PR #56 candidate `99cf0bb` with main. This is not a permanent external deployment.

Jenkins build #1 returned **SUCCESS**, with **166 tests**, zero failures/skips. Setup, lint/migrations, coverage gates, dependency audit, Sonar analysis and Docker build all executed. Sonar returned **OK**, with an actual overall `coverage` condition of **99.7%** against the **80%** threshold. Coverage imported without unresolved-file errors; app statement and branch gates remain 80%/70% in the test report generator.

The adjacent files are copied from the real run's `jenkins-sonarqube-evidence` artifact. Console output retains the stage sequence and quality-gate decision; tool/image metadata and raw build/gate/issue JSON are preserved. Credentials were disposable and masked; credential storage is not included. The complete artifact additionally retains generated JUnit/coverage and reports.

Earlier setup failures remain in Actions runs 41503645738 and 41504158342. Run 41504690049 successfully executed Jenkins but used the default first-analysis gate with no measured conditions and unresolved coverage paths; it is superseded by the explicit measured-gate run above.
