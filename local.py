import os

LOCAL_BACKUP_ROOT = "./backup_images"

def ensure_local_directory(directory: str):
    """
    确保本地目录存在，如不存在则创建。
    """
    if not directory:
        return  # 空目录直接返回
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)

def save_image_to_local(file_content: bytes, directory: str, filename: str):
    """
    保存图片到本地
    """
    local_dir = os.path.join(LOCAL_BACKUP_ROOT, directory) if directory else LOCAL_BACKUP_ROOT
    ensure_local_directory(local_dir)
    local_file_path = os.path.join(local_dir, filename)

    with open(local_file_path, "wb") as f:
        f.write(file_content)

    print(f"[下载成功] 已保存到: {local_file_path}")