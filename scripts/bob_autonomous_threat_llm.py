"""
BOB Autonomous Threat & Microgrid Survival LLM
Listens to local MQTT broker telemetry and uses a local quantized LLM
to dynamically generate offline load-shedding strategies.
"""

import paho.mqtt.client as mqtt
import threading
import time
from transformers import pipeline

# Initialize the local quantized LLM
llm = pipeline("text-generation", model="quantized-llm-model")

# Constants for local MQTT broker
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
GRID_STATUS_TOPIC = "microgrid/status"
BATTERY_LEVEL_TOPIC = "microgrid/battery"

# Variables to store current status
grid_status = "normal"  # Can be 'normal', 'alert', or 'disaster'
battery_level = 100  # Battery level percentage


def on_connect(client, userdata, flags, rc):
    """Callback function for MQTT connect."""
    print(f"Connected to local MQTT broker with result code {rc}")
    client.subscribe([(GRID_STATUS_TOPIC, 0), (BATTERY_LEVEL_TOPIC, 0)])


def on_message(client, userdata, msg):
    """Callback function for MQTT message received."""
    global grid_status, battery_level
    if msg.topic == GRID_STATUS_TOPIC:
        grid_status = msg.payload.decode()
        print(f"Grid status updated: {grid_status}")
    elif msg.topic == BATTERY_LEVEL_TOPIC:
        battery_level = int(msg.payload.decode())
        print(f"Battery level updated: {battery_level}")


def generate_load_shedding_strategy():
    """Generate load shedding strategy using the local offline LLM."""
    prompt = (
        f"The current grid status is {grid_status}. "
        f"The battery level is at {battery_level}%. "
        "Suggest an effective load-shedding strategy to ensure microgrid survival."
    )

    result = llm(prompt, max_length=150, num_return_sequences=1)
    strategy = result[0]["generated_text"]

    print(f"Generated load-shedding strategy: {strategy}")


def monitor_system():
    """Continuously monitor the system and respond to grid disasters."""
    global grid_status
    while True:
        if grid_status == "disaster":
            print("Disaster detected! Generating offline load-shedding strategy.")
            generate_load_shedding_strategy()
            grid_status = "alert"
        time.sleep(10)


def main():
    """Main function to set up local MQTT client and start monitoring."""
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(MQTT_BROKER, MQTT_PORT, 60)

    thread = threading.Thread(target=client.loop_forever)
    thread.start()

    monitor_system()


if __name__ == "__main__":
    main()