#!/usr/bin/env python3
"""
identify_object.py

Full object identify output (as close as practical to in-game identify).
NO runtime source-code parsing: spell names come from spell_lookup.py (spells.json).

Notes:
- We print "identify-style" lines, plus a final "Other attributes" JSON dump so no
  object data is lost even if we don't decode some field yet.
"""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional

from ..utils.spell_lookup import spell_name


PLAYER_ITEM_TYPES: List[str] = [
    "UNDEFINED","Light","Scroll","Wand","Staff","Weapon","Fire-Weapon","Missile","Treasure","Armor","Potion","Worn",
    "Other","Trash","Trap","Container","Note","Liquid Container","Key","Food","Money","Pen","Boat","Fountain","Portal",
    "Herb","Instrument","Warpstone","Airship","Ammunition","For Sale Sign","Recall Item","Orb","UNUSED","UNUSED",
    "Grant Scroll","Forage","Mana Spike","Token","Reward","Dye","Event Scroll","Reroll Scroll","\n"
]

PLAYER_WEAR_BITS: List[str] = [
    "Take","Finger","Neck","Body","Head","Face","Ear","Legs","Feet","Hands","Arms","Shield","About","Waist","Wrist",
    "Wield","Hold","Throw","Two Hands","Ankle","Floating","Orb","\n"
]

PLAYER_ITEM_FLAG_BITS: List[str] = [
    "Glowing","Humming","!Rent","!Donate","!Invis","Invisible","Magical","Cursed","Blessed","!Good","!Evil","!Neutral",
    "^UNUSED","^Unused","^UNUSED","^UNUSED","!Sell","^UNUSED","^UNUSED","Remort-Only","!Mortal","Limited","Quest",
    "Junk","!Purge","^UNUSED","^UNUSED","Hidden","Unused","^UNUSED","UNUSED","String-Parsed","!Locate","Bonding",
    "UNUSED","Inset","UNUSED","UNUSED","UNUSED","!Elf","!Dwarf","!Human","!Neuter","!Male","!Female","\n"
]

AFFECTED_BITS: List[str] = [
    "BLIND","INVIS","DET-ALIGN","DET-INVIS","DET-MAGIC","SENSE-LIFE","WATWALK","SANCT","^UNUSED","^CURSE","INFRA",
    "POISON","PROT-EVIL","PROT-GOOD","^SLEEP","^!TRACK","^UNUSED","^UNUSED","SNEAK","HIDE","^UNUSED","CHARM",
    "^UNUSED","FLY","PASSDOOR","^UNUSED","^UNUSED","^UNUSED","^UNUSED","^UNUSED","^UNUSED","^UNUSED","TRUESIGHT",
    "PENUMBRA","SPIRIT","WRAITH","SCALE","SHIFT","BLOODLUST","SHADOW","ILLUSION","METAMORPH","HEAT","FLAME","FROST",
    "SHOCK","ENERGY","BLUNT","PIERCE","SLASH","ENTROPY","IMPACT",
    "^HASTE","^SLOW","^BURNING","^FROZEN","^PARALYZED","^CRUSADERS_MIGHT","^CRUSADERS_MIGHT_I",
    "^CRUSADERS_MIGHT_II","^CRUSADERS_MIGHT_III","^RADIATION","^KINETIC_ABSORB","\n"
]

PLAYER_APPLY_TYPES: List[str] = [
    "NONE","Strength","Dexterity","Intelligence","Wisdom","Constitution","Charisma","Class","Level","Age","Weight",
    "Height","Max-Mana","Max-Hit","Max-Move","Gold","Exp","Armor","Hitroll","Damroll","UNUSED","UNUSED","UNUSED",
    "UNUSED","Saving Throw","UNUSED","Apply-All","HP-Regen","Mana-Regen","Move-Regen","Regen-All","UNUSED",
    "Magic-Points","Attacks","PSPs","Dam-Enhance","UNUSED","UNUSED","UNUSED","SpellFail","Eat_Spell","UNUSED",
    "Resist Fire","Resist Cold","Resist Elec","Resist Energy","Resist Blunt","Resist Pierce","Resist Slash",
    "Resist Entropy","Resist Impact","SpellDam","SpellDam2","SpellEnhance","UNUSED","UNUSED","UNUSED","Casts",
    "SpellCap","SummonCap","Haste","HP","Mana","Move","Quest Points","Spell Damage Cap",
    "UNUSED","UNUSED","UNUSED","UNUSED","UNUSED","UNUSED","UNUSED","UNUSED","UNUSED","UNUSED","UNUSED","UNUSED",
    "UNUSED","UNUSED","UNUSED","UNUSED","UNUSED","UNUSED","UNUSED","\n"
]

