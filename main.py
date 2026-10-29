"""Modern desktop launcher for the Real-Time Emotion Detection System."""
from __future__ import annotations
import csv
import os
import subprocess
import sys
import tkinter as tk
from tkinter import messagebox
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent
LOG_FILE = BASE_DIR / "emotion_log.csv"
BG = "#F4F7FB"
PANEL = "#FFFFFF"
INK = "#172033"
MUTED = "#667085"
ACCENT = "#4F46E5"
ACCENT_DARK = "#3730A3"
BORDER = "#E5EAF2"
GREEN = "#0F9F6E"

class EmotionApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        root.title("MoodLens | Emotion Detection Studio")
        root.geometry("1080x720")
        root.minsize(900, 620)
        root.configure(bg=BG)
        self._build()
        self.refresh_stats()
        root.after(15000, self._auto_refresh)

    def _build(self):
        sidebar = tk.Frame(self.root, bg="#151B35", width=230)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)
        tk.Label(sidebar, text="◈  MOODLENS", bg="#151B35", fg="white",
                 font=("Segoe UI", 17, "bold")).pack(anchor="w", padx=24, pady=(28, 4))
        tk.Label(sidebar, text="EMOTION DETECTION STUDIO", bg="#151B35", fg="#9CA8D0",
                 font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=25, pady=(0, 34))
        self._nav(sidebar, "⌂   Overview", True, lambda: None)
        self._nav(sidebar, "◉   Live detection", False, self.start_camera)
        self._nav(sidebar, "▥   Analytics", False, self.open_dashboard)
        self._nav(sidebar, "☷   Emotion log", False, self.open_log)
        tk.Frame(sidebar, bg="#343B59", height=1).pack(fill="x", padx=20, pady=(26, 18))
        tk.Label(sidebar, text="HOW IT WORKS", bg="#151B35", fg="#9CA8D0",
                 font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=25, pady=(0, 8))
        tk.Label(sidebar, text="1  Start your webcam\n\n2  View the detected emotion\n\n3  Review saved activity",
                 bg="#151B35", fg="#E0E5F5", justify="left", anchor="w",
                 font=("Segoe UI", 10), wraplength=175).pack(anchor="w", padx=25)
        tk.Frame(sidebar, bg="#151B35").pack(expand=True, fill="both")
        tk.Label(sidebar, text="LOCAL DESKTOP APP  •  v2.0", bg="#151B35", fg="#8994B8",
                 font=("Segoe UI", 8)).pack(anchor="w", padx=24, pady=20)

        content = tk.Frame(self.root, bg=BG)
        content.pack(side="left", fill="both", expand=True)
        header = tk.Frame(content, bg=BG)
        header.pack(fill="x", padx=34, pady=(28, 20))
        title_area = tk.Frame(header, bg=BG)
        title_area.pack(side="left", fill="x", expand=True)
        tk.Label(title_area, text="Your emotion workspace", bg=BG, fg=INK,
                 font=("Segoe UI", 23, "bold")).pack(anchor="w")
        tk.Label(title_area, text="A simple overview of your real-time detection activity.",
                 bg=BG, fg=MUTED, font=("Segoe UI", 10)).pack(anchor="w", pady=(5, 0))
        tk.Label(header, text=datetime.now().strftime("%a, %d %b %Y"), bg=BG, fg=MUTED,
                 font=("Segoe UI", 10)).pack(side="right", anchor="n", pady=9)

        hero = tk.Frame(content, bg=ACCENT, padx=28, pady=24)
        hero.pack(fill="x", padx=34)
        hero_left = tk.Frame(hero, bg=ACCENT)
        hero_left.pack(side="left", fill="x", expand=True)
        tk.Label(hero_left, text="READY WHEN YOU ARE", bg=ACCENT, fg="#DCD9FF",
                 font=("Segoe UI", 8, "bold")).pack(anchor="w")
        tk.Label(hero_left, text="Start a live emotion session", bg=ACCENT, fg="white",
                 font=("Segoe UI", 19, "bold")).pack(anchor="w", pady=(7, 5))
        tk.Label(hero_left, text="Use your webcam to detect facial expressions and save session results.",
                 bg=ACCENT, fg="#ECEBFF", font=("Segoe UI", 10), wraplength=490,
                 justify="left").pack(anchor="w")
        tk.Button(hero, text="▶  Start detection", command=self.start_camera,
                  bg="white", fg=ACCENT_DARK, activebackground="#F0EFFF", activeforeground=ACCENT_DARK,
                  relief="flat", cursor="hand2", font=("Segoe UI", 10, "bold"), padx=18, pady=12,
                  bd=0).pack(side="right", padx=(16, 0), pady=8)

        tk.Label(content, text="ACTIVITY AT A GLANCE", bg=BG, fg=MUTED,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=34, pady=(26, 12))
        cards = tk.Frame(content, bg=BG)
        cards.pack(fill="x", padx=34)
        self.total_value = self._stat_card(cards, "Total detections", "0", "All saved log entries", 0)
        self.top_value = self._stat_card(cards, "Most detected", "—", "Most frequent label", 1)
        self.latest_value = self._stat_card(cards, "Latest activity", "—", "Most recent saved entry", 2)

        lower = tk.Frame(content, bg=BG)
        lower.pack(fill="both", expand=True, padx=34, pady=(22, 28))
        recent = tk.Frame(lower, bg=PANEL, highlightbackground=BORDER, highlightthickness=1)
        recent.pack(side="left", fill="both", expand=True)
        top = tk.Frame(recent, bg=PANEL)
        top.pack(fill="x", padx=20, pady=(17, 8))
        tk.Label(top, text="Recent detections", bg=PANEL, fg=INK,
                 font=("Segoe UI", 12, "bold")).pack(side="left")
        tk.Button(top, text="Refresh", command=self.refresh_stats, bg=PANEL, fg=ACCENT,
                  relief="flat", cursor="hand2", font=("Segoe UI", 9, "bold")).pack(side="right")
        self.recent_text = tk.Text(recent, height=7, bg=PANEL, fg=INK, relief="flat",
                                   font=("Consolas", 9), wrap="none", padx=20, pady=8,
                                   state="disabled", highlightthickness=0)
        self.recent_text.pack(fill="both", expand=True)
        quick = tk.Frame(lower, bg=PANEL, width=220, highlightbackground=BORDER, highlightthickness=1)
        quick.pack(side="left", fill="y", padx=(14, 0))
        quick.pack_propagate(False)
        tk.Label(quick, text="Quick actions", bg=PANEL, fg=INK,
                 font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=18, pady=(18, 13))
        self._action(quick, "View analytics", self.open_dashboard)
        self._action(quick, "Open CSV log", self.open_log)
        self._action(quick, "Generate PDF report", self.generate_report)
        tk.Label(quick, text="Note: emotion labels are\nAI estimates, not diagnoses.", bg=PANEL,
                 fg=MUTED, justify="left", font=("Segoe UI", 9)).pack(anchor="w", padx=18, pady=(18, 0))

    def _nav(self, parent, text, active, command):
        bg = "#343B66" if active else "#151B35"
        fg = "white" if active else "#C5CCE3"
        tk.Button(parent, text=text, command=command, anchor="w", bg=bg, fg=fg,
                  activebackground="#343B66", activeforeground="white", relief="flat",
                  cursor="hand2", font=("Segoe UI", 10, "bold" if active else "normal"),
                  padx=18, pady=12, bd=0).pack(fill="x", padx=12, pady=2)

    def _stat_card(self, parent, title, value, subtitle, column):
        card = tk.Frame(parent, bg=PANEL, highlightbackground=BORDER, highlightthickness=1, padx=18, pady=16)
        card.grid(row=0, column=column, sticky="nsew", padx=(0 if column == 0 else 10, 0))
        parent.grid_columnconfigure(column, weight=1, uniform="stats")
        tk.Label(card, text=title, bg=PANEL, fg=MUTED, font=("Segoe UI", 9)).pack(anchor="w")
        value_label = tk.Label(card, text=value, bg=PANEL, fg=INK, font=("Segoe UI", 20, "bold"))
        value_label.pack(anchor="w", pady=(8, 4))
        tk.Label(card, text=subtitle, bg=PANEL, fg=MUTED, font=("Segoe UI", 8)).pack(anchor="w")
        return value_label

    def _action(self, parent, label, command):
        tk.Button(parent, text="›   " + label, command=command, anchor="w", bg="#F7F8FC", fg=INK,
                  activebackground="#ECEEFF", relief="flat", cursor="hand2",
                  font=("Segoe UI", 9, "bold"), padx=12, pady=11, bd=0).pack(fill="x", padx=14, pady=4)

    def _run_script(self, filename):
        path = BASE_DIR / filename
        if not path.exists():
            messagebox.showerror("File not found", f"Could not find {filename} in the project folder.")
            return
        try:
            subprocess.Popen([sys.executable, str(path)], cwd=str(BASE_DIR))
        except Exception as exc:
            messagebox.showerror("Could not launch", str(exc))

    def start_camera(self):
        self._run_script("deepface_emotion.py")

    def open_dashboard(self):
        self._run_script("dashboard.py")

    def generate_report(self):
        self._run_script("generate_report.py")

    def open_log(self):
        if not LOG_FILE.exists():
            messagebox.showinfo("No log yet", "Start a detection session first to create the emotion log.")
            return
        try:
            if sys.platform.startswith("win"):
                os.startfile(str(LOG_FILE))
            elif sys.platform == "darwin":
                subprocess.Popen(["open", str(LOG_FILE)])
            else:
                subprocess.Popen(["xdg-open", str(LOG_FILE)])
        except Exception as exc:
            messagebox.showerror("Could not open log", f"Open this file manually:\n{LOG_FILE}\n\n{exc}")

    def refresh_stats(self):
        rows = []
        try:
            if LOG_FILE.exists():
                with LOG_FILE.open("r", newline="", encoding="utf-8-sig") as file:
                    rows = list(csv.DictReader(file))
        except (OSError, csv.Error) as exc:
            messagebox.showwarning("Log unavailable", f"Could not read emotion_log.csv:\n{exc}")
            return
        self.total_value.config(text=f"{len(rows):,}")
        counts = {}
        for row in rows:
            emotion = (row.get("Emotion") or "").strip().title()
            if emotion:
                counts[emotion] = counts.get(emotion, 0) + 1
        self.top_value.config(text=max(counts, key=counts.get) if counts else "—")
        latest = rows[-1] if rows else {}
        latest_text = latest.get("Time", "—") or "—"
        if latest.get("Date"):
            latest_text = f"{latest.get('Date')}  {latest_text}"
        self.latest_value.config(text=latest_text)
        self.recent_text.config(state="normal")
        self.recent_text.delete("1.0", "end")
        recent_rows = rows[-7:][::-1]
        if not recent_rows:
            self.recent_text.insert("end", "No detections saved yet.\nStart a live session to see results here.")
        else:
            self.recent_text.insert("end", f"{'DATE':<12} {'TIME':<10} {'EMOTION':<12} {'CONFIDENCE':>10}\n")
            self.recent_text.insert("end", "─" * 48 + "\n")
            for row in recent_rows:
                date = (row.get("Date") or "—")[:10]
                time = (row.get("Time") or "—")[:8]
                emotion = (row.get("Emotion") or "—").title()[:12]
                conf = (row.get("Confidence") or "—")
                self.recent_text.insert("end", f"{date:<12} {time:<10} {emotion:<12} {conf:>10}\n")
        self.recent_text.config(state="disabled")

    def _auto_refresh(self):
        if self.root.winfo_exists():
            self.refresh_stats()
            self.root.after(15000, self._auto_refresh)

def main():
    root = tk.Tk()
    EmotionApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
