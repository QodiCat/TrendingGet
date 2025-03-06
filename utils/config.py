# 读取配置文件
import json 

def load_config():
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"读取配置文件失败: {e}")
        # 返回默认配置
        return {
            "languages": ["python"],
            "auto_push": True,
            "update_frequency": "daily",
            "max_repos_per_language": 10,
            "file_format": "markdown",
            "email": {
                "enable": False,
                "sender": "",
                "password": "",
                "receiver": "",
                "smtp_server": "",
                "smtp_port": 465
            }
        }