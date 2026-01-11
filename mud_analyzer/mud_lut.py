#!/usr/bin/env python3
"""
MUD World SQLite LUT Builder

This script loads CircleMUD/DikuMUD world JSON data and builds a persistent SQLite lookup table.
It processes zones, rooms, objects, mobiles, scripts, shops, assemblies, and their cross-references.
Designed for incremental updates and fast lookup by external tools (e.g. APIs or MCP).

Usage:
    python mud_lut.py [--root <path>] [--db <path>] [--zones <list>] [--sha1] [--log <path>]

Options:
    --root <path>    Root directory of the world (default: current directory).
    --db <path>      Path to the SQLite database file (default: .mud_cache/lut.sqlite).
    --zones <list>   Comma-separated list of zone numbers to process (default: all zones).
    --sha1           Use SHA1 checksum for file change detection (default: use file mtime/size).
    --log <path>     Path to log file (default: stdout).

Integration:
    The resulting SQLite DB contains tables for entities (rooms, objects, mobiles, zones, scripts, shops, assemblies),
    edges (exits, zone_commands, script_attachments, object_contents, shop_rooms, script_refs),
    and metadata for incremental updates. Use this DB for fast lookups without recompute.

"""

import os
import sys
import argparse
import sqlite3
import json
import hashlib
import time

# -- Setup argument parsing --
parser = argparse.ArgumentParser(description="Build MUD world SQLite LUT")
parser.add_argument("--root", default=".", help="Root directory of the world")
parser.add_argument("--db", default=".mud_cache/lut.sqlite", help="Path to SQLite database")
parser.add_argument("--zones", help="Comma-separated list of zone numbers to process")
parser.add_argument("--sha1", action="store_true", help="Use SHA1 for file change detection")
parser.add_argument("--log", help="Path to log file (default stdout)")
args = parser.parse_args()

# Setup logging
if args.log:
    log_file = open(args.log, "a")
else:
    log_file = None

def log(msg):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    if log_file:
        log_file.write(line + "\n")
        log_file.flush()
    else:
        print(line)

# Create or open database
db_path = args.db
os.makedirs(os.path.dirname(db_path), exist_ok=True) if os.path.dirname(db_path) else None
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Enable foreign keys and performance PRAGMAs
cur.execute("PRAGMA foreign_keys = ON")
cur.execute("PRAGMA journal_mode = WAL")
cur.execute("PRAGMA synchronous = NORMAL")

