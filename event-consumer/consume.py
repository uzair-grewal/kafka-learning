import json
from kafka import KafkaConsumer
from common.kafka_config import get_kafka_consumer_config
from event_serializer.avro_serializer import AvroService  # Import your local registry service
from .router import handle_routing
from .produce import send_to_kafka

# 1. Fetch the config
config = get_kafka_consumer_config('student-router-group')

# 2. Initialize Consumer and Avro Service
consumer = KafkaConsumer('student_updates', **config)
avro_svc = AvroService()

# 3. Get the decoder specifically for this topic
# This handles the Magic Byte and Schema ID lookup automatically
avro_decode = avro_svc.get_deserializer('student_updates')

def start_consuming():
    print(f"Consumer '{config['group_id']}' is listening...")
    try:
        for message in consumer:
            # message.value is currently binary (b'\x00\x00\x00\x00\x01...')
            # We decode it into a readable dictionary
            try:
                print(f"Received message: {message.value[:20]}... (total {len(message.value)} bytes)")
                event = avro_decode(message.value)
                print(f"Decoded event: {event}")
            except Exception as decode_error:
                print(f"Failed to decode Avro message: {decode_error}")
                continue

            # Now 'event' is a dict: {'student_id': 1, 'event_type': 'INSERT', ...}
            destination = handle_routing(event)
            
            if destination:
                # Forward the event (Produce will re-encode it for the new topic)
                status = send_to_kafka(destination, event)
                if status:
                    print(f"Routed to {destination}")
                else:
                    print(f"Failed to route to {destination}")
            else:
                # Accessing keys safely from the decoded dict
                event_type = event.get('event_type', 'UNKNOWN')
                print(f"Skipping forward: No destination for {event_type}")
                
    except Exception as e:
        print(f"❌ Consumer Error: {e}")
    finally:
        consumer.close()

if __name__ == "__main__":
    start_consuming()