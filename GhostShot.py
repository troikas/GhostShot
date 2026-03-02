import tkinter as tk
from tkinter import ttk, messagebox
import pyautogui
import os
import time
import subprocess
import requests
import re
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import sys

# Directory Setup (Use a standard hidden config folder)
BASE_DIR = os.path.expanduser("~/.config/GhostShot")
HISTORY_FILE = os.path.join(BASE_DIR, "history.txt")
CONFIG_FILE = os.path.join(BASE_DIR, "config.txt")
if not os.path.exists(BASE_DIR): os.makedirs(BASE_DIR)

# System Path Helper (for assets when packed)
def get_asset_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def get_active_window_region():
    try:
        window_id = subprocess.check_output(['xdotool', 'getactivewindow']).decode().strip()
        stats = subprocess.check_output(['xwininfo', '-id', window_id]).decode()
        x = int(re.search(r'Absolute upper-left X:\s+(-?\d+)', stats).group(1))
        y = int(re.search(r'Absolute upper-left Y:\s+(-?\d+)', stats).group(1))
        w = int(re.search(r'Width:\s+(\d+)', stats).group(1))
        h = int(re.search(r'Height:\s+(\d+)', stats).group(1))
        return (x, y, w, h)
    except: return None

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f: return f.read().strip()
    return "GhostWorker"

def clear_history():
    if messagebox.askyesno("Confirm", "Are you sure you want to clear all history?"):
        if os.path.exists(HISTORY_FILE): os.remove(HISTORY_FILE)
        for item in history_table.get_children(): history_table.delete(item)
        status_label.config(text="History cleared!", fg="blue")

def capture_task():
    user_text = name_entry.get().strip()
    with open(CONFIG_FILE, "w") as f: f.write(user_text)

    status_label.config(text="⏳ 2s Delay: Click your target window!", fg="orange")
    root.update()

    time.sleep(2)
    region = get_active_window_region()
    root.withdraw()
    time.sleep(0.3)

    desktop = subprocess.check_output(['xdg-user-dir', 'DESKTOP']).decode('utf-8').strip()
    folder_path = os.path.join(desktop, "MyScreenshots")
    if not os.path.exists(folder_path): os.makedirs(folder_path)

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
    filename = f"cap_{datetime.now().strftime('%H%M%S')}.png"
    filepath = os.path.join(folder_path, filename)

    # Capture & Intelligent Watermark
    pic = pyautogui.screenshot(region=region) if region else pyautogui.screenshot()

    if user_text:
        pic = pic.convert("RGBA")
        overlay = Image.new("RGBA", pic.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        w, h = pic.size
        rect_w, rect_h = 220, 40
        padding = 10
        x1, y1 = w - rect_w - padding, h - rect_h - padding
        x2, y2 = w - padding, h - padding

        # Translucent background
        draw.rectangle([x1, y1, x2, y2], fill=(0, 0, 0, 150))

        # Centering Text (Uses base font to avoid path issues)
        text_w, text_h = draw.textsize(user_text)
        text_x = x1 + (rect_w - text_w) / 2
        text_y = y1 + (rect_h - text_h) / 2 - 2

        draw.text((text_x, text_y), user_text, fill=(255, 255, 255, 255))

        pic = Image.alpha_composite(pic, overlay)
        pic = pic.convert("RGB")

    pic.save(filepath)
    root.deiconify()

    url = "LOCAL_ONLY"
    if upload_var.get():
        status_label.config(text="⏳ Uploading...", fg="blue")
        root.update()
        try:
            server = server_var.get()
            if server == "SXCU (Fast)":
                response = requests.post("https://sxcu.net/api/files/create", files={"file": open(filepath, "rb")})
                url = response.json()['url']
            else:
                response = requests.post("https://api.imgbb.com/1/upload",
                                       params={"key": "YOUR_API_KEY_HERE"},
                                       files={"image": open(filepath, "rb")})
                url = response.json()['data']['url']
            root.clipboard_clear()
            root.clipboard_append(url)
            status_label.config(text="✅ SUCCESS! Link copied.", fg="green")
        except:
            status_label.config(text="❌ Upload Error!", fg="red")
            url = "UPLOAD_FAILED"
    else:
        status_label.config(text=f"✅ Saved as {filename}", fg="green")

    history_table.insert('', 0, values=(timestamp, filename, url))
    with open(HISTORY_FILE, "a") as f: f.write(f"{timestamp}|{filename}|{url}\n")

# --- GUI Setup ---
root = tk.Tk()
root.title("GhostShot v7.0")
root.geometry("850x680")

# Note: Icon must be set here for packed versions (will handle later)

header = tk.LabelFrame(root, text=" Settings ", padx=10, pady=10)
header.pack(pady=10, fill="x", padx=20)

tk.Label(header, text="Watermark Text:").grid(row=0, column=0)
name_entry = tk.Entry(header)
name_entry.insert(0, load_config())
name_entry.grid(row=0, column=1, padx=10)

upload_var = tk.BooleanVar(value=False)
chk = tk.Checkbutton(header, text="Enable Upload", variable=upload_var,
                    font=("Arial", 11, "bold"), pady=5)
chk.grid(row=0, column=2, padx=20)

server_var = tk.StringVar(value="SXCU (Fast)")
server_menu = ttk.Combobox(header, textvariable=server_var, values=["SXCU (Fast)", "ImgBB"], width=12)
server_menu.grid(row=0, column=3, padx=5)

btn_frame = tk.Frame(root)
btn_frame.pack(pady=10)

btn = tk.Button(btn_frame, text="CAPTURE WINDOW", command=capture_task,
               bg="#007bff", fg="white", font=("Arial", 14, "bold"), padx=20, pady=10)
btn.grid(row=0, column=0, padx=10)

clear_btn = tk.Button(btn_frame, text="Clear History", command=clear_history,
                     bg="#dc3545", fg="white", font=("Arial", 10))
clear_btn.grid(row=0, column=1, padx=10)

status_label = tk.Label(root, text="Tip: Double-click a row to copy its link.", fg="#666")
status_label.pack()

columns = ('time', 'file', 'url')
history_table = ttk.Treeview(root, columns=columns, show='headings')
history_table.heading('time', text='Date/Time')
history_table.heading('file', text='Filename')
history_table.heading('url', text='URL / Status')
history_table.column('url', width=450)
history_table.pack(padx=20, pady=10, fill='both', expand=True)

# Function to copy link from row on double-click
def copy_from_history(event):
    item = history_table.selection()[0]
    link = history_table.item(item, "values")[2]
    if link and link != "LOCAL_ONLY" and link != "UPLOAD_FAILED":
        root.clipboard_clear()
        root.clipboard_append(link)
        status_label.config(text="Link copied from history!", fg="blue")

history_table.bind("<Double-1>", copy_from_history)

if os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, "r") as f:
        for line in reversed(f.readlines()):
            history_table.insert('', 'end', values=line.strip().split('|'))

root.mainloop()
