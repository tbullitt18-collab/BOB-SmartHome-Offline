import sys
import os
from datetime import datetime, timedelta

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'ai'))
from occupancy_learner import OccupancyLearner

def simulate_family_week(ol: OccupancyLearner):
    """Simulates 7 days of realistic motion data in a real house."""
    print("🏠 SIMULATING 7 DAYS OF ACTUAL RESIDENCE OCCUPANCY (Family of 4)...")
    
    start_date = datetime(2026, 8, 20) # A week ago
    
    for day in range(7):
        current_date = start_date + timedelta(days=day)
        
        # Is it a weekday (0-4) or weekend (5-6)?
        is_weekend = current_date.weekday() >= 5
        
        if not is_weekend:
            # WEEKDAY SCHEDULE
            # 6:00 AM - 7:00 AM: Wake up, master bedroom and bathroom motion
            for m in range(0, 60, 5):
                ol.record_motion("Master_Bedroom", (current_date + timedelta(hours=6, minutes=m)).timestamp())
            
            # 7:00 AM - 8:30 AM: Breakfast, Kitchen and Living Room chaotic motion
            for m in range(0, 90, 2):
                ol.record_motion("Kitchen", (current_date + timedelta(hours=7, minutes=m)).timestamp())
                ol.record_motion("Living_Room", (current_date + timedelta(hours=7, minutes=m)).timestamp())
                
            # 8:30 AM - 3:30 PM: House is mostly empty (school/work)
            # Maybe random pet movement
            ol.record_motion("Living_Room", (current_date + timedelta(hours=12, minutes=15)).timestamp())
            
            # 3:30 PM - 5:30 PM: Kids home from school (Living Room, Kitchen)
            for m in range(0, 120, 10):
                ol.record_motion("Living_Room", (current_date + timedelta(hours=15, minutes=30+m)).timestamp())
                ol.record_motion("Kitchen", (current_date + timedelta(hours=15, minutes=30+m)).timestamp())
                
            # 5:30 PM - 10:00 PM: Evening routine (Dinner, TV)
            for m in range(0, 270, 5):
                ol.record_motion("Living_Room", (current_date + timedelta(hours=17, minutes=30+m)).timestamp())
                
            # 10:00 PM onwards: Sleeping (Bedrooms)
            ol.record_motion("Master_Bedroom", (current_date + timedelta(hours=22, minutes=15)).timestamp())
            
        else:
            # WEEKEND SCHEDULE (Messier, home all day, later wake up)
            for m in range(0, 600, 15): # 9 AM to 7 PM random motion
                ol.record_motion("Living_Room", (current_date + timedelta(hours=9, minutes=m)).timestamp())
                ol.record_motion("Kitchen", (current_date + timedelta(hours=9, minutes=m)).timestamp())

def print_occupancy_heatmap(ol: OccupancyLearner, room: str):
    """Prints an ASCII heatmap of a room's probability of being occupied by hour."""
    print(f"\n🔥 AI OCCUPANCY PROBABILITY HEATMAP: {room.replace('_', ' ').upper()} 🔥")
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
    print("="*60)
    print("🤖 BOB: REAL RESIDENCE OCCUPANCY TEST")
    print("="*60)
    
    ol = OccupancyLearner()
    
    # 1. Feed the AI a week of realistic family motion data
    simulate_family_week(ol)
    ol.learn_patterns()
    
    # 2. Ask the AI to generate heatmaps based on what it learned
    print_occupancy_heatmap(ol, "Kitchen")
    print_occupancy_heatmap(ol, "Living_Room")
    
    # 3. Simulate a storm hitting at 1:00 PM (13:00) on a Tuesday
    print("\n" + "="*60)
    print("⛈️ STORM SCENARIO: Grid fails at 1:00 PM (13:00)")
    
    # Use a weekday datetime (August 20th 2026 is a Thursday)
    is_kitchen = ol.predict_occupied("Kitchen", datetime(2026, 8, 20, 13, 0))
    is_living = ol.predict_occupied("Living_Room", datetime(2026, 8, 20, 13, 0))
    
    print("\nBOB BRAIN DECISION MATRIX:")
    if not is_kitchen:
        print(" -> Kitchen probability is LOW. ⚡ Cutting Kitchen lights & appliances to save UPS battery.")
    else:
        print(" -> Kitchen probability is HIGH. Keeping lights on for safety.")
        
    if not is_living:
        print(" -> Living Room probability is LOW. ⚡ Cutting Living Room HVAC & lights.")
    else:
        print(" -> Living Room probability is HIGH. Keeping HVAC active.")
        
    print("\n" + "="*60)

if __name__ == "__main__":
    main()
