import os
import zipstream
from cryptography import x509
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from fastapi import APIRouter, UploadFile, File, Cookie
from fastapi import status
from fastapi.responses import StreamingResponse

from app.schemas.schemas import BaseRsp
from utils.exceptions import CSRException

router = APIRouter(
    prefix="/signature/v1",
    tags=["代码签名"]
)
# 签名文件保存目录
SIGNATURE_FOLDER = "signature"
# 代码文件保存目录
CODE_FOLDER = "code"


# 定义生成ZIP文件流的生成器
def iter_file(z):
    for chunk in z:
        yield chunk


@router.post("/signature", summary="代码签名")
async def signature(server_file_name: str = Cookie("server_file_name", description="生成的证书名称"),
                    code_file: UploadFile = File(..., description="要签名的代码文件"),
                    user_private_key_file: UploadFile = File(..., description="用户私钥")):
    # 生成签名文件和代码文件文件名
    server_signature_name = f"{server_file_name}.sig"
    server_code_name = f"{server_file_name}.{code_file.filename.split(".")[-1]}"
    # 读取待签名的文件
    code_to_sign = await code_file.read()
    # 读取用户私钥
    user_private_key = serialization.load_pem_private_key(await user_private_key_file.read(),
                                                          password=None, backend=default_backend())
    # 代码签名
    signature = user_private_key.sign(
        code_to_sign,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )

    # 保存签名到文件
    if not os.path.exists(SIGNATURE_FOLDER):
        os.makedirs(SIGNATURE_FOLDER)
    signature_file_path = os.path.join(SIGNATURE_FOLDER, server_signature_name)
    with open(signature_file_path, "wb") as f:
        f.write(signature)

    # 保存待签名的代码到文件
    if not os.path.exists(CODE_FOLDER):
        os.makedirs(CODE_FOLDER)
    code_file_path = os.path.join(CODE_FOLDER, server_code_name)
    with open(code_file_path, "wb") as f:
        f.write(code_to_sign)
    # 返回文件，创建一个zip文件流
    z = zipstream.ZipFile(mode='w', compression=zipstream.ZIP_DEFLATED)
    z.write(signature_file_path, arcname=server_signature_name)
    z.write(code_file_path, arcname=server_code_name)
    headers = {"Content-Disposition": f"attachment; filename={server_file_name}.zip",
               'content-type': 'application/octet-stream',
               'Access-Control-Expose-Headers': 'content-disposition'}
    return StreamingResponse(iter_file(z), media_type='application/zip', headers=headers)


@router.post("/verify_signature", summary="验证签名", response_model=BaseRsp)
async def verify_signature(signature_file: UploadFile = File(..., description="签名文件"),
                           cert_file: UploadFile = File(..., description="证书文件"),
                           code_file: UploadFile = File(..., description="代码文件")):
    # 读取签名文件
    signature_file = await signature_file.read()
    # 读取证书文件
    cert_pem = await cert_file.read()
    # 读取签名的代码文件
    code_file = await code_file.read()
    # 从证书中提取公钥
    cert = x509.load_pem_x509_certificate(cert_pem)
    public_key = cert.public_key()
    try:
        public_key.verify(
            signature_file,
            code_file,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
    except InvalidSignature:
        raise CSRException(code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                           msg="签名验证失败，代码可能被篡改或不来自可信来源。")
    return BaseRsp(code=status.HTTP_200_OK, msg="签名验证成功，代码完整且来自可信来源。")
