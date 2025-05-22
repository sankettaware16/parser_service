import os
import yaml
import json
from datetime import datetime
import argparse
from regex_loader import extract_fields

# Load service-to-keywords mapping
with open('/etc/parser_service/config/services.yaml', 'r') as f:
    service_map = yaml.safe_load(f)

def detect_service(log_line):
    for service, keywords in service_map.items():
        if any(keyword in log_line for keyword in keywords):
            return service
    return "unknown"

def parse_log_file(file_path):
    parsed_logs = {}
    failed_logs = {}
    total = 0
    success = 0
    failed = 0

    with open(file_path, 'r') as f:
        lines = f.readlines()

    for line in lines:
        total += 1
        line = line.strip()
        if not line:
            continue

        service = detect_service(line)
        extracted, matched_patterns = extract_fields(line)

        if extracted:
            structured_log = {
                'timestamp': datetime.now().isoformat(),
                'service': service,
                'matched_patterns': matched_patterns,
                'fields': extracted,
                'raw': line
            }
            parsed_logs.setdefault(service, []).append(structured_log)
            success += 1
        else:
            failed_logs.setdefault(service, []).append({'raw': line})
            failed += 1

    return parsed_logs, failed_logs, total, success, failed

def save_output(logs, suffix):
    output_dir = "/etc/parser_service/output/"
    os.makedirs(output_dir, exist_ok=True)

    for service, entries in logs.items():
        filename = f"{service}_{suffix}.json"
        with open(os.path.join(output_dir, filename), 'w') as f:
            json.dump(entries, f, indent=4)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Local log file parser for testing")
    parser.add_argument("file", help="Path to the local .log file")
    args = parser.parse_args()

    parsed_logs, failed_logs, total, success, failed = parse_log_file(args.file)

    save_output(parsed_logs, "parsed")
    save_output(failed_logs, "failed")

    print("\n Parsing Summary:")
    print(f"  Total logs    : {total}")
    print(f"  Parsed logs   : {success}")
    print(f"  Failed logs   : {failed}")
    print("\nOutput saved to /etc/parser_service/output/")
