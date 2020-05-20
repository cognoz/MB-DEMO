## Jenkins Master installation and configuration  
### Install
Configure ssh
```bash
ssh-keygen # enter/enter
cat /root/.ssh/id_rsa.pub >> /root/.ssh/authorized_keys
```
Also copy id\_rsa.pub from gitlab instance to /root/.ssh/authorized\_keys
And update /root/.ssh/authorized\_keys on gitlab instance vice-versa

Configure hostname/ hosts file 
```bash
hostname mb-jenkins-master 
echo "mb-jenkins-master" > /etc/hostname
echo "89.208.230.154 gitlab.mb.com harbor.mb.com" >> /etc/hosts
echo "89.208.231.35 jenkins.mb.com" >> /etc/hosts
```

Update all packages on machine
```bash
yum -y install epel-release
yum -y update
yum -y install nginx # For TLS
```

Install docker on machine
```bash
curl -fsSL https://get.docker.com/ | sh
systemctl start docker
systemctl enable docker
```
### TLS and nginx
Generate https certificates
```bash
mkdir -p /etc/nginx/ssl/
cd /etc/nginx/ssl/
cp /etc/pki/tls/openssl.cnf ./
vim openssl.cnf ##add extension and SAN name
#Copy rootCA.key and rootCA.crt used for gen sertificates from gitlab instance to ./
scp gitlab-mb:/etc/harbor/certs/rootCA* ./
openssl genrsa -out jenkins.mb.com.key 2048
openssl req -new -sha256 -key jenkins.mb.com.key -subj "/C=RU/ST=MS/O=mercedes-benz, LTD./CN=jenkins.mb.com" -reqexts v3_req -config ./openssl.cnf -out jenkins.mb.com.csr
openssl x509 -req -days 365 -in jenkins.mb.com.csr -CA rootCA.crt -CAkey rootCA.key -CAcreateserial -CAserial serial_numbers -out jenkins.mb.com.crt -extensions v3_req -extfile ./openssl.cnf
chown -R nginx:nginx /etc/nginx/ssl/ 
cp $THISREPO/configuration/jenkins-master/confs/nginx.conf /etc/nginx/nginx.conf # confirm
```
Add rootCA.crt to trusted CA:
```bash
cp RootCA.crt /etc/pki/ca-trust/source/anchors/
update-ca-trust extract
```

### build Jenkins image with CA bundle

```bash
cp $THISREPO/configuration/jenkins-master/confs/Dockerfile ./
cp /etc/pki/ca-trust/extracted/pem/tls-ca-bundle.pem ca-bundle.crt
docker build -t harbor.mb.com/mb-demo/jenkins/jenkins:v01
docker login harbor.mb.com #use creds from harbor.yml on harbor instance
docker push harbor.mb.com/mb-demo/jenkins/jenkins:v01
```

### Run jenkins master
```bash
./run-docker.sh
```

Check status via `docker logs jenkins-master`.  

### Configure nginx proxy 
```bash
cp $THISREPO/configuration/jenkins-master/confs/nginx.conf /etc/nginx/nginx.conf #Confirm
systemctl restart nginx
```

### Verify jenkins UI
Go to https://jenkins.mb.com
paste admin\_key from /var/jenkins\_home/secrets/admin\_secret
Create user

### Configure plugins
Go to https://jenkins.mb.com/pluginManager/available
Install plugins:
- BlueOcean
- Active Choices
- Conditional BuildStep
- Docker plugin
- EnvInject API Plugin
- GitLab Plugin
- HTTP Request Plugin
- Multijob plugin
- Pipeline
- Workspace Cleanup Plugin

### Configure credentials
Go to https://jenkins.mb.com/credentials/store/system/domain/\_/  
Create credentials for:
- jenkins slave (ssh username with key) - use private key from jenkins-master ( it should be added to jenkins-slave authorized\_keys)
- harbor credentials (username with password) - use credentials from harbor.yml on harbor instance
- gitlab api token, generated previously with gitlab configuration; 

### Confgure Jenkins
Go to https://jenkins.mb.com/configure
- Configure Gitlab section  
Connection url, credentials, etc.., Test it  
- Configure Global Pipeline Libraries  
Where sould be library CI with URL ssh://git@gitlab.mb.com:2200/mercedes/ci.git and gitlab-api token as credentials

### Jenkins Worker
Go to https://jenkins.mb.com/computer/new
Configure new worker - permanent agent, use this node as much as possible, Custom WorkDir path = /var/jenkins\_home, 
launch agents via SSH, paste ip address of Jenkins Worker; Select credentials;

Go to https://jenkins.mb.com/computer/(master)/configure
configure Use = only build jobs with label...  

### Projects  
- Create directories in main menu
https://jenkins.mb.com/view/all/newJob
for example, "Mercedes-Benz"  

- Create in this directory job pipeline 
"Build App" 
- Configure it:
Add string parameter NAMESPACE and boolean BOOTSTRAP\_NS;  
In build triggers enable webhook (dont forget to press Advanced and generate/write down secret token - we will need it in gitlab);  
In pipeline scrpit write  
```bash
@Library('CI') _
AppBuild()
```
It tells Jenkins to use pipeline script from Gitlab repo CI.

- Create second job, for cleaning
"cleanNS"
- Add parameter string NAMESPACE;
- Options similiar to job "Build App", except for build triggers and script
In pipeline script write
```bash
@Library('CI') _
cleanNS()
```
### Webhook integration
After every push / merge events to SDK-API Gitlab will notify job "Build App" in Jenkins.  
Now we need go back to gitlab, project SDK-API
https://gitlab.mb.com:8443/mercedes/sdk-api/hooks  
Here we add new webhook, URL and Secret Token of this webhook you can get from job "Build App", build triggers section
Enable all events; 
Disable ssl verification and add webhook;
Tested it with gitlab;

### Verification
- Push anything in https://gitlab.mb.com/mercedes/sdk-api
- Watch Jenkins job
