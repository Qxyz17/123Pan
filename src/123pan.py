from PyQt6 import QtCore, QtGui, QtWidgets
import sys
import os
import hashlib
import json
import requests
import time
import random
import re
import uuid
import platform
from log import get_logger

logger = get_logger(__name__)

# 配置文件路径
if platform.system() == 'Windows':
    CONFIG_DIR = os.path.join(os.environ.get('APPDATA', ''), 'Qxyz17', '123pan')
else:
    CONFIG_DIR = os.path.join(os.path.expanduser('~'), '.config', 'Qxyz17', '123pan')
CONFIG_FILE = os.path.join(CONFIG_DIR, 'config.json')

# 自定义侧栏按钮类
class SidebarButton(QtWidgets.QPushButton):
    """侧栏按钮，支持hover事件"""
    entered = QtCore.pyqtSignal()
    left = QtCore.pyqtSignal()
    
    def enterEvent(self, event):
        """鼠标进入事件"""
        super().enterEvent(event)
        self.entered.emit()
    
    def leaveEvent(self, event):
        """鼠标离开事件"""
        super().leaveEvent(event)
        self.left.emit()

# 配置管理类
class ConfigManager:
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

# 设置对话框
class SettingsDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("设置")
        self.setModal(True)
        self.resize(500, 200)
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowType.WindowContextHelpButtonHint)
        
        layout = QtWidgets.QVBoxLayout(self)
        
        # 下载设置组
        download_group = QtWidgets.QGroupBox("下载设置")
        download_layout = QtWidgets.QVBoxLayout()
        
        # 默认下载路径
        path_layout = QtWidgets.QHBoxLayout()
        path_layout.addWidget(QtWidgets.QLabel("默认下载路径:"))
        self.le_download_path = QtWidgets.QLineEdit()
        self.le_download_path.setReadOnly(True)
        path_layout.addWidget(self.le_download_path, 1)
        self.btn_browse = QtWidgets.QPushButton("浏览...")
        self.btn_browse.clicked.connect(self.browse_download_path)
        path_layout.addWidget(self.btn_browse)
        download_layout.addLayout(path_layout)
        
        # 下载前询问
        self.cb_ask_location = QtWidgets.QCheckBox("每次下载前询问保存位置")
        download_layout.addWidget(self.cb_ask_location)
        
        download_group.setLayout(download_layout)
        layout.addWidget(download_group)
        
        # 按钮
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        self.btn_save = QtWidgets.QPushButton("保存")
        self.btn_cancel = QtWidgets.QPushButton("取消")
        button_layout.addWidget(self.btn_save)
        button_layout.addWidget(self.btn_cancel)
        layout.addLayout(button_layout)
        
        # 连接信号
        self.btn_save.clicked.connect(self.accept)
        self.btn_cancel.clicked.connect(self.reject)
        
        # 加载当前设置
        self.load_settings()
    
    def load_settings(self):
        """加载当前设置"""
        default_path = ConfigManager.get_setting("defaultDownloadPath", 
                                                os.path.join(os.path.expanduser("~"), "Downloads"))
        ask_location = ConfigManager.get_setting("askDownloadLocation", True)
        
        self.le_download_path.setText(default_path)
        self.cb_ask_location.setChecked(ask_location)
    
    def browse_download_path(self):
        """浏览下载路径"""
        path = QtWidgets.QFileDialog.getExistingDirectory(
            self, "选择默认下载路径", self.le_download_path.text()
        )
        if path:
            self.le_download_path.setText(path)
    
    def get_settings(self):
        """获取设置的参数"""
        return {
            "defaultDownloadPath": self.le_download_path.text(),
            "askDownloadLocation": self.cb_ask_location.isChecked()
        }

