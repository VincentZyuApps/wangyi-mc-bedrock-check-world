from __future__ import annotations

from inspect_common import (
    folder_size,
    format_size,
    heading,
    load_json,
    ok,
    parse_common_args,
    resolve_world,
    safe_read_text,
    section,
    warn,
)


def main() -> None:
    parser = parse_common_args("Inspect world overview and NetEase sidecars.")
    args = parser.parse_args()
    world = resolve_world(args)

    config = {}
    config_path = world.path / "config"
    if config_path.exists():
        try:
            config = load_json(config_path)
        except Exception as exc:
            config = {"_error": str(exc)}

    behavior_packs = []
    resource_packs = []
    for name, target in [
        ("netease_world_behavior_packs.json", behavior_packs),
        ("netease_world_resource_packs.json", resource_packs),
    ]:
        path = world.path / name
        if path.exists():
            try:
                target.extend(load_json(path))
            except Exception:
                pass

    result = {
        "folder": world.folder,
        "world_name": world.name,
        "path": str(world.path),
        "folder_size": folder_size(world.path),
        "folder_size_h": format_size(folder_size(world.path)),
        "levelname_txt": safe_read_text(world.path / "levelname.txt"),
        "has_level_dat": (world.path / "level.dat").exists(),
        "has_level_dat_old": (world.path / "level.dat_old").exists(),
        "config": config,
        "behavior_pack_count": len(behavior_packs),
        "resource_pack_count": len(resource_packs),
        "behavior_packs": behavior_packs,
        "resource_packs": resource_packs,
    }

    if args.json:
        from inspect_common import print_json_or_pretty

        print_json_or_pretty(result, True)
        return

    print(heading(f"World Overview | {result['world_name']}"))
    print(f"📁 Folder: {result['folder']}")
    print(f"🛣️ Path: {result['path']}")
    print(f"💾 Size: {result['folder_size_h']}")
    print(f"📝 levelname.txt: {result['levelname_txt']}")
    print(f"📦 level.dat: {ok(str(result['has_level_dat']))}")
    print(f"🗂️ level.dat_old: {ok(str(result['has_level_dat_old']))}")
    if isinstance(config, dict):
        world_record = config.get("world_record", {})
        print(section("Config highlights", "⚙️"))
        for key in ["archive_id", "uid"]:
            if key in config:
                print(f"  {key}: {config[key]}")
        if isinstance(world_record, dict):
            for key in ["name", "slogan", "level_id", "allow_pc", "is_multiple_game", "max_member_size"]:
                if key in world_record:
                    print(f"  world_record.{key}: {world_record[key]}")
    print(section("Pack counts", "📚"))
    print(f"  behavior packs: {len(behavior_packs)}")
    print(f"  resource packs: {len(resource_packs)}")
    if not behavior_packs and not resource_packs:
        print(warn("  no pack sidecars found"))


if __name__ == "__main__":
    main()
