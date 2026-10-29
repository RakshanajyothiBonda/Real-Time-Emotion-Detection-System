# MoodLens — Real-Time Emotion Detection System

A Python desktop application that uses a webcam and DeepFace to estimate facial expressions, save session records, and review simple analytics.

## What's improved

- A modern desktop home screen with clear navigation and quick actions.
- At-a-glance counts, most frequent emotion, latest activity, and recent log entries.
- A simpler analytics window with emotion counts and distribution bars.
- More reliable script launching using the current Python interpreter and project folder.
- Cross-platform CSV opening where supported.
- Clear note that emotion labels are estimates, not diagnoses.

## Features

- Real-time webcam-based facial emotion estimation
- Emotion confidence values
- CSV activity log (`emotion_log.csv`)
- Screenshot capture (existing behavior)
- Emotion analytics
- PDF report generation (existing script)

## Requirements

- Python 3.10 or 3.11 recommended
- A working webcam
- Packages listed in `requirements.txt`

## Setup (Windows PowerShell)

```powershell
git clone https://github.com/RakshanajyothiBonda/Real-Time-Emotion-Detection-System.git
cd Real-Time-Emotion-Detection-System
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python main.py
```

If PowerShell blocks activation, you can run the environment's Python directly: `.venv\Scripts\python.exe main.py`.

For an existing local clone, do not clone again. Open its folder, activate your environment, install the requirements, and run `python main.py`.

## Main controls

- **Start detection** launches `deepface_emotion.py` in a separate window. Press `q` in the webcam window to stop.
- **Analytics** opens a summary of saved emotion counts.
- **Emotion log** opens the CSV in your default spreadsheet/text application.
- **Generate PDF report** runs `generate_report.py`.

## Project files

- `main.py` — desktop home screen
- `deepface_emotion.py` — webcam detection, screenshot capture, and CSV logging
- `dashboard.py` — analytics window
- `generate_report.py` — PDF report generation
- `emotion_log.csv` — local session records
- `screenshots/` — saved example/session screenshots
- `reports/` — generated PDF reports

## Important notes

- Webcam access must be permitted by the operating system.
- DeepFace/TensorFlow dependencies may take time to install and may behave differently across Python versions. If installation fails, use Python 3.10 or 3.11 in a fresh virtual environment.
- This project estimates visible facial expressions; it cannot reliably determine a person's true internal emotional state. Do not use its output for medical, employment, educational, or other high-stakes decisions.
- `login.py` is a basic demo login only, not production-grade authentication.

## Updating the existing GitHub repository

After testing locally, review the changes and push them to the same repository:

```powershell
git status
git add main.py dashboard.py README.md requirements.txt
git commit -m "Improve desktop UI and analytics"
git push
```

If you use a different branch, push the current branch with `git push origin <branch-name>`. Keep your existing `.git` folder when updating your local clone; do not initialize a new repository inside it.
