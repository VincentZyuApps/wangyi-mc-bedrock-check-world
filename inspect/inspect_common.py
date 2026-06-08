from __future__ import annotations

import argparse
import json
import os
import struct
from dataclasses import dataclass
from pathlib import Path
from typing import Any


WORLD_ROOT = Path.home() / "AppData/Roaming/MinecraftPC_Netease_PB/minecraftWorlds"
ESC = "\x1b"
RESET = f"{ESC}[0m"
BOLD = f"{ESC}[1m"
DIM = f"{ESC}[2m"
CYAN = f"{ESC}[36m"
GREEN = f"{ESC}[32m"
YELLOW = f"{ESC}[33m"
MAGENTA = f"{ESC}[35m"
RED = f"{ESC}[31m"
BLUE = f"{ESC}[34m"
CLEAR_LINE = f"{ESC}[2K"


@dataclass
class WorldEntry:
    index: int
    folder: str
    name: str
    path: Path


def format_size(size: int) -> str:
    units = ["B", "KB", "MB", "GB"]
    value = float(size)
    for unit in units:
        if value < 1024 or unit == units[-1]:
            return f"{value:.2f} {unit}"
        value /= 1024
    return f"{size} B"


def safe_read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        return None
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="replace").strip()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def list_worlds(root: Path = WORLD_ROOT) -> list[WorldEntry]:
    worlds: list[WorldEntry] = []
    for path in sorted(root.iterdir(), key=lambda p: p.name.lower()):
        if not path.is_dir() or path.name.startswith("+++"):
            continue
        levelname = safe_read_text(path / "levelname.txt")
        if levelname is None:
            continue
        worlds.append(
            WorldEntry(
                index=len(worlds) + 1,
                folder=path.name,
                name=levelname,
                path=path,
            )
        )
    return worlds


