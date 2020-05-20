def call() {
    pipeline {
        agent {
            docker {
                image "mb-demo/jenkins/agent:v0.2"
                registryUrl "https://harbor.mb.com"
                registryCredentialsId "harbor-credentials"
                args """
                    -u  root
                    -v /etc/shadow:/etc/shadow:ro
                    -v /etc/passwd:/etc/passwd:ro
                    -v /etc/group:/etc/group:ro
                    -v /etc/hosts:/etc/hosts:ro
                    -v /root/.kube/config:/root/.kube/config
                """
            }
        }
        stages {
            stage("clean K8S namepspace") {
                steps {
                  script {
                      echo "###################################### Cleaning and removing K8S Namespace ####################################################"
                      sh '''
                        kubectl delete ns $NAMESPACE || true
                      '''
                  }
                }
            }
        }
    }
}
