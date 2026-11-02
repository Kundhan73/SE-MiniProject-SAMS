#!/usr/bin/env bash
# Execute the real Jenkinsfile against a disposable SonarQube server on a hosted runner.
set -euo pipefail
: "${RUNNER_TEMP:?Requires an isolated GitHub Actions runner}"
: "${GITHUB_WORKSPACE:?}"
export JENKINS_HOME="$RUNNER_TEMP/sams-jenkins"
export SAMS_SOURCE_DIR="$GITHUB_WORKSPACE"
export SONAR_HOST_URL=http://127.0.0.1:9000
mkdir -p "$JENKINS_HOME/init.groovy.d" "$JENKINS_HOME/workspace" "$RUNNER_TEMP/sams-bin" evidence/jenkins
cp scripts/ci/jenkins-init.groovy "$JENKINS_HOME/init.groovy.d/sams.groovy"
# A clean local clone gives Jenkins its normal workspace and preserves the exact source commit.
git clone --no-hardlinks "$GITHUB_WORKSPACE" "$JENKINS_HOME/workspace/sams"
git rev-parse HEAD > evidence/jenkins/source-commit.txt
curl --fail --location --retry 3 https://get.jenkins.io/war-stable/2.580.2/jenkins.war -o "$RUNNER_TEMP/jenkins.war"
curl --fail --location --retry 3 https://github.com/jenkinsci/plugin-installation-manager-tool/releases/download/2.16.0/jenkins-plugin-manager-2.16.0.jar -o "$RUNNER_TEMP/jenkins-plugin-manager.jar"
java -jar "$RUNNER_TEMP/jenkins-plugin-manager.jar" --war "$RUNNER_TEMP/jenkins.war" --plugin-download-directory "$JENKINS_HOME/plugins" --plugins workflow-aggregator pipeline-model-definition credentials-binding timestamper junit
sudo sysctl -w vm.max_map_count=524288
docker run -d --name sams-sonar -p 127.0.0.1:9000:9000 sonarqube@sha256:f95aaa9016dd4e92c7d70691167a6d96dbb5d8acffd61eba1cb4335d364a7840
cleanup() {
  if [[ -n "${jenkins_pid:-}" ]]; then kill "$jenkins_pid" 2>/dev/null || true; fi
  docker logs sams-sonar > evidence/jenkins/sonarqube.log 2>&1 || true
  docker rm -f sams-sonar >/dev/null 2>&1 || true
}
trap cleanup EXIT
ready=false
for _ in $(seq 1 150); do
  if curl -fsS "$SONAR_HOST_URL/api/system/status" | jq -e '.status == "UP"' >/dev/null; then ready=true; break; fi
  sleep 2
