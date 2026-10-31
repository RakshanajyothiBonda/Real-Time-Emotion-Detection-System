
"""
MoodLens - Real-Time Emotion Detection System
Live webcam displayed inside the Tkinter dashboard.
"""

from __future__ import annotations

import csv
import os
import subprocess
import sys
import threading
import time
import tkinter as tk

from tkinter import messagebox
from pathlib import Path
from datetime import datetime

import cv2
from PIL import Image, ImageTk
from deepface import DeepFace


# --------------------------------------------------
# Configuration
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
LOG_FILE = BASE_DIR / "emotion_log.csv"
SCREENSHOT_DIR = BASE_DIR / "screenshots"

BG = "#F4F7FB"
PANEL = "#FFFFFF"
INK = "#172033"
MUTED = "#667085"
ACCENT = "#4F46E5"
ACCENT_DARK = "#3730A3"
BORDER = "#E5EAF2"
GREEN = "#0F9F6E"
RED = "#DC2626"

SUGGESTIONS = {
    "happy": "Keep smiling! Have a wonderful day.",
    "sad": "Consider taking a short break or talking to someone you trust.",
    "angry": "Take a slow breath and give yourself a moment to relax.",
    "fear": "Pause, breathe slowly, and focus on one thing at a time.",
    "surprise": "Unexpected moments can bring new opportunities.",
    "neutral": "Stay steady and keep moving forward.",
    "disgust": "Take a short break and refresh your mind."
}


# --------------------------------------------------
# Main Application
# --------------------------------------------------

