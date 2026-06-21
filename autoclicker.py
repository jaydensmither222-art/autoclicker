import tkinter as tk
from tkinter import ttk
import threading
import time
import pyautogui
import keyboard

pyautogui.FAILSAFE = True

class AutoClicker:
    def __init__(self, root):
        self.root = root
        self.root.title("Auto Clicker")
        self.root.geometry("340x420")
        self.root.resizable(False, False)
        self.root.configure(bg="#1a1a2e")

        self.clicking = False
        self.click_thread = None
        self.click_count = 0

        self._build_ui()
        self._setup_hotkey()

    def _build_ui(self):
        BG = "#1a1a2e"
        PANEL = "#16213e"
        ACCENT = "#e94560"
        TEXT = "#eaeaea"
        MUTED = "#8888aa"
        ENTRY_BG = "#0f3460"

        # Title
        tk.Label(self.root, text="⚡ AUTO CLICKER", font=("Consolas", 16, "bold"),
                 bg=BG, fg=ACCENT).pack(pady=(20, 4))
        tk.Label(self.root, text="Hotkey: F6  |  Failsafe: move mouse to corner",
                 font=("Consolas", 8), bg=BG, fg=MUTED).pack(pady=(0, 16))

        # --- Click Interval ---
        panel1 = tk.Frame(self.root, bg=PANEL, bd=0, relief="flat")
        panel1.pack(fill="x", padx=20, pady=6, ipady=10)

        tk.Label(panel1, text="CLICK INTERVAL", font=("Consolas", 9, "bold"),
                 bg=PANEL, fg=MUTED).pack(pady=(8, 4))

        row = tk.Frame(panel1, bg=PANEL)
        row.pack()
        for label, attr, default, width in [
            ("Hours", "hours_var", "0", 5),
            ("Mins", "mins_var", "0", 5),
            ("Secs", "secs_var", "0", 5),
            ("ms", "ms_var", "100", 6),
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
        panel2 = tk.Frame(self.root, bg=PANEL, bd=0, relief="flat")
        panel2.pack(fill="x", padx=20, pady=6, ipady=10)

        tk.Label(panel2, text="CLICK OPTIONS", font=("Consolas", 9, "bold"),
                 bg=PANEL, fg=MUTED).pack(pady=(8, 6))

        row2 = tk.Frame(panel2, bg=PANEL)
        row2.pack()

        # Mouse button
        col_btn = tk.Frame(row2, bg=PANEL)
        col_btn.pack(side="left", padx=12)
        tk.Label(col_btn, text="Button", font=("Consolas", 8), bg=PANEL, fg=MUTED).pack()
        self.button_var = tk.StringVar(value="left")
        btn_menu = ttk.Combobox(col_btn, textvariable=self.button_var,
                                values=["left", "right", "middle"],
                                width=7, state="readonly", font=("Consolas", 10))
        btn_menu.pack()

        # Click type
        col_type = tk.Frame(row2, bg=PANEL)
        col_type.pack(side="left", padx=12)
        tk.Label(col_type, text="Type", font=("Consolas", 8), bg=PANEL, fg=MUTED).pack()
        self.type_var = tk.StringVar(value="single")
        type_menu = ttk.Combobox(col_type, textvariable=self.type_var,
                                 values=["single", "double"],
                                 width=7, state="readonly", font=("Consolas", 10))
        type_menu.pack()

        # Style comboboxes
        style = ttk.Style()
        style.theme_use("default")
        style.configure("TCombobox", fieldbackground=ENTRY_BG, background=ENTRY_BG,
                        foreground=TEXT, selectbackground=ACCENT, selectforeground=TEXT)

        # --- Click Repeat ---
        panel3 = tk.Frame(self.root, bg=PANEL, bd=0, relief="flat")
        panel3.pack(fill="x", padx=20, pady=6, ipady=10)

        tk.Label(panel3, text="REPEAT", font=("Consolas", 9, "bold"),
                 bg=PANEL, fg=MUTED).pack(pady=(8, 6))

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
        tk.Entry(panel3.master if False else panel3, textvariable=self.repeat_count_var,
                 width=6, font=("Consolas", 10), bg=ENTRY_BG, fg=TEXT,
                 insertbackground=TEXT, relief="flat", justify="center").pack(in_=row3, side="left", padx=4)
        tk.Label(row3, text="clicks", font=("Consolas", 9), bg=PANEL, fg=MUTED).pack(side="left")

        # --- Status Bar ---
        self.status_var = tk.StringVar(value="Stopped")
        self.count_var = tk.StringVar(value="Clicks: 0")

        status_row = tk.Frame(self.root, bg=BG)
        status_row.pack(pady=(10, 0))
        self.status_label = tk.Label(status_row, textvariable=self.status_var,
                                     font=("Consolas", 10, "bold"), bg=BG, fg=MUTED)
        self.status_label.pack(side="left", padx=10)
        tk.Label(status_row, textvariable=self.count_var,
                 font=("Consolas", 10), bg=BG, fg=MUTED).pack(side="left", padx=10)

        # --- Start/Stop Button ---
        self.btn = tk.Button(self.root, text="▶  START  (F6)", font=("Consolas", 12, "bold"),
                             bg=ACCENT, fg="white", activebackground="#c73652",
                             activeforeground="white", relief="flat", cursor="hand2",
                             command=self.toggle, padx=20, pady=10)
        self.btn.pack(pady=14)

    def _setup_hotkey(self):
        keyboard.add_hotkey("f6", self.toggle)

    def _get_interval(self):
        try:
            h = int(self.hours_var.get()) * 3600
            m = int(self.mins_var.get()) * 60
            s = int(self.secs_var.get())
            ms = int(self.ms_var.get()) / 1000
            total = h + m + s + ms
            return max(total, 0.01)
        except ValueError:
            return 0.1

    def toggle(self):
        if self.clicking:
            self.stop()
        else:
            self.start()

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
        interval = self._get_interval()
        button = self.button_var.get()
        double = self.type_var.get() == "double"
        infinite = self.repeat_mode.get() == "infinite"
        max_clicks = int(self.repeat_count_var.get()) if not infinite else -1

        while self.clicking:
            if double:
                pyautogui.doubleClick(button=button)
            else:
                pyautogui.click(button=button)

            self.click_count += 1
            self.root.after(0, lambda c=self.click_count: self.count_var.set(f"Clicks: {c}"))

            if not infinite and self.click_count >= max_clicks:
                self.root.after(0, self.stop)
                break

            time.sleep(interval)


if __name__ == "__main__":
    root = tk.Root() if False else tk.Tk()
    app = AutoClicker(root)
    root.mainloop()