done
[[ "$ready" == true ]]
# The fixture password/token are generated per run, masked, and never archived.
export JENKINS_CI_PASSWORD="$(openssl rand -hex 24)"
sonar_password="Aa1!$(openssl rand -hex 24)"
printf '::add-mask::%s\n' "$JENKINS_CI_PASSWORD" "$sonar_password"
curl --fail-with-body -sS -u admin:admin -X POST "$SONAR_HOST_URL/api/users/change_password" --data-urlencode login=admin --data-urlencode previousPassword=admin --data-urlencode "password=$sonar_password"
export SAMS_SONAR_TOKEN="$(curl -fsS -u "admin:$sonar_password" -X POST "$SONAR_HOST_URL/api/user_tokens/generate" --data-urlencode name=sams-ci | jq -er .token)"
printf '::add-mask::%s\n' "$SAMS_SONAR_TOKEN"
# An explicit overall-coverage gate applies even on the first analysis (new-code gates do not).
curl -fsS -u "admin:$sonar_password" -X POST "$SONAR_HOST_URL/api/projects/create" --data-urlencode project=sams --data-urlencode name=SAMS > /dev/null
curl -fsS -u "admin:$sonar_password" -X POST "$SONAR_HOST_URL/api/qualitygates/create" --data-urlencode name=SAMS-acceptance > /dev/null
curl -fsS -u "admin:$sonar_password" -X POST "$SONAR_HOST_URL/api/qualitygates/create_condition" --data-urlencode gateName=SAMS-acceptance --data-urlencode metric=coverage --data-urlencode op=LT --data-urlencode error=80 > /dev/null
curl -fsS -u "admin:$sonar_password" -X POST "$SONAR_HOST_URL/api/qualitygates/select" --data-urlencode gateName=SAMS-acceptance --data-urlencode projectKey=sams > /dev/null
docker pull sonarsource/sonar-scanner-cli@sha256:47956b669bf486bdad919e1cbd0533223515aa0b6d1d31763e5a3754942df6d7
cat > "$RUNNER_TEMP/sams-bin/sonar-scanner" <<'SCANNER'
#!/usr/bin/env bash
set -euo pipefail
docker run --rm --network host --user "$(id -u):$(id -g)" -e SONAR_HOST_URL -e SONAR_TOKEN -e SONAR_USER_HOME=/tmp/sonar -v "$PWD:/usr/src" sonarsource/sonar-scanner-cli@sha256:47956b669bf486bdad919e1cbd0533223515aa0b6d1d31763e5a3754942df6d7 -Dsonar.working.directory=/usr/src/.scannerwork "$@"
SCANNER
chmod +x "$RUNNER_TEMP/sams-bin/sonar-scanner"
export PATH="$RUNNER_TEMP/sams-bin:$PATH"
java -Xmx768m -Djenkins.install.runSetupWizard=false -jar "$RUNNER_TEMP/jenkins.war" --httpListenAddress=127.0.0.1 --httpPort=8081 > evidence/jenkins/controller.log 2>&1 &
jenkins_pid=$!
finished=false
for _ in $(seq 1 600); do
  if curl -fsS -u "ci:$JENKINS_CI_PASSWORD" 'http://127.0.0.1:8081/job/sams/1/api/json' -o evidence/jenkins/build.json; then
    if jq -e '.building == false' evidence/jenkins/build.json >/dev/null; then finished=true; break; fi
  fi
  kill -0 "$jenkins_pid"
  sleep 2
done
curl -fsS -u "ci:$JENKINS_CI_PASSWORD" http://127.0.0.1:8081/job/sams/1/consoleText > evidence/jenkins/console.txt
cp -R "$JENKINS_HOME/workspace/sams/docs/reports" evidence/jenkins/reports
curl -sS -u "admin:$sonar_password" "$SONAR_HOST_URL/api/qualitygates/project_status?projectKey=sams" > evidence/jenkins/quality-gate.json
curl -sS -u "admin:$sonar_password" "$SONAR_HOST_URL/api/issues/search?componentKeys=sams&ps=500" > evidence/jenkins/sonar-issues.json
curl -sS -u "admin:$sonar_password" "$SONAR_HOST_URL/api/hotspots/search?projectKey=sams&ps=500" > evidence/jenkins/sonar-hotspots.json
docker image inspect sonarqube@sha256:f95aaa9016dd4e92c7d70691167a6d96dbb5d8acffd61eba1cb4335d364a7840 sonarsource/sonar-scanner-cli@sha256:47956b669bf486bdad919e1cbd0533223515aa0b6d1d31763e5a3754942df6d7 --format '{{json .RepoDigests}}' > evidence/jenkins/image-digests.txt
java -jar "$RUNNER_TEMP/jenkins.war" --version > evidence/jenkins/jenkins-version.txt
find "$JENKINS_HOME/plugins" -maxdepth 1 -name '*.jpi' -printf '%f\n' > evidence/jenkins/plugins.txt
[[ "$finished" == true ]]
jq -e '.result == "SUCCESS"' evidence/jenkins/build.json
jq -e '.projectStatus.status == "OK" and ([.projectStatus.conditions[] | select(.metricKey == "coverage" and .status == "OK" and (.actualValue | tonumber) >= 80)] | length) == 1' evidence/jenkins/quality-gate.json
