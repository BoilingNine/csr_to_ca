from typing import List

from pydantic import BaseModel, Field

from app.schemas.schemas import BaseRsp
from utils.constants import EStatus


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


class CSRInfo(BaseModel):
    id: int = Field(..., description="csr_ID")
    file_name: str = Field(..., description="file_name")
    country_name: str = Field(..., description="国家")
    state_or_province_name: str = Field(..., description="洲或省")
    locality_name: str = Field(..., description="市")
    organization_name: str = Field(..., description="组织名称")
    common_name: str = Field(..., description="公共名称")
    status: int = Field(..., description="审核状态，0待审核，1通过，2拒绝")


class CSRListRsp(BaseRsp):
    data: List[CSRInfo] = Field([], description="CSR详情列表")


class PassCSRReq(BaseModel):
    csr_id: int = Field(..., description="csr_id")
    status: EStatus = Field(..., description=f"{EStatus.fmt()}")


class DownloadCertReq(BaseModel):
    csr_id: int = Field(..., description="csr_id")


class CertDownloadUrl(BaseModel):
    cert_download: str = Field(..., description="")


class CertDownloadRsp(BaseRsp):
    data: CertDownloadUrl = Field({}, description="证书下载链接")
