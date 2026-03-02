import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import pyautogui
from PIL import Image, ImageDraw
import requests
import os
import datetime
import configparser
import subprocess

class GhostShot:
    def __init__(self, root):
        self.root = root
        self.root.title("GhostShot Pro v4.6 - FIXED")
        self.root.geometry("750x580")

        self.config_file = "config.ini"
        self.config = configparser.ConfigParser()
        self.load_settings()

        # --- UI ---
        top_frame = tk.Frame(root)
        top_frame.pack(pady=10, fill=tk.X)

        tk.Button(top_frame, text="Select Area & Save", command=self.save_locally,
                  width=22, bg="#f0f0f0", fg="black").pack(side=tk.LEFT, padx=10)

        tk.Button(top_frame, text="Select & Upload", command=self.capture_and_upload,
                  bg="#4CAF50", fg="white", font=("Arial", 10, "bold"), width=22).pack(side=tk.LEFT, padx=10)

        tk.Button(top_frame, text="Settings", command=self.open_settings, width=10).pack(side=tk.RIGHT, padx=10)

        # Treeview
        tk.Label(root, text="History (Double click to open):", font=("Arial", 10, "bold")).pack(anchor=tk.W, padx=10)
        self.tree = ttk.Treeview(root, columns=("Time", "File", "Provider", "Link"), show='headings')
        self.tree.heading("Time", text="Time")
        self.tree.heading("File", text="File Name")
        self.tree.heading("Provider", text="Service")
        self.tree.heading("Link", text="Link / Path")
        self.tree.column("Time", width=100); self.tree.column("File", width=130)
        self.tree.column("Provider", width=90); self.tree.column("Link", width=400)
        self.tree.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)

        self.tree.bind("<Double-1>", self.on_double_click)

        bot_frame = tk.Frame(root)
        bot_frame.pack(pady=10)
        tk.Button(bot_frame, text="Copy Link", command=self.copy_from_tree, width=15, bg="#2196F3", fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(bot_frame, text="Open Folder", command=self.open_screenshot_folder, width=15).pack(side=tk.LEFT, padx=5)

        self.status_label = tk.Label(root, text="Ready", fg="gray")
        self.status_label.pack()

    def load_settings(self):
        home = os.path.expanduser("~")
        desktop = os.path.join(home, "Desktop")
        if not os.path.exists(desktop): desktop = os.path.join(home, "Επιφάνεια εργασίας")
        default_folder = os.path.join(desktop, "MyScreenshots")
        if not os.path.exists(default_folder): os.makedirs(default_folder)

        if os.path.exists(self.config_file):
            self.config.read(self.config_file)
            self.api_key = self.config.get('SETTINGS', 'api_key', fallback="")
            self.watermark_text = self.config.get('SETTINGS', 'watermark', fallback="GhostShot")
            self.save_path = self.config.get('SETTINGS', 'save_path', fallback=default_folder)
            self.provider = self.config.get('SETTINGS', 'provider', fallback="ImgBB")
        else:
            self.api_key = ""; self.watermark_text = "GhostShot"
            self.save_path = default_folder; self.provider = "ImgBB"

    def save_locally(self):
        self.take_screenshot(upload=False)

    def capture_and_upload(self):
        if self.provider != "SXCU" and not self.api_key:
            messagebox.showerror("Error", f"API Key required for {self.provider}!")
            return
        self.take_screenshot(upload=True)

    def take_screenshot(self, upload):
        self.root.withdraw()
        self.root.after(500, lambda: self.capture_logic(upload))

    def capture_logic(self, upload):
        now = datetime.datetime.now()
        filename = f"Shot_{now.strftime('%H%M%S')}.png"
        full_path = os.path.join(self.save_path, filename)

        try:
            # Λήψη με scrot (σιγουρέψου ότι έτρεξες: sudo apt install scrot)
            subprocess.run(["scrot", "-s", full_path])

            if os.path.exists(full_path):
                img = Image.open(full_path)
                draw = ImageDraw.Draw(img)
                draw.text((15, 15), self.watermark_text, fill=(255, 255, 255))
                img.save(full_path)

                link = "Local Only"
                if upload:
                    self.status_label.config(text="Uploading...", fg="blue"); self.root.update()
                    link = self.do_upload(full_path)

                self.tree.insert("", 0, values=(now.strftime("%H:%M:%S"), filename, self.provider if upload else "Local", link))
                if "http" in link:
                    self.root.clipboard_clear(); self.root.clipboard_append(link)
                    self.status_label.config(text="Link Copied!", fg="green")
        except Exception as e:
            messagebox.showerror("Error", f"Capture failed: {e}")
        finally:
            self.root.deiconify()

    def do_upload(self, path):
        try:
            # Ορίζουμε το User-Agent για να μας δέχεται το SXCU και οι άλλοι πάροχοι
            headers = {
                'User-Agent': 'GhostShot-Pro/1.1 (Linux Mint; troikas)'
            }

            if self.provider == "ImgBB":
                r = requests.post("https://api.imgbb.com/1/upload",
                                 data={"key": self.api_key},
                                 files={"image": open(path, "rb")},
                                 headers=headers)
                return r.json()['data']['url']

            elif self.provider == "SXCU":
                # Δοκιμάζουμε το σωστό endpoint
                url = "https://sxcu.net/api/files/upload"
                files = {"file": open(path, "rb")}

                r = requests.post(url, files=files, headers=headers)

                # Έλεγχος αν η απάντηση είναι όντως JSON και όχι HTML error
                if r.status_code == 200:
                    try:
                        return r.json()['url']
                    except:
                        return "JSON Error from SXCU"
                else:
                    print(f"SXCU Server Error: {r.status_code}")
                    return f"Error {r.status_code}"

            elif self.provider == "FreeImage":
                r = requests.post("https://freeimage.host/api/1/upload",
                                 data={"key": self.api_key},
                                 files={"source": open(path, "rb")},
                                 headers=headers)
                return r.json()['image']['url']
        except Exception as e:
            print(f"Upload Error: {e}") # Για να βλέπεις το λάθος στο τερματικό
            return "Upload Failed"

    def open_settings(self):
        win = tk.Toplevel(self.root)
        win.title("Settings")
        win.geometry("400x350")

        tk.Label(win, text="Watermark Name:").pack(pady=5)
        wm = tk.Entry(win, width=35); wm.insert(0, self.watermark_text); wm.pack()

        tk.Label(win, text="Upload Provider:").pack(pady=5)
        prov_var = tk.StringVar(value=self.provider)
        tk.OptionMenu(win, prov_var, "ImgBB", "SXCU", "FreeImage").pack()

        tk.Label(win, text="API Key:").pack(pady=5)
        key = tk.Entry(win, width=35); key.insert(0, self.api_key); key.pack()

        def save():
            self.watermark_text, self.api_key, self.provider = wm.get(), key.get(), prov_var.get()
            if not self.config.has_section('SETTINGS'): self.config.add_section('SETTINGS')
            self.config.set('SETTINGS', 'watermark', self.watermark_text)
            self.config.set('SETTINGS', 'api_key', self.api_key)
            self.config.set('SETTINGS', 'provider', self.provider)
            self.config.set('SETTINGS', 'save_path', self.save_path)
            with open(self.config_file, 'w') as f: self.config.write(f)
            win.destroy()
        tk.Button(win, text="Save Settings", command=save, bg="#4CAF50", fg="white").pack(pady=20)

    def on_double_click(self, event):
        sel = self.tree.selection()
        if sel:
            path = os.path.join(self.save_path, self.tree.item(sel[0])['values'][1])
            subprocess.run(["xdg-open", path])

    def open_screenshot_folder(self):
        subprocess.run(["xdg-open", self.save_path])

    def copy_from_tree(self):
        sel = self.tree.selection()
        if sel:
            link = self.tree.item(sel[0])['values'][3]
            self.root.clipboard_clear(); self.root.clipboard_append(link)

if __name__ == "__main__":
    root = tk.Tk()
    app = GhostShot(root)
    root.mainloop()
