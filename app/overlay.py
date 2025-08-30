# -*- coding: utf-8 -*-
"""
主界面 Overlay：标题、歌词、旋转 CD、进度/时间码开关、右键设置
"""
import os
import math
from typing import Optional, Dict
from PyQt5 import QtWidgets, QtCore, QtGui
from .lrc_parser import LRC, load_lrc_for
from .settings_dlg import SettingsDialog
from .utils import save_config, qcolor_from_hex


class Overlay(QtWidgets.QWidget):
    def __init__(self, cfg: dict, emitter, parent=None):
        super().__init__(parent)
        self.setWindowTitle("mAirList Lyrics Overlay v0.9.7")
        self.cfg = cfg
        self.emitter = emitter
        self._last_fingerprint: Optional[str] = None
        self._state = "stop"

        # UI —— 基本布局
        self.title_lbl = QtWidgets.QLabel("——")
        self.title_lbl.setAlignment(QtCore.Qt.AlignCenter)
        self.title_lbl.setStyleSheet("font-weight:600;")

        self.lyric_prev = QtWidgets.QLabel("")
        self.lyric_curr = QtWidgets.QLabel("（等待播放…）")
        self.lyric_next = QtWidgets.QLabel("")
        for lab in (self.lyric_prev, self.lyric_curr, self.lyric_next):
            lab.setAlignment(QtCore.Qt.AlignCenter)

        # 旋转 CD
        self.cd_lbl = QtWidgets.QLabel()
        self.cd_lbl.setFixedSize(220, 220)
        self.cd_angle = 0.0
        self.cd_timer = QtCore.QTimer(self)
        self.cd_timer.timeout.connect(self._rotate_cd)

        # 进度/时间码
        self.progress = QtWidgets.QProgressBar()
        self.progress.setTextVisible(False)
        self.timecode_lbl = QtWidgets.QLabel("00:00 / 00:00")
        self.time_timer = QtCore.QTimer(self)
        self.time_timer.timeout.connect(self._tick_time)

        # 布局
        lay = QtWidgets.QVBoxLayout(self)
        lay.setSpacing(8); lay.setContentsMargins(12, 12, 12, 12)
        lay.addWidget(self.title_lbl)

        cd_and_lyrics = QtWidgets.QHBoxLayout()
        cd_and_lyrics.setSpacing(12)

        self.cd_container = QtWidgets.QWidget()
        cd_lay = QtWidgets.QVBoxLayout(self.cd_container)
        cd_lay.setContentsMargins(0, 0, 0, 0); cd_lay.addWidget(self.cd_lbl, 1, QtCore.Qt.AlignCenter)
        cd_and_lyrics.addWidget(self.cd_container, 0)

        lyr_container = QtWidgets.QWidget()
        lyr_lay = QtWidgets.QVBoxLayout(lyr_container)
        lyr_lay.setContentsMargins(0, 0, 0, 0)
        lyr_lay.addWidget(self.lyric_prev)
        lyr_lay.addWidget(self.lyric_curr)
        lyr_lay.addWidget(self.lyric_next)
        cd_and_lyrics.addWidget(lyr_container, 1)

        lay.addLayout(cd_and_lyrics)
        lay.addWidget(self.progress)
        lay.addWidget(self.timecode_lbl, 0, QtCore.Qt.AlignCenter)

        # 状态
        self._albumart_path: Optional[str] = None
        self._pixmap: Optional[QtGui.QPixmap] = None
        self._duration_ms: int = 0
        self._position_ms: int = 0
        self._lrc: Optional[LRC] = None

        # 应用配置
        self.apply_settings(self.cfg, save=False)

        # 连接信号
        self.emitter.received.connect(self._on_nowplaying)

        # 右键菜单
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._open_ctx_menu)

        # 定时器
        self.cd_timer.start(33)  # ~30fps
        self.time_timer.start(200)  # 进度刷新

    # ---------- 设置相关 ----------
    def apply_settings(self, cfg: dict, save=True):
        """从 cfg 应用样式/功能开关，Apply 立即生效。"""
        self.cfg = cfg

        # 字体/颜色
        font_family = cfg["ui"].get("font_family", "Microsoft YaHei")
        font_size = int(cfg["ui"].get("font_size", 22))
        text_color = cfg["ui"].get("text_color", "#FFFFFF")
        hi_color = cfg["ui"].get("highlight_color", "#00AEEF")

        base_qss = f"color:{text_color}; font-family:'{font_family}'; font-size:{font_size}px;"
        self.title_lbl.setStyleSheet(base_qss + " font-weight:600;")
        self.lyric_prev.setStyleSheet(base_qss + " opacity:0.6;")
        self.lyric_curr.setStyleSheet(base_qss + f" color:{hi_color}; font-weight:600;")
        self.lyric_next.setStyleSheet(base_qss + " opacity:0.6;")
        self.timecode_lbl.setStyleSheet(base_qss.replace(f"{font_size}px", f"{max(12,font_size-6)}px"))

        # 功能开关
        show_cd = bool(cfg["features"].get("show_cd", True))
        show_prog = bool(cfg["features"].get("show_progress", True))
        show_tc = bool(cfg["features"].get("show_timecode", True))

        self.cd_container.setVisible(show_cd)
        self.progress.setVisible(show_prog)
        self.timecode_lbl.setVisible(show_tc)

        if save:
            save_config(cfg)

    # ---------- 右键 ----------
    def _open_ctx_menu(self, pos):
        m = QtWidgets.QMenu(self)
        act_settings = m.addAction("设置…")
        act = m.exec_(self.mapToGlobal(pos))
        if act is act_settings:
            dlg = SettingsDialog(self.cfg, parent=self)
            dlg.applied.connect(self.apply_settings)   # Apply 立即生效
            if dlg.exec_():
                pass  # OK 已在 applied 回调中保存

    # ---------- HTTP 事件 ----------
    @QtCore.pyqtSlot(dict)
    def _on_nowplaying(self, data: Dict[str, str]):
        """
        处理 /nowplaying 传入数据：
        去重：基于 (artist,title,state)；state=stop 时清屏
        """
        artist = data.get("artist", "")
        title = data.get("title", "")
        state = (data.get("state") or "play").lower()
        album = data.get("album", "")
        self._albumart_path = data.get("albumart_path")

        fingerprint = f"{artist}|{title}|{state}"
        if fingerprint == self._last_fingerprint:
            return  # 去重：相同事件不重复处理
        self._last_fingerprint = fingerprint

        if state == "stop":
            self._state = "stop"
            self.title_lbl.setText("——")
            self.lyric_prev.setText("")
            self.lyric_curr.setText("（已停止）")
            self.lyric_next.setText("")
            self._lrc = None
            self._position_ms = 0
            self._duration_ms = 0
            self._pixmap = None
            self.cd_lbl.clear()
            return

        self._state = "play"
        self.title_lbl.setText(f"{artist} - {title}" if artist and title else (title or artist or "——"))

        # 封面
        self._load_cover(self._albumart_path)

        # 时长
        try:
            self._duration_ms = int(data.get("dur") or 0)
        except Exception:
            self._duration_ms = 0
        self._position_ms = 0  # 新曲从 0 计

        # 歌词
        self._lrc = load_lrc_for(artist=artist, title=title)
        self._refresh_lyric()

    # ---------- 显示 ----------
    def _rotate_cd(self):
        if not self.cd_container.isVisible():
            return
        self.cd_angle = (self.cd_angle + 0.9) % 360.0
        if self._pixmap is None:
            self._draw_cd_placeholder()
            return
        # 旋转
        pm = self._pixmap
        side = min(self.cd_lbl.width(), self.cd_lbl.height())
        pm = pm.scaled(side, side, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)

        transform = QtGui.QTransform()
        transform.translate(pm.width()/2, pm.height()/2)
        transform.rotate(self.cd_angle)
        transform.translate(-pm.width()/2, -pm.height()/2)
        rotated = pm.transformed(transform, QtCore.Qt.SmoothTransformation)
        self.cd_lbl.setPixmap(rotated)

    def _draw_cd_placeholder(self):
        side = min(self.cd_lbl.width(), self.cd_lbl.height())
        img = QtGui.QImage(side, side, QtGui.QImage.Format_ARGB32)
        img.fill(QtCore.Qt.transparent)
        p = QtGui.QPainter(img)
        p.setRenderHint(QtGui.QPainter.Antialiasing, True)
        c1 = qcolor_from_hex(self.cfg["ui"].get("highlight_color", "#00AEEF"))
        c2 = qcolor_from_hex(self.cfg["ui"].get("text_color", "#FFFFFF"))
        pen = QtGui.QPen(c2); pen.setWidth(3)
        p.setPen(pen)
        p.setBrush(c1)
        p.drawEllipse(3, 3, side-6, side-6)
        p.setBrush(QtGui.QBrush(QtCore.Qt.black))
        p.drawEllipse(side*0.4, side*0.4, side*0.2, side*0.2)
        p.end()
        self.cd_lbl.setPixmap(QtGui.QPixmap.fromImage(img))

    def _load_cover(self, path: Optional[str]):
        self._pixmap = None
        if path and os.path.exists(path):
            pm = QtGui.QPixmap(path)
            if not pm.isNull():
                self._pixmap = pm
                return
        # 尝试默认
        default = os.path.join("assets", "cd_default.png")
        if os.path.exists(default):
            pm = QtGui.QPixmap(default)
            if not pm.isNull():
                self._pixmap = pm

    def _tick_time(self):
        if self._state != "play":
            return
        self._position_ms += 200
        # 时间码
        if self.timecode_lbl.isVisible():
            def fmt(ms: int):
                s = max(0, ms // 1000); return f"{s//60:02d}:{s%60:02d}"
            self.timecode_lbl.setText(f"{fmt(self._position_ms)} / {fmt(self._duration_ms)}")
        # 进度
        if self.progress.isVisible():
            total = max(1, self._duration_ms)
            val = int(min(100, self._position_ms * 100 / total))
            self.progress.setValue(val)
        # 歌词滚动
        self._refresh_lyric()

    def _refresh_lyric(self):
        """根据 _position_ms 在 LRC 中定位三行（上一/当前/下一）。"""
        if not self._lrc or not self._lrc.lines:
            self.lyric_prev.setText("")
            self.lyric_curr.setText("（未找到歌词）")
            self.lyric_next.setText("")
            return

        idx = self._lrc.index_at(self._position_ms)
        prev_txt = self._lrc.lines[idx-1][1] if idx-1 >= 0 else ""
        curr_txt = self._lrc.lines[idx][1] if idx >= 0 else ""
        next_txt = self._lrc.lines[idx+1][1] if idx+1 < len(self._lrc.lines) else ""

        # 去重：防止“同一句绘制两次（白+蓝）”——我们只绘当前行一次
        self.lyric_prev.setText(prev_txt)
        self.lyric_curr.setText(curr_txt)  # 仅这行用高亮色
        self.lyric_next.setText(next_txt)
