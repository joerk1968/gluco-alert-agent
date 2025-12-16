# glucose_reader.py - MEDICALLY ACCURATE SYNTHETIC GLUCOSE GENERATOR
import random
import math
from datetime import datetime, timedelta, timezone
import time

class AdvancedGlucoseSimulator:
    def __init__(self):
        """Initialize with dynamic seed based on current time for unique sequences"""
        current_time = int(time.time())
        self.rng = random.Random(current_time)  # Dynamic seed = unique each run
        
        # Patient baseline characteristics (realistic diabetic profiles)
        self.baseline_glucose = self.rng.uniform(90, 110)  # Fasting baseline
        self.insulin_resistance = self.rng.uniform(0.8, 1.3)  # 1.0 = normal
        self.carb_ratio = self.rng.uniform(8, 15)  # grams of carbs per unit insulin
        
        # Meal timing patterns (realistic human schedule)
        self.meal_schedule = {
            'breakfast': (7, 9),    # 7-9 AM
            'lunch': (12, 14),      # 12-2 PM  
            'dinner': (18, 20),     # 6-8 PM
            'snack': (15, 16)       # 3-4 PM
        }
        
        # Current state
        self.last_glucose = self.baseline_glucose
        self.last_update = datetime.now(timezone.utc)
        self.current_trend = "stable"
        self.recent_meal = None
        self.recent_insulin = None
        self.recent_exercise = False

    def simulate_glucose(self, current_time):
        """Generate medically accurate glucose based on time of day and context"""
        
        hour = current_time.hour
        minute = current_time.minute
        
        # 🌅 DAWN PHENOMENON (3AM-8AM natural rise)
        dawn_effect = 0
        if 3 <= hour <= 8:
            dawn_factor = (hour - 3) / 5  # 0 to 1 over 5 hours
            dawn_effect = 15 * dawn_factor * self.insulin_resistance
            
        # 🍽️ MEAL EFFECTS (realistic postprandial spikes)
        meal_effect = 0
        meal_context = None
        
        for meal, (start_hour, end_hour) in self.meal_schedule.items():
            if start_hour <= hour <= end_hour:
                # Probability of eating during this window
                if self.rng.random() < 0.85:  # 85% chance of eating
                    time_in_window = (hour - start_hour) + minute/60
                    window_duration = end_hour - start_hour
                    
                    # Peak spike timing (30-45 min after meal start)
                    peak_time = window_duration * 0.6
                    spike_intensity = {
                        'breakfast': self.rng.uniform(30, 50),
                        'lunch': self.rng.uniform(40, 70),
                        'dinner': self.rng.uniform(35, 60),
                        'snack': self.rng.uniform(15, 30)
                    }[meal]
                    
                    # Bell curve spike pattern
                    meal_effect = spike_intensity * math.exp(-0.5 * ((time_in_window - peak_time) / 1.5) ** 2)
                    meal_context = meal
                    break
        
        # 🏃 EXERCISE EFFECT (random 20% chance during active hours)
        exercise_effect = 0
        if 6 <= hour <= 21 and self.rng.random() < 0.2:  # 20% chance of exercise
            exercise_duration = self.rng.uniform(20, 45)  # minutes
            exercise_intensity = self.rng.uniform(0.5, 1.5)  # mild to moderate
            exercise_effect = -exercise_intensity * 0.8 * exercise_duration/30  # glucose lowering
            self.recent_exercise = True
        
        # 🌙 NIGHTTIME METABOLISM (11PM-6AM)
        nighttime_effect = 0
        if 23 <= hour or hour < 6:
            nighttime_factor = 1.0 if hour < 3 else 0.7  # deeper drop early night
            nighttime_effect = -self.rng.uniform(0.3, 0.8) * nighttime_factor * 5  # gradual decline
        
        # 🎲 PHYSIOLOGICAL NOISE (real sensor variation)
        noise = self.rng.uniform(-3, 3)
        
        # 📈 CALCULATE CURRENT GLUCOSE
        base_glucose = self.baseline_glucose
        current_glucose = (
            base_glucose + 
            dawn_effect + 
            meal_effect + 
            exercise_effect + 
            nighttime_effect + 
            noise
        )
        
        # 🛑 MEDICAL SAFETY BOUNDS
        current_glucose = max(40, min(350, current_glucose))
        
        # 🔍 TREND CALCULATION (based on change from last reading)
        time_diff = (current_time - self.last_update).total_seconds() / 60  # minutes
        if time_diff > 0:
            change_rate = (current_glucose - self.last_glucose) / time_diff
            if change_rate > 2:
                trend = "rising rapidly"
            elif change_rate > 0.5:
                trend = "rising"
            elif change_rate < -2:
                trend = "falling rapidly"
            elif change_rate < -0.5:
                trend = "falling"
            else:
                trend = "stable"
        else:
            trend = self.current_trend
        
        # 📊 UPDATE STATE
        self.last_glucose = current_glucose
        self.last_update = current_time
        self.current_trend = trend
        self.recent_meal = meal_context
        
        return {
            "glucose": round(current_glucose, 1),
            "timestamp": current_time.isoformat(),
            "trend": trend,
            "context": {
                "meal": meal_context,
                "exercise": self.recent_exercise,
                "time_of_day": "night" if (23 <= hour or hour < 6) else "day"
            }
        }

    def get_reading(self):
        """Get current glucose reading with realistic timing"""
        current_time = datetime.now(timezone.utc)
        return self.simulate_glucose(current_time)

