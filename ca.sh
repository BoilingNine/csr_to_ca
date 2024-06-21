#!/usr/bin/env bash

# 添加环境变量
export DEBUG=False



PROJECT_DIR="/data/projects/csr_to_ca"
cd $PROJECT_DIR || exit

GUNICORN_PID=log/gunicorn.pid

eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"
pyenv activate pms_admin



result() {
  if [ "$1" -ne 0 ]; then
    echo '  failed'
    exit 0
  else
    sleep 3
    echo "  succeed"
  fi
}

start() {
  echo 'starting gunicorn server for pms'
  nohup gunicorn -k uvicorn.workers.UvicornWorker > log/nohup.log 2>&1 &
  result $?
}

stop() {
  echo 'stopping gunicorn server for pms'
  PID=$(cat $GUNICORN_PID)
  kill -TERM -- $((PID))
  result $?
}

restart() {
  echo 'restarting gunicorn server for pms'
  PID=$(cat $GUNICORN_PID)
  kill -HUP $((PID))
  result $?
}

if [[ $1 == 'start' ]]; then
  start
elif [[ $1 == 'stop' ]]; then
  stop
elif [[ $1 == 'restart' ]]; then
  restart
else
  echo "Usage: ./ca.sh start|stoop|restart"
fi