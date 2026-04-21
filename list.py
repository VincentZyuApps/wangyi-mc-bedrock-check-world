"""
List Minecraft Bedrock (NetEase) world saves:
  - Folder name
  - World name (levelname.txt)
  - Last saved time (level.dat modification time)
"""

import os
import sys
import io
import argparse
from datetime import datetime

# Force UTF-8 output encoding (for Windows console compatibility)
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# NetEase Minecraft PC save directory: %APPDATA%\MinecraftPC_Netease_PB\minecraftWorlds
WORLDS_DIR = os.path.join(os.environ["APPDATA"], "MinecraftPC_Netease_PB", "minecraftWorlds")


def get_world_info(folder_path, folder_name):
    """Read save info, return dict or None"""
    levelname_path = os.path.join(folder_path, "levelname.txt")
    leveldat_path = os.path.join(folder_path, "level.dat")

    if not os.path.isfile(levelname_path):
        return None

    # Calculate folder total size
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(folder_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if os.path.exists(fp):
                total_size += os.path.getsize(fp)

    # World name
    with open(levelname_path, "r", encoding="utf-8") as f:
        world_name = f.read().strip()

    # Last saved time: from level.dat modification time
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
    """Format bytes to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:6.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:6.2f} TB"


def main():
    parser = argparse.ArgumentParser(description="List Minecraft Bedrock (NetEase) world saves")
    parser.add_argument("--no-color", action="store_true", help="Disable colored output")
    parser.add_argument("--no-emoji", action="store_true", help="Disable emoji icons")
    args = parser.parse_args()

    # ANSI color escape codes
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

    # Emoji icons (Unicode escape sequences)
    # 📂 Folder
    emoji_folder = "\U0001f4c2 " if not args.no_emoji else ""
    # 📜 Scroll
    emoji_list = "\U0001f4dc " if not args.no_emoji else ""
    # 🌍 Globe
    emoji_world = "\U0001f30d " if not args.no_emoji else ""
    # 🕒 Clock
    emoji_time = "\U0001f552 " if not args.no_emoji else ""
    # 💾 Floppy disk
    emoji_size = "\U0001f4be " if not args.no_emoji else ""
    # 📊 Chart
    emoji_count = "\U0001f4ca " if not args.no_emoji else ""

    print(f"\n  {BLUE}{emoji_folder}Reading save directory: {RESET} {CYAN}{WORLDS_DIR}{RESET}\n")
    worlds = []

    for entry in os.listdir(WORLDS_DIR):
        full_path = os.path.join(WORLDS_DIR, entry)
        if os.path.isdir(full_path):
            info = get_world_info(full_path, entry)
            if info:
                worlds.append(info)

# Sort by last saved time descending (most recent first)
    worlds.sort(key=lambda w: w["last_saved"] or datetime.min, reverse=True)

    # Calculate column width (CJK chars count as 2)
    def get_width(s):
        """Calculate display width of string (CJK = 2, others = 1)"""
        width = 0
        for char in s:
            if ord(char) > 127:
                width += 2
            else:
                width += 1
        return width

    def pad_string(s, width):
        """Pad string to specified width, considering CJK chars"""
        current_width = get_width(s)
        return s + " " * (width - current_width)

    max_folder = max((get_width(w["folder"]) for w in worlds), default=8)
    max_name = max((get_width(w["name"]) for w in worlds), default=8)
    max_folder = max(max_folder, 8)   # minimum width for "Folder"
    max_name = max(max_name, 20)      # minimum width for "World Name"

    header_folder = pad_string(f"{emoji_list}Folder", max_folder + (get_width(emoji_list) if not args.no_emoji else 0))
    header_name = pad_string(f"{emoji_world}World Name", max_name + (get_width(emoji_world) if not args.no_emoji else 0))
    header_time = f"{emoji_time}Last Saved".ljust(19 + (get_width(emoji_time) if not args.no_emoji else 0))
    header_size = f"{emoji_size}Size"

    print(f"  {BOLD}No.   {header_folder}  {header_name}  {header_time}  {header_size}{RESET}")
    print(f"  ----  {'-' * max_folder}  {'-' * max_name}  {'-' * 19}  {'-' * 10}")

    for i, w in enumerate(worlds, 1):
        folder = pad_string(w["folder"], max_folder)
        name = pad_string(w["name"], max_name)
        time_str = (w["last_saved"].strftime("%Y-%m-%d %H:%M:%S") if w["last_saved"] else "Unknown").ljust(19)
        size_str = format_size(w["size"])

        # Color output
        idx_str = f"{YELLOW}{i:>4}{RESET}"
        folder_str = f"{CYAN}{folder}{RESET}"
        name_str = f"{GREEN}{name}{RESET}"
        time_out = f"{MAGENTA}{time_str}{RESET}"
        size_out = f"{YELLOW}{size_str}{RESET}"

        print(f"  {idx_str}  {folder_str}  {name_str}  {time_out}  {size_out}")

    print(f"\n  {BLUE}{emoji_count}Total: {len(worlds)} saves{RESET}\n")


if __name__ == "__main__":
    main()
