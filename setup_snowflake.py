import snowflake.connector
import os

conn = snowflake.connector.connect(
    user=os.environ['SNOWFLAKE_USER'],
    password=os.environ['SNOWFLAKE_PASSWORD'],
    account=os.environ['SNOWFLAKE_ACCOUNT'],
    warehouse=os.environ['SNOWFLAKE_WAREHOUSE'],
    database=os.environ['SNOWFLAKE_DATABASE'],
    schema=os.environ['SNOWFLAKE_SCHEMA']
)

cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS orders (
    order_id VARCHAR,
    shipment_date DATE,
    delivery_date DATE,
    quantity INT,
    warehouse_location VARCHAR,
    delivery_location VARCHAR,
    distance FLOAT,
    weather_score FLOAT,
    traffic_score FLOAT,
    is_late BOOLEAN
);
""")
cursor.execute("""
INSERT INTO orders VALUES
('12345', '2025-04-15', '2025-04-17', 100, 'Warehouse A', 'Store B', 50.5, 0.8, 0.6, TRUE),
('12346', '2025-04-14', '2025-04-16', 50, 'Warehouse B', 'Store C', 30.0, 0.3, 0.4, FALSE);
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS kpis (
    day DATE,
    avg_delivery_time FLOAT,
    total_orders INT,
    on_time_delivery FLOAT
);
""")
cursor.execute("""
INSERT INTO kpis VALUES
('2025-04-15', 2.5, 100, 0.85),
('2025-04-16', 2.0, 120, 0.90);
""")
conn.commit()
conn.close()