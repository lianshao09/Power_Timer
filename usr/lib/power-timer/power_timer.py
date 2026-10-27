#!/usr/bin/env python3
"""Power Timer - suspend, restart or shut down after a delay or at a set time."""
import subprocess
import time
import tkinter as tk
import tkinter.font as tkfont
from datetime import datetime, timedelta
from tkinter import messagebox

ACTIONS = {"Suspend": "suspend", "Restart": "reboot", "Shutdown": "poweroff"}
MODES = ("Countdown", "At time")

# --- Setup window colors ----------------------------------------------------
BG = "#16171d"
FIELD = "#252833"
TEXT = "#e8e8ee"
MUTED = "#8b8fa0"
ACCENT = "#4c8dff"
ACCENT_HOVER = "#6aa0ff"

# --- Countdown window: text sizes (points) and colors -----------------------
# Change these if you want the text smaller or larger.
CLOCK_SIZE = 16          # system clock at the top
ACTION_SIZE = 24         # action word AND countdown (same size)
CLOCK_COLOR = "#6f6f6f"
ACTION_COLOR = "#cfcfcf"
TIMER_COLOR = "#cfcfcf"


def fmt(seconds):
    seconds = max(0, int(seconds))
    return f"{seconds // 3600:02d}:{seconds % 3600 // 60:02d}:{seconds % 60:02d}"


def run_action(action):
    cmd = ACTIONS[action]
    try:
        subprocess.run(["systemctl", cmd], check=True)
    except Exception:
        try:
            subprocess.run(["loginctl", cmd], check=True)
        except Exception as exc:
            messagebox.showerror("Power Timer", f"Could not run '{cmd}': {exc}")


class Segmented(tk.Frame):
    """A row of options where exactly one is selected."""

    def __init__(self, parent, options, variable, font):
        super().__init__(parent, bg=FIELD)
        self.var = variable
        self.labels = {}
        for i, opt in enumerate(options):
            lbl = tk.Label(self, text=opt, font=font, padx=16, pady=9,
                           cursor="hand2", bd=0)
            lbl.grid(row=0, column=i, sticky="nsew", padx=3, pady=3)
            lbl.bind("<Button-1>", lambda e, o=opt: self.var.set(o))
            self.columnconfigure(i, weight=1, uniform="seg")
            self.labels[opt] = lbl
        self.var.trace_add("write", lambda *_: self.refresh())
        self.refresh()

    def refresh(self):
        for opt, lbl in self.labels.items():
            selected = opt == self.var.get()
            lbl.configure(bg=ACCENT if selected else FIELD,
                          fg="#ffffff" if selected else MUTED)


