from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import status

from app.control.role import get_role_by_role_key
from app.models.casbin_rule import CasbinRule
from app.models.user import User
from utils.constants import COMMON_ROLE_KEY
from utils.exceptions import CSRException
from utils.utils import verify_password, gen_password_hash


async def add_user(db: AsyncSession, user: User) -> User:
    """
    add new user
    :param db:Session instance
    :param user: User instance
    :return: User instance
    """
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def get_user_by_username(db: AsyncSession, username: str):
    """
    get user by username
    :param db: Session instance
    :param username: username
    :return: user instance
    """
    res = await db.execute(select(User).filter_by(username=username))
    return res.scalar()


async def authenticate_user(db: AsyncSession, username: str, password: str):
    """
    Authenticate user
    :param db: session instance
    :param username: username
    :param password: password
    :return: user instance
    """
    user = await get_user_by_username(db, username=username)  # 获取用户信息
    # 用户不存在
    if not user:
        raise CSRException(code=status.HTTP_401_UNAUTHORIZED, msg="用户不存在")
    # 校验密码失败
    if not await verify_password(password, user.hashed_password):
        raise CSRException(code=status.HTTP_401_UNAUTHORIZED, msg="密码错误")
    # 成功返回user
    return user


async def create_user(db: AsyncSession, username: str, password: str):
    """
    create new user
    :param db: Session instance
    :param username: username
    :param password: password
    :param sex: sex
    :param email: email
    :return: None
    """
    role_common = await get_role_by_role_key(db, COMMON_ROLE_KEY)  # 普通用户
    hashed_password = await gen_password_hash(password)
    user = User(username=username, nickname=username, hashed_password=hashed_password)
    casbin_rule = CasbinRule(ptype='g', v0=user.username, v1=role_common.role_key)
    db.add_all([user, casbin_rule])

