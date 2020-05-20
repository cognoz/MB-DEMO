#run with '-p 80:80' port forwarding
FROM tiangolo/uwsgi-nginx-flask:python3.6-alpine3.7
RUN apk update \
  && apk add make automake gcc g++ subversion python3-dev
COPY ./app /app
RUN pip install --upgrade pip
RUN pip install -r /app/requirements.txt
