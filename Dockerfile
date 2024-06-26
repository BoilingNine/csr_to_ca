FROM python:3.12-slim

LABEL version=0.0.1

WORKDIR /var/app
COPY ./ /var/app/

RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

CMD bash docker-start.sh