from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import status

from app.api.dependencies import get_db
from app.control.user import authenticate_user, get_user_by_username, create_user
from app.schemas.schemas import BaseRsp
from app.schemas.usr import UserCreateRsp, UserCreateReq, TokenRsp
from utils.exceptions import CSRException
from utils.utils import gen_access_token

router = APIRouter(
    prefix="/user/v1",
    tags=["用户管理"]
)


@router.post('/register', summary="注册", response_model=BaseRsp)
async def api_gen_rsa(user: UserCreateReq, db: AsyncSession = Depends(get_db)):
    user_db = await get_user_by_username(db, user.username)
    if user_db:
        raise CSRException(status.HTTP_403_FORBIDDEN, msg="用户名重复")
    await create_user(db, user.username, user.password)
    return UserCreateRsp(msg="注册成功")


@router.post('/login', summary="登录", response_model=TokenRsp)
async def api_gen_rsa(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(db, form_data.username, form_data.password)
    access_token = await gen_access_token(data={"user": user.username})
    return TokenRsp(data={"token": access_token})
