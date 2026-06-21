import tkinter as tk
from tkinter import ttk
import threading
import time
import pyautogui
import keyboard
import urllib.request
import sys
import os
import subprocess

pyautogui.FAILSAFE = True

CURRENT_VERSION = "1.0"
VERSION_URL = "https://raw.githubusercontent.com/jaydensmither222-art/autoclicker/main/version.txt"
SCRIPT_URL  = "https://raw.githubusercontent.com/jaydensmither222-art/autoclicker/main/autoclicker.py"

def check_for_update():
    try:
        with urllib.request.urlopen(VERSION_URL, timeout=5) as r:
            latest = r.read().decode().strip()
        if latest != CURRENT_VERSION:
            return latest
    except Exception:
        pass
    return None

def do_update(latest_version, status_label):
    try:
        status_label.config(text=f"Downloading v{latest_version}...")
        script_path = os.path.abspath(sys.argv[0])
        new_path = script_path + ".new"
        urllib.request.urlretrieve(SCRIPT_URL, new_path)

        # Replace current script and relaunch
        backup = script_path + ".bak"
        if os.path.exists(backup):
            os.remove(backup)
        os.rename(script_path, backup)
        os.rename(new_path, script_path)
        subprocess.Popen([sys.executable, script_path])
        sys.exit(0)
    except Exception as e:
        status_label.config(text=f"Update failed: {e}")

