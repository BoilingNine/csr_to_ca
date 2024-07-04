from typing import Optional

from pydantic import BaseModel, Field
from fastapi import status


class BaseRsp(BaseModel):
    code: int = Field(status.HTTP_200_OK, title="返回码", description="返回码")
    msg: str = Field("", description="返回信息")
    data: Optional[dict] = Field(None, description="响应数据")
