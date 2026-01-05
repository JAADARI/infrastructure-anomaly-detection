# Infrastructure Anomaly Detection System

A production-grade infrastructure monitoring system that detects anomalies in real-time using advanced machine learning techniques and provides actionable recommendations via LLM integration.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Testing](#testing)
- [Project Structure](#project-structure)
- [API Documentation](#api-documentation)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## Overview

This system monitors infrastructure metrics (CPU, memory, latency, disk usage, etc.) and uses machine learning algorithms to detect anomalies. When anomalies are detected, the system generates recommendations to optimize infrastructure performance.

**Key Capabilities:**
- Real-time anomaly detection using multiple strategies
- Batch processing for historical data analysis
- Kafka-based event streaming architecture
- LLM-powered actionable recommendations
- Comprehensive logging and monitoring
- Production-ready error handling

## Features

### Detection Strategies

1. **Statistical Detection** - Z-score based anomaly detection
2. **Multivariate Detection** - Isolation Forest algorithm
3. **PCA-Mahalanobis** - Correlation pattern detection

### Metrics Monitored

- CPU Usage (%)
- Memory Usage (%)
- Latency (ms)
- Disk Usage (%)
- Network I/O (Kbps)
- IO Wait (%)
- Thread Count
- Active Connections
- Error Rate (%)
- Temperature (°C)
- Power Consumption (W)
- Service Status

### Processing Modes

- **Batch Mode** - Process static JSON files
- **Stream Mode** - Real-time processing via Kafka

## Architecture

```
┌─────────────────┐
│  Input Source   │
│  (JSON/Kafka)   │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────┐
│   Validation & Parsing      │
│   (Pydantic Models)         │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│   Anomaly Detection         │
│   (ML Strategies)           │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│   LLM Recommendations       │
│   (OpenAI Integration)      │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│   Report Generation         │
│   (JSON Output)             │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────┐
│  Output Sink    │
│  (JSON/Kafka)   │
└─────────────────┘
```

## Prerequisites

- **Python** 3.12+
- **uv** (Python package manager) - [Install uv](https://docs.astral.sh/uv/getting-started/installation/)
- **Docker** & **Docker Compose** (for Kafka streaming mode)
- **Git**
- **OpenAI API Key** (optional, for LLM recommendations)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/infrastructure-anomaly-detection.git
cd infrastructure-anomaly-detection
```

### 2. Install Dependencies with uv

```bash
# uv automatically creates and manages virtual environment
uv sync

# Or install specific dependencies
uv pip install -r requirements.txt
```

### 3. Start Kafka Stack (for streaming mode only)

```bash
# Navigate to project root
docker-compose up -d

# Verify services are running
docker-compose ps

# Check logs
docker-compose logs -f kafka
```

### 4. Create Logs Directory

```bash
mkdir -p logs
```

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# Kafka Configuration
KAFKA_BOOTSTRAP_SERVERS=localhost:29092
KAFKA_INPUT_TOPIC=infra-input
KAFKA_OUTPUT_TOPIC=infra-output
KAFKA_TIMEOUT=30

# LLM Configuration
OPENAI_API_KEY=sk-your-api-key-here
LLM_MODEL=gpt-4o

# Application Configuration
LOG_LEVEL=INFO
DEBUG_MODE=False

# Anomaly Detection Configuration
ANOMALY_THRESHOLD=4.0
CONTAMINATION_RATE=0.05
```

### Settings Override

Edit `app/config/settings.py` for permanent configuration changes:

```python
ANOMALY_THRESHOLD = 4.0  # Z-score threshold
CONTAMINATION_RATE = 0.05  # Expected anomaly percentage
```

## Usage

### Batch Mode (Static Files)

#### Basic Usage

```bash
# Using uv run
uv run python -m app.main --mode batch --input /path/to/your/data.json
```

#### Complete Example

```bash
# Process the sample report
uv run python -m app.main --mode batch --input /home/jaadari/Desktop/test_devoteam/rapport.json

# Or use relative path
uv run python -m app.main --mode batch --input ./rapport.json

# With custom anomaly threshold
uv run python -m app.main --mode batch --input ./rapport.json --threshold 3.0
```

#### Example Input File Structure

Your JSON file should have this structure:

```json
{
  "data": [
    {
      "timestamp": "2024-01-05T10:00:00Z",
      "cpu_usage": 45.5,
      "memory_usage": 62.3,
      "latency_ms": 125.5,
      "disk_usage": 78.2,
      "network_in_kbps": 512.3,
      "network_out_kbps": 256.7,
      "io_wait": 15.2,
      "thread_count": 256,
      "active_connections": 1024,
      "error_rate": 0.5,
      "uptime_seconds": 864000,
      "temperature_celsius": 65.2,
      "power_consumption_watts": 850.5,
      "service_status": {
        "database": "online",
        "api_gateway": "online",
        "cache": "degraded"
      }
    },
    {
      "timestamp": "2024-01-05T10:01:00Z",
      "cpu_usage": 95.8,
      "memory_usage": 92.1,
      "latency_ms": 450.2,
      "disk_usage": 95.5,
      "network_in_kbps": 1024.5,
      "network_out_kbps": 512.3,
      "io_wait": 45.8,
      "thread_count": 512,
      "active_connections": 2048,
      "error_rate": 5.2,
      "uptime_seconds": 864000,
      "temperature_celsius": 85.5,
      "power_consumption_watts": 1500.2,
      "service_status": {
        "database": "degraded",
        "api_gateway": "degraded",
        "cache": "offline"
      }
    }
  ]
}
```

#### Expected Output

```json
{
  "timestamp": "2024-01-05T10:00:00+00:00",
  "insights": {
    "average_latency_ms": 287.85,
    "max_cpu_usage": 95.8,
    "max_memory_usage": 92.1,
    "error_rate": 2.85,
    "uptime_seconds": 864000
  },
  "anomalies": [
    {
      "metric": "cpu_usage",
      "value": 95.8,
      "threshold": 68.5,
      "severity": "high",
      "description": "cpu_usage deviates significantly (z-score=3.45)"
    },
    {
      "metric": "multivariate_pattern",
      "value": -0.245,
      "threshold": null,
      "severity": "high",
      "description": "Abnormal system behavior detected across multiple metrics"
    }
  ],
  "recommendations": [
    {
      "id": "rec-001",
      "action": "Scale up CPU resources",
      "target": "compute_instances",
      "parameters": {
        "cpu_cores": 8,
        "priority": "high"
      },
      "benefit_estimate": "30% reduction in CPU bottlenecks"
    }
  ],
  "service_status_summary": {
    "online": ["database"],
    "degraded": ["api_gateway", "cache"],
    "offline": []
  }
}
```

### Streaming Mode (Kafka)

#### 1. Start Kafka

```bash
docker-compose up -d
```

#### 2. Producer Script (in Terminal 1)

```bash
# Publishes messages to Kafka input topic
uv run python app/services/kafka/produce_test_script.py
```

#### 3. Main Application (in Terminal 2)

```bash
# Processes Kafka stream and publishes results
uv run python -m app.main --mode stream
```

#### 4. Consumer Script (in Terminal 3)

```bash
# Consumes results from Kafka output topic
uv run python app/services/kafka/consume_test_script.py
```

#### Stream Mode Output

```
2026-01-05 12:45:30 - app.main - INFO - Starting application in stream mode
[1] Processing 100 events... ✓ (12 anomalies, 4 recommendations)
[2] Processing 100 events... ✓ (8 anomalies, 3 recommendations)
[3] Processing 100 events... ✓ (15 anomalies, 5 recommendations)
```

## Testing

### 1. Create Test Data Files

```bash
# Normal metrics
cat > data/normal_metrics.json << 'EOF'
{
  "data": [
    {
      "timestamp": "2024-01-05T10:00:00Z",
      "cpu_usage": 25.0,
      "memory_usage": 35.0,
      "latency_ms": 50.0,
      "disk_usage": 40.0,
      "network_in_kbps": 100.0,
      "network_out_kbps": 50.0,
      "io_wait": 5.0,
      "thread_count": 100,
      "active_connections": 500,
      "error_rate": 0.1,
      "uptime_seconds": 1000000,
      "temperature_celsius": 50.0,
      "power_consumption_watts": 500.0,
      "service_status": {
        "database": "online",
        "api_gateway": "online",
        "cache": "online"
      }
    }
  ]
}
EOF

# Anomalous metrics
cat > data/anomaly_metrics.json << 'EOF'
{
  "data": [
    {
      "timestamp": "2024-01-05T10:00:00Z",
      "cpu_usage": 98.5,
      "memory_usage": 96.2,
      "latency_ms": 850.0,
      "disk_usage": 99.0,
      "network_in_kbps": 9999.0,
      "network_out_kbps": 9999.0,
      "io_wait": 95.0,
      "thread_count": 1000,
      "active_connections": 10000,
      "error_rate": 15.5,
      "uptime_seconds": 500,
      "temperature_celsius": 98.5,
      "power_consumption_watts": 2500.0,
      "service_status": {
        "database": "offline",
        "api_gateway": "degraded",
        "cache": "offline"
      }
    }
  ]
}
EOF
```

### 2. Run Tests with Different Data

```bash
# Test with normal metrics (should have few/no anomalies)
uv run python -m app.main --mode batch --input data/normal_metrics.json

# Test with anomalous metrics (should detect many anomalies)
uv run python -m app.main --mode batch --input data/anomaly_metrics.json

# Test with your actual data
uv run python -m app.main --mode batch --input rapport.json
```

### 3. Unit Tests

```bash
# Run all tests
uv run pytest tests/ -v

# Run specific test file
uv run pytest tests/test_anomaly_detector.py -v

# Run with coverage
uv run pytest tests/ --cov=app --cov-report=html
```

### 4. Check Logs

```bash
# View today's logs
tail -f logs/app_*.log

# Search for errors
grep ERROR logs/app_*.log

# Search for anomalies
grep "anomalies detected" logs/app_*.log
```

## Project Structure

```
infrastructure-anomaly-detection/
├── app/
│   ├── config/
│   │   ├── __init__.py
│   │   ├── logger.py              # Logging configuration
│   │   └── settings.py            # Application settings
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── input.py               # Input data models
│   │   └── output.py              # Output data models
│   ├── services/
│   │   ├── anomaly_detector/
│   │   │   ├── __init__.py
│   │   │   ├── base.py            # Abstract base class
│   │   │   ├── classic.py         # ML-based detector
│   │   │   ├── factory.py         # Detector factory
│   │   │   └── utils.py           # Utility constants
│   │   ├── kafka/
│   │   │   ├── __init__.py
│   │   │   ├── producer.py        # Kafka producer
│   │   │   ├── consumer.py        # Kafka consumer
│   │   │   ├── produce_test_script.py
│   │   │   └── consume_test_script.py
│   │   ├── llm/
│   │   │   ├── __init__.py
│   │   │   ├── base.py            # LLM base class
│   │   │   └── llm.py             # OpenAI client
│   │   └── workflow.py            # Main workflow orchestration
│   └── main.py                    # Entry point
├── tests/
│   ├── __init__.py
│   ├── test_anomaly_detector.py
│   ├── test_schemas.py
│   ├── test_workflow.py
│   └── integration/
│       └── test_kafka_flow.py
├── logs/                          # Generated runtime logs
├── data/                          # Test data files
├── .env                           # Environment configuration
├── .gitignore
├── docker-compose.yml             # Kafka stack
├── pyproject.toml                 # Project metadata
├── requirements.txt               # Dependencies
└── README.md                      # This file
```

## API Documentation

### Input Schema (InputData)

```python
class InputData(BaseModel):
    timestamp: str                          # ISO 8601 format
    cpu_usage: float                        # 0-100%
    memory_usage: float                     # 0-100%
    latency_ms: float                       # milliseconds
    disk_usage: float                       # 0-100%
    network_in_kbps: float                  # kilobits/second
    network_out_kbps: float                 # kilobits/second
    io_wait: float                          # 0-100%
    thread_count: int                       # active threads
    active_connections: int                 # number
    error_rate: float                       # 0-100%
    uptime_seconds: int                     # seconds
    temperature_celsius: float              # degrees
    power_consumption_watts: float          # watts
    service_status: ServiceStatus           # {database, api_gateway, cache}
```

### Output Schema (FinalReport)

```python
class FinalReport(BaseModel):
    timestamp: str                          # Report generation time (ISO 8601)
    insights: Insight                       # Aggregate metrics
    anomalies: List[Anomaly]               # Detected anomalies
    recommendations: List[Recommendation]   # LLM recommendations
    service_status_summary: ServiceStatusSummary
```

### Anomaly Detection Strategies

#### 1. Statistical (Z-Score)

```bash
# Default strategy - detects individual metric deviations
uv run python -m app.main --mode batch --input data.json
```

#### 2. Multivariate (Isolation Forest)

Edit `app/config/settings.py`:
```python
# Change detector strategy
from app.services.anomaly_detector.utils import DetectionStrategy
strategy = DetectionStrategy.MULTIVARIATE
```

#### 3. PCA-Mahalanobis

Edit `app/config/settings.py`:
```python
strategy = DetectionStrategy.PCA_MAHALANOBIS
```

## Troubleshooting

### Issue: "No such file or directory" with input file

```bash
# Use absolute path
uv run python -m app.main --mode batch --input /home/jaadari/Desktop/test_devoteam/rapport.json

# Or relative path from project root
uv run python -m app.main --mode batch --input ./rapport.json

# Check file exists
ls -lh rapport.json
```

### Issue: "Address already in use" (Kafka)

```bash
# Stop existing containers
docker-compose down

# Remove volumes if needed
docker-compose down -v

# Start fresh
docker-compose up -d
```

### Issue: "No module named 'app'"

```bash
# Ensure you're in the project root
cd /path/to/infrastructure-anomaly-detection

# Resync with uv
uv sync
```

### Issue: JSON parsing error

```bash
# Validate your JSON file
python -c "import json; json.load(open('rapport.json'))"

# Pretty print to check structure
python -c "import json; print(json.dumps(json.load(open('rapport.json')), indent=2))"
```

### Issue: Kafka Connection Timeout

```bash
# Check Kafka is running
docker-compose ps

# Check Kafka logs
docker-compose logs kafka

# Verify bootstrap server
docker exec kafka kafka-broker-api-versions.sh --bootstrap-server localhost:9092
```

### Issue: Empty Anomalies Detection

```bash
# Lower the threshold for more sensitivity
uv run python -m app.main --mode batch --input rapport.json --threshold 2.0

# Check logs
tail -f logs/app_*.log | grep -i anomaly
```

### Viewing Application Logs

```bash
# Real-time logs
tail -f logs/app_*.log

# Search for errors
grep ERROR logs/app_*.log

# Search for specific component
grep "ClassicAnomalyDetector" logs/app_*.log

# Count detected anomalies
grep "anomalies detected" logs/app_*.log | tail -5
```

## Performance Tips

### For Large Files

```bash
# Lower threshold for more sensitivity (detects more anomalies)
uv run python -m app.main --mode batch --input large_file.json --threshold 2.0

# Higher threshold for fewer false positives
uv run python -m app.main --mode batch --input large_file.json --threshold 5.0
```

### For Streaming

Edit `app/config/settings.py`:
```python
CONTAMINATION_RATE = 0.1  # Expect 10% anomalies
ANOMALY_THRESHOLD = 3.0   # Lower sensitivity for streams
```

## Quick Start Checklist

- [ ] Install uv: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- [ ] Clone repository
- [ ] Run `uv sync` in project root
- [ ] Create `.env` file (optional)
- [ ] For batch mode: `uv run python -m app.main --mode batch --input /path/to/data.json`
- [ ] For stream mode: Start Docker `docker-compose up -d`, then run producer/main/consumer
- [ ] Check logs in `logs/` directory for detailed information

## Real-World Example

```bash
# Using the provided rapport.json
uv run python -m app.main --mode batch --input /home/jaadari/Desktop/test_devoteam/rapport.json

# With lower threshold for more anomalies
uv run python -m app.main --mode batch --input /home/jaadari/Desktop/test_devoteam/rapport.json --threshold 3.0

# Save output to file
uv run python -m app.main --mode batch --input /home/jaadari/Desktop/test_devoteam/rapport.json > analysis_results.json
```

## Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/my-feature`
3. Commit changes: `git commit -am 'Add my feature'`
4. Push to branch: `git push origin feature/my-feature`
5. Submit pull request

## License

This project is licensed under the MIT License - see LICENSE file for details.

---

## Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check existing documentation
- Review logs in `logs/app_*.log`
- Validate your JSON input file structure

Happy monitoring! 🚀
