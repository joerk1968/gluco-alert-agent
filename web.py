# web.py - DEBUG VERSION TO SHOW ACTUAL ENVIRONMENT VARIABLES
from flask import Flask
import os
from datetime import datetime, timezone

app = Flask(__name__)

@app.route('/')
def health():
    return {
        "status": "GlucoAlert AI Debug Mode",
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        "message": "Debug mode active - check /debug-env for environment variables"
    }

@app.route('/debug-env')
def debug_env():
    """Show ALL environment variables available to the app"""
    print("🔍 DEBUGGING ENVIRONMENT VARIABLES...")
    
    # Get all environment variables
    all_env = dict(os.environ)
    
    # Filter for Twilio-related variables (case-insensitive)
    twilio_vars = {}
    for key, value in all_env.items():
        if "TWILIO" in key.upper() or "WHATSAPP" in key.upper() or "PHONE" in key.upper():
            twilio_vars[key] = value[:8] + "..." if value else "EMPTY"
    
    # Check for required variables (case-insensitive)
    required = ["TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN", "TWILIO_WHATSAPP_FROM", "PATIENT_WHATSAPP"]
    found_vars = {}
    
    for req in required:
        found = False
        for env_key in all_env.keys():
            if env_key.upper() == req.upper():
                found_vars[req] = all_env[env_key][:8] + "..." if all_env[env_key] else "EMPTY"
                found = True
                break
        if not found:
            found_vars[req] = "NOT FOUND"
    
    # Print to logs for debugging
    print("=== ALL ENVIRONMENT VARIABLES ===")
    for key in sorted(all_env.keys()):
        print(f"{key}: {all_env[key][:20]}...")
    print("================================")
    
    print("=== TWILIO-RELATED VARIABLES ===")
    for key, value in twilio_vars.items():
        print(f"{key}: {value}")
    print("================================")
    
    print("=== REQUIRED VARIABLES STATUS ===")
    for req, status in found_vars.items():
        print(f"{req}: {status}")
    print("================================")
    
    return {
        "status": "ENVIRONMENT DEBUG RESULTS",
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        "twilio_variables_found": twilio_vars,
        "required_variables_status": found_vars,
        "total_environment_variables": len(all_env),
        "debug_note": "Check Render logs for detailed environment variable dump"
    }

@app.route('/test-alert')
def test_alert():
    """Test alert with environment debugging"""
    print("🚨 TEST ALERT TRIGGERED IN DEBUG MODE")
    
    # Try to get credentials with case-insensitive search
    def get_env_var(name):
        for key, value in os.environ.items():
            if key.upper() == name.upper():
                return value
        return None
    
    account_sid = get_env_var("TWILIO_ACCOUNT_SID")
    auth_token = get_env_var("TWILIO_AUTH_TOKEN")
    whatsapp_from = get_env_var("TWILIO_WHATSAPP_FROM")
    patient_whatsapp = get_env_var("PATIENT_WHATSAPP")
    
    credential_status = {
        "TWILIO_ACCOUNT_SID": "FOUND" if account_sid else "MISSING",
        "TWILIO_AUTH_TOKEN": "FOUND" if auth_token else "MISSING", 
        "TWILIO_WHATSAPP_FROM": "FOUND" if whatsapp_from else "MISSING",
        "PATIENT_WHATSAPP": "FOUND" if patient_whatsapp else "MISSING"
    }
    
    print("=== CREDENTIAL CHECK RESULTS ===")
    for key, status in credential_status.items():
        print(f"{key}: {status}")
    print("================================")
    
    if not all([account_sid, auth_token, whatsapp_from, patient_whatsapp]):
        return {
            "status": "❌ TEST ALERT FAILED - MISSING CREDENTIALS",
            "credential_status": credential_status,
            "debug_action": "Check /debug-env endpoint and Render Environment tab",
            "fix_steps": [
                "1. Go to Render dashboard → Environment tab",
                "2. Verify ALL 4 variables are set EXACTLY as shown below",
                "3. Click 'Save Changes' to trigger rebuild",
                "4. Wait 2 minutes for redeployment"
            ],
            "required_variables": {
                "TWILIO_ACCOUNT_SID": "AC636f695a472e0c37cb2a02cafbb7579d",
                "TWILIO_AUTH_TOKEN": "1fbafadebe35dd911f8d48ab51f8a7f7", 
                "TWILIO_WHATSAPP_FROM": "whatsapp:+14155238886",
                "PATIENT_WHATSAPP": "whatsapp:+9613929206"
            }
        }, 500
    
    return {
        "status": "✅ CREDENTIALS FOUND - SYSTEM READY FOR ALERTS",
        "credential_status": credential_status,
        "next_step": "Remove debug code and redeploy production version"
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print(f"🚀 DEBUG MODE STARTED ON PORT {port}")
    print("🔍 Use /debug-env endpoint to diagnose environment issues")
    app.run(host="0.0.0.0", port=port)
