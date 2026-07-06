import pandas as pd
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime

# Read CSV
df = pd.read_csv("emotion_log.csv")

styles = getSampleStyleSheet()

filename = f"reports/Emotion_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

import os
os.makedirs("reports", exist_ok=True)

doc = SimpleDocTemplate(filename)

story = []

story.append(Paragraph("<b>AI Emotion Detection Report</b>", styles["Title"]))

story.append(
    Paragraph(
        f"Generated on: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}",
        styles["Normal"]
    )
)

story.append(Paragraph("<br/><br/>", styles["Normal"]))

emotion_count = df["Emotion"].value_counts()

story.append(Paragraph("<b>Emotion Statistics</b>", styles["Heading2"]))

for emotion, count in emotion_count.items():
    story.append(
        Paragraph(f"{emotion} : {count}", styles["Normal"])
    )

story.append(Paragraph("<br/>", styles["Normal"]))

story.append(
    Paragraph(
        f"<b>Total Records:</b> {len(df)}",
        styles["Normal"]
    )
)

story.append(
    Paragraph(
        f"<b>Most Frequent Emotion:</b> {emotion_count.idxmax()}",
        styles["Normal"]
    )
)

doc.build(story)

print("PDF Report Generated Successfully!")
print(filename)