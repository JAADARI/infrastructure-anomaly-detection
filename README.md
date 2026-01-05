### 🚀 Infrastructure Anomaly Detection System

- **Stack**
  - **Python**: Core language
  - **LangGraph**: Workflow orchestration
  - **Instructor**: wrapper for LLM providers for recommendations with **structured outputs** 
  - **Pydantic**: Data validation and schema enforcement
  - **scikit-learn**: Machine learning algorithms
  - **Apache Kafka** + **aiokafka**: Real-time streaming
  - **JSON**: Batch data format

- **Design**
  - **Hybrid architecture**: Real-time streaming + batch processing
  - **Multi-step pipelines**: Deterministic workflow with state transitions
  - **Anomaly detection engine**: Z-score, Isolation Forest, PCA-Mahalanobis
  - **Observability**: Structured logging across pipelines and LLM calls
  - **Data safety**: Type-safe recommendations via validated schemas

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
git clone https://github.com/JAADARI/infrastructure-anomaly-detection.git
cd infrastructure-anomaly-detection
```

### 2. Install Dependencies with uv

```bash
# uv automatically creates and manages virtual environment
uv sync
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


## Configuration

### Environment Variables

Create a `.env` file in the project root (or export variables in your shell):

```bash
# Kafka Configuration
KAFKA_BOOTSTRAP_SERVERS=localhost:29092
KAFKA_INPUT_TOPIC=infra-input
KAFKA_OUTPUT_TOPIC=infra-output
KAFKA_TIMEOUT=30

# LLM Configuration (Instructor provider)
LLM_BASE_URL=https://openrouter.ai/api/v1
LLM_API_KEY=sk-your-api-key-here
LLM_MODEL=openrouter/mistralai/devstral-2512:free

# Application Configuration
LOG_LEVEL=INFO
DEBUG_MODE=False

# Anomaly Detection Configuration
ANOMALY_THRESHOLD=4.0
CONTAMINATION_RATE=0.05
```

## Usage

### Batch Mode (Static Files)

#### Basic Usage

```bash
# Using uv run
uv run python -m app.main --mode batch --input /path/to/your/data.json
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

## License

This project is licensed under the MIT License - see LICENSE file for details.

---