APPLY_CONDITIONS: List[str] = [
    "",
    "Spell",
    "Daytime",
    "Nighttime",
    "Good",
    "Evil",
    "Neutral",
    "Full Moon",
    "Waxing Moon",
    "Waning Moon",
    "New Moon",
    "Race",
    "\n",
]

DRINKS: List[str] = [
    "water","beer","wine","ale","dark ale","whiskey","lemonade","firebreather","local specialty","slime mold juice",
    "milk","tea","coffee","blood","salt water","clear water","dr. pepper","cherry slurpee","milk shake","klava",
    "jump juice","\n"
]

PLAYER_EVENT_NAMES: List[str] = [
    "Double Exp","Double HP","Double Mana","Triple EXP","Double Dam Cap","Double SPell Dam Cap","Double Heals",
    "Fast Regen","Load Rates","\n"
]


def _is_binary_string(s: str) -> bool:
    return bool(s) and all(ch in "01" for ch in s)


def parse_bitvector(v: Any) -> int:
    if v is None:
        return 0
    if isinstance(v, bool):
        return int(v)
    if isinstance(v, int):
        return v
    if isinstance(v, float):
        return int(v)
    if isinstance(v, str):
        s = v.strip()
        if s == "":
            return 0
        if s.startswith(("0x", "0X")):
            return int(s, 16)
        if _is_binary_string(s):
            return int(s, 2)
        if re.fullmatch(r"-?\d+", s):
            return int(s, 10)
        if re.fullmatch(r"[0-9A-Fa-f]+", s):
            if any(c in "abcdefABCDEF" for c in s):
                return int(s, 16)
            return int(s, 10)
    raise ValueError(f"Unsupported bitvector encoding: {v!r}")


def sprinttype(idx: Any, table: List[str]) -> str:
    try:
        i = int(idx)
    except Exception:
        return f"Unknown({idx})"
    if 0 <= i < len(table):
        v = table[i]
        return "(none)" if v == "\n" else v
    return f"Unknown({i})"


def sprintbit(bits: Any, table: List[str], skip_unused: bool = True) -> str:
    b = parse_bitvector(bits)
    out: List[str] = []
    stop = table.index("\n") if "\n" in table else len(table)
    for i in range(stop):
        if b & (1 << i):
            name = table[i]
            if not name or name == "\n":
                continue
            if skip_unused:
                up = name.strip().upper()
                if name.startswith("^") or up.startswith("UNUSED"):
                    continue
            out.append(name)
    return " ".join(out) if out else "Nothing"


def _coerce_apply_entries(applys: Any) -> List[Dict[str, Any]]:
    if applys is None:
        return []
    if isinstance(applys, list):
        return [a for a in applys if isinstance(a, dict)]
    if isinstance(applys, dict):
        items = []
        for k, v in applys.items():
            if not isinstance(v, dict):
                continue
            try:
                ki = int(k)
            except Exception:
                ki = 10**9
            items.append((ki, v))
        items.sort(key=lambda x: x[0])
        return [v for _, v in items]
    return []


def _int(v: Any, default: int = 0) -> int:
    try:
        return int(v)
    except Exception:
        return default


