import instaloader
from instaloader import Post
import os
import shutil
import lzma
import json
from datetime import datetime
import subprocess
import time
import traceback
from itertools import islice
import re

USERNAME = ""
COOKIE = {}
COOKIE_FILE_PATH = r''

# 标记是否已记录时间
LOG_TIME_WRITTEN = False
ROOT_DIR = r""  # 根目录
FOLLOWING_FILE = ""  # 用户名列表

L = instaloader.Instaloader()  # 创建 Instaloader 实例


def get_instagram_cookies():
    global COOKIE  # 声明为全局变量

    target_cookies = ['sessionid', 'csrftoken', 'ds_user_id', 'mid', 'ig_did']
    cookies_dict = {}

    try:
        with open(COOKIE_FILE_PATH, 'r', encoding='utf-8') as file:
            cookies = file.readlines()

        for line in cookies:
            if line.startswith('#'):
                continue
            parts = line.strip().split('\t')
            if len(parts) >= 7:
                name = parts[5]
                value = parts[6]
                if name in target_cookies:
                    cookies_dict[name] = value

        COOKIE = {
            "sessionid": cookies_dict.get("sessionid", ""),
            "csrftoken": cookies_dict.get("csrftoken", ""),
            "ds_user_id": cookies_dict.get("ds_user_id", ""),
            "mid": cookies_dict.get("mid", ""),
            "ig_did": cookies_dict.get("ig_did", "")
        }

    except FileNotFoundError:
        print(f"[错误] 未找到 cookie 文件：{COOKIE_FILE_PATH}")
        COOKIE = {}
    except Exception as e:
        print(f"[错误] 处理 cookie 文件时出错: {e}")
        COOKIE = {}


