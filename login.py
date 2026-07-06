import tkinter as tk
from tkinter import messagebox
import subprocess

# Login credentials
USERNAME = "admin"
PASSWORD = "1234"

def login():
    username = username_entry.get()
    password = password_entry.get()

    if username == USERNAME and password == PASSWORD:
        root.destroy()
        subprocess.Popen(["python", "main.py"])
    else:
        messagebox.showerror("Login Failed", "Invalid Username or Password")

root = tk.Tk()
root.title("AI Emotion Detection Login")
root.geometry("400x300")
root.resizable(False, False)

title = tk.Label(root, text="AI Emotion Detection", font=("Arial", 18, "bold"))
title.pack(pady=20)

tk.Label(root, text="Username").pack()
username_entry = tk.Entry(root, width=30)
username_entry.pack(pady=5)

tk.Label(root, text="Password").pack()
password_entry = tk.Entry(root, show="*", width=30)
password_entry.pack(pady=5)

login_button = tk.Button(root, text="Login", width=20, command=login)
login_button.pack(pady=20)

root.mainloop()