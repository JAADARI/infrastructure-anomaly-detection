import asyncio
import json
from aiokafka import AIOKafkaConsumer

KAFKA_BOOTSTRAP_SERVERS = "localhost:29092"
KAFKA_OUTPUT_TOPIC = "infra-output"

async def consume():
    consumer = AIOKafkaConsumer(
        KAFKA_OUTPUT_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id="output-consumer-group",
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        auto_offset_reset='earliest',
        enable_auto_commit=True
    )
    await consumer.start()
    try:
        print(f"Consuming from topic: {KAFKA_OUTPUT_TOPIC}")
        async for message in consumer:
            print("\n=== Output Message ===")
            print(json.dumps(message.value, indent=2))
    finally:
        await consumer.stop()

if __name__ == "__main__":
    asyncio.run(consume())