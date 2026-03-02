# GhostShot Pro v1.1

A lightweight and powerful screenshot utility for Linux and Windows. Capture screen regions, add custom watermarks, and upload to cloud services instantly.

## 🚀 What's New in v1.1
- **Multi-Service Hosting:** Choose between ImgBB, SXCU.net, or FreeImage.host.
- **Precision Capture:** Interactive region selection using the `scrot` engine.
- **Smart Workspace:** Automatic creation and management of the `MyScreenshots` folder on your Desktop.
- **Improved History Log:** Double-click entries to open files locally or copy URLs with one click.
- **Persistent Settings:** Your API keys, watermarks, and preferences are saved in `config.ini`.

## 📥 Installation

### Linux (Mint/Ubuntu/Debian)
1. Install dependencies:
   `sudo apt update && sudo apt install scrot python3-pil`
2. Install the package:
   `sudo dpkg -i ghostshot_1.1_amd64.deb`

### Windows
1. Download `GhostShot_v1.1.exe`.
2. Run and start capturing.

## ⚙️ Configuration
Access the **Settings** menu to:
- Enter your **API Keys**.
- Select your **Upload Provider**.
- Customize your **Watermark** text.
- Change the **Save Directory**.

## 🛠 Fixes in this version
- Resolved `AttributeError: save_locally` crash.
- Fixed path detection for non-English Linux environments.
- Corrected History TreeView display issues.

---
*Created by troikas*
