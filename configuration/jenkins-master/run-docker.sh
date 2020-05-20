docker run -it -p 8080:8080 -p 50000:50000 \
    --detach \
    -v /var/jenkins_home:/var/jenkins_home \
    -v /etc/hosts:/etc/hosts \
    -v /etc/ssl/certs/ca-bundle.crt:/usr/local/share/ca-certificates/ca-bundle.crt \
    --restart unless-stopped \
    --name jenkins-mb \
    harbor.mb.com/mb-demo/jenkins/jenkins:v01
