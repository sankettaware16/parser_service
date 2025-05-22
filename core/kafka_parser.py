import json
import sys
import os
from datetime import datetime, timezone
import yaml
from kafka import KafkaConsumer

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
TOPICS = topic_config['topics']  # Topics loaded dynamically from the YAML file

# Kafka Consumer setup
consumer = KafkaConsumer(
    *TOPICS,
    bootstrap_servers=[KAFKA_BROKER],
    auto_offset_reset='latest',
    enable_auto_commit=True,
    group_id='multi-parser-group',
    value_deserializer=lambda m: m.decode('utf-8')
)

print(f"Listening to Kafka topics: {TOPICS}")

# Make sure output dir exists
OUTPUT_DIR = '/etc/parser_service/output/'
os.makedirs(OUTPUT_DIR, exist_ok=True)

def save_to_service_file(service_name, raw_log, parsed_data):
    # Generate a unique file for each service (topic)
    service_file = os.path.join(OUTPUT_DIR, f"{service_name}_logs.json")

    # Create the JSON structure
    log_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": service_name,
        "original_log": raw_log,
        "parsed_data": parsed_data
    }

    # Save the parsed data in the service-specific JSON file
    with open(service_file, 'a') as f:
        f.write(json.dumps(log_entry) + '\n')  # Append log entry

# Start consuming and saving to the appropriate service file
for message in consumer:
    raw_log = message.value.strip()
    service_name = message.topic  # Topic name corresponds to the service name

    # Extract fields using the regex loader
    parsed_data, matched = extract_fields(raw_log)

    # Save parsed data in service-specific file
    save_to_service_file(service_name, raw_log, parsed_data)

    # Debug output
    if matched:
        print(f"Matched: {matched}")
    else:
        print("No regex matched!")

    print(f"Parsed Fields: {parsed_data}\n")
