# glucose_reader.py
import random
from datetime import datetime

def read_glucose_level():
    """Generate realistic synthetic glucose reading"""
    # Simulate realistic glucose range with trends
    base_glucose = random.randint(80, 120)
    variation = random.randint(-10, 15)
    glucose = base_glucose + variation
    
    # Determine trend
    if variation > 5:
        trend = "rising"
    elif variation < -5:
        trend = "falling"
    else:
        trend = "stable"
    
    return {
        "glucose": glucose,
        "timestamp": datetime.now().isoformat(),
        "trend": trend
    }
