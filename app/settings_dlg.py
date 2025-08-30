# -*- coding: utf-8 -*-
"""
设置对话框：Apply 立即生效，OK 同步保存，Cancel 放弃
"""
from PyQt5 import QtWidgets, QtCore


def _add_row(form: QtWidgets.QFormLayout, name: str, w: QtWidgets.QWidget):
    lab = QtWidgets.QLabel(name)
    form.addRow(lab, w)


class SettingsDialog(QtWidgets.QDialog):
    applied = QtCore.pyqtSignal(dict)  # 发出新的 cfg

    def __init__(self, cfg: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle("设置")
        self._cfg = {**cfg}  # 浅拷贝防止 Cancel 改原值

        lay = QtWidgets.QVBoxLayout(self)

        form = QtWidgets.QFormLayout()
        form.setLabelAlignment(QtCore.Qt.AlignRight)

        # 字体与颜色
        self.font_family = QtWidgets.QLineEdit(self._cfg["ui"].get("font_family", "Microsoft YaHei"))
        self.font_size = QtWidgets.QSpinBox(); self.font_size.setRange(8, 96)
        self.font_size.setValue(int(self._cfg["ui"].get("font_size", 22)))
        self.text_color = QtWidgets.QLineEdit(self._cfg["ui"].get("text_color", "#FFFFFF"))
        self.hi_color = QtWidgets.QLineEdit(self._cfg["ui"].get("highlight_color", "#00AEEF"))

        _add_row(form, "字体", self.font_family)
        _add_row(form, "字号", self.font_size)
        _add_row(form, "文字颜色", self.text_color)
        _add_row(form, "高亮颜色", self.hi_color)

        # 功能开关
        self.show_cd = QtWidgets.QCheckBox("显示 CD")
        self.show_cd.setChecked(bool(self._cfg["features"].get("show_cd", True)))
        self.show_prog = QtWidgets.QCheckBox("显示进度条")
        self.show_prog.setChecked(bool(self._cfg["features"].get("show_progress", True)))
        self.show_tc = QtWidgets.QCheckBox("显示时间码")
        self.show_tc.setChecked(bool(self._cfg["features"].get("show_timecode", True)))

        form.addRow(self.show_cd)
        form.addRow(self.show_prog)
        form.addRow(self.show_tc)

        lay.addLayout(form)

        btns = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Apply | QtWidgets.QDialogButtonBox.Cancel
        )
        btns.accepted.connect(self._on_ok)
        btns.button(QtWidgets.QDialogButtonBox.Apply).clicked.connect(self._on_apply)
        btns.rejected.connect(self.reject)

        lay.addWidget(btns)

    def _collect(self) -> dict:
        cfg = {**self._cfg}
        cfg["ui"]["font_family"] = self.font_family.text().strip() or "Microsoft YaHei"
        cfg["ui"]["font_size"] = int(self.font_size.value())
        cfg["ui"]["text_color"] = self.text_color.text().strip() or "#FFFFFF"
        cfg["ui"]["highlight_color"] = self.hi_color.text().strip() or "#00AEEF"
        cfg["features"]["show_cd"] = bool(self.show_cd.isChecked())
        cfg["features"]["show_progress"] = bool(self.show_prog.isChecked())
        cfg["features"]["show_timecode"] = bool(self.show_tc.isChecked())
        return cfg

    def _on_apply(self):
        cfg = self._collect()
        self._cfg = cfg
        self.applied.emit(cfg)  # 立即生效（由 Overlay.apply_settings 处理）

    def _on_ok(self):
        self._on_apply()
        self.accept()
