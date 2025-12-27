# MP4 Lossless Splitter

A lightweight desktop application for fast, lossless MP4 video splitting without re-encoding.

## Screenshot
![Screenshot](res/screenshot.png?v=2)

## Features

- **Lossless Video Splitting** - Uses FFmpeg's stream copy (`-c copy`) for instant processing
- **Multiple Cut Methods**
  - Manual cut points while playing video
  - Quick cut first/last X seconds
  - Auto-split by duration
- **Mark Segments** - Mark segments as Keep or Discard with visual indicators
- **Real-time Status Display** - See cut point and segment status instantly without popups
- **Project Saving** - Save and load projects to continue work later
- **Integrated Video Player** - Play, pause, seek, and adjust volume
- **Batch Processing** - Split multiple segments in one operation

## Requirements

### System Dependencies
- **FFmpeg** - Required for video processing
  - Windows: Download from [ffmpeg.org](https://ffmpeg.org/download.html)

## Installation

### 1. Create and activate a virtual environment
```bash
python -m venv .venv
.\.venv\Scripts\activate
```

### **2. Install dependencies**

```bash
python.exe -m pip install --upgrade pip
pip install PyQt6
```

### **3. Run the application**

```bash
python src/main.py
```

### **4. Package the application (optional)**

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --icon=res/icon.ico src/main.py
```

---

### Workflow

1. **Open Video** - Click "🔓 Open MP4 File" to load a video
2. **Add Cut Points** - Play video and click "✂ Add Cut Point" to mark segments
3. **Mark Segments** - Click "✗ Mark as Discard" to toggle the last cut point between Keep/Discard
4. **Generate Segments** - Click "🔊 Generate Segments" to create segment list
5. **Adjust Status** - Click segments and use "✓ Mark as Keep" or "✗ Mark as Discard" buttons
6. **Split** - Click "🚀 Start Splitting" and choose output directory
7. **Save Project** - Use "💾 Save Project" to save your cuts for later

### Output Files

Output files are named: `{original_name}_segment_1.mp4`, `{original_name}_segment_2.mp4`, etc.

Discarded segments append `_discard` suffix: `{original_name}_segment_2_discard.mp4`

## Project File Format

Projects are saved as `.mp4proj` (JSON) containing:
- Video file path
- All cut points with timestamps
- Keep/Discard status for each cut point

## License

MIT License