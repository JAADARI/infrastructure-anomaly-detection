from aiokafka import AIOKafkaConsumer
import json
from app.config.logger import setup_logger

logger = setup_logger(__name__)

class AsyncEventConsumer:
    """Async Kafka consumer for event consumption."""
    
    def __init__(self, topic: str, bootstrap_servers: str, group_id: str = "infra-anomaly-group"):
        self.topic = topic
        self.bootstrap_servers = bootstrap_servers
        self.group_id = group_id
        self.consumer = None
        logger.info(f"Initialized AsyncEventConsumer for topic: {topic}, group: {group_id}")

    async def start(self):
        """Start the Kafka consumer."""
        try:
            self.consumer = AIOKafkaConsumer(
                self.topic,
                bootstrap_servers=self.bootstrap_servers,
                group_id=self.group_id,
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                auto_offset_reset='earliest',
                enable_auto_commit=True
            )
            await self.consumer.start()
            logger.info(f"Consumer started for {self.topic}")
        except Exception as e:
            logger.error(f"Error starting consumer: {str(e)}", exc_info=True)
            raise

    async def stop(self):
        """Stop the Kafka consumer."""
        if self.consumer:
            try:
                await self.consumer.stop()
                logger.info(f"Consumer stopped for {self.topic}")
            except Exception as e:
                logger.error(f"Error stopping consumer: {str(e)}", exc_info=True)

    async def consume(self):
        """Consume events from Kafka."""
        try:
            async for message in self.consumer:
                logger.debug(f"Received message from {self.topic}")
                yield message.value
        except Exception as e:
            logger.error(f"Error consuming messages: {str(e)}", exc_info=True)
        finally:
            await self.stop()