# backend/app/report_generator.py
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
from datetime import datetime

def create_pdf_report(inputs: dict, summary: dict, filename: str):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height-50, "Screen-Sense — Personalized Screen Time Report")

    c.setFont("Helvetica", 10)
    c.drawString(50, height-70, f"Generated on: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
    y = height - 100

    # User inputs
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "User Inputs:")
    y -= 18
    c.setFont("Helvetica", 10)
    for k in ['age', 'gender', 'device', 'avg_daily_screen_time_hr', 'educational_hr', 'recreational_hr']:
        if k in inputs:
            c.drawString(56, y, f"{k.replace('_',' ').title()}: {inputs[k]}")
            y -= 14

    y -= 8
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Summary & Recommendations:")
    y -= 18
    c.setFont("Helvetica", 10)

    # Score & recommendations from summary
    for k, v in summary.items():
        if k == "recommendations":
            c.drawString(56, y, "Recommendations:")
            y -= 14
            for idx, r in enumerate(v, 1):
                c.drawString(64, y, f"{idx}. {r}")
                y -= 12
                if y < 80:
                    c.showPage()
                    y = height - 50
        else:
            c.drawString(56, y, f"{k}: {v}")
            y -= 12
            if y < 80:
                c.showPage()
                y = height - 50

    c.save()
    return filename