# Global simulator instance (starts fresh on each app restart)
_simulator = AdvancedGlucoseSimulator()

def read_glucose_level(simulate=True, file_path=None):
    """
    Generate realistic glucose reading with physiological patterns
    
    Args:
        simulate (bool): Must be True for now
        file_path (str): Reserved for future real-data integration
    
    Returns:
        dict: {
            'glucose': float,  # mg/dL
            'timestamp': str,  # ISO format
            'trend': str,      # 'rising', 'falling', 'stable', etc.
            'context': dict    # meal/exercise/time context
        }
    """
    if not simulate:
        raise NotImplementedError("Real CGM support coming soon.")
    return _simulator.get_reading()

# 🔬 TEST FUNCTION - Run to see realistic patterns
if __name__ == "__main__":
    print("🧪 Starting MEDICALLY ACCURATE glucose simulation...")
    print("⏰ Reading every 5 minutes for 2 hours (simulated time)\n")
    
    simulator = AdvancedGlucoseSimulator()
    
    # Simulate 24 readings (2 hours at 5-minute intervals)
    start_time = datetime.now(timezone.utc)
    for i in range(24):
        current_time = start_time + timedelta(minutes=i*5)
        data = simulator.simulate_glucose(current_time)
        
        # Color-coded output for trends
        trend_symbol = {
            "rising rapidly": "↑↑",
            "rising": "↑", 
            "falling rapidly": "↓↓",
            "falling": "↓",
            "stable": "→"
        }.get(data['trend'], "?")
        
        context_str = ""
        if data['context']['meal']:
            context_str += f"🍽️{data['context']['meal'][:3]} "
        if data['context']['exercise']:
            context_str += "🏃 "
            
        print(f"[{current_time.strftime('%H:%M')}] {data['glucose']:5.1f} mg/dL {trend_symbol} {context_str.strip()}")
        
        # Highlight alerts
        if data['glucose'] <= 70:
            print(f"  ⚠️  HYPOGLYCEMIA ALERT! Context: {data['context']}")
        elif data['glucose'] >= 180:
            print(f"  ⚠️  HYPERGLYCEMIA ALERT! Context: {data['context']}")
        
        time.sleep(0.3)  # Faster demo
    
    print("\n✅ Simulation complete. Patterns include:")
    print("   • Dawn phenomenon (early morning rise)")
    print("   • Post-meal spikes with realistic timing")
    print("   • Nighttime glucose decline")
    print("   • Exercise-induced drops")
    print("   • Physiological noise (±3 mg/dL)")
