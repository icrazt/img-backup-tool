# utils.py
import os
from urllib.parse import urlparse
from dotenv import load_dotenv

# 获取当前文件所在目录的绝对路径
current_dir = os.path.dirname(os.path.abspath(__file__))
# 拼接 .env 文件的绝对路径
env_path = os.path.join(current_dir, '.env')

# 加载指定路径的 .env 文件
load_dotenv(dotenv_path=env_path)

def get_smms_api_token():
    return os.getenv("SMMS_API_TOKEN")

def get_r2_endpoint_url():
    return os.getenv("R2_ENDPOINT_URL")

def get_r2_access_key():
    return os.getenv("R2_ACCESS_KEY")

def get_r2_secret_key():
    return os.getenv("R2_SECRET_KEY")

def get_r2_bucket_name():
    return os.getenv("R2_BUCKET_NAME")

def parse_directory_and_filename(smms_path: str, fallback_url: str):
    """
    尝试从 SM.MS 返回的 'path' 字段解析目录和文件名。
    e.g. path = "/2024/12/11/example.webp"
        则目录为 "2024/12/11", 文件名为 "example.webp"
    如果 path 字段缺失或为空，可 fallback 到 url 解析。
    """
    # SM.MS 的 path 可能是 "/2024/12/11/example.webp"
    if smms_path and smms_path.startswith("/"):
        smms_path = smms_path.lstrip("/")
        path_parts = smms_path.split("/")
        filename = path_parts[-1]
        directory = "/".join(path_parts[:-1])
        return directory, filename
    else:
        # 如果 path 无效或没返回，则从 url 尝试解析
        parsed = urlparse(fallback_url)
        # e.g. parsed.path = "/2024/12/11/example.webp"
        path_str = parsed.path.lstrip("/")
        path_parts = path_str.split("/")
        filename = path_parts[-1]
        directory = "/".join(path_parts[:-1])
        return directory, filename