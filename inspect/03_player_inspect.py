from __future__ import annotations

from inspect_common import heading, parse_common_args, parse_local_player, print_json_or_pretty, resolve_world, section, warn


def attributes_to_map(attributes: list[object]) -> dict[str, dict]:
    result = {}
    for item in attributes:
        if isinstance(item, dict) and isinstance(item.get("Name"), str):
            result[item["Name"]] = item
    return result


def main() -> None:
    parser = parse_common_args("Inspect local_player status.")
    args = parser.parse_args()
    world = resolve_world(args)

    payload = parse_local_player(world.path)
    attrs = attributes_to_map(payload.get("Attributes", []))
    result = {
        "folder": world.folder,
        "world_name": world.name,
        "source_log": payload.get("_source_log"),
        "Pos": payload.get("Pos"),
        "Rotation": payload.get("Rotation"),
        "DimensionId": payload.get("DimensionId"),
        "PlayerGameMode": payload.get("PlayerGameMode"),
        "SelectedInventorySlot": payload.get("SelectedInventorySlot"),
        "SpawnBlockPosition": [
            payload.get("SpawnBlockPositionX"),
            payload.get("SpawnBlockPositionY"),
            payload.get("SpawnBlockPositionZ"),
        ],
        "DeathPosition": [
            payload.get("DeathPositionX"),
            payload.get("DeathPositionY"),
            payload.get("DeathPositionZ"),
        ],
        "health": attrs.get("minecraft:health"),
        "hunger": attrs.get("minecraft:player.hunger"),
        "saturation": attrs.get("minecraft:player.saturation"),
        "experience": attrs.get("minecraft:player.experience"),
        "all_keys": sorted(payload.keys()),
        "parse_error": payload.get("_parse_error"),
    }

    if args.json:
        print_json_or_pretty(result, True)
        return

    print(heading(f"Player Inspect | {world.name}"))
    print(f"📁 Folder: {world.folder}")
    print(f"📜 Source log: {result['source_log']}")
    print(section("Player state", "🧍"))
    for key in [
        "Pos",
        "Rotation",
        "DimensionId",
        "PlayerGameMode",
        "SelectedInventorySlot",
        "SpawnBlockPosition",
        "DeathPosition",
    ]:
        print(f"{key}: {result[key]}")
    print(section("Attributes", "❤️"))
    for key in ["health", "hunger", "saturation", "experience"]:
        print(f"  {key}: {result[key]}")
    if result["parse_error"]:
        print(warn(f"⚠️ Parse tail warning: {result['parse_error']}"))


if __name__ == "__main__":
    main()