# Create tables
cur.execute("""CREATE TABLE IF NOT EXISTS zones (
    id INTEGER PRIMARY KEY,
    vnum INTEGER UNIQUE,
    name TEXT,
    author TEXT,
    top INTEGER,
    lifespan INTEGER,
    reset_mode INTEGER,
    created INTEGER,
    last_mod INTEGER,
    flags TEXT,
    raw JSON,
    filepath TEXT,
    mtime REAL,
    size INTEGER,
    sha1 TEXT
);""")
cur.execute("""CREATE TABLE IF NOT EXISTS rooms (
    id INTEGER PRIMARY KEY,
    vnum INTEGER,
    zone INTEGER,
    name TEXT,
    description TEXT,
    room_flags TEXT,
    sector INTEGER,
    raw JSON,
    filepath TEXT,
    mtime REAL,
    size INTEGER,
    sha1 TEXT
);""")
cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_rooms_vnum ON rooms(vnum, zone);")
cur.execute("""CREATE TABLE IF NOT EXISTS mobiles (
    id INTEGER PRIMARY KEY,
    vnum INTEGER,
    zone INTEGER,
    name TEXT,
    short_desc TEXT,
    long_desc TEXT,
    keywords TEXT,
    stats JSON,
    raw JSON,
    filepath TEXT,
    mtime REAL,
    size INTEGER,
    sha1 TEXT
);""")
cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_mobiles_vnum ON mobiles(vnum, zone);")
cur.execute("""CREATE TABLE IF NOT EXISTS objects (
    id INTEGER PRIMARY KEY,
    vnum INTEGER,
    zone INTEGER,
    name TEXT,
    short_desc TEXT,
    long_desc TEXT,
    keywords TEXT,
    type TEXT,
    values JSON,
    effects JSON,
    weight INTEGER,
    cost INTEGER,
    raw JSON,
    filepath TEXT,
    mtime REAL,
    size INTEGER,
    sha1 TEXT
);""")
cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_objects_vnum ON objects(vnum, zone);")
cur.execute("""CREATE TABLE IF NOT EXISTS shops (
    id INTEGER PRIMARY KEY,
    vnum INTEGER,
    zone INTEGER,
    keeper INTEGER,
    buy_types TEXT,
    profit_buy INTEGER,
    profit_sell INTEGER,
    open1 INTEGER,
    open2 INTEGER,
    close1 INTEGER,
    close2 INTEGER,
    messages JSON,
    rooms JSON,
    raw JSON,
    filepath TEXT,
    mtime REAL,
    size INTEGER,
    sha1 TEXT
);""")
cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_shops_vnum ON shops(vnum, zone);")
cur.execute("""CREATE TABLE IF NOT EXISTS scripts (
    id INTEGER PRIMARY KEY,
    vnum INTEGER,
    zone INTEGER,
    name TEXT,
    type INTEGER,
    trigger_type INTEGER,
    arglist TEXT,
    code TEXT,
    raw JSON,
    filepath TEXT,
    mtime REAL,
    size INTEGER,
    sha1 TEXT
);""")
cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_scripts_vnum ON scripts(vnum, zone);")
cur.execute("""CREATE TABLE IF NOT EXISTS assembles (
    id INTEGER PRIMARY KEY,
    vnum INTEGER,
    zone INTEGER,
    keywords TEXT,
    parts TEXT,
    raw JSON,
    filepath TEXT,
    mtime REAL,
    size INTEGER,
    sha1 TEXT
);""")
cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_assembles_vnum ON assembles(vnum, zone);")
cur.execute("""CREATE TABLE IF NOT EXISTS zone_commands (
    id INTEGER PRIMARY KEY,
    zone INTEGER,
    cmd TEXT,
    if_flag INTEGER,
    arg1 INTEGER,
    arg2 INTEGER,
    arg3 INTEGER,
    prob INTEGER,
    raw JSON,
    sequence INTEGER
);""")
cur.execute("""CREATE TABLE IF NOT EXISTS exits (
    id INTEGER PRIMARY KEY,
    from_room INTEGER REFERENCES rooms(id) ON DELETE CASCADE,
    direction TEXT,
    to_room INTEGER REFERENCES rooms(id) ON DELETE SET NULL,
    description TEXT
);""")
cur.execute("""CREATE TABLE IF NOT EXISTS script_attachments (
    id INTEGER PRIMARY KEY,
    entity_type TEXT,
    entity_id INTEGER,
    script_id INTEGER,
    FOREIGN KEY(entity_id) REFERENCES rooms(id) ON DELETE CASCADE,
    FOREIGN KEY(script_id) REFERENCES scripts(id) ON DELETE CASCADE
);""")
cur.execute("""CREATE TABLE IF NOT EXISTS object_contents (
    id INTEGER PRIMARY KEY,
    container_obj INTEGER REFERENCES objects(id) ON DELETE CASCADE,
    contained_obj INTEGER REFERENCES objects(id) ON DELETE CASCADE
);""")
cur.execute("""CREATE TABLE IF NOT EXISTS shop_rooms (
    id INTEGER PRIMARY KEY,
    shop_id INTEGER REFERENCES shops(id) ON DELETE CASCADE,
    room_id INTEGER REFERENCES rooms(id) ON DELETE CASCADE
);""")
cur.execute("""CREATE TABLE IF NOT EXISTS script_refs (
    id INTEGER PRIMARY KEY,
    script_id INTEGER REFERENCES scripts(id) ON DELETE CASCADE,
    ref_vnum INTEGER
);""")
cur.execute("""CREATE TABLE IF NOT EXISTS file_map (
    path TEXT PRIMARY KEY,
    mtime REAL,
    size INTEGER,
    sha1 TEXT
);""")
conn.commit()

