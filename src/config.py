# https://github.com/123panNextGen/123pan
# src/config.py

import os
import json
import platform
from log import get_logger

logger = get_logger(__name__)

# 配置文件路径
if platform.system() == 'Windows':
    CONFIG_DIR = os.path.join(os.environ.get('APPDATA', ''), 'Qxyz17', '123pan')
else:
    CONFIG_DIR = os.path.join(os.path.expanduser('~'), '.config', 'Qxyz17', '123pan')
CONFIG_FILE = os.path.join(CONFIG_DIR, 'config.json')


class ConfigManager:
    """配置管理类"""
    
    @staticmethod
    def ensure_config_dir():
        """确保配置目录存在"""
        if not os.path.exists(CONFIG_DIR):
            os.makedirs(CONFIG_DIR, exist_ok=True)
    
    @staticmethod
    def load_config():
        """加载配置"""
        ConfigManager.ensure_config_dir()
        default_config = {
            "userName": "",
            "passWord": "",
            "authorization": "",
            "deviceType": "",
            "osVersion": "",
            "settings": {
                "defaultDownloadPath": os.path.join(os.path.expanduser("~"), "Downloads"),
                "askDownloadLocation": True
            }
        }
        
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # 确保新版本配置兼容性
                    if "settings" not in config:
                        config["settings"] = default_config["settings"]
                    return config
            except Exception as e:
                logger.error(f"加载配置失败: {e}")
                return default_config
        return default_config
    
    @staticmethod
    def save_config(config):
        """保存配置"""
        try:
            ConfigManager.ensure_config_dir()
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"保存配置失败: {e}")
            return False
    
    @staticmethod
    def get_setting(key, default=None):
        """获取特定设置"""
        config = ConfigManager.load_config()
        return config.get("settings", {}).get(key, default)
