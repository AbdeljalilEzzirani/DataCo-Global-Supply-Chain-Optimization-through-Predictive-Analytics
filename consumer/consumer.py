import os
from kafka import KafkaConsumer
import json
import snowflake.connector

consumer = KafkaConsumer(
    'logs',
    bootstrap_servers='kafka:9092',
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='snowflake-consumer'
)

conn = snowflake.connector.connect(
    account=os.getenv('SNOWFLAKE_ACCOUNT'),
    user=os.getenv('SNOWFLAKE_USER'),
    password=os.getenv('SNOWFLAKE_PASSWORD'),
    database=os.getenv('SNOWFLAKE_DATABASE'),
    schema=os.getenv('SNOWFLAKE_SCHEMA'),
    warehouse=os.getenv('SNOWFLAKE_WAREHOUSE')
)

cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS logistics_data (
        order_id STRING,
        departure_date STRING,
        arrival_date STRING,
        quantity INT,
        warehouse STRING,
        destination STRING,
        shipping_mode STRING,
        order_amount FLOAT,
        customer_id STRING,
        late_delivery_risk INT
    )
""")
conn.commit()

for message in consumer:
    try:
        data = json.loads(message.value.decode('utf-8'))
        cursor.execute("""
            INSERT INTO logistics_data (
                order_id, departure_date, arrival_date, quantity, warehouse, 
                destination, shipping_mode, order_amount, customer_id, late_delivery_risk
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            data['order_id'],
            data['departure_date'],
            data['arrival_date'],
            data['quantity'],
            data['warehouse'],
            data['destination'],
            data.get('shipping_mode', None),
            data.get('order_amount', None),
            data.get('customer_id', None),
            data.get('late_delivery_risk', None)
        ))
        conn.commit()
        print(f"Inserted data: {data}")
    except Exception as e:
        print(f"Error processing message: {e}")