def compute_sha1(path):
    """Compute SHA1 hash of a file."""
    hash_sha1 = hashlib.sha1()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hash_sha1.update(chunk)
    return hash_sha1.hexdigest()

def file_changed(path):
    """Check if file is new or changed since last scan; update metadata."""
    path = os.path.abspath(path)
    st = os.stat(path)
    mtime = st.st_mtime
    size = st.st_size
    sha = compute_sha1(path) if args.sha1 else None
    cur.execute("SELECT mtime, size, sha1 FROM file_map WHERE path = ?", (path,))
    row = cur.fetchone()
    if row:
        old_mtime, old_size, old_sha = row
        if args.sha1:
            changed = (old_sha != sha)
        else:
            changed = (old_mtime != mtime or old_size != size)
        if changed:
            cur.execute("UPDATE file_map SET mtime=?, size=?, sha1=? WHERE path=?", (mtime, size, sha, path))
            conn.commit()
        return changed
    else:
        cur.execute("INSERT OR REPLACE INTO file_map(path, mtime, size, sha1) VALUES(?,?,?,?)", (path, mtime, size, sha))
        conn.commit()
        return True

def process_zone(zone):
    """Load a zone file, insert zone data and parse zone commands."""
    zone_id = zone["vnum"]
    path = os.path.join(args.root, str(zone_id), f"{zone_id}.json")
    if not os.path.exists(path):
        log(f"Zone file not found: {path}")
        return
    changed = file_changed(path)
    if not changed:
        log(f"Zone {zone_id}: no change")
    with open(path) as f:
        data = json.load(f)
    # Insert or update zone metadata
    cur.execute("""INSERT OR REPLACE INTO zones(vnum, name, author, top, lifespan, reset_mode, created, last_mod, flags, raw, filepath, mtime, size, sha1)
        VALUES(?,?,?,?,?,?,?,?,?,?,?, ?, ?, ?)""", (
        data.get("vnum", zone_id),
        data.get("name"),
        data.get("author"),
        data.get("top"),
        data.get("lifespan"),
        data.get("reset_mode"),
        data.get("created"),
        data.get("last_mod"),
        data.get("flags"),
        json.dumps(data.get("cmds", [])),
        path, os.path.getmtime(path), os.path.getsize(path),
        compute_sha1(path) if args.sha1 else None
    ))
    conn.commit()
    # Clear old commands and insert new
    cur.execute("DELETE FROM zone_commands WHERE zone = ?", (zone_id,))
    seq = 0
    for cmd in data.get("cmds", []):
        seq += 1
        cur.execute("""INSERT INTO zone_commands(zone, cmd, if_flag, arg1, arg2, arg3, prob, raw, sequence)
            VALUES(?,?,?,?,?,?,?,?,?)""", (
            zone_id,
            cmd.get("cmd"),
            cmd.get("flag"),
            cmd.get("arg1"),
            cmd.get("arg2"),
            cmd.get("arg3"),
            cmd.get("prob"),
            json.dumps(cmd),
            seq
        ))
    conn.commit()

