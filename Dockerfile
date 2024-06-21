FROM python:3.12-slim
#FROM swr.cn-east-3.myhuaweicloud.com/tianjian/itjcloud-knowledge-graph-base:1

# pms_admin version no
LABEL version=0.0.1

WORKDIR /var/app
COPY ./ /var/app/

RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

CMD bash docker-start.sh