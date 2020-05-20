FROM jenkins/jenkins
ADD ca-bundle.crt /usr/local/share/ca-certificates/
USER root
RUN chmod 644 /usr/local/share/ca-certificates/ca-bundle.crt && update-ca-certificates
