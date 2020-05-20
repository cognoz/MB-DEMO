## Jenkins Worker installation and configuration  
### Install
Configure ssh
```bash
ssh-keygen # enter/enter
cat /root/.ssh/id_rsa.pub >> /root/.ssh/authorized_keys
```
Also copy id\_rsa.pub from gitlab and jenskins master instances to /root/.ssh/authorized\_keys
And update /root/.ssh/authorized\_keys on gitlab/jenkins master instance vice-versa

Configure hostname/ hosts file 
```bash
hostname mb-jenkins-worker
echo "mb-jenkins-worker" > /etc/hostname
echo "89.208.230.154 gitlab.mb.com harbor.mb.com" >> /etc/hosts
echo "89.208.231.35 jenkins.mb.com" >> /etc/hosts
```

Update all packages on machine
```bash
yum -y install epel-release wget unzip
yum -y update
```

Install docker on machine
```bash
curl -fsSL https://get.docker.com/ | sh
systemctl start docker
systemctl enable docker
```
Copy rootCA.crt from harbor and add it to trusted CA:
```bash
scp harbor.mb.com:/etc/harbor/certs/rootCA.crt ./
cp RootCA.crt /etc/pki/ca-trust/source/anchors/
update-ca-trust extract
```

### build Jenkins Agent image
In out agent we will need:
binaries:
- kubectl
- terraform
pip packages:
- ansible


```bash
cp $THISREPO/configuration/jenkins-worker/confs/Dockerfile ./
mkdir bin/ ; cd bin/
wget https://storage.googleapis.com/kubernetes-release/release/v1.18.0/bin/linux/amd64/kubectl
chmod +x ./kubectl
wget https://releases.hashicorp.com/terraform/0.12.25/terraform_0.12.25_linux_amd64.zip 
unzip terraform_0.12.25_linux_amd64.zip
chmod +x ./terraform
cd ../
docker build -t harbor.mb.com/mb-demo/jenkins/agent:v01
docker login harbor.mb.com #use creds from harbor.yml on harbor instance
docker push harbor.mb.com/mb-demo/jenkins/agent:v01
```

### Get .kube config for access to K8S cluster
From MCS UI you easily can download config for your kubernetes cluster, e.g
https://mcs.mail.ru/app/en/services/containers/list/ , "Get Kubeconfig for cluster"

scp it to jenkins-worker:
```bash
mkdir /root/.kube/
scp rk-k8s_kubeconfig.yaml jenkins-worker-ip:/root/.kube/
```

### Configure Ansible Vault pass file
Many secrets and credentials in this repo are encrypted with Ansible Vault
On Jenkins worker create file /root/.ansible\_vault with one line 
"1qaz@WSX"
