"""
Script to send simulated Smart Home metrics to Graphite via the plaintext protocol.
"""
import socket
import time
import random
from typing import Optional

class GraphiteClient:
    """Client to connect to a Graphite server and send metrics."""

    def __init__(self, host: str = 'localhost', port: int = 2003):
        """
        Initialize the GraphiteClient.
        
        Args:
            host (str): Graphite server hostname or IP address.
            port (int): Graphite server plaintext port (usually 2003).
        """
        self.host = host
        self.port = port

    def send_metric(self, path: str, value: float, timestamp: Optional[int] = None) -> None:
        """
        Send a single metric to Graphite.
        
        Args:
            path (str): Metric path (e.g., 'smart_home.power.living_room.watts').
            value (float): Metric value.
            timestamp (Optional[int]): Unix timestamp in seconds. Defaults to current time.
        """
        if timestamp is None:
            timestamp = int(time.time())
            
        message = f"{path} {value} {timestamp}\n"
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect((self.host, self.port))
                sock.sendall(message.encode('utf-8'))
        except Exception as e:
            print(f"Error sending metric {path}: {e}")


def send_device_status(client: GraphiteClient, device_name: str, is_online: bool) -> None:
    """Send device online/offline status (1 for online, 0 for offline)."""
    value = 1.0 if is_online else 0.0
    client.send_metric(f"smart_home.devices.{device_name}.status", value)

def send_power_reading(client: GraphiteClient, device_name: str, watts: float) -> None:
    """Send power consumption in watts."""
    client.send_metric(f"smart_home.power.{device_name}.watts", watts)

def send_temperature(client: GraphiteClient, room: str, celsius: float) -> None:
    """Send room temperature in Celsius."""
    client.send_metric(f"smart_home.sensors.{room}.temperature", celsius)

def send_battery_level(client: GraphiteClient, device_name: str, percent: float) -> None:
    """Send battery level as a percentage (0-100)."""
    client.send_metric(f"smart_home.battery.{device_name}.level", percent)

def send_network_status(client: GraphiteClient, internet_up: bool, hub_up: bool) -> None:
    """Send network status metrics."""
    client.send_metric("smart_home.network.internet.status", 1.0 if internet_up else 0.0)
    client.send_metric("smart_home.network.hub.status", 1.0 if hub_up else 0.0)

def main():
    """Main loop for generating simulated data."""
    client = GraphiteClient()
    
    print("Starting simulated metrics generation for BOB's Smart Home Offline System...")
    
    # State variables for simulation
    ups_battery = 100.0
    
    try:
        while True:
            # Simulate devices status
            send_device_status(client, "living_room_light", True)
            send_device_status(client, "kitchen_light", random.choice([True, False]))
            
            # Simulate power readings
            send_power_reading(client, "tv", random.uniform(50.0, 150.0))
            send_power_reading(client, "fridge", random.uniform(100.0, 300.0))
            
            # Simulate temperatures
            send_temperature(client, "living_room", random.uniform(21.0, 23.0))
            send_temperature(client, "bedroom", random.uniform(19.0, 21.0))
            
            # Simulate battery drain
            ups_battery = max(0.0, ups_battery - random.uniform(0.1, 0.5))
            if ups_battery < 10.0:
                ups_battery = 100.0  # recharge
            send_battery_level(client, "ups", ups_battery)
            
            # Simulate network (hub mostly up, internet might be flaky)
            send_network_status(client, internet_up=random.random() > 0.1, hub_up=True)
            
            # Ping times
            client.send_metric("smart_home.network.living_room_light.ping", random.uniform(10, 50))
            
            # Motion events
            client.send_metric("smart_home.sensors.living_room.motion", random.randint(0, 5))
            
            # Storm mode
            client.send_metric("smart_home.system.storm_mode", random.choice([0.0, 1.0]))
            
            print(f"[{time.strftime('%H:%M:%S')}] Metrics sent. Waiting 30s...")
            time.sleep(30)
            
    except KeyboardInterrupt:
        print("\nMetrics generation stopped.")

if __name__ == "__main__":
    main()
