# mAirList Lyrics Overlay (v0.9.7)

基于 **Python + PyQt5** 的歌词显示/旋转 CD 封面叠加器，支持从 **mAirList** 获取“正在播放”信息并同步显示歌词。  
⚠️ 本项目默认 **仅 HTTP**（已移除 UDP JSON）。

## 功能
- 接收 mAirList 的 **HTTP GET/POST**（支持 multipart 封面）到 `http://127.0.0.1:5005/nowplaying`
- 去重与状态机：避免重复刷新与残留
- LRC 歌词解析与同步显示（支持多行）
- 旋转 CD 封面（无封面时显示占位）
- 进度条 / 时间码 开关
- 设置面板（右键 → 设置），**Apply 即刻生效**

## 快速开始
```bash
git clone https://github.com/<you>/mairlist-lyrics-overlay.git
cd mairlist-lyrics-overlay
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\python main.py
