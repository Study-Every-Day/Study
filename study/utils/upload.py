# -*- encoding: utf-8 -*-
# here put the import lib
from qiniu import Auth, put_file, etag
from .logger import setup_logger

logger = setup_logger(name=__name__)


def upload_image(
        access_key,
        secret_key,
        bucket_name,
        local_file_path,
        remote_file_name):
    logger.info("正在上传登陆二维码至云端")
    q = Auth(access_key, secret_key)
    token = q.upload_token(bucket_name, remote_file_name, 3600)
    ret, info = put_file(token, remote_file_name, local_file_path)
    logger.info(f"上传结果：{info}")
    assert ret['key'] == remote_file_name
    assert ret['hash'] == etag(local_file_path)
    return ret, info
