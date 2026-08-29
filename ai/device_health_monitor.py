import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
import numpy as np

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("DeviceHealthMonitor")

@dataclass
class FailureRisk:
    probability: float
    days_until_failure: int
    symptoms: list[str]
    recommended_action: str

class DeviceHealthMonitor:
    """Predictive device health monitoring using statistical models."""
    
    def __init__(self):
        self.device_metrics = {} # device_id -> dict of metrics
        
    def record_metric(self, device_id: str, metric_name: str, value: float, timestamp: float = None) -> None:
        """Records a health metric for a device."""
        if timestamp is None:
            timestamp = datetime.now().timestamp()
            
        if device_id not in self.device_metrics:
            self.device_metrics[device_id] = {
                'response_time_ms': [],
                'error_count': [],
                'rssi_dbm': [],
                'uptime_hours': [],
                'last_seen': 0
            }
            
        if metric_name in self.device_metrics[device_id]:
            self.device_metrics[device_id][metric_name].append((timestamp, value))
            self.device_metrics[device_id]['last_seen'] = timestamp
            
            # Keep only last 100 readings
            if len(self.device_metrics[device_id][metric_name]) > 100:
                self.device_metrics[device_id][metric_name] = self.device_metrics[device_id][metric_name][-100:]

    def get_health_score(self, device_id: str) -> float:
        """Calculates a health score from 0-100 based on recent metrics."""
        if device_id not in self.device_metrics:
            return 100.0
            
        metrics = self.device_metrics[device_id]
        score = 100.0
        
        # Deduct for high error counts
        recent_errors = [v for t, v in metrics.get('error_count', []) if t > datetime.now().timestamp() - 86400]
        if recent_errors:
            score -= sum(recent_errors) * 5
            
        # Deduct for poor signal
        recent_rssi = [v for t, v in metrics.get('rssi_dbm', [])]
        if recent_rssi:
            avg_rssi = np.mean(recent_rssi[-10:])
            if avg_rssi < -80:
                score -= 15
                
        # Deduct for slow response
        recent_resp = [v for t, v in metrics.get('response_time_ms', [])]
        if recent_resp:
            avg_resp = np.mean(recent_resp[-10:])
            if avg_resp > 2000:
                score -= 20
                
        return float(max(0.0, min(100.0, score)))

    def predict_failure_risk(self, device_id: str) -> FailureRisk:
        """Predicts risk of device failure."""
        score = self.get_health_score(device_id)
        metrics = self.device_metrics.get(device_id, {})
        
        symptoms = []
        prob = 0.0
        days = 999
        action = "Monitor device."
        
        if score < 50:
            prob = 0.8
            days = max(1, int(score / 10))
            symptoms.append(f"Low health score: {score:.1f}")
            action = "Consider replacing or factory resetting the device soon."
            
        recent_rssi = [v for t, v in metrics.get('rssi_dbm', [])]
        if recent_rssi and np.mean(recent_rssi[-5:]) < -85:
            symptoms.append("Critically low WiFi signal")
            prob = max(prob, 0.6)
            days = min(days, 5)
            action = "Check WiFi coverage or move router closer."
            
        return FailureRisk(prob, days, symptoms, action)

    def generate_health_report(self) -> str:
        """Generates a text report of all device health."""
        report = ["=== BOB Device Health Report ==="]
        for dev_id in self.device_metrics.keys():
            score = self.get_health_score(dev_id)
            risk = self.predict_failure_risk(dev_id)
            
            report.append(f"\nDevice: {dev_id}")
            report.append(f"  Health Score: {score:.1f}/100")
            if risk.probability > 0.4:
                report.append(f"  WARNING: Failure probability {risk.probability:.0%}")
                report.append(f"  Estimated days to failure: {risk.days_until_failure}")
                report.append(f"  Symptoms: {', '.join(risk.symptoms)}")
                report.append(f"  Action: {risk.recommended_action}")
            else:
                report.append("  Status: OK")
                
        return "\n".join(report)

def main():
    monitor = DeviceHealthMonitor()
    logger.info("Simulating 10 devices...")
    
    now = datetime.now().timestamp()
    
    for i in range(10):
        dev = f"sensor_node_{i}"
        
        # Simulate healthy devices
        if i < 8:
            monitor.record_metric(dev, 'response_time_ms', np.random.normal(100, 20), now)
            monitor.record_metric(dev, 'error_count', 0, now)
            monitor.record_metric(dev, 'rssi_dbm', np.random.normal(-60, 5), now)
        # Simulate failing devices
        else:
            monitor.record_metric(dev, 'response_time_ms', np.random.normal(3000, 500), now)
            monitor.record_metric(dev, 'error_count', np.random.randint(2, 5), now)
            monitor.record_metric(dev, 'rssi_dbm', np.random.normal(-90, 2), now)
            
    print(monitor.generate_health_report())

if __name__ == "__main__":
    main()
