#!/usr/bin/env python3
"""
zone_summary.py

Generate a full zone summary from a zone directory, including:
- Human-readable resets (always with vnum + readable text)
- Assembles (recipes)
- Scripts (preview or full)
- FULL DETAILS: identify-style output for every unique referenced mob/object

No full-world crawl:
- Lookups are lazy/cached (World).
- Cross-zone VNUM resolution uses zone metadata only when needed.

Usage:
  python3 zone_summary.py <zone_number> [--spells spells.json] [--show-script-code]
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from ..core.world_lookup import World
from .identify_object import format_object_identify
from .identify_mobile import format_mobile_identify
from ..utils.spell_lookup import load_spell_name_map


DIRS = ["north", "east", "south", "west", "up", "down"]

WEAR_SLOTS = [
    "light", "finger", "finger", "neck", "neck", "body", "head", "legs", "feet", "hands",
    "arms", "shield", "about", "waist", "wrist", "wrist", "wield", "hold", "throw",
    "two hands", "ankle", "ankle", "floating", "orb"
]


def _wear_slot_name(pos: int) -> str:
    if 0 <= pos < len(WEAR_SLOTS):
        return WEAR_SLOTS[pos]
    return f"slot#{pos}"


def _door_state_name(state: int) -> str:
    return {0: "open", 1: "closed", 2: "locked"}.get(state, f"state#{state}")


def _flag_desc(flag: int) -> str:
    return {
        0: "always",
        1: "if previous succeeded",
        2: "if previous failed",
        3: "if mob exists",
        4: "if previous was skipped",
        5: "if mob exists",
        6: "if mob missing",
    }.get(flag, f"flag#{flag}")


def _prob_suffix(cmd: str, prob: int) -> str:
    if cmd in ("W", "X", "Y", "Z", "Q") or prob != 100:
        return f" @ {prob}%"
    return ""


def _if_suffix(flag: int) -> str:
    if flag:
        return f" [IF {flag}:{_flag_desc(flag)}]"
    return ""


def _indent(line: str, n: int = 4) -> str:
    return (" " * n) + line


def _safe_listdir(p: Path) -> List[Path]:
    try:
        return sorted([x for x in p.iterdir() if x.is_file()])
    except Exception:
        return []


def _read_json(p: Path) -> Optional[Dict[str, Any]]:
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def render_zone_header(zone: Dict[str, Any], zone_num: int) -> str:
    name = zone.get("name", "(no name)")
    author = zone.get("author", "(unknown)")
    lifespan = zone.get("lifespan", "?")
    reset_mode = zone.get("reset_mode", "?")
    top = zone.get("top", "?")
    plane = zone.get("plane", "?")
    climate = zone.get("climate", "?")
    corpse_room = zone.get("corpse_room", "?")

    lines = []
    lines.append(f"ZONE {zone_num}: {name}")
    lines.append(f"  Author: {author}")
    lines.append(f"  Lifespan: {lifespan}   ResetMode: {reset_mode}   Top: {top}")
    lines.append(f"  Plane: {plane}   Climate: {climate}   CorpseRoom: {corpse_room}")
    return "\n".join(lines) + "\n"


def _cmd_get(c: Dict[str, Any], *keys: str, default: Any = None) -> Any:
    for k in keys:
        if k in c:
            return c[k]
    return default


def parse_zone_cmds(zone: Dict[str, Any]) -> List[Dict[str, Any]]:
    cmds = zone.get("cmds")
    if not isinstance(cmds, list):
        cmds = zone.get("commands")
    if not isinstance(cmds, list):
        cmds = []
    return [x for x in cmds if isinstance(x, dict)]


def render_resets(world: World, zone_cmds: List[Dict[str, Any]], referenced_mobs: Set[int], referenced_objs: Set[int]) -> str:
    lines: List[str] = []
    lines.append("RESETS")
    lines.append("------")

    current_mob: Optional[int] = None
    mob_block_active = False

    last_room_obj: Optional[int] = None
    room_obj_block_active = False

    for idx, c in enumerate(zone_cmds, start=1):
        cmd = str(_cmd_get(c, "cmd", "command", default="?"))
        a1 = int(_cmd_get(c, "arg1", "vnum", default=0) or 0)
        a2 = int(_cmd_get(c, "arg2", "max", default=0) or 0)
        a3 = int(_cmd_get(c, "arg3", "room", default=0) or 0)
        prob = int(_cmd_get(c, "prob", "percent", default=100) or 100)
        flag = int(_cmd_get(c, "flag", default=0) or 0)

        prefix = f"{idx:04d} {cmd}{_if_suffix(flag)}{_prob_suffix(cmd, prob)}: "

        def emit(line: str, indent: int = 0) -> None:
            lines.append(_indent(line, indent) if indent else line)

        if cmd in ("M", "W"):
            mob_block_active = True
            room_obj_block_active = False
            last_room_obj = None

            current_mob = a1
            referenced_mobs.add(a1)
            emit(prefix + f"Load MOB {world.mob_brief(a1)} into ROOM {world.room_brief(a3)} (max {a2})")
            continue

        if cmd in ("E", "Z"):
            referenced_objs.add(a1)
            indent = 4 if mob_block_active and current_mob is not None else 0
            if current_mob is None:
                emit(prefix + f"Equip OBJ {world.obj_brief(a1)} on (no mob context!) pos {a3} ({_wear_slot_name(a3)}) (max {a2})", indent)
            else:
                emit(prefix + f"Equip OBJ {world.obj_brief(a1)} on {world.mob_brief(current_mob)} @ {_wear_slot_name(a3)} (pos {a3}) (max {a2})", indent)
            continue

        if cmd in ("G", "Y"):
            referenced_objs.add(a1)
            indent = 4 if mob_block_active and current_mob is not None else 0
            if current_mob is None:
                emit(prefix + f"Give OBJ {world.obj_brief(a1)} to (no mob context!) (max {a2})", indent)
            else:
                emit(prefix + f"Give OBJ {world.obj_brief(a1)} to {world.mob_brief(current_mob)} inventory (max {a2})", indent)
            continue

        mob_block_active = False
        current_mob = None

        if cmd in ("O", "X"):
            referenced_objs.add(a1)
            room_obj_block_active = True
            last_room_obj = a1
            emit(prefix + f"Load OBJ {world.obj_brief(a1)} into ROOM {world.room_brief(a3)} (max {a2})")
            continue

        if cmd in ("P", "Q"):
            referenced_objs.add(a1)
            referenced_objs.add(a3)
            indent = 4 if room_obj_block_active and last_room_obj == a3 else 0
            emit(prefix + f"Put OBJ {world.obj_brief(a1)} into CONTAINER {world.obj_brief(a3)} (max {a2})", indent)
            continue

        if cmd == "R":
            referenced_objs.add(a2)
            room_obj_block_active = False
            last_room_obj = None
            emit(prefix + f"Remove OBJ {world.obj_brief(a2)} from ROOM {world.room_brief(a1)}")
            continue

        if cmd == "D":
            room_obj_block_active = False
            last_room_obj = None
            dname = DIRS[a2] if 0 <= a2 < len(DIRS) else f"dir#{a2}"
            emit(prefix + f"Set DOOR state in ROOM {world.room_brief(a1)} dir {dname} -> {_door_state_name(a3)}")
            continue

        if cmd == "A":
            room_obj_block_active = False
            last_room_obj = None
            dname = DIRS[a2] if 0 <= a2 < len(DIRS) else f"dir#{a2}"
            if a3 > 0:
                emit(prefix + f"Randomize EXIT in ROOM {world.room_brief(a1)} dir {dname} to a random valid ROOM in zone {a3}")
            else:
                emit(prefix + f"Randomize EXIT in ROOM {world.room_brief(a1)} dir {dname} to a random valid ROOM (global constraints)")
            continue

        room_obj_block_active = False
        last_room_obj = None
        emit(prefix + f"Unhandled command args: arg1={a1} arg2={a2} arg3={a3}")

    return "\n".join(lines) + "\n"


def render_assembles(world: World, zone_dir: Path, referenced_objs: Set[int]) -> str:
    lines: List[str] = []
    lines.append("ASSEMBLES")
    lines.append("---------")

    assemble_dir = zone_dir / "assemble"
    files = _safe_listdir(assemble_dir)
    if not files:
        lines.append("(none)")
        return "\n".join(lines) + "\n"

    for p in files:
        a = _read_json(p)
        if not a or not isinstance(a, dict):
            lines.append(f"- {p.name}: (failed to read)")
            continue

        vnum = int(a.get("vnum", -1))
        if vnum >= 0:
            referenced_objs.add(vnum)

        parts = a.get("parts", [])
        cmds = a.get("cmd", [])
        keywords = a.get("keywords", [])

        lines.append(f"- Result: {world.obj_brief(vnum)}")
        if cmds:
            lines.append(f"    Commands: {', '.join(str(x) for x in cmds)}")
        if keywords:
            lines.append(f"    Keywords: {', '.join(str(x) for x in keywords)}")

        if isinstance(parts, list) and parts:
            lines.append("    Parts:")
            for part in parts:
                try:
                    pv = int(part)
                except Exception:
                    lines.append(f"      - {part}")
                    continue
                referenced_objs.add(pv)
                lines.append(f"      - {world.obj_brief(pv)}")
        else:
            lines.append("    Parts: (none)")

    return "\n".join(lines) + "\n"


def render_scripts(zone_dir: Path, *, show_code: bool, max_lines: int) -> str:
    lines: List[str] = []
    lines.append("SCRIPTS")
    lines.append("-------")

    script_dir = zone_dir / "script"
    files = _safe_listdir(script_dir)
    if not files:
        lines.append("(none)")
        return "\n".join(lines) + "\n"

    for p in files:
        s = _read_json(p)
        if not s or not isinstance(s, dict):
            lines.append(f"- {p.name}: (failed to read)")
            continue

        vnum = s.get("vnum", p.stem)
        name = s.get("name", "(no name)")
        stype = s.get("type", "?")
        trig = s.get("trigger_type", "?")
        level = s.get("level", "?")
        last_edited = s.get("last_edited", "?")

        lines.append(f"- {vnum} \"{name}\"  type={stype} trigger={trig} level={level} last_edited={last_edited}")

        code = s.get("code", "")
        if isinstance(code, str) and code.strip():
            code_lines = code.splitlines()
            if show_code:
                lines.append("    Code:")
                lines.extend(["      " + cl for cl in code_lines])
            else:
                preview = code_lines[:max_lines]
                lines.append(f"    Code (first {min(max_lines, len(code_lines))}/{len(code_lines)} lines):")
                lines.extend(["      " + cl for cl in preview])
                if len(code_lines) > max_lines:
                    lines.append("      ... (truncated; use --show-script-code to include full script text)")
        else:
            lines.append("    Code: (empty)")

    return "\n".join(lines) + "\n"


def render_full_details(
    world: World,
    mobs: Set[int],
    objs: Set[int],
    *,
    spell_map: Dict[int, str],
    show_script_code: bool,
    script_max_lines: int
) -> str:
    lines: List[str] = []
    lines.append("FULL DETAILS")
    lines.append("------------")

    if mobs:
        lines.append("MOBILES")
        lines.append("~~~~~~~")
        for mv in sorted(mobs):
            m = world.load("mobile", mv)
            if not m:
                lines.append(f"[{mv}] (mob missing)\n")
                continue
            lines.append(format_mobile_identify(m, world=world, include_script_code=show_script_code, script_max_lines=script_max_lines).rstrip("\n"))
            lines.append("")

    if objs:
        lines.append("OBJECTS")
        lines.append("~~~~~~~")
        for ov in sorted(objs):
            o = world.load("object", ov)
            if not o:
                lines.append(f"[{ov}] (object missing)\n")
                continue
            lines.append(format_object_identify(o, spell_map).rstrip("\n"))
            lines.append("")

    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description="Generate a full zone summary with full identify text for mobs/objects.")
    ap.add_argument("zone", type=int, help="Zone number (directory name).")
    ap.add_argument("--world-root", default=".", help="Root of world directory (default: .)")
    ap.add_argument("--spells", default=None, help="Path to spells.json (optional).")
    ap.add_argument("--show-script-code", action="store_true", help="Include full script code blocks in mobile/script details.")
    ap.add_argument("--script-max-lines", type=int, default=25, help="Preview max lines when not showing full script code.")
    ap.add_argument("--zone-script-max-lines", type=int, default=30, help="Preview max lines for zone scripts section.")
    args = ap.parse_args()

    world_root = Path(args.world_root).resolve()
    zone_dir = world_root / str(args.zone)
    zone_file = zone_dir / f"{args.zone}.json"
    if not zone_file.exists():
        print(f"ERROR: zone file not found: {zone_file}")
        return 2

    zone = _read_json(zone_file)
    if not zone:
        print(f"ERROR: failed to read zone JSON: {zone_file}")
        return 2

    world = World(world_root)
    world.set_hint_zone(args.zone)

    zone_cmds = parse_zone_cmds(zone)

    referenced_mobs: Set[int] = set()
    referenced_objs: Set[int] = set()

    spell_map = load_spell_name_map(args.spells)

    out: List[str] = []
    out.append(render_zone_header(zone, args.zone))
    out.append(render_resets(world, zone_cmds, referenced_mobs, referenced_objs))
    out.append(render_assembles(world, zone_dir, referenced_objs))
    out.append(render_scripts(zone_dir, show_code=args.show_script_code, max_lines=args.zone_script_max_lines))
    out.append(render_full_details(
        world,
        referenced_mobs,
        referenced_objs,
        spell_map=spell_map,
        show_script_code=args.show_script_code,
        script_max_lines=args.script_max_lines,
    ))

    print("\n".join(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
