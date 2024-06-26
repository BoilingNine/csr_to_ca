import multiprocessing as mp
import os

import settings

if not os.path.exists(settings.LOG_PATH):
    os.makedirs(settings.LOG_PATH)

bind = settings.WEB_SERVER
workers = eval(os.getenv('WORKERS', '0')) or mp.cpu_count() * 2 + 1
wsgi_app = 'main:app'
reload = False
accesslog = 'log/gunicorn-access.log'
errorlog = 'log/gunicorn-error.log'
loglevel = settings.LOG_LEVEL_NAME.lower()
timeout = 120
daemon = False
pidfile = 'log/gunicorn.pid'
user = os.getenv('GUNICORN_USER', 'root')
group = os.getenv('GUNICORN_USER', 'root')
