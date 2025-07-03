# Instagram-Post-Reel-To-md

一个用于下载 Instagram 用户帖子和 Reels 的 Python 脚本，支持批量下载、文件整理和元数据处理。使用 `instaloader` 和 `gallery-dl` 工具，提供增量下载和失败重试功能，适用于自动化抓取 Instagram 内容。

---

## 功能特性

- **批量下载**：从指定用户列表下载帖子（图片、视频）和 Reels。
- **文件整理**：自动分类存储为：
  - `zmarkdown/`：描述文件（Markdown）
  - `media/`：图片 / 视频
  - `metadata/`：元数据（JSON）
- **增量下载**：检测已下载内容，避免重复下载。
- **失败重试**：记录下载失败的帖子并支持重新下载。
- **Markdown 生成**：每个帖子生成 `.md` 文件，包含上传时间、标题、URL、点赞数等。
- **多模式支持**：
  - 模式 1：下载用户的全部帖子和 Reels。
  - 模式 2：重新下载失败的帖子。
  - 模式 3：检查并下载最新内容。
  - 模式 4：保存 Instagram 文件夹的子文件夹名称。
  - 模式 5：从指定文件加载 URL 下载 Reels。

---

## 依赖项

- Python 3.8+
- 库：
  - `instaloader`
  - `gallery-dl`

---

## Instagram Cookies 设置

1. 登录 Instagram。
2. 使用浏览器插件（如 Chrome 插件 [Get cookies.txt](https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc)）导出 cookies。
3. 保存为 `www.instagram.com_cookies.txt`
---

## 使用方法

### 1. 配置用户列表

编辑 `following.txt`，每行输入一个 Instagram 用户名：

```
user1
user2
```

### 2. 修改配置路径

在脚本顶部设置以下路径：

```python
COOKIE_FILE_PATH = 'C:/Users/YourUser/Downloads/www.instagram.com_cookies.txt'
ROOT_DIR = 'D:/0FILE/Library'
```

### 3. 运行脚本并选择模式

```bash
python instagram_downloader.py
```

选择运行模式（输入对应数字）：

- `1`：下载全部帖子和 Reels
- `2`：重新下载失败的帖子
- `3`：检查并下载最新内容
- `4`：保存 Instagram 文件夹的子文件夹名称到 `file_list.txt`
- `5`：从 `url.txt` 加载帖子 URL 并下载 Reels

---

## 输出目录结构

下载的文件将存储在：

```
ROOT_DIR/Instagram/用户名/
├── zmarkdown/
│   ├── 2025-07-03_12-00-00_UTC.md
│   └── ...
├── media/
│   ├── 2025-07-03_12-00-00_UTC.mp4
│   └── ...
├── metadata/
│   ├── 2025-07-03_12-00-00_UTC.json
│   └── ...
```

下载失败的帖子记录在 `failed_downloads.txt` 中。

---

## 📄 License

本项目采用 [MIT License](LICENSE)。

---

## 💬 示例

假设 `following.txt` 内容为：

```
user1
user2
```

运行：

```bash
python instagram_downloader.py
# 输入: 1
```

程序将批量下载 user1 和 user2 的帖子与 Reels，并自动分类存储。