def process_rooms(zone_id):
    """Load room JSON files for a zone and build exit edges."""
    dir_path = os.path.join(args.root, str(zone_id), "room")
    if not os.path.isdir(dir_path):
        return
    for fname in os.listdir(dir_path):
        if not fname.endswith(".json"): 
            continue
        path = os.path.join(dir_path, fname)
        if not file_changed(path):
            continue
        with open(path) as f:
            data = json.load(f)
        vnum = data.get("vnum")
        cur.execute("DELETE FROM rooms WHERE vnum=? AND zone=?", (vnum, zone_id))
        cur.execute("""INSERT INTO rooms(vnum, zone, name, description, room_flags, sector, raw, filepath, mtime, size, sha1)
            VALUES(?,?,?,?,?,?,?,?,?,?,?)""", (
            vnum,
            zone_id,
            data.get("name"),
            data.get("descr"),
            data.get("room_flags"),
            data.get("sector"),
            json.dumps(data),
            path, os.path.getmtime(path), os.path.getsize(path),
            compute_sha1(path) if args.sha1 else None
        ))
    conn.commit()
    # Rebuild exits for this zone's rooms
    cur.execute("""DELETE FROM exits WHERE from_room IN (
        SELECT id FROM rooms WHERE zone=?
    )""", (zone_id,))
    cur.execute("SELECT id, raw FROM rooms WHERE zone=?", (zone_id,))
    for room_id, raw in cur.fetchall():
        room_data = json.loads(raw)
        for direction, exitdata in (room_data.get("exits") or {}).items():
            to_room = exitdata.get("to_room")
            descr = exitdata.get("descr", "")
            cur.execute("SELECT id FROM rooms WHERE vnum=? AND zone=?", (to_room, zone_id))
            row = cur.fetchone()
            to_room_id = row[0] if row else None
            cur.execute("INSERT INTO exits(from_room, direction, to_room, description) VALUES(?,?,?,?)", (
                room_id, direction, to_room_id, descr
            ))
    conn.commit()

def process_mobiles(zone_id):
    """Load mobile JSON files for a zone."""
    dir_path = os.path.join(args.root, str(zone_id), "mobile")
    if not os.path.isdir(dir_path):
        return
    for fname in os.listdir(dir_path):
        if not fname.endswith(".json"):
            continue
        path = os.path.join(dir_path, fname)
        if not file_changed(path):
            continue
        with open(path) as f:
            data = json.load(f)
        vnum = data.get("vnum")
        cur.execute("DELETE FROM mobiles WHERE vnum=? AND zone=?", (vnum, zone_id))
        cur.execute("""INSERT INTO mobiles(vnum, zone, name, short_desc, long_desc, keywords, stats, raw, filepath, mtime, size, sha1)
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""", (
            vnum,
            zone_id,
            data.get("name"),
            data.get("short_descr"),
            data.get("long_descr"),
            ",".join(data.get("aliases", [])),
            json.dumps({k: data.get(k) for k in ["level","alignment","armor","race","sex","money"] if k in data}),
            json.dumps(data),
            path, os.path.getmtime(path), os.path.getsize(path),
            compute_sha1(path) if args.sha1 else None
        ))
    conn.commit()

