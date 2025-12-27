"""
MP4 Quick Splitter - Desktop Application
A local application for fast video splitting without re-encoding

Requirements:
pip install PyQt6 opencv-python-headless ffmpeg-python

Also requires FFmpeg installed on your system:
- Windows: Download from https://ffmpeg.org/download.html or use: choco install ffmpeg
- Mac: brew install ffmpeg
- Linux: sudo apt-get install ffmpeg
"""

import sys
import os
import json
import subprocess
from pathlib import Path
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QSlider, QFileDialog, QListWidget, QListWidgetItem,
    QInputDialog, QMessageBox, QSpinBox, QProgressDialog
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt6.QtGui import QColor, QFont, QIcon
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtCore import QUrl, QTime


class VideoWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(bool, str)

    def __init__(self, ffmpeg_commands):
        super().__init__()
        self.ffmpeg_commands = ffmpeg_commands
        self.is_running = True

    def run(self):
        try:
            for i, cmd in enumerate(self.ffmpeg_commands):
                if not self.is_running:
                    break
                subprocess.run(cmd, shell=True, check=True,
                             stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL)
                self.progress.emit(int((i + 1) / len(self.ffmpeg_commands) * 100))
            self.finished.emit(True, "All segments split successfully!")
        except Exception as e:
            self.finished.emit(False, f"Error: {str(e)}")

    def stop(self):
        self.is_running = False


class VideoSplitterApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MP4 Quick Splitter")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet(self.get_dark_stylesheet())

        self.video_file = None
        self.video_filename = None
        self.duration = 0
        self.cuts = []
        self.segments = []
        self.worker = None

        self.init_ui()

    def get_dark_stylesheet(self):
        return """
            QMainWindow, QWidget {
                background-color: #1e293b;
                color: #e2e8f0;
            }
            QPushButton {
                background-color: #0891b2;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #06b6d4;
            }
            QPushButton:pressed {
                background-color: #0e7490;
            }
            QPushButton:disabled {
                background-color: #64748b;
            }
            QSlider::groove:horizontal {
                background: #334155;
                height: 8px;
                margin: 2px 0;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #0891b2;
                width: 14px;
                margin: -3px 0;
                border-radius: 7px;
            }
            QListWidget {
                background-color: #0f172a;
                border: 1px solid #334155;
                border-radius: 6px;
            }
            QListWidget::item:selected {
                background-color: #0891b2;
            }
            QLabel {
                color: #cbd5e1;
            }
            QInputDialog {
                background-color: #1e293b;
            }
        """

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout()

        # Left panel - Video player
        left_panel = QVBoxLayout()

        # File selection
        file_btn = QPushButton("🔓 Open MP4 File")
        file_btn.clicked.connect(self.open_file)
        left_panel.addWidget(file_btn)

        # Video widget
        self.video_widget = QVideoWidget()
        self.video_widget.setStyleSheet("background-color: #000;")
        left_panel.addWidget(self.video_widget, 1)

        # Media player
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        self.player.setVideoOutput(self.video_widget)

        # Timeline
        self.timeline = QSlider(Qt.Orientation.Horizontal)
        self.timeline.setSliderPosition(0)
        self.timeline.sliderMoved.connect(self.seek_video)
        left_panel.addWidget(self.timeline)

        # Time display
        time_layout = QHBoxLayout()
        self.time_label = QLabel("00:00 / 00:00")
        self.time_label.setFont(QFont("Arial", 10))
        time_layout.addWidget(self.time_label)
        left_panel.addLayout(time_layout)

        # Volume control
        volume_layout = QHBoxLayout()
        volume_label = QLabel("🔊 Volume:")
        volume_layout.addWidget(volume_label)
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setMinimum(0)
        self.volume_slider.setMaximum(100)
        self.volume_slider.setValue(80)
        self.volume_slider.setMaximumWidth(150)
        self.volume_slider.valueChanged.connect(self.set_volume)
        volume_layout.addWidget(self.volume_slider)
        left_panel.addLayout(volume_layout)

        # Controls
        controls = QHBoxLayout()
        self.play_btn = QPushButton("▶ Play")
        self.play_btn.clicked.connect(self.play_video)
        controls.addWidget(self.play_btn)

        self.pause_btn = QPushButton("⸸ Pause")
        self.pause_btn.clicked.connect(self.pause_video)
        controls.addWidget(self.pause_btn)

        self.cut_btn = QPushButton("✂ Add Cut Point")
        self.cut_btn.clicked.connect(self.add_cut)
        self.cut_btn.setStyleSheet("""
            QPushButton {
                background-color: #ea580c;
            }
            QPushButton:hover {
                background-color: #fb923c;
            }
        """)
        controls.addWidget(self.cut_btn)

        left_panel.addLayout(controls)

        # Right panel - Cuts and segments
        right_panel = QVBoxLayout()

        # Quick cut options
        quick_cuts_label = QLabel("Quick Cut Options:")
        quick_cuts_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        right_panel.addWidget(quick_cuts_label)

        quick_cuts_layout = QVBoxLayout()

        # Cut first X seconds
        first_sec_layout = QHBoxLayout()
        first_sec_layout.addWidget(QLabel("First"))
        self.first_sec_spin = QSpinBox()
        self.first_sec_spin.setMinimum(0)
        self.first_sec_spin.setMaximum(3600)
        self.first_sec_spin.setValue(0)
        first_sec_layout.addWidget(self.first_sec_spin)
        first_sec_layout.addWidget(QLabel("seconds"))
        first_btn = QPushButton("✂ Cut First")
        first_btn.clicked.connect(self.cut_first_seconds)
        first_sec_layout.addWidget(first_btn)
        quick_cuts_layout.addLayout(first_sec_layout)

        # Cut last X seconds
        last_sec_layout = QHBoxLayout()
        last_sec_layout.addWidget(QLabel("Last"))
        self.last_sec_spin = QSpinBox()
        self.last_sec_spin.setMinimum(0)
        self.last_sec_spin.setMaximum(3600)
        self.last_sec_spin.setValue(0)
        last_sec_layout.addWidget(self.last_sec_spin)
        last_sec_layout.addWidget(QLabel("seconds"))
        last_btn = QPushButton("✂ Cut Last")
        last_btn.clicked.connect(self.cut_last_seconds)
        last_sec_layout.addWidget(last_btn)
        quick_cuts_layout.addLayout(last_sec_layout)

        # Split by duration
        duration_layout = QHBoxLayout()
        duration_layout.addWidget(QLabel("Split every"))
        self.split_duration_spin = QSpinBox()
        self.split_duration_spin.setMinimum(1)
        self.split_duration_spin.setMaximum(3600)
        self.split_duration_spin.setValue(60)
        duration_layout.addWidget(self.split_duration_spin)
        duration_layout.addWidget(QLabel("seconds"))
        split_btn = QPushButton("🔊 Split by Duration")
        split_btn.clicked.connect(self.split_by_duration)
        duration_layout.addWidget(split_btn)
        quick_cuts_layout.addLayout(duration_layout)

        right_panel.addLayout(quick_cuts_layout)

        # Separator
        separator = QLabel("━" * 50)
        separator.setStyleSheet("color: #475569;")
        right_panel.addWidget(separator)

        # Cuts section
        cuts_label = QLabel("Cut Points:")
        cuts_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        right_panel.addWidget(cuts_label)

        self.cuts_list = QListWidget()
        self.cuts_list.itemDoubleClicked.connect(self.remove_cut)
        right_panel.addWidget(self.cuts_list, 1)

        remove_cut_btn = QPushButton("🗑 Remove Selected Cut")
        remove_cut_btn.clicked.connect(self.remove_selected_cut)
        right_panel.addWidget(remove_cut_btn)

        # Generate segments
        generate_btn = QPushButton("🔊 Generate Segments")
        generate_btn.clicked.connect(self.generate_segments)
        generate_btn.setStyleSheet("""
            QPushButton {
                background-color: #0ea5e9;
            }
            QPushButton:hover {
                background-color: #38bdf8;
            }
        """)
        right_panel.addWidget(generate_btn)

        # Segments section
        segments_label = QLabel("Output Segments:")
        segments_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        right_panel.addWidget(segments_label)

        self.segments_list = QListWidget()
        self.segments_list.itemClicked.connect(self.on_segment_clicked)
        self.segments_list.itemDoubleClicked.connect(self.edit_segment_name)
        right_panel.addWidget(self.segments_list, 1)

        # Segment control buttons
        segment_controls = QHBoxLayout()
        self.keep_btn = QPushButton("✓ Mark as Keep")
        self.keep_btn.clicked.connect(self.mark_segment_keep)
        self.keep_btn.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
            }
            QPushButton:hover {
                background-color: #34d399;
            }
        """)
        self.keep_btn.setEnabled(False)
        segment_controls.addWidget(self.keep_btn)

        self.discard_btn = QPushButton("✗ Mark as Discard")
        self.discard_btn.clicked.connect(self.mark_segment_discard)
        self.discard_btn.setStyleSheet("""
            QPushButton {
                background-color: #ef4444;
            }
            QPushButton:hover {
                background-color: #f87171;
            }
        """)
        self.discard_btn.setEnabled(False)
        segment_controls.addWidget(self.discard_btn)

        right_panel.addLayout(segment_controls)

        # Split button
        self.split_btn = QPushButton("🚀 Start Splitting")
        self.split_btn.clicked.connect(self.start_splitting)
        self.split_btn.setStyleSheet("""
            QPushButton {
                background-color: #8b5cf6;
            }
            QPushButton:hover {
                background-color: #a78bfa;
            }
        """)
        self.split_btn.setEnabled(False)
        right_panel.addWidget(self.split_btn)

        # Add panels to main layout
        main_layout.addLayout(left_panel, 2)
        main_layout.addLayout(right_panel, 1)

        central_widget.setLayout(main_layout)

        # Player signals
        self.player.positionChanged.connect(self.update_timeline)
        self.player.durationChanged.connect(self.update_duration)
        self.player.playbackStateChanged.connect(self.update_play_button)

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open MP4 Video", "",
            "Video Files (*.mp4);;All Files (*)"
        )

        if file_path:
            self.video_file = file_path
            self.video_filename = Path(file_path).stem
            self.player.setSource(QUrl.fromLocalFile(file_path))
            self.cuts = []
            self.segments = []
            self.cuts_list.clear()
            self.segments_list.clear()
            self.setWindowTitle(f"MP4 Quick Splitter - {Path(file_path).name}")
            self.setEnabled(True)
            self.split_btn.setEnabled(False)

    def play_video(self):
        self.player.play()

    def pause_video(self):
        self.player.pause()

    def set_volume(self, value):
        self.audio_output.setVolume(value / 100.0)

    def seek_video(self, position):
        self.player.setPosition(position)

    def update_timeline(self, position):
        self.timeline.blockSignals(True)
        self.timeline.setValue(position)
        self.timeline.blockSignals(False)
        self.update_time_label()

    def update_duration(self, duration):
        self.duration = duration
        self.timeline.setMaximum(duration)
        self.update_time_label()

    def update_time_label(self):
        current = self.player.position() / 1000
        total = self.duration / 1000
        current_str = self.format_time(current)
        total_str = self.format_time(total)
        self.time_label.setText(f"{current_str} / {total_str}")

    def format_time(self, seconds):
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        ms = int((seconds % 1) * 100)
        return f"{mins:02d}:{secs:02d}.{ms:02d}"

    def update_play_button(self):
        if self.player.isPlaying():
            self.play_btn.setText("▶ Playing")
            self.play_btn.setEnabled(False)
            self.pause_btn.setEnabled(True)
        else:
            self.play_btn.setText("▶ Play")
            self.play_btn.setEnabled(True)
            self.pause_btn.setEnabled(False)

    def add_cut(self):
        current = self.player.position() / 1000
        if current not in self.cuts:
            self.cuts.append(current)
            self.cuts.sort()
            self.refresh_cuts_list()

    def refresh_cuts_list(self):
        self.cuts_list.clear()
        for cut in self.cuts:
            self.cuts_list.addItem(self.format_time(cut))

    def remove_selected_cut(self):
        row = self.cuts_list.currentRow()
        if row >= 0:
            self.cuts.pop(row)
            self.refresh_cuts_list()

    def remove_cut(self, item):
        self.remove_selected_cut()

    def cut_first_seconds(self):
        """Skip the first X seconds of the video"""
        seconds = self.first_sec_spin.value()
        if seconds > 0 and seconds < self.duration / 1000:
            if seconds not in self.cuts:
                self.cuts.append(seconds)
                self.cuts.sort()
                self.refresh_cuts_list()
                QMessageBox.information(self, "Success", 
                    f"Cut point added at {self.format_time(seconds)}.\nFirst {seconds}s will be removed.")
        else:
            QMessageBox.warning(self, "Invalid", "Please enter a valid duration.")

    def cut_last_seconds(self):
        """Remove the last X seconds of the video"""
        seconds = self.last_sec_spin.value()
        total_duration = self.duration / 1000
        if seconds > 0 and seconds < total_duration:
            cut_point = total_duration - seconds
            if cut_point not in self.cuts:
                self.cuts.append(cut_point)
                self.cuts.sort()
                self.refresh_cuts_list()
                QMessageBox.information(self, "Success", 
                    f"Cut point added at {self.format_time(cut_point)}.\nLast {seconds}s will be removed.")
        else:
            QMessageBox.warning(self, "Invalid", "Please enter a valid duration.")

    def split_by_duration(self):
        """Split video into equal duration segments"""
        segment_duration = self.split_duration_spin.value()
        total_duration = self.duration / 1000
        
        if segment_duration <= 0 or segment_duration >= total_duration:
            QMessageBox.warning(self, "Invalid", "Please enter a valid segment duration.")
            return
        
        self.cuts = []
        current_time = segment_duration
        
        while current_time < total_duration:
            self.cuts.append(current_time)
            current_time += segment_duration
        
        self.refresh_cuts_list()
        num_segments = len(self.cuts) + 1
        QMessageBox.information(self, "Success", 
            f"Video will be split into {num_segments} segments of ~{segment_duration}s each.")

    def generate_segments(self):
        if not self.cuts:
            QMessageBox.warning(self, "No Cuts", "Please add at least one cut point.")
            return

        sorted_cuts = [0] + self.cuts + [self.duration / 1000]
        self.segments = []

        for i in range(len(sorted_cuts) - 1):
            self.segments.append({
                "id": i,
                "start": sorted_cuts[i],
                "end": sorted_cuts[i + 1],
                "name": f"segment_{i + 1}",
                "status": "keep"
            })

        self.refresh_segments_list()
        self.split_btn.setEnabled(True)

    def refresh_segments_list(self):
        self.segments_list.clear()
        for seg in self.segments:
            start = self.format_time(seg["start"])
            end = self.format_time(seg["end"])
            duration = self.format_time(seg["end"] - seg["start"])
            status_icon = "✓" if seg["status"] == "keep" else "✗"
            status_text = "KEEP" if seg["status"] == "keep" else "DISCARD"
            item_text = f"{status_icon} {seg['name']} [{status_text}]\n{start} → {end} ({duration})"
            self.segments_list.addItem(item_text)

    def on_segment_clicked(self, item):
        self.keep_btn.setEnabled(True)
        self.discard_btn.setEnabled(True)

    def mark_segment_keep(self):
        row = self.segments_list.currentRow()
        if row >= 0:
            self.segments[row]["status"] = "keep"
            self.refresh_segments_list()
            self.segments_list.setCurrentRow(row)

    def mark_segment_discard(self):
        row = self.segments_list.currentRow()
        if row >= 0:
            self.segments[row]["status"] = "discard"
            self.refresh_segments_list()
            self.segments_list.setCurrentRow(row)

    def edit_segment_name(self, item):
        row = self.segments_list.row(item)
        new_name, ok = QInputDialog.getText(
            self, "Edit Segment Name",
            "Enter new name:",
            text=self.segments[row]["name"]
        )
        if ok and new_name:
            self.segments[row]["name"] = new_name
            self.refresh_segments_list()

    def start_splitting(self):
        if not self.video_file or not self.segments:
            QMessageBox.warning(self, "Error", "No segments to split.")
            return

        output_dir = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if not output_dir:
            return

        ffmpeg_commands = []
        for seg in self.segments:
            # Build filename: original_name_segment_x or original_name_segment_x_discard
            suffix = ""
            if seg["status"] == "discard":
                suffix = "_discard"
            
            output_filename = f"{self.video_filename}_{seg['name']}{suffix}.mp4"
            output_path = os.path.join(output_dir, output_filename)
            
            cmd = (
                f'ffmpeg -i "{self.video_file}" '
                f'-ss {seg["start"]} -to {seg["end"]} '
                f'-c copy "{output_path}"'
            )
            ffmpeg_commands.append(cmd)

        # Progress dialog
        self.progress = QProgressDialog("Splitting video...", "Cancel", 0, 100, self)
        self.progress.setWindowModality(Qt.WindowModality.WindowModal)

        self.worker = VideoWorker(ffmpeg_commands)
        self.worker.progress.connect(self.progress.setValue)
        self.worker.finished.connect(self.on_split_finished)
        self.worker.start()

    def on_split_finished(self, success, message):
        self.progress.close()
        if success:
            QMessageBox.information(self, "Success", message)
        else:
            QMessageBox.critical(self, "Error", message)


def main():
    app = QApplication(sys.argv)
    window = VideoSplitterApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()