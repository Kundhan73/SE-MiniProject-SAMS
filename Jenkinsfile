pipeline {
  agent any
  options { timestamps(); disableConcurrentBuilds() }
  environment { CELERY_TASK_ALWAYS_EAGER = '1' }
  stages {
    stage('Setup') { steps { sh 'python3 -m venv .venv && .venv/bin/pip install --upgrade pip && .venv/bin/pip install -r requirements-dev.txt' } }
    stage('Lint and migrations') { steps { sh '.venv/bin/ruff check . && .venv/bin/ruff format --check . && .venv/bin/python manage.py check && .venv/bin/python manage.py makemigrations --check --dry-run' } }
    stage('Tests and coverage') { steps { sh '.venv/bin/pytest --cov --cov-report=xml:docs/reports/coverage.xml --junitxml=docs/reports/junit.xml && .venv/bin/python scripts/test_reports.py' } }
    stage('Dependency audit') { steps { sh '.venv/bin/pip-audit --format json --output docs/reports/dependency-audit.json' } }
    stage('SonarQube') {
      when { expression { return env.SONAR_HOST_URL?.trim() } }
      steps { withCredentials([string(credentialsId: 'sams-sonar-token', variable: 'SONAR_TOKEN')]) { sh 'sonar-scanner -Dsonar.qualitygate.wait=true' } }
    }
    stage('Container') { steps { sh 'docker build -t sams:$BUILD_NUMBER .' } }
  }
  post {
    always { junit allowEmptyResults: true, testResults: 'docs/reports/junit.xml'; archiveArtifacts allowEmptyArchive: true, artifacts: 'docs/reports/*' }
  }
}
