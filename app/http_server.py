# -*- coding: utf-8 -*-
"""
HTTP 接收服务：支持 GET / POST / multipart(albumart)
路由：
  - /nowplaying：接收正在播放信息
  - /health：健康检查
"""
import os
import threading
from datetime import datetime
from flask import Flask, request, jsonify
from PyQt5 import QtCore


class NowPlayingEmitter(QtCore.QObject):
    """跨线程传递“正在播放”字典数据"""
    received = QtCore.pyqtSignal(dict)

    def emit_np(self, payload: dict):
        # 线程安全：PyQt 信号为 QueuedConnection
        self.received.emit(payload)


def _create_app(emitter: NowPlayingEmitter):
    app = Flask(__name__)

    @app.route("/health", methods=["GET"])
    def health():
        return jsonify({"ok": True, "ts": datetime.utcnow().isoformat()})

    @app.route("/nowplaying", methods=["GET", "POST"])
    def nowplaying():
        # 统一解析 GET / POST 表单
        data = {k: (request.values.get(k) or "").strip() for k in
                ["state", "artist", "title", "album", "dur", "nextArtist", "nextTitle"]}

        # 处理封面：字段名 albumart（multipart）
        cover_path = None
        if "albumart" in request.files and request.files["albumart"]:
            f = request.files["albumart"]
            cache_dir = os.path.join("assets", "cache")
            os.makedirs(cache_dir, exist_ok=True)
            cover_path = os.path.join(cache_dir, "cover.jpg")
            f.save(cover_path)
        data["albumart_path"] = cover_path

        # 附加远端信息
        data["_remote_addr"] = request.remote_addr

        emitter.emit_np(data)
        return jsonify({"ok": True})

    return app


def start_http_server(emitter: NowPlayingEmitter, host="127.0.0.1", port=5005):
    """在后台线程启动 Flask。"""
    app = _create_app(emitter)

    th = threading.Thread(
        target=lambda: app.run(host=host, port=port, debug=False, use_reloader=False, threaded=True),
        daemon=True,
        name="HTTPServerThread",
    )
    th.start()
