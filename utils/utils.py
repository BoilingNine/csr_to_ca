from datetime import timedelta, UTC, datetime
from typing import Optional

from fastapi.security.utils import get_authorization_scheme_param
from jose import jwt
from passlib.context import CryptContext
from fastapi import status

from app.schemas.usr import UserBase
from settings import JWT_SECRET_KEY, JWT_ALGORITHM
from utils.casbin import get_casbin_e
from utils.exceptions import AuthException
from utils.fastapi.application import CSRHTTPBearer

# 认证相关
security = CSRHTTPBearer()

# 密码散列 pwd_context.hash(password)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def gen_password_hash(password) -> str:
    """
    gen password hash
    :param password: password
    :return: hashed password
    """
    return pwd_context.hash(password)



async def verify_password(plain_password, hashed_password) -> bool:
    """
    Verify password
    :param plain_password: plain password
    :param hashed_password: hashed password
    :return: bool
    """
    return pwd_context.verify(plain_password, hashed_password)


async def gen_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Generate access token
    :param data: user data
    :param expires_delta: expires delta in seconds
    :return: token
    """
    to_encode: dict = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    token = f'Bearer {encoded_jwt}'
    return token

async def verify_token(token: str):
    """
    verify token
    :param token: str
    :return: jwt.decode
    """
    scheme, token = get_authorization_scheme_param(token)
    if scheme.lower() != "bearer":
        raise AuthException(status.HTTP_401_UNAUTHORIZED, msg="登陆状态已失效")
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    except Exception as e:
        raise AuthException(status.HTTP_401_UNAUTHORIZED, msg="登陆状态已失效")
    return payload


async def verify_enforce(user: UserBase, obj: str, act: str) -> bool:
    """
    verify enforce
    :param user: UserBase object
    :param obj: str
    :param act: str
    :return: bool
    """
    e = await get_casbin_e()
    return e.enforce(user.username, obj, act)