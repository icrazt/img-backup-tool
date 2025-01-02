# smms.py
import requests
from utils import get_smms_api_token

def get_smms_upload_history(page=1):
    """
    从 SM.MS 获取上传历史列表 (根据最新文档，仅支持 page 参数)
    API: GET https://sm.ms/api/v2/upload_history?page=<page>
    Header: { "Authorization": <token> }
    返回: data 列表，如果无更多数据或请求失败则返回空列表
    """
    url = f"https://sm.ms/api/v2/upload_history?page={page}"
    headers = {
        "Authorization": get_smms_api_token()  # 使用 utils.py 中的函数
    }
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if data.get("success"):
            return data.get("data", [])
        else:
            print(f"获取 SM.MS 列表失败: {data}")
            return []
    except Exception as e:
        print(f"请求 SM.MS 发生错误: {e}")
        return []