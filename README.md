# MoodLens – Real-Time Emotion Detection System

MoodLens is a Python desktop application that uses a webcam and DeepFace to estimate facial expressions in real time. It records detection results and provides an analytics dashboard with PDF report generation.

## Features
- Live webcam feed inside the desktop application
- Face detection and emotion estimation
- Emotion labels and confidence scores
- Stabilized emotion predictions
- Automatic CSV logging
- Emotion analytics dashboard
- Emotion distribution and confidence trend charts
- PDF reports with summary statistics
- Start and stop detection controls

## Technologies Used
- Python
- Tkinter
- OpenCV
- DeepFace
- Pandas
- Matplotlib
- ReportLab

## Requirements
- Windows 10 or Windows 11
- Python 3.10
- Working webcam

## Installation

    git clone https://github.com/RakshanajyothiBonda/Real-Time-Emotion-Detection-System.git
    cd Real-Time-Emotion-Detection-System
    py -3.10 -m venv .venv
    .\.venv\Scripts\Activate.ps1
    python -m pip install --upgrade pip
    pip install -r requirements.txt

## Run the Application

    python main.py

## Project Files
- main.py – Main desktop application
- dashboard.py – Analytics dashboard and PDF report functionality
- deepface_emotion.py – Webcam-based emotion detection
- emotion_detector.py – Emotion detection support
- generate_report.py – PDF report generation
- login.py – Demo login functionality
- requirements.txt – Required packages

## Data and Reports

Detection records are stored locally in emotion_log.csv. Generated reports and screenshots are saved in their respective folders.

## Important Notes

- Allow webcam access when prompted.
- Initial DeepFace setup may take some time.
- Emotion results are estimates based on visible facial expressions, not a person's actual internal emotional state.
- This project is for educational purposes and is not a medical diagnostic tool.
- Login functionality is for demonstration only.

## Author
Bonda Rakshana Jyothi

GitHub: https://github.com/RakshanajyothiBonda
