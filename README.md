# mAirList Lyrics Overlay (v0.9.7)

好的——下面是**英文描述**，你可以直接放到 GitHub 项目简介或 README 开头用：

---

**mAirList Lyrics Overlay** is a lightweight desktop overlay built with **Python + PyQt5** that shows synchronized **LRC lyrics**, **rotating album art**, and **playback status** for tracks currently playing in **mAirList**.
The app listens for low-latency **HTTP GET/POST** callbacks from mAirList (via Logging or background scripts) and updates the on-screen display instantly—no UDP required. It includes a simple settings dialog for fonts, colors, and feature toggles, and a small built-in HTTP server for easy plug-and-play integration.

**Key features**

* Real-time now-playing updates from mAirList via HTTP (GET/POST, form-data, multipart).
* LRC parsing with previous/current/next line rendering and de-duplication to prevent double drawing.
* Rotating album art (with sensible placeholder when artwork is missing).
* Optional progress bar and timecode display (toggle on/off).
* Immediate “Apply” in the settings dialog—changes take effect without restart.
* Minimal dependencies and clear project structure for customization.

**Quick start**

1. Run the app: `python main.py` (see `requirements.txt` for dependencies).
2. In mAirList, add a Logging rule or background script that posts now-playing data to
   `http://127.0.0.1:5005/nowplaying` (artist, title, duration; optional album art as multipart).
3. Place your `.lrc` files in the `lyrics/` folder using `Artist - Title.lrc` or `Title - Artist.lrc` naming.

**Why this project?**
It focuses on **reliability, low latency, and a clean overlay**, making it a practical starting point for radio workflows that need KTV-style lyrics and basic visuals without heavyweight dependencies.


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
