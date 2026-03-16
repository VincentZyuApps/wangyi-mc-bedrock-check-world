"""
列出所有 Minecraft 基岩版（网易）存档信息：
  - 文件夹名
  - 世界名称（levelname.txt）
  - 最后保存时间（level.dat 修改时间）
"""

import os
import argparse
from datetime import datetime

# 网易我的世界电脑版存档固定路径：%APPDATA%\MinecraftPC_Netease_PB\minecraftWorlds
WORLDS_DIR = os.path.join(os.environ["APPDATA"], "MinecraftPC_Netease_PB", "minecraftWorlds")


def get_world_info(folder_path, folder_name):
    """读取单个存档的信息，返回 dict 或 None"""
    levelname_path = os.path.join(folder_path, "levelname.txt")
    leveldat_path = os.path.join(folder_path, "level.dat")

    if not os.path.isfile(levelname_path):
        return None

    # 计算文件夹总大小
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(folder_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if os.path.exists(fp):
                total_size += os.path.getsize(fp)

    # 世界名称
    with open(levelname_path, "r", encoding="utf-8") as f:
        world_name = f.read().strip()

    # 最后保存时间：取 level.dat 的修改时间
    if os.path.isfile(leveldat_path):
        mtime = os.path.getmtime(leveldat_path)
        last_saved = datetime.fromtimestamp(mtime)
    else:
        last_saved = None

    return {
        "folder": folder_name,
        "name": world_name,
        "last_saved": last_saved,
        "size": total_size,
    }


def format_size(size_bytes):
    """格式化字节数为人类可读格式"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:6.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:6.2f} TB"


def main():
    parser = argparse.ArgumentParser(description="列出 Minecraft 基岩版（网易）存档信息")
    parser.add_argument("--no-color", action="store_true", help="禁用颜色输出")
    parser.add_argument("--no-emoji", action="store_true", help="禁用 Emoji 输出")
    args = parser.parse_args()

    # ANSI 颜色转义码
    if args.no_color:
        CYAN = GREEN = YELLOW = BLUE = MAGENTA = RESET = BOLD = ""
    else:
        CYAN = "\033[36m"
        GREEN = "\033[32m"
        YELLOW = "\033[33m"
        BLUE = "\033[34m"
        MAGENTA = "\033[35m"
        RESET = "\033[0m"
        BOLD = "\033[1m"

    emoji_folder = "📂 " if not args.no_emoji else ""
    emoji_list = "📜 " if not args.no_emoji else ""
    emoji_world = "🌍 " if not args.no_emoji else ""
    emoji_time = "🕒 " if not args.no_emoji else ""
    emoji_size = "💾 " if not args.no_emoji else ""
    emoji_count = "📊 " if not args.no_emoji else ""

    print(f"\n  {BLUE}{emoji_folder}正在读取存档目录:{RESET} {CYAN}{WORLDS_DIR}{RESET}\n")
    worlds = []

    for entry in os.listdir(WORLDS_DIR):
        full_path = os.path.join(WORLDS_DIR, entry)
        if os.path.isdir(full_path):
            info = get_world_info(full_path, entry)
            if info:
                worlds.append(info)

    # 按最后保存时间倒序排列（最近的在前）
    worlds.sort(key=lambda w: w["last_saved"] or datetime.min, reverse=True)

    # 计算列宽（处理中文字符宽度）
    def get_width(s):
        """计算字符串的显示宽度（中文算2，英文算1）"""
        width = 0
        for char in s:
            if ord(char) > 127:
                width += 2
            else:
                width += 1
        return width

    def pad_string(s, width):
        """用空格填充字符串到指定宽度，考虑中文字符"""
        current_width = get_width(s)
        return s + " " * (width - current_width)

    max_folder = max((get_width(w["folder"]) for w in worlds), default=8)
    max_name = max((get_width(w["name"]) for w in worlds), default=8)
    max_folder = max(max_folder, 8)   # "文件夹名" 占位
    max_name = max(max_name, 20)      # "世界名称" 占位

    header_folder = pad_string(f"{emoji_list}文件夹名", max_folder + (get_width(emoji_list) if not args.no_emoji else 0))
    header_name = pad_string(f"{emoji_world}世界名称", max_name + (get_width(emoji_world) if not args.no_emoji else 0))
    header_time = f"{emoji_time}最后保存时间".ljust(19 + (get_width(emoji_time) if not args.no_emoji else 0))
    header_size = f"{emoji_size}大小"

    print(f"  {BOLD}{'序号':>4}  {header_folder}  {header_name}  {header_time}  {header_size}{RESET}")
    print(f"  {'─' * 4}  {'─' * max_folder}  {'─' * max_name}  {'─' * 19}  {'─' * 10}")

    for i, w in enumerate(worlds, 1):
        folder = pad_string(w["folder"], max_folder)
        name = pad_string(w["name"], max_name)
        time_str = (w["last_saved"].strftime("%Y-%m-%d %H:%M:%S") if w["last_saved"] else "未知").ljust(19)
        size_str = format_size(w["size"])

        # 斑马纹或高亮处理
        idx_str = f"{YELLOW}{i:>4}{RESET}"
        folder_str = f"{CYAN}{folder}{RESET}"
        name_str = f"{GREEN}{name}{RESET}"
        time_out = f"{MAGENTA}{time_str}{RESET}"
        size_out = f"{YELLOW}{size_str}{RESET}"

        print(f"  {idx_str}  {folder_str}  {name_str}  {time_out}  {size_out}")

    print(f"\n  {BLUE}{emoji_count}共 {len(worlds)} 个存档{RESET}\n")


if __name__ == "__main__":
    main()
