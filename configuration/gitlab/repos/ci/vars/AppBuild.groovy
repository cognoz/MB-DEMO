import groovy.json.JsonSlurper

def call() {
    pipeline {
        agent {
            docker {
                image "mb-demo/jenkins/agent:v0.2"
                registryUrl "https://harbor.mb.com"
                registryCredentialsId "harbor-credentials"
                args """
                    -u  root
                    -v /root/.ssh/:/root/.ssh
                    -v /var/run/docker.sock:/var/run/docker.sock
                    -v /usr/bin/docker:/usr/bin/docker:ro
                    -v /etc/shadow:/etc/shadow:ro
                    -v /etc/passwd:/etc/passwd:ro
                    -v /etc/group:/etc/group:ro
                    -v /etc/hosts:/etc/hosts:ro
                    -v /root/.ansible_vault:/root/.ansible_vault
                    -v /root/.kube/config:/root/.kube/config
                """
            }
        }
        environment {
            IMAGE = "harbor.mb.com/mb-demo/sdk-api"
            BOOTSTRAP_NS = check_env_exist(env.BOOTSTRAP_NS, false)
            registry = "harbor.mb.com"
            registryCredential = "harbor-credentials"
        }

        stages {
            stage("init") {
                steps {
                    echo "###################################### Stage Init ###############################################################"
                    script {
                        currentBuild.displayName = "SDK-API-${env.BUILD_NUMBER}"
                    }
                }
            }

            stage("checkout CI playbooks") {
                steps {
                    echo "###################################### Stage Checkout ###################################################################"
                    sh '''
                      rm -rf sdk-api k8s
                      git clone ssh://git@gitlab.mb.com:2200/mercedes/sdk-api.git
                      git clone ssh://git@gitlab.mb.com:2200/mercedes/sdk-api.git -b k8s k8s
                    '''
                }
            }
            stage("Build Image") {
                steps {
                    echo "###################################### Stage Build ############################################################"
                    sh """
                        cd sdk-api
                        docker build . -t "${IMAGE}":"${BUILD_NUMBER}"
                    """
                }
            }
            stage("Local Test") {
                steps {
                    echo "###################################### Stage Test ######################################################################"
                    sh '''
                       docker run -d -p 81:80 --name sdk-api-ci "${IMAGE}":${BUILD_NUMBER} 
                       sleep 5;
                    '''
                    script {
                      def response = httpRequest 'http://localhost:81/index'
                      echo "Status: ${response.status}"
                    }
                    
                }
            }
            stage("Push Image to Registry") {
                steps {
                    echo "###################################### Stage Push ######################################################################"
                    sh '''
                      docker push "${IMAGE}":${BUILD_NUMBER}
                    '''
                    }
            }
            stage("approve release") {
                steps {
                    echo "###################################### Approve deployment to K8S ? ######################################################################"
                    input('Approve deployment to K8S?')
                    }
            }
            stage("bootstrap k8s namespace") {
                steps {
                    script {
                        if (env.BOOTSTRAP_NS.toBoolean()) {
                            echo "###################################### Bootstrap K8S Namespace ####################################################"
                            sh '''
                              ls -la
                              pwd
                              whoami
                              env
                              cd k8s/
                              ansible-vault decrypt --vault-password-file=/root/.ansible_vault registry-secret.yaml tlsSecret.yaml
                              kubectl create ns $NAMESPACE
                              kubectl -n $NAMESPACE create -f limitRange.yaml
                              kubectl -n $NAMESPACE create -f registry-secret.yaml
                              kubectl -n $NAMESPACE create -f tlsSecret.yaml
                              kubectl -n $NAMESPACE create -f deployment.yaml
                              kubectl -n $NAMESPACE create -f service.yaml
                              kubectl -n $NAMESPACE create -f ingress.yaml
                              kubectl -n $NAMESPACE set image deployments/mb-sdk mb-sdk=harbor.mb.com/mb-demo/sdk-api:"${BUILD_NUMBER}"
                            '''
                        } else {
                            echo "###################################### Stage Bootstrap K8S Namespace Ignored ############################################"
                            echo "###################################### Proceed to Upgrade ###############################################################"
                        }
                    }
                }
            }
            stage("Upgrade App K8S") {
                steps {
                  script {
                    if (env.BOOTSTRAP_NS.toBoolean()) {                      
                      echo "######################################### Skipped cause BOOTSTRAP_NS=true ########################################################"
                    
                    } else {
                      echo "###################################### Upgrade deployment ######################################################################"
                      sh '''
                        kubectl -n $NAMESPACE set image deployments/mb-sdk mb-sdk=harbor.mb.com/mb-demo/sdk-api:"${BUILD_NUMBER}"
                      '''
                    }
                  }
                }
            }
        }
        post {
            always {
                echo "###################################### Stage Clean ##################################################"
                sh "docker rm -f sdk-api-ci"
            }
        }
    }
}

def check_env_exist(VAR, VAL) {
    return (VAR) ? VAR : VAL
}
