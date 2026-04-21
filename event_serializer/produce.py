import os
from kafka import KafkaProducer
from common.kafka_config import get_kafka_producer_config
from .avro_serializer import AvroService
from .serialize import STUDENT_EVENT_SCHEMA

# Setup
TOPIC = os.getenv('KAFKA_TOPIC', 'student_updates')
producer_config = get_kafka_producer_config('student-service-poller')

# Initialize Avro Service & Producer
avro_svc = AvroService()
avro_encode = avro_svc.get_serializer(TOPIC, STUDENT_EVENT_SCHEMA)
producer = KafkaProducer(**producer_config)
print("Kafka config:", producer_config)
print("bootstrap connected:", producer.bootstrap_connected())
print("partitions for topic:", producer.partitions_for(TOPIC))

def send_to_kafka(event_dict):
    try:
        # Most efficient: Convert to Avro bytes once
        binary_value = avro_encode(event_dict)
        print(f"Encoded Avro bytes: {binary_value[:20]}... (total {len(binary_value)} bytes)")
        
        # Send raw bytes - Kafka handles this the fastest
        key_bytes = str(event_dict['student_id']).encode('utf-8') if 'student_id' in event_dict else None
        print(f"Sending to Kafka topic '{TOPIC}' with key '{key_bytes}'")

        # .send() pushes to the internal buffer
        future = producer.send(
            TOPIC, 
            value=binary_value, 
            key=key_bytes
        )
        future.get(timeout=30)
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False