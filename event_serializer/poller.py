import time
from psycopg2.extras import RealDictCursor
from .serialize import serialize_student_event
from .produce import send_to_kafka
from common.db import get_direct_connection

def run_polling_service():
    conn = get_direct_connection()
    # Use a persistent cursor for the loop
    cur = conn.cursor(cursor_factory=RealDictCursor)

    print("Starting Polling Service (SASL_SSL + Avro Enabled)...")

    while True:
        try:
            # Fetch PENDING rows. SKIP LOCKED prevents multiple pollers 
            # from grabbing the same data.
            cur.execute("""
                SELECT * FROM notifications 
                WHERE status = 'PENDING' 
                ORDER BY created_at ASC LIMIT 5 
                FOR UPDATE SKIP LOCKED;
            """)
            
            rows = cur.fetchall()
            
            if not rows:
                # No data? Sleep a bit longer to save CPU/DB resources
                print("No pending notifications. Waiting...")
                time.sleep(5)

            for row in rows:
                # Step 1: Transform DB row to a clean Dictionary (via utils/serialize.py)
                # Note: We no longer get bytes here; we get a dict ready for Avro.
                print(f"Processing ID: {row['notification_id']} for Student ID: {row['student_id']}")
                event_dict = serialize_student_event(row)
                
                # Step 2: Send to Kafka (via produce.py)
                # This function now handles:
                # - Connecting via SASL_SSL
                # - Checking/Evolving the Avro Schema
                # - Converting Dict to Binary
                print(f"Sending to Kafka: {event_dict}")
                success = send_to_kafka(event_dict)
                
                # Step 3: Update DB if successful
                if success:
                    cur.execute(
                        "UPDATE notifications SET status = 'PROCESSED' WHERE notification_id = %s",
                        (row['notification_id'],)
                    )
                    print(f"✅ Processed ID: {row['notification_id']}")
                else:
                    print(f"❌ Failed to process ID: {row['notification_id']}")
                    break; # Exit loop to retry the batch on failure
            
            # Commit the batch
            conn.commit()
            
        except Exception as e:
            conn.rollback()
            print(f"Polling Error: {e}")
            time.sleep(5) # Wait before retry on DB error

        time.sleep(2)

if __name__ == "__main__":
    run_polling_service()