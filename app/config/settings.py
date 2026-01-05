import os
from enum import Enum

class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

# Kafka Configuration
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:29092")
KAFKA_INPUT_TOPIC = os.getenv("KAFKA_INPUT_TOPIC", "infra-input")
KAFKA_OUTPUT_TOPIC = os.getenv("KAFKA_OUTPUT_TOPIC", "infra-output")
KAFKA_TIMEOUT = int(os.getenv("KAFKA_TIMEOUT", "30"))

# LLM Configuration
LLM_MODEL = os.getenv("LLM_MODEL", "openrouter/mistralai/devstral-2512:free")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://openrouter.ai/api/v1")
LLM_API_KEY = os.getenv("LLM_API_KEY", "sk-your-api-key-here")
# Application Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() == "true"

# Anomaly Detection Configuration
ANOMALY_THRESHOLD = float(os.getenv("ANOMALY_THRESHOLD", "4.0"))
CONTAMINATION_RATE = float(os.getenv("CONTAMINATION_RATE", "0.05"))