
from app.services.anomaly_detector.classic import ClassicAnomalyDetector
from app.services.anomaly_detector.utils import DetectionStrategy

def create_anomaly_detector(config):
    detector_type = config.get("detector_type", "classic")
    threshold = config.get("threshold", 3.0)

    if detector_type == "classic":
        return ClassicAnomalyDetector(threshold=threshold, strategy=DetectionStrategy.STATISTICAL)

    
    raise ValueError(f"Unknown detector type: {detector_type}")