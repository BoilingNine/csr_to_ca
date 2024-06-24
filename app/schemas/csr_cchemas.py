from pydantic import BaseModel, Field

from app.schemas.schemas import BaseRsp


class RSADownload(BaseModel):
    public_key_download: str = Field(..., description="公钥下载地址")
    private_key_download: str = Field(..., description="私钥下载地址")


class RSARsp(BaseRsp):
    data: RSADownload = Field({}, description="密匙对下载地址")


class CSRReq(BaseModel):
    COUNTRY_NAME: str = Field(..., description="国家")
    STATE_OR_PROVINCE_NAME: str = Field(..., description="洲或省")
    LOCALITY_NAME: str = Field(..., description="市")
    ORGANIZATION_NAME: str = Field(..., description="组织名称")
    COMMON_NAME: str = Field(..., description="公共名称")
    DNSName: str = Field(..., description="主题备用名称扩展")


class CSRDownload(BaseModel):
    csr_download: str = Field(..., description="CSR下载地址")


class CSRRsp(BaseRsp):
    data: CSRDownload = Field({}, description="CSR下载地址")
