import logging
import json
from pathlib import Path
from dataclasses import dataclass
import numpy as np
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("OccupancyLearner")

@dataclass
class TimeWindow:
    start_hour: int
    end_hour: int
    probability: float

class OccupancyLearner:
    """Learns daily occupancy patterns from motion sensor history."""
    
    def __init__(self, data_file: str = None):
        self.data_file = data_file or str(Path(__file__).parent / "data" / "occupancy.json")
        self.motion_history = {} # room -> list of timestamps
        self.patterns = {} # room -> 24-hour array of probabilities
        
        Path(self.data_file).parent.mkdir(parents=True, exist_ok=True)
        self._load_data()

    def _load_data(self):
        if Path(self.data_file).exists():
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    self.motion_history = data.get('history', {})
                    self.patterns = data.get('patterns', {})
            except Exception as e:
                logger.error(f"Error loading occupancy data: {e}")

    def record_motion(self, room: str, timestamp: float) -> None:
        """Records a motion event in a room."""
        if room not in self.motion_history:
            self.motion_history[room] = []
        self.motion_history[room].append(timestamp)

    def learn_patterns(self) -> dict:
        """Learns hour-by-hour occupancy probability."""
        logger.info("Learning occupancy patterns from history...")
        for room, timestamps in self.motion_history.items():
            # Create a 24-hour histogram
            hour_counts = np.zeros(24)
            total_days = set()
            
            for ts in timestamps:
                dt = datetime.fromtimestamp(ts)
                hour_counts[dt.hour] += 1
                total_days.add(dt.date())
                
            num_days = len(total_days) if len(total_days) > 0 else 1
            # Simple probability: max 1.0
            probabilities = np.clip(hour_counts / (num_days * 5), 0.0, 1.0) # Assuming 5+ events in an hour means highly likely occupied
            self.patterns[room] = probabilities.tolist()
            
        return self.patterns

    def predict_occupied(self, room: str, time_of_day: datetime) -> bool:
        """Predicts if a room is likely occupied at a given time."""
        if room not in self.patterns:
            return False
        
        prob = self.patterns[room][time_of_day.hour]
        return prob > 0.5

    def get_optimal_automation_times(self, room: str) -> list[TimeWindow]:
        """Returns time windows where automation (like heating/cooling) makes sense."""
        if room not in self.patterns:
            return []
            
        windows = []
        probs = self.patterns[room]
        
        in_window = False
        start = 0
        
        for hour in range(24):
            if probs[hour] > 0.3 and not in_window:
                in_window = True
                start = hour
            elif probs[hour] <= 0.3 and in_window:
                in_window = False
                windows.append(TimeWindow(start, hour, float(np.mean(probs[start:hour]))))
                
        if in_window:
            windows.append(TimeWindow(start, 24, float(np.mean(probs[start:24]))))
            
        return windows

    def export_patterns_json(self, path: str = None) -> None:
        """Exports learned patterns to JSON."""
        target_path = path or self.data_file
        data = {
            'history': self.motion_history,
            'patterns': self.patterns
        }
        with open(target_path, 'w') as f:
            json.dump(data, f, indent=2)
        logger.info(f"Exported occupancy patterns to {target_path}")

def main():
    learner = OccupancyLearner()
    
    # Generate synthetic week of motion data
    logger.info("Generating synthetic motion data...")
    base_time = datetime.now() - timedelta(days=7)
    
    # Simulate living room: active evenings
    for day in range(7):
        for hour in range(18, 23):
            for _ in range(np.random.randint(5, 15)):
                dt = base_time + timedelta(days=day, hours=hour, minutes=np.random.randint(0, 60))
                learner.record_motion("living_room", dt.timestamp())
                
    # Simulate bedroom: active mornings and nights
    for day in range(7):
        for hour in [7, 8, 22, 23]:
            for _ in range(np.random.randint(2, 10)):
                dt = base_time + timedelta(days=day, hours=hour, minutes=np.random.randint(0, 60))
                learner.record_motion("bedroom", dt.timestamp())
                
    learner.learn_patterns()
    learner.export_patterns_json()
    
    logger.info(f"Optimal automation times for living room: {learner.get_optimal_automation_times('living_room')}")
    logger.info(f"Optimal automation times for bedroom: {learner.get_optimal_automation_times('bedroom')}")
    
    test_time = datetime.now().replace(hour=20)
    logger.info(f"Living room occupied at 20:00? {learner.predict_occupied('living_room', test_time)}")

if __name__ == "__main__":
    main()
