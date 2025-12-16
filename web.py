# web.py
from datetime import datetime, timezone
import pytz
from flask import Flask
import threading
import time
import schedule
from datetime import datetime
from glucose_reader import read_glucose_level
from llm_advisor import get_glucose_advice
from whatsapp_sender import send_whatsapp_alert
from sms_sender import send_glucose_alert
from config import HYPO_THRESHOLD, HYPER_THRESHOLD

app = Flask(__name__)

def check_and_alert():
    # (same as before — copy from main.py)
    try:
        data = read_glucose_level()
        glucose = data["glucose"]
        timestamp = data["timestamp"]
        trend = data.get("trend", "stable")
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Glucose: {glucose} mg/dL")

        if glucose <= HYPO_THRESHOLD or glucose >= HYPER_THRESHOLD:
            advice = get_glucose_advice(glucose, trend, "cloud agent")
            result = send_whatsapp_alert(glucose, timestamp, advice)
            if "❌" in result:
                send_glucose_alert(glucose, timestamp, advice)
    except Exception as e:
        print(f"Error: {e}")

def run_scheduler():
    # Schedule 4x/day (adjust as needed)
    for t in ["7:30","8:30", "12:00", "18:30","20:00", "22:00"]:
        schedule.every().day.at(t).do(check_and_alert)
    while True:
        schedule.run_pending()
        time.sleep(60)

@app.route('/')
def health():
    # Get current time in UTC (Render's default timezone)
    now = datetime.now(timezone.utc)
    return {
        "status": "GlucoAlert Agent Running",
        "server_time_utc": now.strftime("%Y-%m-%d %H:%M:%S"),
        "scheduled_times": ["7:30", "12:00", "18:30", "22:00"],
        "timezone": "UTC"
    }

# Start scheduler in background
threading.Thread(target=run_scheduler, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
