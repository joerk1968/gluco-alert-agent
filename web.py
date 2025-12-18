# web.py - MINIMAL WORKING VERSION FOR RENDER
from flask import Flask
import os
import time
import threading

app = Flask(__name__)

def continuous_monitoring():
    """Simple monitoring that prints to logs every 5 minutes"""
    while True:
        print("✅ GlucoAlert AI: Healthy - monitoring active")
        time.sleep(300)  # 5 minutes

@app.route('/')
def health():
    return {
        "status": "GlucoAlert AI Running",
        "message": "System healthy - ready for deployment",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }

@app.route('/test')
def test():
    return {"message": "Test endpoint working - system is operational"}

if __name__ == "__main__":
    # Start monitoring thread
    threading.Thread(target=continuous_monitoring, daemon=True).start()
    
    # Get port from environment or use default
    port = int(os.environ.get("PORT", 10000))
    print(f"🚀 Starting GlucoAlert AI on port {port}")
    app.run(host="0.0.0.0", port=port)