# ----------------------------------------------------------------------------
# Window 1: settings
# ----------------------------------------------------------------------------
def setup_window():
    root = tk.Tk()
    root.title("Power Timer")
    root.configure(bg=BG)
    root.resizable(False, False)

    f_title = tkfont.Font(family="Sans", size=16, weight="bold")
    f_section = tkfont.Font(family="Sans", size=9, weight="bold")
    f_seg = tkfont.Font(family="Sans", size=11, weight="bold")
    f_input = tkfont.Font(family="Sans", size=20)
    f_small = tkfont.Font(family="Sans", size=10)
    f_btn = tkfont.Font(family="Sans", size=12, weight="bold")

    action = tk.StringVar(value="Shutdown")
    mode = tk.StringVar(value="Countdown")
    h_var, m_var, s_var = (tk.StringVar(value=v) for v in ("0", "30", "0"))
    later = datetime.now() + timedelta(hours=1)
    ch_var = tk.StringVar(value=f"{later.hour:02d}")
    cm_var = tk.StringVar(value=f"{later.minute:02d}")
    result = {}

    body = tk.Frame(root, bg=BG)
    body.pack(padx=28, pady=24, fill="both")

    tk.Label(body, text="Power Timer", font=f_title, bg=BG, fg=TEXT,
             anchor="w").pack(fill="x", pady=(0, 18))

    tk.Label(body, text="ACTION", font=f_section, bg=BG, fg=MUTED,
             anchor="w").pack(fill="x", pady=(0, 6))
    Segmented(body, list(ACTIONS), action, f_seg).pack(fill="x")

    tk.Label(body, text="WHEN", font=f_section, bg=BG, fg=MUTED,
             anchor="w").pack(fill="x", pady=(18, 6))
    Segmented(body, MODES, mode, f_seg).pack(fill="x")

    def make_spin(parent, var, hi):
        return tk.Spinbox(
            parent, from_=0, to=hi, width=3, textvariable=var, font=f_input,
            justify="center", format="%02.0f", wrap=True, bg=FIELD, fg=TEXT,
            insertbackground=TEXT, buttonbackground=FIELD, relief="flat",
            highlightthickness=0, bd=0, disabledbackground=FIELD,
            readonlybackground=FIELD, selectbackground=ACCENT)

    holder = tk.Frame(body, bg=BG)
    holder.pack(fill="x", pady=(14, 0))

    count_f = tk.Frame(holder, bg=BG)
    count_f.grid(row=0, column=0, sticky="w")
    for var, hi, unit in ((h_var, 99, "h"), (m_var, 59, "m"), (s_var, 59, "s")):
        make_spin(count_f, var, hi).pack(side="left")
        tk.Label(count_f, text=unit, font=f_small, bg=BG, fg=MUTED).pack(
            side="left", padx=(4, 14))

    clock_f = tk.Frame(holder, bg=BG)
    clock_f.grid(row=0, column=0, sticky="w")
    make_spin(clock_f, ch_var, 23).pack(side="left")
    tk.Label(clock_f, text=":", font=f_input, bg=BG, fg=MUTED).pack(
        side="left", padx=6)
    make_spin(clock_f, cm_var, 59).pack(side="left")

    preview = tk.Label(body, text="", font=f_small, bg=BG, fg=MUTED, anchor="w")
    preview.pack(fill="x", pady=(14, 0))

    def to_int(var, lo, hi):
        value = int(var.get())
        if not lo <= value <= hi:
            raise ValueError
        return value

    def compute_target():
        if mode.get() == "Countdown":
            secs = (to_int(h_var, 0, 99) * 3600 + to_int(m_var, 0, 59) * 60
                    + to_int(s_var, 0, 59))
            if secs <= 0:
                raise ValueError
            return time.time() + secs
        t = datetime.now().replace(hour=to_int(ch_var, 0, 23),
                                   minute=to_int(cm_var, 0, 59),
                                   second=0, microsecond=0)
        if t <= datetime.now():
            t += timedelta(days=1)
        return t.timestamp()

    def refresh(*_):
        if mode.get() == "Countdown":
            clock_f.grid_remove()
            count_f.grid()
        else:
            count_f.grid_remove()
            clock_f.grid()
        try:
            target = compute_target()
        except ValueError:
            preview.configure(text="Enter a valid time")
            return
        preview.configure(
            text=f"{action.get()} at {datetime.fromtimestamp(target):%H:%M:%S}"
                 f"  -  in {fmt(target - time.time())}")

    for var in (action, mode, h_var, m_var, s_var, ch_var, cm_var):
        var.trace_add("write", refresh)

    def tick():
        refresh()
        root.after(1000, tick)

    def start():
        try:
            target = compute_target()
        except ValueError:
            messagebox.showwarning("Power Timer", "Please enter a valid time.")
            return
        result["action"] = action.get()
        result["target"] = target
        root.destroy()

    btn = tk.Button(body, text="Start", font=f_btn, bg=ACCENT, fg="#ffffff",
                    activebackground=ACCENT_HOVER, activeforeground="#ffffff",
                    relief="flat", bd=0, highlightthickness=0, pady=11,
                    cursor="hand2", command=start)
    btn.pack(fill="x", pady=(20, 0))
    btn.bind("<Enter>", lambda e: btn.configure(bg=ACCENT_HOVER))
    btn.bind("<Leave>", lambda e: btn.configure(bg=ACCENT))

    root.bind("<Return>", lambda e: start())
    root.bind("<Escape>", lambda e: root.destroy())
    tick()
    root.mainloop()
    return result or None


# ----------------------------------------------------------------------------
# Window 2: countdown
#   F11 or double-click: toggle full screen
#   Esc: leave full screen, then cancel and return to settings
# ----------------------------------------------------------------------------
def countdown_window(action, target):
    root = tk.Tk()
    root.title("Power Timer")
    root.configure(bg="black")
    root.geometry("560x340")
    root.minsize(360, 220)
    state = {"outcome": "cancel", "full": False}

    f_clock = tkfont.Font(family="Sans", size=CLOCK_SIZE)
    f_action = tkfont.Font(family="Sans", size=ACTION_SIZE, weight="bold")

    root.rowconfigure(0, weight=1, uniform="rows")
    root.rowconfigure(1, weight=1)
    root.rowconfigure(2, weight=1, uniform="rows")
    root.columnconfigure(0, weight=1)

    clock = tk.Label(root, bg="black", fg=CLOCK_COLOR, font=f_clock)
    clock.grid(row=0, column=0, sticky="n", pady=24)

    # Action word with the countdown directly below it, centered on screen.
    center = tk.Frame(root, bg="black")
    center.grid(row=1, column=0)
    tk.Label(center, text=action.upper(), bg="black", fg=ACTION_COLOR,
             font=f_action).pack()
    remain = tk.Label(center, bg="black", fg=TIMER_COLOR, font=f_action)
    remain.pack(pady=(6, 0))

    def finish(outcome):
        state["outcome"] = outcome
        root.destroy()

    def set_full(value):
        state["full"] = value
        root.attributes("-fullscreen", value)
        root.configure(cursor="none" if value else "")

    def on_escape(_event=None):
        if state["full"]:
            set_full(False)
        else:
            finish("cancel")

    root.bind("<F11>", lambda e: set_full(not state["full"]))
    root.bind("<Double-Button-1>", lambda e: set_full(not state["full"]))
    root.bind("<Escape>", on_escape)

    def tick():
        left = target - time.time()
        clock.configure(text=time.strftime("%H:%M:%S"))
        remain.configure(text=fmt(left + 0.999))
        if left <= 0:
            finish("done")
            return
        root.after(200, tick)

    tick()
    root.mainloop()
    return state["outcome"]


def main():
    while True:
        cfg = setup_window()
        if not cfg:
            return
        if countdown_window(cfg["action"], cfg["target"]) == "done":
            run_action(cfg["action"])
            return


if __name__ == "__main__":
    main()