def process_objects(zone_id):
    """Load object JSON files for a zone."""
    dir_path = os.path.join(args.root, str(zone_id), "object")
    if not os.path.isdir(dir_path):
        return
    for fname in os.listdir(dir_path):
        if not fname.endswith(".json"):
            continue
        path = os.path.join(dir_path, fname)
        if not file_changed(path):
            continue
        with open(path) as f:
            data = json.load(f)
        vnum = data.get("vnum")
        cur.execute("DELETE FROM objects WHERE vnum=? AND zone=?", (vnum, zone_id))
        cur.execute("""INSERT INTO objects(vnum, zone, name, short_desc, long_desc, keywords, type, values, effects, weight, cost, raw, filepath, mtime, size, sha1)
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", (
            vnum,
            zone_id,
            data.get("name"),
            data.get("short_descr"),
            data.get("long_descr"),
            ",".join(data.get("aliases", [])),
            data.get("type", {}).get("note"),
            json.dumps(data.get("values")),
            json.dumps(data.get("affects", [])),
            data.get("weight"),
            data.get("cost"),
            json.dumps(data),
            path, os.path.getmtime(path), os.path.getsize(path),
            compute_sha1(path) if args.sha1 else None
        ))
    conn.commit()

def process_shops(zone_id):
    """Load shop JSON files for a zone."""
    dir_path = os.path.join(args.root, str(zone_id), "shop")
    if not os.path.isdir(dir_path):
        return
    for fname in os.listdir(dir_path):
        if not fname.endswith(".json"):
            continue
        path = os.path.join(dir_path, fname)
        if not file_changed(path):
            continue
        with open(path) as f:
            data = json.load(f)
        vnum = data.get("vnum")
        cur.execute("DELETE FROM shops WHERE vnum=? AND zone=?", (vnum, zone_id))
        cur.execute("""INSERT INTO shops(vnum, zone, keeper, buy_types, profit_buy, profit_sell, open1, open2, close1, close2, messages, rooms, raw, filepath, mtime, size, sha1)
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", (
            vnum,
            zone_id,
            data.get("keeper"),
            data.get("trade_with"),
            data.get("profit_buy"),
            data.get("profit_sell"),
            data.get("open1"),
            data.get("open2"),
            data.get("close1"),
            data.get("close2"),
            json.dumps({
                "no_such_item": data.get("no_such_item",""),
                "no_buy": data.get("no_buy",""),
                "missing_cash1": data.get("missing_cash1",""),
                "missing_cash2": data.get("missing_cash2","")
            }),
            json.dumps(data.get("rooms", [])),
            json.dumps(data),
            path, os.path.getmtime(path), os.path.getsize(path),
            compute_sha1(path) if args.sha1 else None
        ))
    conn.commit()
    # Build shop_rooms relationships
    cur.execute("""DELETE FROM shop_rooms WHERE shop_id IN (
        SELECT id FROM shops WHERE zone=?
    )""", (zone_id,))
    cur.execute("SELECT id, rooms FROM shops WHERE zone=?", (zone_id,))
    for shop_id, rooms_json in cur.fetchall():
        rooms = json.loads(rooms_json)
        for r in rooms:
            cur.execute("SELECT id FROM rooms WHERE vnum=? AND zone=?", (r, zone_id))
            row = cur.fetchone()
            if row:
                room_id = row[0]
                cur.execute("INSERT INTO shop_rooms(shop_id, room_id) VALUES(?,?)", (shop_id, room_id))
    conn.commit()

def process_scripts(zone_id):
    """Load script JSON files for a zone."""
    dir_path = os.path.join(args.root, str(zone_id), "script")
    if not os.path.isdir(dir_path):
        return
    for fname in os.listdir(dir_path):
        if not fname.endswith(".json"):
            continue
        path = os.path.join(dir_path, fname)
        if not file_changed(path):
            continue
        with open(path) as f:
            data = json.load(f)
        vnum = data.get("vnum")
        cur.execute("DELETE FROM scripts WHERE vnum=? AND zone=?", (vnum, zone_id))
        cur.execute("""INSERT INTO scripts(vnum, zone, name, type, trigger_type, arglist, code, raw, filepath, mtime, size, sha1)
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""", (
            vnum,
            zone_id,
            data.get("name"),
            data.get("type"),
            data.get("trigger_type"),
            data.get("arglist"),
            data.get("code"),
            json.dumps(data),
            path, os.path.getmtime(path), os.path.getsize(path),
            compute_sha1(path) if args.sha1 else None
        ))
    conn.commit()
    # Extract numeric references from script code
    cur.execute("DELETE FROM script_refs WHERE script_id IN (SELECT id FROM scripts WHERE zone=?)", (zone_id,))
    cur.execute("SELECT id, code FROM scripts WHERE zone=?", (zone_id,))
    for script_id, code in cur.fetchall():
        nums = set()
        for token in code.replace("\n", " ").split():
            if token.isdigit():
                nums.add(int(token))
        for num in nums:
            cur.execute("INSERT INTO script_refs(script_id, ref_vnum) VALUES(?,?)", (script_id, num))
    conn.commit()