class Pan123:
    def __init__(
            self,
            readfile=True,
            user_name="",
            pass_word="",
            authorization="",
            input_pwd=False,
    ):

        self.all_device_type = [
            "MI-ONE PLUS", "MI-ONE C1", "MI-ONE", "2012051", "2012053", "2012052", "2012061", "2012062", "2013012",
            "2013021", "2012121", "2013061", "2013062", "2013063", "2014215", "2014218", "2014216", "2014719",
            "2014716", "2014726", "2015015", "2015561", "2015562", "2015911", "2015201", "2015628", "2015105",
            "2015711", "2016070", "2016089", "MDE2", "MDT2", "MCE16", "MCT1", "M1804D2SE", "M1804D2ST", "M1804D2SC",
            "M1803E1A", "M1803E1T", "M1803E1C", "M1807E8S", "M1807E8A", "M1805E2A", "M1808D2TE", "M1808D2TT",
            "M1808D2TC", "M1808D2TG", "M1902F1A", "M1902F1T", "M1902F1C", "M1902F1G", "M1908F1XE", "M1903F2A",
            "M1903F2G", "M1903F10G", "M1903F11G", "M1904F3BG", "M2001J2E", "M2001J2G", "M2001J2I", "M2001J1E",
            "M2001J1G", "M2002J9E", "M2002J9G", "M2002J9S", "M2002J9R", "M2007J1SC", "M2007J3SY", "M2007J3SP",
            "M2007J3SG", "M2007J3SI", "M2007J17G", "M2007J17I", "M2102J2SC", "M2011K2C", "M2011K2G", "M2102K1AC",
            "M2102K1C", "M2102K1G", "M2101K9C", "M2101K9G", "M2101K9R", "M2101K9AG", "M2101K9AI", "2107119DC",
            "2109119DG", "2109119DI", "M2012K11G", "M2012K11AI", "M2012K11I", "21081111RG", "2107113SG", "2107113SI",
            "2107113SR", "21091116I", "21091116UI", "2201123C", "2201123G", "2112123AC", "2112123AG", "2201122C",
            "2201122G", "2207122MC", "2203129G", "2203129I", "2206123SC", "2206122SC", "2203121C", "22071212AG",
            "22081212UG", "22081212R", "A201XM", "2211133C", "2211133G", "2210132C", "2210132G", "2304FPN6DC",
            "2304FPN6DG", "2210129SG", "2306EPN60G", "2306EPN60R", "XIG04", "23078PND5G", "23088PND5R", "A301XM",
            "23127PN0CC", "23127PN0CG", "23116PN5BC", "2311BPN23C", "24031PN0DC", "24030PN60G", "24053PY09I",
            "2406APNFAG", "XIG06", "2407FPN8EG", "2407FPN8ER", "A402XM", "2014616", "2014619", "2014618", "2014617",
            "2015011", "2015021", "2015022", "2015501", "2015211", "2015212", "2015213", "MCE8", "MCT8", "M1910F4G",
            "M1910F4S", "M2002F4LG", "2016080", "MDE5", "MDT5", "MDE5S", "M1803D5XE", "M1803D5XA", "M1803D5XT",
            "M1803D5XC", "M1810E5E", "M1810E5A", "M1810E5GG", "2106118C", "M2011J18C", "22061218C", "2308CPXD0C",
            "24072PX77C", "2405CPX3DC", "2405CPX3DG", "2016001", "2016002", "2016007", "MDE40", "MDT4", "MDI40",
            "M1804E4A", "M1804E4T", "M1804E4C", "M1904F3BC", "M1904F3BT", "M1906F9SC", "M1910F4E", "2109119BC",
            "2109119BC", "2209129SC", "23046PNC9C", "24053PY09C", "M1901F9E", "M1901F9T", "MDG2", "MDI2", "M1804D2SG",
            "M1804D2SI", "M1805D1SG", "M1906F9SH", "M1906F9SI", "A0101", "2015716", "MCE91", "M1806D9W", "M1806D9E",
            "M1806D9PE", "21051182C", "21051182G", "M2105K81AC", "M2105K81C", "22081281AC", "23043RP34C", "23043RP34G",
            "23043RP34I", "23046RP50C", "2307BRPDCC", "24018RPACC", "24018RPACG", "2013022", "2013023", "2013029",
            "2013028", "2014011", "2014501", "2014813", "2014112", "2014811", "2014812", "2014821", "2014817",
            "2014818", "2014819", "2014502", "2014512", "2014816", "2015811", "2015812", "2015810", "2015817",
            "2015818", "2015816", "2016030", "2016031", "2016032", "2016037", "2016036", "2016035", "2016033",
            "2016090", "2016060", "2016111", "2016112", "2016117", "2016116", "MAE136", "MAT136", "MAG138", "MAI132",
            "MDE1", "MDT1", "MDG1", "MDI1", "MEE7", "MET7", "MEG7", "MCE3B", "MCT3B", "MCG3B", "MCI3B", "M1804C3DE",
            "M1804C3DT", "M1804C3DC", "M1804C3DG", "M1804C3DI", "M1805D1SE", "M1805D1ST", "M1805D1SC", "M1805D1SI",
            "M1804C3CE", "M1804C3CT", "M1804C3CC", "M1804C3CG", "M1804C3CI", "M1810F6LE", "M1810F6LT", "M1810F6LG",
            "M1810F6LI", "M1903C3EE", "M1903C3ET", "M1903C3EC", "M1903C3EG", "M1903C3EI", "M1908C3IE", "M1908C3IC",
            "M1908C3IG", "M1908C3II", "M1908C3KE", "M1908C3KG", "M1908C3KI", "M2001C3K3I", "M2004J19C", "M2004J19G",
            "M2004J19I", "M2004J19AG", "M2006C3LC", "M2006C3LG", "M2006C3LVG", "M2006C3LI", "M2006C3LII", "M2006C3MG",
            "M2006C3MT", "M2006C3MNG", "M2006C3MII", "M2010J19SG", "M2010J19SI", "M2010J19SR", "M2010J19ST",
            "M2010J19SY", "M2010J19SL", "21061119AG", "21061119AL", "21061119BI", "21061119DG", "21121119SG",
            "21121119VL", "22011119TI", "22011119UY", "22041219G", "22041219I", "22041219NY", "220333QAG", "220333QBI",
            "220333QNY", "220333QL", "220233L2C", "220233L2G", "220233L2I", "22071219AI", "23053RN02A", "23053RN02I",
            "23053RN02L", "23053RN02Y", "23077RABDC", "23076RN8DY", "23076RA4BR", "XIG03", "A401XM", "23076RN4BI",
            "23076RA4BC", "22120RN86C", "22120RN86G", "22120RN86H", "2212ARNC4L", "22126RN91Y", "2404ARN45A",
            "2404ARN45I", "24049RN28L", "24040RN64Y", "2406ERN9CI", "23106RN0DA", "2311DRN14I", "23100RN82L",
            "23108RN04Y", "23124RN87C", "23124RN87I", "23124RN87G", "2409BRN2CA", "2409BRN2CI", "2409BRN2CL",
            "2409BRN2CY", "2411DRN47C", "2014018", "2013121", "2014017", "2013122", "2014022", "2014021", "2014715",
            "2014712", "2014915", "2014912", "2014916", "2014911", "2014910", "2015052", "2015051", "2015712",
            "2015055", "2015056", "2015617", "2015611", "2015112", "2015116", "2015161", "2016050", "2016051",
            "2016101", "2016130", "2016100", "MBE6A5", "MBT6A5", "MEI7", "MEE7S", "MET7S", "MEC7S", "M1803E7SG",
            "MEI7S", "MDE6", "MDT6", "MDG6", "MDI6", "MDE6S", "MDT6S", "MDG6S", "MDI6S", "M1806E7TG", "M1806E7TI",
            "M1901F7E", "M1901F7T", "M1901F7C", "M1901F7G", "M1901F7I", "M1901F7BE", "M1901F7S", "M1908C3JE",
            "M1908C3JC", "M1908C3JG", "M1908C3JI", "M1908C3XG", "M1908C3JGG", "M1906G7E", "M1906G7T", "M1906G7G",
            "M1906G7I", "M2010J19SC", "M2007J22C", "M2003J15SS", "M2003J15SI", "M2003J15SG", "M2007J22G", "M2007J22R",
            "M2007J17C", "M2003J6A1G", "M2003J6A1R", "M2003J6A1I", "M2003J6B1I", "M2003J6B2G", "M2101K7AG", "M2101K7AI",
            "M2101K7BG", "M2101K7BI", "M2101K7BNY", "M2101K7BL", "M2103K19C", "M2103K19I", "M2103K19G", "M2103K19Y",
            "M2104K19J", "22021119KR", "A101XM", "M2101K6G", "M2101K6T", "M2101K6R", "M2101K6P", "M2101K6I",
            "M2104K10AC", "2109106A1I", "21121119SC", "2201117TG", "2201117TI", "2201117TL", "2201117TY", "21091116AC",
            "21091116AI", "22041219C", "2201117SG", "2201117SI", "2201117SL", "2201117SY", "22087RA4DI", "22031116BG",
            "21091116C", "2201116TG", "2201116TI", "2201116SC", "2201116SG", "2201116SR", "2201116SI", "21091116UC",
            "21091116UG", "22041216C", "22041216UC", "22095RA98C", "23021RAAEG", "23027RAD4I", "23028RA60L",
            "23021RAA2Y", "22101317C", "22111317G", "22111317I", "23076RA4BC", "2303CRA44A", "2303ERA42L", "23030RAC7Y",
            "2209116AG", "22101316C", "22101316G", "22101316I", "22101316UCP", "22101316UG", "22101316UP", "22101316UC",
            "22101320C", "23054RA19C", "23049RAD8C", "23129RAA4G", "23129RA5FL", "23124RA7EO", "2312DRAABC",
            "2312DRAABI", "2312DRAABG", "23117RA68G", "2312DRA50C", "2312DRA50G", "2312DRA50I", "XIG05", "23090RA98C",
            "23090RA98G", "23090RA98I", "24040RA98R", "2406ERN9CC", "2311FRAFDC", "24094RAD4C", "24094RAD4G",
            "24094RAD4I", "24090RA29C", "24090RA29G", "24090RA29I", "24115RA8EC", "24115RA8EG", "24115RA8EI",
            "M2004J7AC", "M2004J7BC", "M2003J15SC", "24069RA21C", "M1903F10A", "M1903F10C", "M1903F10I", "M1903F11A",
            "M1903F11C", "M1903F11I", "M1903F11A", "M2001G7AE", "M2001G7AC", "M2001G7AC", "M1912G7BE", "M1912G7BC",
            "M2001J11C", "M2001J11C", "M2006J10C", "M2007J3SC", "M2012K11AC", "M2012K11C", "M2012K10C", "22021211RC",
            "22041211AC", "22011211C", "21121210C", "22081212C", "22041216I", "23013RK75C", "22127RK46C", "22122RK93C",
            "23078RKD5C", "23113RKC6C", "23117RK66C", "2311DRK48C", "2407FRK8EC", "2016020", "2016021", "M1803E6E",
            "M1803E6T", "M1803E6C", "M1803E6G", "M1803E6I", "M1810F6G", "M1810F6I", "M1903C3GG", "M1903C3GI",
            "220733SG", "220733SH", "220733SL", "220733SFG", "220733SFH", "23028RN4DG", "23028RN4DH", "23026RN54G",
            "23028RNCAG", "23028RNCAH", "23129RN51X", "23129RN51H", "2312CRNCCL", "24048RN6CG", "24048RN6CI",
            "24044RN32L", "2409BRN2CG", "22081283C", "22081283G", "23073RPBFC", "23073RPBFG", "23073RPBFL",
            "2405CRPFDC", "2405CRPFDG", "2405CRPFDI", "2405CRPFDL", "24074RPD2C", "24074RPD2G", "24074RPD2I",
            "24075RP89G", "24076RP19G", "24076RP19I", "M1805E10A", "M2004J11G", "M2012K11AG", "M2104K10I", "22021211RG",
            "22021211RI", "21121210G", "23049PCD8G", "23049PCD8I", "23013PC75G", "24069PC21G", "24069PC21I",
            "23113RKC6G", "M1912G7BI", "M2007J20CI", "M2007J20CG", "M2007J20CT", "M2102J20SG", "M2102J20SI",
            "21061110AG", "2201116PG", "2201116PI", "22041216G", "22041216UG", "22111317PG", "22111317PI", "22101320G",
            "22101320I", "23122PCD1G", "23122PCD1I", "2311DRK48G", "2311DRK48I", "2312FRAFDI", "M2004J19PI",
            "M2003J6CI", "M2010J19CG", "M2010J19CT", "M2010J19CI", "M2103K19PG", "M2103K19PI", "22041219PG",
            "22041219PI", "2201117PG", "2201117PI", "21091116AG", "22031116AI", "22071219CG", "22071219CI",
            "2207117BPG", "2404APC5FG", "2404APC5FI", "23128PC33I", "24066PC95I", "2312FPCA6G", "23076PC4BI",
            "M2006C3MI", "211033MI", "220333QPG", "220333QPI", "220733SPH", "2305EPCC4G", "2302EPCC4H", "22127PC95G",
            "22127PC95H", "2312BPC51X", "2312BPC51H", "2310FPCA4G", "2310FPCA4I", "2405CPCFBG", "24074PCD2I", "FYJ01QP",
            "21051191C"
        ]
        self.all_os_versions = [
            "Android_7.1.2", "Android_8.0.0", "Android_8.1.0", "Android_9.0", "Android_10", "Android_11", "Android_12",
            "Android_13", "Android_6.0.1", "Android_5.1.1", "Android_4.4.4", "Android_4.3", "Android_4.2.2",
            "Android_4.1.2",
        ]
        # 随机生成设备信息
        self.devicetype = random.choice(self.all_device_type)
        self.osversion = random.choice(self.all_os_versions)

        self.cookies = None
        self.recycle_list = None
        self.list = []
        self.total = 0
        self.parent_file_name_list = []
        self.all_file = False
        self.file_page = 0
        self.file_list = []
        self.dir_list = []
        self.name_dict = {}
        if readfile:
            self.read_ini(user_name, pass_word, input_pwd, authorization)
        else:
            if user_name == "" or pass_word == "":
                raise Exception("用户名或密码为空")
            self.user_name = user_name
            self.password = pass_word
            self.authorization = authorization
        self.header_logined = {
            "user-agent": "123pan/v2.4.0(" + self.osversion + ";Xiaomi)",
            "authorization": self.authorization,
            "accept-encoding": "gzip",
            "content-type": "application/json",
            "osversion": self.osversion,
            "loginuuid": str(uuid.uuid4().hex),
            "platform": "android",
            "devicetype": self.devicetype,
            "devicename": "Xiaomi",
            "host": "www.123pan.com",
            "app-version": "61",
            "x-app-version": "2.4.0"
        }
        self.parent_file_id = 0  # 路径，文件夹的id,0为根目录
        self.parent_file_list = [0]
        res_code_getdir = self.get_dir()[0]
        if res_code_getdir != 0:
            self.login()
            self.get_dir()

    def login(self):
        """登录123云盘账户并获取授权令牌"""
        data = {"type": 1, "passport": self.user_name, "password": self.password}
        login_res = requests.post(
            "https://www.123pan.com/b/api/user/sign_in",
            headers=self.header_logined,
            data=data,
        )

        res_sign = login_res.json()
        res_code_login = res_sign["code"]
        if res_code_login != 200:
            logger.error("code = 1 Error:" + str(res_code_login))
            logger.error(res_sign.get("message", ""))
            return res_code_login
        set_cookies = login_res.headers.get("Set-Cookie", "")
        set_cookies_list = {}

        for cookie in set_cookies.split(';'):
            if '=' in cookie:
                key, value = cookie.strip().split('=', 1)
                set_cookies_list[key] = value
            else:
                set_cookies_list[cookie.strip()] = None

        self.cookies = set_cookies_list

        token = res_sign["data"]["token"]
        self.authorization = "Bearer " + token
        self.header_logined["authorization"] = self.authorization
        self.save_file()
        return res_code_login

    def save_file(self):
        """将账户信息保存到配置文件"""
        try:
            config = ConfigManager.load_config()
            config.update({
                "userName": self.user_name,
                "passWord": self.password,
                "authorization": self.authorization,
                "deviceType": self.devicetype,
                "osVersion": self.osversion,
            })
            ConfigManager.save_config(config)
            logger.info("账号已保存")
        except Exception as e:
            logger.error("保存账号失败:", e)

    def get_dir(self, save=True):
        """获取当前目录下的文件列表"""
        return self.get_dir_by_id(self.parent_file_id, save)

    def get_dir_by_id(self, file_id, save=True, all=False, limit=100):
        """按文件夹ID获取文件列表（支持分页）
        
        Args:
            file_id: 文件夹ID
            save: 是否保存结果到列表
            all: 是否强制获取所有文件
            limit: 每页限制数量
        """
        get_pages = 3
        res_code_getdir = 0
        page = self.file_page * get_pages + 1
        lenth_now = len(self.list)
        if all:
            # 强制获取所有文件
            page = 1
            lenth_now = 0
        lists = []

        total = -1
        times = 0
        while (lenth_now < total or total == -1) and (times < get_pages or all):
            base_url = "https://www.123pan.com/api/file/list/new"
            params = {
                "driveId": 0,
                "limit": limit,
                "next": 0,
                "orderBy": "file_id",
                "orderDirection": "desc",
                "parentFileId": str(file_id),
                "trashed": False,
                "SearchData": "",
                "Page": str(page),
                "OnlyLookAbnormalFile": 0,
            }
            try:
                a = requests.get(base_url, headers=self.header_logined, params=params, timeout=30)
            except Exception:
                logger.error("连接失败")
                return -1, []
            text = a.json()
            res_code_getdir = text["code"]
            if res_code_getdir != 0:
                logger.error("code = 2 Error:" + str(res_code_getdir))
                logger.error(text.get("message", ""))
                return res_code_getdir, []
            lists_page = text["data"]["InfoList"]
            lists += lists_page
            total = text["data"]["Total"]
            lenth_now += len(lists_page)
            page += 1
            times += 1
            if times % 5 == 0:
                logger.warning("警告：文件夹内文件过多：" + str(lenth_now) + "/" + str(total))
                logger.info("为防止对服务器造成影响，暂停3秒")
                time.sleep(3)

        if lenth_now < total:
            logger.warning("文件夹内文件过多：" + str(lenth_now) + "/" + str(total))
            self.all_file = False
        else:
            self.all_file = True
        self.total = total
        self.file_page += 1
        if save:
            self.list = self.list + lists

        return res_code_getdir, lists

    def show(self):
        """显示文件列表信息到日志"""
        if not self.all_file:
            logger.info(f"获取了{len(self.list)}/{self.total}个文件")
        else:
            logger.info(f"获取全部{len(self.list)}个文件")

    # fileNumber 从0开始，0为第一个文件，传入时需要减一 
    def link_by_number(self, file_number, showlink=True):
        file_detail = self.list[file_number]
        return self.link_by_fileDetail(file_detail, showlink)

    def link_by_fileDetail(self, file_detail, showlink=True):
        type_detail = file_detail["Type"]

        if type_detail == 1:
            down_request_url = "https://www.123pan.com/a/api/file/batch_download_info"
            down_request_data = {"fileIdList": [{"fileId": int(file_detail["FileId"])}]}

        else:
            down_request_url = "https://www.123pan.com/a/api/file/download_info"
            down_request_data = {
                "driveId": 0,
                "etag": file_detail["Etag"],
                "fileId": file_detail["FileId"],
                "s3keyFlag": file_detail["S3KeyFlag"],
                "type": file_detail["Type"],
                "fileName": file_detail["FileName"],
                "size": file_detail["Size"],
            }

        link_res = requests.post(
            down_request_url,
            headers=self.header_logined,
            data=json.dumps(down_request_data),
            timeout=10
        )
        link_res_json = link_res.json()
        res_code_download = link_res_json["code"]
        if res_code_download != 0:
            logger.error("获取下载链接失败，返回码: " + str(res_code_download))
            logger.error(link_res_json.get("message", ""))
            return res_code_download
        down_load_url = link_res.json()["data"]["DownloadUrl"]
        next_to_get = requests.get(down_load_url, timeout=10, allow_redirects=False).text
        url_pattern = re.compile(r"href='(https?://[^']+)'")
        redirect_url = url_pattern.findall(next_to_get)[0]
        if showlink:
            logger.info(f"获取下载链接成功: {redirect_url}")

        return redirect_url

    def download(self, file_number, download_path="download"):
        file_detail = self.list[file_number]
        if file_detail["Type"] == 1:
            logger.info("开始下载")
            file_name = file_detail["FileName"] + ".zip"
        else:
            file_name = file_detail["FileName"]  # 文件名

        down_load_url = self.link_by_number(file_number, showlink=False)
        if type(down_load_url) == int:
            return
        self.download_from_url(down_load_url, file_name, download_path)

    def download_from_url(self, url, file_name, download_path="download"):
        """从URL下载文件"""
        if not os.path.exists(download_path):
            logger.info("创建下载目录")
            os.makedirs(download_path)
        
        file_path = os.path.join(download_path, file_name)
        temp_path = file_path + ".123pan"
        
        # 如果临时文件存在，删除它（防止之前的不完整下载）
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        down = requests.get(url, stream=True, timeout=10)
        file_size = int(down.headers.get("Content-Length", 0) or 0)
        
        # 以.123pan后缀下载，下载完成重命名，防止下载中断
        with open(temp_path, "wb") as f:
            for chunk in down.iter_content(8192):
                if chunk:
                    f.write(chunk)
        
        os.rename(temp_path, file_path)

    def get_all_things(self, id):
        self.dir_list.remove(id)
        all_list = self.get_dir_by_id(id, save=False)[1]

        for i in all_list:
            if i["Type"] == 0:
                self.file_list.append(i)
            else:
                self.dir_list.append(i["FileId"])
                self.name_dict[i["FileId"]] = i["FileName"]

        for i in self.dir_list:
            self.get_all_things(i)

    def download_dir(self, file_detail, download_path_root="download"):
        self.name_dict[file_detail["FileId"]] = file_detail["FileName"]
        if file_detail["Type"] != 1:
            logger.warning("不是文件夹")
            return

        all_list = self.get_dir_by_id(file_detail["FileId"], save=False, all=True, limit=100)[1]
        for i in all_list[::-1]:
            if i["Type"] == 0:  # 直接开始下载
                AbsPath = i["AbsPath"]
                for key, value in self.name_dict.items():
                    AbsPath = AbsPath.replace(str(key), value)
                download_path = download_path_root + AbsPath
                download_path = download_path.replace("/" + str(i["FileId"]), "")
                self.download_from_url(i["DownloadUrl"], i["FileName"], download_path)

            else:
                self.download_dir(i, download_path_root)

    def recycle(self):
        recycle_id = 0
        url = (
                "https://www.123pan.com/a/api/file/list/new?driveId=0&limit=100&next=0"
                "&orderBy=fileId&orderDirection=desc&parentFileId="
                + str(recycle_id)
                + "&trashed=true&&Page=1"
        )
        recycle_res = requests.get(url, headers=self.header_logined, timeout=10)
        json_recycle = recycle_res.json()
        recycle_list = json_recycle["data"]["InfoList"]
        self.recycle_list = recycle_list

    # fileNumber 从0开始，0为第一个文件，传入时需要减一
    def delete_file(self, file, by_num=True, operation=True):
        """删除或恢复文件"""
        if by_num:
            if not str(file).isdigit():
                raise ValueError("文件索引必须是数字")
            if 0 <= file < len(self.list):
                file_detail = self.list[file]
            else:
                raise IndexError("文件索引超出范围")
        else:
            if file in self.list:
                file_detail = file
            else:
                raise ValueError("文件不存在")
        data_delete = {
            "driveId": 0,
            "fileTrashInfoList": file_detail,
            "operation": operation,
        }
        delete_res = requests.post(
            "https://www.123pan.com/a/api/file/trash",
            data=json.dumps(data_delete),
            headers=self.header_logined,
            timeout=10
        )
        dele_json = delete_res.json()
        print(dele_json)
        message = dele_json.get("message", "")
        print(message)

    def share(self, file_id_list, share_pwd=""):
        """分享文件"""
        if not file_id_list:
            raise ValueError("文件ID列表为空")
        data = {
            "driveId": 0,
            "expiration": "2099-12-12T08:00:00+08:00",
            "fileIdList": file_id_list,
            "shareName": "123云盘分享",
            "sharePwd": share_pwd or "",
            "event": "shareCreate"
        }
        share_res = requests.post(
            "https://www.123pan.com/a/api/share/create",
            headers=self.header_logined,
            data=json.dumps(data),
            timeout=10
        )
        share_res_json = share_res.json()
        if share_res_json.get("code", -1) != 0:
            raise RuntimeError(f"分享失败: {share_res_json.get('message', '')}")
        share_key = share_res_json["data"]["ShareKey"]
        share_url = "https://www.123pan.com/s/" + share_key
        return share_url

    def up_load(self, file_path):
        file_path = file_path.replace('"', "").replace("\\", "/")
        file_name = os.path.basename(file_path)
        if not os.path.exists(file_path):
            raise FileNotFoundError("文件不存在")
        if os.path.isdir(file_path):
            raise IsADirectoryError("不支持文件夹上传")
        fsize = os.path.getsize(file_path)
        readable_hash = self._compute_file_md5(file_path)

        list_up_request = {
            "driveId": 0,
            "etag": readable_hash,
            "fileName": file_name,
            "parentFileId": self.parent_file_id,
            "size": fsize,
            "type": 0,
            "duplicate": 0,
        }

        up_res = requests.post(
            "https://www.123pan.com/b/api/file/upload_request",
            headers=self.header_logined,
            data=list_up_request,
            timeout=10
        )
        up_res_json = up_res.json()
        res_code_up = up_res_json.get("code", -1)
        if res_code_up == 5060:
            # 同名文件处理由调用者在GUI中处理
            raise RuntimeError("同名文件存在")
        if res_code_up != 0:
            raise RuntimeError(f"上传请求失败: {up_res_json}")
        if up_res_json["data"].get("Reuse", False):
            return up_file_id

        bucket = up_res_json["data"]["Bucket"]
        storage_node = up_res_json["data"]["StorageNode"]
        upload_key = up_res_json["data"]["Key"]
        upload_id = up_res_json["data"]["UploadId"]
        up_file_id = up_res_json["data"]["FileId"]  # 上传文件的fileId,完成上传后需要用到

        # 获取已将上传的分块
        start_data = {
            "bucket": bucket,
            "key": upload_key,
            "uploadId": upload_id,
            "storageNode": storage_node,
        }
        start_res = requests.post(
            "https://www.123pan.com/b/api/file/s3_list_upload_parts",
            headers=self.header_logined,
            data=json.dumps(start_data),
            timeout=10
        )
        start_res_json = start_res.json()
        res_code_up = start_res_json.get("code", -1)
        if res_code_up != 0:
            raise RuntimeError(f"获取传输列表失败: {start_res_json}")

        # 分块，每一块取一次链接，依次上传
        block_size = 5242880
        with open(file_path, "rb") as f:
            part_number_start = 1
            put_size = 0
            while True:
                data = f.read(block_size)
                put_size = put_size + len(data)

                if not data:
                    break
                get_link_data = {
                    "bucket": bucket,
                    "key": upload_key,
                    "partNumberEnd": part_number_start + 1,
                    "partNumberStart": part_number_start,
                    "uploadId": upload_id,
                    "StorageNode": storage_node,
                }

                get_link_url = (
                    "https://www.123pan.com/b/api/file/s3_repare_upload_parts_batch"
                )
                get_link_res = requests.post(
                    get_link_url,
                    headers=self.header_logined,
                    data=json.dumps(get_link_data),
                    timeout=10
                )
                get_link_res_json = get_link_res.json()
                res_code_up = get_link_res_json.get("code", -1)
                if res_code_up != 0:
                    raise RuntimeError(f"获取链接失败: {get_link_res_json}")
                upload_url = get_link_res_json["data"]["presignedUrls"][
                    str(part_number_start)
                ]
                requests.put(upload_url, data=data, timeout=10)

                part_number_start = part_number_start + 1


        uploaded_list_url = "https://www.123pan.com/b/api/file/s3_list_upload_parts"
        uploaded_comp_data = {
            "bucket": bucket,
            "key": upload_key,
            "uploadId": upload_id,
            "storageNode": storage_node,
        }
        requests.post(
            uploaded_list_url,
            headers=self.header_logined,
            data=json.dumps(uploaded_comp_data),
            timeout=10
        )
        compmultipart_up_url = (
            "https://www.123pan.com/b/api/file/s3_complete_multipart_upload"
        )
        requests.post(
            compmultipart_up_url,
            headers=self.header_logined,
            data=json.dumps(uploaded_comp_data),
            timeout=10
        )

        if fsize > 64 * 1024 * 1024:
            time.sleep(3)
        close_up_session_url = "https://www.123pan.com/b/api/file/upload_complete"
        close_up_session_data = {"fileId": up_file_id}
        close_up_session_res = requests.post(
            close_up_session_url,
            headers=self.header_logined,
            data=json.dumps(close_up_session_data),
            timeout=10
        )
        close_res_json = close_up_session_res.json()
        res_code_up = close_res_json.get("code", -1)
        if res_code_up != 0:
            raise RuntimeError(f"上传完成确认失败: {close_res_json}")
        return up_file_id

    # dirId 就是 fileNumber，从0开始，0为第一个文件，传入时需要减一 ！！！（好像文件夹都排在前面）
    def cd(self, dir_num):
        """进入文件夹"""
        if dir_num == "..":
            if len(self.parent_file_list) > 1:
                self.all_file = False
                self.file_page = 0
                self.parent_file_list.pop()
                self.parent_file_id = self.parent_file_list[-1]
                self.list = []
                self.parent_file_name_list.pop()
                self.get_dir()
            else:
                raise RuntimeError("已经是根目录")
            return
        if dir_num == "/":
            self.all_file = False
            self.file_page = 0
            self.parent_file_id = 0
            self.parent_file_list = [0]
            self.list = []
            self.parent_file_name_list = []
            self.get_dir()
            return
        if not str(dir_num).isdigit():
            raise ValueError("文件夹编号必须是数字")
        dir_num = int(dir_num) - 1
        if dir_num > (len(self.list) - 1) or dir_num < 0:
            raise IndexError("文件夹编号超出范围")
        if self.list[dir_num]["Type"] != 1:
            raise TypeError("选中项不是文件夹")
        self.all_file = False
        self.file_page = 0
        self.parent_file_id = self.list[dir_num]["FileId"]
        self.parent_file_list.append(self.parent_file_id)
        self.parent_file_name_list.append(self.list[dir_num]["FileName"])
        self.list = []
        self.get_dir()

    def cdById(self, file_id):
        self.all_file = False
        self.file_page = 0
        self.list = []
        self.parent_file_id = file_id
        self.parent_file_list.append(self.parent_file_id)
        self.get_dir()
        self.show()

    def read_ini(
            self,
            user_name,
            pass_word,
            input_pwd,
            authorization="",
    ):
        """从配置文件读取账号信息"""
        try:
            config = ConfigManager.load_config()
            deviceType = config.get("deviceType", "")
            osVersion = config.get("osVersion", "")
            if deviceType:
                self.devicetype = deviceType
            if osVersion:
                self.osversion = osVersion
            user_name = config.get("userName", user_name)
            pass_word = config.get("passWord", pass_word)
            authorization = config.get("authorization", authorization)
        except Exception as e:
            logger.error(f"获取配置失败: {e}")
            if user_name == "" or pass_word == "":
                raise Exception("无法从配置获取账号信息")

        self.user_name = user_name
        self.password = pass_word
        self.authorization = authorization

    def mkdir(self, dirname, remakedir=False):
        """创建文件夹"""
        if not remakedir:
            for i in self.list:
                if i["FileName"] == dirname:
                    logger.info("文件夹已存在")
                    return i["FileId"]

        url = "https://www.123pan.com/a/api/file/upload_request"
        data_mk = {
            "driveId": 0,
            "etag": "",
            "fileName": dirname,
            "parentFileId": self.parent_file_id,
            "size": 0,
            "type": 1,
            "duplicate": 1,
            "NotReuse": True,
            "event": "newCreateFolder",
            "operateType": 1,
        }
        res_mk = requests.post(
            url,
            headers=self.header_logined,
            data=json.dumps(data_mk),
            timeout=10
        )
        try:
            res_json = res_mk.json()
        except json.decoder.JSONDecodeError:
            logger.error("创建失败")
            logger.error(res_mk.text)
            return
        code_mkdir = res_json.get("code", -1)

        if code_mkdir == 0:
            logger.info(f"创建成功: {res_json['data']['FileId']}")
            self.get_dir()
            return res_json["data"]["Info"]["FileId"]
        logger.error(f"创建失败: {res_json}")
        return
    
    @staticmethod
    def _compute_file_md5(file_path):
        """计算文件MD5值"""
        md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            while True:
                data = f.read(64 * 1024)
                if not data:
                    break
                md5.update(data)
        return md5.hexdigest()