def read_following_usernames(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def get_all_md_urls_with_shortcode(folder_path):
    results = []
    pattern = re.compile(r'\*\*URL：\*\* \[(https?://www\.instagram\.com/p/([^/]+)/?)\]')

    for filename in os.listdir(folder_path):
        if filename.endswith(".md"):
            md_path = os.path.join(folder_path, filename)
            with open(md_path, "r", encoding="utf-8") as f:
                content = f.read()
                match = pattern.search(content)
                if match:
                    url = match.group(1)
                    shortcode = match.group(2)
                    results.append((shortcode, url))
    return results


def download_reels(username_to_download, base_dir, post_urls, base_dir1, idx_main, total_users_main, max_reels,markdown_dir, times, mode):
    # gallery-dl 下载 Reels
    os.makedirs(base_dir, exist_ok=True)
    COOKIE_FILE_PATH  # 你的 JSON cookies 路径

    start = 1 + (times - 1) * max_reels
    end = max_reels * times

    try:
        command = [
            "gallery-dl",
            f"https://www.instagram.com/{username_to_download}/reels/",
            "--cookies", COOKIE_FILE_PATH,
            "--write-metadata",  # 生成 .json 文件
            "--no-download",  # 不下载实际的视频文件
            "-d", base_dir
        ]
        # 如果 mode == 2, 限制只下载指定范围的 Reels
        if mode == 2:
            command.append("--range")
            command.append(f"{start}-{end}")
        # 执行命令
        subprocess.run(command, check=True)
        print(f"成功下载 Reels 元数据：{username_to_download}")

    except subprocess.CalledProcessError as e:
        print(f"下载失败：{e}")
        return [], False

    if mode == 2:
        post_urls = get_all_md_urls_with_shortcode(markdown_dir)

    reel_urls = []
    found_duplicate_once = False
    found_duplicate_twice = False

    for file in os.listdir(base_dir1):
        if file.endswith(".json"):
            json_path = os.path.join(base_dir1, file)
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                post_url = data.get("post_url")
                if post_url:
                    shortcode = post_url.rstrip("/").split("/")[-1]
                    # 先判断是否已在 reel_urls 中
                    if any(post_url == url for _, url in reel_urls):
                        continue
                    # 再判断是否在已有 post_urls 中
                    if any(post_url == url for _, url in post_urls):
                        print(f"重复的 URL：{post_url}")
                        if times != 1:
                            if found_duplicate_once:
                                found_duplicate_twice = True
                            else:
                                found_duplicate_once = True
                    else:
                        reel_urls.append((shortcode, post_url))
                        print(f"新的 Reels URL：{post_url}")
    print("times", times)
    print("found_duplicate_once:", found_duplicate_once)
    print("found_duplicate_twice:", found_duplicate_twice)
    save_post_urls(username_to_download, reel_urls, "downloaded_reel_urls.txt")

    if mode == 1:
        if not reel_urls:
            print(f"没有新 Reels URL，跳过下载和处理：{username_to_download}")
            return []

    download_user(choose, username_to_download, reel_urls, idx_main, total_users_main)
    log_process(username_to_download, "Instagram")
    return reel_urls, found_duplicate_twice


def rename_reels_files(folder_path, username_to_download):
    base_dir, markdown_dir, media_dir, metadata_dir = path(username_to_download, "Instagram")
    for file in os.listdir(folder_path):
        if file.endswith(".json"):
            json_path = os.path.join(folder_path, file)
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            date_str = data.get("date")
            if not date_str:
                print(f"缺少 date 字段：{file}")
                continue

            try:
                dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                new_base = dt.strftime("%Y-%m-%d_%H-%M-%S_UTC")
            except ValueError:
                print(f"时间格式错误：{date_str} in {file}")
                continue

            old_base = file.replace(".json", "")
            mp4_old = os.path.join(folder_path, f"{old_base}")
            json_old = json_path

            mp4_new = os.path.join(folder_path, f"{new_base}.mp4")
            json_new = os.path.join(folder_path, f"{new_base}_reel_gallery-dl.json")

            # 为避免 WinError 32，稍作等待
            time.sleep(0.01)

            if os.path.exists(mp4_old):
                os.rename(mp4_old, mp4_new)
                print(f"mp4  重命名：{mp4_old} → {mp4_new}")
            else:
                print(f"未找到视频文件：{mp4_old}")

            os.rename(json_old, json_new)
            print(f"json 重命名：{json_old} → {json_new}")

            # 转移文件
            metadata_gallery_dl_dir = os.path.join(folder_path, "metadata_gallery-dl")
            os.makedirs(media_dir, exist_ok=True)
            os.makedirs(metadata_gallery_dl_dir, exist_ok=True)

            if os.path.exists(mp4_new):
                shutil.move(mp4_new, os.path.join(media_dir, os.path.basename(mp4_new)))
                print(f"移动视频到 {media_dir}")
            if os.path.exists(json_new):
                shutil.move(json_new, os.path.join(metadata_gallery_dl_dir, os.path.basename(json_new)))
                print(f"移动元数据到 {metadata_gallery_dl_dir}")


def process_user_reels(username_to_download, idx_main, total_users_main, post_urls, times, mode):
    base_dir, markdown_dir, media_dir, metadata_dir = path(username_to_download, None)
    base_dir1, markdown_dir1, media_dir1, metadata_dir1 = path(username_to_download, "Instagram")
    if mode == 1:
        # 传入 post_urls
        download_reels(username_to_download, base_dir, post_urls, base_dir1, idx_main, total_users_main, 262144,
                       markdown_dir1, times, mode=1)
        rename_reels_files(base_dir1, username_to_download)
        return False
    elif mode == 2:
        # 传入 post_urls
        reel_urls, found_duplicate_twice = download_reels(username_to_download, base_dir, post_urls, base_dir1,
                                                          idx_main, total_users_main, 3, markdown_dir1, times, mode=2)
        rename_reels_files(base_dir1, username_to_download)
        return reel_urls, found_duplicate_twice


def path(username_to_download, Insta):
    if Insta == None:
        base_dir = os.path.join(ROOT_DIR)
    else:
        base_dir = os.path.join(ROOT_DIR, Insta, username_to_download)
    markdown_dir = os.path.join(base_dir, "zmarkdown")
    media_dir = os.path.join(base_dir, "media")
    metadata_dir = os.path.join(base_dir, "metadata")
    return base_dir, markdown_dir, media_dir, metadata_dir


def get_all_post_urls(username_to_download, times, mode):
    L.context._session.cookies.update(COOKIE)

    profile = instaloader.Profile.from_username(L.context, username_to_download)
    post_urls = []

    if mode == 1:
        for post in profile.get_posts():
            shortcode = post.shortcode
            url = f"https://www.instagram.com/p/{shortcode}/"
            post_urls.append((shortcode, url))

        print(f"共获取到 {len(post_urls)} 个 post")
        print(post_urls)
        return post_urls
    elif mode == 2:
        cache = 3
        start = (times - 1) * cache
        end = times * cache
        posts = profile.get_posts()  # 必须先拿到 posts
        posts = islice(posts, start, end)  # 再根据 start/end 切片

        for post in posts:
            shortcode = post.shortcode
            url = f"https://www.instagram.com/p/{shortcode}/"
            post_urls.append((shortcode, url))

        print(f"times={times} 获取到 {len(post_urls)} 个 post")
        print(post_urls)
        return post_urls


def remove_failed_log_entry(shortcode):
    if not os.path.exists('failed_downloads.txt'):
        return

    with open('failed_downloads.txt', 'r', encoding='utf-8') as fr:
        lines = fr.readlines()

    new_lines = []
    i = 0
    while i < len(lines):
        # 检查是否是完整的三行记录
        if i + 2 < len(lines) and shortcode in lines[i + 2]:
            # 跳过这三行（即删除）
            i += 3
        else:
            new_lines.append(lines[i])
            i += 1

    with open('failed_downloads.txt', 'w', encoding='utf-8') as fw:
        fw.writelines(new_lines)


def log_failed_download(username_to_download, shortcode, url, log_file='failed_downloads.txt'):
    global LOG_TIME_WRITTEN
    with open(log_file, 'a', encoding='utf-8') as f:
        # 记录时间
        f.write(f'记录时间：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
        # 写入失败的下载信息
        f.write(f'username: {username_to_download}\n')
        f.write(f'{shortcode}\t{url}\n')
    print(f"Invalid log file path: {log_file}")


def download_posts_by_url(choose, username_to_download, post_urls, base_dir, idx_main, total_users_main):
    os.makedirs(base_dir, exist_ok=True)
    L.context._session.cookies.update(COOKIE)
    L.dirname_pattern = base_dir

    total_url = len(post_urls)

    for idx, (shortcode, url) in enumerate(post_urls, start=1):
        try:
            post = Post.from_shortcode(L.context, shortcode)
            L.download_post(post, target=f"{shortcode}")
            print(f"下载成功：{shortcode}: [{total_users_main}/{idx_main}]: [{total_url}/{idx}]")
            if choose == "2":
                remove_failed_log_entry(shortcode)
        except Exception as e:
            print(f"[{total_url}/{idx}]: 下载失败 {shortcode}: {e}")
            if not choose == "2":
                log_failed_download(username_to_download, shortcode, url)


def download_user(choose, username_to_download, post_urls, idx_main, total_users_main):
    base_dir, markdown_dir, media_dir, metadata_dir = path(username_to_download, "Instagram")

    os.makedirs(markdown_dir, exist_ok=True)
    os.makedirs(media_dir, exist_ok=True)
    os.makedirs(metadata_dir, exist_ok=True)

    download_posts_by_url(choose, username_to_download, post_urls, base_dir, idx_main, total_users_main)

    # 分类整理
    for filename in os.listdir(base_dir):
        file_path = os.path.join(base_dir, filename)
        if os.path.isfile(file_path):
            if filename.endswith((".txt", ".md")):
                shutil.move(file_path, os.path.join(markdown_dir, filename))
            elif filename.endswith((".jpg", ".png", ".mp4", ".webp")):
                shutil.move(file_path, os.path.join(media_dir, filename))
            elif filename.endswith(".json.xz"):
                shutil.move(file_path, os.path.join(metadata_dir, filename))


def log_process(username_to_download, Insta):
    base_dir, markdown_dir, media_dir, metadata_dir = path(username_to_download, "Instagram")
    metadata_files = [f for f in os.listdir(metadata_dir) if f.endswith(".json.xz") and f.startswith("20")]
    total = len(metadata_files)

    for idx, filename in enumerate(metadata_files, start=1):
        print(f"正在处理 [{idx}/{total}]: {filename}")
        base_name = filename.replace(".json.xz", "")
        post_time = base_name
        json_xz_path = os.path.join(metadata_dir, filename)
        json_path = os.path.join(metadata_dir, f"{base_name}.json")

        # 解压 json.xz 成 json
        with lzma.open(json_xz_path) as f_in, open(json_path, "wb") as f_out:
            f_out.write(f_in.read())
        # 删除 .xz 文件
        os.remove(json_xz_path)
        # 加载解压后的 json 数据
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        txt_path = os.path.join(markdown_dir, f"{base_name}.txt")
        title = "（无标题）"
        if os.path.exists(txt_path):
            with open(txt_path, "r", encoding="utf-8") as f:
                title = f.read().strip()

        node = data.get("node", {})
        shortcode = node.get("shortcode", "unknown")
        url = f"https://www.instagram.com/p/{shortcode}/"
        likes = node.get("edge_media_preview_like", {}).get("count", 0)
        comment_counts = node.get("edge_media_preview_comment", {}).get("count", 0)

        # post = Post.from_shortcode(L.context, shortcode)
        # 替换 md_lines 中添加评论的部分：
        md_lines = [
            f"# Instagram Post",
            f"**上传时间：** {post_time}",
            f"**标题：** {title}",
            f"**URL：** [{url}]({url})",
            f"**点赞数：** {likes}",
            f"**评论数：** {comment_counts}",
            # "\n## 评论："
        ]

        # 处理媒体文件（图片和视频）
        media_files = [f for f in os.listdir(media_dir) if f.endswith((".jpg", ".png", ".mp4", ".webp"))]

        # 从文本文件名中提取时间戳（去掉 .md 后缀）
        base_name_without_extension = base_name  # e.g., "2025-04-03_00-35-57_UTC"
        for media_file in media_files:
            # 提取媒体文件名中的时间戳部分
            media_name_without_extension = os.path.splitext(media_file)[0]  # 去掉文件扩展名
            if media_name_without_extension.startswith(base_name_without_extension):
                if media_file.endswith((".jpg", ".png", ".webp")):
                    # 添加图片的 HTML 标签，并设置宽度
                    md_lines.append(f'<img src="{os.path.join(media_dir, media_file)}" height="650" />')
                elif media_file.endswith(".mp4"):
                    # 添加视频的 HTML 标签，并设置宽度
                    md_lines.append(f'<video id="video" controls="" preload="none" width="35%" height="auto">')
                    md_lines.append(
                        f'    <source id="mp4" src="{os.path.join(media_dir, media_file)}" type="video/mp4">')
                    md_lines.append(f'</video>')

        # 处理每个评论
        '''
        for comment in post.get_comments():
            user = comment.owner.username
            text = comment.text
            created_at = comment.created_at_utc.strftime("%Y-%m-%d %H:%M:%S")
            comment_likes = getattr(comment, "likes_count", 0)
            md_lines.append(f"- **{user}** ({created_at}, likes: {comment_likes}): {text}")

            if comment.answers:
                for reply in comment.answers:
                    reply_user = reply.owner.username
                    reply_text = reply.text
                    reply_created_at = reply.created_at_utc.strftime("%Y-%m-%d %H:%M:%S")
                    reply_likes = getattr(reply, "likes_count", 0)
                    md_lines.append(
                        f"    - ↳ **{reply_user}** ({reply_created_at}, likes: {reply_likes}): {reply_text}"
                    )
        '''

        # 将 md_lines 写入文件
        md_path = os.path.join(markdown_dir, f"{base_name}.md")
        with open(md_path, "w", encoding="utf-8") as f:
            f.write("\n".join(md_lines))

        if os.path.exists(txt_path):
            os.remove(txt_path)


def read_failed_downloads(log_file='failed_downloads.txt'):
    user_post_map = {}

    current_username = None

    with open(log_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line.startswith('username: '):
                current_username = line.replace('username: ', '').strip()
                if current_username not in user_post_map:
                    user_post_map[current_username] = set()
            elif not line.startswith('记录时间') and current_username:
                parts = line.split('\t')
                if len(parts) == 2:
                    shortcode, url = parts
                    user_post_map[current_username].add((shortcode.strip(), url.strip()))

    # 展平为列表
    usernames = list(user_post_map.keys())
    user_posts = list(user_post_map.values())

    return usernames, user_posts


def save_post_urls(username, post_urls, output_file):
    with open(output_file, 'a', encoding='utf-8') as f:
        f.write(f"username: {username}\n")
        for shortcode, url in post_urls:
            f.write(f"{shortcode}\t{url}\n")


def get_latest_downloaded_filename(username_to_download, idx_main, total_users_main):
    base_dir, markdown_dir, media_dir, metadata_dir = path(username_to_download, "Instagram")
    post_updates = []
    # 获取 metadata_dir 目录下的所有文件
    existing_files = os.listdir(metadata_dir)
    context = instaloader.InstaloaderContext()

    # posts update
    p_found_duplicate_once = False  # 记录第一次重复
    p_found_duplicate_twice = False  # 记录第二次重复
    max_timep = 65536
    stop_download = False  # 外层控制
    for times in range(1, max_timep + 1):
        if stop_download:
            break  # 在每次 times 循环开始时检查！

        post_urls = get_all_post_urls(username_to_download, times, mode=2)

        for shortcode, url in post_urls:
            post = instaloader.Post.from_shortcode(context, shortcode)
            post_datetime = post.date_utc
            formatted_time = post_datetime.strftime('%Y-%m-%d_%H-%M-%S_UTC')
            file_name = f"{formatted_time}.json"

            if file_name in existing_files:
                print(f"文件重复：{file_name} ")

                if p_found_duplicate_once:
                    p_found_duplicate_twice = True
                else:
                    p_found_duplicate_once = True

                if times >= 2 and p_found_duplicate_twice:
                    print(f"连续两次检测到重复，停止下载！times={times}")
                    stop_download = True
                    break  # 跳出内层 for
                else:
                    break  # 只跳出当前 post_urls 循环，继续下一次 times
            else:
                print(f"添加文件：{file_name}")
                post_updates.append((shortcode, url))
                p_found_duplicate_once = False  # 成功添加则清空第一次重复标志
        download_user("1", username_to_download, post_updates, idx_main, total_users_main)

    # reels update
    max_timer = 65536
    # 注意省略置顶帖文
    for times in range(1, max_timer + 1):
        reel_urls, found_duplicate_twice = process_user_reels(username_to_download, idx_main, total_users_main,
                                                              post_urls, times=times, mode=2)
        print("found_duplicate", found_duplicate_twice)
        if times >= 2 and found_duplicate_twice:
            print(f"连续两次检测到重复，停止：times={times}")
            break


if __name__ == "__main__":
    get_instagram_cookies()
    choose = input("Choose: 1.download 2.redownload 3.update")
    if choose == "1":
        username_to_download = read_following_usernames(FOLLOWING_FILE)
        total_users_main = len(username_to_download)
        print(f"共读取 {total_users_main} 个用户名")

        for idx_main, username in enumerate(username_to_download, start=1):
            print(f"[{idx_main}/{total_users_main}] 正在处理用户：{username}")
            post_urls = get_all_post_urls(username, times=-1, mode=1)
            save_post_urls(username, post_urls, "downloaded_post_urls.txt")
            download_user(choose, username, post_urls, idx_main, total_users_main)
            log_process(username, "Instagram")
            process_user_reels(username, idx_main, total_users_main, post_urls, times=-1, mode=1)
    elif choose == "2":
        username_to_download, user_posts_list = read_failed_downloads()
        total_users_main = len(username_to_download)
        print(f"共读取 {total_users_main} 个用户名")

        for idx_main, (username, post_urls) in enumerate(zip(username_to_download, user_posts_list), 1):
            post_urls = list(post_urls)  # set 转 list
            print(f"[{idx_main}/{total_users_main}] 正在处理用户：{username}")
            download_user(choose, username, post_urls, idx_main, total_users_main)
            log_process(username, "Instagram")
    elif choose == "3":
        username_to_download = read_following_usernames('file_list.txt')
        total_users_main = len(username_to_download)
        print(f"共读取 {total_users_main} 个用户名")

        for idx_main, username in enumerate(username_to_download, start=1):
            print(f"[{idx_main}/{total_users_main}] 正在处理用户：{username}")
            get_latest_downloaded_filename(username, idx_main, total_users_main)
