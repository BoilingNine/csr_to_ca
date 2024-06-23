import io

from fastapi import APIRouter, Depends
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

from app.api.dependencies import get_user
from app.schemas.csr_cchemas import RSARsp
from app.schemas.usr import UserBase
from settings import MINIO_BUCKET
from utils.minio_client import minio

router = APIRouter(
    prefix="/casbin/v1",
    tags=["rsa密匙对"]
)


@router.get('/rsa', summary="生成密匙对", response_model=RSARsp)
async def api_gen_rsa(user: UserBase = Depends(get_user),):
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
    minio.upload_file("rsa/private_key/private_key.pem", io.BytesIO(private_key_pem), len(private_key_pem),
                      bucket=MINIO_BUCKET)
    minio.upload_file("rsa/public_key/public_key.pem", io.BytesIO(public_key_pem), len(public_key_pem),
                      bucket=MINIO_BUCKET)
    private_key_path = minio.get_download_url(object_name="private_key.pem", bucket=MINIO_BUCKET)
    public_key_path = minio.get_download_url(object_name="public_key.pem", bucket=MINIO_BUCKET)

    return RSARsp(data={"private_key": private_key_path, "public_key": public_key_path})
