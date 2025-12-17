# glucose_reader.py - REALISTIC SYNTHETIC DATA GENERATOR
import random
from datetime import datetime, timedelta, timezone
import time

class GlucoseSimulator:
    def __init__(self):
        """Initialize with dynamic values for realistic simulation"""
        self.rng = random.Random(int(time.time()))  # Unique seed each run
        self.base_glucose = self.rng.uniform(85, 105)  # Baseline fasting glucose
        self.last_glucose = self.base_glucose
        self.last_meal_time = None
        self.current_trend = "stable"
        
    def simulate_reading(self):
        """Generate realistic glucose reading with physiological patterns"""
        now = datetime.now(timezone.utc)
        hour = now.hour
        
        # 🌅 Dawn phenomenon (3-8 AM natural rise)
        dawn_effect = 0
        if 3 <= hour <= 8:
            dawn_factor = (hour - 3) / 5  # 0 to 1 over 5 hours
            dawn_effect = 15 * dawn_factor
            
        # 🍽️ Meal effects (simulate 3 main meals)
        meal_effect = 0
        current_time = now.time()
        
        # Breakfast effect (7-10 AM)
        if 7 <= hour <= 10:
            if not self.last_meal_time or (now - self.last_meal_time).total_seconds() > 7200:  # 2 hours since last meal
                self.last_meal_time = now
                meal_effect = self.rng.uniform(30, 60)  # Post-breakfast spike
                
        # Lunch effect (12-2 PM)
        elif 12 <= hour <= 14:
            if not self.last_meal_time or (now - self.last_meal_time).total_seconds() > 7200:
                self.last_meal_time = now
                meal_effect = self.rng.uniform(40, 80)  # Post-lunch spike
                
        # Dinner effect (6-9 PM)
        elif 18 <= hour <= 21:
            if not self.last_meal_time or (now - self.last_meal_time).total_seconds() > 7200:
                self.last_meal_time = now
                meal_effect = self.rng.uniform(35, 70)  # Post-dinner spike
        
        # 🌙 Nighttime decline (10 PM - 6 AM)
        nighttime_effect = 0
        if 22 <= hour or hour < 6:
            nighttime_effect = -self.rng.uniform(0.5, 1.5) * 5  # Gradual decline
        
        # 🎲 Physiological noise (real sensor variation)
        noise = self.rng.uniform(-3, 3)
        
        # 📈 Calculate current glucose
        current_glucose = (
            self.base_glucose +
            dawn_effect +
            meal_effect +
            nighttime_effect +
            noise
        )
        
        # 🛑 Medical safety bounds
        current_glucose = max(40, min(350, current_glucose))
        
        # 🔍 Determine trend (based on change from last reading)
        if current_glucose > self.last_glucose + 2:
            trend = "rising"
        elif current_glucose < self.last_glucose - 2:
            trend = "falling"
        else:
            trend = "stable"
        
        # 📊 Update state for next reading
        self.last_glucose = current_glucose
        
        return {
            "glucose": round(current_glucose, 1),
            "timestamp": now.isoformat(),
            "trend": trend
        }

# Global simulator instance
_simulator = GlucoseSimulator()

def read_glucose_level(simulate=True, file_path=None):
    """Get current glucose reading"""
    if not simulate:
        raise NotImplementedError("Real CGM support coming soon")
    return _simulator.simulate_reading()

# 🔬 Test function
if __name__ == "__main__":
    print("🧪 Testing realistic glucose simulation...")
    for i in range(10):
        data = read_glucose_level()
        print(f"[{data['timestamp'][-13:-4]}] Glucose: {data['glucose']} mg/dL ({data['trend']})")
        time.sleep(1)  # Simulate 5-minute intervals
