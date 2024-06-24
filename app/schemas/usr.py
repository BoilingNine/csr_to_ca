from pydantic import BaseModel, Field, constr

from app.schemas.schemas import BaseRsp
from utils.constants import USER_NAME_MIN, USER_NAME_MAX, PASSWORD_MIN, PASSWORD_MAX, USER_NICKNAME_MIN, \
    USER_NICKNAME_MAX


class TokenBase(BaseModel):
    token: str = Field(..., title='token', description='bearer token')


class TokenRsp(BaseRsp):
    data: TokenBase = Field(..., title="Token信息", description="Token信息")


class UserBase(BaseModel):
    id: int = Field(..., title="ID", description="用户ID")
    username: constr(strip_whitespace=True,
                     min_length=USER_NAME_MIN,
                     max_length=USER_NAME_MAX) = Field(..., title="账号", description="账号")
    nickname: constr(strip_whitespace=True,
                     min_length=USER_NICKNAME_MIN,
                     max_length=USER_NICKNAME_MAX) = Field(..., title="用户昵称", description="用户昵称")
    rsa: bool = Field(..., title="是否生成密钥对", description="是否生成密钥对")

    class Config:
        from_attributes = True


class UserCreateReq(BaseModel):
    username: constr(strip_whitespace=True,
                     min_length=USER_NAME_MIN,
                     max_length=USER_NAME_MAX) = Field(..., title="用户名", description="用户名")
    password: str = Field(..., min_length=PASSWORD_MIN, max_length=PASSWORD_MAX, title="密码", description="密码")


class UserCreateRsp(BaseRsp):
    pass
