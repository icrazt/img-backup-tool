# r2.py
import boto3
from botocore.exceptions import ClientError
from utils import get_r2_endpoint_url, get_r2_access_key, get_r2_secret_key, get_r2_bucket_name

# 初始化 Boto3 S3 Client
s3_client = boto3.client(
    "s3",
    endpoint_url=get_r2_endpoint_url(),  # 使用 utils.py 中的函数
    aws_access_key_id=get_r2_access_key(),  # 使用 utils.py 中的函数
    aws_secret_access_key=get_r2_secret_key()  # 使用 utils.py 中的函数
)

def check_r2_object_exists(key: str) -> bool:
    """
    检查 R2 存储桶中是否存在指定 Key
    """
    try:
        s3_client.head_object(Bucket=get_r2_bucket_name(), Key=key)  # 使用 utils.py 中的函数
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == "404":
            return False
        else:
            raise e

def upload_to_r2(file_content: bytes, key: str, content_type: str = "application/octet-stream"):
    """
    上传文件数据到 R2
    """
    s3_client.put_object(
        Bucket=get_r2_bucket_name(),
        Key=key,
        Body=file_content,
        ContentType=content_type
    )
    print(f"[上传成功] R2 Key: {key}")