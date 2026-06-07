from __future__ import annotations

import re
from collections import Counter, defaultdict

from inspect_common import heading, parse_common_args, print_json_or_pretty, resolve_world, section


ASCII_RE = re.compile(rb"[\x20-\x7E]{3,}")
PATTERNS = {
    "local_player": ["local_player"],
    "playerish": ["minecraft:player", "playerPermissionsLevel", "PlayerGameMode"],
    "positionish": ["Pos", "Rotation", "DimensionId", "SpawnBlockPosition", "DeathPosition"],
    "attributeish": ["Attributes", "minecraft:health", "minecraft:player.hunger", "minecraft:player.saturation"],
    "inventoryish": ["Armor", "Inventory", "Offhand", "Mainhand", "Count", "Damage", "WasPickedUp"],
    "entityish": ["identifier", "UniqueID", "Motion", "OnGround", "AutonomousEntity"],
    "recipeish": ["recipeId", "WorkBench", "stonecutter_", "Jukebox_recipeId"],
    "block_item_names": ["minecraft:"],
}


def categorize(text: str) -> list[str]:
    matches = []
    for name, needles in PATTERNS.items():
        if any(needle in text for needle in needles):
            matches.append(name)
    return matches or ["uncategorized"]


def main() -> None:
    parser = parse_common_args("Inspect db string-pattern families for one world.")
    args = parser.parse_args()
    world = resolve_world(args)

    by_category = defaultdict(list)
    file_hits: dict[str, Counter[str]] = {}
    for path in sorted((world.path / "db").iterdir(), key=lambda p: p.name.lower()):
        if path.suffix.lower() not in {".log", ".ldb"}:
            continue
        seen = set()
        strings = []
        for raw in ASCII_RE.findall(path.read_bytes()):
            text = raw.decode("ascii", errors="replace")
            if text not in seen:
                seen.add(text)
                strings.append(text)
        counter: Counter[str] = Counter()
        for text in strings:
            for category in categorize(text):
                counter[category] += 1
                if len(by_category[category]) < 20 and text not in by_category[category]:
                    by_category[category].append(text)
        file_hits[path.name] = counter

    result = {
        "folder": world.folder,
        "world_name": world.name,
        "categories": {
            name: {"count": len(samples), "samples": samples}
            for name, samples in sorted(by_category.items())
        },
        "files": {name: dict(counter.most_common()) for name, counter in sorted(file_hits.items())},
    }

    if args.json:
        print_json_or_pretty(result, True)
        return

    print(heading(f"DB Pattern Inspect | {world.name}"))
    print(f"📁 Folder: {world.folder}")
    print(section("Categories", "🗂️"))
    for name, info in result["categories"].items():
        print(f"- {name}: {info['count']} sample strings")
        for sample in info["samples"][:12]:
            print(f"  {sample}")
    print(section("Per-file counts", "📊"))
    for name, counts in result["files"].items():
        if not counts:
            continue
        joined = ", ".join(f"{key}={value}" for key, value in counts.items())
        print(f"- {name}: {joined}")


if __name__ == "__main__":
    main()
