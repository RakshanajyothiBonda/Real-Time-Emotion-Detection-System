import cv2
from deepface import DeepFace
from datetime import datetime
import csv
import os
import time

# -----------------------------
# Open Webcam
# -----------------------------
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Cannot open webcam")
    exit()

# -----------------------------
# CSV File
# -----------------------------
filename = "emotion_log.csv"

if not os.path.exists(filename):
    with open(filename, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Date", "Time", "Emotion", "Confidence"])

# -----------------------------
# Screenshot Folder
# -----------------------------
folder = "screenshots"

if not os.path.exists(folder):
    os.makedirs(folder)

# Save only one screenshot every 5 seconds
last_saved = 0

# -----------------------------
# Emotion Suggestions
# -----------------------------
suggestions = {
    "happy": "Keep smiling! Have a wonderful day.",
    "sad": "Take a short break and talk to someone you trust.",
    "angry": "Take a deep breath and relax for a moment.",
    "fear": "Stay calm. Focus on one thing at a time.",
    "surprise": "Unexpected moments can lead to new opportunities!",
    "neutral": "Stay positive and keep moving forward.",
    "disgust": "Take a break and refresh your mind."
}

print("Press 'q' to quit.")

# -----------------------------
# Main Loop
# -----------------------------
while True:

    ret, frame = cap.read()

    if not ret:
        break

    try:

        results = DeepFace.analyze(
            frame,
            actions=["emotion"],
            enforce_detection=False,
            detector_backend="opencv"
        )

        if isinstance(results, list):
            result = results[0]
        else:
            result = results

        emotion = result["dominant_emotion"]
        confidence = result["emotion"][emotion]
        suggestion = suggestions.get(emotion, "")

        # -----------------------------
        # Save Screenshot
        # -----------------------------
        current = time.time()

        if confidence > 80 and (current - last_saved) > 5:

            image_name = f"{emotion}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"

            cv2.imwrite(
                os.path.join(folder, image_name),
                frame
            )

            last_saved = current

        # -----------------------------
        # Save CSV
        # -----------------------------
        now = datetime.now()

        with open(filename, "a", newline="") as file:

            writer = csv.writer(file)

            writer.writerow([
                now.strftime("%d-%m-%Y"),
                now.strftime("%H:%M:%S"),
                emotion,
                f"{confidence:.2f}"
            ])

        # -----------------------------
        # Face Rectangle
        # -----------------------------
        region = result["region"]

        x = region["x"]
        y = region["y"]
        w = region["w"]
        h = region["h"]

        cv2.rectangle(
            frame,
            (x, y),
            (x + w, y + h),
            (0, 255, 0),
            2
        )

        # -----------------------------
        # Emotion Text
        # -----------------------------
        text = f"{emotion.upper()} ({confidence:.2f}%)"

        cv2.putText(
            frame,
            text,
            (x, y - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2
        )

        # -----------------------------
        # Suggestion
        # -----------------------------
        cv2.putText(
            frame,
            suggestion,
            (20, 460),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 0),
            2
        )

    except Exception as e:
        print(e)

    # -----------------------------
    # Date & Time
    # -----------------------------
    current_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

    cv2.putText(
        frame,
        current_time,
        (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2
    )

    # -----------------------------
    # Show Window
    # -----------------------------
    cv2.imshow("AI Emotion Detection System", frame)

    # Quit
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# -----------------------------
# Release
# -----------------------------
cap.release()
cv2.destroyAllWindows()