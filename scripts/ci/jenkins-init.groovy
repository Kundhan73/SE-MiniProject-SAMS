import jenkins.model.Jenkins
import hudson.security.HudsonPrivateSecurityRealm
import hudson.security.FullControlOnceLoggedInAuthorizationStrategy
import com.cloudbees.plugins.credentials.CredentialsScope
import com.cloudbees.plugins.credentials.SystemCredentialsProvider
import org.jenkinsci.plugins.plaincredentials.impl.StringCredentialsImpl
import hudson.util.Secret
import org.jenkinsci.plugins.workflow.job.WorkflowJob
import org.jenkinsci.plugins.workflow.cps.CpsFlowDefinition

// Disposable loopback-only CI controller. Never install this fixture on a shared server.
def instance = Jenkins.get()
def realm = new HudsonPrivateSecurityRealm(false)
realm.createAccount('ci', System.getenv('JENKINS_CI_PASSWORD'))
instance.setSecurityRealm(realm)
def authorization = new FullControlOnceLoggedInAuthorizationStrategy()
authorization.setAllowAnonymousRead(false)
instance.setAuthorizationStrategy(authorization)
instance.setNumExecutors(1)
SystemCredentialsProvider.getInstance().getCredentials().add(
    new StringCredentialsImpl(CredentialsScope.GLOBAL, 'sams-sonar-token',
        'Disposable validation token', Secret.fromString(System.getenv('SAMS_SONAR_TOKEN'))))
def job = instance.createProject(WorkflowJob, 'sams')
job.setDefinition(new CpsFlowDefinition(new File(System.getenv('SAMS_SOURCE_DIR'), 'Jenkinsfile').text, true))
instance.save()
job.save()
job.scheduleBuild2(0)
