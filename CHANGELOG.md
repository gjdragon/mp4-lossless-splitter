# Changelog

All notable changes to MP4 Lossless Splitter are documented in this file.

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
- Supports Windows, macOS, and Linux
