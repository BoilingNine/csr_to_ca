import logging
import os

# DEBUG
DEBUG = os.getenv('DEBUG') == 'True'
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

# MYSQL
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '1qaz%40WSX%40BML')
DB_NAME = os.getenv('DB_NAME', 'ca')
DB_HOST = os.getenv('DB_HOST', '127.0.0.1')
DB_PORT = os.getenv('DB_PORT', '13306')

# for jwt token
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'afccddcdd9bd42d6e1d8b6b698e7cb11488c6885463c0a917353af31e45c53fc')
JWT_ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')
JWT_EXPIRATION = eval(os.getenv('JWT_EXPIRATION', '60 * 60 * 24')) or 60 * 60 * 24

DING_TALK_WEBHOOK_URL = os.getenv('DING_TALK_WEBHOOK_URL',
                                  f'https://oapi.dingtalk.com/robot/send?'
                                  f'access_token=b3a46878c85690129bce01c6631f5e9a1f82541dbe38434dafca084ab7c7cc05')
DINGTALK_WEBHOOK_HEADERS = {
    'Content-Type': 'application/json',
    'charset': 'utf-8',
}

# MINIO
MINIO_ENDPOINT = os.getenv('MINIO_ENDPOINT', '127.0.0.1:9000')
MINIO_ACCESS_KEY = os.getenv('MINIO_ACCESS_KEY', 'vBemlNtBC6dQxN64jIYD')
MINIO_SECRET_KEY = os.getenv('MINIO_SECRET_KEY', 'p138PtZckI0sWQZoGctpzbFlydaNNYzAUGWMZCZI')
MINIO_BUCKET = os.getenv('MINIO_BUCKET', 'pms-admin')
