import json
import sys
import os
from datetime import datetime, timezone
import yaml
from kafka import KafkaConsumer
import time

# Add core directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.regex_loader import extract_fields

# Load topics from YAML config
CONFIG_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', 'config', 'kafka_config.yaml')
)

with open(CONFIG_PATH, 'r') as f:
    topic_config = yaml.safe_load(f)

KAFKA_BROKER = topic_config['broker']
TOPICS = topic_config['topics']

# --- BATCHING CONFIGURATION ---
# The script will write to disk when either of these conditions is met:
BATCH_SIZE = 1000  # The number of messages to collect before writing
BATCH_TIMEOUT = 5  # The max number of seconds to wait before writing (for low-volume times)

# Kafka Consumer setup
consumer = KafkaConsumer(
    *TOPICS,
    bootstrap_servers=[KAFKA_BROKER],
    auto_offset_reset='latest',
    enable_auto_commit=True,
    group_id='multi-parser-group-batch', # Use a new group_id to ensure it starts fresh
    value_deserializer=lambda m: m.decode('utf-8')
)

print(f"Listening to Kafka topics: {TOPICS}")
print(f"Batching configuration: Size={BATCH_SIZE}, Timeout={BATCH_TIMEOUT}s")

OUTPUT_DIR = '/etc/parser_service_mail/output/'
os.makedirs(OUTPUT_DIR, exist_ok=True)

def save_batch_to_files(batch):
    """
    Efficiently saves a batch of log entries to their respective service files.
    """
    if not batch:
        return

    # Group logs by service to write to the correct files (e.g., postfix_logs.json)
    logs_by_service = {}
    for entry in batch:
        service = entry['service']
        if service not in logs_by_service:
            logs_by_service[service] = []
        # Convert the Python dictionary to a JSON string
        logs_by_service[service].append(json.dumps(entry))

    # Write each service's logs to its file in one operation
    for service, log_jsons in logs_by_service.items():
        service_file = os.path.join(OUTPUT_DIR, f"{service}_logs.json")
        try:
            with open(service_file, 'a') as f:
                # Join all JSON strings with newlines and write them all at once
                f.write('\n'.join(log_jsons) + '\n')
        except Exception as e:
            print(f"Error writing to {service_file}: {e}")
    
    print(f" Successfully wrote a batch of {len(batch)} logs to disk.")


# --- Main consumption loop with batching logic ---
log_batch = []
last_write_time = time.time()

try:
    for message in consumer:
        raw_log = message.value.strip()
        service_name = message.topic

        parsed_data, _ = extract_fields(raw_log)

        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "service": service_name,
            "original_log": raw_log,
            "parsed_data": parsed_data
        }
        
        log_batch.append(log_entry)

        # Check if it's time to write the batch to disk
        now = time.time()
        if len(log_batch) >= BATCH_SIZE or (now - last_write_time > BATCH_TIMEOUT and log_batch):
            save_batch_to_files(log_batch)
            log_batch = [] # Reset the batch
            last_write_time = now

except KeyboardInterrupt:
    print("\nShutdown detected. Writing final batch...")
    save_batch_to_files(log_batch) # Ensure any remaining logs are saved
    consumer.close()
    print("Kafka consumer closed. Exiting.")

    
