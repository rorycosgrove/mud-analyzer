#!/usr/bin/env python3
"""
world_lookup.py

Lazy cached lookups for AddictMUD JSON world data.

Expected layout (world root == current directory when running scripts):
  <zone>/<zone>.json
  <zone>/{room,object,mobile,script,assemble}/<vnum>.json

Important: zone directories can represent large VNUM ranges, so vnum//100 is not
reliable. We:
  - Prefer a zone "hint" (when summarizing zone N, default to directory N)
  - If that fails, build a lightweight index from zone metadata (<zone>/<zone>.json)
    and resolve via start_vnum=zone*100 and top=zone.top.
"""

from __future__ import annotations

import bisect
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, List


def parse_int(v: Any, default: int = 0) -> int:
    try:
        return int(v)
    except Exception:
        return default


@dataclass
class World:
    root: Path
    hint_zone: Optional[int] = None

    _cache: Dict[Tuple[str, int], Optional[Dict[str, Any]]] = field(default_factory=dict)
    _zone_ranges: List[Tuple[int, int, int]] = field(default_factory=list)  # (start_vnum, top_vnum, zone)
    _zone_starts: List[int] = field(default_factory=list)
    _zone_index_built: bool = False

    def set_hint_zone(self, zone: Optional[int]) -> None:
        self.hint_zone = zone

    def zone_dir(self, zone: int) -> Path:
        return self.root / str(zone)

    def zone_file(self, zone: int) -> Path:
        return self.zone_dir(zone) / f"{zone}.json"

    def load_zone(self, zone: int) -> Optional[Dict[str, Any]]:
        p = self.zone_file(zone)
        if not p.exists():
            return None
        return self._read_json(p)

    def _maybe_build_zone_index(self) -> None:
        if self._zone_index_built:
            return

        ranges: List[Tuple[int, int, int]] = []
        for d in self.root.iterdir():
            if not d.is_dir() or not d.name.isdigit():
                continue
            z = int(d.name)
            zp = d / f"{z}.json"
            if not zp.exists():
                continue
            zj = self._read_json(zp)
            if not zj:
                continue
            top = zj.get("top")
            zone_num = zj.get("zone", z)
            if isinstance(top, int) and isinstance(zone_num, int):
                start = int(zone_num) * 100
                ranges.append((start, int(top), int(zone_num)))

        ranges.sort(key=lambda x: x[0])
        self._zone_ranges = ranges
        self._zone_starts = [r[0] for r in ranges]
        self._zone_index_built = True

    def _zone_for_vnum(self, vnum: int) -> Optional[int]:
        vnum = int(vnum)

        # 1) Use hint first (fast path while summarizing a zone).
        if self.hint_zone is not None:
            return int(self.hint_zone)

        # 2) Heuristic: directory == vnum//100.
        z1 = vnum // 100
        if (self.root / str(z1)).is_dir():
            return z1

        # 3) Heuristic: large-zone directory == floor(z1/10)*10.
        z2 = (z1 // 10) * 10
        if (self.root / str(z2)).is_dir():
            return z2

        # 4) Range index by zone metadata.
        self._maybe_build_zone_index()
        if not self._zone_ranges:
            return None

        i = bisect.bisect_right(self._zone_starts, vnum) - 1
        if 0 <= i < len(self._zone_ranges):
            start, top, zone = self._zone_ranges[i]
            if start <= vnum <= top:
                return zone

        # 5) Fallback scan.
        for start, top, zone in self._zone_ranges:
            if start <= vnum <= top:
                return zone
        return None

    def entity_file(self, kind: str, vnum: int) -> Optional[Path]:
        zone = self._zone_for_vnum(vnum)
        if zone is None:
            return None
        return self.zone_dir(zone) / kind / f"{int(vnum)}.json"

    def load(self, kind: str, vnum: int) -> Optional[Dict[str, Any]]:
        vnum = int(vnum)
        key = (kind, vnum)
        if key in self._cache:
            return self._cache[key]

        # Try using hint.
        p = self.entity_file(kind, vnum)
        if p is not None and p.exists():
            data = self._read_json(p)
            self._cache[key] = data
            return data

        # If hint zone is set and failed, retry without hint.
        if self.hint_zone is not None:
            old_hint = self.hint_zone
            self.hint_zone = None
            try:
                p2 = self.entity_file(kind, vnum)
                if p2 is not None and p2.exists():
                    data2 = self._read_json(p2)
                    self._cache[key] = data2
                    return data2
            finally:
                self.hint_zone = old_hint

        self._cache[key] = None
        return None

    def _read_json(self, p: Path) -> Optional[Dict[str, Any]]:
        try:
            with p.open("r", encoding="utf-8") as f:
                obj = json.load(f)
            return obj if isinstance(obj, dict) else None
        except Exception:
            return None

    # ---- brief helpers: always include vnum + readable text ----

    def room_brief(self, vnum: int) -> str:
        r = self.load("room", vnum)
        if r:
            name = r.get("name") or r.get("title")
            if isinstance(name, str) and name.strip():
                return f'[{vnum}] "{name}"'
        return f"[{vnum}] (room missing)"

    def mob_brief(self, vnum: int) -> str:
        m = self.load("mobile", vnum)
        if m:
            short = m.get("short_descr") or m.get("short_desc") or m.get("name")
            if isinstance(short, str) and short.strip():
                lvl = m.get("level")
                align = m.get("alignment")
                extra = []
                if isinstance(lvl, int):
                    extra.append(f"lvl {lvl}")
                if isinstance(align, int):
                    extra.append(f"align {align}")
                suffix = f" ({', '.join(extra)})" if extra else ""
                return f'[{vnum}] "{short}"{suffix}'
        return f"[{vnum}] (mob missing)"

    def obj_brief(self, vnum: int) -> str:
        o = self.load("object", vnum)
        if o:
            short = o.get("short_desc") or o.get("short_descr") or o.get("name")
            if isinstance(short, str) and short.strip():
                t = o.get("type_flag")
                suffix = f" (type {t})" if isinstance(t, int) else ""
                return f'[{vnum}] "{short}"{suffix}'
        return f"[{vnum}] (object missing)"

    def detect_entity_type(self, vnum: int) -> Optional[str]:
        """Detect entity type by checking which file exists for the VNUM"""
        vnum = int(vnum)
        zone = self._zone_for_vnum(vnum)
        if zone is None:
            return None
        
        zone_dir = self.zone_dir(zone)
        for entity_type in ["object", "mobile", "room", "script", "assemble"]:
            entity_file = zone_dir / entity_type / f"{vnum}.json"
            if entity_file.exists():
                return entity_type
        return None
    
    def get_entity_brief(self, vnum: int) -> str:
        """Get brief description for any entity type by auto-detecting type"""
        entity_type = self.detect_entity_type(vnum)
        if entity_type == "object":
            return self.obj_brief(vnum)
        elif entity_type == "mobile":
            return self.mob_brief(vnum)
        elif entity_type == "room":
            return self.room_brief(vnum)
        elif entity_type == "script":
            return self.script_brief(vnum)
        else:
            return f"[{vnum}] (unknown entity type)"
    
    def load_any(self, vnum: int) -> Optional[Dict[str, Any]]:
        """Load entity data by auto-detecting type"""
        entity_type = self.detect_entity_type(vnum)
        if entity_type:
            return self.load(entity_type, vnum)
        return None
    
    def script_brief(self, vnum: int) -> str:
        s = self.load("script", vnum)
        if s:
            name = s.get("name") or "(no name)"
            stype = s.get("type")
            trig = s.get("trigger_type")
            bits = []
            if stype is not None:
                bits.append(f"type={stype}")
            if trig is not None:
                bits.append(f"trigger={trig}")
            suffix = f" ({', '.join(bits)})" if bits else ""
            return f'[{vnum}] "{name}"{suffix}'
        return f"[{vnum}] (script missing)"
