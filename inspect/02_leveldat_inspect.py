from __future__ import annotations

from inspect_common import heading, parse_common_args, parse_leveldat, print_json_or_pretty, resolve_world, section


KEYS = [
    "LevelName",
    "GameType",
    "Difficulty",
    "InventoryVersion",
    "NetworkVersion",
    "RandomSeed",
    "SpawnX",
    "SpawnY",
    "SpawnZ",
    "Time",
    "LastPlayed",
    "PlayerHasDied",
    "neteaseEncryptFlag",
    "showcoordinates",
    "keepinventory",
    "pvp",
]


def main() -> None:
    parser = parse_common_args("Inspect level.dat metadata.")
    args = parser.parse_args()
    world = resolve_world(args)

    parsed = parse_leveldat(world.path / "level.dat")
    payload = parsed["payload"]
    abilities = payload.get("abilities", {}) if isinstance(payload, dict) else {}
    experiments = payload.get("experiments", {}) if isinstance(payload, dict) else {}
    result = {
        "folder": world.folder,
        "world_name": world.name,
        "nbt_offset": parsed["offset"],
        "summary": {key: payload.get(key) for key in KEYS},
        "abilities": abilities,
        "experiments": experiments,
        "all_keys": sorted(payload.keys()),
    }

    if args.json:
        print_json_or_pretty(result, True)
        return

    print(heading(f"level.dat Inspect | {world.name}"))
    print(f"📁 Folder: {world.folder}")
    print(f"🧱 NBT offset: {parsed['offset']}")
    print(section("Summary", "📋"))
    for key, value in result["summary"].items():
        print(f"  {key}: {value}")
    print(section("Abilities", "🪽"))
    for key, value in abilities.items():
        print(f"  {key}: {value}")
    print(section("Experiments", "🧪"))
    for key, value in experiments.items():
        print(f"  {key}: {value}")
    print(f"🔢 Top-level keys: {len(result['all_keys'])}")


if __name__ == "__main__":
    main()
