import os
import logging
from pathlib import Path
from dataclasses import dataclass
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("StormPredictor")

class StormPredictor:
    """Predicts storm probabilities and outage risks using RandomForestClassifier."""
    
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.is_trained = False
        
    def generate_synthetic_training_data(self, samples=1000) -> pd.DataFrame:
        """Generates synthetic training data for storms."""
        np.random.seed(42)
        
        # 0: Normal, 1: Storm
        labels = np.random.choice([0, 1], size=samples, p=[0.8, 0.2])
        
        data = {
            'barometric_pressure': np.where(labels == 1, np.random.normal(990, 5, samples), np.random.normal(1015, 5, samples)),
            'wind_speed': np.where(labels == 1, np.random.normal(40, 10, samples), np.random.normal(10, 5, samples)),
            'humidity': np.where(labels == 1, np.random.normal(90, 5, samples), np.random.normal(50, 15, samples)),
            'temperature_delta': np.where(labels == 1, np.random.normal(-5, 2, samples), np.random.normal(0, 1, samples)),
            'historical_outage_patterns': np.where(labels == 1, np.random.normal(0.8, 0.1, samples), np.random.normal(0.1, 0.1, samples)),
            'storm_event': labels
        }
        return pd.DataFrame(data)

    def train(self, historical_data: pd.DataFrame) -> None:
        """Trains the model on historical weather data."""
        logger.info("Training StormPredictor model...")
        X = historical_data.drop(columns=['storm_event'])
        y = historical_data['storm_event']
        self.model.fit(X, y)
        self.is_trained = True
        logger.info("Model training complete.")

    def predict_storm_probability(self, current_readings: dict) -> float:
        """Predicts probability of a storm event."""
        if not self.is_trained:
            logger.warning("Model not trained, returning default 0.0")
            return 0.0
            
        df = pd.DataFrame([current_readings])
        prob = self.model.predict_proba(df)[0][1]
        return float(prob)

    def predict_outage_risk(self, current_readings: dict) -> str:
        """Categorizes outage risk based on readings."""
        prob = self.predict_storm_probability(current_readings)
        if prob < 0.2:
            return "LOW"
        elif prob < 0.5:
            return "MEDIUM"
        elif prob < 0.8:
            return "HIGH"
        else:
            return "CRITICAL"

    def save_model(self, path: str) -> None:
        """Saves the trained model to disk."""
        if not self.is_trained:
            logger.error("Cannot save untrained model.")
            return
            
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.model, path)
        logger.info(f"Model saved to {path}")

    def load_model(self, path: str) -> None:
        """Loads a trained model from disk."""
        if Path(path).exists():
            self.model = joblib.load(path)
            self.is_trained = True
            logger.info(f"Model loaded from {path}")
        else:
            logger.error(f"Model file not found at {path}")

def main():
    predictor = StormPredictor()
    
    logger.info("Generating synthetic data...")
    data = predictor.generate_synthetic_training_data()
    
    predictor.train(data)
    
    model_path = Path(__file__).parent / "models" / "storm_predictor.pkl"
    predictor.save_model(str(model_path))
    
    example_reading = {
        'barometric_pressure': 985.0,
        'wind_speed': 45.0,
        'humidity': 92.0,
        'temperature_delta': -6.5,
        'historical_outage_patterns': 0.85
    }
    
    logger.info(f"Example Reading: {example_reading}")
    prob = predictor.predict_storm_probability(example_reading)
    risk = predictor.predict_outage_risk(example_reading)
    
    logger.info(f"Storm Probability: {prob:.2%}")
    logger.info(f"Outage Risk: {risk}")

if __name__ == "__main__":
    main()