def identify_type_specific(obj: Dict[str, Any], spell_map: Dict[int, str]) -> List[str]:
    t = _int(obj.get("type_flag", -1), -1)
    v0 = _int(obj.get("v0", 0))
    v1 = _int(obj.get("v1", 0))
    v2 = _int(obj.get("v2", 0))
    v3 = _int(obj.get("v3", 0))
    lines: List[str] = []

    # These are best-effort decodes. Anything we miss will still appear under "Other attributes".
    if t == 5:  # Weapon
        avg = ((v2 + 1) / 2.0) * v1
        lines.append(f"Damage Dice is '{v1}D{v2}', for an average per-round damage of {avg:.1f}.")
    elif t == 9:  # Armor
        lines.append(f"AC-apply is {v0}")
    elif t == 2:  # Scroll
        spells = [v1, v2, v3]
        names = [spell_name(s, spell_map) for s in spells if _int(s) >= 1]
        lines.append("This Scroll casts: " + (", ".join(names) if names else "(none)"))
    elif t == 10:  # Potion
        spells = [v1, v2, v3]
        names = [spell_name(s, spell_map) for s in spells if _int(s) >= 1]
        lines.append("This Potion casts: " + (", ".join(names) if names else "(none)"))
    elif t == 3:  # Wand
        lines.append(f"This wand casts: {spell_name(v3, spell_map)}")
        lines.append(f"It has {v1} maximum charge(s) and {v2} remaining.")
    elif t == 4:  # Staff
        lines.append(f"This Staff casts: {spell_name(v3, spell_map)}")
        lines.append(f"It has {v1} maximum charge(s) and {v2} remaining.")
    elif t == 1:  # Light
        lines.append("Hours left: [Infinite]" if v2 == -1 else f"Hours left: [{v2}]")
    elif t == 15:  # Container
        lines.append(f"Can hold {v0} items with a maximum weight of {v3}.")
        if v1 & 1:  # Closeable
            lines.append("This container can be closed.")
        if v1 & 2:  # Pickproof
            lines.append("This container is pickproof.")
        if v1 & 4:  # Closed
            lines.append("This container is currently closed.")
        if v1 & 8:  # Locked
            lines.append("This container is currently locked.")
        if v2 > 0:  # Key vnum
            lines.append(f"Key required: {v2}")
    elif t == 17:  # Liquid Container
        drink = DRINKS[v2] if 0 <= v2 < len(DRINKS) and DRINKS[v2] != "\n" else f"Unknown({v2})"
        lines.append(f"Can hold {v0} drink units.")
        lines.append(f"Contains {v1} drink units of {drink}.")
    elif t == 7:  # Missile
        avg = ((v2 + 1) / 2.0) * v1
        lines.append(f"Damage Dice is '{v1}D{v2}', for an average damage of {avg:.1f} on impact.")
    elif t == 8:  # Treasure
        lines.append(f"It has {v0} psp(s) stored.")
    elif t == 35:  # Grant Scroll
        spells = [v0, v1, v2, v3]
        names = [spell_name(s, spell_map) for s in spells if _int(s) >= 1]
        lines.append("This scroll grants: " + (" ".join(f"'{n}'" for n in names) if names else "(none)"))
    elif t == 41:  # Event Scroll
        ev = PLAYER_EVENT_NAMES[v0] if 0 <= v0 < len(PLAYER_EVENT_NAMES) and PLAYER_EVENT_NAMES[v0] != "\n" else f"Unknown({v0})"
        lines.append(f"This scroll activates 5 minutes of {ev}")
    elif t == 19:  # Food
        lines.append(f"This food will fill you up by {v0} hours.")
        if v1 > 0:
            lines.append(f"This food is poisoned (poison level: {v1}).")
    elif t == 14:  # Trap
        lines.append(f"Trap type: {v0}, Damage: {v1}, Charges: {v2}")
    elif t == 22:  # Boat
        lines.append("This item allows water travel.")
    elif t == 23:  # Fountain
        drink = DRINKS[v2] if 0 <= v2 < len(DRINKS) and DRINKS[v2] != "\n" else f"Unknown({v2})"
        lines.append(f"This fountain contains {drink}.")
        lines.append(f"Drink units available: {v1}")
    elif t == 24:  # Portal
        lines.append(f"This portal leads to room {v0}.")
        if v1 > 0:
            lines.append(f"Portal key required: {v1}")
        if v2 > 0:
            lines.append(f"Portal has {v2} charges remaining.")
    elif t == 37:  # Mana Spike
        lines.append("Currently owned by somebody." if v0 > 0 else "This mana spike is not owned by anybody.")

    # Also show type_info raw (some types have rich structures)
    type_info = obj.get("type_info")
    if isinstance(type_info, dict) and type_info:
        lines.append("Type-specific data:")
        lines.append(json.dumps(type_info, indent=2, ensure_ascii=False, sort_keys=True))

    return lines


