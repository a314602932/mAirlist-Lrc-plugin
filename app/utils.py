# -*- coding: utf-8 -*-
import json, os
from PyQt5 import QtGui

_DEFAULT = {
    "ui": {
        "font_family": "Microsoft YaHei",
        "font_size": 22,
        "text_color": "#FFFFFF",
        "highlight_color": "#00AEEF",
    },
    "features": {
        "show_cd": True,
        "show_progress": True,
        "show_timecode": True
    },
    "server": {
        "host": "127.0.0.1",
        "port": 5005
    }
}

def ensure_dirs():
    os.makedirs(os.path.join("assets", "cache"), exist_ok=True)
    os.makedirs("lyrics", exist_ok=True)

def load_config() -> dict:
    if os.path.exists("config.json"):
        try:
            with open("config.json", "r", encoding="utf-8") as f:
                cfg = json.load(f)
                return _merge(_DEFAULT, cfg)
        except Exception:
            pass
    return _DEFAULT.copy()

def save_config(cfg: dict):
    with open("config.json", "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)

def _merge(a: dict, b: dict) -> dict:
    out = a.copy()
    for k, v in b.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _merge(out[k], v)
        else:
            out[k] = v
    return out

def qcolor_from_hex(s: str) -> QtGui.QColor:
    return QtGui.QColor(s if s else "#FFFFFF")
