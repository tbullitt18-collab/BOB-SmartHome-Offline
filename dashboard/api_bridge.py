import http.server
import socketserver
import json
import logging
import os
from urllib.parse import urlparse, parse_qs

# Configuration
PORT = 8888
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# In-memory store
device_state = {
    "lights": {"living_room": True, "kitchen": True, "bedroom": False, "exterior": True},
    "locks": {"front_door": True, "back_door": True, "garage": True},
    "climate": {"target": 70, "living_room": 72.1, "bedroom": 68.5, "outside": 85.0},
    "power": {"total_w": 1420, "hvac": 800, "appliances": 450, "always_on": 170},
    "system": {"hub_online": True, "ups_battery": 98, "storm_risk": "LOW"}
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
            logging.info("Served /api/status")
            return
            
        elif parsed_path.path == '/api/metrics':
            self._set_headers()
            self.wfile.write(json.dumps({
                "power": device_state["power"],
                "climate": device_state["climate"]
            }).encode())
            logging.info("Served /api/metrics")
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
            logging.info("Served /api/ai/report")
            return
            
        # Fallback to serving static files
        super().do_GET()

    def do_POST(self):
        parsed_path = urlparse(self.path)
        
        if parsed_path.path.startswith('/api/device/') and parsed_path.path.endswith('/toggle'):
            parts = parsed_path.path.split('/')
            if len(parts) >= 5:
                device_type = parts[3] # e.g., lights
                device_id = parts[4]   # e.g., living_room
                
                # We would parse body here for state, but for simple toggle:
                if device_type in device_state and device_id in device_state[device_type]:
                    device_state[device_type][device_id] = not device_state[device_type][device_id]
                    self._set_headers()
                    self.wfile.write(json.dumps({"status": "success", "new_state": device_state[device_type][device_id]}).encode())
                    logging.info(f"Toggled {device_type}/{device_id} to {device_state[device_type][device_id]}")
                else:
                    self._set_error(404, "Device not found")
            else:
                self._set_error(400, "Bad request")
            return

        self._set_error(404, "Endpoint not found")


if __name__ == "__main__":
    Handler = DashboardHTTPRequestHandler
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        logging.info(f"Serving BOB Dashboard at http://localhost:{PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass
        httpd.server_close()
        logging.info("Server stopped.")