def format_object_identify(obj: Dict[str, Any], spell_map: Optional[Dict[int, str]] = None) -> str:
    if spell_map is None:
        spell_map = {}

    vnum = obj.get("vnum", "?")
    short_desc = obj.get("short_desc") or obj.get("short_descr") or obj.get("name") or "(no short_desc)"
    type_flag = _int(obj.get("type_flag", -1), -1)

    out: List[str] = []
    out.append("You feel informed:")
    out.append(f"Object [{vnum}] '{short_desc}', Item type: {sprinttype(type_flag, PLAYER_ITEM_TYPES)}")
    out.append(f"Can be worn on: {sprintbit(obj.get('wear_flags', 0), PLAYER_WEAR_BITS)}")

    affs_val = parse_bitvector(obj.get("affs", 0))
    if affs_val:
        out.append(f"Item will give you the following abilities: {sprintbit(affs_val, AFFECTED_BITS)}")

    item_flags_val = parse_bitvector(obj.get("item_flags", 0))
    if item_flags_val:
        out.append(f"Item is: {sprintbit(item_flags_val, PLAYER_ITEM_FLAG_BITS)}")

    guild_val = parse_bitvector(obj.get("guild_rests", 0))
    if guild_val:
        out.append(f"Guild restrictions: bitmask={guild_val}")

    out.append(f"Weight: {_int(obj.get('weight', 0))}, Value: {_int(obj.get('cost', 0))}")
    out.extend(identify_type_specific(obj, spell_map))

    min_level = _int(obj.get("min_level", 0), 0)
    if min_level:
        out.append(f"You must be at least level {min_level} to use this.")

    apply_entries = _coerce_apply_entries(obj.get("applys"))
    apply_lines: List[str] = []

    try:
        apply_eat_spell_idx = PLAYER_APPLY_TYPES.index("Eat_Spell")
    except ValueError:
        apply_eat_spell_idx = -1

    for a in apply_entries:
        loc = _int(a.get("type", 0))
        mod = _int(a.get("modifier", 0))
        if loc == 0 or mod == 0:
            continue

        if loc == apply_eat_spell_idx:
            line = f"     Casts: {spell_name(mod, spell_map)} when eaten"
        else:
            line = f"   Affects: {sprinttype(loc, PLAYER_APPLY_TYPES)} By {mod}"

        cond_flags = parse_bitvector(a.get("cond_flags", 0))
        if cond_flags:
            cond_text = sprintbit(cond_flags, APPLY_CONDITIONS, skip_unused=False)
            line += f" - {cond_text}"
            cond_val = a.get("cond_val", 0)
            # bit 1 == Spell, bit 11 == Race (based on APPLY_CONDITIONS table position)
            if cond_flags & (1 << 1):
                line += f"({spell_name(cond_val, spell_map)})"
            elif cond_flags & (1 << 11):
                line += f"(Race#{_int(cond_val, 0)})"

        apply_lines.append(line)

    if apply_lines:
        out.append("Can affect you as :")
        out.extend(apply_lines)

    ws = obj.get("weaponspell")
    if isinstance(ws, list) and ws:
        out.append("Casts Spells:")
        for entry in ws:
            if not isinstance(entry, dict):
                continue
            sid = entry.get("skill_id")
            lvl = _int(entry.get("level", 0))
            pct = _int(entry.get("percent", 0))
            arg = entry.get("arg", "")
            line = f"   Spell: {spell_name(sid, spell_map)}, Level: {lvl}, Percent Prob.: {pct}"
            if isinstance(arg, str):
                arg_s = arg.strip()
                if arg_s and arg_s not in ("0", "0.0"):
                    line += f" ({arg_s})"
            out.append(line)

    known = {
        "vnum","name","short_desc","short_descr","description","type_flag","wear_flags","affs","item_flags","guild_rests",
        "weight","cost","v0","v1","v2","v3","min_level","applys","weaponspell","type_info","action_desc","last_edited","zone"
    }
    extras = {k: v for k, v in obj.items() if k not in known}
    if extras:
        out.append("Other attributes:")
        out.append(json.dumps(extras, indent=2, ensure_ascii=False, sort_keys=True))

    return "\n".join(out) + "\n"
