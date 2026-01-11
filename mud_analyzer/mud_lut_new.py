#!/usr/bin/env python3
"""mud_lut.py

Persistent LUT (lookup table) for AddictMUD / CircleMUD JSON world data.

This builds a SQLite DB you keep around. Subsequent runs are incremental.

Indexed entity types
- zone, room, object, mobile, script, assemble, shop

Captured data
- entity: one row per entity JSON file
- edge: cross-reference edges (exits, scripts attached, loads/equips/contains, assemble parts, shop rooms/keeper)
- zone_cmd: ALL zone reset commands verbatim (args + raw JSON)
- ref: optional "deep" vnum references discovered by conservative key-based traversal (useful for scripts)
- parse_error: non-fatal parse/indexing errors

Per-zone progress
- Prints one status line per zone processed (recommended).

Typical usage
  python mud_lut.py --root addict-world-master build --full
  python mud_lut.py --root addict-world-master build              # incremental
  python mud_lut.py --root addict-world-master build --zones 180

  python mud_lut.py --root addict-world-master stats
  python mud_lut.py --root addict-world-master query 18021
  python mud_lut.py --root addict-world-master where-used object 13462
  python mud_lut.py --root addict-world-master verify

DB default (relative to --root): .mud_cache/lut.sqlite
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sqlite3
import sys
import time
import traceback
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Sequence, Set, Tuple


ZONE_DIR_RE = re.compile(r"^\d+$")
ENTITY_DIRS = ("room", "object", "mobile", "script", "assemble", "shop")


def safe_int(x: Any) -> Optional[int]:
    try:
        if x is None:
            return None
        if isinstance(x, bool):
            return int(x)
        if isinstance(x, int):
            return int(x)
        if isinstance(x, str) and x.strip():
            return int(x.strip())
    except Exception:
        return None
    return None


def json_dumps(x: Any) -> str:
    return json.dumps(x, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def sha1_bytes(b: bytes) -> str:
    h = hashlib.sha1()
    h.update(b)
    return h.hexdigest()


def detect_world_root(p: Path) -> Path:
    """Return a directory that directly contains numeric zone dirs."""
    p = p.resolve()
    try:
        if any((p / d).is_dir() and ZONE_DIR_RE.match(d) for d in os.listdir(p)):
            return p
    except Exception:
        pass

    # One level deeper: common when you point at a repo root.
    for c in [c for c in p.iterdir() if c.is_dir()]:
        try:
            if any((c / d).is_dir() and ZONE_DIR_RE.match(d) for d in os.listdir(c)):
                return c.resolve()
        except Exception:
            pass

    return p


def parse_zones_spec(spec: Optional[str]) -> Optional[Set[int]]:
    """Parse: "134" | "134,712" | "1-500" | "1-500,900,1000-1100"""
    if spec is None or not str(spec).strip():
        return None

    out: Set[int] = set()
    parts = [p.strip() for p in str(spec).split(",") if p.strip()]
    for p in parts:
        if "-" in p:
            a, b = p.split("-", 1)
            a_i, b_i = safe_int(a), safe_int(b)
            if a_i is None or b_i is None:
                raise ValueError(f"Bad zone range: {p!r}")
            lo, hi = (a_i, b_i) if a_i <= b_i else (b_i, a_i)
            out.update(range(lo, hi + 1))
        else:
            v = safe_int(p)
            if v is None:
                raise ValueError(f"Bad zone number: {p!r}")
            out.add(v)
    return out


def iter_zone_dirs(world_root: Path, zones: Optional[Set[int]] = None) -> List[Path]:
    zone_dirs = [d for d in world_root.iterdir() if d.is_dir() and ZONE_DIR_RE.match(d.name)]
    zone_dirs.sort(key=lambda p: int(p.name))
    if zones is not None:
        zone_dirs = [d for d in zone_dirs if int(d.name) in zones]
    return zone_dirs


def iter_zone_files(zone_dir: Path) -> Iterator[Tuple[str, Path]]:
    """Yield (kind, path) for the zone's files."""
    zone_file = zone_dir / f"{zone_dir.name}.json"
    if zone_file.exists():
        yield ("zone", zone_file)

    for sub in ENTITY_DIRS:
        subdir = zone_dir / sub
        if not subdir.is_dir():
            continue
        for p in sorted(subdir.glob("*.json"), key=lambda x: x.name):
            yield (sub, p)


def load_json_file(p: Path, use_sha1: bool) -> Tuple[Dict[str, Any], str, bytes]:
    raw = p.read_bytes()
    h = sha1_bytes(raw) if use_sha1 else "-"
    try:
        data = json.loads(raw.decode("utf-8"))
    except UnicodeDecodeError:
        data = json.loads(raw.decode("latin-1"))
    return data, h, raw

