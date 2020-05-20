export GITLAB_HOME=/srv
docker run --detach \
  --hostname gitlab.mb.com \
  --publish 8443:8443 --publish 2200:22 \
  --name gitlab-mb \
  --restart always \
  --volume /etc/hosts:/etc/hosts \
  --volume $GITLAB_HOME/gitlab/config:/etc/gitlab \
  --volume $GITLAB_HOME/gitlab/logs:/var/log/gitlab \
  --volume $GITLAB_HOME/gitlab/data:/var/opt/gitlab \
  gitlab/gitlab-ce

