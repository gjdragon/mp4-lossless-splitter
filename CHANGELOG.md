# Changelog

All notable changes to MP4 Lossless Splitter are documented in this file.

---

## [0.5.0] - 2025-12-27

### Added
- **Keep/Dicard** - Display keep and discard info on the fly before generating segments.

---

## [0.4.0] - 2025-12-27

### Added
- **Combined Play/Pause Button** - Single toggle button for play/pause control
- **Keep/Discard Toggle for Cut Points** - Mark cut points as Keep or Discard during playback without generating segments

---

## [0.3.0] - 2025-12-27

### Added
- **Keep/Discard Marking for Segments** - Mark output segments as Keep or Discard before splitting
- **Visual Status Indicators** - Segments display with status icon and label (✓ KEEP or ✗ DISCARD)
- **Filename Suffix for Discarded Segments** - Discarded segments automatically append `_discard` to filename
- **Mark Keep/Discard Buttons** - Green and red buttons to toggle segment status
---

## [0.2.0] - 2025-12-27

### Added
- **Quick Cut Options**
  - Cut first X seconds
  - Cut last X seconds
  - Split by duration

---

## [0.1.0] - 2025-12-27

### Added
- **Core Features**
  - Lossless MP4 video splitting using FFmpeg stream copy
  - Integrated video player with play/pause and seek controls
  - Real-time timeline slider
  - Volume control
  - Time display (current / total duration)
  
- **Cut Point Management**
  - Add cut points during playback
  - View list of all cut points with timestamps
  - Remove individual cut points
  
- **Segment Generation**
  - Automatically generate segments from cut points
  - View segment list with start time, end time, and duration
  
- **Batch Splitting**
  - Split all segments in one operation
  - Multi-threaded processing with progress dialog
  - Output files in MP4 format with lossless quality

- **User Interface**
  - Dark theme stylesheet for comfortable viewing
  - Responsive layout with video player on left, controls on right
  - Color-coded buttons for different actions
  - File selection dialog

### Technical Details
- Built with PyQt6 for cross-platform compatibility
- Uses FFmpeg for reliable video processing
- Multi-threaded video worker for non-blocking UI
