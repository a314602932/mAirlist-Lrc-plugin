# -*- coding: utf-8 -*-
"""
简易 LRC 解析：返回按时间排序的 (ms, text) 列表
"""
import os
import re
from dataclasses import dataclass
from typing import List, Tuple, Optional


@dataclass
class LRC:
    lines: List[Tuple[int, str]]  # (time_ms, text)

    def index_at(self, ms: int) -> int:
        """返回 <= ms 的最后一行索引；若无，返回 0."""
        if not self.lines:
            return 0
        lo, hi = 0, len(self.lines)-1
        ans = 0
        while lo <= hi:
            mid = (lo + hi) // 2
            if self.lines[mid][0] <= ms:
                ans = mid; lo = mid + 1
            else:
                hi = mid - 1
        return ans


_TIME = re.compile(r"\[(\d{1,2}):(\d{1,2})(?:\.(\d{1,2}))?\]")

def _parse_lrc_text(text: str) -> LRC:
    lines: List[Tuple[int, str]] = []
    for raw in text.splitlines():
        tags = list(_TIME.finditer(raw))
        lyric = _TIME.sub("", raw).strip()
        for m in tags:
            mm = int(m.group(1)); ss = int(m.group(2)); xx = int(m.group(3) or 0)
            ms = (mm * 60 + ss) * 1000 + (xx * (10 if len(m.group(3) or "") == 1 else 10**(3-len(m.group(3) or "0"))))
            if lyric:
                lines.append((ms, lyric))
    lines.sort(key=lambda x: x[0])
    return LRC(lines=lines)


def load_lrc_for(artist: str, title: str, base="lyrics") -> Optional[LRC]:
    """根据命名规则在目录中查找 LRC."""
    cand = []
    safe_artist = (artist or "").strip()
    safe_title = (title or "").strip()
    if safe_artist and safe_title:
        cand += [f"{safe_artist} - {safe_title}.lrc", f"{safe_title} - {safe_artist}.lrc"]
    if safe_title:
        cand += [f"{safe_title}.lrc"]
    for name in cand:
        path = os.path.join(base, name)
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return _parse_lrc_text(f.read())
            except Exception:
                pass
    return None
