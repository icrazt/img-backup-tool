# 图片备份工具

本项目是一个自动化图片备份工具，旨在提供多重备份策略，保障图片数据的安全性和可靠性。目前支持将图片从 [SM.MS 图床](https://sm.ms/) 备份到 [Cloudflare R2 对象存储](https://www.cloudflare.com/products/r2/) 以及本地存储。同时，也支持使用 `rclone` 在本地存储和 R2 之间进行双向同步。

## 功能特性

*   **SM.MS 备份至 R2**:  从 SM.MS 获取上传历史，并将图片备份到 R2 存储桶，保持与 SM.MS 相同的目录结构，便于未来切换图床。
*   **SM.MS 备份至本地**: 将 SM.MS 上的图片下载到本地存储，按照日期进行归档，提供离线备份。
*   **本地备份上传至 R2**: 利用 `rclone` 工具将本地备份的图片上传到 R2，实现多重备份。
*   **R2 备份至本地**: 使用 `rclone` 将 R2 上的图片下载到本地，提供额外的数据冗余。
*   **环境变量配置**: 敏感信息（如 API 密钥、存储桶配置等）通过 `.env` 文件进行配置，避免直接编码在代码中。

## 项目结构

```
image_backup_tool/
├── main.py          # 主程序入口
├── smms.py         # SM.MS 相关操作
├── r2.py           # R2 相关操作
├── local.py        # 本地文件操作
├── utils.py        # 通用工具函数
├── requirements.txt # 依赖包
└── .env.example    # 环境变量配置示例 (需复制为 .env 并填写实际配置)
```

## 环境与依赖

为了隔离项目依赖，建议创建一个虚拟环境，使用 venv (Python 3.3+ 内置)

```bash
# 创建虚拟环境 (在项目根目录下执行)
python3 -m venv .venv

# 激活虚拟环境
# Linux/macOS
source .venv/bin/activate
# Windows
.venv\Scripts\activate
```

使用以下命令安装 Python 依赖：

```bash
pip install -r requirements.txt
```

**`rclone` 安装和配置:**

本项目使用 `rclone` 进行本地和 R2 之间的同步，请确保已安装并配置好 `rclone`。

1. **安装**: 请参考 [rclone 官方文档](https://rclone.org/install/) 进行安装。

2. **配置**: 安装完成后，运行 `rclone config` 并按照提示进行配置。你需要创建一个名为 `R2` 的远端 (remote)，并配置好对应的 Access Key ID, Secret Access Key, 以及 Endpoint URL。

    配置完成后，你可以使用 `rclone lsd R2:` 命令来列出你的 R2 存储桶，以验证配置是否正确。

## 配置

1. **环境变量**:

    复制 `.env.example` 文件为 `.env`，并根据实际情况填写配置信息：

    ```
    SMMS_API_TOKEN="your_smms_api_token"  # 替换为你的 SM.MS API Token
    R2_ENDPOINT_URL="your_r2_endpoint_url" # 替换为你的 R2 Endpoint URL
    R2_ACCESS_KEY="your_r2_access_key"   # 替换为你的 R2 Access Key ID
    R2_SECRET_KEY="your_r2_secret_key"   # 替换为你的 R2 Secret Access Key
    R2_BUCKET_NAME="img"                 # R2 存储桶名称，根据你的实际情况修改
    ```

    **重要提示**: `.env` 文件包含敏感信息，请勿将其提交到公共代码仓库。

2. **本地备份目录**:

    默认的本地备份根目录为 `./backup_images`。你可以在 `local.py` 文件中修改 `LOCAL_BACKUP_ROOT` 变量来自定义备份目录。

## 使用

**运行主程序 `main.py`，根据提示选择备份模式：**

```bash
python main.py
```

**可选的备份模式：**

1. **SM.MS 备份至 R2**:
    *   此模式会将 SM.MS 上的图片备份到 R2 的 `sa/` 目录下。例如，SM.MS 上的图片 `https://cdn.sa.net/2024/09/10/YuKZHz32BWwFbX4.jpg` 将被备份到 R2 的 `sa/2024/09/10/YuKZHz32BWwFbX4.jpg`。
2. **SM.MS 备份至本地**:
    *   此模式会将 SM.MS 上的图片下载到本地的 `./backup_images/sa/` 目录下。例如，SM.MS 上的图片 `https://cdn.sa.net/2024/09/10/YuKZHz32BWwFbX4.jpg` 将被备份到 `./backup_images/sa/2024/09/10/YuKZHz32BWwFbX4.jpg`。
3. **本地备份上传至 R2**:
    *   此模式使用 `rclone copy ./backup_images R2:img/` 命令将 `./backup_images` 目录下的所有文件上传到 R2 存储桶的根目录下，并保持相同的目录结构。
4. **R2 备份至本地**:
    *   此模式使用 `rclone copy R2:img/ ./backup_images` 命令将 R2 存储桶根目录下的所有文件下载到 `./backup_images` 目录下，并保持相同的目录结构。

**注意**: 在执行模式 3 和 4 之前，请确保已正确安装和配置 `rclone`。

## 定时任务

你可以使用 `crontab` (Linux/macOS) 或 `Task Scheduler` (Windows) 来定时运行备份脚本。

例如，在 Linux 下，你可以编辑 `crontab`：

```bash
crontab -e
```

然后添加类似以下的规则（每天凌晨 3 点执行 SM.MS 到 R2 的备份）：

```
0 3 * * * /usr/bin/python3 /path/to/image_backup_tool/main.py <<< "1"
```

请根据你的实际路径和 Python 解释器路径修改上述命令。

## 注意事项

*   **API 限制**: SM.MS 的 API 可能有访问频率限制，大量图片备份时请注意控制请求频率，避免触发限制。
*   **存储空间**: 请确保 R2 和本地存储有足够的空间来存储备份的图片。
*   **网络连接**: 备份过程需要稳定的网络连接，网络中断可能导致备份失败。
*   **安全性**: 请妥善保管好你的 API 密钥和 R2 访问凭证，避免泄露。
*   **测试**: 在正式使用之前，建议先进行小规模的测试，确保备份和恢复流程都能正常工作。

## 免责声明

本项目仅供学习和参考使用，作者不对因使用本项目造成的任何数据丢失或其他损失负责。请根据自身情况谨慎使用，并定期检查备份数据的完整性。

## 贡献

欢迎提出 Issue 或 Pull Request 来帮助改进本项目。

## 许可

本项目基于 [MIT 许可](LICENSE) 发布。
