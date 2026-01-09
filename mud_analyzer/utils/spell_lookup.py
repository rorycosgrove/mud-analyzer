#!/usr/bin/env python3
"""
spell_lookup.py

NO source-code parsing. Loads spell/skill names from a local JSON file.

Default lookup file: spells.json (placed alongside the scripts, or in current dir).

Format: {"format": "...", "spells": {"<id>": {"name": "...", ...}, ...}}
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional

_cached_path: Optional[Path] = None
_cached_map: Optional[Dict[int, str]] = None


def load_spell_name_map(spells_json: Optional[str] = None) -> Dict[int, str]:
    """
    Load and cache spell id -> name mapping.

    spells_json:
      - None: try (script_dir/../data/spells.json), then (cwd/spells.json)
      - else: explicit path
    """
    global _cached_path, _cached_map

    cand: Optional[Path]
    if spells_json:
        cand = Path(spells_json).expanduser().resolve()
    else:
        script_dir = Path(__file__).resolve().parent
        # Look in data directory relative to utils
        p1 = script_dir.parent / "data" / "spells.json"
        p2 = Path.cwd() / "spells.json"
        cand = p1 if p1.exists() else p2 if p2.exists() else None

    if cand is None or not cand.exists():
        print(f"⚠️  Warning: spells.json not found. Checked: {script_dir.parent / 'data' / 'spells.json'}, {Path.cwd() / 'spells.json'}")
        _cached_path = None
        _cached_map = {}
        return _cached_map

    if _cached_path == cand and _cached_map is not None:
        return _cached_map

    try:
        data = json.loads(cand.read_text(encoding="utf-8"))
        spells = data.get("spells", {})
        out: Dict[int, str] = {}
        if isinstance(spells, dict):
            for k, v in spells.items():
                try:
                    sid = int(k)
                except Exception:
                    continue
                if isinstance(v, dict):
                    name = v.get("name")
                else:
                    name = v
                if isinstance(name, str) and name.strip():
                    out[sid] = name.strip()
        _cached_path = cand
        _cached_map = out
        print(f"✅ Loaded {len(out)} spells from {cand}")
        return out
    except Exception as e:
        print(f"❌ Error loading spells from {cand}: {e}")
        _cached_path = cand
        _cached_map = {}
        return _cached_map


def spell_name(spell_id: int, name_map: Dict[int, str]) -> str:
    try:
        sid = int(spell_id)
    except Exception:
        return str(spell_id)
    return name_map.get(sid, f"#{sid}")
