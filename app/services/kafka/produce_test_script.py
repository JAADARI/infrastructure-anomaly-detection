import asyncio
import json
from aiokafka import AIOKafkaProducer

KAFKA_BOOTSTRAP_SERVERS = "localhost:29092"
KAFKA_INPUT_TOPIC = "infra-input"
JSON_FILE_PATH = "rapport.json"  # Path to your JSON file

async def produce():
    producer = AIOKafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda m: json.dumps(m).encode('utf-8')
    )
    await producer.start()
    try:
        # Load data from JSON file
        with open(JSON_FILE_PATH, 'r') as f:
            data = json.load(f)
        
        # Handle different JSON structures
        if isinstance(data, dict) and "data" in data:
            entries = data["data"]
        elif isinstance(data, list):
            entries = data
        else:
            print("Error: JSON file must contain a list or a dict with 'data' key")
            return
        
        print(f"Loaded {len(entries)} entries from {JSON_FILE_PATH}")
        
        batch_count = 0
        entry_index = 0
        
        while True:
            batch_count += 1
            print(f"\n=== Batch {batch_count} ===")
            print("Creating a batch of 100 entries...")
            
            # Collect 100 entries into a single list
            batch = []
            for i in range(100):
                entry = entries[entry_index % len(entries)]
                batch.append(entry)
                entry_index += 1
            
            # Send the batch as a SINGLE message (list of 100 entries)
            await producer.send_and_wait(KAFKA_INPUT_TOPIC, batch)
            
            print(f"✓ Batch {batch_count} sent (1 message containing 100 entries)")
            print("Waiting 60 seconds before next batch...")
            
            # Wait 60 seconds before sending the next batch
            await asyncio.sleep(60)
    except FileNotFoundError:
        print(f"Error: {JSON_FILE_PATH} not found. Please create this file with your test data.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await producer.stop()

if __name__ == "__main__":
    asyncio.run(produce())