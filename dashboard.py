"""Readable analytics window for emotion_log.csv."""
import csv
from pathlib import Path
import tkinter as tk
from tkinter import messagebox

BASE_DIR = Path(__file__).resolve().parent
LOG_FILE = BASE_DIR / "emotion_log.csv"
BG = "#F4F7FB"
INK = "#172033"
MUTED = "#667085"
ACCENT = "#4F46E5"


def load_rows():
    if not LOG_FILE.exists():
        return []
    with LOG_FILE.open("r", newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def main():
    root = tk.Tk()
    root.title("MoodLens | Emotion Analytics")
    root.geometry("760x600")
    root.minsize(620, 480)
    root.configure(bg=BG)
    tk.Label(root, text="Emotion analytics", bg=BG, fg=INK,
             font=("Segoe UI", 23, "bold")).pack(anchor="w", padx=28, pady=(24, 3))
    tk.Label(root, text="A summary of the records saved by your detection sessions.",
             bg=BG, fg=MUTED, font=("Segoe UI", 10)).pack(anchor="w", padx=28, pady=(0, 18))
    body = tk.Frame(root, bg="white", highlightbackground="#E5EAF2", highlightthickness=1)
    body.pack(fill="both", expand=True, padx=28, pady=(0, 18))
    rows = []
    try:
        rows = load_rows()
    except (OSError, csv.Error) as exc:
        messagebox.showerror("Could not read log", str(exc))
    counts = {}
    for row in rows:
        emotion = (row.get("Emotion") or "").strip().title()
        if emotion:
            counts[emotion] = counts.get(emotion, 0) + 1
    summary = tk.Frame(body, bg="white")
    summary.pack(fill="x", padx=22, pady=20)
    for title, value in [("TOTAL RECORDS", f"{len(rows):,}"),
                         ("EMOTION TYPES", str(len(counts))),
                         ("MOST FREQUENT", max(counts, key=counts.get) if counts else "—")]:
        card = tk.Frame(summary, bg="#F7F8FC", padx=14, pady=13)
        card.pack(side="left", fill="both", expand=True, padx=(0, 9))
        tk.Label(card, text=title, bg="#F7F8FC", fg=MUTED,
                 font=("Segoe UI", 8, "bold")).pack(anchor="w")
        tk.Label(card, text=value, bg="#F7F8FC", fg=INK,
                 font=("Segoe UI", 17, "bold")).pack(anchor="w", pady=(6, 0))
    tk.Label(body, text="Emotion distribution", bg="white", fg=INK,
             font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=22, pady=(0, 10))
    chart = tk.Frame(body, bg="white")
    chart.pack(fill="both", expand=True, padx=22, pady=(0, 18))
    if not counts:
        tk.Label(chart, text="No emotion data yet. Start a webcam session to build your report.",
                 bg="white", fg=MUTED, font=("Segoe UI", 10)).pack(anchor="w", pady=10)
    else:
        max_count = max(counts.values()) or 1
        for emotion, count in sorted(counts.items(), key=lambda item: item[1], reverse=True):
            line = tk.Frame(chart, bg="white")
            line.pack(fill="x", pady=5)
            tk.Label(line, text=emotion, width=12, anchor="w", bg="white", fg=INK,
                     font=("Segoe UI", 9, "bold")).pack(side="left")
            track = tk.Frame(line, bg="#EEF0F8", height=16)
            track.pack(side="left", fill="x", expand=True, padx=10)
            track.pack_propagate(False)
            bar_width = max(4, int(240 * count / max_count))
            tk.Frame(track, bg=ACCENT, width=bar_width, height=16).pack(side="left", fill="y")
            tk.Label(line, text=f"{count}  ({count / max(1, len(rows)):.0%})", width=12,
                     anchor="e", bg="white", fg=MUTED, font=("Segoe UI", 9)).pack(side="right")
    tk.Label(root, text="Emotion recognition is an AI estimate and may be inaccurate.",
             bg=BG, fg=MUTED, font=("Segoe UI", 9)).pack(anchor="w", padx=28, pady=(0, 14))
    root.mainloop()

if __name__ == "__main__":
    main()
