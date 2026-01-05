import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from scipy.stats import chi2

from app.services.anomaly_detector.base import AnanomalyDetector
from app.services.anomaly_detector.utils import NUMERIC_FEATURES, DetectionStrategy
from app.config.logger import setup_logger
from app.config.settings import ANOMALY_THRESHOLD, CONTAMINATION_RATE

logger = setup_logger(__name__)

class ClassicAnomalyDetector(AnanomalyDetector):
    """Classic machine learning-based anomaly detection."""
    
    def __init__(self, threshold: float = ANOMALY_THRESHOLD, strategy: str = DetectionStrategy.MULTIVARIATE):
        super().__init__({"threshold": threshold, "strategy": strategy})
        self.threshold = threshold
        self.strategy = strategy
        self.model = IsolationForest(
            n_estimators=200,
            contamination=CONTAMINATION_RATE,
            random_state=42
        )
        self._strategies = {
            DetectionStrategy.STATISTICAL: self.detect_statistical_anomalies,
            DetectionStrategy.MULTIVARIATE: self.detect_multivariate_anomalies,
            DetectionStrategy.PCA_MAHALANOBIS: self.pca_mahalanobis_anomalies,
        }
        logger.info(f"Initialized ClassicAnomalyDetector with strategy: {strategy}")

    def detect_statistical_anomalies(self, df: pd.DataFrame):
        """Detect anomalies using statistical Z-score method."""
        anomalies = []
        indices = set()
        
        for feature in NUMERIC_FEATURES:
            try:
                mean = df[feature].mean()
                std = df[feature].std()
                
                if std == 0:
                    logger.debug(f"Skipping {feature}: zero standard deviation")
                    continue
                
                z_scores = (df[feature] - mean) / std
                
                for idx, z in z_scores.items():
                    if abs(z) > self.threshold:
                        severity = self._calculate_severity(abs(z))
                        anomalies.append({
                            "metric": feature,
                            "value": float(df.loc[idx, feature]),
                            "threshold": float(mean + self.threshold * std),
                            "severity": severity,
                            "description": f"{feature} deviates significantly (z-score={z:.2f})",
                            "index": idx
                        })
                        indices.add(idx)
                        
            except Exception as e:
                logger.warning(f"Error processing feature {feature}: {str(e)}")
                continue
        
        logger.debug(f"Statistical anomalies detected: {len(anomalies)}")
        return anomalies, indices

    def detect_multivariate_anomalies(self, df: pd.DataFrame):
        """Detect anomalies using Isolation Forest."""
        try:
            X = df[NUMERIC_FEATURES]
            self.model.fit(X)
            scores = self.model.decision_function(X)
            predictions = self.model.predict(X)
            
            anomalies = []
            indices = set()
            
            for i, pred in enumerate(predictions):
                if pred == -1:
                    anomalies.append({
                        "metric": "multivariate_pattern",
                        "value": float(scores[i]),
                        "threshold": None,
                        "severity": "high",
                        "description": "Abnormal system behavior detected across multiple metrics",
                        "index": i
                    })
                    indices.add(i)
            
            logger.debug(f"Multivariate anomalies detected: {len(anomalies)}")
            return anomalies, indices
            
        except Exception as e:
            logger.error(f"Error in multivariate detection: {str(e)}", exc_info=True)
            raise

    def pca_mahalanobis_anomalies(self, df: pd.DataFrame):
        """Detect anomalies using PCA and Mahalanobis distance."""
        try:
            X = df[NUMERIC_FEATURES].values
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            pca = PCA(n_components=0.95)
            X_pca = pca.fit_transform(X_scaled)
            
            mean = np.mean(X_pca, axis=0)
            cov = np.cov(X_pca, rowvar=False)
            inv_cov = np.linalg.inv(cov)
            
            anomalies = []
            indices = set()
            
            for i, x in enumerate(X_pca):
                diff = x - mean
                distance = diff.T @ inv_cov @ diff
                threshold = chi2.ppf(0.99, df=X_pca.shape[1])
                
                if distance > threshold:
                    severity = self._calculate_pca_severity(distance, threshold)
                    anomalies.append({
                        "metric": "correlation_pattern",
                        "value": float(distance),
                        "threshold": float(threshold),
                        "severity": severity,
                        "description": "Abnormal correlation among metrics (PCA + Mahalanobis)",
                        "index": i
                    })
                    indices.add(i)
            
            logger.debug(f"PCA-Mahalanobis anomalies detected: {len(anomalies)}")
            return anomalies, indices
            
        except Exception as e:
            logger.error(f"Error in PCA-Mahalanobis detection: {str(e)}", exc_info=True)
            raise

    @staticmethod
    def _calculate_severity(z_score: float) -> str:
        """Calculate anomaly severity based on Z-score."""
        if z_score > 5:
            return "high"
        elif z_score > 4:
            return "medium"
        return "low"

    @staticmethod
    def _calculate_pca_severity(distance: float, threshold: float) -> str:
        """Calculate anomaly severity based on Mahalanobis distance."""
        if distance > threshold * 2:
            return "high"
        elif distance > threshold * 1.5:
            return "medium"
        return "low"

    def detect(self, df: pd.DataFrame) -> dict:
        """Execute anomaly detection using selected strategy."""
        logger.info(f"Starting anomaly detection with strategy: {self.strategy}")
        
        strategy_func = self._strategies.get(self.strategy, self.detect_multivariate_anomalies)
        anomalies, indices = strategy_func(df)
        
        for anomaly in anomalies:
            anomaly.pop("index", None)
        
        df_anom = df.iloc[list(indices)] if indices else df.iloc[[]]
        
        insights = {
            "average_latency_ms": float(df_anom["latency_ms"].mean()) if not df_anom.empty else 0.0,
            "max_cpu_usage": float(df_anom["cpu_usage"].max()) if not df_anom.empty else 0.0,
            "max_memory_usage": float(df_anom["memory_usage"].max()) if not df_anom.empty else 0.0,
            "error_rate": float(df_anom["error_rate"].mean()) if not df_anom.empty else 0.0,
            "uptime_seconds": int(df_anom["uptime_seconds"].max()) if not df_anom.empty else 0
        }
        
        status_summary = {"online": [], "degraded": [], "offline": []}
        for row in df_anom["service_status"]:
            for service, status in row.items():
                if status in status_summary:
                    status_summary[status].append(service)
        
        for k in status_summary:
            status_summary[k] = list(set(status_summary[k]))
        
        logger.info(f"Detection complete: {len(anomalies)} anomalies found")
        
        return {
            "anomalies": anomalies,
            "insights": insights,
            "service_status_summary": status_summary
        }