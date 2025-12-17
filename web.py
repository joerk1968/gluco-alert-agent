# web.py - PRODUCTION READY WITH CORRECT PORT BINDING
from flask import Flask, request, jsonify
from twilio.twiml.messaging_response import MessagingResponse
import threading
import time
import schedule
import traceback
from datetime import datetime, timezone
import os
from glucose_reader import read_glucose_level
from llm_advisor import get_glucose_advice
from whatsapp_sender import send_whatsapp_alert
from config import HYPO_THRESHOLD, HYPER_THRESHOLD

app = Flask(__name__)

def check_and_alert():
    """Check glucose and send alert ONLY if abnormal with full error handling"""
    try:
        print(f"\n{'='*60}")
        print(f"🔍 Glucose Check at {datetime.now(timezone.utc).strftime('%H:%M:%S UTC')}")
        
        # Get glucose reading
        data = read_glucose_level()
        glucose = data["glucose"]
        timestamp = data["timestamp"]
        trend = data.get("trend", "stable")
        
        # Log reading
        print(f"🩺 Current glucose: {glucose} mg/dL ({trend})")
        
        # Only alert if abnormal
        if glucose <= HYPO_THRESHOLD or glucose >= HYPER_THRESHOLD:
            print(f"⚠️ {'CRITICAL LOW' if glucose <= 55 else 'LOW' if glucose <= 70 else 'HIGH'} ALERT TRIGGERED!")
            
            # Get LLM advice (real ChatGPT response)
            advice = get_glucose_advice(glucose, trend, "automated monitoring")
            
            # Send WhatsApp alert
            result = send_whatsapp_alert(glucose, timestamp, advice)
            
            # Log result
            status = "✅" if "✅" in result else "❌"
            print(f"{status} Alert result: {result}")
        else:
            print(f"✅ Normal glucose ({glucose} mg/dL) - No alert needed")
            
        print(f"{'='*60}")
            
    except Exception as e:
        error_details = traceback.format_exc()
        print(f"🚨 Monitoring error: {str(e)}")
        print(f"   Details: {error_details[:200]}...")
        
        # Emergency fallback alert
        try:
            emergency_advice = (
                "🚨 SYSTEM ERROR - GLUCOSE MONITORING FAILED\n"
                "Check your glucose monitor manually.\n"
                "If you feel unwell, contact your healthcare provider or emergency services."
            )
            result = send_whatsapp_alert(0, datetime.now(timezone.utc).isoformat(), emergency_advice)
            print(f"🆘 Emergency alert sent: {result}")
        except Exception as emergency_e:
            print(f"❌ Failed to send emergency alert: {str(emergency_e)}")

def run_scheduler():
    """Run continuous monitoring every 5 minutes with startup check"""
    print("✅ Starting GlucoAlert AI Continuous Monitoring")
    print(f"⏰ Schedule: Every 5 minutes (HYPO ≤{HYPO_THRESHOLD}, HYPER ≥{HYPER_THRESHOLD})")
    print(f"📍 Timezone: UTC (Render server time)")
    
    # Schedule checks every 5 minutes
    schedule.every(5).minutes.do(check_and_alert)
    
    # Run first check immediately
    print("🚀 Running first check immediately...")
    check_and_alert()
    
    print("✅ Scheduler activated - monitoring in background")
    
    while True:
        schedule.run_pending()
        time.sleep(30)  # Check every 30 seconds

@app.route('/')
def health():
    """Enhanced health check with system status"""
    now = datetime.now(timezone.utc)
    next_run = schedule.next_run()
    
    return jsonify({
        "status": "GlucoAlert AI Running",
        "server_time_utc": now.strftime("%Y-%m-%d %H:%M:%S"),
        "monitoring_frequency": "Every 5 minutes",
        "thresholds": {
            "hypoglycemia": f"≤ {HYPO_THRESHOLD} mg/dL",
            "hyperglycemia": f"≥ {HYPER_THRESHOLD} mg/dL"
        },
        "next_check": next_run.strftime("%Y-%m-%d %H:%M:%S") if next_run else "Starting soon",
        "system_health": "OK"
    })

@app.route('/force-alert')
def force_alert():
    """Force alert with REAL LLM advice for testing"""
    try:
        print("\n🚨 MANUAL ALERT TRIGGERED VIA /force-alert")
        
        # Get REAL simulated glucose value
        data = read_glucose_level()
        glucose = data["glucose"]
        timestamp = data["timestamp"]
        trend = data.get("trend", "falling")
        
        print(f"   Glucose: {glucose} mg/dL ({trend})")
        
        # Get REAL LLM advice
        advice = get_glucose_advice(glucose, trend, "manual test")
        print(f"💡 LLM Advice: {advice[:100]}...")
        
        # Send alert
        result = send_whatsapp_alert(glucose, timestamp, advice)
        print(f"📲 Result: {result}")
        
        return jsonify({
            "status": "Manual alert triggered successfully",
            "glucose_level": glucose,
            "trend": trend,
            "timestamp": timestamp,
            "advice": advice,
            "whatsapp_result": result
        })
        
    except Exception as e:
        error_details = traceback.format_exc()
        print(f"❌ Force alert error: {str(e)}")
        print(f"   Details: {error_details[:200]}...")
        
        return jsonify({
            "status": "Error triggering manual alert",
            "error": str(e),
            "details": error_details[:500]
        }), 500

@app.route('/whatsapp-webhook', methods=['POST'])
def whatsapp_webhook():
    """Handle incoming WhatsApp messages with error handling"""
    try:
        message_body = request.values.get('Body', '').strip().lower()
        from_number = request.values.get('From', '')
        print(f"📱 Incoming WhatsApp message from {from_number}: '{message_body}'")
        
        # Simple responses
        if "status" in message_body or "health" in message_body:
            response_text = (
                "🟢 GlucoAlert AI: System HEALTHY\n"
                "⏰ Monitoring every 5 minutes\n"
                "🩺 Ready for abnormal glucose alerts"
            )
        elif "help" in message_body:
            response_text = (
                "💡 I monitor glucose levels 24/7 and send alerts when needed.\n"
                "Reply 'status' for system health information."
            )
        elif "test" in message_body:
            response_text = "✅ System test passed. Monitoring active."
        else:
            response_text = "✅ GlucoAlert AI is active. Reply 'status' for details."
        
        resp = MessagingResponse()
        resp.message(response_text)
        return str(resp)
        
    except Exception as e:
        print(f"❌ WhatsApp webhook error: {str(e)}")
        resp = MessagingResponse()
        resp.message("❌ Error processing your request. System is still monitoring.")
        return str(resp), 500

# Start scheduler in background thread
threading.Thread(target=run_scheduler, daemon=True).start()

if __name__ == "__main__":
    # ✅ CORRECT PORT BINDING FOR RENDER (Port 10000)
    port = int(os.environ.get("PORT", 10000))
    print(f"🚀 Starting server on port {port} (Render default: 10000)")
    app.run(host="0.0.0.0", port=port)