# 线程辅助
class WorkerSignals(QtCore.QObject):
    finished = QtCore.pyqtSignal()
    error = QtCore.pyqtSignal(str)
    result = QtCore.pyqtSignal(object)
    progress = QtCore.pyqtSignal(int)
    log = QtCore.pyqtSignal(str)
    cancel = QtCore.pyqtSignal()

class ThreadedTask(QtCore.QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()
        self.is_cancelled = False

    @QtCore.pyqtSlot()
    def run(self):
        try:
            if self.is_cancelled:
                return
            res = self.fn(*self.args, **self.kwargs, signals=self.signals, task=self)
            if not self.is_cancelled:
                self.signals.result.emit(res)
        except Exception as e:
            if not self.is_cancelled:
                self.signals.error.emit(str(e))
        finally:
            if not self.is_cancelled:
                self.signals.finished.emit()
    
    def cancel(self):
        """取消任务"""
        self.is_cancelled = True
        self.signals.cancel.emit()

# 登录对话框
class LoginDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("登录123云盘")
        self.setModal(True)
        self.resize(420, 150)
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowType.WindowContextHelpButtonHint)

        layout = QtWidgets.QVBoxLayout(self)

        form = QtWidgets.QFormLayout()
        self.le_user = QtWidgets.QLineEdit()
        self.le_pass = QtWidgets.QLineEdit()
        self.le_pass.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        form.addRow("用户名：", self.le_user)
        form.addRow("密码：", self.le_pass)
        layout.addLayout(form)

        h = QtWidgets.QHBoxLayout()
        h.addStretch()
        self.btn_ok = QtWidgets.QPushButton("登录")
        self.btn_cancel = QtWidgets.QPushButton("取消")
        h.addWidget(self.btn_ok)
        h.addWidget(self.btn_cancel)
        layout.addLayout(h)

        self.btn_ok.clicked.connect(self.on_ok)
        self.btn_cancel.clicked.connect(self.reject)

        self.pan = None
        self.login_error = None

        # 从配置文件中加载用户名
        config = ConfigManager.load_config()
        self.le_user.setText(config.get("userName", ""))

    def on_ok(self):
        user = self.le_user.text().strip()
        pwd = self.le_pass.text()
        if not user or not pwd:
            QtWidgets.QMessageBox.information(self, "提示", "请输入用户名和密码。")
            return
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CursorShape.WaitCursor)
        try:
            # 构造123pan并登录
            try:
                self.pan = Pan123(readfile=False, user_name=user, pass_word=pwd, input_pwd=False)
            except Exception:
                self.pan = Pan123(readfile=False, user_name=user, pass_word=pwd, input_pwd=False)
            if not getattr(self.pan, "authorization", None):
                code = self.pan.login()
                if code != 200 and code != 0:
                    self.login_error = f"登录失败，返回码: {code}"
                    QtWidgets.QApplication.restoreOverrideCursor()
                    QtWidgets.QMessageBox.critical(self, "登录失败", self.login_error)
                    return
        except Exception as e:
            self.login_error = str(e)
            QtWidgets.QApplication.restoreOverrideCursor()
            QtWidgets.QMessageBox.critical(self, "登录异常", "登录时发生异常:\n" + str(e))
            return
        finally:
            QtWidgets.QApplication.restoreOverrideCursor()

        try:
            if hasattr(self.pan, "save_file"):
                self.pan.save_file()
        except Exception:
            pass
        self.accept()

    def get_pan(self):
        return self.pan

