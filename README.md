# Kafka Streaming Service

This project demonstrates a Kafka-based event streaming architecture with producers, consumers, and schema serialization using Avro.

## Prerequisites

- Python 3.8+
- Apache Kafka (latest version, using KRaft mode)
- PostgreSQL
- Git

## PostgreSQL Setup

1. Install and start PostgreSQL.

2. Create a database and user:
   ```
   createdb your_db_name
   createuser your_db_user
   psql -c "ALTER USER your_db_user PASSWORD 'your_db_password';"
   psql -c "GRANT ALL PRIVILEGES ON DATABASE your_db_name TO your_db_user;"
   ```

3. Create tables and trigger:
   ```sql
   -- Connect to your database
   psql -d your_db_name -U your_db_user

   -- Students table
   CREATE TABLE students (
       student_id SERIAL PRIMARY KEY,
       first_name VARCHAR(50),
       last_name VARCHAR(50),
       email VARCHAR(100)
   );

   -- Notifications table for events
   CREATE TABLE notifications (
       notification_id SERIAL PRIMARY KEY,
       student_id INT,
       action_type VARCHAR(10),
       payload JSONB,
       status VARCHAR(20) DEFAULT 'PENDING',
       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
   );

   -- Function for trigger
   CREATE OR REPLACE FUNCTION notify_student_changes() RETURNS TRIGGER AS $$
   BEGIN
       INSERT INTO notifications (student_id, action_type, payload, status)
       VALUES (COALESCE(NEW.student_id, OLD.student_id), TG_OP, row_to_json(NEW), 'PENDING');
       RETURN NEW;
   END;
   $$ LANGUAGE plpgsql;

   -- Trigger
   CREATE TRIGGER student_changes_trigger
       AFTER INSERT OR UPDATE OR DELETE ON students
       FOR EACH ROW EXECUTE FUNCTION notify_student_changes();
   ```

## Kafka Setup

Use the latest Kafka version with KRaft mode (no Zookeeper needed). This setup includes SASL authentication.

### SASL Configuration

1. Create `config/server.jaas.conf` in your Kafka directory:
   ```
   KafkaServer {
       org.apache.kafka.common.security.plain.PlainLoginModule required
       username="admin"
       password="admin-secret"
       user_admin="admin-secret"
       user_alice="alice-secret";
   };
   ```

2. Update `config/server.properties` to enable SASL:
   ```
   listeners=SASL_PLAINTEXT://localhost:9092
   security.inter.broker.protocol=SASL_PLAINTEXT
   sasl.mechanism.inter.broker.protocol=PLAIN
   sasl.enabled.mechanisms=PLAIN
   authorizer.class.name=kafka.security.authorizer.AclAuthorizer
   allow.everyone.if.no.acl.found=true
   ```

3. Create `config/client.properties` for client authentication:
   ```
   security.protocol=SASL_PLAINTEXT
   sasl.mechanism=PLAIN
   sasl.jaas.config=org.apache.kafka.common.security.plain.PlainLoginModule required username="admin" password="admin-secret";
   ```

### Starting Kafka

1. Download Kafka from [kafka.apache.org](https://kafka.apache.org/downloads).

2. Extract and navigate to the Kafka directory.

3. Set environment variable for JAAS config:
   ```
   export KAFKA_OPTS="-Djava.security.auth.login.config=/path/to/kafka/config/server.jaas.conf"
   ```

4. In Terminal 1:
   ```
   rm -rf /tmp/kraft-combined-logs/*
   K_ID=$(bin/kafka-storage.sh random-uuid)
   bin/kafka-storage.sh format --standalone -t $K_ID -c config/server.properties
   bin/kafka-server-start.sh config/server.properties
   ```

5. In Terminal 2:
   ```
   export KAFKA_OPTS="-Djava.security.auth.login.config=/path/to/kafka/config/server.jaas.conf"
   cd /path/to/kafka

   # Create topics
   bin/kafka-topics.sh --bootstrap-server localhost:9092 --create --topic student-updates --partitions 3 --replication-factor 1 --command-config config/client.properties
   bin/kafka-topics.sh --bootstrap-server localhost:9092 --create --topic student_registrations --partitions 3 --replication-factor 1 --command-config config/client.properties
   bin/kafka-topics.sh --bootstrap-server localhost:9092 --create --topic student_profile_changes --partitions 3 --replication-factor 1 --command-config config/client.properties

   # List topics
   bin/kafka-topics.sh --bootstrap-server localhost:9092 --list --command-config config/client.properties
   ```

   To test consumer:
   ```
   bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic student_profile_changes --from-beginning --consumer.config config/client.properties
   ```

## Environment Configuration

Create a `.env` file in the root directory with the following variables:

```
# Database
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432

# Kafka
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_TOPIC=student_updates
KAFKA_SECURITY_PROTOCOL=PLAINTEXT

# Optional for SASL/SSL
KAFKA_SASL_MECHANISM=PLAIN
KAFKA_SASL_USERNAME=your_username
KAFKA_SASL_PASSWORD=your_password
KAFKA_SSL_CAFILE=path/to/ca.pem
KAFKA_SSL_CERTFILE=path/to/client.pem
KAFKA_SSL_KEYFILE=path/to/client.key
KAFKA_SSL_CHECK_HOSTNAME=true
```

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/kafka-learning.git
   cd kafka-learning
   ```

2. Create a virtual environment:
   ```
   python -m venv .venv
   .venv\Scripts\activate  # On Windows
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Ensure Kafka and database are running.

2. Run the producer (e.g., poller):
   ```
   python event_serializer/poller.py
   ```

3. Run the consumer:
   ```
   python event-consumer/consume.py
   ```

4. Run the CRUD app:
   ```
   python crud_app/main.py
   ```

## Project Structure

- `common/`: Shared utilities (Kafka config, DB connection)
- `crud_app/`: Web app for CRUD operations
- `event_serializer/`: Avro serialization and producer
- `event-consumer/`: Consumer and routing logic