class AutoClicker:
    def __init__(self, root):
        self.root = root
        self.root.title(f"Auto Clicker v{CURRENT_VERSION}")
        self.root.geometry("340x460")
        self.root.resizable(False, False)
        self.root.configure(bg="#1a1a2e")

        self.clicking = False
        self.click_thread = None
        self.click_count = 0

        self._build_ui()
        self._setup_hotkey()
        self._check_update_async()

    def _check_update_async(self):
        def run():
            latest = check_for_update()
            if latest:
                self.root.after(0, lambda: self._show_update_banner(latest))
        threading.Thread(target=run, daemon=True).start()

    def _show_update_banner(self, latest_version):
        BG = "#1a1a2e"
        ACCENT = "#e94560"
        banner = tk.Frame(self.root, bg="#0f3460")
        banner.pack(fill="x", padx=20, pady=(0, 4))
        tk.Label(banner, text=f"⬆  Update v{latest_version} available!",
                 font=("Consolas", 9), bg="#0f3460", fg="#4ecca3").pack(side="left", padx=8, pady=6)
        tk.Button(banner, text="Update now", font=("Consolas", 9, "bold"),
                  bg=ACCENT, fg="white", relief="flat", cursor="hand2",
                  command=lambda: do_update(latest_version, self.status_label)
                  ).pack(side="right", padx=8, pady=4)

    def _build_ui(self):
        BG = "#1a1a2e"
        PANEL = "#16213e"
        ACCENT = "#e94560"
        TEXT = "#eaeaea"
        MUTED = "#8888aa"
        ENTRY_BG = "#0f3460"

        tk.Label(self.root, text="⚡ AUTO CLICKER", font=("Consolas", 16, "bold"),
                 bg=BG, fg=ACCENT).pack(pady=(20, 2))
        tk.Label(self.root, text=f"v{CURRENT_VERSION}  |  Hotkey: F6",
                 font=("Consolas", 8), bg=BG, fg=MUTED).pack(pady=(0, 10))

        # --- Click Interval ---
        panel1 = tk.Frame(self.root, bg=PANEL)
        panel1.pack(fill="x", padx=20, pady=4, ipady=8)
        tk.Label(panel1, text="CLICK INTERVAL", font=("Consolas", 9, "bold"),
                 bg=PANEL, fg=MUTED).pack(pady=(6, 4))
        row = tk.Frame(panel1, bg=PANEL)
        row.pack()
        for label, attr, default, width in [
            ("Hours", "hours_var", "0", 5),
            ("Mins",  "mins_var",  "0", 5),
            ("Secs",  "secs_var",  "0", 5),
            ("ms",    "ms_var",  "100", 6),
        ]:
            col = tk.Frame(row, bg=PANEL)
            col.pack(side="left", padx=6)
            tk.Label(col, text=label, font=("Consolas", 8), bg=PANEL, fg=MUTED).pack()
            var = tk.StringVar(value=default)
            setattr(self, attr, var)
            tk.Entry(col, textvariable=var, width=width, font=("Consolas", 11),
                     bg=ENTRY_BG, fg=TEXT, insertbackground=TEXT,
                     relief="flat", justify="center").pack()

        # --- Click Options ---
        panel2 = tk.Frame(self.root, bg=PANEL)
        panel2.pack(fill="x", padx=20, pady=4, ipady=8)
        tk.Label(panel2, text="CLICK OPTIONS", font=("Consolas", 9, "bold"),
                 bg=PANEL, fg=MUTED).pack(pady=(6, 6))
        row2 = tk.Frame(panel2, bg=PANEL)
        row2.pack()

        col_btn = tk.Frame(row2, bg=PANEL)
        col_btn.pack(side="left", padx=12)
        tk.Label(col_btn, text="Button", font=("Consolas", 8), bg=PANEL, fg=MUTED).pack()
        self.button_var = tk.StringVar(value="left")
        ttk.Combobox(col_btn, textvariable=self.button_var,
                     values=["left", "right", "middle"],
                     width=7, state="readonly", font=("Consolas", 10)).pack()

        col_type = tk.Frame(row2, bg=PANEL)
        col_type.pack(side="left", padx=12)
        tk.Label(col_type, text="Type", font=("Consolas", 8), bg=PANEL, fg=MUTED).pack()
        self.type_var = tk.StringVar(value="single")
        ttk.Combobox(col_type, textvariable=self.type_var,
                     values=["single", "double"],
                     width=7, state="readonly", font=("Consolas", 10)).pack()

        style = ttk.Style()
        style.theme_use("default")
        style.configure("TCombobox", fieldbackground=ENTRY_BG, background=ENTRY_BG,
                        foreground=TEXT, selectbackground=ACCENT, selectforeground=TEXT)

        # --- Repeat ---
        panel3 = tk.Frame(self.root, bg=PANEL)
        panel3.pack(fill="x", padx=20, pady=4, ipady=8)
        tk.Label(panel3, text="REPEAT", font=("Consolas", 9, "bold"),
                 bg=PANEL, fg=MUTED).pack(pady=(6, 6))
        row3 = tk.Frame(panel3, bg=PANEL)
        row3.pack()
        self.repeat_mode = tk.StringVar(value="infinite")
        tk.Radiobutton(row3, text="Infinite", variable=self.repeat_mode, value="infinite",
                       bg=PANEL, fg=TEXT, selectcolor=PANEL, activebackground=PANEL,
                       font=("Consolas", 9)).pack(side="left", padx=10)
        tk.Radiobutton(row3, text="Stop after:", variable=self.repeat_mode, value="count",
                       bg=PANEL, fg=TEXT, selectcolor=PANEL, activebackground=PANEL,
                       font=("Consolas", 9)).pack(side="left")
        self.repeat_count_var = tk.StringVar(value="10")
        tk.Entry(row3, textvariable=self.repeat_count_var, width=6, font=("Consolas", 10),
                 bg=ENTRY_BG, fg=TEXT, insertbackground=TEXT, relief="flat", justify="center").pack(side="left", padx=4)
        tk.Label(row3, text="clicks", font=("Consolas", 9), bg=PANEL, fg=MUTED).pack(side="left")

        # --- Status ---
        self.status_var = tk.StringVar(value="Stopped")
        self.count_var  = tk.StringVar(value="Clicks: 0")
        status_row = tk.Frame(self.root, bg=BG)
        status_row.pack(pady=(8, 0))
        self.status_label = tk.Label(status_row, textvariable=self.status_var,
                                     font=("Consolas", 10, "bold"), bg=BG, fg=MUTED)
        self.status_label.pack(side="left", padx=10)
        tk.Label(status_row, textvariable=self.count_var,
                 font=("Consolas", 10), bg=BG, fg=MUTED).pack(side="left", padx=10)

        # --- Button ---
        self.btn = tk.Button(self.root, text="▶  START  (F6)", font=("Consolas", 12, "bold"),
                             bg=ACCENT, fg="white", activebackground="#c73652",
                             activeforeground="white", relief="flat", cursor="hand2",
                             command=self.toggle, padx=20, pady=10)
        self.btn.pack(pady=12)

    def _setup_hotkey(self):
        keyboard.add_hotkey("f6", self.toggle)

    def _get_interval(self):
        try:
            h  = int(self.hours_var.get()) * 3600
            m  = int(self.mins_var.get())  * 60
            s  = int(self.secs_var.get())
            ms = int(self.ms_var.get()) / 1000
            return max(h + m + s + ms, 0.01)
        except ValueError:
            return 0.1

    def toggle(self):
        if self.clicking: self.stop()
        else: self.start()

    def start(self):
        self.clicking = True
        self.click_count = 0
        self.count_var.set("Clicks: 0")
        self.status_var.set("Running...")
        self.status_label.config(fg="#4ecca3")
        self.btn.config(text="■  STOP  (F6)", bg="#333366")
        self.click_thread = threading.Thread(target=self._click_loop, daemon=True)
        self.click_thread.start()

    def stop(self):
        self.clicking = False
        self.status_var.set("Stopped")
        self.status_label.config(fg="#8888aa")
        self.btn.config(text="▶  START  (F6)", bg="#e94560")

    def _click_loop(self):
        interval  = self._get_interval()
        button    = self.button_var.get()
        double    = self.type_var.get() == "double"
        infinite  = self.repeat_mode.get() == "infinite"
        max_clicks = int(self.repeat_count_var.get()) if not infinite else -1

        while self.clicking:
            if double: pyautogui.doubleClick(button=button)
            else:      pyautogui.click(button=button)
            self.click_count += 1
            self.root.after(0, lambda c=self.click_count: self.count_var.set(f"Clicks: {c}"))
            if not infinite and self.click_count >= max_clicks:
                self.root.after(0, self.stop)
                break
            time.sleep(interval)

if __name__ == "__main__":
    root = tk.Tk()
    app = AutoClicker(root)
    root.mainloop()
