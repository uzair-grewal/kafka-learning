from kafka import KafkaProducer
from common.kafka_config import get_kafka_producer_config
import json

# Pass the ID directly as a parameter
config = get_kafka_producer_config('student-outbox-poller')
producer = KafkaProducer(**config)

def send_to_kafka(topic, value_dict, key=None):
    try:
        key_bytes = str(key).encode('utf-8') if key else None
        print(f"Sending to Kafka topic '{topic}' with key '{key_bytes}'")

        json_bytes = json.dumps(value_dict).encode('utf-8')
        print(f"Serialized JSON bytes: {json_bytes[:20]}... (total {len(json_bytes)} bytes)")
    
        
        future = producer.send(topic, value=json_bytes, key=key_bytes)
        future.get(timeout=30)
        return True
    except Exception as e:
        print(f"Kafka Production Error: {e}")
        return False
