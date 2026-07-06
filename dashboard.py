import pandas as pd
import matplotlib.pyplot as plt

# Read CSV
df = pd.read_csv("emotion_log.csv")

# Check if data exists
if df.empty:
    print("No emotion data found.")
    exit()

# Count each emotion
emotion_count = df["Emotion"].value_counts()

print("\n========== Emotion Report ==========")
print(emotion_count)

print("\nMost Detected Emotion:", emotion_count.idxmax())
print("Total Records:", len(df))

# -------------------------
# Bar Chart
# -------------------------
plt.figure(figsize=(8,5))

emotion_count.plot(kind="bar")

plt.title("Emotion Detection Count")
plt.xlabel("Emotion")
plt.ylabel("Count")

plt.tight_layout()
plt.show()

# -------------------------
# Pie Chart
# -------------------------
plt.figure(figsize=(6,6))

emotion_count.plot(
    kind="pie",
    autopct="%1.1f%%"
)

plt.ylabel("")
plt.title("Emotion Distribution")

plt.tight_layout()
plt.show()