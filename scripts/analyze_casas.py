import sys
import os
import argparse
from datetime import datetime
from collections import defaultdict

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'ai'))
from occupancy_learner import OccupancyLearner

def parse_casas_dataset(file_path: str, ol: OccupancyLearner):
    """
    Parses a standard WSU CASAS Smart Home dataset file.
    Expected format per line:
    YYYY-MM-DD HH:MM:SS.mmmmmm SensorID SensorValue [Activity]
    e.g., 2010-11-04 00:03:50.209589 M003 ON Sleep
    """
    print(f"📂 Loading CASAS Dataset from: {file_path}")
    print("⏳ Processing millions of rows... This may take a moment.")
    
    line_count = 0
    motion_events = 0
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line_count += 1
                parts = line.strip().split()
                if len(parts) < 4:
                    continue
                
                date_str = parts[0]
                time_str = parts[1]
                sensor_id = parts[2]
                sensor_value = parts[3]
                
                # We only care about Motion sensors (usually start with 'M' in CASAS)
                # and when they are triggered 'ON'
                if sensor_id.startswith('M') and sensor_value == 'ON':
                    try:
                        # Parse the timestamp: 2010-11-04 00:03:50.209589
                        dt_str = f"{date_str} {time_str}"
                        # CASAS sometimes drops the microseconds
                        if '.' in time_str:
                            dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S.%f")
                        else:
                            dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
                        
                        # In a real setup, you'd map 'M003' to 'Living_Room', etc.
                        # For now, we group by the raw sensor ID.
                        ol.record_motion(sensor_id, dt.timestamp())
                        motion_events += 1
                        
                    except ValueError:
                        continue
                        
                if line_count % 500000 == 0:
                    print(f"   -> Parsed {line_count} rows...")
                    
    except FileNotFoundError:
        print(f"❌ ERROR: File not found at {file_path}")
        print("Please download the CASAS Aruba dataset (or similar) from Zenodo and place it here.")
        sys.exit(1)
        
    print(f"✅ Successfully parsed {line_count} total rows.")
    print(f"✅ Extracted {motion_events} valid motion events.")
    
    # Trigger the ML learning phase
    ol.learn_patterns()
    print("🧠 BOB has finished learning the actual human occupancy patterns from the CASAS data.")
    return ol

def print_occupancy_heatmap(ol: OccupancyLearner, room: str):
    """Prints an ASCII heatmap of a room's probability of being occupied by hour."""
    print(f"\n🔥 IRL OCCUPANCY HEATMAP: SENSOR {room} 🔥")
    print("Hour | Probability Bar")
    print("-----|--------------------------------------------------")
    
    for hour in range(24):
        # We query the AI to predict if occupied based on a datetime matching that hour
        dt = datetime(2026, 8, 20, hour, 0)
        is_occupied = ol.predict_occupied(room, dt)
        
        # Display logic
        bar = "█" * 30 if is_occupied else "░" * 5
        status = "HIGH" if is_occupied else "LOW "
        print(f"{hour:02d}:00 | {bar} ({status})")

def main():
    parser = argparse.ArgumentParser(description='Analyze WSU CASAS Dataset with BOB AI.')
    parser.add_argument('dataset_path', type=str, help='Path to the CASAS dataset file (e.g., data.txt)')
    parser.add_argument('--sensor', type=str, default='M003', help='Specific sensor ID to map (default M003)')
    
    args = parser.parse_args()
    
    ol = OccupancyLearner()
    parse_casas_dataset(args.dataset_path, ol)
    
    # Print the heatmap for the requested sensor
    print_occupancy_heatmap(ol, args.sensor)

if __name__ == "__main__":
    main()
