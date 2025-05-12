# 🎵 APE to FLAC Converter & Tagger

This project provides scripts to batch convert `.ape` (Monkey's Audio) files to `.flac`, optionally split them using `.cue` files, tag the resulting FLAC files, and clean up unnecessary files.

---

## 📦 Features

- Convert entire `.ape` albums to `.flac` using `ffmpeg` or `shntool + cue`.
- Split APE files into individual track FLACs using `.cue` files.
- Tag FLAC tracks automatically with metadata from `.cue` files.
- Compress or remove original APE files after successful conversion.
- Use multiprocessing to speed up processing of directories.
- Skip already-tagged or pregap files to avoid redundancy.
- Optional: Delete `*pregap.flac` files automatically.

---

## 🛠️ Setup

### 1. Clone this project

```bash
git clone https://github.com/yourusername/ape-to-flac-tools.git
cd ape-to-flac-tools
