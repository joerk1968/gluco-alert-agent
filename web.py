# web.py
from datetime import datetime, timezone
from datetime import datetime, timezone
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
    """Run checks at 4 fixed times daily with proper error handling."""
    times = ["7:30","9:30","12:00", "18:30", "22:00"]  # Linux-compatible format (no leading zero)
    successful_times = []
    
    for t in times:
        try:
            schedule.every().day.at(t).do(check_and_alert)
            successful_times.append(t)
            print(f"✅ Successfully scheduled: {t}")
        except Exception as e:
            print(f"❌ Failed to schedule {t}: {str(e)}")
    
    if successful_times:
        print(f"✅ Scheduler active with {len(successful_times)} times: {', '.join(successful_times)}")
    else:
        print("❌ No times were successfully scheduled!")
    
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
@app.route('/force-alert')
def force_alert():
    """Trigger an immediate glucose alert for testing/demo purposes."""
    print("🚨 MANUAL ALERT TRIGGERED!")
    
    # Generate a synthetic low glucose reading for testing
    test_data = {
        "glucose": 65,  # Simulate hypoglycemia
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "trend": "falling"
    }
    
    # Get LLM advice
    advice = get_glucose_advice(
        glucose_level=test_data["glucose"],
        trend=test_data["trend"],
        context="manual test alert"
    )
    print(f"💡 Generated advice: {advice}")
    
    # Send WhatsApp alert
    whatsapp_result = send_whatsapp_alert(
        glucose_level=test_data["glucose"],
        timestamp=test_data["timestamp"],
        advice=advice
    )
    print(f"📲 WhatsApp result: {whatsapp_result}")
    
    # Fallback to SMS if WhatsApp fails
    sms_result = ""
    if "❌" in whatsapp_result:
        print("🔁 Falling back to SMS...")
        sms_result = send_glucose_alert(
            glucose_level=test_data["glucose"],
            timestamp=test_data["timestamp"],
            advice=advice
        )
        print(f"📱 SMS result: {sms_result}")
    
    return {
        "status": "Manual alert triggered successfully",
        "glucose_level": test_data["glucose"],
        "timestamp": test_data["timestamp"],
        "advice": advice,
        "whatsapp_result": whatsapp_result,
        "sms_result": sms_result if sms_result else "Not used"
    }
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
