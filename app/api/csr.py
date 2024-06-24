import io
import uuid

from cryptography import x509
from cryptography.hazmat._oid import NameOID
from fastapi import APIRouter, Depends
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization, hashes
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_user, get_db
from app.control.csr import add_csr
from app.models.csr import CSR
from app.schemas.csr_cchemas import RSARsp, CSRReq, CSRRsp
from app.schemas.usr import UserBase
from settings import MINIO_BUCKET
from utils.minio_client import minio

router = APIRouter(
    prefix="/casbin/v1",
    tags=["rsa密匙对"]
)


@router.get('/rsa', summary="获取密匙对", response_model=RSARsp)
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


@router.post('/csr', summary="生成csr", response_model=CSRRsp)
async def api_gen_rsa(csr: CSRReq, user: UserBase = Depends(get_user), db: AsyncSession = Depends(get_db)):
    private_key_response = minio.get_object(MINIO_BUCKET, f"rsa/private_key/private_key_{user.id}.pem")
    private_key_data = private_key_response.read()
    private_key = serialization.load_pem_private_key(
        private_key_data,
        password=None,
    )
    # 生成 CSR
    csr = x509.CertificateSigningRequestBuilder().subject_name(x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, csr.COUNTRY_NAME),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, csr.STATE_OR_PROVINCE_NAME),
        x509.NameAttribute(NameOID.LOCALITY_NAME, csr.LOCALITY_NAME),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, csr.ORGANIZATION_NAME),
        x509.NameAttribute(NameOID.COMMON_NAME, csr.COMMON_NAME),
    ])).add_extension(
        x509.SubjectAlternativeName([
            x509.DNSName(csr.DNSName),
            x509.DNSName(f"www.{csr.DNSName}"),
        ]),
        critical=False,
    ).sign(private_key, hashes.SHA256())
    csr_pem = csr.public_bytes(serialization.Encoding.PEM)
    file_name = f"{uuid.uuid4()}.pem"
    minio.upload_file(f"csr/{user.id}/{file_name}", io.BytesIO(csr_pem),
                      len(csr_pem),
                      bucket=MINIO_BUCKET)
    csr_path = minio.get_download_url(object_name=f"csr/{user.id}/{file_name}",
                                      bucket=MINIO_BUCKET)
    await add_csr(db, CSR(file_name=file_name, user_id=user.id))
    return CSRRsp(data={"csr_download": csr_path})
