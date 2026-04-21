import io
import json
import os
from quopri import decode
from fastavro import schemaless_reader, schemaless_writer, parse_schema

class AvroService:
    def __init__(self):
        # We use a local JSON file to act as our "Registry"
        self.registry_file = 'local_schema_registry.json'
        self._ensure_registry_exists()

    def _ensure_registry_exists(self):
        if not os.path.exists(self.registry_file):
            with open(self.registry_file, 'w') as f:
                json.dump({}, f)

    def get_serializer(self, topic, schema_dict):
        subject = f"{topic}-value"
        
        # 1. Check/Assign ID locally
        schema_id = self._get_or_assign_id(subject, schema_dict)
        
        # 2. Parse schema for the writer
        parsed_schema = parse_schema(schema_dict)

        def encode(record):
            with io.BytesIO() as out:
                # Still use the 5-byte Wire Format header
                # This makes your data "Registry Compatible" for the future
                out.write(b'\x00')          # Magic Byte
                out.write(schema_id.to_bytes(4, 'big'))
                schemaless_writer(out, parsed_schema, record)
                return out.getvalue()
        
        return encode
    
    def get_deserializer(self, topic):
        """Mocks the Registry lookup to decode binary Avro."""
        with open(self.registry_file, 'r') as f:
            data = json.load(f)
        
        subject = f"{topic}-value"
        # Get the schema associated with this topic from our local 'database'
        parsed_schema = parse_schema(data[subject]['schema'])

        def decode(binary_data):
            # Skip the 5-byte header (Magic Byte + Schema ID) 
            # because our local mock only uses one schema per topic anyway
            payload_reader = io.BytesIO(binary_data[5:]) 
            return schemaless_reader(payload_reader, parsed_schema)
        
        return decode

    def _get_or_assign_id(self, subject, schema):
        """Mocks the 'Check or Create' logic of a real registry."""
        with open(self.registry_file, 'r') as f:
            data = json.load(f)

        # If subject exists, return ID. If not, create it.
        if subject not in data:
            new_id = len(data) + 1
            data[subject] = {"id": new_id, "schema": schema}
            with open(self.registry_file, 'w') as f:
                json.dump(data, f, indent=4)
            return new_id
        
        return data[subject]['id']