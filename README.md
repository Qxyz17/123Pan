<div align="center">
  <img src="icon.ico" alt="123pan" width="120" height="120">
  
  # 🚀 123pan
  
  <p>突破限制 · 高效下载 · 简单易用</p>
  
  <div>
    <a href="https://github.com/Qxyz17/123pan/stargazers"><img src="https://img.shields.io/github/stars/Qxyz17/123pan?style=for-the-badge&color=yellow&logo=github" alt="Stars"></a>
    <a href="https://github.com/Qxyz17/123pan/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-Apache%202.0-green?style=for-the-badge" alt="License"></a>
    <a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-3.8%2B-blue?style=for-the-badge&logo=python" alt="Python Version"></a>
    <a href="https://github.com/Qxyz17/123pan/releases"><img src="https://img.shields.io/github/downloads/Qxyz17/123pan/total?style=for-the-badge&color=orange" alt="Downloads"></a>
  </div>
  
</div>

---

## 📖 项目介绍

[项目原地址](https://github.com/Qxyz17/123pan)

123pan是一款基于Python开发的高效下载辅助工具，通过模拟安卓客户端协议，帮助用户绕过123云盘的自用下载流量限制，实现无阻碍下载体验。

工具提供两种使用方式（安卓协议/网页协议），支持文件管理全流程操作，适用于需要下载云盘文件的用户。

---

## ✨ 功能

| 功能 | 支持协议 |
|------|----------|
| 🔑 账号登录 | 安卓/网页 |
| 📂 文件浏览 | 安卓/网页 |
| 💾 高速下载 | 安卓协议 |
| 📤 文件上传 | 安卓协议 |
| 🔗 生成链接 | 安卓/网页 |
| 🗑️ 文件管理 | 安卓/网页 |

> ⚠️ 注意：网页协议已停止更新且受流量限制，**强烈推荐使用安卓协议**

---

## 🚀 快速开始

1. 前往 [Releases](https://github.com/Qxyz17/123pan/releases) 下载可执行文件
   - Windows用户：下载`123pan.exe`运行
   - macOS/Linux用户：下载`123pan.py`文件运行

2. 首次运行将自动生成配置文件，按照提示输入账号信息即可使用


## ⚙️ 配置说明

首次运行工具后，会在C:\Users\%USERNAME%\AppData\Roaming\Qxyz17\123pan生成 `config.json` 配置文件，格式如下：

```json
{
  "userName": "账号",
  "passWord": "密码",
  "authorization": "令牌",
  "deviceType": "驱动类型",
  "osVersion": "安卓版本",
  "settings": {
    "defaultDownloadPath": "默认下载路径",
    "askDownloadLocation": 开关
}
```

---

## 📝 使用教程

1. **登录流程**
   - 运行工具后输入账号密码
   - 成功登录后会显示云盘根目录文件列表

2. **文件下载**
   - 输入文件编号，按提示确认下载
   - 下载文件临时以 `.123pan` 为后缀，完成后自动恢复原名称

---

## ⚠️ 注意事项

- 📶 确保网络连接稳定，下载大文件时建议使用有线网络
- 🔒 本工具仅用于学习研究，请勿用于商业用途
- ⚖️ 使用者需遵守123云盘用户协议，滥用可能导致账号限制
- 🔄 定期更新工具以获取最新协议支持

---

## 待开发功能
- [ ] 退出登录
- [ ] 文件拖拽上传
- [ ] 拖拽上传功能
- [ ] 界面美化

## 🤝 贡献指南

欢迎提交PR改进代码，或通过Issues反馈问题。

---

<div align="center">
  <p>123pan | 基于 Apache 2.0 协议开源</p>
  <p>如有问题请提交Issues</p>
</div>
