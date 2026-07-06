import tkinter as tk
from tkinter import messagebox
import subprocess
import os

def start_camera():
    subprocess.Popen(["python", "deepface_emotion.py"])

def open_dashboard():
    subprocess.Popen(["python", "dashboard.py"])

def open_log():
    if os.path.exists("emotion_log.csv"):
        os.startfile("emotion_log.csv")
    else:
        messagebox.showerror("Error", "emotion_log.csv not found!")

root = tk.Tk()
root.title("AI Emotion Recognition System")
root.geometry("500x450")

title = tk.Label(
    root,
    text="AI Emotion Recognition System",
    font=("Arial", 18, "bold")
)
title.pack(pady=20)

btn1 = tk.Button(
    root,
    text="Start Camera",
    width=25,
    height=2,
    command=start_camera
)
btn1.pack(pady=10)

btn2 = tk.Button(
    root,
    text="View Dashboard",
    width=25,
    height=2,
    command=open_dashboard
)
btn2.pack(pady=10)

btn3 = tk.Button(
    root,
    text="Open Emotion Log",
    width=25,
    height=2,
    command=open_log
)
btn3.pack(pady=10)

btn4 = tk.Button(
    root,
    text="Exit",
    width=25,
    height=2,
    command=root.destroy
)
btn4.pack(pady=20)

root.mainloop()