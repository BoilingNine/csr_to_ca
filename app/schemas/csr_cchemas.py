from pydantic import BaseModel, Field

from app.schemas.schemas import BaseRsp


class RSA(BaseModel):
    public_key: str = Field(..., description="公钥下载地址")
    private_key: str = Field(..., description="私钥下载地址")


class RSARsp(BaseRsp):
    data: RSA = Field({}, description="response code data")
