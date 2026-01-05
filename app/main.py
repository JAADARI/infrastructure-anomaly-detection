import argparse
import json
import asyncio
from app.services.workflow import InfraWorkflow
from app.services.kafka.consumer import AsyncEventConsumer
from app.services.kafka.producer import AsyncEventProducer
from app.config.settings import (
    KAFKA_BOOTSTRAP_SERVERS, 
    KAFKA_INPUT_TOPIC, 
    KAFKA_OUTPUT_TOPIC,
    ANOMALY_THRESHOLD
)
from app.config.logger import setup_logger

logger = setup_logger(__name__)

def main():
    """Main entry point for batch and streaming modes."""
    parser = argparse.ArgumentParser(description="Infrastructure Anomaly Detection System")
    parser.add_argument('--mode', choices=['batch', 'stream'], default='batch',
                       help='Execution mode: batch or stream')
    parser.add_argument('--input', help='Path to input JSON file (batch mode)')
    args = parser.parse_args()

    try:
        workflow = InfraWorkflow(
            anomaly_config={
                "detector_type": "classic",
                "threshold": ANOMALY_THRESHOLD
            }
        )
        
        if args.mode == 'batch':
            batch_mode(workflow, args.input)
        else:
            asyncio.run(stream_mode(workflow))
            
    except Exception as e:
        logger.critical(f"Fatal error in main: {str(e)}", exc_info=True)
        raise

def batch_mode(workflow: InfraWorkflow, input_file: str):
    """Process data in batch mode."""
    try:
        logger.info(f"Starting batch mode with input: {input_file}")
        
        with open(input_file, 'r') as f:
            data = json.load(f)
        
        if isinstance(data, dict) and "data" in data:
            data = data["data"]
        
        logger.info(f"Loaded {len(data)} records from {input_file}")
        
        report = workflow.process(data)
        
        with open("final_report.json", "w", encoding="utf-8") as f:
            json.dump(json.loads(report.model_dump_json()), f, indent=2, ensure_ascii=False)

        logger.info("Batch processing completed successfully")
        
    except FileNotFoundError:
        logger.error(f"Input file not found: {input_file}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in input file: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error in batch mode: {str(e)}", exc_info=True)
        raise

async def stream_mode(workflow: InfraWorkflow):
    """Process data in streaming mode."""
    consumer = AsyncEventConsumer(KAFKA_INPUT_TOPIC, KAFKA_BOOTSTRAP_SERVERS)
    producer = AsyncEventProducer(KAFKA_OUTPUT_TOPIC, KAFKA_BOOTSTRAP_SERVERS)
    
    await consumer.start()
    await producer.start()
    
    try:
        logger.info(f"Started streaming mode: {KAFKA_INPUT_TOPIC} -> {KAFKA_OUTPUT_TOPIC}")
        
        async for event in consumer.consume():
            try:
                logger.debug("Processing event from stream")
                report = workflow.process(event if isinstance(event, list) else [event])
                output = json.loads(report.model_dump_json())
                await producer.send(output)
            except Exception as e:
                logger.error(f"Error processing stream event: {str(e)}", exc_info=True)
                
    finally:
        await consumer.stop()
        await producer.stop()

if __name__ == "__main__":
    main()