# ----------------------------
# DB schema + helpers
# ----------------------------

SCHEMA_SQL = r"""
PRAGMA journal_mode=WAL;
PRAGMA synchronous=NORMAL;
PRAGMA temp_store=MEMORY;

CREATE TABLE IF NOT EXISTS file_state (
  path TEXT PRIMARY KEY,
  mtime REAL NOT NULL,
  size INTEGER NOT NULL,
  sha1 TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS entity (
  etype TEXT NOT NULL,
  vnum INTEGER NOT NULL,
  zone INTEGER,
  path TEXT NOT NULL,
  name TEXT,
  keywords TEXT,
  short_descr TEXT,
  last_edited TEXT,
  extra_json TEXT NOT NULL,
  raw_json TEXT,
  PRIMARY KEY (etype, vnum)
);

CREATE INDEX IF NOT EXISTS idx_entity_vnum ON entity(vnum);
CREATE INDEX IF NOT EXISTS idx_entity_zone ON entity(zone);
CREATE INDEX IF NOT EXISTS idx_entity_etype_zone ON entity(etype, zone);

-- Cross-reference edges. source_path lets incremental builds delete edges from a changed file.
CREATE TABLE IF NOT EXISTS edge (
  source_path TEXT NOT NULL,
  src_etype TEXT NOT NULL,
  src_vnum INTEGER NOT NULL,
  dst_etype TEXT NOT NULL,
  dst_vnum INTEGER NOT NULL,
  rel TEXT NOT NULL,
  zone INTEGER,
  context_json TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_edge_src ON edge(src_etype, src_vnum);
CREATE INDEX IF NOT EXISTS idx_edge_dst ON edge(dst_etype, dst_vnum);
CREATE INDEX IF NOT EXISTS idx_edge_rel ON edge(rel);
CREATE INDEX IF NOT EXISTS idx_edge_source ON edge(source_path);

-- All zone commands verbatim.
CREATE TABLE IF NOT EXISTS zone_cmd (
  source_path TEXT NOT NULL,
  zone INTEGER NOT NULL,
  idx INTEGER NOT NULL,
  cmd TEXT NOT NULL,
  prob INTEGER,
  if_flag INTEGER,
  arg1 INTEGER,
  arg2 INTEGER,
  arg3 INTEGER,
  raw_json TEXT NOT NULL,
  PRIMARY KEY(zone, idx)
);

CREATE INDEX IF NOT EXISTS idx_zone_cmd_cmd ON zone_cmd(cmd);

-- Conservative deep references (mostly for scripts).
CREATE TABLE IF NOT EXISTS ref (
  source_path TEXT NOT NULL,
  src_etype TEXT NOT NULL,
  src_vnum INTEGER NOT NULL,
  keypath TEXT NOT NULL,
  guess_etype TEXT NOT NULL,
  dst_vnum INTEGER NOT NULL,
  context_json TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_ref_src ON ref(src_etype, src_vnum);
CREATE INDEX IF NOT EXISTS idx_ref_dst ON ref(guess_etype, dst_vnum);
CREATE INDEX IF NOT EXISTS idx_ref_source ON ref(source_path);

-- Non-fatal errors.
CREATE TABLE IF NOT EXISTS parse_error (
  source_path TEXT NOT NULL,
  zone INTEGER,
  etype TEXT,
  message TEXT NOT NULL,
  traceback TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_parse_error_source ON parse_error(source_path);
"""


def _ensure_column(conn: sqlite3.Connection, table: str, col: str, decl: str) -> None:
    cols = {r[1] for r in conn.execute(f"PRAGMA table_info({table})").fetchall()}
    if col not in cols:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {col} {decl}")


