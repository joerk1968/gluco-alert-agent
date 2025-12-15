# glucose_reader.py
import random
import time
from datetime import datetime, timedelta

class GlucoseSimulator:
    def __init__(self, seed=None):
        self.rng = random.Random(seed)
        # Initial glucose: normal fasting range
        self.glucose = self.rng.randint(85, 95)
        self.last_meal_time = datetime.now() - timedelta(hours=2)  # Last "meal" 2h ago

    def simulate_step(self):
        now = datetime.now()
        
        # 🍽️ Simulate meals 3x/day: 8AM, 12PM, 6PM ±30min
        meal_hours = [8, 12, 18]
        current_hour = now.hour
        minutes = now.minute
        
        recent_meal = False
        for h in meal_hours:
            if abs(current_hour - h) == 0 and 0 <= minutes <= 45:
                recent_meal = True
                # Ensure we don't spike repeatedly in same window
                if (now - self.last_meal_time).total_seconds() > 30 * 60:  # 30 min gap
                    self.last_meal_time = now
                break
        
        # 📈 Glucose dynamics
        if recent_meal:
            # Post-meal: rise up to +60 mg/dL over 30–60 min
            rise = self.rng.randint(1, 3)  # +1 to +3 per step
            self.glucose += rise
        else:
            # Between meals: slow decline or stability
            drift = self.rng.choice([-2, -1, 0, 0, 1])  # slight downward bias
            self.glucose += drift
        
        # 🌙 Night (11PM–6AM): slower metabolism → smaller swings
        if 23 <= current_hour or current_hour < 6:
            self.glucose += self.rng.choice([-1, 0, 0, 1])
        
        # 🎲 Add physiological noise (±3 mg/dL)
        noise = self.rng.randint(-3, 3)
        self.glucose += noise

        # 🛑 Physiological bounds (clamp to realistic range)
        self.glucose = max(40, min(400, self.glucose))

        return {
            "glucose": int(self.glucose),
            "timestamp": now.isoformat(),
            "trend": "rising" if noise > 0 else "falling" if noise < 0 else "stable"
        }

# Global simulator instance (persists state between calls)
_simulator = GlucoseSimulator(seed=42)  # Reproducible for testing

def read_glucose_level(simulate=True, file_path=None):
    """
    Returns simulated glucose level with realistic dynamics.
    
    Args:
        simulate (bool): Must be True for now.
        file_path (str): Reserved for future real-data integration.
    
    Returns:
        dict: {'glucose': int, 'timestamp': str, 'trend': str}
    """
    if not simulate:
        raise NotImplementedError("Real CGM support coming soon.")
    return _simulator.simulate_step()

# 🔬 Test
if __name__ == "__main__":
    print("🧪 Starting realistic glucose simulation (5 readings, 5s apart)...")
    for i in range(5):
        data = read_glucose_level()
        print(f"[{data['timestamp'][-13:-4]}] Glucose: {data['glucose']:3d} mg/dL ({data['trend']})")
        time.sleep(1)  # Simulate 1-sec intervals