# -*- coding: utf-8 -*-
"""
mAirList Lyrics Overlay — v0.9.7
入口：启动 Qt GUI + HTTP 接收服务
"""
import os
import sys
from PyQt5 import QtWidgets
from app.overlay import Overlay
from app.http_server import NowPlayingEmitter, start_http_server
from app.utils import ensure_dirs, load_config

__version__ = "0.9.7"


def main():
    ensure_dirs()

    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName(f"mAirList Lyrics Overlay {__version__}")

    # 载入配置
    cfg = load_config()

    # 信号桥：HTTP 线程 -> GUI
    emitter = NowPlayingEmitter()

    # GUI
    ui = Overlay(cfg=cfg, emitter=emitter)
    ui.resize(900, 560)
    ui.show()

    # 启动 HTTP（默认 127.0.0.1:5005）
    host = cfg.get("server", {}).get("host", "127.0.0.1")
    port = int(cfg.get("server", {}).get("port", 5005))
    start_http_server(emitter=emitter, host=host, port=port)

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
