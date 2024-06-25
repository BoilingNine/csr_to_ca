import logging
import os

# DEBUG
DEBUG = True
ENV_NAME = os.getenv('ENV_NAME', 'DEBUG')
# 默认跨域
CORS_ORIGINS_ADMIN = eval(os.getenv('CORS_ORIGINS_APP', '["*"]'))
CORS_ORIGINS_APP = eval(os.getenv('CORS_ORIGINS_APP', '["*"]'))
# 端口信息
WEB_SERVER = os.getenv('WEB_SERVER', '0.0.0.0:8011')
WEB_HOST, WEB_PORT = WEB_SERVER.split(':')
WEB_PORT = int(WEB_PORT)

# LOG
LOG_PATH = os.getenv('LOG_PATH', 'log')
LOG_LEVEL_NAME = os.getenv('LOG_LEVEL_NAME', 'DEBUG')
LOG_LEVEL = logging.getLevelName(LOG_LEVEL_NAME)
LOG_ROTATION = os.getenv('LOG_ROTATION', '1 month')
LOG_RETENTION = os.getenv('LOG_RETENTION', '1 month')
LOG_DIAGNOSE = bool(os.getenv('LOG_DIAGNOSE'))