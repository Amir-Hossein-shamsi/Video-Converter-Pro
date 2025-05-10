import os
import sys
import subprocess
import re

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QSpinBox, QCheckBox,
    QTextEdit, QFileDialog, QMessageBox, QProgressBar, QGroupBox,
    QStatusBar, QMenuBar, QMenu, QComboBox, QSizePolicy
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QIcon

FFMPEG_PATH = r"C:\ffmpeg\bin\ffmpeg.exe"
FFPROBE_PATH = r"C:\ffmpeg\bin\ffprobe.exe"

class ConversionWorker(QThread):
    log_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(bool, str)
    progress_signal = pyqtSignal(int)

    def __init__(self, input_file, output_dir, preset, target_size_mb, use_gpu):
        super().__init__()
        self.input_file = input_file
        self.output_dir = output_dir
        self.preset = preset
        self.target_size_mb = target_size_mb
        self.use_gpu = use_gpu
        self.process = None
        self.duration = 0.0
        self.running = True

    @staticmethod
    def probe_duration(path):
        try:
            proc = subprocess.run([
                FFPROBE_PATH, '-v', 'error', '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1', path
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            return float(proc.stdout.strip())
        except:
            return 0.0

    def run(self):
        try:
            self.log_signal.emit("[INFO] Initializing conversion...")
            os.makedirs(self.output_dir, exist_ok=True)

            self.duration = self.probe_duration(self.input_file)
            if not self.duration:
                raise RuntimeError("Could not read video duration.")

            target_bytes = self.target_size_mb * 1024 * 1024
            total_bits = target_bytes * 8
            total_bitrate_bps = total_bits / self.duration
            audio_bitrate_kbps = 128
            video_bitrate_kbps = max((total_bitrate_bps / 1000) - audio_bitrate_kbps, 100)

            base = os.path.splitext(os.path.basename(self.input_file))[0]
            output_file = os.path.join(self.output_dir, f"{base}_{self.preset}.mp4")

            cmd = [FFMPEG_PATH, '-i', self.input_file]
            if self.use_gpu:
                cmd += ['-c:v', 'h264_nvenc', '-preset', self.preset]
            else:
                cmd += ['-c:v', 'libx264', '-preset', self.preset, '-threads', '4']
            cmd += ['-b:v', f"{int(video_bitrate_kbps)}k"]
            cmd += ['-c:a', 'aac', '-b:a', f"{audio_bitrate_kbps}k", output_file, '-y']

            self.log_signal.emit(f"[CMD] {' '.join(cmd)}")
            env = os.environ.copy(); env['LANG'] = 'C'
            self.process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=env
            )

            while self.running and self.process.poll() is None:
                line = self.process.stdout.readline()
                if line:
                    self.log_signal.emit(line.strip())
                    self._update_progress(line)

            if self.process.returncode != 0:
                raise subprocess.CalledProcessError(self.process.returncode, cmd)

            self.finished_signal.emit(True, output_file)
        except Exception as e:
            self.log_signal.emit(f"[ERROR] {e}")
            self.finished_signal.emit(False, str(e))
        finally:
            if self.process and self.process.poll() is None:
                self.process.terminate()

    def _update_progress(self, text):
        m = re.search(r'time=(\d+):(\d+):(\d+\.\d+)', text)
        if m and self.duration:
            h, m_, s = m.groups()
            elapsed = int(h)*3600 + int(m_)*60 + float(s)
            percent = int((elapsed / self.duration) * 100)
            self.progress_signal.emit(percent)

    def stop(self):
        self.running = False
        if self.process and self.process.poll() is None:
            self.process.terminate()

class VideoConverterGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.worker = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Video Converter Pro')
        self.setMinimumSize(800, 650)
        self.setWindowIcon(QIcon.fromTheme('video-x-generic'))

        menubar = self.menuBar()
        file_menu = menubar.addMenu('File')
        file_menu.addAction('Open Video', self.browse_video)
        file_menu.addSeparator()
        file_menu.addAction('Exit', self.close)

        central = QWidget(); layout = QVBoxLayout()

        self.drop_label = QLabel('Drag & Drop video file here')
        self.drop_label.setFixedHeight(100)
        self.drop_label.setStyleSheet('QLabel { border: 2px dashed #888; }')
        self.drop_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.drop_label.setAcceptDrops(True)
        layout.addWidget(self.drop_label)

        io_group = QGroupBox('Input / Output')
        io_layout = QHBoxLayout()
        self.input_le = QLineEdit(placeholderText='Input video...')
        io_layout.addWidget(self.input_le)
        io_layout.addWidget(QPushButton('Browse', clicked=self.browse_video))
        self.output_le = QLineEdit(placeholderText='Output folder...')
        io_layout.addWidget(self.output_le)
        io_layout.addWidget(QPushButton('Browse', clicked=self.browse_output))
        io_group.setLayout(io_layout)
        layout.addWidget(io_group)

        st_group = QGroupBox('Conversion Settings')
        st_layout = QHBoxLayout()
        st_layout.addWidget(QLabel('Preset:'))
        self.preset_cb = QComboBox(); self.preset_cb.addItems(['ultrafast','fast','medium','slow','veryslow'])
        st_layout.addWidget(self.preset_cb)
        st_layout.addWidget(QLabel('Target Size (MB):'))
        self.size_sb = QSpinBox(); self.size_sb.setRange(1,20000); self.size_sb.setValue(600)
        self.size_sb.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        st_layout.addWidget(self.size_sb)
        self.gpu_cb = QCheckBox('Use GPU')
        st_layout.addWidget(self.gpu_cb)
        st_group.setLayout(st_layout)
        layout.addWidget(st_group)

        pr_group = QGroupBox('Progress & Log')
        pr_layout = QVBoxLayout()
        self.progress_bar = QProgressBar(alignment=Qt.AlignmentFlag.AlignCenter)
        self.log_te = QTextEdit(readOnly=True); self.log_te.setFont(QFont('Courier',9))
        pr_layout.addWidget(self.progress_bar); pr_layout.addWidget(self.log_te)
        pr_group.setLayout(pr_layout); layout.addWidget(pr_group)

        ctrl = QHBoxLayout()
        ctrl.addWidget(QPushButton('Start', clicked=self.start_conversion))
        self.cancel_btn = QPushButton('Cancel', clicked=self.cancel_conversion)
        self.cancel_btn.setEnabled(False)
        ctrl.addWidget(self.cancel_btn)
        layout.addLayout(ctrl)

        central.setLayout(layout)
        self.setCentralWidget(central)
        self.statusBar().showMessage('Ready')

    def browse_video(self):
        fn, _ = QFileDialog.getOpenFileName(self, 'Select Video', '', 'Video Files (*.mp4 *.mov *.avi)')
        if fn:
            self.input_le.setText(fn)

    def browse_output(self):
        dn = QFileDialog.getExistingDirectory(self, 'Select Output Folder')
        if dn:
            self.output_le.setText(dn)

    def start_conversion(self):
        inp, out = self.input_le.text(), self.output_le.text()
        if not inp or not out:
            QMessageBox.warning(self, 'Error', 'Select input file and output folder.')
            return
        if self.worker and self.worker.isRunning():
            return
        self.progress_bar.setValue(0); self.log_te.clear()
        self.cancel_btn.setEnabled(True); self.statusBar().showMessage('Converting...')

        self.worker = ConversionWorker(
            inp, out,
            self.preset_cb.currentText(),
            self.size_sb.value(),
            self.gpu_cb.isChecked()
        )
        self.worker.log_signal.connect(self.log_te.append)
        self.worker.progress_signal.connect(self.progress_bar.setValue)
        self.worker.finished_signal.connect(self.finish)
        self.worker.start()

    def cancel_conversion(self):
        if self.worker:
            self.worker.stop()
        self.cancel_btn.setEnabled(False)
        self.statusBar().showMessage('Cancelled')
        self.log_te.append('[INFO] Conversion cancelled')

    def finish(self, ok, msg):
        self.cancel_btn.setEnabled(False)
        if ok:
            self.progress_bar.setValue(100)
            QMessageBox.information(self, 'Done', f'Output saved: {msg}')
            self.statusBar().showMessage('Completed')
        else:
            self.progress_bar.setValue(0)
            QMessageBox.critical(self, 'Error', msg)
            self.statusBar().showMessage('Failed')

    def dragEnterEvent(self, e): e.accept() if e.mimeData().hasUrls() else None
    def dropEvent(self, e): self.input_le.setText(e.mimeData().urls()[0].toLocalFile())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = VideoConverterGUI(); win.show()
    sys.exit(app.exec())
