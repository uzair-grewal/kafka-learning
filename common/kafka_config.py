import os
import ssl
from dotenv import load_dotenv

load_dotenv()

def get_security_config():
    security_protocol = os.getenv('KAFKA_SECURITY_PROTOCOL', 'PLAINTEXT')
    config = {'security_protocol': security_protocol}

    if 'SASL' in security_protocol:
        config.update({
            'sasl_mechanism': os.getenv('KAFKA_SASL_MECHANISM', 'PLAIN'),
            'sasl_plain_username': os.getenv('KAFKA_SASL_USERNAME'),
            'sasl_plain_password': os.getenv('KAFKA_SASL_PASSWORD'),
        })

    if security_protocol in ('SSL', 'SASL_SSL'):
        config.update({
            'ssl_cafile': os.getenv('KAFKA_SSL_CAFILE'),
            'ssl_certfile': os.getenv('KAFKA_SSL_CERTFILE'),
            'ssl_keyfile': os.getenv('KAFKA_SSL_KEYFILE'),
            'ssl_check_hostname': os.getenv('KAFKA_SSL_CHECK_HOSTNAME', 'true').lower() == 'true',
        })
    return config

def get_kafka_producer_config(client_id):
    """Configuration for KafkaProducer."""
    config = {
        'bootstrap_servers': os.getenv('KAFKA_BOOTSTRAP_SERVERS', '172.26.247.238:9092').split(','),
        'client_id': client_id,
        'acks': 'all',
        'retries': 5,
    }
    config.update(get_security_config())
    return config

def get_kafka_consumer_config(client_id):
    """Configuration for KafkaConsumer."""
    config = {
        'bootstrap_servers': os.getenv('KAFKA_BOOTSTRAP_SERVERS', '172.26.247.238:9092').split(','),
        'group_id': client_id,
        'auto_offset_reset': 'earliest',
        'enable_auto_commit': True,
    }
    config.update(get_security_config())
    return config
