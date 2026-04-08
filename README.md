# [国家中小学智慧教育平台 电子课本](https://www.google.com/search?q=https://basic.smartedu.cn/tchMaterial/) 下载工具 (Termux / CLI 版)

本工具是 [tchMaterial-parser](https://github.com/happycola233/tchMaterial-parser) 的命令行重构版，专门优化了对 **Termux (Android)** 和 **Linux** 环境的支持。通过简单的命令行操作，即可批量下载国家中小学智慧教育平台的 PDF 课本。

## ✨ 工具特点

  * 终端原生支持：无需 GUI 界面，在 Termux 或远程服务器上也能轻松运行。
  * 📚 批量下载：支持通过文件批量导入 URL，一次性下载全套教材。
  * 🔖 自动添加书签：下载完成后自动根据资源目录生成 PDF 书签，方便查阅。
  * 🔑 令牌持久化：支持 Access Token 配置并自动加密保存，避免重复输入。
  * 🚀 动态下载逻辑：针对大文件优化分块下载，提高 Termux 环境下的稳定性。

-----

## 📥 安装与环境配置 (Termux)

在 Termux 中运行前，请执行以下命令安装必要组件：

```bash
# 更新软件包
pkg update && pkg upgrade

# 安装 Python
pkg install python

# 安装依赖库
pip install requests pypdf
```

将脚本文件（例如 `tch_cli.py`）放置在你的工作目录即可开始使用。

-----

## 🚀 使用指南

### 1\. 设置 Access Token (必选)

为了访问私有资源并获取高清 PDF，你需要设置 Access Token。获取方法详见[原项目说明](https://www.google.com/search?q=https://github.com/happycola233/tchMaterial-parser%232--%E8%AE%BE%E7%BD%AE-access-token%E5%8F%AF%E9%80%89)。

```bash
python tch_cli.py -t "你的_Access_Token"
```

> **注意**：Token 会加密保存在 `~/.config/tchMaterial-parser/data.json`。

### 2\. 下载单个课本

使用 `-u` 参数指定课本详情页地址：

```bash
python tch_cli.py -u "https://basic.smartedu.cn/tchMaterial/detail?contentId=xxx&contentType=assets_document"
```

### 3\. 批量下载

将所有 URL 写入一个文本文件（如 `list.txt`），每行一个：

```bash
python tch_cli.py -f list.txt -d ./my_books
```

### 4\. 参数说明

| 参数 | 长参数 | 说明 |
| :--- | :--- | :--- |
| `-t` | `--token` | 设置并保存 Access Token |
| `-u` | `--url` | 下载单个指定的资源链接 |
| `-f` | `--file` | 从文本文件批量读取链接下载 |
| `-d` | `--dir` | 指定保存目录 (默认当前目录) |
| | `--no-bookmarks` | 禁用自动生成书签功能 |

-----

## ❓ 常见问题

### 1\. 下载后的文件在哪里？

默认情况下，文件会保存在你运行脚本的当前目录下。如果你使用了 `-d` 参数，则保存在指定目录。在 Termux 中，你可以使用 `termux-setup-storage` 将其移动到手机内部存储。

### 2\. 为什么提示 Access Token 过期？

Access Token 通常具有 7 天左右的有效期。如果下载失败，请按照[获取教程](https://www.google.com/search?q=https://github.com/happycola233/tchMaterial-parser%232--%E8%AE%BE%E7%BD%AE-access-token%E5%8F%AF%E9%80%89)重新获取并使用 `-t` 重新设置。

### 3\. 配置文件保存在哪？

  * **Linux / Termux**: `~/.config/tchMaterial-parser/data.json`
  * **Windows (CLI)**: `%USERPROFILE%\.config\tchMaterial-parser\data.json`

-----

## ⚖️ 免责声明

本工具仅供个人学习研究和教育使用，严禁用于商业用途。请尊重版权，下载后于 24 小时内删除。

## ⚖️ 许可证与版权信息

- 本工具的原始版本由 [happycola233](https://github.com/happycola233/tchMaterial-parser) 开发。
- 本修改版（CLI/Termux 版）由[chlink2025](https://github.com/chlink2025/tchMaterial-parser-cli)进行重构与维护。
- 全体代码遵循 **MIT License** 协议开源。
