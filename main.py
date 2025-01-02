import os
import sys
import argparse
import requests
from smms import get_smms_upload_history
from r2 import check_r2_object_exists, upload_to_r2
from local import save_image_to_local, ensure_local_directory
from utils import parse_directory_and_filename
import subprocess

def backup_smms_to_r2():
    """
    1. sm.ms 备份至 r2 储存
    """
    page = 1
    total_count = 0

    while True:
        smms_list = get_smms_upload_history(page=page)
        if not smms_list:
            break  # 没有更多数据，退出循环

        for item in smms_list:
            # SM.MS 返回的字段通常包含 url / path / filename 等
            image_url = item.get("url")
            image_path = item.get("path", "")  # "/2024/12/11/example.webp"

            # 解析目录+文件名
            directory, filename = parse_directory_and_filename(image_path, fallback_url=image_url)
            r2_key = f"sa/{directory}/{filename}" if directory else f"sa/{filename}"  # 注意这里的路径调整 e.g. "sa/2024/12/11/example.webp"

            # 检查 R2 是否已有同名文件
            if check_r2_object_exists(r2_key):
                print(f"[跳过] R2 已存在: {r2_key}")
                continue

            # 下载原图
            try:
                resp = requests.get(image_url, timeout=15)
                resp.raise_for_status()
                file_content = resp.content
                content_type = resp.headers.get("Content-Type", "application/octet-stream")

                # 上传到 R2
                upload_to_r2(file_content, r2_key, content_type)
                total_count += 1

            except Exception as e:
                print(f"[错误] 下载或上传失败: {image_url}, 错误: {e}")

        page += 1

    print(f"=== 同步完成，上传了 {total_count} 张图片到 R2 ===")


def backup_smms_to_local():
    """
    2. sm.ms 备份至本地储存
    """
    page = 1
    total_count = 0

    while True:
        smms_list = get_smms_upload_history(page=page)
        if not smms_list:
            break

        for item in smms_list:
            image_url = item.get("url")
            image_path = item.get("path", "")

            directory, filename = parse_directory_and_filename(image_path, fallback_url=image_url)
            # 构造本地保存路径，例如: "./backup_images/sa/2024/12/11/example.webp"
            local_file_path = os.path.join("./backup_images", "sa", directory, filename) if directory else os.path.join(
                "./backup_images", "sa", filename)

            if os.path.exists(local_file_path):
                print(f"[跳过] 本地已存在: {local_file_path}")
                continue

            # 只有当文件不存在时才创建目录并下载
            os.makedirs(os.path.dirname(local_file_path), exist_ok=True)
            try:
                resp = requests.get(image_url, timeout=15)
                resp.raise_for_status()
                # save_image_to_local(resp.content, local_dir, filename)
                # 修正后的保存文件：
                with open(local_file_path, "wb") as f:
                    f.write(resp.content)
                print(f"[下载成功] 已保存到: {local_file_path}")
                total_count += 1
            except Exception as e:
                print(f"[错误] 下载或保存失败: {image_url}, 错误: {e}")

        page += 1

    print(f"=== 备份完成，共下载了 {total_count} 张图片到本地 ===")

def backup_local_to_r2():
    """
    3. 本地储存备份上传至 R2
    直接使用 rclone 命令
    """
    try:
        # 检查 rclone 是否已配置
        subprocess.run(["rclone", "version"], check=True, capture_output=True)
    except FileNotFoundError:
        print("错误: rclone 未找到，请先安装并配置 rclone。")
        return
    except subprocess.CalledProcessError as e:
        print(f"rclone 配置检查失败: {e.stderr.decode()}")
        return

    try:
        # 使用 rclone copy 命令上传 backup_images 目录到 R2
        result = subprocess.run([
            "rclone",
            "copy",
            "./backup_images",
            "R2:img/",
            "--progress"
        ], check=True, stdout=None, stderr=None)  # 修改这里

        print("=== 本地备份上传到 R2 完成 ===")  # 不需要打印 result.stdout

    except subprocess.CalledProcessError as e:
        print(f"上传到 R2 失败: {e}")  # 简化错误输出

def backup_r2_to_local():
    """
    4. R2 备份至本地储存
    直接使用 rclone 命令
    """
    try:
        # 检查 rclone 是否已配置
        subprocess.run(["rclone", "version"], check=True, capture_output=True)
    except FileNotFoundError:
        print("错误: rclone 未找到，请先安装并配置 rclone。")
        return
    except subprocess.CalledProcessError as e:
        print(f"rclone 配置检查失败: {e.stderr.decode()}")
        return

    try:
        # 使用 rclone copy 命令从 R2 下载到 backup_images
        # 注意：这里 stdout=None, stderr=None
        result = subprocess.run(
            ["rclone", "copy", "R2:img/", "./backup_images", "--progress"],
            check=True,
            stdout=None,  # 默认行为，输出到父进程的标准输出
            stderr=None   # 默认行为，输出到父进程的标准错误
        )
        print(f"=== R2 备份下载到本地完成 ===")
    except subprocess.CalledProcessError as e:
        print(f"从 R2 下载失败: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="图片备份工具")
    parser.add_argument("mode", type=int, choices=[1, 2, 3, 4], nargs='?',
                        help="备份模式：1 (SM.MS -> R2), 2 (SM.MS -> 本地), 3 (本地 -> R2), 4 (R2 -> 本地)")

    args = parser.parse_args()

    if args.mode is None:
        # 没有传入参数，进入交互模式
        print("请选择备份模式：")
        print("1. sm.ms 备份至 R2")
        print("2. sm.ms 备份至本地")
        print("3. 本地备份上传至 R2")
        print("4. R2 备份至本地")

        choice = input("请输入数字选择：")
        try:
            mode = int(choice)
        except ValueError:
            print("无效的输入，请输入数字 1-4")
            sys.exit(1)
    else:
        # 传入了参数，直接执行
        mode = args.mode

    if mode == 1:
        backup_smms_to_r2()
    elif mode == 2:
        backup_smms_to_local()
    elif mode == 3:
        backup_local_to_r2()
    elif mode == 4:
        backup_r2_to_local()
    else:
        print("无效的模式选择。")