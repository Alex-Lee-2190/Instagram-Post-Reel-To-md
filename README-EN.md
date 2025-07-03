# Instagram-Post-Reel-To-md

A Python script for downloading Instagram user posts and Reels and exporting post content into Markdown format. Using the `instaloader` and `gallery-dl` libraries, suitable for automating the archiving of Instagram content.

---

## Features

- **Batch Download**: Download all posts (photos/videos) and Reels from a list of specified users.
- **File Organization**: Automatically sort into:
  - `zmarkdown/`: Markdown files describing each post.
  - `media/`: Image and video files.
  - `metadata/`: JSON files containing metadata.
- **Deduplication**: Keeps track of downloaded post and Reel URLs to avoid duplicates.
- **Retry on Failure**: Records failed downloads and supports re-downloading them.
- **Markdown Export**: Generates `.md` file for each post, including upload time, caption, URL, likes, etc.
- **Multiple Modes**:
  - Mode 1: Download all posts and Reels of users.
  - Mode 2: Retry failed downloads.
  - Mode 3: Check and download only new content.

---

## Requirements

- Python 3.8+
- Libraries:
  - `instaloader`
  - `gallery-dl`

---

## Instagram Cookies Setup

1. Log into Instagram using a browser.
2. Use a browser extension (e.g., [Get cookies.txt](https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc)) to export your cookies.
3. Save the file as `www.instagram.com_cookies.txt`.

---

## Usage

### 1. Configure User List

Edit `following.txt`, one Instagram username per line:

```
user1
user2
```

### 2. Set Paths

At the top of the script, configure the paths:

```python
COOKIE_FILE_PATH = '...'
ROOT_DIR = '...'
```

### 3. Run the Script and Choose Mode

Run the script and enter the mode number as prompted.

---

## Output Directory Structure

Downloaded content will be saved under:

```
ROOT_DIR/Instagram/username/
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

Failed downloads are recorded in `failed_downloads.txt`.

---

## Example

Original Instagram post:

<img src="https://github.com/user-attachments/assets/f0d642f4-7281-43bf-a110-40ea55db0add" alt="ep1" width="500"/>

Generated Markdown version:

<img src="https://github.com/user-attachments/assets/96a70711-9140-4e89-892e-4fc925abc6de" alt="ep2" width="300"/>

---

## License

This project is licensed under the [MIT License](LICENSE).

---
