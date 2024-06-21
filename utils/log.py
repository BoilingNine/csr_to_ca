import logging
import os
import sys

from loguru import logger

import settings

FORMAT = "patient_managements_system | " \
         "<cyan>{process}</cyan> | " \
         "<level>{level: <8}</level> | " \
         "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | " \
         "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | " \
         "<level>{message}</level>"


class InterceptHandler(logging.Handler):
    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = sys._getframe(6), 6
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(
            depth=depth,
            exception=record.exc_info,
        ).log(level, f'{record.getMessage()}')


def check_level(record):
    return record['level'].no >= settings.LOG_LEVEL


def redirect_log():
    logger.remove()

    # console
    logger.add(sys.stdout,
               enqueue=True,
               level=logging.NOTSET,
               filter=check_level,
               format=FORMAT,
               )
    # debug log
    logger.add(os.path.join(settings.LOG_PATH, 'debug.log'),
               enqueue=True,
               level=logging.DEBUG,
               filter=check_level,
               format=FORMAT,
               rotation=settings.LOG_ROTATION,
               retention=settings.LOG_RETENTION,
               diagnose=settings.LOG_DIAGNOSE,
               )
    # info/warn log
    logger.add(os.path.join(settings.LOG_PATH, 'info.log'),
               enqueue=True,
               level=logging.WARN,
               filter=check_level,
               format=FORMAT,
               rotation=settings.LOG_ROTATION,
               retention=settings.LOG_RETENTION,
               diagnose=settings.LOG_DIAGNOSE,
               )
    # error log
    logger.add(os.path.join(settings.LOG_PATH, 'error.log'),
               enqueue=True,
               level=logging.ERROR,
               filter=check_level,
               format=FORMAT,
               rotation=settings.LOG_ROTATION,
               retention=settings.LOG_RETENTION,
               diagnose=settings.LOG_DIAGNOSE,
               )

    # redirect log
    # logging.basicConfig(handlers=[InterceptHandler()], level=logging.NOTSET)
    for _logger_name in ('uvicorn.access',
                         'uvicorn.error',
                         'fastapi'):
        _logger = logging.getLogger(_logger_name)
        _logger.handlers = [InterceptHandler()]