def parse_common_args(description: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--index", type=int, help="Select world by 1-based index from the world list.")
    parser.add_argument("--folder", help="Select world by folder name.")
    parser.add_argument("--worlds-root", type=Path, default=WORLD_ROOT)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--debug", action="store_true", help="Show heavier and more detailed output.")
    return parser


def style(text: str, *codes: str) -> str:
    return "".join(codes) + text + RESET


def heading(text: str, emoji: str = "📌") -> str:
    return style(f"{emoji} {text}", BOLD, CYAN)


def section(text: str, emoji: str = "•") -> str:
    return style(f"{emoji} {text}", BOLD, BLUE)


def ok(text: str) -> str:
    return style(text, GREEN)


def warn(text: str) -> str:
    return style(text, YELLOW)


def err(text: str) -> str:
    return style(text, RED)


def muted(text: str) -> str:
    return style(text, DIM)


def move_cursor_up(lines: int) -> None:
    if lines > 0:
        print(f"{ESC}[{lines}A", end="")


def render_picker_frame(worlds: list[WorldEntry], selected: int) -> int:
    lines = 0
    print(heading("Interactive World Picker", "🎮"))
    lines += 1
    print(muted("Use Up/Down and Enter. Press Esc to cancel."))
    lines += 1
    print()
    lines += 1
    print(section(f"Current selection: [{worlds[selected].index:02d}] {worlds[selected].name} ({worlds[selected].folder})", "🧭"))
    lines += 1
    for i, world in enumerate(worlds):
        marker = ">" if i == selected else " "
        line = f"{marker} [{world.index:02d}] {world.name}  ({world.folder})"
        if i == selected:
            print(style(line, BOLD, MAGENTA))
        else:
            print(line)
        lines += 1
    return lines


def clear_rendered_lines(lines: int) -> None:
    move_cursor_up(lines)
    for i in range(lines):
        print(CLEAR_LINE, end="")
        if i < lines - 1:
            print()
    if lines > 1:
        move_cursor_up(lines - 1)


def _read_key_windows() -> str:
    import msvcrt

    key = msvcrt.getch()
    if key in {b"\x00", b"\xe0"}:
        key2 = msvcrt.getch()
        if key2 == b"H":
            return "up"
        if key2 == b"P":
            return "down"
        return "other"
    if key == b"\r":
        return "enter"
    if key == b"\x1b":
        return "esc"
    return "other"


def interactive_pick_world(worlds: list[WorldEntry]) -> WorldEntry:
    if not worlds:
        raise SystemExit("No worlds found.")
    selected = 0
    rendered_lines = render_picker_frame(worlds, selected)
    while True:
        key = _read_key_windows() if os.name == "nt" else input("Enter index: ").strip()
        if key == "up":
            selected = (selected - 1) % len(worlds)
            clear_rendered_lines(rendered_lines)
            rendered_lines = render_picker_frame(worlds, selected)
        elif key == "down":
            selected = (selected + 1) % len(worlds)
            clear_rendered_lines(rendered_lines)
            rendered_lines = render_picker_frame(worlds, selected)
        elif key == "enter":
            clear_rendered_lines(rendered_lines)
            print()
            print(ok(f"✅ Selected: [{worlds[selected].index:02d}] {worlds[selected].name} ({worlds[selected].folder})"))
            return worlds[selected]
        elif key == "esc":
            raise SystemExit("Selection cancelled.")
        else:
            if os.name != "nt":
                try:
                    index = int(key)
                except ValueError:
                    continue
                if 1 <= index <= len(worlds):
                    clear_rendered_lines(rendered_lines)
                    print()
                    print(ok(f"✅ Selected: [{worlds[index - 1].index:02d}] {worlds[index - 1].name} ({worlds[index - 1].folder})"))
                    return worlds[index - 1]


def resolve_world(args: argparse.Namespace) -> WorldEntry:
    worlds = list_worlds(args.worlds_root)
    if args.index is not None and 1 <= args.index <= len(worlds):
        return worlds[args.index - 1]
    if args.folder:
        match = next((world for world in worlds if world.folder == args.folder), None)
        if match is not None:
            return match
    return interactive_pick_world(worlds)


def folder_size(path: Path) -> int:
    total = 0
    for child in path.rglob("*"):
        if child.is_file():
            total += child.stat().st_size
    return total


def read_exact(data: memoryview, offset: int, size: int) -> tuple[bytes, int]:
    end = offset + size
    if end > len(data):
        raise EOFError(f"expected {size} bytes, got {len(data) - offset}")
    return bytes(data[offset:end]), end


def read_u16_le(data: memoryview, offset: int) -> tuple[int, int]:
    raw, offset = read_exact(data, offset, 2)
    return struct.unpack("<H", raw)[0], offset


def read_utf8(data: memoryview, offset: int) -> tuple[str, int]:
    length, offset = read_u16_le(data, offset)
    raw, offset = read_exact(data, offset, length)
    return raw.decode("utf-8", errors="replace"), offset


def parse_nbt_payload(data: memoryview, offset: int, tag_id: int) -> tuple[Any, int]:
    if tag_id == 0:
        return None, offset
    if tag_id == 1:
        raw, offset = read_exact(data, offset, 1)
        return struct.unpack("<b", raw)[0], offset
    if tag_id == 2:
        raw, offset = read_exact(data, offset, 2)
        return struct.unpack("<h", raw)[0], offset
    if tag_id == 3:
        raw, offset = read_exact(data, offset, 4)
        return struct.unpack("<i", raw)[0], offset
    if tag_id == 4:
        raw, offset = read_exact(data, offset, 8)
        return struct.unpack("<q", raw)[0], offset
    if tag_id == 5:
        raw, offset = read_exact(data, offset, 4)
        return struct.unpack("<f", raw)[0], offset
    if tag_id == 6:
        raw, offset = read_exact(data, offset, 8)
        return struct.unpack("<d", raw)[0], offset
    if tag_id == 7:
        raw, offset = read_exact(data, offset, 4)
        length = struct.unpack("<i", raw)[0]
        raw, offset = read_exact(data, offset, length)
        return list(raw), offset
    if tag_id == 8:
        return read_utf8(data, offset)
    if tag_id == 9:
        raw, offset = read_exact(data, offset, 1)
        child_id = raw[0]
        raw, offset = read_exact(data, offset, 4)
        length = struct.unpack("<i", raw)[0]
        values = []
        for _ in range(length):
            value, offset = parse_nbt_payload(data, offset, child_id)
            values.append(value)
        return values, offset
    if tag_id == 10:
        result: dict[str, Any] = {}
        while True:
            raw, offset = read_exact(data, offset, 1)
            child_id = raw[0]
            if child_id == 0:
                return result, offset
            try:
                name, offset = read_utf8(data, offset)
                value, offset = parse_nbt_payload(data, offset, child_id)
                result[name] = value
            except Exception as exc:
                result["_parse_error"] = str(exc)
                result["_parse_error_offset"] = offset
                result["_parse_error_tag_id"] = child_id
                return result, len(data)
    if tag_id == 11:
        raw, offset = read_exact(data, offset, 4)
        length = struct.unpack("<i", raw)[0]
        raw, offset = read_exact(data, offset, 4 * length)
        return list(struct.unpack(f"<{length}i", raw)), offset
    if tag_id == 12:
        raw, offset = read_exact(data, offset, 4)
        length = struct.unpack("<i", raw)[0]
        raw, offset = read_exact(data, offset, 8 * length)
        return list(struct.unpack(f"<{length}q", raw)), offset
    raise ValueError(f"unknown tag id {tag_id}")


def parse_leveldat(leveldat_path: Path) -> dict[str, Any]:
    raw = leveldat_path.read_bytes()
    offset = 8 if len(raw) >= 9 and raw[8] == 0x0A else 0
    data = memoryview(raw)
    tag_id = raw[offset]
    name, next_offset = read_utf8(data, offset + 1)
    payload, _ = parse_nbt_payload(data, next_offset, tag_id)
    return {
        "offset": offset,
        "root_tag": tag_id,
        "root_name": name,
        "payload": payload,
    }


def parse_local_player(world_path: Path) -> dict[str, Any]:
    db_dir = world_path / "db"
    for path in sorted(db_dir.glob("*.log")):
        raw = path.read_bytes()
        idx = raw.find(b"local_player")
        if idx < 0:
            continue
        start = raw.find(b"\x0A\x00\x00", idx + len(b"local_player"), idx + len(b"local_player") + 64)
        if start < 0:
            continue
        data = memoryview(raw[start:])
        tag_id = raw[start]
        name, next_offset = read_utf8(data, 1)
        payload, _ = parse_nbt_payload(data, next_offset, tag_id)
        if isinstance(payload, dict):
            payload["_source_log"] = path.name
            return payload
    raise FileNotFoundError("local_player record not found in db logs")


def print_json_or_pretty(payload: Any, as_json: bool) -> None:
    if as_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    if isinstance(payload, dict):
        for key, value in payload.items():
            print(f"{key}: {value}")
        return
    print(payload)
