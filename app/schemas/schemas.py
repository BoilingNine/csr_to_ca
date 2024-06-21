from pydantic import BaseModel, Field
from fastapi import status


class BaseRsp(BaseModel):
    code: int = Field(status.HTTP_200_OK, title="response code", description="response code")
    msg: str = Field("", title="return information", description="return information")
    data: dict = Field({}, title="response code data", description="response code data")