def process_assembles(zone_id):
    """Load assembly recipe JSON files for a zone."""
    dir_path = os.path.join(args.root, str(zone_id), "assemble")
    if not os.path.isdir(dir_path):
        return
    for fname in os.listdir(dir_path):
        if not fname.endswith(".json"):
            continue
        path = os.path.join(dir_path, fname)
        if not file_changed(path):
            continue
        with open(path) as f:
            data = json.load(f)
        vnum = data.get("vnum")
        parts = ",".join(str(p) for p in data.get("parts", []))
        keywords = ",".join(data.get("keywords", []))
        cur.execute("DELETE FROM assembles WHERE vnum=? AND zone=?", (vnum, zone_id))
        cur.execute("""INSERT INTO assembles(vnum, zone, keywords, parts, raw, filepath, mtime, size, sha1)
            VALUES(?,?,?,?,?,?,?,?,?)""", (
            vnum,
            zone_id,
            keywords,
            parts,
            json.dumps(data),
            path, os.path.getmtime(path), os.path.getsize(path),
            compute_sha1(path) if args.sha1 else None
        ))
    conn.commit()

# Determine which zones to process
all_zone_dirs = [d for d in os.listdir(args.root) if os.path.isdir(os.path.join(args.root, d)) and d.isdigit()]
if args.zones:
    target_zones = []
    for z in args.zones.split(","):
        try:
            target_zones.append(int(z))
        except:
            log(f"Invalid zone: {z}")
else:
    target_zones = sorted(int(z) for z in all_zone_dirs)

log(f"Processing zones: {target_zones}")

# Process each zone
for zone_id in target_zones:
    process_rooms(zone_id)
    process_mobiles(zone_id)
    process_objects(zone_id)
    process_shops(zone_id)
    process_scripts(zone_id)
    process_assembles(zone_id)
    process_zone({"vnum": zone_id})

# Build script_attachments (rooms, objects, mobiles referencing scripts)
cur.execute("DELETE FROM script_attachments")
cur.execute("SELECT id, raw FROM mobiles")
for mob_id, raw in cur.fetchall():
    data = json.loads(raw)
    for sid in data.get("scripts", []):
        cur.execute("SELECT id FROM scripts WHERE vnum=?", (sid,))
        res = cur.fetchone()
        if res:
            script_id = res[0]
            cur.execute("INSERT INTO script_attachments(entity_type, entity_id, script_id) VALUES(?,?,?)",
                        ("mobile", mob_id, script_id))
cur.execute("SELECT id, raw FROM objects")
for obj_id, raw in cur.fetchall():
    data = json.loads(raw)
    for sid_str in (data.get("scripts") or {}):
        try:
            sid_int = int(sid_str)
        except:
            continue
        cur.execute("SELECT id FROM scripts WHERE vnum=?", (sid_int,))
        res = cur.fetchone()
        if res:
            script_id = res[0]
            cur.execute("INSERT INTO script_attachments(entity_type, entity_id, script_id) VALUES(?,?,?)",
                        ("object", obj_id, script_id))
cur.execute("SELECT id, raw FROM rooms")
for room_id, raw in cur.fetchall():
    data = json.loads(raw)
    for sid in data.get("scripts", []):
        cur.execute("SELECT id FROM scripts WHERE vnum=?", (sid,))
        res = cur.fetchone()
        if res:
            script_id = res[0]
            cur.execute("INSERT INTO script_attachments(entity_type, entity_id, script_id) VALUES(?,?,?)",
                        ("room", room_id, script_id))
conn.commit()

# Summary of counts
cur.execute("SELECT COUNT(*) FROM rooms")
room_count = cur.fetchone()[0]
cur.execute("SELECT COUNT(*) FROM mobiles")
mob_count = cur.fetchone()[0]
cur.execute("SELECT COUNT(*) FROM objects")
obj_count = cur.fetchone()[0]
cur.execute("SELECT COUNT(*) FROM shops")
shop_count = cur.fetchone()[0]
cur.execute("SELECT COUNT(*) FROM scripts")
script_count = cur.fetchone()[0]
cur.execute("SELECT COUNT(*) FROM assembles")
assem_count = cur.fetchone()[0]
log(f"Summary: Rooms={room_count}, Mobs={mob_count}, Objects={obj_count}, Shops={shop_count}, Scripts={script_count}, Assemblies={assem_count}")

# Close log and DB
if log_file:
    log_file.close()
conn.close()
