from aiokafka import AIOKafkaProducer
import asyncio
import json
from app.config.logger import setup_logger
from app.config.settings import KAFKA_TIMEOUT

logger = setup_logger(__name__)

class AsyncEventProducer:
    """Async Kafka producer for event publishing."""
    
    def __init__(self, topic: str, bootstrap_servers: str):
        self.topic = topic
        self.bootstrap_servers = bootstrap_servers
        self.producer = None
        logger.info(f"Initialized AsyncEventProducer for topic: {topic}")

    async def start(self):
        """Start the Kafka producer."""
        try:
            self.producer = AIOKafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda m: json.dumps(m).encode('utf-8'),
                request_timeout_ms=KAFKA_TIMEOUT * 1000
            )
            await self.producer.start()
            logger.info(f"Producer started for {self.topic}")
        except Exception as e:
            logger.error(f"Error starting producer: {str(e)}", exc_info=True)
            raise

    async def stop(self):
        """Stop the Kafka producer."""
        if self.producer:
            try:
                await self.producer.stop()
                logger.info(f"Producer stopped for {self.topic}")
            except Exception as e:
                logger.error(f"Error stopping producer: {str(e)}", exc_info=True)

    async def send(self, data: dict):
        """Send event to Kafka."""
        try:
            await self.producer.send_and_wait(self.topic, data)
            logger.debug(f"Event sent to {self.topic}")
        except Exception as e:
            logger.error(f"Error sending event: {str(e)}", exc_info=True)
            raise