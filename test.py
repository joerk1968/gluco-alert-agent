# test_5_sms_with_llm.py
from glucose_reader import read_glucose_level
from llm_advisor import get_glucose_advice
from sms_sender import send_glucose_alert
import time

print("🧠📲 Sending 5 SMS with LLM advice (one every 10 seconds)...\n")

for i in range(1, 6):
    # 1. Read synthetic glucose
    data = read_glucose_level()
    glucose = data["glucose"]
    timestamp = data["timestamp"]
    trend = data.get("trend", "stable")
    
    # 2. Get LLM advice (even for normal values)
    advice = get_glucose_advice(
        glucose_level=glucose,
        trend=trend,
        context="automated test"
    )
    
    # 3. Send SMS with glucose + full LLM advice
    result = send_glucose_alert(
        glucose_level=glucose,
        timestamp=timestamp,
        advice=advice  # ← now includes AI advice
    )
    
    # 4. Display summary
    print(f"[{i}/5] Glucose: {glucose:3d} mg/dL | Trend: {trend}")
    print(f"   💡 Advice: {advice[:60]}...")
    print(f"   📲 {result}")
    
    # Wait 10 sec (skip after last)
    if i < 5:
        print("   ⏳ Waiting 10 seconds...\n")
        time.sleep(10)

print("\n✅ Done — 5 SMS with LLM advice sent.")