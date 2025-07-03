# Instagram-Post-Reel-To-md

一个用于下载 Instagram 用户帖子和 Reels 的 Python 脚本，支持批量下载、文件整理和元数据处理，并将贴文的内容整理为md文件。使用 `instaloader` 和 `gallery-dl` 库，提供去重下载和失败重试功能，适用于自动化抓取 Instagram 内容。

---

## 功能特性

- **批量下载**：从指定用户列表下载帖子（图片、视频）和 Reels。
- **文件整理**：自动分类存储为：
  - `zmarkdown/`：描述文件（Markdown）
  - `media/`：图片 / 视频
  - `metadata/`：元数据（JSON）
- **去重下载**：记录每个帖子和 Reels 的 URL，避免重复下载。
- **失败重试**：记录下载失败的帖子和 Reels 并支持重新下载。
- **Markdown 生成**：每个帖子生成 `.md` 文件，包含上传时间、标题、URL、点赞数等。
- **多模式支持**：
  - 模式 1：下载用户的全部帖子和 Reels。
  - 模式 2：重新下载失败的帖子。
  - 模式 3：检查并下载最新内容。

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
COOKIE_FILE_PATH = '...'
ROOT_DIR = '...'
```

### 3. 运行脚本并选择模式

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

## 示例

![ep1](https://github.com/user-attachments/assets/f0d642f4-7281-43bf-a110-40ea55db0add)
原帖文
![ep2](https://github.com/user-attachments/assets/96a70711-9140-4e89-892e-4fc925abc6de)
下载后的md格式贴文
---

## License

本项目采用 [MIT License](LICENSE)。

---
