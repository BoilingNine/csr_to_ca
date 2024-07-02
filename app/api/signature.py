import os
import zipstream
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from fastapi import APIRouter, UploadFile, File, Cookie
from starlette.responses import StreamingResponse

router = APIRouter(
    prefix="/signature/v1",
    tags=["代码签名"]
)
# 签名文件保存目录
SIGNATURE_FOLDER = "signature"
# 代码文件保存目录
CODE_FOLDER = "code_path"


# 定义生成ZIP文件流的生成器
def iter_file(z):
    for chunk in z:
        yield chunk


@router.post("/signature", summary="代码签名")
async def csr_to_ca(server_file_name: str = Cookie(..., description="生成的证书名称"),
                    code_file: UploadFile = File(..., description="要签名的代码文件")):
    server_signature_name = f"{server_file_name}.sig"
    server_code_name = f"{server_file_name}.{code_file.filename.split(".")[-1]}"
    code_to_sign = await code_file.read()
    # 从 CA 私钥文件加载私钥
    # TODO 应该是用户上传私钥签名代码，然后用证书中的公钥去验证代码，目前用ca的私钥去签名代码与证书中的公钥对不起来导致签名验证不通过。
    with open("ca_private_key.pem", "rb") as f:
        ca_private_key = serialization.load_pem_private_key(f.read(), password=None, backend=default_backend())
    ca_private_key.public_key()
    # 代码签名
    signature = ca_private_key.sign(
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

# if __name__ == '__main__':
#     # 读取签名
#     with open("code_signature.sig", "rb") as f:
#         signature_file = f.read()
#
#     # 读取待签名的代码
#     with open("code_to_sign.py", "rb") as f:
#         code_to_verify = f.read()
#
#     # 从证书中提取公钥
#     cert = x509.load_pem_x509_certificate(cert_pem)
#     public_key = cert.public_key()
#     try:
#         public_key.verify(
#             signature_file,
#             code_to_verify,
#             padding.PSS(
#                 mgf=padding.MGF1(hashes.SHA256()),
#                 salt_length=padding.PSS.MAX_LENGTH
#             ),
#             hashes.SHA256()
#         )
#         print("签名验证成功，代码完整且来自可信来源。")
#     except Exception as e:
#         print("签名验证失败，代码可能被篡改或不来自可信来源。", e)
