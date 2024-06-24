import io
import uuid
from datetime import datetime, timedelta

from cryptography import x509
from cryptography.hazmat._oid import NameOID
from fastapi import APIRouter, Depends
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization, hashes
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.api.dependencies import get_user, get_db
from app.control.csr import add_csr, get_csr_list_from_db, check_csr_db, get_csr_db
from app.models.csr import CSR
from app.schemas.csr import RSARsp, CSRReq, CSRRsp, CSRListRsp, PassCSRReq, DownloadCertReq, CertDownloadRsp
from app.schemas.schemas import BaseRsp
from app.schemas.usr import UserBase
from settings import MINIO_BUCKET
from utils.constants import EStatus
from utils.exceptions import CSRException
from utils.minio_client import minio
from utils.utils import verify_enforce

router = APIRouter(
    prefix="/csr/v1",
    tags=["rsa密匙对"]
)


@router.get('/rsa', summary="获取密匙对下载链接", response_model=RSARsp)
async def api_gen_rsa(user: UserBase = Depends(get_user)):
    # 如果没生成密钥对
    if not user.rsa:
        # 生成 RSA 私钥
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        # 提取公钥
        public_key = private_key.public_key()
        # 将私钥序列化为 PEM 格式
        private_key_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),  # 无加密
        )
        # 将公钥序列化为 PEM 格式
        public_key_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        # 上传私钥到 MinIO
        minio.upload_file(f"rsa/private_key/private_key_{user.id}.pem", io.BytesIO(private_key_pem),
                          len(private_key_pem),
                          bucket=MINIO_BUCKET)
        minio.upload_file(f"rsa/public_key/public_key_{user.id}.pem", io.BytesIO(public_key_pem), len(public_key_pem),
                          bucket=MINIO_BUCKET)
    private_key_path = minio.get_download_url(object_name=f"rsa/private_key/private_key_{user.id}.pem",
                                              bucket=MINIO_BUCKET)
    public_key_path = minio.get_download_url(object_name=f"rsa/public_key/public_key_{user.id}.pem",
                                             bucket=MINIO_BUCKET)
    return RSARsp(data={"private_key_download": private_key_path, "public_key_download": public_key_path})


@router.post('/csr', summary="生成csr并提交审核，返回下载链接", response_model=CSRRsp)
async def api_gen_csr(req: CSRReq, user: UserBase = Depends(get_user), db: AsyncSession = Depends(get_db)):
    # 从minio获取私钥
    private_key_response = minio.get_object(MINIO_BUCKET, f"rsa/private_key/private_key_{user.id}.pem")
    private_key_data = private_key_response.read()
    private_key = serialization.load_pem_private_key(
        private_key_data,
        password=None,
    )
    # 生成 CSR
    csr = x509.CertificateSigningRequestBuilder().subject_name(x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, req.COUNTRY_NAME),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, req.STATE_OR_PROVINCE_NAME),
        x509.NameAttribute(NameOID.LOCALITY_NAME, req.LOCALITY_NAME),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, req.ORGANIZATION_NAME),
        x509.NameAttribute(NameOID.COMMON_NAME, req.COMMON_NAME),
    ])).add_extension(
        x509.SubjectAlternativeName([
            x509.DNSName(req.DNSName),
            x509.DNSName(f"www.{req.DNSName}"),
        ]),
        critical=False,
    ).sign(private_key, hashes.SHA256())
    csr_pem = csr.public_bytes(serialization.Encoding.PEM)
    # 将csr上传到minio并保存数据库
    file_name = f"{uuid.uuid4()}.pem"
    minio.upload_file(f"csr/{user.id}/{file_name}", io.BytesIO(csr_pem),
                      len(csr_pem),
                      bucket=MINIO_BUCKET)
    csr_path = minio.get_download_url(object_name=f"csr/{user.id}/{file_name}",
                                      bucket=MINIO_BUCKET)
    await add_csr(db, CSR(file_name=file_name, user_id=user.id, country_name=req.COUNTRY_NAME,
                          state_or_province_name=req.STATE_OR_PROVINCE_NAME, locality_name=req.LOCALITY_NAME,
                          organization_name=req.ORGANIZATION_NAME, common_name=req.COMMON_NAME, dns_name=req.DNSName))
    return CSRRsp(data={"csr_download": csr_path})


@router.get('/csr_list', summary="查询生成的csr申请列表", response_model=CSRListRsp)
async def get_csr_list(user: UserBase = Depends(get_user), db: AsyncSession = Depends(get_db)):
    res = await get_csr_list_from_db(db, user)
    data = []
    for i in res:
        info = await i.to_dict()
        data.append(info)
    return CSRListRsp(data=data)


@router.post("/check_csr", summary="审核csr", response_model=BaseRsp)
async def check_csr(req: PassCSRReq, user: UserBase = Depends(get_user), db: AsyncSession = Depends(get_db)):
    if not await verify_enforce(user, 'CSR', 'check'):
        raise CSRException(status.HTTP_403_FORBIDDEN, msg="用户无权限")
    await check_csr_db(db, req.csr_id, req.status)
    if req.status == EStatus.passed:
        # 加载 CSR
        csr = await get_csr_db(db, req.csr_id)
        file_name = csr.file_name
        crs_file = minio.get_object(MINIO_BUCKET, f"csr/{csr.user_id}/{file_name}")
        _crs_file_data = crs_file.read()
        crs_file_data = x509.load_pem_x509_csr(_crs_file_data)
        # 检查 CSR 是否有效
        if not crs_file_data.is_signature_valid:
            raise CSRException(status.HTTP_403_FORBIDDEN, msg="CSR 签名无效")
        # 读取私钥
        private_key_response = minio.get_object(MINIO_BUCKET, f"rsa/private_key/private_key_{csr.user_id}.pem")
        private_key_data = private_key_response.read()
        private_key = serialization.load_pem_private_key(
            private_key_data,
            password=None,
        )
        # 生成自签名证书
        subject = issuer = crs_file_data.subject
        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            crs_file_data.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.utcnow()
        ).not_valid_after(
            # 证书有效期为1年
            datetime.utcnow() + timedelta(days=365)
        ).add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName("mycompany.com"),
                x509.DNSName("www.mycompany.com"),
            ]),
            critical=False,
        ).sign(private_key, hashes.SHA256())
        # 将证书序列化为 PEM 格式
        cert_pem = cert.public_bytes(serialization.Encoding.PEM)
        minio.upload_file(f"cert/{csr.user_id}/{file_name}", io.BytesIO(cert_pem),
                          len(cert_pem),
                          bucket=MINIO_BUCKET)
    return BaseRsp()


@router.post("/download", summary="下载证书", response_model=CertDownloadRsp)
async def check_csr(req: DownloadCertReq, user: UserBase = Depends(get_user), db: AsyncSession = Depends(get_db)):
    csr = await get_csr_db(db, req.csr_id)
    cert_path = minio.get_download_url(object_name=f"cert/{user.id}/{csr.file_name}",
                                       bucket=MINIO_BUCKET)
    return CertDownloadRsp(data={"cert_download": cert_path})