def open_db(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.executescript(SCHEMA_SQL)
    # Migrations for older DBs:
    _ensure_column(conn, "entity", "raw_json", "TEXT")
    return conn


def needs_update(conn: sqlite3.Connection, relpath: str, mtime: float, size: int, sha1: str) -> bool:
    row = conn.execute("SELECT mtime,size,sha1 FROM file_state WHERE path=?", (relpath,)).fetchone()
    if row is None:
        return True
    return not (float(row[0]) == float(mtime) and int(row[1]) == int(size) and row[2] == sha1)


def upsert_file_state(conn: sqlite3.Connection, relpath: str, mtime: float, size: int, sha1: str) -> None:
    conn.execute(
        "INSERT INTO file_state(path,mtime,size,sha1) VALUES(?,?,?,?) "
        "ON CONFLICT(path) DO UPDATE SET mtime=excluded.mtime,size=excluded.size,sha1=excluded.sha1",
        (relpath, mtime, size, sha1),
    )


def delete_by_source(conn: sqlite3.Connection, relpath: str) -> None:
    conn.execute("DELETE FROM edge WHERE source_path=?", (relpath,))
    conn.execute("DELETE FROM zone_cmd WHERE source_path=?", (relpath,))
    conn.execute("DELETE FROM ref WHERE source_path=?", (relpath,))
    conn.execute("DELETE FROM parse_error WHERE source_path=?", (relpath,))


def delete_missing_files(conn: sqlite3.Connection, existing_relpaths: Set[str]) -> int:
    rows = conn.execute("SELECT path FROM file_state").fetchall()
    missing = [r[0] for r in rows if r[0] not in existing_relpaths]
    if not missing:
        return 0
    for rp in missing:
        conn.execute("DELETE FROM entity WHERE path=?", (rp,))
        conn.execute("DELETE FROM edge WHERE source_path=?", (rp,))
        conn.execute("DELETE FROM zone_cmd WHERE source_path=?", (rp,))
        conn.execute("DELETE FROM ref WHERE source_path=?", (rp,))
        conn.execute("DELETE FROM parse_error WHERE source_path=?", (rp,))
        conn.execute("DELETE FROM file_state WHERE path=?", (rp,))
    return len(missing)

# ----------------------------
# Parsing
# ----------------------------

@dataclass
class ParsedEntity:
    etype: str
    vnum: int
    zone: Optional[int]
    relpath: str
    name: Optional[str]
    keywords: Optional[str]
    short_descr: Optional[str]
    last_edited: Optional[str]
    extra: Dict[str, Any]


def parse_entity(kind: str, relpath: str, data: Dict[str, Any], zone_hint: Optional[int]) -> Optional[ParsedEntity]:
    # Be defensive: vnum is present in this dataset but don't assume.
    vnum = safe_int(data.get("vnum")) or safe_int(data.get("id")) or safe_int(Path(relpath).stem)
    if vnum is None:
        return None

    zone = safe_int(data.get("zone")) or zone_hint

    last_edited: Optional[str] = None
    for k in ("last_edited", "lastEdited", "last_edited_ts", "lastEditedTs"):
        if k in data and data.get(k) is not None:
            last_edited = str(data.get(k))
            break

    name: Optional[str] = None
    keywords: Optional[str] = None
    short_descr: Optional[str] = None

    if kind == "room":
        name = data.get("name")
    elif kind == "mobile":
        keywords = data.get("name")
        short_descr = data.get("short_descr") or data.get("short_desc") or data.get("shortDesc")
        if short_descr is None:
            short_descr = data.get("long_descr") or data.get("longDesc")
        name = short_descr or keywords
    elif kind == "object":
        keywords = data.get("name")
        short_descr = data.get("short_desc") or data.get("short_descr") or data.get("shortDesc")
        name = short_descr or keywords
    elif kind == "script":
        name = data.get("name") or data.get("title")
    elif kind == "assemble":
        kws = data.get("keywords")
        if isinstance(kws, list):
            keywords = " ".join(str(x) for x in kws if str(x).strip())
        elif isinstance(kws, str):
            keywords = kws
        name = keywords or data.get("name")
    elif kind == "shop":
        name = f"Shop {vnum}"
    elif kind == "zone":
        name = data.get("name")

    # Keep a compact subset of useful fields; full raw JSON is stored separately.
    extra: Dict[str, Any] = {}
    for k in (
        # objects
        "type_flag", "wear_flags", "item_flags", "extra_flags", "affs", "applys",
        "min_level", "guild_rests", "v0", "v1", "v2", "v3", "weight", "cost",
        # mobiles
        "level", "alignment", "race", "sex", "mob_flags", "repops", "inventory", "equipment",
        # rooms
        "room_flags", "sector", "exits",
        # scripts
        "trigger_type", "type", "level", "triggers",
        # assemble
        "cmd", "keywords", "parts",
        # shops
        "keeper", "rooms",
        # zones
        "top", "lifespan", "reset_mode", "flags", "plane", "corpse_room",
    ):
        if k in data:
            extra[k] = data[k]

    return ParsedEntity(
        etype=kind,
        vnum=int(vnum),
        zone=zone,
        relpath=relpath,
        name=str(name) if name is not None else None,
        keywords=str(keywords) if keywords is not None else None,
        short_descr=str(short_descr) if short_descr is not None else None,
        last_edited=last_edited,
        extra=extra,
    )


def iter_script_refs(x: Any) -> List[int]:
    out: List[int] = []
    if x is None:
        return out
    if isinstance(x, list):
        for v in x:
            iv = safe_int(v)
            if iv is not None:
                out.append(iv)
    elif isinstance(x, dict):
        for k in x.keys():
            iv = safe_int(k)
            if iv is not None:
                out.append(iv)
    else:
        iv = safe_int(x)
        if iv is not None:
            out.append(iv)
    return out


EntityRow = Tuple[str, int, Optional[int], str, Optional[str], Optional[str], Optional[str], Optional[str], str, Optional[str]]
EdgeRow = Tuple[str, str, int, str, int, str, Optional[int], str]
ZoneCmdRow = Tuple[str, int, int, str, Optional[int], Optional[int], Optional[int], Optional[int], Optional[int], str]
RefRow = Tuple[str, str, int, str, str, int, str]
ErrRow = Tuple[str, Optional[int], Optional[str], str, str]

# ----------------------------
# Deep refs (conservative)
# ----------------------------

_KEY_TO_ETYPE = (
    ("to_room", "room"),
    ("room", "room"),
    ("mob", "mobile"),
    ("mobile", "mobile"),
    ("npc", "mobile"),
    ("obj", "object"),
    ("object", "object"),
    ("item", "object"),
    ("script", "script"),
    ("trigger", "script"),
    ("trig", "script"),
    ("zone", "zone"),
)


def guess_etype_from_key(key: str) -> str:
    k = key.lower()
    for needle, et in _KEY_TO_ETYPE:
        if needle in k:
            return et
    if k.endswith("vnum") or k == "vnum":
        return "any"
    return "any"


def walk_keyed_ints(obj: Any, prefix: str = "") -> Iterator[Tuple[str, str, int]]:
    """Yield (keypath, key, int_value) for int-like values under dict keys.

    This does NOT try to interpret Diku/Circle value slots (v0-v3, etc.). It is intended
    mainly for script-like structures where keys encode semantics.
    """
    if isinstance(obj, dict):
        for k, v in obj.items():
            kp = f"{prefix}.{k}" if prefix else str(k)
            if isinstance(v, (int, bool)):
                iv = safe_int(v)
                if iv is not None:
                    yield (kp, str(k), iv)
            elif isinstance(v, str):
                iv = safe_int(v)
                if iv is not None:
                    yield (kp, str(k), iv)
            elif isinstance(v, list):
                # If the key suggests list of vnums, capture elements too.
                for i, el in enumerate(v):
                    if isinstance(el, (int, bool)):
                        iv = safe_int(el)
                        if iv is not None:
                            yield (f"{kp}[{i}]", str(k), iv)
                    elif isinstance(el, str):
                        iv = safe_int(el)
                        if iv is not None:
                            yield (f"{kp}[{i}]", str(k), iv)
                    elif isinstance(el, (dict, list)):
                        yield from walk_keyed_ints(el, prefix=f"{kp}[{i}]")
            elif isinstance(v, dict):
                yield from walk_keyed_ints(v, prefix=kp)
    elif isinstance(obj, list):
        for i, el in enumerate(obj):
            yield from walk_keyed_ints(el, prefix=f"{prefix}[{i}]" if prefix else f"[{i}]")


# ----------------------------
# Edges (structured relationships)
# ----------------------------

def edges_from_room(source_path: str, room_vnum: int, zone: Optional[int], data: Dict[str, Any]) -> List[EdgeRow]:
    edges: List[EdgeRow] = []

    exits = data.get("exits")

    # Common form: dict of directions -> {to_room: vnum, ...}
    if isinstance(exits, dict):
        for direction, ex in exits.items():
            if not isinstance(ex, dict):
                continue
            to_room = safe_int(ex.get("to_room") or ex.get("toRoom") or ex.get("to"))
            if to_room is None:
                continue
            ctx = dict(ex)
            ctx["dir"] = direction
            edges.append((source_path, "room", room_vnum, "room", to_room, f"exit:{direction}", zone, json_dumps(ctx)))

    # Some zones might use list form.
    elif isinstance(exits, list):
        for ex in exits:
            if not isinstance(ex, dict):
                continue
            to_room = safe_int(ex.get("to_room") or ex.get("toRoom") or ex.get("to"))
            if to_room is None:
                continue
            direction = ex.get("dir") or ex.get("direction")
            rel = f"exit:{direction}" if direction is not None else "exit"
            edges.append((source_path, "room", room_vnum, "room", to_room, rel, zone, json_dumps(ex)))

    for s in iter_script_refs(data.get("scripts")):
        edges.append((source_path, "room", room_vnum, "script", s, "has_script", zone, json_dumps({"owner": "room"})))

    return edges


def edges_from_object(source_path: str, obj_vnum: int, zone: Optional[int], data: Dict[str, Any]) -> List[EdgeRow]:
    edges: List[EdgeRow] = []

    for s in iter_script_refs(data.get("scripts")):
        edges.append((source_path, "object", obj_vnum, "script", s, "has_script", zone, json_dumps({"owner": "object"})))

    # Best-effort container contents from JSON (not resets).
    for k in ("contains", "contents", "inventory", "items"):
        v = data.get(k)
        if isinstance(v, list):
            for el in v:
                iv = safe_int(el)
                if iv is not None:
                    edges.append((source_path, "object", obj_vnum, "object", iv, f"contains:{k}", zone, json_dumps({"key": k})))

    return edges


def edges_from_mobile(source_path: str, mob_vnum: int, zone: Optional[int], data: Dict[str, Any]) -> List[EdgeRow]:
    edges: List[EdgeRow] = []

    for s in iter_script_refs(data.get("scripts")):
        edges.append((source_path, "mobile", mob_vnum, "script", s, "has_script", zone, json_dumps({"owner": "mobile"})))

    repops = data.get("repops")
    if isinstance(repops, list):
        for r in repops:
            if not isinstance(r, dict):
                continue
            cmd = r.get("command") or r.get("cmd")
            obj = safe_int(r.get("vnum") or r.get("arg1") or r.get("obj"))
            if obj is None or cmd is None:
                continue
            edges.append((source_path, "mobile", mob_vnum, "object", obj, f"mob_repop:{cmd}", zone, json_dumps(r)))

    # Some exports include explicit inventory/equipment lists.
    inv = data.get("inventory")
    if isinstance(inv, list):
        for el in inv:
            iv = safe_int(el)
            if iv is not None:
                edges.append((source_path, "mobile", mob_vnum, "object", iv, "has_inventory", zone, json_dumps({})))

    eq = data.get("equipment")
    if isinstance(eq, list):
        for el in eq:
            if isinstance(el, dict):
                iv = safe_int(el.get("vnum") or el.get("obj") or el.get("id"))
                if iv is not None:
                    edges.append((source_path, "mobile", mob_vnum, "object", iv, "has_equipment", zone, json_dumps(el)))
            else:
                iv = safe_int(el)
                if iv is not None:
                    edges.append((source_path, "mobile", mob_vnum, "object", iv, "has_equipment", zone, json_dumps({})))

    return edges


def edges_from_assemble(source_path: str, assemble_vnum: int, zone: Optional[int], data: Dict[str, Any]) -> List[EdgeRow]:
    edges: List[EdgeRow] = []

    ctx = {"cmd": data.get("cmd"), "keywords": data.get("keywords")}

    # By convention in this dataset, the assemble's vnum is the produced object vnum.
    edges.append((source_path, "assemble", assemble_vnum, "object", assemble_vnum, "produces", zone, json_dumps(ctx)))

    parts = data.get("parts")
    if isinstance(parts, list):
        for p in parts:
            pv = safe_int(p)
            if pv is not None:
                edges.append((source_path, "assemble", assemble_vnum, "object", pv, "requires_part", zone, json_dumps(ctx)))

    # Some assembles may specify "result" or "product".
    for k in ("result", "product", "produces"):
        rv = safe_int(data.get(k))
        if rv is not None and rv != assemble_vnum:
            edges.append((source_path, "assemble", assemble_vnum, "object", rv, f"produces:{k}", zone, json_dumps(ctx)))

    return edges


def edges_from_shop(source_path: str, shop_vnum: int, zone: Optional[int], data: Dict[str, Any]) -> List[EdgeRow]:
    edges: List[EdgeRow] = []
    keeper = safe_int(data.get("keeper"))
    if keeper is not None:
        edges.append((source_path, "shop", shop_vnum, "mobile", keeper, "shop_keeper", zone, json_dumps({})))

    rooms = data.get("rooms")
    if isinstance(rooms, list):
        for r in rooms:
            rv = safe_int(r)
            if rv is not None:
                edges.append((source_path, "shop", shop_vnum, "room", rv, "shop_room", zone, json_dumps({})))

    return edges

# ----------------------------
# Zone commands
# ----------------------------

def edges_from_zone_cmds(source_path: str, zone: int, cmds: List[Dict[str, Any]]) -> Tuple[List[EdgeRow], List[ZoneCmdRow]]:
    edges: List[EdgeRow] = []
    zrows: List[ZoneCmdRow] = []

    current_mob: Optional[int] = None

    for idx, c in enumerate(cmds):
        if not isinstance(c, dict):
            continue
        cmd = c.get("cmd")
        if not isinstance(cmd, str) or not cmd:
            continue

        prob = safe_int(c.get("prob"))
        if_flag = safe_int(c.get("flag"))
        a1 = safe_int(c.get("arg1"))
        a2 = safe_int(c.get("arg2"))
        a3 = safe_int(c.get("arg3"))

        zrows.append((source_path, zone, idx, cmd, prob, if_flag, a1, a2, a3, json_dumps(c)))

        # Best-effort: build a graph from classic Circle resets.
        if cmd == "M" and a1 is not None and a3 is not None:
            current_mob = a1
            edges.append((source_path, "zone", zone, "mobile", a1, "zone_cmd:M_load_mob", zone, json_dumps(c)))
            edges.append((source_path, "mobile", a1, "room", a3, "spawns_in", zone, json_dumps(c)))

        elif cmd == "O" and a1 is not None and a3 is not None:
            edges.append((source_path, "zone", zone, "object", a1, "zone_cmd:O_load_obj", zone, json_dumps(c)))
            edges.append((source_path, "object", a1, "room", a3, "loads_in", zone, json_dumps(c)))

        elif cmd in ("G", "E") and a1 is not None:
            if current_mob is not None:
                rel = "zone_cmd:G_give_obj" if cmd == "G" else "zone_cmd:E_equip_obj"
                edges.append((source_path, "mobile", current_mob, "object", a1, rel, zone, json_dumps(c)))
                edges.append((source_path, "zone", zone, "object", a1, rel, zone, json_dumps(c)))

        elif cmd in ("P", "Q") and a1 is not None and a3 is not None:
            # Put a1 into container a3 (Q is used similarly in some codebases).
            edges.append((source_path, "object", a3, "object", a1, f"contains_on_reset:{cmd}", zone, json_dumps(c)))
            edges.append((source_path, "zone", zone, "object", a1, f"zone_cmd:{cmd}_put_obj", zone, json_dumps(c)))

        elif cmd == "D" and a1 is not None:
            edges.append((source_path, "zone", zone, "room", a1, "zone_cmd:D_door", zone, json_dumps(c)))

        elif cmd == "R" and a1 is not None:
            edges.append((source_path, "zone", zone, "room", a1, "zone_cmd:R_remove", zone, json_dumps(c)))

        # Unknown commands remain in zone_cmd verbatim.

    return edges, zrows


# ----------------------------
# Flush / insert
# ----------------------------

def flush(
    conn: sqlite3.Connection,
    entity_rows: List[EntityRow],
    edge_rows: List[EdgeRow],
    zone_cmd_rows: List[ZoneCmdRow],
    ref_rows: List[RefRow],
    err_rows: List[ErrRow],
) -> None:
    if entity_rows:
        conn.executemany(
            "INSERT INTO entity(etype,vnum,zone,path,name,keywords,short_descr,last_edited,extra_json,raw_json) "
            "VALUES(?,?,?,?,?,?,?,?,?,?) "
            "ON CONFLICT(etype,vnum) DO UPDATE SET "
            "zone=excluded.zone,path=excluded.path,name=excluded.name,keywords=excluded.keywords,"
            "short_descr=excluded.short_descr,last_edited=excluded.last_edited,extra_json=excluded.extra_json,raw_json=excluded.raw_json",
            entity_rows,
        )

    if edge_rows:
        conn.executemany(
            "INSERT INTO edge(source_path,src_etype,src_vnum,dst_etype,dst_vnum,rel,zone,context_json) "
            "VALUES(?,?,?,?,?,?,?,?)",
            edge_rows,
        )

    if zone_cmd_rows:
        conn.executemany(
            "INSERT INTO zone_cmd(source_path,zone,idx,cmd,prob,if_flag,arg1,arg2,arg3,raw_json) "
            "VALUES(?,?,?,?,?,?,?,?,?,?) "
            "ON CONFLICT(zone,idx) DO UPDATE SET "
            "source_path=excluded.source_path,cmd=excluded.cmd,prob=excluded.prob,if_flag=excluded.if_flag,"
            "arg1=excluded.arg1,arg2=excluded.arg2,arg3=excluded.arg3,raw_json=excluded.raw_json",
            zone_cmd_rows,
        )

    if ref_rows:
        conn.executemany(
            "INSERT INTO ref(source_path,src_etype,src_vnum,keypath,guess_etype,dst_vnum,context_json) "
            "VALUES(?,?,?,?,?,?,?)",
            ref_rows,
        )

    if err_rows:
        conn.executemany(
            "INSERT INTO parse_error(source_path,zone,etype,message,traceback) VALUES(?,?,?,?,?)",
            err_rows,
        )


# ----------------------------
# Build
# ----------------------------

def fmt_dur(seconds: float) -> str:
    seconds = max(0.0, float(seconds))
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    if h:
        return f"{h:d}:{m:02d}:{s:02d}"
    return f"{m:d}:{s:02d}"


def build(
    world_root: Path,
    db_path: Path,
    zones: Optional[Set[int]],
    full: bool,
    use_sha1: bool,
    store_raw_json: bool,
    deep_refs_mode: str,
    log_path: Optional[Path],
    quiet: bool,
) -> None:
    world_root = detect_world_root(world_root)
    conn = open_db(db_path)
    conn.row_factory = sqlite3.Row

    if full:
        conn.execute("DELETE FROM entity")
        conn.execute("DELETE FROM edge")
        conn.execute("DELETE FROM zone_cmd")
        conn.execute("DELETE FROM ref")
        conn.execute("DELETE FROM parse_error")
        conn.execute("DELETE FROM file_state")
        conn.commit()

    zone_dirs = iter_zone_dirs(world_root, zones=zones)
    total_zones = len(zone_dirs)

    existing_relpaths: Set[str] = set()

    # Buffers
    entity_rows: List[EntityRow] = []
    edge_rows: List[EdgeRow] = []
    zone_cmd_rows: List[ZoneCmdRow] = []
    ref_rows: List[RefRow] = []
    err_rows: List[ErrRow] = []

    # Totals
    total_files = 0
    total_parsed = 0
    total_changed = 0
    total_entities_written = 0
    total_edges_written = 0
    total_cmd_rows = 0
    total_ref_rows = 0
    total_err_rows = 0

    def _log(line: str) -> None:
        if quiet:
            return
        print(line)
        if log_path is not None:
            log_path.parent.mkdir(parents=True, exist_ok=True)
            with log_path.open("a", encoding="utf-8") as f:
                f.write(line + "\n")

    started = time.time()

    for zi, zone_dir in enumerate(zone_dirs, start=1):
        zone_started = time.time()
        zone_num = int(zone_dir.name)

        # Pull zone name from DB if we have it already.
        zone_name: str = ""
        row = conn.execute("SELECT name FROM entity WHERE etype='zone' AND vnum=?", (zone_num,)).fetchone()
        if row and row[0]:
            zone_name = str(row[0])

        z_total_files = 0
        z_parsed = 0
        z_changed = 0
        z_entities_written = 0
        z_edges_written = 0
        z_cmd_rows = 0
        z_ref_rows = 0
        z_err_rows = 0

        for kind, path in iter_zone_files(zone_dir):
            z_total_files += 1
            total_files += 1

            relpath = str(path.relative_to(world_root))
            existing_relpaths.add(relpath)

            try:
                st = path.stat()
            except FileNotFoundError:
                continue

            prev = conn.execute("SELECT mtime,size,sha1 FROM file_state WHERE path=?", (relpath,)).fetchone()
            if prev is not None and (not use_sha1):
                if float(prev[0]) == float(st.st_mtime) and int(prev[1]) == int(st.st_size):
                    # unchanged
                    continue

            try:
                data, h, raw = load_json_file(path, use_sha1=use_sha1)
            except Exception as e:
                z_err_rows += 1
                total_err_rows += 1
                err_rows.append((relpath, zone_num, kind, f"JSON load failed: {e}", traceback.format_exc()))
                continue

            z_parsed += 1
            total_parsed += 1

            if not needs_update(conn, relpath, st.st_mtime, st.st_size, h):
                continue

            z_changed += 1
            total_changed += 1

            # On incremental runs, clear derived rows for this file.
            if not full:
                delete_by_source(conn, relpath)

            # Parse entity row
            zone_hint = zone_num
            try:
                pe = parse_entity(kind, relpath, data, zone_hint)
            except Exception as e:
                z_err_rows += 1
                total_err_rows += 1
                err_rows.append((relpath, zone_num, kind, f"parse_entity failed: {e}", traceback.format_exc()))
                upsert_file_state(conn, relpath, st.st_mtime, st.st_size, h)
                continue

            if pe is not None:
                # Update zone_name from zone.json if present
                if pe.etype == "zone" and pe.name:
                    zone_name = pe.name

                entity_rows.append(
                    (
                        pe.etype,
                        pe.vnum,
                        pe.zone,
                        pe.relpath,
                        pe.name,
                        pe.keywords,
                        pe.short_descr,
                        pe.last_edited,
                        json_dumps(pe.extra),
                        raw.decode("utf-8", errors="replace") if store_raw_json else None,
                    )
                )
                z_entities_written += 1
                total_entities_written += 1

                # Structured edges
                try:
                    if kind == "room":
                        edge_rows.extend(edges_from_room(relpath, pe.vnum, pe.zone, data))
                    elif kind == "object":
                        edge_rows.extend(edges_from_object(relpath, pe.vnum, pe.zone, data))
                    elif kind == "mobile":
                        edge_rows.extend(edges_from_mobile(relpath, pe.vnum, pe.zone, data))
                    elif kind == "assemble":
                        edge_rows.extend(edges_from_assemble(relpath, pe.vnum, pe.zone, data))
                    elif kind == "shop":
                        edge_rows.extend(edges_from_shop(relpath, pe.vnum, pe.zone, data))
                    elif kind == "zone":
                        cmds = data.get("cmds")
                        if isinstance(cmds, list):
                            e, z = edges_from_zone_cmds(relpath, pe.vnum, cmds)
                            edge_rows.extend(e)
                            zone_cmd_rows.extend(z)
                            z_cmd_rows += len(z)
                            total_cmd_rows += len(z)
                except Exception as e:
                    z_err_rows += 1
                    total_err_rows += 1
                    err_rows.append((relpath, zone_num, kind, f"edge extraction failed: {e}", traceback.format_exc()))

                # Deep refs (mostly scripts)
                do_deep = deep_refs_mode != "none" and (deep_refs_mode == "all" or kind == "script")
                if do_deep:
                    try:
                        for keypath, key, iv in walk_keyed_ints(data):
                            guess = guess_etype_from_key(key)
                            ref_rows.append((relpath, pe.etype, pe.vnum, keypath, guess, int(iv), json_dumps({"key": key})))
                            z_ref_rows += 1
                            total_ref_rows += 1
                            # For scripts, also create edges when the guess is specific.
                            if kind == "script" and guess in {"room", "object", "mobile", "script", "zone"}:
                                edge_rows.append((relpath, pe.etype, pe.vnum, guess, int(iv), f"ref:{key}", pe.zone, json_dumps({"keypath": keypath})))
                    except Exception as e:
                        z_err_rows += 1
                        total_err_rows += 1
                        err_rows.append((relpath, zone_num, kind, f"deep refs failed: {e}", traceback.format_exc()))

            upsert_file_state(conn, relpath, st.st_mtime, st.st_size, h)

            # Periodic flush to keep memory bounded.
            if (len(entity_rows) + len(edge_rows) + len(zone_cmd_rows) + len(ref_rows) + len(err_rows)) >= 10000:
                flush(conn, entity_rows, edge_rows, zone_cmd_rows, ref_rows, err_rows)
                conn.commit()
                edge_rows.clear()
                entity_rows.clear()
                zone_cmd_rows.clear()
                ref_rows.clear()
                err_rows.clear()

        # End of zone: flush + commit
        flush(conn, entity_rows, edge_rows, zone_cmd_rows, ref_rows, err_rows)
        conn.commit()

        z_edges_written = 0
        if edge_rows:
            z_edges_written = len(edge_rows)
        # edge_rows got cleared in flush? flush doesn't clear. We'll report via deltas instead:
        # We already tracked entity counts, cmd rows, ref rows; for edges, compute per-zone by querying delta is expensive.
        # Instead, estimate from buffered edges written this zone by tracking len added before flush.
        # To keep it honest, we will report "edges buffered" rather than exact inserted.

        # Clear buffers after flush
        edge_rows.clear()
        entity_rows.clear()
        zone_cmd_rows.clear()
        ref_rows.clear()
        err_rows.clear()

        elapsed = time.time() - started
        zone_elapsed = time.time() - zone_started
        avg = elapsed / max(1, zi)
        eta = avg * max(0, total_zones - zi)

        name_part = f" \"{zone_name}\"" if zone_name else ""
        _log(
            f"[{zi:03d}/{total_zones:03d}] zone={zone_num}{name_part} files={z_total_files} parsed={z_parsed} changed={z_changed} "
            f"entities+={z_entities_written} cmds+={z_cmd_rows} refs+={z_ref_rows} errs+={z_err_rows} "
            f"({zone_elapsed:.2f}s, eta {fmt_dur(eta)})"
        )

    # Only delete missing files when doing an all-zones build.
    if zones is None:
        missing_deleted = delete_missing_files(conn, existing_relpaths)
        if missing_deleted:
            _log(f"Removed missing files from DB: {missing_deleted}")

    conn.execute("ANALYZE")
    conn.commit()
    conn.close()

    _log(
        f"DONE. world_root={world_root} db={db_path} zones={'ALL' if zones is None else ','.join(map(str, sorted(zones)))} "
        f"files={total_files} parsed={total_parsed} changed={total_changed} entities_written={total_entities_written} "
        f"zone_cmd_rows={total_cmd_rows} ref_rows={total_ref_rows} errors={total_err_rows} elapsed={fmt_dur(time.time()-started)}"
    )
