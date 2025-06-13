#  Trust Labs Parser Service

A lightweight, modular log parser designed for Security Operations Centers (SOCs). Built to support 
multiple services (like Postfix, Roundcube) with easy extensibility and real-time log forwarding via Kafka and Elasticsearch.

---

##  Project Structure

/etc/parser_service/
├── config/
│ ├── kafka_config.yaml # Kafka broker and topic configuration
│ └── services.yaml # Maps service keywords to parser classes
├── core/
│ ├── regex_loader.py # Loads regex patterns from YAML
│ └── kafka_parser.py # Kafka consumer/parser integration
├── elastic/  Elasticsearch integration
├── output/
│ ├── mail_login_logs.json # Sample output logs
│ └── postfix_logs.json
├── regexes/
│ ├── postfix/patterns.yaml # Regex patterns for Postfix logs
│ └── roundcube/patterns.yaml # Regex patterns for Roundcube logs


to test you logs there  log_test.py in /core/
just run python3 log_test.py /to/the/path/test.log

##  Requirements

Make sure you have the following installed:
- Python 3.8+
- pip (Python package manager)
- Kafka (running broker)
- Elasticsearch (optional for final log storage)
- 
## Configuration

1. config/kafka_config.yaml
yaml
Copy
Edit
bootstrap_servers: "<KAFKAIP>"
topic: "add_you_topic_name"
group_id: "parser_service"

2. config/services.yaml
yaml
Copy
Edit
roundcube: roundcube_parser.RoundcubeParser
postfix: postfix_parser.PostfixParser


## How to Run
make setup.sh executable using chmod +x setup.sh

then run ./setup.sh

this will install all the requirements

run the main file 
cd /etc/parser_service/

python3 core/kafka_parser.py

The service will:

Listen to Kafka topic

Parse incoming logs using regex

Output structured JSON to output/

Forward logs to Elasticsearch(still working on it)


# RUN AS SERVICE
if want this parser to run as a service 

make sure your dir looks like /etc/parser_service

make install_as_service.sh executanle

chmod +x install_as_service.sh

verify by 

systemctl status parser
