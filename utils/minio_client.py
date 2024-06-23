"""
    上传文件到文件存储系统
    Minio为HTTP连接，不考虑断连、重连
"""
from datetime import timedelta as td
from functools import wraps
from io import BufferedReader
from minio import Minio
from minio.error import MinioException
from settings import MINIO_ENDPOINT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY, MINIO_BUCKET
from utils.exceptions import CSRException


def minio_exception(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except MinioException as e:
            raise CSRException(500, f'[MinioClient:{func.__name__}] {e}')

    return wrapper


class MinioClient(Minio):
    def __init__(self, endpoint: str, access_key: str = None,
                 secret_key: str = None):
        super().__init__(endpoint,
                         access_key=access_key,
                         secret_key=secret_key,
                         secure=False,
                         )
        if not self.bucket_exists(MINIO_BUCKET):
            self.make_bucket(MINIO_BUCKET)

    @minio_exception
    def upload_file(self, object_name: str, data: BufferedReader, length: int,
                    bucket: str = MINIO_BUCKET,
                    content_type='application/octet-stream', **kwargs):
        """
        Upload object stream.
        :param object_name: Object name in the bucket.
        :param data: An object having callable read() returning bytes object.
        :param length: Data size
        :param bucket: Bucket name
        :param content_type: Content type of the object.
        """
        self.put_object(bucket, object_name, data, length,
                        content_type=content_type, **kwargs)

    @minio_exception
    def get_file(self, object_name: str):
        """
        Get data of an object.
        :param object_name: Object name in the bucket.
        """
        return self.get_object(MINIO_BUCKET, object_name)

    @minio_exception
    def f_upload_file(self, object_name: str, file_path: str, **kwargs):
        """
        Upload object.
        :param object_name: Object name in the bucket.
        :param file_path: Name of file to upload.
        """
        self.fput_object(MINIO_BUCKET, object_name, file_path, **kwargs)

    @minio_exception
    def get_download_url(self, object_name: str, bucket: str = MINIO_BUCKET, expires: td = td(hours=1)):
        """
        :param object_name: Object name in the bucket.
        :param expires: Expiry in seconds; defaults to 7 days.
        :param bucket: Bucket name
        """
        download_url = self.get_presigned_url('GET', bucket, object_name,
                                              expires=expires)
        return download_url


minio = MinioClient(MINIO_ENDPOINT,
                    access_key=MINIO_ACCESS_KEY,
                    secret_key=MINIO_SECRET_KEY)
