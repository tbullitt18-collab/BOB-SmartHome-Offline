import logging
from pathlib import Path
from dataclasses import dataclass
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
import joblib

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("DeviceAnomalyDetector")

@dataclass
class AnomalyResult:
    is_anomaly: bool
    confidence: float
    description: str
    recommended_action: str

class DeviceAnomalyDetector:
    """Local anomaly detection for smart home devices."""
    
    def __init__(self, base_model_dir: str = None):
        self.base_model_dir = base_model_dir or str(Path(__file__).parent / "models" / "anomaly")
        self.models = {}  # device_id -> model
        Path(self.base_model_dir).mkdir(parents=True, exist_ok=True)

    def _get_model_path(self, device_id: str) -> Path:
        return Path(self.base_model_dir) / f"{device_id}_iforest.pkl"

    def fit_device(self, device_id: str, normal_readings: list[dict]) -> None:
        """Trains an anomaly detection model for a specific device."""
        logger.info(f"Training anomaly detector for {device_id} with {len(normal_readings)} readings")
        df = pd.DataFrame(normal_readings)
        
        # Basic isolation forest
        model = IsolationForest(n_estimators=100, contamination=0.05, random_state=42)
        model.fit(df)
        
        self.models[device_id] = model
        
        model_path = self._get_model_path(device_id)
        joblib.dump(model, model_path)
        logger.info(f"Model saved to {model_path}")

    def load_device_model(self, device_id: str) -> None:
        """Loads a specific device model."""
        model_path = self._get_model_path(device_id)
        if model_path.exists():
            self.models[device_id] = joblib.load(model_path)
            logger.debug(f"Loaded model for {device_id}")
        else:
            logger.warning(f"No model found for {device_id}")

    def detect(self, device_id: str, current_reading: dict) -> AnomalyResult:
        """Detects if a current reading is anomalous."""
        if device_id not in self.models:
            self.load_device_model(device_id)
            
        if device_id not in self.models:
            return AnomalyResult(False, 0.0, "Model not trained", "No action needed")
            
        model = self.models[device_id]
        df = pd.DataFrame([current_reading])
        
        prediction = model.predict(df)[0]
        score = model.score_samples(df)[0]
        
        is_anomaly = (prediction == -1)
        # Score is negative, lower means more anomalous.
        confidence = float(min(1.0, max(0.0, abs(score) / 2.0))) if is_anomaly else 0.0
        
        description = "Normal operation"
        action = "No action needed"
        
        if is_anomaly:
            # Simple heuristic for anomaly type based on keys
            if "power_usage" in current_reading and current_reading["power_usage"] > 1000:
                description = "POWER_SPIKE"
                action = "Check device power supply or turn off if overheating."
            elif "response_time" in current_reading and current_reading["response_time"] > 5000:
                description = "DEVICE_UNRESPONSIVE"
                action = "Reboot device or check network connection."
            else:
                description = "UNUSUAL_ACTIVITY"
                action = "Monitor device for further issues."
                
        return AnomalyResult(is_anomaly, confidence, description, action)

def main():
    detector = DeviceAnomalyDetector()
    
    demo_devices = [f"smart_plug_{i}" for i in range(1, 6)]
    
    # Generate normal data
    for device_id in demo_devices:
        normal_data = [
            {"power_usage": np.random.normal(50, 5), "response_time": np.random.normal(20, 5)}
            for _ in range(200)
        ]
        detector.fit_device(device_id, normal_data)
        
    # Feed anomalous data
    test_device = "smart_plug_1"
    normal_reading = {"power_usage": 52.0, "response_time": 21.0}
    anomaly_reading = {"power_usage": 1500.0, "response_time": 25.0}
    
    logger.info(f"Testing normal reading on {test_device}: {normal_reading}")
    res1 = detector.detect(test_device, normal_reading)
    logger.info(f"Result: {res1}")
    
    logger.info(f"Testing anomaly reading on {test_device}: {anomaly_reading}")
    res2 = detector.detect(test_device, anomaly_reading)
    logger.info(f"Result: {res2}")

if __name__ == "__main__":
    main()
