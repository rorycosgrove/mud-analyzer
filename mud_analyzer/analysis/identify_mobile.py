#!/usr/bin/env python3
"""
identify_mobile.py

Full mobile "identify/stat" style output.

We print a readable stat block + flags + scripts (resolved via World lookup)
and finally dump any remaining JSON fields under "Other attributes:".
"""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional

from ..core.world_lookup import World

MOBF_BITS: List[str] = [
    "SPEC","SENTINEL","SCAVENGER","ISNPC","AWARE","AGGR","STAY-ZONE","WIMPY","AGGR_EVIL","AGGR_GOOD","AGGR_NEUTRAL",
    "MEMORY","HELPER","!CHARM","!SUMMN","!SLEEP","!BASH","!BLIND","UNUSED","UNUSED","!NO_POISON","UNUSED","UNUSED",
    "UNUSED","UNUSED","UNUSED","UNUSED","!FIRE","!COLD","!ELEC","!ENERGY","!BLUNT","!PIERCE","!SLASH","!ENTROPY",
    "!IMPACT","HUNTER","SUMMONED","UNDEAD_NOT_ROT","UNUSED","DONTFIGHT","!PUMMEL","!PETRIFY","RECALL","^UNUSD",
    "!FIGHT_MOBS","MAG_SUMMONS","!STEAL","QUEST","\n"
]

MSK_BITS: List[str] = [
    "DISARM","\n"
]

POSITION_TYPES: List[str] = [
    "Dead","Mortally wounded","Incapacitated","Stunned","Sleeping","Resting","Sitting","Fighting","Standing","\n"
]

AFFECT_BITS: List[str] = [
    "Blind","Invis","Det-Align","Det-Invis","Det-Magic","Sense-Life","Waterwalk","Sanctuary","","Curse","Infravision",
    "Poison","Protection from Evil","Protection from Good","Sleep","!Track","","","Sneak","Hide","","Charm","","Fly",
    "Passdoor","","","","","","","","TrueSight","Penumbra","Spirit","Wraith","Scale","Shift","Bloodlust","Shadow",
    "Illusion","Metamorph","Heat","Flame","Frost","Shock","Energy","Blunt","Pierce","Slash","Entropy","Impact","Haste",
    "Slow","Fear","Petrify","Prismatic Shield","Proficiency","Gills","Tomb Rot","Mind Disrupt","Corruption",
    "Maw of Darkness","Might","Regeneration","Reflect","Entangle","Plague","!Hunger","!Thirst","Find Traps",
    "Tower Of Iron Will","Aggrevate Good","Aggrevate Evil","Ensnare","Light","Darkness","Aqua","Fire","Earth","Air",
    "Transformation","Sonic","Turbulent Winds","Cimmerian Curse","Gaea's Kiss","Arcane Aura","Insight","Dissipation",
    "Weaken","Dispel Evil","Dispel Good","Manipulate","Nimbleness","Battering","Glimmering","Carefulness","Hedging",
    "Rending","Intrepidity","Protecting","Seeking","Absorbing","Chivalry","Heroic Scream","Gallantry","Arthurs Gift",
    "Crusaders Might One","Crusaders Might Two","Crusaders Might Three","Radiation","Kinetic Absorbtion","\n"
]

ATTACK_TYPES: List[str] = [
    "hit","sting","whip","slash","bite","bludgeon","crush","pound","claw","maul","thrash","pierce","blast","punch",
    "stab"
]

RACE_ID_TO_NAME: Dict[int, str] = {
    0: "Human",
    1: "Elven",
    2: "Dwarf",
    3: "Halfling",
    4: "Gnome",
    5: "Halfbreed",
    6: "Reptilian",
    7: "Special",
    8: "Lycanth",
    9: "Draconian",
    10: "Undead",
    11: "Orc",
    12: "Insect",
    13: "Arachnid",
    14: "Dinosaur",
    15: "Fish",
    16: "Bird",
    17: "Giant",
    18: "Predator",
    19: "Parasite",
    20: "Slime",
    21: "Demon",
    22: "Snake",
    23: "Herbiv",
    24: "Tree",
    25: "Veggie",
    26: "Faerie",
    27: "Planar",
    28: "Devil",
    29: "Ghost",
    30: "Goblin",
    31: "Troll",
    32: "Vegman",
    33: "Mindflayer",
    34: "Primate",
    35: "Enchanted",
    36: "Golem",
    37: "Dragon",
    38: "Elemental",
    39: "Ogre",
    40: "Humaned",
}

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
    raise ValueError(f"Unsupported bitvector encoding: {v!r}")

