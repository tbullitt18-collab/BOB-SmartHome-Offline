import logging
import time
from dataclasses import dataclass
from datetime import datetime

from storm_predictor import StormPredictor
from anomaly_detector import DeviceAnomalyDetector
from occupancy_learner import OccupancyLearner
from device_health_monitor import DeviceHealthMonitor

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("BobBrain")

@dataclass
class BobReport:
    storm_risk: str
    storm_probability: float
    anomalous_devices: list[str]
    health_alerts: list[str]
    predicted_occupancy: dict
    recommended_automations: list[str]
    overall_status: str

class BobBrain:
    """The master AI orchestrator — BOB's brain."""
    
    def __init__(self):
        logger.info("Initializing BOB Brain...")
        self.storm_predictor = StormPredictor()
        self.anomaly_detector = DeviceAnomalyDetector()
        self.occupancy_learner = OccupancyLearner()
        self.health_monitor = DeviceHealthMonitor()
        
        self.storm_predictor.load_model("models/storm_predictor.pkl")
        if not self.storm_predictor.is_trained:
            logger.info("Training fresh storm predictor model...")
            data = self.storm_predictor.generate_synthetic_training_data()
            self.storm_predictor.train(data)
            self.storm_predictor.save_model("models/storm_predictor.pkl")
            
        logger.info("BOB Brain initialized.")

    def run_analysis_cycle(self) -> BobReport:
        """Runs a complete analysis cycle across all AI modules."""
        logger.info("Running BOB analysis cycle...")
        
        # 1. Storm Prediction
        current_weather = {
            'barometric_pressure': 995.0,
            'wind_speed': 35.0,
            'humidity': 85.0,
            'temperature_delta': -4.0,
            'historical_outage_patterns': 0.6
        }
        storm_prob = self.storm_predictor.predict_storm_probability(current_weather)
        storm_risk = self.storm_predictor.predict_outage_risk(current_weather)
        
        # 2. Anomaly Detection & Health Monitor Simulation
        demo_devices = ["living_room_light", "kitchen_fridge", "bedroom_ac"]
        anomalous_devices = []
        health_alerts = []
        
        for dev in demo_devices:
            # Inject fake data
            self.health_monitor.record_metric(dev, 'response_time_ms', 150)
            self.health_monitor.record_metric(dev, 'rssi_dbm', -65)
            
            # Simulate a fridge power spike anomaly
            if dev == "kitchen_fridge":
                self.health_monitor.record_metric(dev, 'error_count', 2)
                res = self.anomaly_detector.detect(dev, {"power_usage": 1800.0, "response_time": 50})
                if res.is_anomaly:
                    anomalous_devices.append(f"{dev}: {res.description}")
            
            risk = self.health_monitor.predict_failure_risk(dev)
            if risk.probability > 0.5:
                health_alerts.append(f"{dev} ({risk.recommended_action})")
                
        # 3. Occupancy
        rooms = ["living_room", "bedroom"]
        predicted_occupancy = {}
        for room in rooms:
            predicted_occupancy[room] = self.occupancy_learner.predict_occupied(room, datetime.now())
            
        # 4. Synthesize Status
        overall_status = "OPTIMAL"
        if storm_risk in ["HIGH", "CRITICAL"] or len(anomalous_devices) > 0 or len(health_alerts) > 0:
            overall_status = "ALERT"
        if storm_risk == "CRITICAL" and len(anomalous_devices) > 2:
            overall_status = "CRITICAL"
            
        return BobReport(
            storm_risk=storm_risk,
            storm_probability=storm_prob,
            anomalous_devices=anomalous_devices,
            health_alerts=health_alerts,
            predicted_occupancy=predicted_occupancy,
            recommended_automations=[],
            overall_status=overall_status
        )

    def generate_natural_language_summary(self, report: BobReport) -> str:
        """Watson-style natural language generation."""
        summary = [f"BOB has analyzed your home. Overall system status is {report.overall_status}."]
        
        if report.storm_risk in ["HIGH", "CRITICAL"]:
            summary.append(f"Storm risk is {report.storm_risk} with a {report.storm_probability:.0%} probability. Recommend pre-charging battery backups.")
            
        if report.anomalous_devices:
            summary.append(f"I detected unusual behavior in: {', '.join(report.anomalous_devices)}.")
            
        if report.health_alerts:
            summary.append(f"Health alerts: {', '.join(report.health_alerts)}.")
            
        occupied = [r for r, occ in report.predicted_occupancy.items() if occ]
        if occupied:
            summary.append(f"Predicted occupied rooms based on habits: {', '.join(occupied)}.")
            
        return " ".join(summary)

    def take_action(self, report: BobReport) -> list[str]:
        """Determines automation actions to take."""
        actions = []
        if report.storm_risk in ["HIGH", "CRITICAL"]:
            actions.append("TRIGGER script.prepare_for_outage")
        if report.predicted_occupancy.get("living_room", False):
            actions.append("TURN_ON light.living_room_main")
        return actions

    def run_continuous(self, interval_seconds=60):
        """Runs the brain continuously."""
        logger.info(f"Starting continuous analysis (interval={interval_seconds}s)")
        try:
            while True:
                report = self.run_analysis_cycle()
                summary = self.generate_natural_language_summary(report)
                logger.info(f"BOB Summary: {summary}")
                actions = self.take_action(report)
                if actions:
                    logger.info(f"Executing actions: {actions}")
                time.sleep(interval_seconds)
        except KeyboardInterrupt:
            logger.info("BOB Brain shutting down.")

def main():
    brain = BobBrain()
    report = brain.run_analysis_cycle()
    summary = brain.generate_natural_language_summary(report)
    
    print("\n" + "="*50)
    print("BOB BRAIN REPORT")
    print("="*50)
    print(summary)
    print("="*50)
    
    actions = brain.take_action(report)
    print(f"\nTriggered Actions: {actions}\n")

if __name__ == "__main__":
    main()