class EmotionApp:

    def __init__(self, root):

        self.root = root

        self.root.title(
            "MoodLens | Emotion Detection Studio"
        )

        self.root.geometry("1080x720")
        self.root.minsize(900, 620)
        self.root.configure(bg=BG)

        # Camera variables
        self.camera = None
        self.camera_running = False
        self.camera_thread = None

        self.frame_lock = threading.Lock()
        self.latest_frame = None
        self.photo_image = None

        # Emotion variables
        self.latest_emotion = "Looking for a face..."
        self.latest_confidence = 0.0

        self.emotion_history = []

        self.confidence_history = []

        self.emotion_history_size = 5

        self.confidence_threshold = 40.0

        self.latest_suggestion = (
            "Position your face in front of the camera."
        )

        self.latest_region = {}

        self.last_analysis_time = 0.0
        self.last_log_time = 0.0
        self.last_screenshot_time = 0.0

        # Camera display widgets
        self.video_label = None
        self.emotion_value_label = None
        self.confidence_value_label = None
        self.suggestion_label = None

        # Build application
        self._build()

        self.refresh_stats()

        self.root.protocol(
            "WM_DELETE_WINDOW",
            self.close_app
        )

        self.root.after(
            15000,
            self._auto_refresh
        )

    # --------------------------------------------------
    # Main Dashboard
    # --------------------------------------------------

    def _build(self):

        sidebar = tk.Frame(
            self.root,
            bg="#151B35",
            width=230
        )

        sidebar.pack(
            side="left",
            fill="y"
        )

        sidebar.pack_propagate(False)

        tk.Label(
            sidebar,
            text="◈  MOODLENS",
            bg="#151B35",
            fg="white",
            font=("Segoe UI", 17, "bold")
        ).pack(
            anchor="w",
            padx=24,
            pady=(28, 4)
        )

        tk.Label(
            sidebar,
            text="EMOTION DETECTION STUDIO",
            bg="#151B35",
            fg="#9CA8D0",
            font=("Segoe UI", 8, "bold")
        ).pack(
            anchor="w",
            padx=25,
            pady=(0, 34)
        )

        self._nav(
            sidebar,
            "⌂   Overview",
            self.show_overview
        )

        self._nav(
            sidebar,
            "◉   Live detection",
            self.start_camera
        )

        self._nav(
            sidebar,
            "▥   Analytics",
            self.open_dashboard
        )

        self._nav(
            sidebar,
            "☷   Emotion log",
            self.open_log
        )

        tk.Frame(
            sidebar,
            bg="#343B59",
            height=1
        ).pack(
            fill="x",
            padx=20,
            pady=(26, 18)
        )

        tk.Label(
            sidebar,
            text="HOW IT WORKS",
            bg="#151B35",
            fg="#9CA8D0",
            font=("Segoe UI", 8, "bold")
        ).pack(
            anchor="w",
            padx=25,
            pady=(0, 8)
        )

        tk.Label(
            sidebar,
            text=(
                "1  Start your webcam\n\n"
                "2  View the detected emotion\n\n"
                "3  Review saved activity"
            ),
            bg="#151B35",
            fg="#E0E5F5",
            justify="left",
            anchor="w",
            font=("Segoe UI", 10),
            wraplength=175
        ).pack(
            anchor="w",
            padx=25
        )

        tk.Frame(
            sidebar,
            bg="#151B35"
        ).pack(
            expand=True,
            fill="both"
        )

        tk.Label(
            sidebar,
            text="LOCAL DESKTOP APP  •  v2.1",
            bg="#151B35",
            fg="#8994B8",
            font=("Segoe UI", 8)
        ).pack(
            anchor="w",
            padx=24,
            pady=20
        )

        # Main content area
        self.content = tk.Frame(
            self.root,
            bg=BG
        )

        self.content.pack(
            side="left",
            fill="both",
            expand=True
        )

        self._build_overview()

    # --------------------------------------------------
    # Sidebar Navigation
    # --------------------------------------------------

    def _nav(self, parent, text, command):

        tk.Button(
            parent,
            text=text,
            command=command,
            anchor="w",
            bg="#151B35",
            fg="#C5CCE3",
            activebackground="#343B66",
            activeforeground="white",
            relief="flat",
            cursor="hand2",
            font=("Segoe UI", 10),
            padx=18,
            pady=12,
            bd=0
        ).pack(
            fill="x",
            padx=12,
            pady=2
        )

    # --------------------------------------------------
    # Overview Page
    # --------------------------------------------------

    def _build_overview(self):

        for child in self.content.winfo_children():
            child.destroy()

        header = tk.Frame(
            self.content,
            bg=BG
        )

        header.pack(
            fill="x",
            padx=34,
            pady=(28, 20)
        )

        title_area = tk.Frame(
            header,
            bg=BG
        )

        title_area.pack(
            side="left",
            fill="x",
            expand=True
        )

        tk.Label(
            title_area,
            text="Your emotion workspace",
            bg=BG,
            fg=INK,
            font=("Segoe UI", 23, "bold")
        ).pack(anchor="w")

        tk.Label(
            title_area,
            text="A simple overview of your real-time detection activity.",
            bg=BG,
            fg=MUTED,
            font=("Segoe UI", 10)
        ).pack(
            anchor="w",
            pady=(5, 0)
        )

        tk.Label(
            header,
            text=datetime.now().strftime("%a, %d %b %Y"),
            bg=BG,
            fg=MUTED,
            font=("Segoe UI", 10)
        ).pack(
            side="right",
            anchor="n",
            pady=9
        )

        # Hero section
        hero = tk.Frame(
            self.content,
            bg=ACCENT,
            padx=28,
            pady=24
        )

        hero.pack(
            fill="x",
            padx=34
        )

        hero_left = tk.Frame(
            hero,
            bg=ACCENT
        )

        hero_left.pack(
            side="left",
            fill="x",
            expand=True
        )

        tk.Label(
            hero_left,
            text="READY WHEN YOU ARE",
            bg=ACCENT,
            fg="#DCD9FF",
            font=("Segoe UI", 8, "bold")
        ).pack(anchor="w")

        tk.Label(
            hero_left,
            text="Start a live emotion session",
            bg=ACCENT,
            fg="white",
            font=("Segoe UI", 19, "bold")
        ).pack(
            anchor="w",
            pady=(7, 5)
        )

        tk.Label(
            hero_left,
            text=(
                "Use your webcam to estimate facial expressions "
                "and save session results."
            ),
            bg=ACCENT,
            fg="#ECEBFF",
            font=("Segoe UI", 10),
            wraplength=490,
            justify="left"
        ).pack(anchor="w")

        tk.Button(
            hero,
            text="▶  Start detection",
            command=self.start_camera,
            bg="white",
            fg=ACCENT_DARK,
            activebackground="#F0EFFF",
            activeforeground=ACCENT_DARK,
            relief="flat",
            cursor="hand2",
            font=("Segoe UI", 10, "bold"),
            padx=18,
            pady=12,
            bd=0
        ).pack(
            side="right",
            padx=(16, 0),
            pady=8
        )

        tk.Label(
            self.content,
            text="ACTIVITY AT A GLANCE",
            bg=BG,
            fg=MUTED,
            font=("Segoe UI", 9, "bold")
        ).pack(
            anchor="w",
            padx=34,
            pady=(26, 12)
        )

        cards = tk.Frame(
            self.content,
            bg=BG
        )

        cards.pack(
            fill="x",
            padx=34
        )

        self.total_value = self._stat_card(
            cards,
            "Total detections",
            "0",
            "Saved log entries",
            0
        )

        self.top_value = self._stat_card(
            cards,
            "Most detected",
            "—",
            "Most frequent label",
            1
        )

        self.latest_value = self._stat_card(
            cards,
            "Latest activity",
            "—",
            "Most recent saved entry",
            2
        )

        lower = tk.Frame(
            self.content,
            bg=BG
        )

        lower.pack(
            fill="both",
            expand=True,
            padx=34,
            pady=(22, 28)
        )

        # Recent detections
        recent = tk.Frame(
            lower,
            bg=PANEL,
            highlightbackground=BORDER,
            highlightthickness=1
        )

        recent.pack(
            side="left",
            fill="both",
            expand=True
        )

        top = tk.Frame(
            recent,
            bg=PANEL
        )

        top.pack(
            fill="x",
            padx=20,
            pady=(17, 8)
        )

        tk.Label(
            top,
            text="Recent detections",
            bg=PANEL,
            fg=INK,
            font=("Segoe UI", 12, "bold")
        ).pack(side="left")

        tk.Button(
            top,
            text="Refresh",
            command=self.refresh_stats,
            bg=PANEL,
            fg=ACCENT,
            relief="flat",
            cursor="hand2",
            font=("Segoe UI", 9, "bold")
        ).pack(side="right")

        self.recent_text = tk.Text(
            recent,
            height=7,
            bg=PANEL,
            fg=INK,
            relief="flat",
            font=("Consolas", 9),
            wrap="none",
            padx=20,
            pady=8,
            state="disabled",
            highlightthickness=0
        )

        self.recent_text.pack(
            fill="both",
            expand=True
        )

        # Quick actions
        quick = tk.Frame(
            lower,
            bg=PANEL,
            width=220,
            highlightbackground=BORDER,
            highlightthickness=1
        )

        quick.pack(
            side="left",
            fill="y",
            padx=(14, 0)
        )

        quick.pack_propagate(False)

        tk.Label(
            quick,
            text="Quick actions",
            bg=PANEL,
            fg=INK,
            font=("Segoe UI", 12, "bold")
        ).pack(
            anchor="w",
            padx=18,
            pady=(18, 13)
        )

        self._action(
            quick,
            "View analytics",
            self.open_dashboard
        )

        self._action(
            quick,
            "Open CSV log",
            self.open_log
        )

        self._action(
            quick,
            "Generate PDF report",
            self.generate_report
        )

        tk.Label(
            quick,
            text=(
                "Note: emotion labels are\n"
                "AI estimates, not diagnoses."
            ),
            bg=PANEL,
            fg=MUTED,
            justify="left",
            font=("Segoe UI", 9)
        ).pack(
            anchor="w",
            padx=18,
            pady=(18, 0)
        )

    # --------------------------------------------------
    # Statistics Cards
    # --------------------------------------------------

    def _stat_card(
        self,
        parent,
        title,
        value,
        subtitle,
        column
    ):

        card = tk.Frame(
            parent,
            bg=PANEL,
            highlightbackground=BORDER,
            highlightthickness=1,
            padx=18,
            pady=16
        )

        card.grid(
            row=0,
            column=column,
            sticky="nsew",
            padx=(0 if column == 0 else 10, 0)
        )

        parent.grid_columnconfigure(
            column,
            weight=1,
            uniform="stats"
        )

        tk.Label(
            card,
            text=title,
            bg=PANEL,
            fg=MUTED,
            font=("Segoe UI", 9)
        ).pack(anchor="w")

        value_label = tk.Label(
            card,
            text=value,
            bg=PANEL,
            fg=INK,
            font=("Segoe UI", 20, "bold")
        )

        value_label.pack(
            anchor="w",
            pady=(8, 4)
        )

        tk.Label(
            card,
            text=subtitle,
            bg=PANEL,
            fg=MUTED,
            font=("Segoe UI", 8)
        ).pack(anchor="w")

        return value_label

    # --------------------------------------------------
    # Quick Action Buttons
    # --------------------------------------------------

    def _action(self, parent, label, command):

        tk.Button(
            parent,
            text="›   " + label,
            command=command,
            anchor="w",
            bg="#F7F8FC",
            fg=INK,
            activebackground="#ECEEFF",
            relief="flat",
            cursor="hand2",
            font=("Segoe UI", 9, "bold"),
            padx=12,
            pady=11,
            bd=0
        ).pack(
            fill="x",
            padx=14,
            pady=4
        )

    # --------------------------------------------------
    # Start Embedded Camera
    # --------------------------------------------------

    def start_camera(self):

        if self.camera_running:
            self.show_camera_page()
            return

        self.camera = cv2.VideoCapture(0)

        if not self.camera.isOpened():

            self.camera.release()
            self.camera = None

            messagebox.showerror(
                "Camera unavailable",
                "MoodLens could not open the webcam.\n\n"
                "Close other camera applications and try again."
            )

            return

        self.camera_running = True

        self.latest_frame = None
        self.latest_region = {}

        self.latest_emotion = "Looking for a face..."

        self.latest_confidence = 0.0

        self.latest_suggestion = (
            "Position your face in front of the camera."
        )

        self.last_analysis_time = 0.0
        self.last_log_time = 0.0
        self.last_screenshot_time = 0.0

        self.show_camera_page()

        self.camera_thread = threading.Thread(
            target=self._camera_worker,
            daemon=True
        )

        self.camera_thread.start()

        self._update_camera_view()

    # --------------------------------------------------
    # Camera Display Page
    # --------------------------------------------------

    def show_camera_page(self):

        for child in self.content.winfo_children():
            child.destroy()

        page = tk.Frame(
            self.content,
            bg=BG
        )

        page.pack(
            fill="both",
            expand=True
        )

        header = tk.Frame(
            page,
            bg=BG
        )

        header.pack(
            fill="x",
            padx=28,
            pady=(22, 14)
        )

        tk.Label(
            header,
            text="Live emotion detection",
            bg=BG,
            fg=INK,
            font=("Segoe UI", 21, "bold")
        ).pack(side="left")

        tk.Button(
            header,
            text="✕  Stop camera",
            command=self.stop_camera,
            bg="#FEE2E2",
            fg=RED,
            activebackground="#FECACA",
            relief="flat",
            cursor="hand2",
            font=("Segoe UI", 9, "bold"),
            padx=14,
            pady=9
        ).pack(side="right")

        # Video panel inside dashboard
        video_panel = tk.Frame(
            page,
            bg="#101426",
            highlightbackground=BORDER,
            highlightthickness=1
        )

        video_panel.pack(
            fill="both",
            expand=True,
            padx=28,
            pady=(0, 14)
        )

        self.video_label = tk.Label(
            video_panel,
            text="Starting webcam...",
            bg="#101426",
            fg="white",
            font=("Segoe UI", 12)
        )

        self.video_label.pack(
            fill="both",
            expand=True,
            padx=6,
            pady=6
        )

        # Emotion information panel
        info = tk.Frame(
            page,
            bg=PANEL,
            highlightbackground=BORDER,
            highlightthickness=1
        )

        info.pack(
            fill="x",
            padx=28,
            pady=(0, 20)
        )

        line = tk.Frame(
            info,
            bg=PANEL
        )

        line.pack(
            fill="x",
            padx=18,
            pady=(12, 4)
        )

        tk.Label(
            line,
            text="Detected emotion:",
            bg=PANEL,
            fg=MUTED,
            font=("Segoe UI", 10)
        ).pack(side="left")

        self.emotion_value_label = tk.Label(
            line,
            text=self.latest_emotion.title(),
            bg=PANEL,
            fg=ACCENT,
            font=("Segoe UI", 12, "bold")
        )

        self.emotion_value_label.pack(
            side="left",
            padx=(8, 24)
        )

        tk.Label(
            line,
            text="Confidence:",
            bg=PANEL,
            fg=MUTED,
            font=("Segoe UI", 10)
        ).pack(side="left")

        self.confidence_value_label = tk.Label(
            line,
            text="—",
            bg=PANEL,
            fg=INK,
            font=("Segoe UI", 10, "bold")
        )

        self.confidence_value_label.pack(
            side="left",
            padx=(8, 0)
        )

        self.suggestion_label = tk.Label(
            info,
            text=self.latest_suggestion,
            bg=PANEL,
            fg=INK,
            font=("Segoe UI", 9),
            anchor="w",
            justify="left",
            wraplength=700
        )

        self.suggestion_label.pack(
            fill="x",
            padx=18,
            pady=(4, 12)
        )

        tk.Label(
            info,
            text="CAMERA RUNNING",
            bg=PANEL,
            fg=GREEN,
            font=("Segoe UI", 8, "bold")
        ).pack(
            anchor="w",
            padx=18,
            pady=(0, 10)
        )

    # --------------------------------------------------
    # Camera Processing Thread
    # --------------------------------------------------

    def _camera_worker(self):

        while self.camera_running and self.camera is not None:

            try:

                ok, frame = self.camera.read()

                if not ok:
                    time.sleep(0.05)
                    continue

                # Mirror camera
                frame = cv2.flip(frame, 1)

                now = time.time()

                # Run emotion analysis every 1.5 seconds
                if now - self.last_analysis_time >= 1.5:

                    self.last_analysis_time = now

                    try:

                        result = DeepFace.analyze(
                            frame,
                            actions=["emotion"],
                            enforce_detection=False,
                            detector_backend="opencv",
                            silent=True
                        )

                        if isinstance(result, list):
                            result = result[0] if result else {}

                        emotion = str(
                            result.get(
                                "dominant_emotion",
                                "unknown"
                            )
                        ).lower()

                        scores = result.get("emotion", {}) or {}

                        confidence = float(
                            scores.get(emotion, 0.0)
                        )

                        # Store recent emotion predictions
                        if emotion in SUGGESTIONS:
                            self.emotion_history.append(emotion)
                            self.confidence_history.append(confidence)

                            # Keep only the latest five predictions
                            self.emotion_history = self.emotion_history[
                                -self.emotion_history_size:
                            ]

                            self.confidence_history = self.confidence_history[
                                -self.emotion_history_size:
                            ]

                            # Select the most frequently detected emotion
                            stable_emotion = max(
                                set(self.emotion_history),
                                key=self.emotion_history.count
                            )

                            # Calculate average confidence
                            matching_confidences = [
                                score
                                for detected_emotion, score in zip(
                                    self.emotion_history,
                                    self.confidence_history
                                )
                                if detected_emotion == stable_emotion
                            ]

                            stable_confidence = sum(
                                matching_confidences
                            ) / len(matching_confidences)

                            self.latest_confidence = stable_confidence

                            # Handle low-confidence predictions
                            if stable_confidence < self.confidence_threshold:
                                self.latest_emotion = "Uncertain expression"
                                self.latest_suggestion = (
                                    "Please adjust your position and lighting "
                                    "for a clearer expression."
                                )
                            else:
                                self.latest_emotion = stable_emotion
                                self.latest_suggestion = SUGGESTIONS.get(
                                    stable_emotion,
                                    "Keep a comfortable, relaxed expression."
                                )


                        # Save detected face coordinates
                        self.latest_region = result.get(
                            "region", {}
                        )

                        # Save CSV entry every three seconds
                        if now - self.last_log_time >= 3:

                            self._append_log(
                                emotion,
                                confidence
                            )

                            self.last_log_time = now

                        # Save screenshot when score is above 80
                        if (
                            confidence >= 80
                            and now - self.last_screenshot_time >= 5
                        ):

                            self._save_screenshot(
                                emotion,
                                frame
                            )

                            self.last_screenshot_time = now

                    except Exception as exc:

                        print(
                            "Emotion analysis issue:",
                            exc
                        )

                # Draw green face rectangle
                region = self.latest_region

                if region:

                    x = int(region.get("x", 0))
                    y = int(region.get("y", 0))
                    w = int(region.get("w", 0))
                    h = int(region.get("h", 0))

                    if w > 0 and h > 0:

                        cv2.rectangle(
                            frame,
                            (x, y),
                            (x + w, y + h),
                            (0, 255, 0),
                            2
                        )

                        cv2.putText(
                            frame,
                            (
                                f"{self.latest_emotion.upper()} "
                                f"({self.latest_confidence:.2f}%)"
                            ),
                            (max(10, x), max(25, y - 10)),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.7,
                            (0, 255, 0),
                            2
                        )

                # Date and time
                current_time = datetime.now().strftime(
                    "%d-%m-%Y %H:%M:%S"
                )

                cv2.putText(
                    frame,
                    current_time,
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255, 255, 255),
                    2
                )

                # Suggestion on video
                cv2.putText(
                    frame,
                    self.latest_suggestion[:70],
                    (10, frame.shape[0] - 15),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 255, 255),
                    1
                )

                # Share the latest frame with Tkinter
                with self.frame_lock:
                    self.latest_frame = frame.copy()

            except Exception as exc:

                print("Camera issue:", exc)
                time.sleep(0.1)

    # --------------------------------------------------
    # Update Webcam Inside Dashboard
    # --------------------------------------------------

    def _update_camera_view(self):

        if not self.camera_running:
            return

        with self.frame_lock:

            frame = (
                self.latest_frame.copy()
                if self.latest_frame is not None
                else None
            )

        if (
            frame is not None
            and self.video_label is not None
            and self.video_label.winfo_exists()
        ):

            try:

                available_w = max(
                    self.video_label.winfo_width(),
                    320
                )

                available_h = max(
                    self.video_label.winfo_height(),
                    240
                )

                height, width = frame.shape[:2]

                scale = min(
                    available_w / width,
                    available_h / height,
                    1.0
                )

                size = (
                    max(1, int(width * scale)),
                    max(1, int(height * scale))
                )

                frame = cv2.resize(
                    frame,
                    size,
                    interpolation=cv2.INTER_AREA
                )

                frame = cv2.cvtColor(
                    frame,
                    cv2.COLOR_BGR2RGB
                )

                image = Image.fromarray(frame)

                self.photo_image = ImageTk.PhotoImage(
                    image=image
                )

                self.video_label.configure(
                    image=self.photo_image,
                    text=""
                )

            except tk.TclError:
                return

        # Update emotion information
        try:

            if (
                self.emotion_value_label is not None
                and self.emotion_value_label.winfo_exists()
            ):

                self.emotion_value_label.configure(
                    text=self.latest_emotion.title()
                )

                self.confidence_value_label.configure(
                    text=f"{self.latest_confidence:.1f}%"
                )

                self.suggestion_label.configure(
                    text=self.latest_suggestion
                )

        except tk.TclError:
            pass

        self.root.after(
            30,
            self._update_camera_view
        )

    # --------------------------------------------------
    # Save Emotion to CSV
    # --------------------------------------------------

    def _append_log(self, emotion, confidence):

        try:

            LOG_FILE.parent.mkdir(
                parents=True,
                exist_ok=True
            )

            write_header = (
                not LOG_FILE.exists()
                or LOG_FILE.stat().st_size == 0
            )

            with LOG_FILE.open(
                "a",
                newline="",
                encoding="utf-8"
            ) as file:

                writer = csv.writer(file)

                if write_header:

                    writer.writerow([
                        "Date",
                        "Time",
                        "Emotion",
                        "Confidence"
                    ])

                now = datetime.now()

                writer.writerow([
                    now.strftime("%Y-%m-%d"),
                    now.strftime("%H:%M:%S"),
                    emotion.title(),
                    f"{confidence:.2f}"
                ])

        except OSError as exc:

            print(
                "Could not save emotion log:",
                exc
            )

    # --------------------------------------------------
    # Save Screenshots
    # --------------------------------------------------

    def _save_screenshot(self, emotion, frame):

        try:

            SCREENSHOT_DIR.mkdir(
                parents=True,
                exist_ok=True
            )

            filename = (
                f"{emotion}_"
                f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            )

            cv2.imwrite(
                str(SCREENSHOT_DIR / filename),
                frame
            )

        except OSError as exc:

            print(
                "Could not save screenshot:",
                exc
            )

    # --------------------------------------------------
    # Stop Camera
    # --------------------------------------------------

    def stop_camera(self):

        if not self.camera_running:
            return

        self.camera_running = False

        if self.camera is not None:

            try:
                self.camera.release()
            except Exception:
                pass

            self.camera = None

        self.latest_frame = None
        self.latest_region = {}
        self.photo_image = None

        self.video_label = None
        self.emotion_value_label = None
        self.confidence_value_label = None
        self.suggestion_label = None

        self._build_overview()
        self.refresh_stats()

    # --------------------------------------------------
    # Overview Navigation
    # --------------------------------------------------

    def show_overview(self):

        if self.camera_running:
            self.stop_camera()
        else:
            self._build_overview()
            self.refresh_stats()

    # --------------------------------------------------
    # External Dashboard and Report
    # --------------------------------------------------

    def _run_script(self, filename):

        path = BASE_DIR / filename

        if not path.exists():

            messagebox.showerror(
                "File not found",
                f"Could not find {filename} in the project folder."
            )

            return

        try:

            subprocess.Popen(
                [sys.executable, str(path)],
                cwd=str(BASE_DIR)
            )

        except Exception as exc:

            messagebox.showerror(
                "Could not launch",
                str(exc)
            )

    def open_dashboard(self):

        if self.camera_running:
            self.stop_camera()

        self._run_script("dashboard.py")

    def generate_report(self):

        self._run_script("generate_report.py")

    # --------------------------------------------------
    # Open Emotion CSV Log
    # --------------------------------------------------

    def open_log(self):

        if self.camera_running:
            self.stop_camera()

        if not LOG_FILE.exists():

            messagebox.showinfo(
                "No log yet",
                "Start a detection session first to create the emotion log."
            )

            return

        try:

            if sys.platform.startswith("win"):
                os.startfile(str(LOG_FILE))

            elif sys.platform == "darwin":
                subprocess.Popen(["open", str(LOG_FILE)])

            else:
                subprocess.Popen(["xdg-open", str(LOG_FILE)])

        except Exception as exc:

            messagebox.showerror(
                "Could not open log",
                f"Open this file manually:\n{LOG_FILE}\n\n{exc}"
            )

    # --------------------------------------------------
    # Refresh Dashboard Statistics
    # --------------------------------------------------

    def refresh_stats(self):

        rows = []

        try:

            if LOG_FILE.exists():

                with LOG_FILE.open(
                    "r",
                    newline="",
                    encoding="utf-8-sig"
                ) as file:

                    rows = list(csv.DictReader(file))

        except (OSError, csv.Error) as exc:

            print(
                "Could not read emotion log:",
                exc
            )

            return

        if (
            not hasattr(self, "total_value")
            or not self.total_value.winfo_exists()
        ):
            return

        self.total_value.config(
            text=f"{len(rows):,}"
        )

        counts = {}

        for row in rows:

            emotion = (
                row.get("Emotion") or ""
            ).strip().title()

            if emotion:

                counts[emotion] = (
                    counts.get(emotion, 0) + 1
                )

        self.top_value.config(
            text=(
                max(counts, key=counts.get)
                if counts else "—"
            )
        )

        latest = rows[-1] if rows else {}

        latest_text = latest.get(
            "Time",
            "—"
        ) or "—"

        if latest.get("Date"):

            latest_text = (
                f"{latest.get('Date')}  {latest_text}"
            )

        self.latest_value.config(
            text=latest_text
        )

        self.recent_text.config(
            state="normal"
        )

        self.recent_text.delete(
            "1.0",
            "end"
        )

        recent_rows = rows[-7:][::-1]

        if not recent_rows:

            self.recent_text.insert(
                "end",
                "No detections saved yet.\n"
                "Start a live session to see results here."
            )

        else:

            self.recent_text.insert(
                "end",
                f"{'DATE':<12} {'TIME':<10} "
                f"{'EMOTION':<12} {'CONFIDENCE':>10}\n"
            )

            self.recent_text.insert(
                "end",
                "─" * 48 + "\n"
            )

            for row in recent_rows:

                date = (
                    row.get("Date") or "—"
                )[:10]

                clock = (
                    row.get("Time") or "—"
                )[:8]

                emotion = (
                    row.get("Emotion") or "—"
                ).title()[:12]

                confidence = (
                    row.get("Confidence") or "—"
                )

                self.recent_text.insert(
                    "end",
                    f"{date:<12} {clock:<10} "
                    f"{emotion:<12} {confidence:>10}\n"
                )

        self.recent_text.config(
            state="disabled"
        )

    # --------------------------------------------------
    # Automatic Dashboard Refresh
    # --------------------------------------------------

    def _auto_refresh(self):

        try:

            if self.root.winfo_exists():

                if not self.camera_running:
                    self.refresh_stats()

                self.root.after(
                    15000,
                    self._auto_refresh
                )

        except tk.TclError:
            pass

    # --------------------------------------------------
    # Close Application
    # --------------------------------------------------

    def close_app(self):

        self.camera_running = False

        if self.camera is not None:

            try:
                self.camera.release()
            except Exception:
                pass

            self.camera = None

        self.root.destroy()


# --------------------------------------------------
# Application Entry Point
# --------------------------------------------------

def main():

    root = tk.Tk()

    app = EmotionApp(root)

    root.mainloop()


if __name__ == "__main__":
    main()
