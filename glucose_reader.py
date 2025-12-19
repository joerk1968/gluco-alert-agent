# glucose_reader.py
import random
from datetime import datetime

def read_glucose_level():
    """Generate realistic synthetic glucose reading"""
    # Normal range with variation
    base_level = 95 + random.uniform(-10, 15)
    
    # 5% chance of abnormal reading
    if random.random() < 0.05:
        if random.random() < 0.5:
            return {"glucose": 62, "timestamp": datetime.now().isoformat(), "trend": "falling"}
        else:
            return {"glucose": 190, "timestamp": datetime.now().isoformat(), "trend": "rising"}
    
    return {
        "glucose": base_level,
        "timestamp": datetime.now().isoformat(),
        "trend": "stable"
    }