def _named_len(table: List[str]) -> int:
    return table.index("\n") if "\n" in table else len(table)

def sprinttype(idx: Any, table: List[str]) -> str:
    # Accept either numeric index or a string already in the table.
    if isinstance(idx, str):
        s = idx.strip()
        if not s:
            return "Unknown()"
        named = [t for t in table if t != "\n"]
        for t in named:
            if t.lower() == s.lower():
                return t
        return f"Unknown({idx})"
    try:
        i = int(idx)
    except Exception:
        return f"Unknown({idx})"
    if 0 <= i < len(table):
        v = table[i]
        return "(none)" if v == "\n" else v
    return f"Unknown({i})"

def sprintbit(bits: Any, table: List[str], *, skip_unused: bool = True, max_bits: int = 128) -> str:
    b = parse_bitvector(bits)
    out: List[str] = []
    n = _named_len(table)

    for i in range(n):
        if b & (1 << i):
            name = table[i]
            if not name or name == "\n":
                continue
            if skip_unused:
                up = name.strip().upper()
                if name.startswith("^") or up.startswith("UNUSED"):
                    continue
            out.append(name)

    for i in range(n, max_bits):
        if b & (1 << i):
            out.append(f"BIT#{i}")

    return " ".join(out) if out else "Nothing"

def safe_int(v: Any, default: int = 0) -> int:
    try:
        return int(v)
    except Exception:
        return default

def sex_name(sex: Any) -> str:
    s = safe_int(sex, -1)
    return {0: "Neuter", 1: "Male", 2: "Female"}.get(s, f"Unknown({s})")

def race_name(race_id: Any) -> str:
    r = safe_int(race_id, -1)
    return RACE_ID_TO_NAME.get(r, f"Race#{r}")

def attack_type_name(attack_type: Any) -> str:
    a = safe_int(attack_type, -1)
    if 0 <= a < len(ATTACK_TYPES):
        return ATTACK_TYPES[a]
    return f"Unknown({a})"

