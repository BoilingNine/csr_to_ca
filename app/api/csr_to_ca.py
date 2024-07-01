import io
import os
import datetime
import random
import uuid

import zipstream
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import padding
from fastapi import APIRouter, UploadFile, File
from cryptography.hazmat.primitives import serialization, hashes
from starlette import status
from starlette.responses import StreamingResponse

from utils.exceptions import CSRException

router = APIRouter(
    prefix="/csr/v1",
    tags=["生成证书"]
)

# CSR 文件保存目录
CSR_UPLOAD_FOLDER = "csrs"
# 生成的证书文件保存目录
CA_GEN_FOLDER = "cas"
# 生成的记录文件保存目录
RECORD_FOLDER = "record"


@router.post("/csr_to_ca", summary="提交csr生成证书")
async def csr_to_ca(file_csr: UploadFile = File(..., description="csr文件")):
    time_now = datetime.datetime.utcnow().strftime('%Y-%m-%d-%H-%M-%S')
    _name = f'{uuid.uuid1()}{random.random()}'
    uuid_name = uuid.uuid5(uuid.NAMESPACE_DNS, _name).hex
    server_file_name = f"{uuid_name}{time_now}.pem"

    # 读取上传的文件内容
    contents = await file_csr.read()

    # 保存上传的 CSR 文件
    if not os.path.exists(CSR_UPLOAD_FOLDER):
        os.makedirs(CSR_UPLOAD_FOLDER)
    csr_file_path = os.path.join(CSR_UPLOAD_FOLDER, server_file_name)
    with open(csr_file_path, "wb") as f:
        f.write(contents)

    # 使用 cryptography 库加载 CSR
    csr = x509.load_pem_x509_csr(contents, default_backend())

    # 检查 CSR 是否有效
    if not csr.is_signature_valid:
        raise CSRException(status.HTTP_403_FORBIDDEN, msg="CSR 签名无效")

    # 从 CSR 中提取信息
    subject = csr.subject
    subject_info = {attr.oid._name: attr.value for attr in subject}

    # 记录csv
    if not os.path.exists(RECORD_FOLDER):
        os.makedirs(RECORD_FOLDER)
    record_file_path = os.path.join(RECORD_FOLDER, "record.csv")
    if not os.path.exists(record_file_path):
        with open(record_file_path, "w", encoding="utf-8") as file:
            file.write("文件名,国家,洲或省,市,组织名称,公共名称,创建时间\n")
    with open(record_file_path, "a", encoding="utf-8") as file:
        file.write(
            f"'{server_file_name}','{subject_info.get("countryName", "")}',"
            f"‘{subject_info.get("stateOrProvinceName", "")}',"
            f"'{subject_info.get("localityName", "")}',"
            f"'{subject_info.get("organizationName", "")}',"
            f"'{subject_info.get("commonName", "")}',"
            f"'{time_now}'\n")

    # 从 CA 私钥文件加载私钥
    with open("ca_private_key.pem", "rb") as f:
        ca_private_key = serialization.load_pem_private_key(f.read(), password=None, backend=default_backend())

    # 从 CA 证书文件加载证书
    with open("ca_certificate.pem", "rb") as f:
        ca_certificate = x509.load_pem_x509_certificate(f.read(), default_backend())

    # 生成并签名证书
    certificate = x509.CertificateBuilder().subject_name(
        csr.subject
    ).issuer_name(
        ca_certificate.subject
    ).public_key(
        csr.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.datetime.utcnow()
    ).not_valid_after(
        datetime.datetime.utcnow() + datetime.timedelta(days=365)
    ).add_extension(
        x509.BasicConstraints(ca=False, path_length=None), critical=True,
    ).sign(ca_private_key, hashes.SHA256())

    # 将证书序列化为 PEM 格式
    cert_pem = certificate.public_bytes(serialization.Encoding.PEM)

    # 保存证书到文件
    if not os.path.exists(CA_GEN_FOLDER):
        os.makedirs(CA_GEN_FOLDER)
    csr_file_path = os.path.join(CA_GEN_FOLDER, server_file_name)
    with open(csr_file_path, "wb") as f:
        f.write(cert_pem)
    # 返回文件相应
    headers = {
        'content-type': 'application/octet-stream',
        'Content-Disposition': f'attachment; filename="{server_file_name}"',
        'Access-Control-Expose-Headers': 'content-disposition'
    }
    bio = io.BytesIO()
    bio.write(cert_pem)
    bio.seek(0)
    response = StreamingResponse(bio, headers=headers)
    response.set_cookie("server_file_name", f"{uuid_name}{time_now}")
    return response
