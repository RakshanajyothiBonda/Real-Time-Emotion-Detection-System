
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
    print("Error: Cannot open webcam.")
    print("Check camera permissions or try changing camera index 0 to 1.")
    cap.release()
    raise SystemExit

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
os.makedirs(folder, exist_ok=True)

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

window_name = "AI Emotion Detection System"

# -----------------------------
# Create Webcam Window
# -----------------------------
cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

print("Camera started successfully.")
print("Press 'q' to quit.")

# -----------------------------
# Main Loop
# -----------------------------
try:
    while True:

        # Read webcam frame
        ret, frame = cap.read()

        if not ret:
            print("Error: Could not read a frame from the webcam.")
            break

        # Flip image horizontally for a mirror effect
        frame = cv2.flip(frame, 1)

        # Get frame dimensions
        frame_height, frame_width = frame.shape[:2]

        # Default display values
        emotion = "Detecting..."
        confidence = 0.0
        suggestion = "Please look at the camera."

        # -----------------------------
        # Detect Emotion
        # -----------------------------
        try:
            results = DeepFace.analyze(
                frame,
                actions=["emotion"],
                enforce_detection=False,
                detector_backend="opencv",
                silent=True
            )

            if isinstance(results, list):
                result = results[0]
            else:
                result = results

            emotion = result.get("dominant_emotion", "neutral")
            emotion_scores = result.get("emotion", {})
            confidence = float(emotion_scores.get(emotion, 0.0))
            suggestion = suggestions.get(emotion, "")

            # -----------------------------
            # Save Screenshot
            # -----------------------------
            current = time.time()

            if confidence > 80 and (current - last_saved) > 5:
                image_name = (
                    f"{emotion}_"
                    f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                )

                image_path = os.path.join(folder, image_name)

                if cv2.imwrite(image_path, frame):
                    last_saved = current

            # -----------------------------
            # Save Emotion to CSV
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
            # Draw Face Rectangle
            # -----------------------------
            region = result.get("region", {})

            x = int(region.get("x", 0))
            y = int(region.get("y", 0))
            w = int(region.get("w", 0))
            h = int(region.get("h", 0))

            # Draw rectangle only if a valid face region exists
            if w > 0 and h > 0:
                cv2.rectangle(
                    frame,
                    (x, y),
                    (x + w, y + h),
                    (0, 255, 0),
                    2
                )

                # Keep emotion text inside the visible frame
                text_y = max(y - 10, 25)

                cv2.putText(
                    frame,
                    f"{emotion.upper()} ({confidence:.2f}%)",
                    (max(x, 10), text_y),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 0),
                    2
                )

        except Exception as e:
            print("Emotion detection error:", e)
            suggestion = "Unable to detect emotion. Please try again."

        # -----------------------------
        # Display Date and Time
        # -----------------------------
        current_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

        cv2.putText(
            frame,
            current_time,
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2
        )

        # -----------------------------
        # Display Emotion
        # -----------------------------
        cv2.putText(
            frame,
            f"Emotion: {emotion.upper()}",
            (10, 65),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )

        # -----------------------------
        # Display Suggestion
        # -----------------------------
        # Wrap long suggestions across multiple lines
        words = suggestion.split()
        lines = []
        current_line = ""

        for word in words:
            test_line = (
                current_line + " " + word
            ).strip()

            if cv2.getTextSize(
                test_line,
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                1
            )[0][0] < frame_width - 30:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

        suggestion_y = frame_height - 20

        for line in reversed(lines):
            cv2.putText(
                frame,
                line,
                (10, suggestion_y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 0),
                1
            )
            suggestion_y -= 25

        # -----------------------------
        # Show Webcam Window
        # -----------------------------
        cv2.imshow(window_name, frame)

        # Press q to quit
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

finally:
    # -----------------------------
    # Release Webcam and Close Window
    # -----------------------------
    cap.release()
    cv2.destroyAllWindows()
    print("Camera stopped. Resources released.")