def format_mobile_identify(
    mob: Dict[str, Any],
    world: Optional[World] = None,
    *,
    include_script_code: bool = False,
    script_max_lines: int = 25
) -> str:
    vnum = mob.get("vnum", "?")
    short = mob.get("short_descr") or mob.get("short_desc") or mob.get("name") or "(no short)"
    name = mob.get("name") or "(no keywords)"
    longd = mob.get("long_descr") or mob.get("long_desc") or ""
    desc = mob.get("description") or ""

    level = mob.get("level", 0)
    align = mob.get("alignment", 0)
    race = mob.get("race", 0)
    sex = mob.get("sex", 0)

    str_ = mob.get("str", 0)
    str_add = mob.get("str_add", 0)
    dex = mob.get("dex", 0)
    con = mob.get("con", 0)
    intel = mob.get("int", 0)
    wis = mob.get("wis", 0)
    cha = mob.get("cha", 0)

    hit = mob.get("hit", 0)
    max_hit = mob.get("max_hit", 0)
    mana = mob.get("mana", 0)
    move = mob.get("move", 0)

    armor = mob.get("armor", 0)
    hitroll = mob.get("hitroll", 0)
    damroll = mob.get("damroll", 0)

    dam_n = mob.get("damnodice", 0)
    dam_s = mob.get("damsizedice", 0)
    attacks = mob.get("attacks", 0)

    attack_type = mob.get("attack_type", 0)
    elem_attack = mob.get("elem_attack", 0)

    gold = mob.get("gold", 0)
    exp = mob.get("exp", 0)

    pos = mob.get("position", 0)
    def_pos = mob.get("default_pos", 0)

    mob_flags = mob.get("mob_flags", 0)
    affs = mob.get("affs", 0)
    msk = mob.get("msk", 0)

    out: List[str] = []
    out.append("You feel informed:")
    out.append(f"Mobile [{vnum}] '{short}'")
    out.append(f"Keywords: {name}")
    if isinstance(longd, str) and longd.strip():
        out.append(f"Long: {longd.rstrip()}")
    if isinstance(desc, str) and desc.strip():
        out.append("Description:")
        out.extend([f"  {line}" for line in desc.rstrip().splitlines()])

    out.append(f"Level {level}  Alignment {align}")
    out.append(f"Race: {race_name(race)} ({safe_int(race, 0)})  Sex: {sex_name(sex)} ({safe_int(sex, 0)})")
    out.append(f"Pos: {sprinttype(pos, POSITION_TYPES)}  Default: {sprinttype(def_pos, POSITION_TYPES)}")

    out.append(f"Stats: STR {str_}/{str_add}  DEX {dex}  CON {con}  INT {intel}  WIS {wis}  CHA {cha}")
    out.append(f"HP {hit}/{max_hit}  Mana {mana}  Move {move}")
    out.append(f"AC {armor}  Hitroll {hitroll}  Damroll {damroll}")

    if safe_int(dam_n, 0) and safe_int(dam_s, 0):
        avg = ((safe_int(dam_s, 0) + 1) / 2.0) * safe_int(dam_n, 0)
        out.append(f"Damage Dice {dam_n}D{dam_s} (avg {avg:.1f} before damroll)")
    if safe_int(attacks, 0):
        out.append(f"Attacks: {attacks}")
    out.append(f"Attack type: {attack_type_name(attack_type)} (#{safe_int(attack_type, 0)})  Elem attack: {elem_attack}")

    out.append(f"Gold {gold}  Exp {exp}")
    out.append(f"Mob flags: {sprintbit(mob_flags, MOBF_BITS)}")

    if parse_bitvector(msk):
        out.append(f"MSK: {sprintbit(msk, MSK_BITS, skip_unused=False)}")
    if parse_bitvector(affs):
        out.append(f"Affects: {sprintbit(affs, AFFECT_BITS, skip_unused=False)}")

    scripts = mob.get("scripts")
    if isinstance(scripts, list) and scripts:
        out.append("Scripts:")
        for sid_raw in scripts:
            sid = safe_int(sid_raw, -1)
            if sid < 0:
                out.append(f"  - {sid_raw}")
                continue

            s = world.load("script", sid) if world else None
            if s and isinstance(s, dict):
                sname = s.get("name") or "(no name)"
                stype = s.get("type")
                trig = s.get("trigger_type")
                level = s.get("level")
                out.append(f"  - {sid} '{sname}' type={stype} trigger={trig} level={level}")

                code = s.get("code", "")
                if isinstance(code, str) and code.strip():
                    code_lines = code.splitlines()
                    if include_script_code:
                        out.append("    Code:")
                        out.extend([f"      {cl}" for cl in code_lines])
                    else:
                        preview = code_lines[:script_max_lines]
                        out.append(f"    Code (first {min(script_max_lines, len(code_lines))}/{len(code_lines)} lines):")
                        out.extend([f"      {cl}" for cl in preview])
                        if len(code_lines) > script_max_lines:
                            out.append("      ... (truncated; use --show-script-code in zone_summary)")
            else:
                out.append(f"  - {sid} (script missing)")

    # Format repops section
    repops = mob.get("repops")
    if isinstance(repops, list) and repops:
        out.append("Equipment:")
        for repop in repops:
            if isinstance(repop, dict):
                vnum = safe_int(repop.get("vnum", 0))
                percent = safe_int(repop.get("percent", 100))
                position = safe_int(repop.get("position", 0))
                
                if vnum > 0:
                    item_name = world.obj_brief(vnum) if world else f"Item {vnum}"
                    pos_names = {1: "finger", 7: "wield", 8: "hold", 9: "light", 10: "body", 11: "head", 12: "legs", 13: "feet", 14: "shield", 15: "arms", 16: "hands", 17: "about", 18: "waist", 19: "wrist", 20: "wrist", 21: "neck", 22: "neck"}
                    pos_name = pos_names.get(position, f"position {position}")
                    out.append(f"  - {item_name} ({percent}% chance, {pos_name})")

    known = {
        "vnum","name","short_descr","short_desc","long_descr","long_desc","description",
        "level","alignment","race","sex",
        "str","str_add","dex","con","int","wis","cha",
        "hit","max_hit","mana","move",
        "armor","hitroll","damroll","damnodice","damsizedice","attacks",
        "attack_type","elem_attack",
        "gold","exp","position","default_pos",
        "mob_flags","affs","msk","scripts","repops","actions","resists","intel","last_edited","zone"
    }
    extras = {k: v for k, v in mob.items() if k not in known}
    if extras:
        out.append("Other attributes:")
        out.append(json.dumps(extras, indent=2, ensure_ascii=False, sort_keys=True))

    return "\n".join(out) + "\n"
