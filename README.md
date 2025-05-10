**🚀 Video Converter Pro**

> *Your personal desktop video compression wizard powered by Python, PyQt6 & FFmpeg*

[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## ✨ Features

* 🎥 **Drag & Drop** support for effortless file selection
* ⚙️ Choose from multiple FFmpeg presets (`ultrafast`, `fast`, `medium`, `slow`, `veryslow`)
* 💾 **Target size** slider (in MB) to hit your exact file size goal
* 🚀 **GPU acceleration** via NVENC when available
* 📊 Real‑time **progress bar** & detailed **conversion log**
* 📁 Automatic output folder creation

---

## 📦 Prerequisites

1. **Python 3.8+** installed.
2. **FFmpeg** CLI tools (`ffmpeg` & `ffprobe`) installed and paths configured:

   ```python
   FFMPEG_PATH = r"C:\ffmpeg\bin\ffmpeg.exe"
   FFPROBE_PATH = r"C:\ffmpeg\bin\ffprobe.exe"
   ```
3. Install Python dependencies:

   ```bash
   pip install PyQt6
   ```

---

## 🏗 Installation

1. Clone this repository:

   ```bash
   git clone https://github.com/Amir-Hossein-shamsi/video-converter-pro.git
   cd video-converter-pro
   ```
2. Update the FFmpeg paths in the source if needed (see **Prerequisites**).
3. (Optional) Create a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate      # Linux/macOS
   venv\\Scripts\\activate     # Windows
   ```
4. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

---

## 🚀 Usage

1. Launch the application:

   ```bash
   python main.py
   ```
2. **Select Input** video by clicking **Browse** or dragging a file onto the dashed area.
3. **Select Output** folder.
4. Adjust **Preset**, **Target Size (MB)**, and toggle **Use GPU** if available.
5. Click **Start** to begin conversion.
6. Monitor the **progress bar** and **log** for details.
7. Click **Cancel** to stop at any time.

> ℹ️ After completion, a dialog will show the output file location.

---

## 📸 Screenshot

![App Screenshot](docs/screenshot.png)

---

## 🛠️ How It Works

1. **Probe Duration**: Uses `ffprobe` to read video length.
2. **Bitrate Calculation**: Computes video bitrate from target size minus audio bitrate (128 kbps).
3. **FFmpeg Command**: Builds and runs an `ffmpeg` command with chosen preset and codecs.
4. **Progress Tracking**: Parses `ffmpeg` output for `time=HH:MM:SS.ms` to update GUI progress bar.

---

## 🤝 Contributing

Contributions are welcome!

1. Fork the repo.
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -m "feat: add awesome feature"`
4. Push: `git push origin feature/my-feature`
5. Open a Pull Request.

Please make sure your code follows PEP8 and include relevant tests.

---

## 📄 License

This project is licensed under the **MIT License**. See [LICENSE](LICENSE) for details.

---

<footer align="center">
  Made with ❤️ by **Your Name**
</footer>
