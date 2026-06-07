from __future__ import annotations

from inspect_common import heading, parse_common_args, parse_local_player, print_json_or_pretty, resolve_world, section, warn


def summarize_item(item: object, index: int) -> dict:
    if not isinstance(item, dict):
        return {"index": index, "raw": item}
    summary = {
        "index": index,
        "Name": item.get("Name"),
        "Count": item.get("Count"),
        "Damage": item.get("Damage"),
        "Slot": item.get("Slot"),
        "WasPickedUp": item.get("WasPickedUp"),
    }
    tag = item.get("tag")
    if isinstance(tag, dict):
        summary["tag_keys"] = sorted(tag.keys())
    if item.get("Block") is not None:
        summary["Block"] = item.get("Block")
    if item.get("CanPlaceOn") is not None:
        summary["CanPlaceOn"] = item.get("CanPlaceOn")
    return summary


def normalize_container(value: object) -> list[dict]:
    if isinstance(value, list):
        return [summarize_item(item, index) for index, item in enumerate(value)]
    if isinstance(value, dict):
        return [summarize_item(value, 0)]
    if value is None:
        return []
    return [{"index": 0, "raw": value}]


def non_empty_items(items: list[dict]) -> list[dict]:
    return [item for item in items if item.get("Name") or item.get("Count")]


def main() -> None:
    parser = parse_common_args("Inspect local_player inventory containers.")
    args = parser.parse_args()
    world = resolve_world(args)

    payload = parse_local_player(world.path)
    containers = {
        "Armor": normalize_container(payload.get("Armor")),
        "Inventory": normalize_container(payload.get("Inventory")),
        "EnderChestInventory": normalize_container(payload.get("EnderChestInventory")),
        "Mainhand": normalize_container(payload.get("Mainhand")),
        "Offhand": normalize_container(payload.get("Offhand")),
    }
    result = {
        "folder": world.folder,
        "world_name": world.name,
        "source_log": payload.get("_source_log"),
        "containers": {
            name: {
                "total_slots_seen": len(items),
                "non_empty_count": len(non_empty_items(items)),
                "non_empty_items": non_empty_items(items),
            }
            for name, items in containers.items()
        },
        "parse_error": payload.get("_parse_error"),
    }

    if args.json:
        print_json_or_pretty(result, True)
        return

    print(heading(f"Inventory Inspect | {world.name}"))
    print(f"📁 Folder: {world.folder}")
    print(f"📜 Source log: {result['source_log']}")
    for name, info in result["containers"].items():
        print(section(name, "🎒"))
        print(f"  total slots/items seen: {info['total_slots_seen']}")
        print(f"  non-empty items: {info['non_empty_count']}")
        for item in info["non_empty_items"][:20]:
            print(f"  - {item}")
        if not info["non_empty_items"]:
            print("  - <none>")
    if result["parse_error"]:
        print(warn(f"⚠️ Parse tail warning: {result['parse_error']}"))


if __name__ == "__main__":
    main()
