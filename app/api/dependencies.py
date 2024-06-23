from fastapi import Request, Depends
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.control.user import get_user_by_username
from app.schemas.usr import UserBase
from utils.exceptions import AuthException
from utils.utils import security, verify_token


async def get_db(request: Request):
    """
    get database session
    :param request: Request object
    :return: database session
    """
    return request.state.db


async def get_user(authorization: HTTPAuthorizationCredentials = Depends(security), db: AsyncSession = Depends(get_db)):
    """
    get user
    :param authorization: HTTPAuthorizationCredentials
    :param db: session instance
    :return: User instance
    """
    payload = await verify_token(authorization.credentials)
    username = payload.get("user")
    user = await get_user_by_username(db, username)
    return UserBase(**await user.to_dict())

