## Harbor installation and configuration  
### Install
Configure ssh
```bash
ssh-keygen # enter/enter
cat /root/.ssh/id_rsa.pub >> /root/.ssh/authorized_keys
```

Configure hostname/ hosts file 
```bash
hostname mb-harbor 
echo "mb-harbor" > /etc/hostname
echo "89.208.230.154 gitlab.mb.com harbor.mb.com" >> /etc/hosts
echo "89.208.231.35 jenkins.mb.com" >> /etc/hosts
```

Update all packages on machine
```bash
yum -y install epel-release
yum -y update
```

Install docker on machine
```bash
curl -fsSL https://get.docker.com/ | sh
systemctl start docker
systemctl enable docker
```

### Harbor configuration
Get Harbor release
```bash
cd /opt
wget https://github.com/goharbor/harbor/releases/download/v2.0.0/harbor-online-installer-v2.0.0.tgz
tar -xf harbor-online-installer-v2.0.0.tgz
```

Copy configuration
```bash
cp $THISREPO/configuration/harbor/confs/harbor.yml /opt/harbor/ #confirm
```

### TLS
Generate https certificates
```bash
mkdir -p /etc/harbor/certs/
cd /etc/harbor/certs/
cp /etc/pki/tls/openssl.cnf ./
vim openssl.cnf ##add extension and SAN name 
openssl genrsa -out rootCA.key 4096
openssl req -x509 -new -nodes -key rootCA.key -sha256 -days 1024 -out rootCA.crt
openssl genrsa -out harbor.mb.com.key 2048
openssl req -new -sha256 -key harbor.mb.com.key -subj "/C=RU/ST=MS/O=mercedes-benz, LTD./CN=harbor.mb.com" -reqexts v3_req -config ./openssl.cnf -out harbor.mb.com.csr
openssl x509 -req -days 365 -in harbor.mb.com.csr -CA rootCA.crt -CAkey rootCA.key -CAcreateserial -CAserial serial_numbers -out harbor.mb.com.crt -extensions v3_req -extfile ./openssl.cnf
```
Add rootCA.crt to trusted CA:
```bash
cp RootCA.crt /etc/pki/ca-trust/source/anchors/
update-ca-trust extract
```
### Run installation
Review configuration, start installation
```bash
vi /opt/harbor/harbor.yml
cd /opt/harbor/
./install.sh --with-notary --with-clair --with-chartmuseum
```
wait for docker containers startup

### Verification
- Copy rootCA.crt from /etc/harbor/certs/ to your local machine
- Add it to your trusted root CA vault with appropriate method for your OS:
- Add line 
89.208.230.154 gitlab.mb.com harbor.mb.com
to your /etc/hosts file
- Now you should be able access harbor UI via browser, via address
*https://harbor.mb.com*
