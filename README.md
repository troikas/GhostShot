# 👻 GhostShot v1.0
**The Ultimate Screenshot & Auto-Upload Tool for Freelancers**

GhostShot is a lightweight, powerful automation tool designed specifically for micro-task workers (SproutGigs, FreeCash, etc.) and developers who need to capture, watermark, and upload proofs in seconds.



---

## 🚀 Key Features
* **Smart Window Capture:** Automatically detects the active window (perfect for dual-monitor setups).
* **Custom Watermarking:** Adds a professional, translucent centered watermark to your proofs.
* **One-Click Cloud Upload:** Supports **SXCU** (Ultra Fast) and **ImgBB** (High Reliability).
* **Auto-Copy to Clipboard:** The image URL is copied instantly after upload.
* **History Logs:** Never lose a link! All screenshots and URLs are saved in a local database.
* **Privacy First:** Toggle internet upload on/off with a single checkbox.

---

## 🛠️ Installation

### For Linux (Ubuntu/Mint/Debian)
1. Download the `.deb` package from the [Releases](https://github.com/YOUR_USERNAME/GhostShot/releases) section.
2. Double-click to install.
3. Find **GhostShot** in your Applications menu.

### For Windows
1. Download `GhostShot.exe`.
2. Run it (no installation required).

---

## 📦 Requirements (If running from source)
If you want to run the Python script directly, you will need:
* Python 3.6+
* `pyautogui`, `Pillow`, `requests`
* Linux users: `xdotool`, `xwininfo`

```bash
pip install pyautogui Pillow requests
sudo apt install xdotool xwininfo
