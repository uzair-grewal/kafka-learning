import json
from datetime import datetime

# The Schema follows your DB: notification_id, student_id, action_type, payload
STUDENT_EVENT_SCHEMA = {
    "type": "record",
    "name": "StudentNotification",
    "namespace": "com.school.notifications",
    "fields": [
        {
            "name": "metadata",
            "type": {
                "type": "record",
                "name": "EventMetadata",
                "fields": [
                    {"name": "notification_id", "type": "int"},
                    {"name": "timestamp", "type": "string"},
                    {"name": "status", "type": "string"}
                ]
            }
        },
        {"name": "student_id", "type": "int"},
        {"name": "action_type", "type": "string"},
        {"name": "payload", "type": "string"} # Stores the jsonb data as a string
    ]
}

def serialize_student_event(row):
    """
    Maps the DB row columns directly to the Avro schema.
    """
    return {
        "metadata": {
            "notification_id": int(row['notification_id']),
            "timestamp": row['created_at'].isoformat() if hasattr(row['created_at'], 'isoformat') else str(row['created_at']),
            "status": row['status']
        },
        "student_id": int(row['student_id']),
        "action_type": row['action_type'],
        # Convert the jsonb (dict) to a string so it fits the Avro "string" type
        "payload": json.dumps(row['payload']) if isinstance(row['payload'], (dict, list)) else str(row['payload'])
    }