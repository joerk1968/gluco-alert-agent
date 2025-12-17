
# web.py - COMPLETELY CORRECTED VERSION
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import threading
import time
import schedule
from datetime import datetime, timezone
import os
from glucose_reader import read_glucose_level
from llm_advisor import get_glucose_advice
from whatsapp_sender import send_whatsapp_alert
from config import HYPO_THRESHOLD, HYPER_THRESHOLD

app = Flask(__name__)

def check_and_alert():
    """Check glucose and send alert ONLY if abnormal"""
    try:
        # Get current glucose reading
        data = read_glucose_level()
        glucose = data["glucose"]
        timestamp = data["timestamp"]
        trend = data["trend"]
        
        # Get current time in UTC
        now = datetime.now(timezone.utc)
        display_time = now.strftime("%H:%M")
        
        # Log reading
        print(f"[{display_time}] Glucose: {glucose} mg/dL ({trend})")
        
        # ONLY send alerts if glucose is abnormal
        if glucose <= HYPO_THRESHOLD or glucose >= HYPER_THRESHOLD:
            print(f"⚠️ ALERT TRIGGERED! Glucose: {glucose} mg/dL")
            
            # Get LLM advice (handle as string)
            advice = get_glucose_advice(glucose, trend, "automated monitoring")
            print(f"💡 Advice: {advice[:60]}...")
            
            # Send WhatsApp alert
            result = send_whatsapp_alert(glucose, timestamp, advice)
            print(f"📲 WhatsApp: {result}")
            
            # No SMS fallback needed unless WhatsApp fails
        else:
            print(f"✅ Normal glucose: {glucose} mg/dL - No alert sent")
            
    except Exception as e:
        print(f"🚨 Error in monitoring: {str(e)}")

def run_scheduler():
    """Run continuous monitoring every 5 minutes"""
    print("✅ Starting continuous glucose monitoring")
    print(f"⏰ Checking every 5 minutes (HYPO ≤{HYPO_THRESHOLD}, HYPER ≥{HYPER_THRESHOLD})")
    
    # Schedule checks every 5 minutes
    schedule.every(5).minutes.do(check_and_alert)
    
    # Run first check immediately on startup
    print("🚀 Running first check now...")
    check_and_alert()
    
    print("="*60)
    print("GlucoAlert AI: 24/7 Monitoring Active")
    print("="*60)
    
    while True:
        schedule.run_pending()
        time.sleep(30)  # Check every 30 seconds for pending jobs

@app.route('/')
def health():
    """Health check endpoint"""
    now = datetime.now(timezone.utc)
    next_run = schedule.next_run()
    return {
        "status": "GlucoAlert AI Running",
        "server_time_utc": now.strftime("%Y-%m-%d %H:%M:%S"),
        "monitoring_frequency": "Every 5 minutes",
        "thresholds": {
            "hypoglycemia": f"≤ {HYPO_THRESHOLD} mg/dL",
            "hyperglycemia": f"≥ {HYPER_THRESHOLD} mg/dL"
        },
        "next_check": next_run.strftime("%Y-%m-%d %H:%M:%S") if next_run else "Starting soon"
    }

@app.route('/force-alert')
def force_alert():
    """Force alert for testing (uses REAL simulated value)"""
    print("🚨 MANUAL ALERT TRIGGERED!")
    
    # Get REAL simulated glucose value (not hardcoded)
    data = read_glucose_level()
    glucose = data["glucose"]
    timestamp = data["timestamp"]
    trend = data["trend"]
    
    # Get LLM advice
    advice = get_glucose_advice(glucose, trend, "manual test")
    print(f"💡 Generated advice for {glucose} mg/dL: {advice}")
    
    # Send alert
    result = send_whatsapp_alert(glucose, timestamp, advice)
    print(f"📲 WhatsApp: {result}")
    
    return {
        "status": "Manual alert triggered successfully",
        "glucose_level": glucose,
        "trend": trend,
        "timestamp": timestamp,
        "advice": advice,
        "whatsapp_result": result
    }

@app.route('/whatsapp-webhook', methods=['POST'])
def whatsapp_webhook():
    """Handle incoming WhatsApp messages"""
    try:
        message_body = request.values.get('Body', '').lower()
        print(f"📱 Incoming WhatsApp message: '{message_body}'")
        
        if "status" in message_body:
            response_text = "🟢 GlucoAlert AI: System HEALTHY\n⏰ Checking every 5 minutes\n🩺 Ready for alerts"
        elif "help" in message_body:
            response_text = "💡 I monitor glucose levels and send alerts when needed. Reply 'status' for system health."
        else:
            response_text = "✅ System active. Send 'status' for details."
        
        resp = MessagingResponse()
        resp.message(response_text)
        return str(resp)
    except Exception as e:
        print(f"❌ Webhook error: {str(e)}")
        return "Error processing request", 500

# Start scheduler in background thread
threading.Thread(target=run_scheduler, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Render's default port is 10000
    app.run(host="0.0.0.0", port=port)
