import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

import cv2
from fer.fer import FER

# Initialize emotion detector
detector = FER(mtcnn=True)

# Open webcam
cap = cv2.VideoCapture(0)

print("Press 'q' to quit.")

while True:
    ret, frame = cap.read()

    if not ret:
        break

    # Detect emotions
    results = detector.detect_emotions(frame)

    # Loop through each detected face
    for face in results:
        x, y, w, h = face["box"]

        emotions = face["emotions"]
        emotion = max(emotions, key=emotions.get)
        score = emotions[emotion]

        # Draw rectangle around face
        cv2.rectangle(frame, (x, y), (x + w, y + h),
                      (0, 255, 0), 2)

        # Display emotion
        cv2.putText(frame,
                    f"{emotion} ({score:.2f})",
                    (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 255, 0),
                    2)

    cv2.imshow("Real-Time Emotion Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()