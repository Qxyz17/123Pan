from PyQt5 import QtCore, QtGui, QtWidgets
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

# 配置文件路径
if platform.system() == 'Windows':
    CONFIG_DIR = os.path.join(os.environ.get('APPDATA', ''), 'Qxyz17', '123pan')
else:
    CONFIG_DIR = os.path.join(os.path.expanduser('~'), '.config', 'Qxyz17', '123pan')
CONFIG_FILE = os.path.join(CONFIG_DIR, 'config.json')

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
                print(f"加载配置失败: {e}")
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
            print(f"保存配置失败: {e}")
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
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)
        
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
            input_pwd=True,
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

        self.download_mode = 1
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
                print("读取已禁用，用户名或密码为空")
                if input_pwd:
                    user_name = input("请输入用户名:")
                    pass_word = input("请输入密码:")
                else:
                    raise Exception("用户名或密码为空：读取禁用时，userName和passWord不能为空")
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
        data = {"type": 1, "passport": self.user_name, "password": self.password}
        login_res = requests.post(
            "https://www.123pan.com/b/api/user/sign_in",
            headers=self.header_logined,
            data=data,
        )

        res_sign = login_res.json()
        res_code_login = res_sign["code"]
        if res_code_login != 200:
            print("code = 1 Error:" + str(res_code_login))
            print(res_sign.get("message", ""))
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
        """保存配置到统一配置文件"""
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
            print("账号已保存")
        except Exception as e:
            print("保存账号失败:", e)

    def get_dir(self, save=True):
        return self.get_dir_by_id(self.parent_file_id, save)

    # 按页（非123页数）读取文件
    # all = True 强制获取所有文件
    def get_dir_by_id(self, file_id, save=True, all=False, limit=100):
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
                print("连接失败")
                return -1, []
            text = a.json()
            res_code_getdir = text["code"]
            if res_code_getdir != 0:
                print("code = 2 Error:" + str(res_code_getdir))
                print(text.get("message", ""))
                return res_code_getdir, []
            lists_page = text["data"]["InfoList"]
            lists += lists_page
            total = text["data"]["Total"]
            lenth_now += len(lists_page)
            page += 1
            times += 1
            if times % 5 == 0:
                print("警告：文件夹内文件过多：" + str(lenth_now) + "/" + str(total))
                print("为防止对服务器造成影响，暂停3秒")
                print("请耐心等待！")
                time.sleep(3)

        if lenth_now < total:
            print("文件夹内文件过多：" + str(lenth_now) + "/" + str(total))
            self.all_file = False
        else:
            self.all_file = True
        self.total = total
        self.file_page += 1
        if save:
            self.list = self.list + lists

        return res_code_getdir, lists

    def show(self):
        print("--------------------")
        for i in self.list:
            file_size = i["Size"]
            if file_size > 1073741824:
                download_size_print = str(round(file_size / 1073741824, 2)).ljust(6) + " GB"
            elif file_size > 1048576:
                download_size_print = str(round(file_size / 1048576, 2)).ljust(6) + " MB"
            else:
                download_size_print = str(round(file_size / 1024, 2)).ljust(6) + " KB"

            if i["Type"] == 0:
                print(
                    "\033[33m" + "编号:",
                    self.list.index(i) + 1,
                    "\033[0m \t\t" + download_size_print + "\t\t\033[36m",
                    i["FileName"],
                    "\033[0m",
                )
            elif i["Type"] == 1:
                print(
                    "\033[35m" + "编号:",
                    self.list.index(i) + 1,
                    " \t\t\033[36m",
                    i["FileName"],
                    "\033[0m",
                )
        if not self.all_file:
            print("剩余" + str(self.total - len(self.list)) + "个文件未获取")
            print("输入more继续获取")
        print("--------------------")

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
            print("code = 3 Error:" + str(res_code_download))
            print(link_res_json.get("message", ""))
            return res_code_download
        down_load_url = link_res.json()["data"]["DownloadUrl"]
        next_to_get = requests.get(down_load_url, timeout=10, allow_redirects=False).text
        url_pattern = re.compile(r"href='(https?://[^']+)'")
        redirect_url = url_pattern.findall(next_to_get)[0]
        if showlink:
            print(redirect_url)

        return redirect_url

    def download(self, file_number, download_path="download"):
        file_detail = self.list[file_number]
        if file_detail["Type"] == 1:
            print("开始下载")
            file_name = file_detail["FileName"] + ".zip"
        else:
            file_name = file_detail["FileName"]  # 文件名

        down_load_url = self.link_by_number(file_number, showlink=False)
        if type(down_load_url) == int:
            return
        self.download_from_url(down_load_url, file_name, download_path)

    def download_from_url(self, url, file_name, download_path="download"):
        if os.path.exists(download_path + "/" + file_name):
            if self.download_mode == 4:
                print("文件 " + file_name + "已跳过")
                return
            print("文件 " + file_name + " 已存在，是否要覆盖？")
            sure_download = input("输入1覆盖，2跳过，3全部覆盖，4全部跳过：")
            if sure_download == "2":
                return
            elif sure_download == "3":
                self.download_mode = 3
            elif sure_download == "4":
                self.download_mode = 4
                print("已跳过")
                return
            else:
                os.remove(download_path + "/" + file_name)

        if not os.path.exists(download_path):
            print("文件夹不存在，创建文件夹")
            os.makedirs(download_path)
        down = requests.get(url, stream=True, timeout=10)

        file_size = int(down.headers.get("Content-Length", 0) or 0)  # 文件大小
        content_size = int(file_size)  # 文件总大小
        data_count = 0  # 当前已传输的大小
        if file_size > 1048576:
            size_print_download = str(round(file_size / 1048576, 2)) + "MB"
        else:
            size_print_download = str(round(file_size / 1024, 2)) + "KB"
        print(file_name + "    " + size_print_download)
        time1 = time.time()
        time_temp = time1
        data_count_temp = 0
        # 以.123pan后缀下载，下载完成重命名，防止下载中断
        with open(download_path + "/" + file_name + ".123pan", "wb") as f:
            for i in down.iter_content(1024):
                f.write(i)
                done_block = int((data_count / content_size) * 50) if content_size else 0
                data_count = data_count + len(i)
                # 实时进度条进度
                now_jd = (data_count / content_size) * 100 if content_size else 0
                # 测速
                time1 = time.time()
                pass_time = time1 - time_temp
                if pass_time > 1:
                    time_temp = time1
                    pass_data = int(data_count) - int(data_count_temp)
                    data_count_temp = data_count
                    speed = pass_data / int(pass_time)
                    speed_m = speed / 1048576
                    if speed_m > 1:
                        speed_print = str(round(speed_m, 2)) + "MB/S"
                    else:
                        speed_print = str(round(speed_m * 1024, 2)) + "KB/S"
                    print(
                        "\r [%s%s] %d%%  %s"
                        % (
                            done_block * "█",
                            " " * (50 - 1 - done_block),
                            now_jd,
                            speed_print,
                        ),
                        end="",
                    )
                elif data_count == content_size:
                    print("\r [%s%s] %d%%  %s" % (50 * "█", "", 100, ""), end="")
            print("\nok")

        os.rename(download_path + "/" + file_name + ".123pan", download_path + "/" + file_name)

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
            print("不是文件夹")
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
        # operation = 'true' 删除 ， operation = 'false' 恢复
        if by_num:
            print(file)
            if not str(file).isdigit():
                print("请输入数字")
                return -1
            if 0 <= file < len(self.list):
                file_detail = self.list[file]
            else:
                print("不在合理范围内")
                return
        else:
            if file in self.list:
                file_detail = file
            else:
                print("文件不存在")
                return
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

    def share(self):
        file_id_list = ""
        share_name_list = []
        add = "1"
        while str(add) == "1":
            share_num = input("分享文件的编号：")
            num_test2 = share_num.isdigit()
            if num_test2:
                share_num = int(share_num)
                if 0 < share_num < len(self.list) + 1:
                    share_id = self.list[int(share_num) - 1]["FileId"]
                    share_name = self.list[int(share_num) - 1]["FileName"]
                    share_name_list.append(share_name)
                    print(share_name_list)
                    file_id_list = file_id_list + str(share_id) + ","
                    add = input("输入1添加文件，0发起分享，其他取消")
            else:
                print("请输入数字，，")
                add = "1"
        if str(add) == "0":
            share_pwd = input("提取码，不设留空：")
            file_id_list = file_id_list.strip(",")
            data = {
                "driveId": 0,
                "expiration": "2099-12-12T08:00:00+08:00",
                "fileIdList": file_id_list,
                "shareName": "123云盘分享",
                "sharePwd": share_pwd,
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
                print(share_res_json.get("message", ""))
                print("分享失败")
                return
            message = share_res_json.get("message", "")
            print(message)
            share_key = share_res_json["data"]["ShareKey"]
            share_url = "https://www.123pan.com/s/" + share_key
            print("分享链接：\n" + share_url + "提取码：" + share_pwd)
        else:
            print("退出分享")

    def up_load(self, file_path):
        file_path = file_path.replace('"', "")
        file_path = file_path.replace("\\", "/")
        file_name = file_path.split("/")[-1]
        print("文件名:", file_name)
        if not os.path.exists(file_path):
            print("文件不存在，请检查路径是否正确")
            return
        if os.path.isdir(file_path):
            print("暂不支持文件夹上传")
            return
        fsize = os.path.getsize(file_path)
        with open(file_path, "rb") as f:
            md5 = hashlib.md5()
            while True:
                data = f.read(64 * 1024)
                if not data:
                    break
                md5.update(data)
            readable_hash = md5.hexdigest()

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
            sure_upload = input("检测到1个同名文件,输入1覆盖，2保留两者，0取消：")
            if sure_upload == "1":
                list_up_request["duplicate"] = 1

            elif sure_upload == "2":
                list_up_request["duplicate"] = 2
            else:
                print("取消上传")
                return
            up_res = requests.post(
                "https://www.123pan.com/b/api/file/upload_request",
                headers=self.header_logined,
                data=json.dumps(list_up_request),
                timeout=10
            )
            up_res_json = up_res.json()
        res_code_up = up_res_json.get("code", -1)
        if res_code_up == 0:
            reuse = up_res_json["data"].get("Reuse", False)
            if reuse:
                print("上传成功，文件已MD5复用")
                return
        else:
            print(up_res_json)
            print("上传请求失败")
            return

        bucket = up_res_json["data"]["Bucket"]
        storage_node = up_res_json["data"]["StorageNode"]
        upload_key = up_res_json["data"]["Key"]
        upload_id = up_res_json["data"]["UploadId"]
        up_file_id = up_res_json["data"]["FileId"]  # 上传文件的fileId,完成上传后需要用到
        print("上传文件的fileId:", up_file_id)

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
        if res_code_up == 0:
            pass
        else:
            print(start_data)
            print(start_res_json)
            print("获取传输列表失败")
            return

        # 分块，每一块取一次链接，依次上传
        block_size = 5242880
        with open(file_path, "rb") as f:
            part_number_start = 1
            put_size = 0
            while True:
                data = f.read(block_size)

                precent = round(put_size / fsize, 2) if fsize else 0
                print("\r已上传：" + str(precent * 100) + "%", end="")
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
                if res_code_up == 0:
                    pass
                else:
                    print("获取链接失败")
                    return
                upload_url = get_link_res_json["data"]["presignedUrls"][
                    str(part_number_start)
                ]
                requests.put(upload_url, data=data, timeout=10)

                part_number_start = part_number_start + 1

        print("\n处理中")
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
        if res_code_up == 0:
            print("上传成功")
        else:
            print("上传失败")
            print(close_res_json)
            return

    # dirId 就是 fileNumber，从0开始，0为第一个文件，传入时需要减一 ！！！（好像文件夹都排在前面）
    def cd(self, dir_num):
        if not dir_num.isdigit():
            if dir_num == "..":
                if len(self.parent_file_list) > 1:
                    self.all_file = False
                    self.file_page = 0

                    self.parent_file_list.pop()
                    self.parent_file_id = self.parent_file_list[-1]
                    self.list = []
                    self.parent_file_name_list.pop()
                    self.get_dir()
                    self.show()
                else:
                    print("已经是根目录")
                return
            if dir_num == "/":
                self.all_file = False
                self.file_page = 0

                self.parent_file_id = 0
                self.parent_file_list = [0]
                self.list = []
                self.parent_file_name_list = []
                self.get_dir()
                self.show()
                return
            print("输入错误")
            return
        dir_num = int(dir_num) - 1
        if dir_num > (len(self.list) - 1) or dir_num < 0:
            print("输入错误")
            return
        if self.list[dir_num]["Type"] != 1:
            print("不是文件夹")
            return

        self.all_file = False
        self.file_page = 0

        self.parent_file_id = self.list[dir_num]["FileId"]
        self.parent_file_list.append(self.parent_file_id)
        self.parent_file_name_list.append(self.list[dir_num]["FileName"])
        self.list = []
        self.get_dir()
        self.show()

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

        except Exception:
            print("获取配置失败，重新输入")

            if user_name == "" or pass_word == "":
                if input_pwd:
                    user_name = input("userName:")
                    pass_word = input("passWord:")
                    authorization = ""
                else:
                    raise Exception("禁止输入模式下，没有账号或密码")

        self.user_name = user_name
        self.password = pass_word
        self.authorization = authorization

    def mkdir(self, dirname, remakedir=False):
        if not remakedir:
            for i in self.list:
                if i["FileName"] == dirname:
                    print("文件夹已存在")
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
            print("创建失败")
            print(res_mk.text)
            return
        code_mkdir = res_json.get("code", -1)

        if code_mkdir == 0:
            print("创建成功: ", res_json["data"]["FileId"])
            self.get_dir()
            return res_json["data"]["Info"]["FileId"]
        print(res_json)
        print("创建失败")
        return

# 线程辅助
class WorkerSignals(QtCore.QObject):
    finished = QtCore.pyqtSignal()
    error = QtCore.pyqtSignal(str)
    result = QtCore.pyqtSignal(object)
    progress = QtCore.pyqtSignal(int)
    log = QtCore.pyqtSignal(str)

class ThreadedTask(QtCore.QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    @QtCore.pyqtSlot()
    def run(self):
        try:
            res = self.fn(*self.args, **self.kwargs, signals=self.signals)
            self.signals.result.emit(res)
        except Exception as e:
            self.signals.error.emit(str(e))
        finally:
            self.signals.finished.emit()

# 登录对话框
class LoginDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("登录123云盘")
        self.setModal(True)
        self.resize(420, 150)
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)

        layout = QtWidgets.QVBoxLayout(self)

        form = QtWidgets.QFormLayout()
        self.le_user = QtWidgets.QLineEdit()
        self.le_pass = QtWidgets.QLineEdit()
        self.le_pass.setEchoMode(QtWidgets.QLineEdit.Password)
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
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
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
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)

        self.pan = None
        self.threadpool = QtCore.QThreadPool.globalInstance()

        # 应用123云盘主题
        self.apply_blue_white_theme()

        # 中央布局
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        main_layout = QtWidgets.QVBoxLayout(central)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(8)

        # 顶部横向按钮栏（左上角为设置按钮）
        toolbar_h = QtWidgets.QHBoxLayout()
        toolbar_h.setSpacing(6)
        
        # 设置按钮（左上角齿轮图标）
        self.btn_settings = QtWidgets.QPushButton("⚙️")
        self.btn_settings.setToolTip("设置")
        self.btn_settings.setMinimumHeight(30)
        self.btn_settings.setMinimumWidth(40)
        self.btn_settings.setStyleSheet("font-size: 16px;")
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
        for b in btns:
            b.setMinimumHeight(30)
            b.setMinimumWidth(110)
            toolbar_h.addWidget(b)

        toolbar_h.addStretch()
        main_layout.addLayout(toolbar_h)

        # 路径栏
        path_h = QtWidgets.QHBoxLayout()
        path_h.addWidget(QtWidgets.QLabel("路径："))
        self.lbl_path = QtWidgets.QLabel("/")
        font = self.lbl_path.font()
        font.setBold(True)
        self.lbl_path.setFont(font)
        path_h.addWidget(self.lbl_path)
        path_h.addStretch()
        main_layout.addLayout(path_h)

        # 文件列表表格
        self.table = QtWidgets.QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["编号", "名称", "类型", "大小"])
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table.doubleClicked.connect(self.on_table_double)
        self.table.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.on_table_context_menu)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setStretchLastSection(True)
        main_layout.addWidget(self.table, stretch=1)

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

        # 启动登录流程
        self.startup_login_flow()

    def apply_blue_white_theme(self):
        """
        123云盘主题样式表
        """
        style = """
        QWidget {
            background-color: #F8FBFF;
            color: #0B2A66;
            font-family: "Microsoft YaHei", "PingFang SC", "Helvetica Neue", Arial;
            font-size: 12px;
        }
        QTableWidget {
            background-color: #FFFFFF;
            gridline-color: #E6F0FF;
            selection-background-color: #D9EEFF;
            selection-color: #0B2A66;
            alternate-background-color: #FBFDFF;
        }
        QHeaderView::section {
            background-color: #EAF5FF;
            color: #0B2A66;
            padding: 6px;
            border: 1px solid #DDEFFB;
        }
        QPushButton {
            background-color: #2B79E6;
            color: #FFFFFF;
            border-radius: 4px;
            padding: 6px 10px;
            border: none;
        }
        QPushButton:hover { background-color: #1F63C9; }
        QPushButton:pressed { background-color: #164EA3; }
        QLineEdit, QTextEdit, QComboBox {
            background-color: #FFFFFF;
            border: 1px solid #DCEEFF;
            padding: 6px;
            border-radius: 4px;
        }
        QStatusBar {
            background-color: #EAF5FF;
            color: #0B2A66;
        }
        QMenu {
            background-color: #FFFFFF;
            border: 1px solid #DCEEFF;
        }
        """
        self.setStyleSheet(style)

    def on_settings(self):
        """打开设置对话框"""
        dlg = SettingsDialog(self)
        if dlg.exec_() == QtWidgets.QDialog.Accepted:
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
            if dlg.exec_() != QtWidgets.QDialog.Accepted:
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

    def populate_table(self):
        if not self.pan:
            return
        self.table.setRowCount(0)
        for i, item in enumerate(self.pan.list):
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QtWidgets.QTableWidgetItem(str(i + 1)))
            self.table.setItem(row, 1, QtWidgets.QTableWidgetItem(item.get("FileName", "")))
            typ = "文件夹" if item.get("Type", 0) == 1 else "文件"
            self.table.setItem(row, 2, QtWidgets.QTableWidgetItem(typ))
            size = item.get("Size", 0)
            if size > 1073741824:
                s = f"{round(size / 1073741824, 2)} GB"
            elif size > 1048576:
                s = f"{round(size / 1048576, 2)} MB"
            else:
                s = f"{round(size / 1024, 2)} KB"
            self.table.setItem(row, 3, QtWidgets.QTableWidgetItem(s))

        names = getattr(self.pan, "parent_file_name_list", [])
        path = "/" + "/".join(names) if names else "/"
        self.lbl_path.setText(path)

    def refresh_file_list(self, reset_page=True):
        if not self.pan:
            QtWidgets.QMessageBox.information(self, "提示", "尚未初始化，请先登录。")
            return
        if reset_page:
            self.pan.all_file = False
            self.pan.file_page = 0
            self.pan.list = []
        self.status.showMessage("正在获取目录...")
        task = ThreadedTask(self._task_get_dir)
        task.signals.result.connect(self._after_get_dir)
        task.signals.error.connect(lambda e: self._show_error("获取目录失败: " + e))
        self.threadpool.start(task)

    def _task_get_dir(self, signals=None):
        code, _ = self.pan.get_dir(save=True)
        return code

    def _after_get_dir(self, code):
        if code != 0:
            self.status.showMessage(f"获取目录返回码: {code}", 5000)
        else:
            self.status.showMessage("目录获取完成", 3000)
        self.populate_table()

    def on_table_double(self, index):
        row = index.row()
        typ_item = self.table.item(row, 2)
        if typ_item and typ_item.text() == "文件夹":
            try:
                self.pan.cd(str(row + 1))
                self.populate_table()
            except Exception as e:
                self._show_error("进入文件夹失败: " + str(e))
        else:
            ret = QtWidgets.QMessageBox.question(self, "下载", "是否下载所选文件？", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            if ret == QtWidgets.QMessageBox.Yes:
                self.on_download()

    def on_table_context_menu(self, pos):
        row = self.table.indexAt(pos).row()
        if row < 0:
            return
        menu = QtWidgets.QMenu()
        a_download = menu.addAction("下载")
        a_link = menu.addAction("显示链接")
        a_delete = menu.addAction("删除")
        a_share = menu.addAction("分享")
        action = menu.exec_(self.table.viewport().mapToGlobal(pos))
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
            self.pan.cd("..")
            self.populate_table()
        except Exception as e:
            self._show_error("返回上级失败: " + str(e))

    def get_selected_detail(self):
        row = self.prompt_selected_row()
        if row is None:
            return None, None
        idx_item = self.table.item(row, 0)
        if not idx_item:
            return None, None
        file_index = int(idx_item.text()) - 1
        if not self.pan or file_index < 0 or file_index >= len(self.pan.list):
            return None, None
        return file_index, self.pan.list[file_index]

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
        
        self.status.showMessage("正在解析下载链接...")
        task = ThreadedTask(self._task_get_download_and_stream, file_index, download_dir)
        task.signals.progress.connect(lambda p: self.status.showMessage(f"下载进度: {p}%", 2000))
        task.signals.result.connect(lambda r: self.status.showMessage("下载完成: " + str(r), 5000))
        task.signals.error.connect(lambda e: self._show_error("下载失败: " + e))
        self.threadpool.start(task)

    def _task_get_download_and_stream(self, file_index, download_dir, signals=None):
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
        if os.path.exists(out_path):
            reply = QtWidgets.QMessageBox.question(None, "文件已存在", f"{fname} 已存在，是否覆盖？", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            if reply == QtWidgets.QMessageBox.No:
                return "已取消"
        with requests.get(redirect_url, stream=True, timeout=30) as r:
            r.raise_for_status()
            total = int(r.headers.get("Content-Length", 0) or 0)
            temp = out_path + ".123pan"
            done = 0
            with open(temp, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        done += len(chunk)
                        if total and signals:
                            signals.progress.emit(int(done * 100 / total))
            os.replace(temp, out_path)
        return out_path

    def on_showlink(self):
        file_index, file_detail = self.get_selected_detail()
        if file_detail is None:
            return
        task = ThreadedTask(self._task_get_link, file_index)
        task.signals.result.connect(self._after_get_link)
        task.signals.error.connect(lambda e: self._show_error("获取链接失败: " + e))
        self.threadpool.start(task)

    def _task_get_link(self, file_index, signals=None):
        url = self.pan.link_by_number(file_index, showlink=False)
        return url

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
        dlg.exec_()

    def on_upload(self):
        if not self.pan:
            QtWidgets.QMessageBox.information(self, "提示", "请先登录。")
            return
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "选择要上传的文件", os.path.expanduser("~"))
        if not path:
            return
        fname = os.path.basename(path)
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
        task = ThreadedTask(self._task_upload_file, path, dup_choice)
        task.signals.progress.connect(lambda p: self.status.showMessage(f"上传进度: {p}%", 2000))
        task.signals.result.connect(lambda r: (self.status.showMessage("上传完成", 3000), self.refresh_file_list(reset_page=True)))
        task.signals.error.connect(lambda e: self._show_error("上传失败: " + e))
        self.threadpool.start(task)

    def _task_upload_file(self, file_path, dup_choice, signals=None):
        file_path = file_path.replace('"', "").replace("\\", "/")
        file_name = os.path.basename(file_path)
        if not os.path.exists(file_path):
            raise RuntimeError("文件不存在")
        if os.path.isdir(file_path):
            raise RuntimeError("不支持文件夹上传")
        fsize = os.path.getsize(file_path)
        md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            while True:
                data = f.read(64 * 1024)
                if not data:
                    break
                md5.update(data)
        readable_hash = md5.hexdigest()
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
        r = QtWidgets.QMessageBox.question(self, "删除确认", f"确认将 '{file_detail['FileName']}' 删除？", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if r == QtWidgets.QMessageBox.No:
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
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
