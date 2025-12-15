# main.py
import time
import schedule
from datetime import datetime
from glucose_reader import read_glucose_level
from llm_advisor import get_glucose_advice
from whatsapp_sender import send_whatsapp_alert
from sms_sender import send_glucose_alert
from config import HYPO_THRESHOLD, HYPER_THRESHOLD

def check_and_alert():
    """Read glucose, get LLM advice, send alert if out of range."""
    try:
        data = read_glucose_level()
        glucose = data["glucose"]
        timestamp = data["timestamp"]
        trend = data.get("trend", "stable")

        print(f"[{datetime.now().strftime('%H:%M:%S')}] Glucose: {glucose} mg/dL ({trend})")

        # Only alert if out of safe range
        if glucose <= HYPO_THRESHOLD or glucose >= HYPER_THRESHOLD:
            print("⚠️ Alert triggered!")

            # Get AI advice
            advice = get_glucose_advice(
                glucose_level=glucose,
                trend=trend,
                context="automated monitoring"
            )
            print(f"💡 Advice: {advice[:60]}...")

            # ✅ Try WhatsApp first (best for Lebanon)
            result = send_whatsapp_alert(glucose, timestamp, advice)
            print(f"📲 WhatsApp: {result}")

            # ❌ Fallback to SMS if WhatsApp fails
            if "❌" in result:
                print("🔁 Fallback to SMS...")
                result = send_glucose_alert(glucose, timestamp, advice)
                print(f"📱 SMS: {result}")

        else:
            print("✅ Glucose in normal range — no alert.")

    except Exception as e:
        print(f"🚨 Error in check_and_alert: {e}")

def run_scheduler():
    """Run scheduled checks (e.g., 07:30, 12:00, 18:30, 22:00)."""
    # Default schedule (can be overridden by config or WhatsApp later)
    times = ["07:30", "12:00", "18:30", "22:00"]
    
    for t in times:
        schedule.every().day.at(t).do(check_and_alert)
        print(f"⏰ Scheduled check at {t}")

    print("\n✅ Scheduler started. Waiting for next check...")
    while True:
        schedule.run_pending()
        time.sleep(30)  # Check every 30 sec for due jobs

if __name__ == "__main__":
    try:
        print("🩺 GlucoAlert Agent v1.0 — WhatsApp + LLM + Fallback")
        print("="*60)
        run_scheduler()
    except KeyboardInterrupt:
        print("\n🛑 Stopped by user.")