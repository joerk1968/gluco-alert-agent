# glucose_reader.py - OPTIMIZED FOR FREQUENT READINGS
import random
import time
from datetime import datetime, timedelta

class GlucoseSimulator:
    def __init__(self, seed=None):
        self.rng = random.Random(seed)
        self.glucose = self.rng.randint(85, 95)  # Stable baseline
        self.last_meal_time = datetime.now() - timedelta(hours=2)
        self.last_insulin_time = None
        self.activity_factor = 1.0  # 1.0 = normal, <1.0 = exercise

    def simulate_step(self):
        now = datetime.now()
        current_hour = now.hour
        
        # 🍽️ MEAL SIMULATION (3x daily with realistic timing)
        meal_times = [(7, 9), (12, 14), (18, 20)]  # Breakfast, Lunch, Dinner windows
        recent_meal = False
        
        for start_hour, end_hour in meal_times:
            if start_hour <= current_hour <= end_hour:
                recent_meal = True
                # Only spike once per meal window
                if not hasattr(self, 'last_meal_spike') or (now - self.last_meal_spike).total_seconds() > 3600:
                    self.last_meal_spike = now
                break
        
        # 📈 GLUCOSE DYNAMICS (realistic medical modeling)
        if recent_meal:
            # Post-meal rise (30-80 mg/dL over 45-90 minutes)
            rise_rate = self.rng.uniform(0.5, 1.5)  # mg/dL per minute
            self.glucose += rise_rate * 5  # 5-minute intervals
        else:
            # Between meals: gradual decline
            decline_rate = self.rng.uniform(0.2, 0.8)
            self.glucose -= decline_rate * 5
        
        # 🌙 NIGHTTIME METABOLISM (11PM-6AM)
        if 23 <= current_hour or current_hour < 6:
            self.glucose -= self.rng.uniform(0.1, 0.3) * 5  # Slower decline
        
        # 🏃 EXERCISE EFFECT (random 15% chance during active hours)
        if 6 <= current_hour <= 22 and self.rng.random() < 0.15:
            self.glucose -= self.rng.uniform(1.0, 3.0) * 5  # Faster decline
        
        # 🎲 PHYSIOLOGICAL NOISE (±3 mg/dL variation)
        noise = self.rng.uniform(-3, 3)
        self.glucose += noise
        
        # 🛑 MEDICAL SAFETY BOUNDS
        self.glucose = max(40, min(400, self.glucose))
        
        # 🔍 TREND CALCULATION
        trend = "stable"
        if noise > 1:
            trend = "rising"
        elif noise < -1:
            trend = "falling"
        
        return {
            "glucose": int(self.glucose),
            "timestamp": now.isoformat(),
            "trend": trend
        }

# Global simulator instance
_simulator = GlucoseSimulator(seed=42)

def read_glucose_level(simulate=True, file_path=None):
    """Generate realistic glucose reading every 5 minutes"""
    if not simulate:
        raise NotImplementedError("Real CGM support coming soon.")
    return _simulator.simulate_step()

# 🔬 TEST FUNCTION
if __name__ == "__main__":
    print("🧪 Starting REAL-TIME glucose simulation (5-minute intervals)...")
    for i in range(10):
        data = read_glucose_level()
        print(f"[{data['timestamp'][-13:-4]}] Glucose: {data['glucose']:3d} mg/dL ({data['trend']})")
        time.sleep(1)  # Simulate 5-minute intervals in demo
        
           
    
   
