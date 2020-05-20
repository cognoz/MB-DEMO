## Gitlab (co-located with Harbor) installation and configuration  
### Install
docker, packages, SSH keys and /etc/hosts are already confgiured after harbor installation; 

### TLS
Generate https certificates
```bash
mkdir -p /srv/gitlab/config/ssl/
cd /srv/gitlab/config/ssl/
cp /etc/pki/tls/openssl.cnf ./
vim openssl.cnf ##add extension and SAN name 
#copy rootCA from harbor installation
cp /etc/harbor/certs/rootCA.crt /etc/harbor/certs/rootCA.key ./
openssl genrsa -out gitlab.mb.com.key 2048
openssl req -new -sha256 -key gitlab.mb.com.key -subj "/C=RU/ST=MS/O=mercedes-benz, LTD./CN=gitlab.mb.com" -reqexts v3_req -config ./openssl.cnf -out gitlab.mb.com.csr
openssl x509 -req -days 365 -in gitlab.mb.com.csr -CA rootCA.crt -CAkey rootCA.key -CAcreateserial -CAserial serial_numbers -out gitlab.mb.com.crt -extensions v3_req -extfile ./openssl.cnf
```

### Post installation configuration  
Copy configuration 
```bash
cp $THISREPO/configuration/gitlab/confs/gitlab.rb /srv/gitlab/config/gitlab.rb #confirm
```
Review configuration
```bash
vim /srv/gitlab/config/gitlab.rb
```
### Installation
Run `./docker-run.sh` script, it will starts gitlab server

Wait for 2-3 minutes (check status via `docker logs gitlab-mb` command)

### Verification
- Now you should be able access harbor UI via browser, via address
*https://gitlab.mb.com:8443*

### Configure gitlab resources
- Create Group, e.g. Mercedes-Benz
- Create User for CI, e.g "Jenkins", impersonate it
- Add to this user ssh key from jenkins-worker and jenkins-master machines
- Create Access Token for this user with all access; Write down secret token - we will need it later in jenkins
- Create Projects in Mercedes-Benz group: "CI","SDK-API"
- Add root and jenkins users as masters to these projects
- Push CI and SDK-API repos from $THISREPO/configuration/gitlab/repos/ to gitlab.mb.com:  

```bash
cd $THISREPO/configuration/gitlab/repos/ci
git init
git remote add origin 
ssh://git@gitlab.mb.com:2200/mercedes/ci.git  
git add -A
git commit -m "Initial"
git push origin master

cd $THISREPO/configuration/gitlab/repos/sdk-api
git remote add origin
ssh://git@gitlab.mb.com:2200/mercedes/sdk-api.git
git add -A
git commit -m "Initial"
git push origin master

cd $THISREPO/configuration/gitlab/repos/k8s
git remote add origin
ssh://git@gitlab.mb.com:2200/mercedes/sdk-api.git
git add -A
git commit -m "Initial"
git push origin k8s
```
That's all for now. Later we will add webhook with information from Jenkins;  
