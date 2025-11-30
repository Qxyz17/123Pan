<div align="center">
  <img src="icon.ico" alt="123云盘" width="120" height="120">
  
  # 🚀 123云盘下载工具
  
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

123云盘下载工具是一款基于Python开发的高效下载辅助工具，通过模拟安卓客户端协议，帮助用户绕过123云盘的自用下载流量限制，实现无阻碍下载体验。

工具提供两种使用方式（安卓协议/网页协议），支持文件管理全流程操作，适用于需要高频下载云盘文件的用户。

---

## ✨ 核心功能

| 功能 | 说明 | 支持协议 |
|------|------|----------|
| 🔑 账号登录 | 用户名密码快速登录，自动保存会话 | 安卓/网页 |
| 📂 文件浏览 | 树形结构展示云盘文件，支持目录切换 | 安卓/网页 |
| 💾 高速下载 | 突破流量限制，文件自动保存至`download`目录 | 安卓协议 |
| 📤 文件上传 | 本地文件快速上传至云盘指定目录 | 安卓协议 |
| 🔗 生成链接 | 一键获取文件分享链接 | 安卓/网页 |
| 🗑️ 文件管理 | 支持创建文件夹、删除文件等操作 | 安卓/网页 |

> ⚠️ 注意：网页协议已停止更新且受流量限制，**强烈推荐使用安卓协议**

---

## 🚀 快速开始

1. 前往 [Releases](https://github.com/Qxyz17/123pan/releases) 下载对应系统的可执行文件
   - Windows用户：下载`Android.exe`运行
   - macOS/Linux用户：下载`android.py`文件运行

2. 首次运行将自动生成配置文件，按照提示输入账号信息即可使用


## ⚙️ 配置说明

首次运行工具后，会在当前目录生成 `123pan.txt` 配置文件，格式如下：

```json
{
  "userName": "你的账号",
  "passWord": "你的密码",
  "authorization": "自动生成的令牌"
}
```

> 📌 提示：配置文件自动加密保存，无需担心账号信息泄露

---

## 📝 使用教程

1. **登录流程**
   - 运行工具后输入账号密码
   - 成功登录后会显示云盘根目录文件列表

2. **文件下载**
   - 输入文件编号，按提示确认下载
   - 下载文件临时以 `.123pan` 为后缀，完成后自动恢复原名称

3. **目录导航**
   - 输入文件夹编号进入子目录
   - 输入 `..` 返回上一级目录

---

## ⚠️ 注意事项

- 📶 确保网络连接稳定，下载大文件时建议使用有线网络
- 🔒 本工具仅用于学习研究，请勿用于商业用途
- ⚖️ 使用者需遵守123云盘用户协议，滥用可能导致账号限制
- 🔄 定期更新工具以获取最新协议支持

---

## 🤝 贡献指南

欢迎提交PR改进代码，或通过Issues反馈问题。贡献流程：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交修改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 打开Pull Request

---

<div align="center">
  <p>123云盘 | 基于 Apache 2.0 协议开源</p>
  <p>如有问题请联系：18859251107@163.com</p>
</div>
