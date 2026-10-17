import http.server
import socketserver
import json
import logging
import os
import sys
from urllib.parse import urlparse

# Import physical WiZ UDP controller from scripts/ or C:\Users\tbull\bob_local_wiz.py
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts")))
sys.path.insert(0, r"C:\Users\tbull")
try:
    from bob_local_wiz import discover_and_set_wiz, get_local_subnet
    HAS_WIZ = True
except Exception as e:
    logging.warning(f"Could not import bob_local_wiz: {e}")
    HAS_WIZ = False

PORT = 8888
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

device_state = {
    "lights": {"living_room": True, "kitchen": True, "bedroom": False, "exterior": True},
    "locks": {"front_door": True, "back_door": True, "garage": True},
    "climate": {"target": 70, "living_room": 72.1, "bedroom": 68.5, "outside": 85.0},
    "power": {"total_w": 1420, "hvac": 800, "appliances": 450, "always_on": 170},
    "system": {"hub_online": True, "ups_battery": 98, "storm_risk": "LOW", "wiz_relay": True}
}

class DashboardHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def _set_headers(self, content_type='application/json'):
        self.send_response(200)
        self.send_header('Content-type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

    def _set_error(self, code, message):
        self.send_response(code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({'error': message}).encode())

    def do_GET(self):
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/api/status':
            self._set_headers()
            self.wfile.write(json.dumps(device_state).encode())
            return
            
        elif parsed_path.path == '/api/metrics':
            self._set_headers()
            self.wfile.write(json.dumps({
                "power": device_state["power"],
                "climate": device_state["climate"]
            }).encode())
            return
            
        elif parsed_path.path == '/api/ai/report':
            self._set_headers()
            self.wfile.write(json.dumps({
                "logs": [
                    "[OK] Normal power usage detected.",
                    "[INFO] Occupancy predicted in Kitchen in 15m.",
                    "[WARN] Outside temp rising rapidly."
                ],
                "storm_probability": 15
            }).encode())
            return
            
        super().do_GET()

    def do_POST(self):
        parsed_path = urlparse(self.path)

        # Physical WiZ Hardware Relay Endpoint (/api/wiz/on or /api/wiz/off)
        if parsed_path.path in ('/api/wiz/on', '/api/wiz/off'):
            target_state = (parsed_path.path == '/api/wiz/on')
            logging.info(f"[HARDWARE] Executing physical WiZ UDP command: state={target_state}")
            if HAS_WIZ:
                try:
                    discover_and_set_wiz(target_state)
                    local_ip, prefix = get_local_subnet()
                except Exception as e:
                    logging.error(f"WiZ hardware error: {e}")
                    local_ip, prefix = ("unknown", "unknown")
            else:
                local_ip, prefix = ("simulated", "simulated")

            device_state["system"]["wiz_relay"] = target_state
            device_state["power"]["hvac"] = 800 if target_state else 0
            device_state["power"]["appliances"] = 450 if target_state else 0
            device_state["power"]["total_w"] = 1420 if target_state else 170

            self._set_headers()
            self.wfile.write(json.dumps({
                "status": "success",
                "wiz_state": target_state,
                "edge_ip": local_ip,
                "relay_ip": "192.168.0.114",
                "mac": "cc4085c58c2c",
                "power": device_state["power"]
            }).encode())
            return

        if parsed_path.path.startswith('/api/device/') and parsed_path.path.endswith('/toggle'):
            parts = parsed_path.path.split('/')
            if len(parts) >= 5:
                device_type = parts[3]
                device_id = parts[4]
                if device_type in device_state and device_id in device_state[device_type]:
                    device_state[device_type][device_id] = not device_state[device_type][device_id]
                    self._set_headers()
                    self.wfile.write(json.dumps({"status": "success", "new_state": device_state[device_type][device_id]}).encode())
                else:
                    self._set_error(404, "Device not found")
            else:
                self._set_error(400, "Bad request")
            return

        self._set_error(404, "Endpoint not found")


if __name__ == "__main__":
    socketserver.TCPServer.allow_reuse_address = True
    Handler = DashboardHTTPRequestHandler
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        logging.info(f"Serving BOB Dashboard at http://localhost:{PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass
        httpd.server_close()
        logging.info("Server stopped.")
