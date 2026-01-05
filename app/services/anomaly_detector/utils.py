NUMERIC_FEATURES = [
    "cpu_usage",
    "memory_usage",
    "latency_ms",
    "disk_usage",
    "network_in_kbps",
    "network_out_kbps",
    "io_wait",
    "thread_count",
    "active_connections",
    "error_rate",
    "temperature_celsius",
    "power_consumption_watts"
]

Z_SCORE_THRESHOLD = 3.0  # statistical anomaly cutoff

class DetectionStrategy:
    STATISTICAL = "statistical"
    MULTIVARIATE = "multivariate"
    PCA_MAHALANOBIS = "pca_mahalanobis"
