import logging
import traceback

from loguru import logger

from fastapi import Request, status
from fastapi.responses import JSONResponse

from utils.database import SessionLocal
from utils.ret_code import (CODE_DESC)


class CSRException(Exception):
    """
    Exception raised when an error occurs while processing PMS
    """
    prefix = 'PMS'

    def __init__(self, code: int, msg: str = '', data: any = None, notify: bool = False):
        """
        initialization parameter
        :param code: error code
        :param msg:  error message
        :param data: response data
        :param notify: Notification or not
        """
        super().__init__()
        self.code = code
        self.msg = msg
        self.data = data
        self.notify = notify

    def dict(self):
        """
        dictionary representation of PMSException
        :return: dictionary representation of PMSException
        """
        msg = f"{self.msg or CODE_DESC.get(self.code, '')}"
        return {'code': self.code, 'msg': msg, 'data': self.data}

    @property
    def info(self):
        """
        return info about PMSException
        :return: info about PMSException
        """
        return f'{self.prefix} -- {self.msg or CODE_DESC.get(self.code)}'

    def log(self):
        """
        log message
        :return: None
        """
        if self.code == status.HTTP_500_INTERNAL_SERVER_ERROR:
            logger.error(self.info)
        else:
            logger.debug(self.info)


class AuthException(CSRException):
    """
    Exception raised when Auth request fails
    """
    prefix = "Auth"


async def auth_exception_handler(request, exc: AuthException):
    log_parameters(request, logging.WARNING)
    exc.log()
    return JSONResponse(exc.dict())


def log_parameters(request: Request, level=logging.ERROR):
    """
    log parameters
    :param request: Request instance
    :param level: logging level
    :return: None
    """
    msg = f'{request.query_params or ""}' \
          f'{request.path_params or ""}'
    if msg:
        logger.log(logging.getLevelName(level), msg)


def return_err_msg(code: str, msg: str = ''):
    """
    code to msg
    :param code: error code
    :param msg: error message
    :return: error message
    """
    return f'{msg or CODE_DESC.get(code)}'


async def csr_exception_handler(request: Request, exc: CSRException):
    """
    pms exception handler
    :param request: Request instance
    :param exc: PMSException instance
    :return: JSONResponse
    """
    log_parameters(request, logging.DEBUG)
    exc.log()
    return JSONResponse(exc.dict())


async def http_middleware(request: Request, call_next):
    """
    http middleware
    :param request: FastApi request instance
    :param call_next: Call next function
    :return: JSONResponse
    """
    try:
        request.state.db = SessionLocal()
        return await call_next(request)
    except Exception as e:
        await request.state.db.rollback()
        log_parameters(request)
        error = "".join(traceback.format_exception(e, limit=None, chain=True))
        logger.error(error)
        return JSONResponse({'code': status.HTTP_500_INTERNAL_SERVER_ERROR,
                             'msg': return_err_msg(status.HTTP_500_INTERNAL_SERVER_ERROR)})
    finally:
        await request.state.db.commit()
        await request.state.db.close()


exception_handlers = {
    CSRException: csr_exception_handler,
    AuthException: auth_exception_handler
}