# 主窗口
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("123云盘")
        self.resize(980, 620)
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowType.WindowContextHelpButtonHint)

        self.pan = None
        self.threadpool = QtCore.QThreadPool.globalInstance()
        # 设置线程池的最大线程数，允许同时下载多个文件
        self.threadpool.setMaxThreadCount(64)

        # 应用123云盘主题
        self.apply_blue_white_theme()

        # 中央布局
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        main_layout = QtWidgets.QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 创建侧边栏
        self.sidebar = QtWidgets.QWidget()
        self.sidebar.setMinimumWidth(200)
        self.sidebar.setMaximumWidth(200)
        self.sidebar.setStyleSheet(
            "background-color: rgba(255, 255, 255, 0.95);"
            "border-right: 1px solid rgba(0, 0, 0, 0.05);"
            "border-radius: 0;"
        )
        sidebar_layout = QtWidgets.QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(10, 20, 10, 10)
        sidebar_layout.setSpacing(8)
        sidebar_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        
        # 侧边栏标题
        sidebar_title = QtWidgets.QLabel("功能菜单")
        sidebar_title.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        sidebar_title.setStyleSheet(
            "font-size: 20px; font-weight: bold; color: #334155; margin-bottom: 20px;"
            "padding: 10px 0;"
        )
        sidebar_layout.addWidget(sidebar_title)
        
        # 侧边栏按钮组
        self.sidebar_buttons = []
        self.sidebar_animations = {}
        self.sidebar_original_geoms = {}
        
        # 文件页按钮
        self.btn_files = SidebarButton("📁 文件")
        self.btn_files.setMinimumHeight(50)
        self.btn_files.setStyleSheet(
            "font-size: 16px; text-align: left; padding-left: 20px;"
            "background-color: rgba(59, 130, 246, 0.9);"
            "color: white; border-radius: 12px;"
            "border: none;"
        )
        sidebar_layout.addWidget(self.btn_files)
        self.sidebar_buttons.append(self.btn_files)
        
        # 传输页按钮
        self.btn_transfer = SidebarButton("🔄 传输")
        self.btn_transfer.setMinimumHeight(50)
        self.btn_transfer.setStyleSheet(
            "font-size: 16px; text-align: left; padding-left: 20px;"
            "background-color: transparent; color: #334155;"
            "border-radius: 12px;"
            "border: none;"
        )
        sidebar_layout.addWidget(self.btn_transfer)
        self.sidebar_buttons.append(self.btn_transfer)
        
        # 为侧边栏按钮添加悬停和点击事件，实现动画效果
        for btn in self.sidebar_buttons:
            btn.entered.connect(lambda b=btn: self.on_sidebar_button_hover(b))
            btn.left.connect(lambda b=btn: self.on_sidebar_button_leave(b))
            btn.pressed.connect(lambda b=btn: self.on_sidebar_button_pressed(b))
            btn.released.connect(lambda b=btn: self.on_sidebar_button_released(b))
            
            # 保存按钮的原始位置
            QtCore.QTimer.singleShot(100, lambda b=btn: self.save_original_position(b))
        
        sidebar_layout.addStretch()
        main_layout.addWidget(self.sidebar)
        
        # 创建右侧内容区域
        right_content = QtWidgets.QWidget()
        right_layout = QtWidgets.QVBoxLayout(right_content)
        right_layout.setContentsMargins(10, 10, 10, 10)
        right_layout.setSpacing(8)
        
        # 顶部横向按钮栏（左上角为设置按钮）
        toolbar_h = QtWidgets.QHBoxLayout()
        toolbar_h.setSpacing(6)
        
        # 设置按钮（左上角齿轮图标）
        self.btn_settings = QtWidgets.QPushButton("⚙️")
        self.btn_settings.setToolTip("设置")
        self.btn_settings.setMinimumHeight(36)
        self.btn_settings.setMinimumWidth(45)
        self.btn_settings.setMaximumHeight(36)
        self.btn_settings.setMaximumWidth(45)
        self.btn_settings.setStyleSheet(
            "font-size: 20px;"
            "background-color: transparent;"
            "border: none;"
            "border-radius: 8px;"
        )
        self.btn_settings.setObjectName("btn_settings")
        toolbar_h.addWidget(self.btn_settings)
        
        # 操作按钮（横向排列）
        self.btn_refresh = QtWidgets.QPushButton("刷新")
        self.btn_more = QtWidgets.QPushButton("更多")
        self.btn_up = QtWidgets.QPushButton("上级")
        self.btn_delete = QtWidgets.QPushButton("删除")
        self.btn_download = QtWidgets.QPushButton("下载")
        self.btn_share = QtWidgets.QPushButton("分享")
        self.btn_link = QtWidgets.QPushButton("显示链接")
        self.btn_upload = QtWidgets.QPushButton("上传文件")
        self.btn_mkdir = QtWidgets.QPushButton("新建文件夹")

        # 设置按钮最小宽度统一外观
        btns = [self.btn_refresh, self.btn_more, self.btn_up, self.btn_download, self.btn_link,
                self.btn_upload, self.btn_mkdir, self.btn_delete, self.btn_share]
        
        # 为每个按钮添加动画效果
        self.button_animations = {}
        for b in btns:
            b.setMinimumHeight(30)
            b.setMinimumWidth(110)
            toolbar_h.addWidget(b)
            
            # 为按钮添加悬停和点击事件，实现动画效果
            b.enterEvent = lambda event, btn=b: self.on_button_hover(btn)
            b.leaveEvent = lambda event, btn=b: self.on_button_leave(btn)
            b.pressed.connect(lambda btn=b: self.on_button_pressed(btn))
            b.released.connect(lambda btn=b: self.on_button_released(btn))
            
            # 初始化按钮动画
            animation = QtCore.QPropertyAnimation(b, b"geometry")
            animation.setDuration(100)
            self.button_animations[b] = animation

        toolbar_h.addStretch()
        right_layout.addLayout(toolbar_h)
        
        # 路径栏
        self.path_widget = QtWidgets.QWidget()
        path_h = QtWidgets.QHBoxLayout(self.path_widget)
        path_h.addWidget(QtWidgets.QLabel("路径："))
        self.lbl_path = QtWidgets.QLabel("/")
        font = self.lbl_path.font()
        font.setBold(True)
        self.lbl_path.setFont(font)
        path_h.addWidget(self.lbl_path)
        path_h.addStretch()
        right_layout.addWidget(self.path_widget)
        
        # 创建页面堆栈
        self.page_stack = QtWidgets.QStackedWidget()
        
        # 文件页面
        self.files_page = QtWidgets.QWidget()
        files_layout = QtWidgets.QVBoxLayout(self.files_page)
        files_layout.setContentsMargins(0, 0, 0, 0)
        
        # 文件列表区域（包含表格和加载动画）
        file_list_widget = QtWidgets.QWidget()
        file_list_layout = QtWidgets.QVBoxLayout(file_list_widget)
        file_list_layout.setContentsMargins(0, 0, 0, 0)
        
        # 文件列表表格
        self.table = QtWidgets.QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["", "编号", "名称", "类型", "大小"])
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.doubleClicked.connect(self.on_table_double)
        self.table.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.on_table_context_menu)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setStretchLastSection(True)
        file_list_layout.addWidget(self.table, stretch=1)
        
        # 加载动画布局
        self.loading_widget = QtWidgets.QWidget()
        loading_layout = QtWidgets.QVBoxLayout(self.loading_widget)
        loading_layout.setContentsMargins(0, 0, 0, 0)
        loading_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        
        # 加载标签
        self.loading_label = QtWidgets.QLabel()
        self.loading_label.setText("正在加载...")
        font = self.loading_label.font()
        font.setPointSize(14)
        self.loading_label.setFont(font)
        self.loading_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        loading_layout.addWidget(self.loading_label)
        
        # 旋转动画
        self.loading_spinner = QtWidgets.QLabel()
        self.loading_spinner.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        # 创建一个简单的旋转动画
        self.spinner_timer = QtCore.QTimer()
        self.spinner_angle = 0
        self.spinner_timer.timeout.connect(self.update_spinner)
        self.spinner_timer.start(50)  # 每50毫秒更新一次
        
        loading_layout.addWidget(self.loading_spinner)
        
        # 初始隐藏加载动画
        self.loading_widget.setVisible(False)
        file_list_layout.addWidget(self.loading_widget)
        
        files_layout.addWidget(file_list_widget, stretch=1)
        
        # 传输任务管理
        self.transfer_tasks = []
        self.next_task_id = 0
        self.active_tasks = {}  # 保存活动任务的引用，用于取消
        
        # 传输页面
        self.transfer_page = QtWidgets.QWidget()
        transfer_layout = QtWidgets.QVBoxLayout(self.transfer_page)
        transfer_layout.setContentsMargins(0, 0, 0, 0)
        
        # 传输页面内容
        transfer_title = QtWidgets.QLabel("传输任务")
        transfer_title.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        transfer_title.setStyleSheet("font-size: 24px; font-weight: bold; color: #334155; margin: 20px 0;")
        transfer_layout.addWidget(transfer_title)
        
        self.transfer_table = QtWidgets.QTableWidget(0, 6)
        self.transfer_table.setHorizontalHeaderLabels(["类型", "文件名", "大小", "进度", "状态", "操作"])
        self.transfer_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.transfer_table.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.transfer_table.verticalHeader().setVisible(False)
        self.transfer_table.horizontalHeader().setStretchLastSection(True)
        # 设置列宽
        self.transfer_table.setColumnWidth(0, 80)
        self.transfer_table.setColumnWidth(2, 120)
        self.transfer_table.setColumnWidth(3, 100)
        self.transfer_table.setColumnWidth(4, 100)
        self.transfer_table.setColumnWidth(5, 80)
        transfer_layout.addWidget(self.transfer_table, stretch=1)
        
        # 添加页面到堆栈
        self.page_stack.addWidget(self.files_page)
        self.page_stack.addWidget(self.transfer_page)
        
        right_layout.addWidget(self.page_stack, stretch=1)
        main_layout.addWidget(right_content, stretch=1)

        # 状态栏显示简短提示/进度
        self.status = self.statusBar()
        self.status.showMessage("准备就绪")

        # 信号连接
        self.btn_settings.clicked.connect(self.on_settings)
        self.btn_refresh.clicked.connect(lambda: self.refresh_file_list(reset_page=True))
        self.btn_more.clicked.connect(lambda: self.refresh_file_list(reset_page=False))
        self.btn_up.clicked.connect(self.on_up)
        self.btn_download.clicked.connect(self.on_download)
        self.btn_link.clicked.connect(self.on_showlink)
        self.btn_upload.clicked.connect(self.on_upload)
        self.btn_mkdir.clicked.connect(self.on_mkdir)
        self.btn_delete.clicked.connect(self.on_delete)
        self.btn_share.clicked.connect(self.on_share)
        
        # 侧边栏按钮信号
        self.btn_files.clicked.connect(lambda: self.switch_page(0))
        self.btn_transfer.clicked.connect(lambda: self.switch_page(1))
        
        # 初始化默认页面
        self.switch_page(0)

        # 启动登录流程
        self.startup_login_flow()

    def apply_blue_white_theme(self):
        """
        123云盘主题样式表 - iOS 26 Liquid Glass 液态毛玻璃效果
        """
        style = """
        /* 全局样式 */
        QWidget {
            background-color: rgba(255, 255, 255, 0.8);
            color: #1E293B;
            font-family: "SF Pro Display", "Segoe UI", "Microsoft YaHei", "PingFang SC", "Helvetica Neue", Arial;
            font-size: 13px;
        }
        
        /* 主窗口 */
        QMainWindow {
            background-color: rgba(245, 245, 247, 0.95);
        }
        
        /* 表格样式 - 液态毛玻璃效果（模拟） */
        QTableWidget {
            background-color: rgba(255, 255, 255, 0.9);
            border: 1px solid rgba(255, 255, 255, 0.8);
            border-radius: 12px;
            padding: 8px;
            gridline-color: rgba(0, 0, 0, 0.05);
        }
        
        /* 表格行样式 */
        QTableWidget::item {
            padding: 10px 6px;
            border: none;
            background-color: transparent;
            border-radius: 6px;
        }
        
        /* 表格行悬停效果 */
        QTableWidget::item:hover {
            background-color: rgba(59, 130, 246, 0.1);
        }
        
        /* 表格行选中效果 */
        QTableWidget::item:selected {
            background-color: rgba(59, 130, 246, 0.9);
            color: #FFFFFF;
        }
        
        /* 表头样式 */
        QHeaderView::section {
            background-color: rgba(255, 255, 255, 0.95);
            color: #334155;
            padding: 12px 16px;
            border: none;
            border-bottom: 1px solid rgba(0, 0, 0, 0.05);
            font-weight: 600;
            text-align: left;
            border-radius: 8px 8px 0 0;
        }
        
        QHeaderView {
            background-color: transparent;
            border: none;
        }
        
        /* 按钮样式 - 液态毛玻璃效果（模拟） */
        QPushButton {
            background-color: rgba(255, 255, 255, 0.95);
            color: #3B82F6;
            border: 1px solid rgba(59, 130, 246, 0.4);
            border-radius: 12px;
            padding: 10px 18px;
            font-weight: 500;
            font-size: 14px;
        }
        
        QPushButton:hover {
            background-color: rgba(255, 255, 255, 0.98);
            border-color: rgba(59, 130, 246, 0.6);
        }
        
        QPushButton:pressed {
            background-color: rgba(230, 240, 255, 0.95);
            border-color: rgba(59, 130, 246, 0.8);
        }
        
        QPushButton:disabled {
            background-color: rgba(240, 240, 245, 0.8);
            border-color: rgba(148, 163, 184, 0.4);
            color: rgba(148, 163, 184, 0.8);
        }
        
        /* 输入控件样式 - 液态毛玻璃效果（模拟） */
        QLineEdit, QTextEdit, QComboBox {
            background-color: rgba(255, 255, 255, 0.95);
            border: 1px solid rgba(0, 0, 0, 0.08);
            padding: 10px 14px;
            border-radius: 12px;
        }
        
        QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
            border-color: rgba(59, 130, 246, 0.6);
        }
        
        /* 状态栏样式 - 液态毛玻璃效果（模拟） */
        QStatusBar {
            background-color: rgba(255, 255, 255, 0.95);
            color: #334155;
            padding: 8px 16px;
            border-top: 1px solid rgba(0, 0, 0, 0.05);
        }
        
        /* 菜单样式 - 液态毛玻璃效果（模拟） */
        QMenu {
            background-color: rgba(255, 255, 255, 0.98);
            border: 1px solid rgba(0, 0, 0, 0.08);
            border-radius: 12px;
            padding: 8px 0;
        }
        
        QMenu::item {
            padding: 10px 24px;
            background-color: transparent;
            border: none;
            border-radius: 8px;
            margin: 2px 8px;
        }
        
        QMenu::item:selected {
            background-color: rgba(59, 130, 246, 0.15);
            color: #3B82F6;
        }
        
        /* 滚动条样式 - 液态毛玻璃效果（模拟） */
        QScrollBar {
            background-color: rgba(255, 255, 255, 0.7);
            border-radius: 10px;
            width: 10px;
            height: 10px;
        }
        
        QScrollBar::handle {
            background-color: rgba(59, 130, 246, 0.6);
            border-radius: 10px;
            min-width: 24px;
            min-height: 24px;
        }
        
        QScrollBar::handle:hover {
            background-color: rgba(59, 130, 246, 0.8);
        }
        
        QScrollBar::add-line, QScrollBar::sub-line {
            background-color: transparent;
        }
        
        /* 对话框样式 - 液态毛玻璃效果（模拟） */
        QDialog {
            background-color: rgba(255, 255, 255, 0.98);
            border: 1px solid rgba(255, 255, 255, 0.9);
            border-radius: 16px;
        }
        
        /* 分组框样式 - 液态毛玻璃效果（模拟） */
        QGroupBox {
            background-color: rgba(255, 255, 255, 0.9);
            border: 1px solid rgba(0, 0, 0, 0.08);
            border-radius: 12px;
            margin-top: 16px;
            padding: 16px;
        }
        
        QGroupBox::title {
            color: #334155;
            font-weight: 600;
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 0 12px;
        }
        
        /* 复选框样式 - 液态毛玻璃效果（模拟） */
        QCheckBox {
            spacing: 8px;
        }
        
        QCheckBox::indicator {
            width: 20px;
            height: 20px;
            border: 2px solid rgba(59, 130, 246, 0.6);
            border-radius: 6px;
            background-color: rgba(255, 255, 255, 0.95);
        }
        
        QCheckBox::indicator:checked {
            background-color: rgba(59, 130, 246, 0.95);
            border-color: rgba(59, 130, 246, 0.95);
        }
        
        /* 标签样式 */
        QLabel {
            color: #334155;
        }
        
        /* 路径标签 */
        QLabel#lbl_path {
            font-weight: 600;
            color: #3B82F6;
            font-size: 14px;
        }
        
        /* 加载动画标签 */
        QLabel#loading_label {
            color: #3B82F6;
        }
        
        /* 设置按钮特殊样式 */
        QPushButton#btn_settings {
            background-color: transparent;
            border: none;
            border-radius: 8px;
            font-size: 18px;
            padding: 6px;
            color: #3B82F6;
        }
        
        QPushButton#btn_settings:hover {
            background-color: rgba(59, 130, 246, 0.1);
        }
        """
        self.setStyleSheet(style)

    def on_settings(self):
        """打开设置对话框"""
        dlg = SettingsDialog(self)
        if dlg.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            settings = dlg.get_settings()
            # 保存设置到配置文件
            config = ConfigManager.load_config()
            config["settings"] = settings
            ConfigManager.save_config(config)
            QtWidgets.QMessageBox.information(self, "设置", "设置已保存")

    def startup_login_flow(self):
        cfg_loaded = False
        config = ConfigManager.load_config()
        if config.get("userName") and config.get("passWord"):
            try:
                self.pan = Pan123(readfile=True, input_pwd=False)
                res_code = self.pan.get_dir(save=False)[0]
                if res_code == 0:
                    cfg_loaded = True
                else:
                    cfg_loaded = False
            except Exception:
                cfg_loaded = False

        if not cfg_loaded:
            dlg = LoginDialog(self)
            if dlg.exec() != QtWidgets.QDialog.DialogCode.Accepted:
                QtWidgets.QMessageBox.information(self, "提示", "未登录，程序将退出。")
                QtCore.QTimer.singleShot(0, self.close)
                return
            self.pan = dlg.get_pan()

        self.refresh_file_list(reset_page=True)

    def prompt_selected_row(self):
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            QtWidgets.QMessageBox.information(self, "提示", "请先选择一项。")
            return None
        return rows[0].row()

    def get_file_icon(self, file_detail):
        """根据文件类型获取图标"""
        file_type = file_detail.get("Type", 0)
        file_name = file_detail.get("FileName", "")
        
        # 创建一个32x32的图标
        pixmap = QtGui.QPixmap(32, 32)
        pixmap.fill(QtCore.Qt.GlobalColor.transparent)
        painter = QtGui.QPainter(pixmap)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        
        if file_type == 1:  # 文件夹
            # 绘制文件夹图标
            painter.setBrush(QtGui.QColor(255, 193, 7))
            painter.setPen(QtGui.QColor(255, 152, 0))
            # 文件夹主体
            painter.drawRect(6, 10, 20, 16)
            # 文件夹盖子
            painter.drawRect(6, 6, 16, 8)
        else:  # 文件
            # 根据文件扩展名选择图标颜色
            ext = os.path.splitext(file_name)[1].lower()
            colors = {
                ".txt": QtGui.QColor(25, 118, 210),
                ".pdf": QtGui.QColor(211, 47, 47),
                ".doc": QtGui.QColor(33, 150, 243),
                ".docx": QtGui.QColor(33, 150, 243),
                ".xls": QtGui.QColor(76, 175, 80),
                ".xlsx": QtGui.QColor(76, 175, 80),
                ".ppt": QtGui.QColor(255, 193, 7),
                ".pptx": QtGui.QColor(255, 193, 7),
                ".jpg": QtGui.QColor(156, 39, 176),
                ".jpeg": QtGui.QColor(156, 39, 176),
                ".png": QtGui.QColor(156, 39, 176),
                ".gif": QtGui.QColor(156, 39, 176),
                ".mp3": QtGui.QColor(94, 53, 177),
                ".mp4": QtGui.QColor(233, 30, 99),
                ".zip": QtGui.QColor(121, 85, 72),
                ".rar": QtGui.QColor(121, 85, 72),
                ".7z": QtGui.QColor(121, 85, 72),
            }
            
            color = colors.get(ext, QtGui.QColor(100, 116, 139))
            painter.setBrush(color)
            painter.setPen(color.darker(120))
            
            # 绘制文件图标
            painter.drawRect(6, 8, 20, 20)
            # 绘制文件顶部的横线
            painter.setBrush(color.darker(120))
            painter.drawRect(6, 8, 20, 4)
        
        painter.end()
        return QtGui.QIcon(pixmap)
    
    def populate_table(self):
        if not self.pan:
            return
        self.table.setRowCount(0)
        
        # 逐行添加，使用定时器实现动画效果
        for i, item in enumerate(self.pan.list):
            # 使用定时器延迟添加，实现逐行出现的效果
            QtCore.QTimer.singleShot(i * 30, lambda idx=i: self._add_row(idx))

        names = getattr(self.pan, "parent_file_name_list", [])
        path = "/" + "/".join(names) if names else "/"
        self.lbl_path.setText(path)
    
    def _add_row(self, index):
        """添加行，逐行显示"""
        if index >= len(self.pan.list):
            return
            
        item = self.pan.list[index]
        row = self.table.rowCount()
        self.table.insertRow(row)
        
        # 添加文件图标
        icon = self.get_file_icon(item)
        icon_item = QtWidgets.QTableWidgetItem()
        icon_item.setIcon(icon)
        self.table.setItem(row, 0, icon_item)
        
        # 设置列宽，图标列不需要太宽
        self.table.setColumnWidth(0, 40)
        
        # 编号
        self.table.setItem(row, 1, QtWidgets.QTableWidgetItem(str(index + 1)))
        
        # 文件名
        name_item = QtWidgets.QTableWidgetItem(item.get("FileName", ""))
        # 文件夹使用粗体
        if item.get("Type", 0) == 1:
            font = name_item.font()
            font.setBold(True)
            name_item.setFont(font)
        self.table.setItem(row, 2, name_item)
        
        # 文件类型
        typ = "文件夹" if item.get("Type", 0) == 1 else "文件"
        self.table.setItem(row, 3, QtWidgets.QTableWidgetItem(typ))
        
        # 文件大小
        size = item.get("Size", 0)
        if size > 1073741824:
            s = f"{round(size / 1073741824, 2)} GB"
        elif size > 1048576:
            s = f"{round(size / 1048576, 2)} MB"
        else:
            s = f"{round(size / 1024, 2)} KB"
        self.table.setItem(row, 4, QtWidgets.QTableWidgetItem(s))

    def update_spinner(self):
        """更新旋转动画"""
        self.spinner_angle = (self.spinner_angle + 10) % 360
        pixmap = QtGui.QPixmap(32, 32)
        pixmap.fill(QtCore.Qt.GlobalColor.transparent)
        painter = QtGui.QPainter(pixmap)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        
        # 绘制旋转圆环
        pen = QtGui.QPen(QtGui.QColor(59, 130, 246), 3)
        pen.setCapStyle(QtCore.Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        rect = QtCore.QRect(4, 4, 24, 24)
        painter.drawArc(rect, (90 - self.spinner_angle) * 16, 180 * 16)
        
        painter.end()
        self.loading_spinner.setPixmap(pixmap)
    
    def refresh_file_list(self, reset_page=True):
        if not self.pan:
            QtWidgets.QMessageBox.information(self, "提示", "尚未初始化，请先登录。")
            return
        if reset_page:
            self.pan.all_file = False
            self.pan.file_page = 0
            self.pan.list = []
        
        # 显示加载动画
        self.table.setVisible(False)
        self.loading_widget.setVisible(True)
        self.status.showMessage("正在获取目录...")
        
        task = ThreadedTask(self._task_get_dir)
        task.signals.result.connect(self._after_get_dir)
        task.signals.error.connect(lambda e: self._show_error("获取目录失败: " + e))
        self.threadpool.start(task)

    def _task_get_dir(self, signals=None, task=None):
        code, _ = self.pan.get_dir(save=True)
        return code

    def _after_get_dir(self, code):
        # 隐藏加载动画，显示表格
        self.loading_widget.setVisible(False)
        self.table.setVisible(True)
        
        if code != 0:
            self.status.showMessage(f"获取目录返回码: {code}", 5000)
        else:
            self.status.showMessage("目录获取完成", 3000)
        self.populate_table()

    def on_table_double(self, index):
        row = index.row()
        typ_item = self.table.item(row, 3)
        if typ_item and typ_item.text() == "文件夹":
            try:
                # 保存要进入的文件夹编号
                self.target_folder_num = str(row + 1)
                # 添加淡出动画
                self.fade_animation = QtCore.QPropertyAnimation(self.table, b"windowOpacity")
                self.fade_animation.setDuration(200)
                self.fade_animation.setStartValue(1.0)
                self.fade_animation.setEndValue(0.0)
                self.fade_animation.finished.connect(self._after_fade_out_enter_folder)
                self.fade_animation.start()
            except Exception as e:
                self._show_error("进入文件夹失败: " + str(e))
        else:
            ret = QtWidgets.QMessageBox.question(self, "下载", "是否下载所选文件？", QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No)
            if ret == QtWidgets.QMessageBox.StandardButton.Yes:
                self.on_download()
    
    def _after_fade_out_enter_folder(self):
        """淡出动画完成后执行的操作 - 进入文件夹"""
        try:
            self.pan.cd(self.target_folder_num)
            self.populate_table()
            # 添加淡入动画
            self.fade_animation = QtCore.QPropertyAnimation(self.table, b"windowOpacity")
            self.fade_animation.setDuration(200)
            self.fade_animation.setStartValue(0.0)
            self.fade_animation.setEndValue(1.0)
            self.fade_animation.start()
        except Exception as e:
            self._show_error("进入文件夹失败: " + str(e))
    
    def on_button_hover(self, button):
        """按钮悬停效果 - 修复动画冲突"""
        # 停止当前正在运行的动画
        if button in self.button_animations:
            self.button_animations[button].stop()
        
        # 保存原始位置，用于恢复
        if not hasattr(self, 'button_original_geoms'):
            self.button_original_geoms = {}
        if button not in self.button_original_geoms:
            self.button_original_geoms[button] = button.geometry()
        
        # 创建放大动画
        scale_animation = QtCore.QPropertyAnimation(button, b"geometry")
        current_geom = button.geometry()
        original_geom = self.button_original_geoms[button]
        # 基于原始位置计算新位置，避免累积误差
        new_geom = QtCore.QRect(
            original_geom.x() - 2,
            original_geom.y() - 2,
            original_geom.width() + 4,
            original_geom.height() + 4
        )
        scale_animation.setStartValue(current_geom)
        scale_animation.setEndValue(new_geom)
        scale_animation.setDuration(150)
        scale_animation.setEasingCurve(QtCore.QEasingCurve.Type.OutQuad)
        scale_animation.start()
        
        # 保存动画引用
        self.button_animations[button] = scale_animation
    
    def on_button_leave(self, button):
        """按钮离开效果 - 修复动画冲突"""
        # 停止当前正在运行的动画
        if button in self.button_animations:
            self.button_animations[button].stop()
        
        # 恢复到原始位置
        if hasattr(self, 'button_original_geoms') and button in self.button_original_geoms:
            # 创建恢复动画
            scale_animation = QtCore.QPropertyAnimation(button, b"geometry")
            current_geom = button.geometry()
            original_geom = self.button_original_geoms[button]
            scale_animation.setStartValue(current_geom)
            scale_animation.setEndValue(original_geom)
            scale_animation.setDuration(150)
            scale_animation.setEasingCurve(QtCore.QEasingCurve.Type.OutQuad)
            scale_animation.start()
            
            # 保存动画引用
            self.button_animations[button] = scale_animation
    
    def on_button_pressed(self, button):
        """按钮按下效果 - 修复动画冲突"""
        # 停止当前正在运行的动画
        if button in self.button_animations:
            self.button_animations[button].stop()
        
        # 创建按下动画
        scale_animation = QtCore.QPropertyAnimation(button, b"geometry")
        current_geom = button.geometry()
        # 基于当前位置轻微缩小
        new_geom = QtCore.QRect(
            current_geom.x() + 1,
            current_geom.y() + 1,
            current_geom.width() - 2,
            current_geom.height() - 2
        )
        scale_animation.setStartValue(current_geom)
        scale_animation.setEndValue(new_geom)
        scale_animation.setDuration(100)
        scale_animation.setEasingCurve(QtCore.QEasingCurve.Type.InQuad)
        scale_animation.start()
        
        # 保存动画引用
        self.button_animations[button] = scale_animation
    
    def on_button_released(self, button):
        """按钮释放效果 - 修复动画冲突"""
        # 停止当前正在运行的动画
        if button in self.button_animations:
            self.button_animations[button].stop()
        
        # 恢复到原始放大状态（如果是悬停中）或原始状态
        scale_animation = QtCore.QPropertyAnimation(button, b"geometry")
        current_geom = button.geometry()
        
        if hasattr(self, 'button_original_geoms') and button in self.button_original_geoms:
            # 检查鼠标是否仍然在按钮上
            if button.underMouse():
                # 恢复到悬停放大状态
                original_geom = self.button_original_geoms[button]
                new_geom = QtCore.QRect(
                    original_geom.x() - 2,
                    original_geom.y() - 2,
                    original_geom.width() + 4,
                    original_geom.height() + 4
                )
            else:
                # 恢复到原始状态
                new_geom = self.button_original_geoms[button]
            
            scale_animation.setStartValue(current_geom)
            scale_animation.setEndValue(new_geom)
            scale_animation.setDuration(100)
            scale_animation.setEasingCurve(QtCore.QEasingCurve.Type.OutQuad)
            scale_animation.start()
            
            # 保存动画引用
            self.button_animations[button] = scale_animation

    def on_table_context_menu(self, pos):
        row = self.table.indexAt(pos).row()
        if row < 0:
            return
        menu = QtWidgets.QMenu()
        a_download = menu.addAction("下载")
        a_link = menu.addAction("显示链接")
        a_delete = menu.addAction("删除")
        a_share = menu.addAction("分享")
        action = menu.exec(self.table.viewport().mapToGlobal(pos))
        self.table.selectRow(row)
        if action == a_download:
            self.on_download()
        elif action == a_link:
            self.on_showlink()
        elif action == a_delete:
            self.on_delete()
        elif action == a_share:
            self.on_share()

    def on_up(self):
        if not self.pan:
            return
        try:
            # 添加淡出动画
            self.fade_animation = QtCore.QPropertyAnimation(self.table, b"windowOpacity")
            self.fade_animation.setDuration(200)
            self.fade_animation.setStartValue(1.0)
            self.fade_animation.setEndValue(0.0)
            self.fade_animation.finished.connect(self._after_fade_out_up)
            self.fade_animation.start()
        except Exception as e:
            self._show_error("返回上级失败: " + str(e))
    
    def _after_fade_out_up(self):
        """淡出动画完成后执行的操作 - 返回上级"""
        try:
            self.pan.cd("..")
            self.populate_table()
            # 添加淡入动画
            self.fade_animation = QtCore.QPropertyAnimation(self.table, b"windowOpacity")
            self.fade_animation.setDuration(200)
            self.fade_animation.setStartValue(0.0)
            self.fade_animation.setEndValue(1.0)
            self.fade_animation.start()
        except Exception as e:
            self._show_error("返回上级失败: " + str(e))
    
    def save_original_position(self, button):
        """保存按钮的原始位置"""
        self.sidebar_original_geoms[button] = button.geometry()
    
    def switch_page(self, page_index):
        """切换页面"""
        # 切换堆栈页面
        self.page_stack.setCurrentIndex(page_index)
        
        # 更新按钮样式
        for i, btn in enumerate(self.sidebar_buttons):
            if i == page_index:
                btn.setStyleSheet(
                    "font-size: 16px; text-align: left; padding-left: 20px;"
                    "background-color: rgba(59, 130, 246, 0.9);"
                    "color: white; border-radius: 12px;"
                    "border: none;"
                )
            else:
                btn.setStyleSheet(
                    "font-size: 16px; text-align: left; padding-left: 20px;"
                    "background-color: transparent; color: #334155;"
                    "border-radius: 12px;"
                    "border: none;"
                )
        
        # 根据页面显示/隐藏路径栏和相关按钮
        if page_index == 0:  # 文件页面
            self.path_widget.setVisible(True)
            self.btn_refresh.setVisible(True)
            self.btn_more.setVisible(True)
            self.btn_up.setVisible(True)
            self.btn_delete.setVisible(True)
            self.btn_download.setVisible(True)
            self.btn_share.setVisible(True)
            self.btn_link.setVisible(True)
            self.btn_upload.setVisible(True)
            self.btn_mkdir.setVisible(True)
        else:  # 传输页面
            self.path_widget.setVisible(False)
            self.btn_refresh.setVisible(False)
            self.btn_more.setVisible(False)
            self.btn_up.setVisible(False)
            self.btn_delete.setVisible(False)
            self.btn_download.setVisible(False)
            self.btn_share.setVisible(False)
            self.btn_link.setVisible(False)
            self.btn_upload.setVisible(False)
            self.btn_mkdir.setVisible(False)
    
    def on_sidebar_button_hover(self, button):
        """侧边栏按钮悬停效果"""
        # 停止当前正在运行的动画
        if button in self.sidebar_animations:
            self.sidebar_animations[button].stop()
        
        # 获取原始位置
        if button not in self.sidebar_original_geoms:
            self.save_original_position(button)
        original_geom = self.sidebar_original_geoms[button]
        
        # 创建缩放动画
        scale_animation = QtCore.QPropertyAnimation(button, b"geometry")
        scale_animation.setStartValue(button.geometry())
        scale_animation.setEndValue(QtCore.QRect(
            original_geom.x() - 5,
            original_geom.y() - 2,
            original_geom.width() + 10,
            original_geom.height() + 4
        ))
        scale_animation.setDuration(150)
        scale_animation.setEasingCurve(QtCore.QEasingCurve.Type.OutQuad)
        scale_animation.start()
        
        # 保存动画引用
        self.sidebar_animations[button] = scale_animation
    
    def on_sidebar_button_leave(self, button):
        """侧边栏按钮离开效果"""
        # 停止当前正在运行的动画
        if button in self.sidebar_animations:
            self.sidebar_animations[button].stop()
        
        # 获取原始位置
        if button not in self.sidebar_original_geoms:
            self.save_original_position(button)
        original_geom = self.sidebar_original_geoms[button]
        
        # 创建恢复动画
        scale_animation = QtCore.QPropertyAnimation(button, b"geometry")
        scale_animation.setStartValue(button.geometry())
        scale_animation.setEndValue(original_geom)
        scale_animation.setDuration(150)
        scale_animation.setEasingCurve(QtCore.QEasingCurve.Type.OutQuad)
        scale_animation.start()
        
        # 保存动画引用
        self.sidebar_animations[button] = scale_animation
    
    def on_sidebar_button_pressed(self, button):
        """侧边栏按钮按下效果"""
        # 改变背景色
        button.setStyleSheet(
            button.styleSheet().replace(
                "background-color: rgba(59, 130, 246, 0.9);",
                "background-color: rgba(37, 99, 235, 0.9);"
            ).replace(
                "background-color: transparent;",
                "background-color: rgba(59, 130, 246, 0.1);"
            )
        )
    
    def on_sidebar_button_released(self, button):
        """侧边栏按钮释放效果"""
        # 恢复背景色
        if button == self.btn_files:
            if self.page_stack.currentIndex() == 0:
                button.setStyleSheet(
                    "font-size: 16px; text-align: left; padding-left: 20px;"
                    "background-color: rgba(59, 130, 246, 0.9);"
                    "color: white; border-radius: 12px;"
                    "border: none;"
                )
            else:
                button.setStyleSheet(
                    "font-size: 16px; text-align: left; padding-left: 20px;"
                    "background-color: transparent; color: #334155;"
                    "border-radius: 12px;"
                    "border: none;"
                )
        elif button == self.btn_transfer:
            if self.page_stack.currentIndex() == 1:
                button.setStyleSheet(
                    "font-size: 16px; text-align: left; padding-left: 20px;"
                    "background-color: rgba(59, 130, 246, 0.9);"
                    "color: white; border-radius: 12px;"
                    "border: none;"
                )
            else:
                button.setStyleSheet(
                    "font-size: 16px; text-align: left; padding-left: 20px;"
                    "background-color: transparent; color: #334155;"
                    "border-radius: 12px;"
                    "border: none;"
                )
    
    def add_transfer_task(self, task_type, file_name, file_size):
        """添加传输任务到列表和表格"""
        task_id = self.next_task_id
        self.next_task_id += 1
        
        # 创建任务对象
        task = {
            "id": task_id,
            "type": task_type,  # "下载" 或 "上传"
            "file_name": file_name,
            "file_size": file_size,
            "progress": 0,
            "status": "等待中",
            "file_path": "",  # 用于保存下载文件路径，便于取消时删除
            "threaded_task": None  # 保存线程任务引用
        }
        
        # 添加到任务列表
        self.transfer_tasks.append(task)
        
        # 添加到表格
        row = self.transfer_table.rowCount()
        self.transfer_table.insertRow(row)
        
        # 设置表格内容
        self.transfer_table.setItem(row, 0, QtWidgets.QTableWidgetItem(task_type))
        self.transfer_table.setItem(row, 1, QtWidgets.QTableWidgetItem(file_name))
        self.transfer_table.setItem(row, 2, QtWidgets.QTableWidgetItem(self.format_file_size(file_size)))
        self.transfer_table.setItem(row, 3, QtWidgets.QTableWidgetItem("0%"))
        self.transfer_table.setItem(row, 4, QtWidgets.QTableWidgetItem("等待中"))
        
        # 添加取消按钮
        cancel_btn = QtWidgets.QPushButton("取消")
        cancel_btn.setStyleSheet(
            "background-color: rgba(239, 68, 68, 0.1);"
            "color: #EF4444;"
            "border: 1px solid rgba(239, 68, 68, 0.3);"
            "border-radius: 8px;"
            "padding: 4px 12px;"
            "font-size: 12px;"
        )
        cancel_btn.clicked.connect(lambda _, tid=task_id: self.cancel_transfer_task(tid))
        self.transfer_table.setCellWidget(row, 5, cancel_btn)
        
        return task_id
    
    def update_transfer_task(self, task_id, progress, status):
        """更新传输任务的进度和状态"""
        # 查找任务
        for i, task in enumerate(self.transfer_tasks):
            if task["id"] == task_id:
                # 更新任务对象
                task["progress"] = progress
                task["status"] = status
                
                # 更新表格
                self.transfer_table.setItem(i, 3, QtWidgets.QTableWidgetItem(f"{progress}%"))
                self.transfer_table.setItem(i, 4, QtWidgets.QTableWidgetItem(status))
                break
    
    def cancel_transfer_task(self, task_id):
        """取消传输任务"""
        # 查找任务
        for i, task in enumerate(self.transfer_tasks):
            if task["id"] == task_id:
                # 取消线程任务
                if task.get("threaded_task"):
                    task["threaded_task"].cancel()
                
                # 如果是下载任务，删除临时文件
                if task["type"] == "下载" and task.get("file_path") and os.path.exists(task["file_path"]):
                    try:
                        os.remove(task["file_path"])
                        # 也检查是否有最终文件存在（如果下载已完成但未清理）
                        final_path = task["file_path"].replace(".123pan", "")
                        if os.path.exists(final_path):
                            os.remove(final_path)
                    except Exception as e:
                        print(f"删除文件失败: {e}")
                
                # 更新任务状态
                task["status"] = "已取消"
                task["progress"] = 0
                self.transfer_table.setItem(i, 3, QtWidgets.QTableWidgetItem("0%"))
                self.transfer_table.setItem(i, 4, QtWidgets.QTableWidgetItem("已取消"))
                
                # 移除取消按钮
                widget = self.transfer_table.cellWidget(i, 5)
                if widget:
                    widget.setVisible(False)
                
                # 从活动任务列表中移除
                if task_id in self.active_tasks:
                    del self.active_tasks[task_id]
                
                break
    
    def remove_transfer_task(self, task_id):
        """移除传输任务"""
        # 查找任务
        for i, task in enumerate(self.transfer_tasks):
            if task["id"] == task_id:
                # 从列表中移除
                self.transfer_tasks.pop(i)
                # 从表格中移除
                self.transfer_table.removeRow(i)
                # 从活动任务列表中移除
                if task_id in self.active_tasks:
                    del self.active_tasks[task_id]
                break
    
    def format_file_size(self, size):
        """格式化文件大小"""
        if size > 1073741824:
            return f"{round(size / 1073741824, 2)} GB"
        elif size > 1048576:
            return f"{round(size / 1048576, 2)} MB"
        elif size > 1024:
            return f"{round(size / 1024, 2)} KB"
        else:
            return f"{size} B"

    def get_selected_detail(self):
        row = self.prompt_selected_row()
        if row is None:
            return None, None
        try:
            # 直接使用行索引作为文件索引，更可靠
            if not self.pan or row < 0 or row >= len(self.pan.list):
                self._show_error("无效的选择行")
                return None, None
            return row, self.pan.list[row]
        except Exception as e:
            self._show_error(f"获取选中文件失败: {str(e)}")
            return None, None

    def on_download(self):
        file_index, file_detail = self.get_selected_detail()
        if file_detail is None:
            return
        
        # 获取设置
        ask_location = ConfigManager.get_setting("askDownloadLocation", True)
        default_path = ConfigManager.get_setting("defaultDownloadPath", 
                                                os.path.join(os.path.expanduser("~"), "Downloads"))
        
        download_dir = default_path
        if ask_location:
            download_dir = QtWidgets.QFileDialog.getExistingDirectory(
                self, "选择下载文件夹", default_path
            )
            if not download_dir:
                return
        
        file_name = file_detail.get("FileName", "未知文件")
        file_size = file_detail.get("Size", 0)
        
        # 添加传输任务
        task_id = self.add_transfer_task("下载", file_name, file_size)
        
        self.status.showMessage("正在解析下载链接...")
        task = ThreadedTask(self._task_get_download_and_stream, file_index, download_dir, task_id)
        
        # 保存任务对象引用
        for i, t in enumerate(self.transfer_tasks):
            if t["id"] == task_id:
                self.transfer_tasks[i]["threaded_task"] = task
                break
        
        self.active_tasks[task_id] = task
        
        task.signals.progress.connect(lambda p, tid=task_id: (
            self.status.showMessage(f"下载进度: {p}%", 2000),
            self.update_transfer_task(tid, p, "下载中")
        ))
        def on_task_finished(tid):
            if tid in self.active_tasks:
                del self.active_tasks[tid]
        
        task.signals.result.connect(lambda r, tid=task_id: (
            self.status.showMessage("下载完成: " + str(r), 5000),
            self.update_transfer_task(tid, 100, "已完成"),
            on_task_finished(tid)
        ))
        task.signals.error.connect(lambda e, tid=task_id: (
            self._show_error("下载失败: " + e),
            self.update_transfer_task(tid, 0, "失败"),
            on_task_finished(tid)
        ))
        task.signals.finished.connect(lambda tid=task_id: on_task_finished(tid))
        self.threadpool.start(task)

    def _task_get_download_and_stream(self, file_index, download_dir, task_id, signals=None, task=None):
        file_detail = self.pan.list[file_index]
        if file_detail["Type"] == 1:
            redirect_url = self.pan.link_by_fileDetail(file_detail, showlink=False)
        else:
            redirect_url = self.pan.link_by_number(file_index, showlink=False)
        if isinstance(redirect_url, int):
            raise RuntimeError("获取下载链接失败，返回码: " + str(redirect_url))
        if file_detail["Type"] == 1:
            fname = file_detail["FileName"] + ".zip"
        else:
            fname = file_detail["FileName"]
        out_path = os.path.join(download_dir, fname)
        temp = out_path + ".123pan"
        
        # 保存文件路径到任务对象
        for i, t in enumerate(self.transfer_tasks):
            if t["id"] == task_id:
                self.transfer_tasks[i]["file_path"] = temp
                break
        
        if os.path.exists(out_path):
            reply = QtWidgets.QMessageBox.question(None, "文件已存在", f"{fname} 已存在，是否覆盖？", QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No)
            if reply == QtWidgets.QMessageBox.StandardButton.No:
                return "已取消"
        with requests.get(redirect_url, stream=True, timeout=30) as r:
            r.raise_for_status()
            total = int(r.headers.get("Content-Length", 0) or 0)
            done = 0
            with open(temp, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    # 检查是否被取消
                    if task and task.is_cancelled:
                        f.close()
                        # 删除临时文件
                        if os.path.exists(temp):
                            os.remove(temp)
                        return "已取消"
                    if chunk:
                        f.write(chunk)
                        done += len(chunk)
                        if total and signals:
                            signals.progress.emit(int(done * 100 / total))
            if task and task.is_cancelled:
                # 删除临时文件
                if os.path.exists(temp):
                    os.remove(temp)
                return "已取消"
            os.replace(temp, out_path)
        return out_path

    def on_showlink(self):
        file_index, file_detail = self.get_selected_detail()
        if file_detail is None:
            return
        try:
            # 直接调用获取链接，不使用线程，避免参数传递问题
            url = self._task_get_link(file_index)
            self._after_get_link(url)
        except Exception as e:
            self._show_error(f"获取链接失败: {str(e)}")

    def _task_get_link(self, file_index, signals=None, task=None):
        try:
            url = self.pan.link_by_number(file_index, showlink=False)
            return url
        except Exception as e:
            return f"获取链接失败: {str(e)}"

    def _after_get_link(self, url):
        if isinstance(url, int):
            self._show_error("获取链接失败，返回码: " + str(url))
            return
        dlg = QtWidgets.QDialog(self)
        dlg.setWindowTitle("下载链接")
        dlg.resize(700, 140)
        v = QtWidgets.QVBoxLayout(dlg)
        te = QtWidgets.QTextEdit()
        te.setReadOnly(True)
        te.setPlainText(url)
        v.addWidget(te)
        h = QtWidgets.QHBoxLayout()
        btn_copy = QtWidgets.QPushButton("复制到剪贴板")
        btn_copy.clicked.connect(lambda: QtWidgets.QApplication.clipboard().setText(url))
        btn_close = QtWidgets.QPushButton("关闭")
        btn_close.clicked.connect(dlg.accept)
        h.addStretch()
        h.addWidget(btn_copy)
        h.addWidget(btn_close)
        v.addLayout(h)
        dlg.exec()

    def on_upload(self):
        if not self.pan:
            QtWidgets.QMessageBox.information(self, "提示", "请先登录。")
            return
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "选择要上传的文件", os.path.expanduser("~"))
        if not path:
            return
        fname = os.path.basename(path)
        file_size = os.path.getsize(path)
        same = [i for i in self.pan.list if i.get("FileName") == fname]
        dup_choice = 1
        if same:
            text, ok = QtWidgets.QInputDialog.getText(self, "同名文件", "检测到同名文件，输入行为：1 覆盖；2 保留两者；0 取消（默认1）", text="1")
            if not ok:
                return
            if text.strip() not in ("0", "1", "2"):
                QtWidgets.QMessageBox.information(self, "提示", "无效的选择，已取消")
                return
            if text.strip() == "0":
                return
            dup_choice = int(text.strip())
        
        # 添加传输任务
        task_id = self.add_transfer_task("上传", fname, file_size)
        
        task = ThreadedTask(self._task_upload_file, path, dup_choice, task_id)
        
        # 保存任务对象引用
        for i, t in enumerate(self.transfer_tasks):
            if t["id"] == task_id:
                self.transfer_tasks[i]["threaded_task"] = task
                break
        
        self.active_tasks[task_id] = task
        
        def on_task_finished(tid):
            if tid in self.active_tasks:
                del self.active_tasks[tid]
        
        task.signals.progress.connect(lambda p, tid=task_id: (
            self.status.showMessage(f"上传进度: {p}%", 2000),
            self.update_transfer_task(tid, p, "上传中")
        ))
        task.signals.result.connect(lambda r, tid=task_id: (
            self.status.showMessage("上传完成", 3000),
            self.update_transfer_task(tid, 100, "已完成"),
            self.refresh_file_list(reset_page=True),
            on_task_finished(tid)
        ))
        task.signals.error.connect(lambda e, tid=task_id: (
            self._show_error("上传失败: " + e),
            self.update_transfer_task(tid, 0, "失败"),
            on_task_finished(tid)
        ))
        task.signals.finished.connect(lambda tid=task_id: on_task_finished(tid))
        self.threadpool.start(task)

    def _task_upload_file(self, file_path, dup_choice, task_id, signals=None, task=None):
        file_path = file_path.replace('"', "").replace("\\", "/")
        file_name = os.path.basename(file_path)
        if not os.path.exists(file_path):
            raise RuntimeError("文件不存在")
        if os.path.isdir(file_path):
            raise RuntimeError("不支持文件夹上传")
        fsize = os.path.getsize(file_path)
        
        # 检查是否被取消
        if task and task.is_cancelled:
            return "已取消"
        
        md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            while True:
                data = f.read(64 * 1024)
                if not data:
                    break
                md5.update(data)
                # 检查是否被取消
                if task and task.is_cancelled:
                    return "已取消"
        readable_hash = md5.hexdigest()
        
        # 检查是否被取消
        if task and task.is_cancelled:
            return "已取消"
        list_up_request = {
            "driveId": 0,
            "etag": readable_hash,
            "fileName": file_name,
            "parentFileId": self.pan.parent_file_id,
            "size": fsize,
            "type": 0,
            "duplicate": 0,
        }
        url = "https://www.123pan.com/b/api/file/upload_request"
        headers = self.pan.header_logined.copy()
        res = requests.post(url, headers=headers, data=list_up_request, timeout=30)
        res_json = res.json()
        code = res_json.get("code", -1)
        if code == 5060:
            list_up_request["duplicate"] = dup_choice
            res = requests.post(url, headers=headers, data=json.dumps(list_up_request), timeout=30)
            res_json = res.json()
            code = res_json.get("code", -1)
        if code != 0:
            raise RuntimeError("上传请求失败: " + json.dumps(res_json, ensure_ascii=False))
        data = res_json["data"]
        if data.get("Reuse"):
            return "复用上传成功"
        bucket = data["Bucket"]
        storage_node = data["StorageNode"]
        upload_key = data["Key"]
        upload_id = data["UploadId"]
        up_file_id = data["FileId"]
        block_size = 5242880
        total_sent = 0
        part_number = 1
        with open(file_path, "rb") as f:
            while True:
                block = f.read(block_size)
                if not block:
                    break
                get_link_data = {
                    "bucket": bucket,
                    "key": upload_key,
                    "partNumberEnd": part_number + 1,
                    "partNumberStart": part_number,
                    "uploadId": upload_id,
                    "StorageNode": storage_node,
                }
                get_link_url = "https://www.123pan.com/b/api/file/s3_repare_upload_parts_batch"
                get_link_res = requests.post(get_link_url, headers=headers, data=json.dumps(get_link_data), timeout=30)
                get_link_res_json = get_link_res.json()
                if get_link_res_json.get("code", -1) != 0:
                    raise RuntimeError("获取上传链接失败: " + json.dumps(get_link_res_json, ensure_ascii=False))
                upload_url = get_link_res_json["data"]["presignedUrls"][str(part_number)]
                requests.put(upload_url, data=block, timeout=60)
                total_sent += len(block)
                if signals and fsize:
                    signals.progress.emit(int(total_sent * 100 / fsize))
                part_number += 1
        uploaded_list_url = "https://www.123pan.com/b/api/file/s3_list_upload_parts"
        uploaded_comp_data = {"bucket": bucket, "key": upload_key, "uploadId": upload_id, "storageNode": storage_node}
        requests.post(uploaded_list_url, headers=headers, data=json.dumps(uploaded_comp_data), timeout=30)
        compmultipart_up_url = "https://www.123pan.com/b/api/file/s3_complete_multipart_upload"
        requests.post(compmultipart_up_url, headers=headers, data=json.dumps(uploaded_comp_data), timeout=30)
        if fsize > 64 * 1024 * 1024:
            time.sleep(3)
        close_up_session_url = "https://www.123pan.com/b/api/file/upload_complete"
        close_up_session_data = {"fileId": up_file_id}
        close_res = requests.post(close_up_session_url, headers=headers, data=json.dumps(close_up_session_data), timeout=30)
        cr = close_res.json()
        if cr.get("code", -1) != 0:
            raise RuntimeError("上传完成确认失败: " + json.dumps(cr, ensure_ascii=False))
        return up_file_id

    def on_mkdir(self):
        if not self.pan:
            QtWidgets.QMessageBox.information(self, "提示", "请先登录。")
            return
        name, ok = QtWidgets.QInputDialog.getText(self, "新建文件夹", "请输入文件夹名称：")
        if not ok or not name.strip():
            return
        res = self.pan.mkdir(name.strip(), remakedir=False)
        self.status.showMessage("创建完成", 3000)
        self.refresh_file_list(reset_page=True)

    def on_delete(self):
        file_index, file_detail = self.get_selected_detail()
        if file_detail is None:
            return
        r = QtWidgets.QMessageBox.question(self, "删除确认", f"确认将 '{file_detail['FileName']}' 删除？", QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No)
        if r == QtWidgets.QMessageBox.StandardButton.No:
            return
        try:
            self.pan.delete_file(file_index, by_num=True, operation=True)
            self.status.showMessage("删除请求已发送", 3000)
            self.refresh_file_list(reset_page=True)
        except Exception as e:
            self._show_error("删除失败: " + str(e))

    def on_share(self):
        file_index, file_detail = self.get_selected_detail()
        if file_detail is None:
            return
        pwd, ok = QtWidgets.QInputDialog.getText(self, "分享", "提取码（留空则没有提取码）：")
        if not ok:
            return
        file_id_list = str(file_detail["FileId"])
        data = {
            "driveId": 0,
            "expiration": "2099-12-12T08:00:00+08:00",
            "fileIdList": file_id_list,
            "shareName": "123云盘分享",
            "sharePwd": pwd or "",
            "event": "shareCreate"
        }
        headers = self.pan.header_logined.copy()
        try:
            r = requests.post("https://www.123pan.com/a/api/share/create", headers=headers, data=json.dumps(data), timeout=30)
            jr = r.json()
            if jr.get("code", -1) != 0:
                self._show_error("分享失败: " + jr.get("message", str(jr)))
                return
            share_key = jr["data"]["ShareKey"]
            share_url = "https://www.123pan.com/s/" + share_key
            QtWidgets.QMessageBox.information(self, "分享链接", f"{share_url}\n提取码：{pwd or '(无)'}")
        except Exception as e:
            self._show_error("分享异常: " + str(e))

    def _show_error(self, msg):
        QtWidgets.QMessageBox.critical(self, "错误", msg)
        self.status.showMessage(msg, 8000)

    def closeEvent(self, event):
        try:
            if self.pan and getattr(self.pan, "user_name", "") and getattr(self.pan, "password", ""):
                self.pan.save_file()
        except Exception:
            pass
        event.accept()

def main():
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

